# 🏗️ Sewer Network Design Optimization using Modified PSO

This repository contains a modular Python framework for **Sewer Network Design Optimization** using **Particle Swarm Optimization (PSO)**.  
It automatically finds optimal sewer layout spanning trees + optimal pipe diameters, slopes & costs subject to hydraulic + functional constraints.

---

## 🚀 Features

- Generates multiple sewer network spanning trees (ranked by cumulative flow)
- Modified PSO based component sizing (Diameter + Slope per link)
- Full hydraulic validation (velocity, d/D, cover depth, progressive diameter)
- Cost optimization (pipe, earthwork, manhole)
- Sensitivity Analysis support (Swarm Size vs Iterations)
- CSV output + Graph Visualization auto saved

---

## 📂 Project Structure

```
SND_PSO_CODE/
│
├── main.py                       # main runner script
├── requirements.txt
├── .gitignore
└── sewer_opt/
    ├── models.py
    ├── hydraulics.py
    ├── costs.py
    ├── pso.py
    ├── spanning_tree.py
    ├── optimizer.py
    ├── graph_utils.py
    ├── parsers.py
    ├── cli.py
    └── input/
        ├── LiMathew_Revised.txt
        └── CedritosNorte.txt
```

> Place all input TXT networks inside `sewer_opt/input/`  
> Outputs (plots/CSV) are generated in `/output/` automatically.

---

## ▶️ Run

```bash
python main.py
```

The script will interactively ask:

| Parameter | Description |
|----------|-------------|
| Number of spanning tree layouts to test | e.g. 5 or 8 |
| No. of PSO Particles | e.g. 10, 30, 60 |
| Max PSO Iterations | e.g. 10, 30, 90 |
| Sensitivity analysis | Yes/No |

---

## 📊 Generated Outputs

| Result Type | File |
|-------------|------|
| Best design CSV | `output/*_results.csv` |
| Sewer Network layout plot | `output/result_layout.png` |
| Sensitivity analysis plot | `output/sensitivity_analysis.png` |

---

## Requirements

```bash
pip install -r requirements.txt
```

Tested Python Version: **Python 3.9+**

---

## Applications

- Urban Drainage Design
- Research & Academic Optimization Studies
- Municipal Sewer System Cost Minimization
- Net Zero Event Infrastructure Planning

---

## Author

**Sumit Kumar (Octodo Solutions)**  
Civil Engineering | Optimization | PSO Research

---

## Contributions

Pull Requests welcomed.  
Raise issues for bugs / enhancements.
