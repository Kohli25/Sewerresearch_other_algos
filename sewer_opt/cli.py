def get_pso_settings():
    while True:
        default = input("Use default settings (Y/N): ").strip().upper()

        if default == "N":
            try:
                n_layouts = int(input("Enter number of top layouts: "))
                pso_particles = int(input("Enter number of PSO particles: "))
                pso_iterations = int(input("Enter Max Iterations: "))
                break
            except ValueError:
                print("⚠️ Invalid input! Please enter numeric values.\n")
        
        elif default == "Y":
            n_layouts = 8
            pso_particles = 800
            pso_iterations = 90
            break
        
        else:
            print("⚠️ Please enter only Y or N.\n")

    print("\n✅ Settings Applied Successfully:")
    print(f"Top Layouts     : {n_layouts}")
    print(f"PSO Particles   : {pso_particles}")
    print(f"Max Iterations  : {pso_iterations}")
    
    return n_layouts, pso_particles, pso_iterations

def ask_and_run_sensitivity(optimizer, best_tree):
    run_choice = input("Do you want to run Sensitivity Analysis? (Y/N): ").strip().upper()

    if run_choice == "N":
        print("\n⏭️ Sensitivity analysis skipped.")
        return None

    elif run_choice == "Y":
        default = input("Use default sensitivity settings? (Y/N): ").strip().upper()

        if default == "N":
            try:
                swarm_sizes = list(map(int, input("Enter swarm sizes (comma-separated): ").split(",")))
                iterations_list = list(map(int, input("Enter iteration list (comma-separated): ").split(",")))
            except ValueError:
                print("⚠️ Invalid input! Using default values instead.")
                swarm_sizes = [200, 400, 600, 800, 1000]
                iterations_list = [30, 60, 90, 120]
        else:
            swarm_sizes = [200, 400, 600, 800, 1000]
            iterations_list = [30, 60, 90, 120]

        print("\n⚙️ Running Sensitivity Analysis with settings:")
        print(f"Swarm Sizes      : {swarm_sizes}")
        print(f"Iteration Counts : {iterations_list}\n")

        sensitivity_results = optimizer.run_sensitivity_analysis(
            best_tree,
            swarm_sizes=swarm_sizes,
            iterations_list=iterations_list
        )

        print("\nGenerating sensitivity analysis plot...")
        optimizer.plot_sensitivity_analysis(sensitivity_results, save_path='output/sensitivity_analysis.png')
        print("DETAILED OPTIMAL DESIGN - BEST LAYOUT (Minimum Cost)")
        print("=" * 120)
        print("✅ Sensitivity Analysis Completed Successfully!")
        return sensitivity_results

    else:
        print("⚠️ Please enter only Y or N.\n")
        return ask_and_run_sensitivity(optimizer, best_tree)