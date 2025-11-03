import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List, Tuple
from .models import Node
from .hydraulics import SewerHydraulics
from .costs import CostCalculator
from .pso import ModifiedPSO
from .spanning_tree import SpanningTreeGenerator


class SewerNetworkOptimizer:
    """Main optimizer combining spanning tree generation and PSO"""
    
    def __init__(self, base_graph: nx.Graph, nodes: Dict[int, Node], outlet_node: int):
        self.base_graph = base_graph
        self.nodes = nodes
        self.outlet_node = outlet_node
        self.hydraulics = SewerHydraulics()
        self.cost_calc = CostCalculator()
        self.best_design_details = None  # Store detailed design info
        self.optimization_history = {}  # Store optimization results for plotting
        
    def calculate_cumulative_flow(self, tree: nx.Graph) -> float:
        """Calculate total cumulative flow (CQ) for a layout (Eq 1)"""
        # Convert to directed tree first
        directed_tree = self._get_flow_direction_tree(tree)
        
        total_cq = 0.0
        
        # For each link, calculate the flow and add to cumulative total
        for u, v in directed_tree.edges():
            # Calculate flow in this link by summing all upstream contributions
            link_flow = self._calculate_link_flow_directed(directed_tree, u, v)
            total_cq += link_flow
        
        return total_cq
    
    def _calculate_link_flow(self, tree: nx.Graph, u: int, v: int) -> float:
        """Calculate flow in a link by summing upstream contributions (simplified)"""
        # This is a fallback for undirected trees
        return abs(self.nodes[u].wastewater_contribution + 
                   self.nodes[v].wastewater_contribution) / 1000  # Convert l/s to m3/s
    
    def optimize_layout_sequence(self, n_layouts: int = 10, 
                                 pso_particles: int = 100,
                                 pso_iterations: int = 30):
        """Main optimization routine"""
        # Step 1: Generate spanning trees
        print("\n" + "=" * 80)
        print("STEP 1: Generating Spanning Trees")
        print("=" * 80)
        tree_gen = SpanningTreeGenerator(self.base_graph, self.outlet_node)
        trees = tree_gen.generate_spanning_trees(n_layouts)
        
        if len(trees) < n_layouts:
            print(f"⚠ Warning: Only generated {len(trees)} unique trees out of {n_layouts} requested")
        
        # Step 2: Calculate CQ for each layout
        print("\n" + "=" * 80)
        print("STEP 2: Calculating Cumulative Flows (CQ)")
        print("=" * 80)
        layouts_with_cq = []
        for i, tree in enumerate(trees):
            cq = self.calculate_cumulative_flow(tree)
            length = sum(data['length'] for _, _, data in tree.edges(data=True))
            layouts_with_cq.append((cq, tree, length))
            print(f"Layout {i+1}: CQ = {cq:.4f} m³/s ({cq*1000:.2f} l/s), Length = {length:.2f} m")
        
        # Step 3: Sort by CQ
        print("\n" + "=" * 80)
        print("STEP 3: Sorting Layouts by Cumulative Flow")
        print("=" * 80)
        layouts_with_cq.sort(key=lambda x: x[0])
        
        print(f"\nLayouts sorted (ascending CQ):")
        for i, (cq, _, length) in enumerate(layouts_with_cq[:10]):
            print(f"  Rank {i+1}: CQ = {cq:.4f} m³/s ({cq*1000:.2f} l/s), Length = {length:.2f} m")
        
        # Step 4: Optimize each layout with Modified PSO
        print("\n" + "=" * 80)
        print("STEP 4: Optimizing Component Sizes with Modified PSO")
        print("=" * 80)
        results = []
        
        for i, (cq, tree, length) in enumerate(layouts_with_cq):
            print(f"\n--- Optimizing Layout {i+1}/{len(layouts_with_cq)} ---")
            print(f"    CQ = {cq:.4f} m³/s, Length = {length:.2f} m")
            cost, design_details = self._optimize_component_sizing(tree, pso_particles, pso_iterations)
            results.append((i+1, cq, cost, tree, design_details))
            print(f"    Final Cost: Rs. {cost:,.2f}")
        
        # Sort results by cost (lowest cost = best design)
        print("\n" + "=" * 80)
        print("STEP 5: Sorting Layouts by Total Cost")
        print("=" * 80)
        results.sort(key=lambda x: x[2])  # Sort by cost (index 2)
        
        print("\nLayouts ranked by cost (Best = Minimum Cost):")
        for rank, (layout_num, cq, cost, _, _) in enumerate(results[:10], 1):
            print(f"  Rank {rank}: Layout {layout_num}, Cost = Rs. {cost:,.2f}, CQ = {cq:.4f} m³/s")
        
        # Store the best design details (minimum cost)
        if results:
            self.best_design_details = results[0][4]  # Details from best layout (lowest cost)
            
        return results
    
    def _optimize_component_sizing(self, tree: nx.Graph, 
                                   n_particles: int, 
                                   n_iterations: int) -> Tuple[float, Dict]:
        """Optimize component sizes for a given layout using Modified PSO"""
        n_links = tree.number_of_edges()
        
        # Each link has 2 variables: diameter index and slope
        n_dimensions = n_links * 2
        
        # Define bounds with extended diameter range
        available_diameters = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5]
        bounds = []
        for _ in range(n_links):
            bounds.append((0, len(available_diameters) - 1))  # Diameter index
            bounds.append((0.0004, 0.02))  # Slope range
        
        # Define cost function
        def cost_function(x):
            cost, _ = self._evaluate_design(tree, x, available_diameters)
            return cost
        
        # Run PSO
        pso = ModifiedPSO(n_particles, n_iterations, n_dimensions)
        best_solution, best_cost = pso.optimize(cost_function, bounds)
        
        # Get detailed design for best solution
        _, design_details = self._evaluate_design(tree, best_solution, available_diameters)
        
        return best_cost, design_details
    
    def _get_flow_direction_tree(self, tree: nx.Graph) -> nx.DiGraph:
        """Convert undirected tree to directed tree with flow from sources to outlet"""
        # Create directed graph with flow towards outlet
        directed_tree = nx.DiGraph()
        directed_tree.add_nodes_from(tree.nodes(data=True))
        
        # BFS from outlet to determine flow direction
        visited = set()
        queue = [self.outlet_node]
        visited.add(self.outlet_node)
        parent = {self.outlet_node: None}
        
        while queue:
            current = queue.pop(0)
            for neighbor in tree.neighbors(current):
                if neighbor not in visited:
                    # Flow goes FROM neighbor TO current (towards outlet)
                    directed_tree.add_edge(neighbor, current, **tree[neighbor][current])
                    parent[neighbor] = current
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return directed_tree
    
    def _get_topological_order(self, directed_tree: nx.DiGraph) -> List[Tuple]:
        """Get edges in topological order (upstream to downstream)"""
        # Find leaf nodes (sources - no incoming edges)
        in_degree = {node: directed_tree.in_degree(node) for node in directed_tree.nodes()}
        
        # Start with nodes that have no predecessors (leaf nodes)
        queue = [node for node, degree in in_degree.items() if degree == 0]
        ordered_edges = []
        
        while queue:
            current = queue.pop(0)
            # Get all outgoing edges (downstream direction)
            for successor in directed_tree.successors(current):
                edge_data = directed_tree[current][successor]
                ordered_edges.append((current, successor, edge_data))
                
                # Decrease in-degree and add to queue if all predecessors processed
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    queue.append(successor)
        
        return ordered_edges
    
    def _evaluate_design(self, tree: nx.Graph, design: np.ndarray, 
                        available_diameters: List[float]) -> Tuple[float, Dict]:
        """Evaluate total cost and constraints for a design"""
        total_cost = 0.0
        penalty = 0.0
        design_details = []
        
        # Convert to directed tree for proper flow direction
        directed_tree = self._get_flow_direction_tree(tree)
        
        # Get edges in topological order (upstream to downstream)
        ordered_edges = self._get_topological_order(directed_tree)
        
        # Map to store diameter at each node for progressive diameter constraint
        node_diameter = {}
        
        # Create edge index mapping
        edge_to_index = {}
        for i, (u, v, _) in enumerate(ordered_edges):
            edge_to_index[(u, v)] = i
        
        for i, (u, v, data) in enumerate(ordered_edges):
            # Extract design variables
            d_idx = int(round(design[i * 2]))
            d_idx = np.clip(d_idx, 0, len(available_diameters) - 1)
            diameter = available_diameters[d_idx]
            slope = design[i * 2 + 1]
            
            # Progressive diameter constraint (Eq. 11): D_current >= D_preceding
            # For each upstream node feeding into current link, check its diameter
            max_preceding_diameter = 0.0
            upstream_nodes_with_diameter = []
            
            for pred in directed_tree.predecessors(u):
                if pred in node_diameter:
                    upstream_nodes_with_diameter.append((pred, node_diameter[pred]))
                    max_preceding_diameter = max(max_preceding_diameter, node_diameter[pred])
            
            # Enforce progressive diameter constraint
            if max_preceding_diameter > 0:
                if diameter < max_preceding_diameter:
                    # Must use at least the maximum preceding diameter
                    diameter = max_preceding_diameter
                    # Find closest available diameter that satisfies constraint
                    valid_diameters = [d for d in available_diameters if d >= max_preceding_diameter]
                    if valid_diameters:
                        diameter = min(valid_diameters)
            
            # Store diameter at downstream node for this link
            node_diameter[v] = diameter
            
            length = data['length']
            flow = self._calculate_link_flow_directed(directed_tree, u, v)
            
            # Calculate hydraulics
            params = self.hydraulics.calculate_flow_parameters(flow, diameter, slope)
            
            if params is None:
                penalty += 1e8
                # Store design even if invalid
                design_details.append({
                    'link': i + 1,
                    'from_node': u,
                    'to_node': v,
                    'length': length,
                    'diameter': diameter,
                    'slope': slope,
                    'slope_ratio': f"1 in {int(1/slope) if slope > 0 else 'inf'}",
                    'flow': flow,
                    'velocity': None,
                    'd_D': None,
                    'd': None,
                    'status': 'Invalid - K >= 1/π'
                })
                continue
            
            # Calculate costs
            pipe_cost = self.cost_calc.get_pipe_cost(diameter, length)
            
            # Simplified depth calculation
            avg_depth = 1.5  # Simplified
            manhole_cost = self.cost_calc.get_manhole_cost(avg_depth)
            earthwork_cost = self.cost_calc.get_earthwork_cost(avg_depth, length * 1.0)
            
            link_cost = pipe_cost + manhole_cost + earthwork_cost
            total_cost += link_cost
            
            # Check constraints
            V = params['V']
            d_D = params['d_D']
            d = params['d']
            
            # Track constraint violations
            violations = []
            
            # Check progressive diameter constraint
            if max_preceding_diameter > 0:
                original_d_idx = int(round(design[i * 2]))
                original_d_idx = np.clip(original_d_idx, 0, len(available_diameters) - 1)
                original_diameter = available_diameters[original_d_idx]
                
                if original_diameter < max_preceding_diameter - 0.001:
                    penalty += 1e6 * (max_preceding_diameter - original_diameter)
                    violations.append(f"D_prog: needed {diameter*1000:.0f}mm")
            
            # Velocity constraints
            if V < 0.6:
                if flow >= 0.0014:  # As per paper
                    penalty += 1e8 * (0.6 - V)
                    violations.append(f"V < 0.6 m/s")
            if V > 3.0:
                penalty += 1e8 * (V - 3.0)
                violations.append(f"V > 3.0 m/s")
            
            # Depth ratio constraint
            if d_D > 0.8:
                penalty += 1e8 * (d_D - 0.8)
                violations.append(f"d/D > 0.8")
            
            # Cover depth (simplified check)
            if avg_depth < 0.9:
                penalty += 1e8 * (0.9 - avg_depth)
                violations.append(f"Cover < 0.9 m")
            if avg_depth > 5.0:
                penalty += 1e8 * (avg_depth - 5.0)
                violations.append(f"Cover > 5.0 m")
            
            # Store design details
            design_details.append({
                'link': i + 1,
                'from_node': u,
                'to_node': v,
                'length': length,
                'diameter': diameter,
                'slope': slope,
                'slope_ratio': f"1 in {int(1/slope) if slope > 0 else 'inf'}",
                'flow': flow,
                'flow_lps': flow * 1000,  # Convert to l/s
                'velocity': V,
                'd_D': d_D,
                'd': d,
                'link_cost': link_cost,
                'status': 'OK' if not violations else ', '.join(violations),
                'max_preceding_diameter': max_preceding_diameter if max_preceding_diameter > 0 else None
            })
        
        return total_cost + penalty, design_details
    
    def _calculate_link_flow_directed(self, directed_tree: nx.DiGraph, u: int, v: int) -> float:
        """Calculate flow in a directed link by summing all upstream contributions"""
        # Get all nodes upstream of u (including u itself)
        upstream_nodes = set()
        
        def find_upstream(node):
            upstream_nodes.add(node)
            # Find all predecessors in directed tree
            for pred in directed_tree.predecessors(node):
                find_upstream(pred)
        
        find_upstream(u)
        
        # Sum all wastewater contributions from upstream nodes
        total_flow = sum(self.nodes[node].wastewater_contribution 
                        for node in upstream_nodes 
                        if self.nodes[node].wastewater_contribution > 0)
        
        return total_flow / 1000  # Convert l/s to m3/s

    def run_sensitivity_analysis(self, best_tree: nx.Graph, 
                                 swarm_sizes: List[int] = [200, 400, 600, 800, 1000],
                                 iterations_list: List[int] = [30, 60, 90, 120]):
        """
        Run sensitivity analysis for different swarm sizes and iterations
        Returns results for plotting
        """
        print("\n" + "=" * 80)
        print("SENSITIVITY ANALYSIS: Swarm Size vs Cost")
        print("=" * 80)
        
        results = {}
        total_runs = len(swarm_sizes) * len(iterations_list)
        current_run = 0
        
        for iterations in iterations_list:
            results[iterations] = {}
            for swarm_size in swarm_sizes:
                current_run += 1
                print(f"\n[{current_run}/{total_runs}] Testing: Swarm={swarm_size}, Iterations={iterations}")
                
                # Run optimization
                cost, _ = self._optimize_component_sizing(best_tree, swarm_size, iterations)
                results[iterations][swarm_size] = cost
                
                print(f"    Result: Rs. {cost:,.2f}")
                
                
        
        # Store in history
        self.optimization_history = results
        
        return results
    
    
    def plot_sensitivity_analysis(self, results: Dict = None, save_path: str = 'output'):
        """
        Plot swarm size vs cost for different iterations
        """
        if results is None:
            results = self.optimization_history
        
        if not results:
            print("No results to plot. Run sensitivity analysis first.")
            return
        
        # Create figure with larger size
        plt.figure(figsize=(12, 8))
        
        # Define colors and markers for different iterations
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        markers = ['o', 's', '^', 'D']
        
        # Extract data and plot
        iterations_list = sorted(results.keys())
        
        for idx, iterations in enumerate(iterations_list):
            swarm_sizes = sorted(results[iterations].keys())
            costs = [results[iterations][size] for size in swarm_sizes]
            
            # Convert costs to millions for better readability
            costs_millions = [c / 1e6 for c in costs]
            
            plt.plot(swarm_sizes, costs_millions, 
                    marker=markers[idx % len(markers)], 
                    color=colors[idx % len(colors)],
                    linewidth=2, 
                    markersize=8,
                    label=f'{iterations} Iterations')
        
        plt.xlabel('Swarm Size', fontsize=12, fontweight='bold')
        plt.ylabel('Total Cost (Million Rs.)', fontsize=12, fontweight='bold')
        plt.title('Sensitivity Analysis: Swarm Size vs Total Cost\nat Different Iterations', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10, loc='best')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.xticks(swarm_sizes if swarm_sizes else [200, 400, 600, 800, 1000])
        
        # Add minor gridlines
        plt.minorticks_on()
        plt.grid(which='minor', alpha=0.2, linestyle=':')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\nPlot saved to: {save_path}")
        
        plt.show()
        
        # Print summary table
        print("\n" + "=" * 80)
        print("SENSITIVITY ANALYSIS RESULTS TABLE")
        print("=" * 80)
        print(f"\n{'Swarm Size':<12}", end='')
        for iterations in iterations_list:
            print(f"{'Iter=' + str(iterations):<20}", end='')
        print()
        print("-" * 80)
        
        if iterations_list and results[iterations_list[0]]:
            swarm_sizes = sorted(results[iterations_list[0]].keys())
            for swarm_size in swarm_sizes:
                print(f"{swarm_size:<12}", end='')
                for iterations in iterations_list:
                    cost = results[iterations][swarm_size]
                    print(f"Rs. {cost:>15,.2f}   ", end='')
                print()
        
        # Find best configuration
        print("\n" + "=" * 80)
        print("BEST CONFIGURATIONS")
        print("=" * 80)
        
        min_cost = float('inf')
        best_config = None
        
        for iterations in iterations_list:
            for swarm_size, cost in results[iterations].items():
                if cost < min_cost:
                    min_cost = cost
                    best_config = (swarm_size, iterations)
        
        if best_config:
            print(f"\n★ Overall Best: Swarm Size = {best_config[0]}, Iterations = {best_config[1]}")
            print(f"  Minimum Cost: Rs. {min_cost:,.2f}")
            
        # Best for each iteration level
        print("\n📊 Best Swarm Size for Each Iteration Level:")
        for iterations in iterations_list:
            costs = results[iterations]
            best_swarm = min(costs, key=costs.get)
            best_cost = costs[best_swarm]
            print(f"  {iterations} Iterations: Swarm = {best_swarm}, Cost = Rs. {best_cost:,.2f}")
        
        

        
        
