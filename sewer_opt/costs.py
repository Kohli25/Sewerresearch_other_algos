class CostCalculator:
    """Calculate costs for sewer network components"""
    
    def __init__(self):
        # Extended cost data with larger diameters
        self.pipe_costs = {
            0.2: 518, 0.25: 724, 0.3: 973, 0.35: 1600,
            0.4: 1850, 0.45: 2150, 0.5: 2520, 0.6: 2600, 
            0.7: 2900, 0.8: 3500, 0.9: 4000, 1.0: 5000, 
            1.5: 10000
        }
        
        self.manhole_costs = {
            (0, 1): 11800, (1, 2): 23100, (2, 3): 40000,
            (3, 4): 54600, (4, 5): 69200, (5, 6): 77500
        }
        
        self.earthwork_costs = {
            (0, 1.5): 203, (1.5, 3.0): 233.5,
            (3.0, 4.5): 299, (4.5, 6.0): 405
        }
        
    def get_pipe_cost(self, diameter: float, length: float) -> float:
        """Get cost per meter for pipe diameter"""
        available_diameters = sorted(self.pipe_costs.keys())
        selected_d = min(available_diameters, key=lambda x: abs(x - diameter))
        if selected_d < diameter:
            idx = available_diameters.index(selected_d)
            if idx < len(available_diameters) - 1:
                selected_d = available_diameters[idx + 1]
        return self.pipe_costs[selected_d] * length
    
    def get_manhole_cost(self, depth: float) -> float:
        """Get manhole cost based on depth"""
        for (d_min, d_max), cost in self.manhole_costs.items():
            if d_min < depth <= d_max:
                return cost
        return 77500  # Maximum cost
    
    def get_earthwork_cost(self, depth: float, volume: float) -> float:
        """Get earthwork cost"""
        for (d_min, d_max), cost in self.earthwork_costs.items():
            if d_min < depth <= d_max:
                return cost * volume
        return 405 * volume  # Maximum cost
    
    

