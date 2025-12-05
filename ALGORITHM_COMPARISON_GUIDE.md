# Algorithm Comparison Guide

## Overview

The sewer network optimization framework now supports **three optimization algorithms**:
1. **PSO** - Modified Particle Swarm Optimization (original)
2. **GA** - Genetic Algorithm (new)
3. **ACO** - Ant Colony Optimization (new)

You can now run a single algorithm or compare all three algorithms side-by-side!

---

## New Features

### 1. Algorithm Selection
When you run `main.py`, you'll be prompted to choose:
- **Option 1**: PSO only
- **Option 2**: GA only
- **Option 3**: ACO only
- **Option 4**: Compare ALL three algorithms

### 2. Algorithm Comparison
When selecting "ALL", the system will:
1. First find the best layout using PSO (quick search)
2. Run all three algorithms on the same best layout
3. Compare their performance (cost, convergence)
4. Generate comparison plots

### 3. Comparison Outputs
- **Comparison Table**: Shows cost ranking of all algorithms
- **Comparison Plot**: Two-panel visualization:
  - Bar chart comparing final costs
  - Convergence curves showing optimization progress
- **Saved to**: `output/algorithm_comparison.png`

---

## Algorithm Details

### Genetic Algorithm (GA)
- **Selection**: Tournament selection
- **Crossover**: Simulated Binary Crossover (SBX)
- **Mutation**: Polynomial mutation
- **Elitism**: Preserves best individuals across generations
- **Parameters**:
  - Crossover rate: 0.8
  - Mutation rate: 0.1
  - Elitism rate: 10%

### Ant Colony Optimization (ACO)
- **Pheromone-based**: Uses pheromone trails to guide search
- **Heuristic-guided**: Combines pheromone and heuristic information
- **Discretization**: 50 levels per dimension
- **Parameters**:
  - Alpha (pheromone importance): 1.0
  - Beta (heuristic importance): 2.0
  - Rho (evaporation rate): 0.1
  - Q0 (exploitation probability): 0.9

### Modified PSO (Original)
- **Time-varying parameters**: Inertia weight and acceleration coefficients
- **Convergence tracking**: Now includes convergence history

---

## Usage Examples

### Example 1: Run Single Algorithm (GA)
```python
# When prompted:
# Select algorithm (1/2/3/4): 2
# Use default settings (Y/N): Y
```

### Example 2: Compare All Algorithms
```python
# When prompted:
# Select algorithm (1/2/3/4): 4
# Use default settings (Y/N): Y
```

### Example 3: Custom Settings
```python
# When prompted:
# Select algorithm (1/2/3/4): 4
# Use default settings (Y/N): N
# Enter number of top layouts: 5
# Enter population/swarm size: 200
# Enter Max Iterations: 50
```

---

## Output Files

1. **`output/algorithm_comparison.png`**: Comparison visualization (when comparing all)
2. **`output/{filename}_results.csv`**: Best design results
3. **`output/result_layout.png`**: Network layout visualization
4. **`output/sensitivity_analysis.png`**: Sensitivity analysis (optional)

---

## Performance Tips

1. **For Quick Testing**: Use smaller population sizes (50-100) and fewer iterations (20-30)
2. **For Best Results**: Use larger population sizes (500-1000) and more iterations (90-120)
3. **For Comparison**: Use moderate settings (200-400 population, 50-90 iterations) to balance speed and quality

---

## Algorithm Selection Guide

| Algorithm | Best For | Characteristics |
|-----------|----------|----------------|
| **PSO** | General purpose, fast convergence | Good balance of exploration/exploitation |
| **GA** | Complex landscapes, diversity | Strong exploration, handles non-convex problems |
| **ACO** | Discrete/structured problems | Good for combinatorial aspects |

---

## Technical Notes

- All algorithms use the **same cost function** and **constraints**
- Comparison is done on the **same layout** for fair comparison
- Convergence histories are tracked for visualization
- All algorithms respect the same bounds and constraints

---

## Future Enhancements

Potential improvements:
- Hybrid algorithms (PSO-GA, etc.)
- Adaptive parameter tuning
- Multi-objective optimization
- Parallel execution for faster comparison

---

## Questions?

Refer to the main README.md or check the code documentation in:
- `sewer_opt/ga.py` - Genetic Algorithm implementation
- `sewer_opt/aco.py` - Ant Colony Optimization implementation
- `sewer_opt/optimizer.py` - Comparison functionality

