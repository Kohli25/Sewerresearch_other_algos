import numpy as np
from typing import List, Tuple, Callable
import random

class GeneticAlgorithm:
    """Genetic Algorithm for sewer component sizing optimization"""
    
    def __init__(self, population_size: int, n_iterations: int, n_dimensions: int,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.1,
                 elitism_rate: float = 0.1):
        self.population_size = population_size
        self.n_iterations = n_iterations
        self.n_dimensions = n_dimensions
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = max(1, int(population_size * elitism_rate))
        
        # Population and fitness
        self.population = None
        self.fitness = None
        self.best_solution = None
        self.best_fitness = float('inf')
        self.convergence_history = []
        
    def optimize(self, cost_function: Callable, bounds: List[Tuple[float, float]]) -> Tuple:
        """
        Optimize using Genetic Algorithm
        cost_function: function to minimize
        bounds: list of (min, max) for each dimension
        """
        # Initialize population randomly within bounds
        # For diameter indices (even dimensions), use integer values
        self.population = []
        for _ in range(self.population_size):
            individual = np.zeros(self.n_dimensions)
            for d in range(self.n_dimensions):
                if d % 2 == 0:  # Diameter index dimension
                    # Use integer values for diameter indices
                    individual[d] = np.random.randint(int(bounds[d][0]), int(bounds[d][1]) + 1)
                else:  # Slope dimension
                    # Use continuous values for slopes
                    individual[d] = np.random.uniform(bounds[d][0], bounds[d][1])
            self.population.append(individual)
        self.population = np.array(self.population)
        
        # Evaluate initial population
        self.fitness = np.array([cost_function(ind) for ind in self.population])
        
        # Find initial best
        best_idx = np.argmin(self.fitness)
        self.best_solution = self.population[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_history = [self.best_fitness]
        
        # Main evolution loop
        for generation in range(self.n_iterations):
            # Selection: Tournament selection
            new_population = self._tournament_selection()
            
            # Crossover
            offspring = self._crossover(new_population, bounds)
            
            # Mutation
            offspring = self._mutate(offspring, bounds)
            
            # Evaluate offspring
            offspring_fitness = np.array([cost_function(ind) for ind in offspring])
            
            # Elitism: Keep best individuals from previous generation
            elite_indices = np.argsort(self.fitness)[:self.elitism_count]
            elite_individuals = self.population[elite_indices]
            elite_fitness = self.fitness[elite_indices]
            
            # Combine elite and offspring
            self.population = np.vstack([elite_individuals, offspring])
            self.fitness = np.concatenate([elite_fitness, offspring_fitness])
            
            # Keep population size constant
            if len(self.population) > self.population_size:
                # Keep best individuals
                sorted_indices = np.argsort(self.fitness)
                self.population = self.population[sorted_indices[:self.population_size]]
                self.fitness = self.fitness[sorted_indices[:self.population_size]]
            
            # Repair population: ensure diameter indices are integers
            for ind in self.population:
                for d in range(0, self.n_dimensions, 2):  # Only diameter indices
                    ind[d] = np.round(ind[d])
                    ind[d] = np.clip(ind[d], bounds[d][0], bounds[d][1])
            
            # Update best solution
            current_best_idx = np.argmin(self.fitness)
            current_best_fitness = self.fitness[current_best_idx]
            
            if current_best_fitness < self.best_fitness:
                self.best_solution = self.population[current_best_idx].copy()
                self.best_fitness = current_best_fitness
            
            self.convergence_history.append(self.best_fitness)
            
            if (generation + 1) % 10 == 0:
                print(f"Generation {generation+1}/{self.n_iterations}, Best Cost: {self.best_fitness:.2f}")
        
        return self.best_solution, self.best_fitness
    
    def _tournament_selection(self, tournament_size: int = 3) -> np.ndarray:
        """Tournament selection for parent selection"""
        selected = []
        for _ in range(self.population_size):
            # Randomly select tournament_size individuals
            tournament_indices = np.random.choice(
                self.population_size, 
                size=min(tournament_size, self.population_size),
                replace=False
            )
            # Select the best from tournament
            winner_idx = tournament_indices[np.argmin(self.fitness[tournament_indices])]
            selected.append(self.population[winner_idx])
        return np.array(selected)
    
    def _crossover(self, parents: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
        """Simulated Binary Crossover (SBX) with discrete handling for diameter indices"""
        offspring = []
        n_parents = len(parents)
        
        for i in range(0, n_parents - 1, 2):
            parent1 = parents[i]
            parent2 = parents[i + 1] if i + 1 < n_parents else parents[0]
            
            if np.random.random() < self.crossover_rate:
                # SBX crossover
                eta_c = 20  # Distribution index for crossover
                u = np.random.random(self.n_dimensions)
                
                beta = np.where(u <= 0.5,
                               (2 * u) ** (1 / (eta_c + 1)),
                               (1 / (2 * (1 - u))) ** (1 / (eta_c + 1)))
                
                child1 = 0.5 * ((1 + beta) * parent1 + (1 - beta) * parent2)
                child2 = 0.5 * ((1 - beta) * parent1 + (1 + beta) * parent2)
                
                # Apply bounds and handle discrete dimensions (diameter indices)
                for d in range(self.n_dimensions):
                    child1[d] = np.clip(child1[d], bounds[d][0], bounds[d][1])
                    child2[d] = np.clip(child2[d], bounds[d][0], bounds[d][1])
                    
                    # For diameter indices (even indices), ensure integer values
                    # This helps with discrete selection
                    if d % 2 == 0:  # Diameter index dimension
                        # Round to nearest integer for better discrete exploration
                        child1[d] = np.round(child1[d])
                        child2[d] = np.round(child2[d])
                        # Ensure still within bounds
                        child1[d] = np.clip(child1[d], bounds[d][0], bounds[d][1])
                        child2[d] = np.clip(child2[d], bounds[d][0], bounds[d][1])
                
                offspring.extend([child1, child2])
            else:
                # No crossover, copy parents
                offspring.extend([parent1.copy(), parent2.copy()])
        
        return np.array(offspring[:self.population_size])
    
    def _mutate(self, population: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
        """Polynomial mutation with discrete handling for diameter indices"""
        mutated = population.copy()
        
        for i in range(len(mutated)):
            if np.random.random() < self.mutation_rate:
                eta_m = 20  # Distribution index for mutation
                
                for d in range(self.n_dimensions):
                    if np.random.random() < 1.0 / self.n_dimensions:  # Mutation probability per dimension
                        # For diameter indices, use integer mutation
                        if d % 2 == 0:  # Diameter index dimension
                            # Integer mutation: move to adjacent valid index
                            current_idx = int(np.round(mutated[i, d]))
                            if np.random.random() < 0.5:
                                # Move to next index
                                mutated[i, d] = min(current_idx + 1, bounds[d][1])
                            else:
                                # Move to previous index
                                mutated[i, d] = max(current_idx - 1, bounds[d][0])
                        else:
                            # Continuous mutation for slopes
                            u = np.random.random()
                            delta = (bounds[d][1] - bounds[d][0])
                            
                            if u < 0.5:
                                delta_q = (2 * u) ** (1 / (eta_m + 1)) - 1
                            else:
                                delta_q = 1 - (2 * (1 - u)) ** (1 / (eta_m + 1))
                            
                            mutated[i, d] += delta_q * delta * 0.1  # Scale mutation
                            mutated[i, d] = np.clip(mutated[i, d], bounds[d][0], bounds[d][1])
        
        return mutated

