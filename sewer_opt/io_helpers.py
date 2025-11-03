import csv, os
import pandas as pd


def safe_float(value, decimals=None):
    if value is None or value == "":
        return ""
    try:
        v = float(value)
        return round(v, decimals) if decimals is not None else v
    except:
        return ""

def save_results_with_input_details(
    Input_file: str,
    nodes_df,
    nodes_data: dict,
    best_details: list,
    output_dir: str = "output"
):
    base_name = os.path.splitext(os.path.basename(Input_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}_results.csv")

    required_cols = ["x", "y", "elevation", "flow"]
    for col in required_cols:
        if col not in nodes_df.columns:
            raise KeyError(f"Column '{col}' not found in nodes_df")

    fieldnames = [
        'link', 'from_node', 'to_node', 'length', 'diameter', 'slope', 'slope_ratio',
        'flow_lps', 'velocity', 'd_D', 'd', 'status', 'max_preceding_diameter',
        'input_flow_lps', 'x', 'y', 'z'
    ]

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for detail in best_details:
            from_node = detail.get('from_node')
            node_info = nodes_df.loc[from_node] if from_node in nodes_df.index else None

            input_flow = x = y = z = ""
            if node_info is not None:
                input_flow = safe_float(node_info['flow'] * 1000, 3)
                x = safe_float(node_info['x'])
                y = safe_float(node_info['y'])
                z = safe_float(node_info['elevation'])

            flow_lps = detail.get('flow_lps')
            if flow_lps is None and 'flow' in detail:
                flow_lps = detail['flow'] * 1000

            writer.writerow({
                'link': detail.get('link', ''),
                'from_node': from_node,
                'to_node': detail.get('to_node', ''),
                'input_flow_lps': input_flow,
                'x': x,
                'y': y,
                'z': z,
                'length': safe_float(detail.get('length'), 2),
                'diameter': detail.get('diameter', ''),
                'slope': safe_float(detail.get('slope'), 2),
                'slope_ratio': detail.get('slope_ratio', ''),
                'flow_lps': safe_float(flow_lps, 3),
                'velocity': safe_float(detail.get('velocity'), 2),
                'd_D': safe_float(detail.get('d_D'), 3),
                'd': safe_float(detail.get('d'), 3),
                'status': detail.get('status', ''),
                'max_preceding_diameter': detail.get('max_preceding_diameter', '')
            })

    print(f"✅ Results with input details saved to: {output_file}")
    return output_file