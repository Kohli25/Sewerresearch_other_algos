import os
import pandas as pd
import numpy as np


from sewer_opt import (
    Node,
    SewerNetworkOptimizer,
    parse_sewer_file_1,
    build_weighted_graph,
    save_results_with_input_details,
    plot_graph_with_coords,
)
from sewer_opt.cli import get_pso_settings, ask_and_run_sensitivity


if __name__ == "__main__":
    # ===================== Input & settings =====================
    Input_file = 'input/LiMathew_Revised.txt'
    Name = str(Input_file)

    nodes_df, edges_df = parse_sewer_file_1(Input_file)
    n_layouts, pso_particles, pso_iterations = get_pso_settings()

    # ===================== Graph build ==========================
    G, outlet_id = build_weighted_graph(nodes_df, edges_df)

    nodes_data = {}
    for nid, row in nodes_df.iterrows():
        nodes_data[nid] = Node(
            id=nid,
            wastewater_contribution=round(float(row['flow'] * 1000), 3),
            ground_level=float(row["elevation"])
        )

    print("=" * 80)
    print(f"SEWER NETWORK OPTIMIZATION - {len(nodes_df)} MANHOLE NETWORK")
    print("=" * 80)

    total_inflow = sum(n.wastewater_contribution for n in nodes_data.values() if n.wastewater_contribution > 0)
    outlet_flow = abs(nodes_data[outlet_id].wastewater_contribution)
    print(f"  Total Inflow: {total_inflow:.2f} l/s ({total_inflow/1000:.4f} m³/s)")
    print(f"  Outlet Flow: {outlet_flow:.2f} l/s ({outlet_flow/1000:.4f} m³/s)")
    print(f"  Flow Balance: {'✓ OK' if abs(total_inflow - outlet_flow) < 1 else '✗ Imbalanced'}")

    optimizer = SewerNetworkOptimizer(G, nodes_data, outlet_id)

    print("\n" + "=" * 80)
    print(f"Starting Optimization Process for {Name}...")
    print("=" * 80)

    results = optimizer.optimize_layout_sequence(
        n_layouts,
        pso_particles,
        pso_iterations
    )

    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS - ALL LAYOUTS")
    print("=" * 80)
    print(f"\n{'Rank':<6} {'Layout':<8} {'CQ (m³/s)':<12} {'CQ (l/s)':<12} {'Total Cost (Rs.)':<20}")
    print("-" * 65)
    for rank, (layout_num, cq, cost, _, _) in enumerate(results[:10], 1):
        marker = "★ BEST" if rank == 1 else ""
        print(f"{rank:<6} {layout_num:<8} {cq:<12.4f} {cq*1000:<12.2f} {cost:>18,.2f}  {marker}")

    if results:
        best_layout_num, best_cq, best_cost, best_tree, best_details = results[0]

        # Save CSV
        save_results_with_input_details(Input_file, nodes_df, nodes_data, best_details)

        print(f"\n✓ Best Layout: #{best_layout_num}")
        print(f"✓ Total Cumulative Flow (CQ): {best_cq:.4f} m³/s ({best_cq*1000:.2f} l/s)")
        print(f"✓ TOTAL NETWORK COST: Rs. {best_cost:,.2f} ★ MINIMUM ★")
        print(f"✓ Number of Sewer Sections: {len(best_details)}")

        # Print header
        print(f"\n{'Pipe':<6} {'From':<6} {'To':<6} {'Length':<9} {'Diameter':<10} {'Slope':<14} "
              f"{'Flow':<11} {'Velocity':<10} {'d/D':<8} {'d (m)':<8} {'Prev D':<10} {'Status':<25}")
        print(f"{'No.':<6} {'Node':<6} {'Node':<6} {'(m)':<9} {'(mm)':<10} {'(1 in X)':<14} "
              f"{'(l/s)':<11} {'(m/s)':<10} {'':<8} {'':<8} {'(mm)':<10} {'':<25}")
        print("-" * 140)

        # Print each link
        total_length = 0
        valid_links = 0
        progressive_violations = 0

        

        for detail in best_details:
            link = detail['link']
            from_node = detail['from_node']
            to_node = detail['to_node']
            length = detail['length']
            diameter = detail['diameter']
            slope = detail['slope']
            slope_ratio = detail['slope_ratio']
            flow_lps = detail.get('flow_lps', detail['flow'] * 1000)
            velocity = detail['velocity']
            d_D = detail['d_D']
            d = detail['d']
            status = detail['status']
            max_preceding_diameter = detail.get('max_preceding_diameter', None)

            total_length += length
            if status == 'OK':
                valid_links += 1

            if 'D_prog' in status:
                progressive_violations += 1

            # Format values
            diameter_mm = diameter * 1000
            vel_str = f"{velocity:.3f}" if velocity is not None else "N/A"
            d_D_str = f"{d_D:.4f}" if d_D is not None else "N/A"
            d_str = f"{d:.4f}" if d is not None else "N/A"
            prev_d_str = f"{max_preceding_diameter*1000:.0f}" if max_preceding_diameter else "-"

            # Color code status
            status_display = status if len(status) <= 25 else status[:22] + "..."

            print(f"{link:<6} {from_node:<6} {to_node:<6} {length:<9.2f} {diameter_mm:<10.0f} "
                  f"{slope_ratio:<14} {flow_lps:<11.3f} {vel_str:<10} {d_D_str:<8} "
                  f"{d_str:<8} {prev_d_str:<10} {status_display:<25}")
            
        # plot the graph 
        plot_graph_with_coords(best_tree,"output_graph",show_lengths=False,show_elevation=False)

        print("-" * 140)
        print(f"Total Network Length: {total_length:.2f} m")
        print(f"Valid Links (All constraints satisfied): {valid_links}/{len(best_details)}")
        if progressive_violations > 0:
            print(f"⚠ Progressive Diameter Violations: {progressive_violations}")

        # Detailed statistics
        print("\n" + "=" * 120)
        print("DESIGN STATISTICS AND CONSTRAINT VERIFICATION")
        print("=" * 120)

        velocities = [d['velocity'] for d in best_details if d['velocity'] is not None]
        d_D_ratios = [d['d_D'] for d in best_details if d['d_D'] is not None]
        diameters = [d['diameter'] * 1000 for d in best_details]
        flows = [d.get('flow_lps', d['flow'] * 1000) for d in best_details]

        print("\n📊 HYDRAULIC PARAMETERS:")
        if velocities:
            print(f"  Velocity Statistics:")
            print(f"    • Minimum: {min(velocities):.3f} m/s")
            print(f"    • Maximum: {max(velocities):.3f} m/s")
            print(f"    • Average: {np.mean(velocities):.3f} m/s")
            print(f"    • Std Dev: {np.std(velocities):.3f} m/s")

            below_min = sum(1 for v in velocities if v < 0.6)
            above_max = sum(1 for v in velocities if v > 3.0)
            print(f"    • Links below 0.6 m/s: {below_min}")
            print(f"    • Links above 3.0 m/s: {above_max}")

        if d_D_ratios:
            print(f"\n  d/D Ratio Statistics:")
            print(f"    • Minimum: {min(d_D_ratios):.4f}")
            print(f"    • Maximum: {max(d_D_ratios):.4f}")
            print(f"    • Average: {np.mean(d_D_ratios):.4f}")
            above_08 = sum(1 for r in d_D_ratios if r > 0.8)
            print(f"    • Links above 0.8: {above_08}")

        print(f"\n  Diameter Distribution:")
        unique_diameters = sorted(set(diameters))
        for d in unique_diameters:
            count = sum(1 for dia in diameters if dia == d)
            print(f"    • {d:.0f} mm: {count} links")

        print(f"\n  Flow Statistics:")
        print(f"    • Minimum: {min(flows):.3f} l/s")
        print(f"    • Maximum: {max(flows):.3f} l/s")
        print(f"    • Average: {np.mean(flows):.3f} l/s")

        print("\n✓ CONSTRAINT LIMITS:")
        print("    • Velocity: 0.6 - 3.0 m/s")
        print("    • d/D ratio: ≤ 0.8")
        print("    • Min diameter: 200 mm")
        print("    • Cover depth: 0.9 - 5.0 m")
        print("    • Progressive diameter: D_current ≥ D_preceding (Eq. 11) - ENFORCED BY SELECTION")

        # Check if any diameters were increased to satisfy progressive constraint
        enforced_increases = [d for d in best_details if d.get('enforced_increase', False)]
        if enforced_increases:
            print(f"\n⚙ Progressive Diameter Adjustments:")
            print(f"    • {len(enforced_increases)} pipe(s) had diameter increased to satisfy Eq. 11")
            for detail in enforced_increases[:5]:  # Show first 5
                link = detail['link']
                proposed = detail.get('proposed_diameter', 0) * 1000
                actual = detail['diameter'] * 1000
                print(f"      Link {link}: {proposed:.0f}mm → {actual:.0f}mm")

        # Cost breakdown
        print("\n💰 COST SUMMARY:")
        print(f"    • Total Network Cost: Rs. {best_cost:,.2f}")
        print(f"    • Cost per meter: Rs. {best_cost/total_length:,.2f}/m")

        print("\n" + "=" * 120)
        
        
        
        #============================================RUN SESITIVITY ANALYSIS=======================================

        # sensitivity_results = ask_and_run_sensitivity(best_tree)
        sensitivity_results = ask_and_run_sensitivity(optimizer, best_tree)
