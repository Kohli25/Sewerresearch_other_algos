import numpy as np
from typing import List, Tuple
from typing import List, Tuple, Dict
class ModifiedPSO:
    """Modified Particle Swarm Optimization for sewer component sizing"""
    
    def __init__(self, n_particles: int, n_iterations: int, n_dimensions: int):
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.n_dimensions = n_dimensions
        
        # PSO parameters
        self.w_max = 0.7
        self.w_min = 0.2
        self.c1_max = 2.0
        self.c1_min = 0.5
        self.c2_max = 2.0
        self.c2_min = 0.5
        
        # Initialize particles
        self.particles = None
        self.velocities = None
        self.pbest = None
        self.pbest_costs = None
        self.gbest = None
        self.gbest_cost = float('inf')
        self.convergence_history = []  # Track convergence
        
    def optimize(self, cost_function, bounds: List[Tuple[float, float]]) -> Tuple:
        """
        Optimize using Modified PSO
        cost_function: function to minimize
        bounds: list of (min, max) for each dimension
        """
        # Initialize particles randomly within bounds
        self.particles = np.random.uniform(
            low=[b[0] for b in bounds],
            high=[b[1] for b in bounds],
            size=(self.n_particles, self.n_dimensions)
        )
        
        # Initialize velocities
        v_max = [(b[1] - b[0]) * 0.15 for b in bounds]
        self.velocities = np.random.uniform(
            low=[-vm for vm in v_max],
            high=v_max,
            size=(self.n_particles, self.n_dimensions)
        )
        
        # Initialize personal best
        self.pbest = self.particles.copy()
        self.pbest_costs = np.array([cost_function(p) for p in self.particles])
        
        # Initialize global best
        best_idx = np.argmin(self.pbest_costs)
        self.gbest = self.pbest[best_idx].copy()
        self.gbest_cost = self.pbest_costs[best_idx]
        
        # Optimization loop
        for t in range(self.n_iterations):
            # Update inertia weight and acceleration coefficients (Eqs 20-22)
            w = self.w_max - (self.w_max - self.w_min) * t / self.n_iterations
            c1 = self.c1_max - (self.c1_max - self.c1_min) * t / self.n_iterations
            c2 = self.c2_max - (self.c2_max - self.c2_min) * t / self.n_iterations
            
            for i in range(self.n_particles):
                # Random coefficients
                r1 = np.random.random(self.n_dimensions)
                r2 = np.random.random(self.n_dimensions)
                
                # Update velocity (Eq 19)
                self.velocities[i] = (
                    w * self.velocities[i] +
                    c1 * r1 * (self.pbest[i] - self.particles[i]) +
                    c2 * r2 * (self.gbest - self.particles[i])
                )
                
                # Limit velocity
                for d in range(self.n_dimensions):
                    self.velocities[i, d] = np.clip(
                        self.velocities[i, d],
                        -v_max[d], v_max[d]
                    )
                
                # Update position (Eq 18)
                self.particles[i] = self.particles[i] + self.velocities[i]
                
                # Apply bounds
                for d in range(self.n_dimensions):
                    self.particles[i, d] = np.clip(
                        self.particles[i, d],
                        bounds[d][0], bounds[d][1]
                    )
                
                # Evaluate fitness
                cost = cost_function(self.particles[i])
                
                # Update personal best
                if cost < self.pbest_costs[i]:
                    self.pbest[i] = self.particles[i].copy()
                    self.pbest_costs[i] = cost
                    
                    # Update global best
                    if cost < self.gbest_cost:
                        self.gbest = self.particles[i].copy()
                        self.gbest_cost = cost
            
            # Track convergence
            self.convergence_history.append(self.gbest_cost)
            
            if (t + 1) % 10 == 0:
                print(f"Iteration {t+1}/{self.n_iterations}, Best Cost: {self.gbest_cost:.2f}")
        
        return self.gbest, self.gbest_cost
