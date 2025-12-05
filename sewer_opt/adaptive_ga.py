import numpy as np
from typing import List, Tuple, Callable
import random

class AdaptiveGeneticAlgorithm:
    """
    Adaptive Genetic Algorithm for sewer network optimization
    Based on the flowchart: "Adaptive genetic algorithm for sewer networks design"
    """
    
    def __init__(self, population_size: int, n_iterations: int, n_dimensions: int,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1,
                 elitism_rate: float = 0.1, bits_per_gene: int = 8):
        self.population_size = population_size
        self.n_iterations = n_iterations
        self.n_dimensions = n_dimensions
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = max(1, int(population_size * elitism_rate))
        self.bits_per_gene = bits_per_gene  # Number of bits per gene (diameter or slope)
        
        # Binary population: each chromosome is a binary string
        self.binary_population = None
        self.decoded_population = None  # Decoded to real values
        self.fitness = None
        self.best_solution = None
        self.best_fitness = float('inf')
        self.best_binary = None
        self.convergence_history = []
        
    def optimize(self, cost_function: Callable, bounds: List[Tuple[float, float]]) -> Tuple:
        """
        Optimize using Adaptive Genetic Algorithm following the flowchart
        cost_function: function to minimize
        bounds: list of (min, max) for each dimension
        """
        # Initialize: Randomly generate initial population (binary chromosomes)
        self._initialize_population(bounds)
        
        # Evaluate initial population
        self.fitness = np.array([cost_function(ind) for ind in self.decoded_population])
        
        # Find initial best
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.decoded_population[best_idx].copy()
        self.best_binary = self.binary_population[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_history = [self.best_fitness]
        
        # Main evolution loop
        for generation in range(self.n_iterations):
            # For all chromosomes: Decode and evaluate (already done above)
            
            # Rank the chromosomes
            ranked_indices = np.argsort(self.fitness)
            
            # Transfer good chromosomes into the mating pool
            mating_pool_size = int(self.population_size * 0.6)  # Top 60% go to mating pool
            mating_pool_indices = ranked_indices[:mating_pool_size]
            mating_pool = self.binary_population[mating_pool_indices].copy()
            mating_pool_fitness = self.fitness[mating_pool_indices].copy()
            
            # Select parents and apply crossover
            offspring = self._crossover_operation(mating_pool, bounds)
            
            # Apply mutation operator
            offspring = self._mutation_operation(offspring, bounds)
            
            # Decode offspring to evaluate
            offspring_decoded = np.array([
                self._decode_chromosome(offspring[i], bounds) 
                for i in range(len(offspring))
            ])
            offspring_fitness = np.array([cost_function(ind) for ind in offspring_decoded])
            
            # Elitism: Keep best individuals
            elite_indices = ranked_indices[:self.elitism_count]
            elite_binary = self.binary_population[elite_indices].copy()
            elite_decoded = self.decoded_population[elite_indices].copy()
            elite_fitness = self.fitness[elite_indices].copy()
            
            # Combine elite and offspring
            self.binary_population = np.vstack([elite_binary, offspring])
            self.decoded_population = np.vstack([elite_decoded, offspring_decoded])
            self.fitness = np.concatenate([elite_fitness, offspring_fitness])
            
            # Keep population size constant (select best)
            if len(self.binary_population) > self.population_size:
                sorted_indices = np.argsort(self.fitness)
                self.binary_population = self.binary_population[sorted_indices[:self.population_size]]
                self.decoded_population = self.decoded_population[sorted_indices[:self.population_size]]
                self.fitness = self.fitness[sorted_indices[:self.population_size]]
            
            # Update best solution
            current_best_idx = np.argmin(self.fitness)
            current_best_fitness = self.fitness[current_best_idx]
            
            if current_best_fitness < self.best_fitness:
                self.best_solution = self.decoded_population[current_best_idx].copy()
                self.best_binary = self.binary_population[current_best_idx].copy()
                self.best_fitness = current_best_fitness
            
            self.convergence_history.append(self.best_fitness)
            
            # Convergence checking
            if (generation + 1) % 10 == 0:
                print(f"Generation {generation+1}/{self.n_iterations}, Best Cost: {self.best_fitness:.2f}")
            
            # Simple convergence: if no improvement for last 20% of iterations
            if generation > self.n_iterations * 0.8:
                recent_improvement = self.convergence_history[-int(self.n_iterations * 0.2):]
                if len(recent_improvement) > 1:
                    if abs(recent_improvement[-1] - recent_improvement[0]) < 1e-6:
                        print(f"Converged at generation {generation+1}")
                        break
        
        return self.best_solution, self.best_fitness
    
    def _initialize_population(self, bounds: List[Tuple[float, float]]):
        """Randomly generate initial population (binary chromosomes)"""
        total_bits = self.n_dimensions * self.bits_per_gene
        self.binary_population = np.random.randint(0, 2, size=(self.population_size, total_bits))
        
        # Decode initial population
        self.decoded_population = np.array([
            self._decode_chromosome(self.binary_population[i], bounds)
            for i in range(self.population_size)
        ])
    
    def _decode_chromosome(self, binary_chromosome: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
        """
        Two-stage decoding process:
        Stage 1: Decode binary chromosomes to normal diameters [d] and slopes [s] using Eq. (6)
        Stage 2: Decode normal values to design values [D] and [S] using Eq. (7) and Eq. (11)
        """
        decoded = np.zeros(self.n_dimensions)
        
        for d in range(self.n_dimensions):
            # Extract bits for this dimension
            start_bit = d * self.bits_per_gene
            end_bit = start_bit + self.bits_per_gene
            gene_bits = binary_chromosome[start_bit:end_bit]
            
            # Stage 1: Decode binary to normalized value [0, 1] (Eq. 6 equivalent)
            # Convert binary string to integer, then normalize
            binary_str = ''.join(map(str, gene_bits.astype(int)))
            integer_value = int(binary_str, 2)
            max_value = 2 ** self.bits_per_gene - 1
            normalized_value = integer_value / max_value  # Normal value in [0, 1]
            
            # Stage 2: Decode normalized value to design value [D] or [S] (Eq. 7 and 11 equivalent)
            # Linear mapping from [0, 1] to [bounds[d][0], bounds[d][1]]
            min_val, max_val = bounds[d]
            design_value = min_val + normalized_value * (max_val - min_val)
            
            # For diameter indices (even dimensions), ensure integer values
            if d % 2 == 0:  # Diameter index dimension
                design_value = np.round(design_value)
                design_value = np.clip(design_value, min_val, max_val)
            
            decoded[d] = design_value
        
        return decoded
    
    def _crossover_operation(self, mating_pool: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
        """
        Select parents and apply crossover operator to generate two offsprings per couple
        Following flowchart: "Apply the crossover operator to generate two offsprings by each couple"
        """
        offspring = []
        n_parents = len(mating_pool)
        total_bits = self.n_dimensions * self.bits_per_gene
        n_offspring_needed = self.population_size - self.elitism_count
        
        # Pair up parents and generate two offsprings per couple
        n_couples = (n_offspring_needed + 1) // 2  # Need pairs, round up
        
        for _ in range(n_couples):
            if n_parents >= 2 and np.random.random() < self.crossover_rate:
                # Select two different parents
                parent1_idx = np.random.randint(0, n_parents)
                parent2_idx = np.random.randint(0, n_parents)
                while parent2_idx == parent1_idx:
                    parent2_idx = np.random.randint(0, n_parents)
                
                parent1 = mating_pool[parent1_idx]
                parent2 = mating_pool[parent2_idx]
                
                # Single-point crossover: generate two offsprings
                crossover_point = np.random.randint(1, total_bits)
                child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
                child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
                
                offspring.extend([child1, child2])
            else:
                # No crossover, select random parents and copy
                if n_parents > 0:
                    parent1_idx = np.random.randint(0, n_parents)
                    parent2_idx = np.random.randint(0, n_parents)
                    offspring.extend([
                        mating_pool[parent1_idx].copy(),
                        mating_pool[parent2_idx].copy()
                    ])
        
        # Trim to exact number needed
        return np.array(offspring[:n_offspring_needed])
    
    def _mutation_operation(self, population: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
        """
        Apply mutation operator to mutate genes corresponding to the specified mutation ratio
        """
        mutated = population.copy()
        total_bits = self.n_dimensions * self.bits_per_gene
        total_genes = len(population) * self.n_dimensions
        
        # Calculate number of genes to mutate based on mutation rate
        n_mutations = int(total_genes * self.mutation_rate)
        
        for _ in range(n_mutations):
            # Select random chromosome and gene
            chrom_idx = np.random.randint(0, len(mutated))
            dim_idx = np.random.randint(0, self.n_dimensions)
            
            # Select random bit in this gene to flip
            start_bit = dim_idx * self.bits_per_gene
            bit_idx = np.random.randint(start_bit, start_bit + self.bits_per_gene)
            
            # Flip the bit
            mutated[chrom_idx, bit_idx] = 1 - mutated[chrom_idx, bit_idx]
        
        return mutated

