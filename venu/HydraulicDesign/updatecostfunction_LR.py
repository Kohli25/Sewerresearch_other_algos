import pandas as pd
import csv
import os
import sys
# Automatically add project root to sys.path
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def update_cost_with_direction_check(input_file, result_file, output_file):
    # Load input and result files
    df_input = pd.read_excel(input_file,sheet_name='Input_Iter2')
    df_result = pd.read_excel(result_file,sheet_name='Result_hydraulic_2')

    # Ensure consistent column names
    df_input = df_input[['i', 'j', 'c_ij', 'a_ij']]  # We only need node pairs from input
    df_result = df_result[['i', 'j', 'q_ij', 'cost_ij']]

    updated_rows = []

    for _, row in df_input.iterrows():
        orig_i, orig_j = row['i'], row['j']
        orig_c, orig_a = row['c_ij'], row['a_ij']

        # Flag to track if match found
        direction_updated = False

        # Try original direction
        match = df_result[(df_result['i'] == orig_i) & (df_result['j'] == orig_j)]

        if match.empty:
            # Try reversed direction
            match = df_result[(df_result['i'] == orig_j) & (df_result['j'] == orig_i)]
            if not match.empty:
                i, j = orig_j, orig_i  # Reverse direction
                direction_updated = True
            else:
                # No match at all, keep original
                updated_rows.append({
                    'i': orig_i,
                    'j': orig_j,
                    'c_ij': orig_c,
                    'a_ij': orig_a
                })
                continue
        else:
            i, j = orig_i, orig_j  # Keep original direction

        match_row = match.iloc[0]
        q = match_row['q_ij']
        cost = match_row['cost_ij']

        if q == 0:
            print(f"⚠️ Zero flow for pipe ({i}, {j}), retaining original cost.")
            updated_rows.append({
                'i': orig_i if not direction_updated else orig_j,
                'j': orig_j if not direction_updated else orig_i,
                'c_ij': orig_c,
                'a_ij': orig_a
            })
            continue

        c_ij = cost / q

        updated_rows.append({
            'i': i,
            'j': j,
            'c_ij': c_ij,
            'a_ij': 0
        })

    # Prepare DataFrame
    df_output = pd.DataFrame(updated_rows)
    df_output.to_excel(output_file, index=False)
    print(f"✅ Updated iteration 3 input saved to: {output_file}")

# --- Run with your file paths ---
update_cost_with_direction_check(
    input_file=os.path.join(project_root, "Files","Input_LiMathew.xlsx"),
    result_file=os.path.join(project_root,"Files","Input_LiMathew.xlsx"),
    output_file=os.path.join(project_root, "Files", "Input_LiMathew3.xlsx")
)
