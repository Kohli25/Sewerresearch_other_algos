import os

def get_algorithm_choice():
    """Get algorithm selection from user"""
    while True:
        print("\n" + "=" * 80)
        print("ALGORITHM SELECTION")
        print("=" * 80)
        print("Available algorithms:")
        print("  1. PSO  - Modified Particle Swarm Optimization")
        print("  2. GA   - Genetic Algorithm (Standard)")
        print("  3. AGA  - Adaptive Genetic Algorithm (Flowchart-based)")
        print("  4. ACO  - Ant Colony Optimization")
        print("  5. ALL  - Compare all algorithms")
        print("=" * 80)
        
        choice = input("Select algorithm (1/2/3/4): ").strip()
        
        if choice == "1":
            return "PSO", False
        elif choice == "2":
            return "GA", False
        elif choice == "3":
            return "AGA", False
        elif choice == "4":
            return "ACO", False
        elif choice == "5":
            return "ALL", True
        else:
            print("⚠️ Invalid choice! Please enter 1, 2, 3, 4, or 5.\n")

def get_optimization_settings():
    """Get optimization settings from user"""
    while True:
        default = input("\nUse default settings (Y/N): ").strip().upper()

        if default == "N":
            try:
                n_layouts = int(input("Enter number of top layouts: "))
                population_size = int(input("Enter population/swarm size: "))
                n_iterations = int(input("Enter Max Iterations: "))
                break
            except ValueError:
                print("⚠️ Invalid input! Please enter numeric values.\n")
        
        elif default == "Y":
            n_layouts = 8
            population_size = 800
            n_iterations = 90
            break
        
        else:
            print("⚠️ Please enter only Y or N.\n")

    print("\n✅ Settings Applied Successfully:")
    print(f"Top Layouts      : {n_layouts}")
    print(f"Population Size  : {population_size}")
    print(f"Max Iterations   : {n_iterations}")
    
    return n_layouts, population_size, n_iterations

def get_pso_settings():
    """Legacy function for backward compatibility"""
    n_layouts, population_size, n_iterations = get_optimization_settings()
    return n_layouts, population_size, n_iterations

def ask_and_run_sensitivity(optimizer, best_tree, output_dir="output"):
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
        optimizer.plot_sensitivity_analysis(sensitivity_results, save_path=os.path.join(output_dir, 'sensitivity_analysis.png'))
        print("DETAILED OPTIMAL DESIGN - BEST LAYOUT (Minimum Cost)")
        print("=" * 120)
        print("✅ Sensitivity Analysis Completed Successfully!")
        return sensitivity_results

    else:
        print("⚠️ Please enter only Y or N.\n")
        return ask_and_run_sensitivity(optimizer, best_tree, output_dir=output_dir)

def ask_and_run_comparison(optimizer, best_tree, output_dir="output"):
    """Ask user if they want to run algorithm comparison"""
    run_choice = input("\nDo you want to compare all algorithms? (Y/N): ").strip().upper()

    if run_choice == "N":
        print("\n⏭️ Algorithm comparison skipped.")
        return None

    elif run_choice == "Y":
        default = input("Use default comparison settings? (Y/N): ").strip().upper()

        if default == "N":
            try:
                population_size = int(input("Enter population/swarm size: "))
                n_iterations = int(input("Enter Max Iterations: "))
            except ValueError:
                print("⚠️ Invalid input! Using default values instead.")
                population_size = 100
                n_iterations = 30
        else:
            population_size = 100
            n_iterations = 30

        print("\n⚙️ Running Algorithm Comparison with settings:")
        print(f"Population Size  : {population_size}")
        print(f"Iteration Count  : {n_iterations}\n")

        comparison_results = optimizer.compare_algorithms(
            best_tree,
            population_size=population_size,
            n_iterations=n_iterations
        )

        print("\nGenerating comparison plot...")
        optimizer.plot_algorithm_comparison(
            comparison_results, 
            save_path=os.path.join(output_dir, 'algorithm_comparison.png')
        )
        print("\n✅ Algorithm Comparison Completed Successfully!")
        return comparison_results

    else:
        print("⚠️ Please enter only Y or N.\n")
        return ask_and_run_comparison(optimizer, best_tree, output_dir=output_dir)