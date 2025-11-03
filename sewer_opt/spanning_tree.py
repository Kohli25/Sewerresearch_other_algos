import numpy as np
import networkx as nx
import math
from typing import List, Tuple, Dict
class SpanningTreeGenerator:
    """Generates predetermined number of spanning trees in order of increasing length"""
    
    def __init__(self, base_graph: nx.Graph, outlet_node: int):
        self.base_graph = base_graph
        self.outlet_node = outlet_node
        self.spanning_trees = []
        
    def generate_spanning_trees(self, n_trees: int) -> List[nx.Graph]:
        """Generate n spanning trees in order of increasing total length"""
        all_trees = []
        seen_trees = set()
        
        # Generate MST as first tree
        mst = nx.minimum_spanning_tree(self.base_graph, weight='length')
        tree_signature = self._get_tree_signature(mst)
        all_trees.append((self._calculate_total_length(mst), mst))
        seen_trees.add(tree_signature)
        
        print(f"Generated MST with length: {self._calculate_total_length(mst):.2f} m")
        
        # Generate additional trees using different methods
        attempts = 0
        max_attempts = n_trees * 100
        
        while len(all_trees) < n_trees and attempts < max_attempts:
            attempts += 1
            
            # Method 1: Random spanning tree using DFS
            if attempts % 3 == 0:
                tree = self._random_spanning_tree_dfs()
            # Method 2: Modified Kruskal with randomization
            elif attempts % 3 == 1:
                tree = self._random_spanning_tree_kruskal()
            # Method 3: Random walk based
            else:
                tree = self._random_spanning_tree_walk()
            
            if tree and nx.is_connected(tree) and tree.number_of_nodes() == self.base_graph.number_of_nodes():
                tree_signature = self._get_tree_signature(tree)
                if tree_signature not in seen_trees:
                    length = self._calculate_total_length(tree)
                    all_trees.append((length, tree))
                    seen_trees.add(tree_signature)
                    if len(all_trees) % 5 == 0:
                        print(f"Generated {len(all_trees)} trees...")
        
        # Sort by length and return top n_trees
        all_trees.sort(key=lambda x: x[0])
        self.spanning_trees = [tree for _, tree in all_trees[:n_trees]]
        
        print(f"Successfully generated {len(self.spanning_trees)} unique spanning trees")
        return self.spanning_trees
    
    def _random_spanning_tree_dfs(self) -> nx.Graph:
        """Generate random spanning tree using randomized DFS"""
        tree = nx.Graph()
        tree.add_nodes_from(self.base_graph.nodes(data=True))
        
        visited = set()
        stack = [self.outlet_node]
        visited.add(self.outlet_node)
        
        while stack and len(visited) < self.base_graph.number_of_nodes():
            current = stack.pop()
            neighbors = list(self.base_graph.neighbors(current))
            np.random.shuffle(neighbors)
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    tree.add_edge(current, neighbor, **self.base_graph[current][neighbor])
                    visited.add(neighbor)
                    stack.append(neighbor)
        
        return tree if len(visited) == self.base_graph.number_of_nodes() else None
    
    def _random_spanning_tree_kruskal(self) -> nx.Graph:
        """Generate spanning tree using randomized Kruskal's algorithm"""
        edges = list(self.base_graph.edges(data=True))
        # Randomize edge weights slightly
        weighted_edges = [(u, v, data['length'] * (0.8 + 0.4 * np.random.random()), data) 
                         for u, v, data in edges]
        weighted_edges.sort(key=lambda x: x[2])
        
        tree = nx.Graph()
        tree.add_nodes_from(self.base_graph.nodes(data=True))
        
        for u, v, _, data in weighted_edges:
            tree.add_edge(u, v, **data)
            if not nx.is_tree(tree):
                tree.remove_edge(u, v)
            if tree.number_of_edges() == self.base_graph.number_of_nodes() - 1:
                break
        
        return tree if nx.is_connected(tree) else None
    
    def _random_spanning_tree_walk(self) -> nx.Graph:
        """Generate spanning tree using random walk"""
        tree = nx.Graph()
        tree.add_nodes_from(self.base_graph.nodes(data=True))
        
        visited = set()
        start_node = np.random.choice(list(self.base_graph.nodes()))
        visited.add(start_node)
        
        while len(visited) < self.base_graph.number_of_nodes():
            # Pick a random visited node
            current = np.random.choice(list(visited))
            # Get unvisited neighbors
            neighbors = [n for n in self.base_graph.neighbors(current) if n not in visited]
            
            if neighbors:
                next_node = np.random.choice(neighbors)
                tree.add_edge(current, next_node, **self.base_graph[current][next_node])
                visited.add(next_node)
            
        return tree if nx.is_connected(tree) else None
    
    def _get_tree_signature(self, tree: nx.Graph) -> frozenset:
        """Get unique signature for a tree based on its edges"""
        return frozenset(frozenset([u, v]) for u, v in tree.edges())
    
    def _calculate_total_length(self, graph: nx.Graph) -> float:
        """Calculate total length of all edges"""
        return sum(data['length'] for _, _, data in graph.edges(data=True))
