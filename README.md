# 🏗️ Sewer Network Design using PSO (Particle Swarm Optimization)

This project automates **Sewer Network Design** using **Particle Swarm Optimization (PSO)** based on **hydraulic and functional constraints**. It determines the **optimal pipe diameters, slopes, and layout** that minimize cost while satisfying flow and velocity requirements.

---

## 🚀 Features

✅ Automatic optimal design of sewer networks  
✅ Uses **PSO algorithm** for global search  
✅ Handles multiple design scenarios  
✅ Sensitivity analysis (Swarm size vs Iterations)  
✅ Input validation for hydraulic constraints  
✅ Results exported to CSV & visual graph plots  
✅ User-friendly console input for settings  
✅ Modular & scalable code structure

---

## 📂 Project Structure

```
SND_PSO_CODE/
│
├── SND/
│   ├── input/
│   │   ├── <Input network text files>
│   ├── output/
│   │   ├── result_layout.png
│   │   ├── sensitivity_analysis.png
│   │   ├── *_results.csv
│   ├── sewer_design_code.ipynb
│
├── README.md  ← (This File)
```

✅ All input networks go inside **SND/input**  
✅ All result outputs auto-save inside **SND/output**

---

## 🧠 How it Works

1️⃣ Load network nodes and pipe connectivity  
2️⃣ Initialize PSO with:
- Particle positions = Design variable set (diameter + slope)
- Objective function = Cost minimization  

3️⃣ Evaluate each solution using:
- Velocity checks  
- d/D constraint (partial/full flow)
- Minimum slope requirements  

4️⃣ Best solution stored as **best_tree**  
5️⃣ Optionally: perform **Sensitivity Analysis**

---

## 🔧 Configurable Parameters

When running the script, it asks user for input:

| Parameter | Default | Description |
|----------|---------|-------------|
| n_layouts | 8 | No. of top design layouts to evaluate |
| pso_particles | 10 | Swarm population |
| pso_iterations | 10 | Maximum optimization cycles |
| Sensitivity | Optional | Switch ON/OFF |

Supports both:
- ✅ User custom settings  
- ✅ Auto default settings  

---

## 📊 Output Results

The tool generates:

| Result Type | File |
|------------|------|
| Best network design CSV | `*_results.csv` |
| Sewer network plot | `result_layout.png` |
| Sensitivity performance graph | `sensitivity_analysis.png` |

CSV includes:
- Pipe IDs  
- Diameters  
- Flow velocity  
- d/D ratio  
- Coordinate-based hydraulic details  

---

## 🧪 Sample Command Execution

Run the notebook or script directly:

```bash
python sewer_design_code.py
```

🔥 The program automatically:
✔ Runs PSO  
✔ Saves results  
✔ Visualizes sewer layout

---

## 🌍 Applications

✔ Urban drainage planning  
✔ Municipal sewer design optimization  
✔ Research and academic studies  
✔ Cost-efficient design modelling  

---

## 🧩 Sensitivity Analysis

Helps determine:
- Best **Swarm Size**  
- Optimal **Iteration Count**  
- Convergence behavior of PSO

Used parameters example:

```python
swarm_sizes = [200, 400, 600, 800, 1000]
iterations_list = [30, 60, 90, 120]
```

---

## 🧑‍💻 Requirements

- Python 3.8+
- Pandas
- NumPy
- Matplotlib
- Any supported PSO module (custom included in this repo)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 📌 Future Enhancements

- GUI-based user input for better UX  
- Support for multiple pipe materials  
- Integration with EPANET / SWMM hydraulic models  
- Cloud execution support  

---

## 👤 Author

**Sumit Kumar**  
Civil Engineering | Sewer Design Optimization  
📧 Contact via GitHub issues

---

## 🤝 Contribution

Pull Requests are welcome!  
If you want to add new features, just:

1. Create a new branch  
2. Commit your changes  
3. Submit a Pull Request with details  
