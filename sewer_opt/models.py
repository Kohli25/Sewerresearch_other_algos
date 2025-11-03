from dataclasses import dataclass

@dataclass
class SewerLink:
    up_node: int
    down_node: int
    length: float
    diameter: float = 0.2
    slope: float = 0.001
    flow: float = 0.0

@dataclass
class Node:
    id: int
    wastewater_contribution: float  # l/s
    ground_level: float = 0.0
    invert_level: float = 0.0
