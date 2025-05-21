import csv
import os
import sys
# Automatically add project root to sys.path
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def export_arc_costs_to_layout_format(solution_arcs, output_file=os.path.join(project_root, "Files", "observed_layout_costs.csv")):
    with open(output_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['i', 'j', 't', 'q_ij', 'cost_ij'])

        for arc in solution_arcs:
            i = arc.dn_up.ls_node.my_manhole.id
            j = arc.dn_down.ls_node.my_manhole.id
            t = arc.type              # 1 = pipe, 2 = vertical drop
            q = arc.flow             # discharge
            cost = arc.arc_cost      # actual hydraulic cost

            writer.writerow([i, j, t, q, cost])
    
    print(f"Exported cost file for layout model to: {output_file}") 