import numpy as np
from typing import List, Tuple, Callable

class AntColonyOptimization:
    """Ant Colony Optimization for sewer component sizing optimization"""
    
    def __init__(self, n_ants: int, n_iterations: int, n_dimensions: int,
                 alpha: float = 1.0, beta: float = 2.0, rho: float = 0.1,
                 q0: float = 0.9):
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.n_dimensions = n_dimensions
        self.alpha = alpha  # Pheromone importance
        self.beta = beta   # Heuristic importance
        self.rho = rho     # Evaporation rate
        self.q0 = q0       # Exploitation probability
        
        # Pheromone matrix (for discrete optimization, we discretize the search space)
        self.n_discrete_levels = 50  # Discretization levels per dimension
        self.pheromone = None
        self.heuristic = None
        
        # Best solution tracking
        self.best_solution = None
        self.best_cost = float('inf')
        self.convergence_history = []
        
    def optimize(self, cost_function: Callable, bounds: List[Tuple[float, float]]) -> Tuple:
        """
        Optimize using Ant Colony Optimization
        cost_function: function to minimize
        bounds: list of (min, max) for each dimension
        """
        # Initialize pheromone matrix
        tau0 = 1.0  # Initial pheromone value
        self.pheromone = np.ones((self.n_dimensions, self.n_discrete_levels)) * tau0
        
        # Initialize heuristic information (inverse of range)
        self.heuristic = np.ones((self.n_dimensions, self.n_discrete_levels))
        for d in range(self.n_dimensions):
            range_size = bounds[d][1] - bounds[d][0]
            self.heuristic[d, :] = 1.0 / (range_size + 1e-10)
        
        # Main ACO loop
        for iteration in range(self.n_iterations):
            solutions = []
            costs = []
            
            # Each ant constructs a solution
            for ant in range(self.n_ants):
                solution = self._construct_solution(bounds)
                cost = cost_function(solution)
                solutions.append(solution)
                costs.append(cost)
                
                # Update best solution
                if cost < self.best_cost:
                    self.best_solution = solution.copy()
                    self.best_cost = cost
            
            # Update pheromones
            self._update_pheromones(solutions, costs, bounds)
            
            self.convergence_history.append(self.best_cost)
            
            if (iteration + 1) % 10 == 0:
                print(f"Iteration {iteration+1}/{self.n_iterations}, Best Cost: {self.best_cost:.2f}")
        
        return self.best_solution, self.best_cost
    
    def _construct_solution(self, bounds: List[Tuple[float, float]]) -> np.ndarray:
        """Construct a solution using pheromone and heuristic information"""
        solution = np.zeros(self.n_dimensions)
        
        for d in range(self.n_dimensions):
            # Discretize dimension d
            levels = np.linspace(bounds[d][0], bounds[d][1], self.n_discrete_levels)
            
            # Calculate probabilities using pheromone and heuristic
            pheromone_values = self.pheromone[d, :]
            heuristic_values = self.heuristic[d, :]
            
            # Probability = (tau^alpha) * (eta^beta)
            probabilities = (pheromone_values ** self.alpha) * (heuristic_values ** self.beta)
            
            # Normalize probabilities and handle edge cases
            prob_sum = probabilities.sum()
            if prob_sum > 1e-10:
                probabilities = probabilities / prob_sum
            else:
                # If all probabilities are too small, use uniform distribution
                probabilities = np.ones(self.n_discrete_levels) / self.n_discrete_levels
            
            # Ensure probabilities sum to exactly 1 (fix floating point errors)
            probabilities = probabilities / probabilities.sum()
            
            # Selection: exploitation or exploration
            if np.random.random() < self.q0:
                # Exploitation: choose best
                selected_idx = np.argmax(probabilities)
            else:
                # Exploration: probabilistic selection
                selected_idx = np.random.choice(self.n_discrete_levels, p=probabilities)
            
            # Add some continuous variation around selected level
            level_value = levels[selected_idx]
            if selected_idx > 0 and selected_idx < self.n_discrete_levels - 1:
                # Interpolate between adjacent levels
                if np.random.random() < 0.5:
                    solution[d] = level_value + np.random.uniform(
                        -0.1 * (levels[1] - levels[0]),
                        0.1 * (levels[1] - levels[0])
                    )
                else:
                    solution[d] = level_value
            else:
                solution[d] = level_value
            
            # Ensure bounds
            solution[d] = np.clip(solution[d], bounds[d][0], bounds[d][1])
        
        return solution
    
    def _update_pheromones(self, solutions: List[np.ndarray], costs: List[float], 
                           bounds: List[Tuple[float, float]]):
        """Update pheromone matrix"""
        # Evaporation
        self.pheromone *= (1 - self.rho)
        
        # Deposit pheromone (only for good solutions)
        Q = 1.0  # Pheromone deposit constant
        min_cost = min(costs)
        
        for solution, cost in zip(solutions, costs):
            # Only update for solutions within top 50% or best solution
            if cost <= np.percentile(costs, 50) or cost == min_cost:
                delta_tau = Q / (cost + 1e-10)  # Inverse of cost
                
                for d in range(self.n_dimensions):
                    # Find closest discrete level
                    levels = np.linspace(bounds[d][0], bounds[d][1], self.n_discrete_levels)
                    closest_idx = np.argmin(np.abs(levels - solution[d]))
                    
                    # Deposit pheromone
                    self.pheromone[d, closest_idx] += delta_tau
        
        # Keep pheromone within reasonable bounds
        tau_min = 0.01
        tau_max = 10.0
        self.pheromone = np.clip(self.pheromone, tau_min, tau_max)

