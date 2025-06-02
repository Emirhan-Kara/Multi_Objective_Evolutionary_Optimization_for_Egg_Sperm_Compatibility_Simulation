import Config
from Sperm import Sperm
from Egg import Egg
from Evaluate import evaluate_population
from Visuals import plot_fronts
from Selection import crowded_tournament_selection
from Variation import variation
from Survivor import rank_filtering
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time

def generate_population(size=Config.POPULATION_SIZE):
    P_t = []
    for _ in range(size):
        P_t.append(Sperm())
    
    return P_t

def animate_population_evolution(saved_populations, generation_numbers):
    """
    Animate the evolution of populations with fixed axis limits
    Only includes objective space visualization with enlarged fonts
    """
    fig, ax1 = plt.subplots(figsize=(10, 10))

    # Set font sizes
    label_fontsize = 24
    title_fontsize = 28
    tick_fontsize = 18
    gen_text_fontsize = 24
    cbar_fontsize = 18

    # Objective space
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_xlabel("Genetic Compatibility (Objective 1)", fontsize=label_fontsize)
    ax1.set_ylabel("Biological Quality (Objective 2)", fontsize=label_fontsize)
    ax1.set_title("Population Evolution in Objective Space", fontsize=title_fontsize)
    ax1.tick_params(axis='both', labelsize=tick_fontsize)
    ax1.grid(True, alpha=0.3)

    # Scatter plot in objective space
    scatter = ax1.scatter([], [], s=80, c=[], cmap='viridis', alpha=0.6, edgecolors='black')

    # Generation text
    gen_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes,
                        fontsize=gen_text_fontsize, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Colorbar for genetic resources
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=10, vmax=90))
    cbar = plt.colorbar(sm, ax=ax1)
    cbar.set_label('Genetic Resources', fontsize=cbar_fontsize)
    cbar.ax.tick_params(labelsize=tick_fontsize)

    def update_plot(frame):
        population = saved_populations[frame]
        gen_num = generation_numbers[frame]

        x = [ind.objectives[0] for ind in population]
        y = [ind.objectives[1] for ind in population]
        colors = [ind.genetic_resources for ind in population]

        scatter.set_offsets(np.c_[x, y])
        scatter.set_array(np.array(colors))
        gen_text.set_text(f'Generation: {gen_num}')

        return scatter, gen_text

    ani = animation.FuncAnimation(fig, update_plot, frames=len(saved_populations),
                                  interval=100, blit=False, repeat=True)

    plt.tight_layout()
    plt.show()
    return ani

"""
def plot_objective_progression(pareto_front_history, generation_numbers):
    # Calculate average values
    avg_obj1, avg_obj2 = [], []
    avg_genetic_res, avg_biological_res = [], []

    for front in pareto_front_history:
        if len(front) > 0:
            avg_obj1.append(np.mean([ind.objectives[0] for ind in front]))
            avg_obj2.append(np.mean([ind.objectives[1] for ind in front]))
            avg_genetic_res.append(np.mean([ind.genetic_resources for ind in front]))
            avg_biological_res.append(np.mean([ind.biological_resources for ind in front]))
        else:
            avg_obj1.append(0)
            avg_obj2.append(0)
            avg_genetic_res.append(50)
            avg_biological_res.append(50)

    # Create figure
    fig = plt.figure(figsize=(18, 12))

    label_fontsize = 24
    title_fontsize = 28
    tick_fontsize = 20
    marker_size = 12
    scatter_size = 200

    # Objective 1 progression
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(generation_numbers, avg_obj1, 'b-o', linewidth=3, markersize=marker_size)
    ax1.set_xlabel('Generation', fontsize=label_fontsize)
    ax1.set_ylabel('Average Genetic Compatibility', fontsize=label_fontsize)
    ax1.set_title('Objective 1: Genetic Compatibility Progress', fontsize=title_fontsize)
    ax1.tick_params(axis='both', labelsize=tick_fontsize)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)

    # Objective 2 progression
    ax2 = plt.subplot(2, 2, 2)
    ax2.plot(generation_numbers, avg_obj2, 'g-o', linewidth=3, markersize=marker_size)
    ax2.set_xlabel('Generation', fontsize=label_fontsize)
    ax2.set_ylabel('Average Biological Quality', fontsize=label_fontsize)
    ax2.set_title('Objective 2: Biological Quality Progress', fontsize=title_fontsize)
    ax2.tick_params(axis='both', labelsize=tick_fontsize)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1)

    # Resource allocation
    ax3 = plt.subplot(2, 2, 3)
    ax3.plot(generation_numbers, avg_genetic_res, 'r-o', linewidth=3, markersize=marker_size, label='Genetic')
    ax3.plot(generation_numbers, avg_biological_res, 'm-o', linewidth=3, markersize=marker_size, label='Biological')
    ax3.set_xlabel('Generation', fontsize=label_fontsize)
    ax3.set_ylabel('Average Resources', fontsize=label_fontsize)
    ax3.set_title('Resource Allocation in Pareto Front', fontsize=title_fontsize)
    ax3.tick_params(axis='both', labelsize=tick_fontsize)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 100)
    ax3.legend(fontsize=label_fontsize)

    # Final Pareto front scatter
    ax4 = plt.subplot(2, 2, 4)
    if len(pareto_front_history) > 0:
        final_front = pareto_front_history[-1]
        x_final = [ind.objectives[0] for ind in final_front]
        y_final = [ind.objectives[1] for ind in final_front]
        colors_final = [ind.genetic_resources for ind in final_front]
        scatter = ax4.scatter(x_final, y_final, c=colors_final, cmap='viridis',
                              s=scatter_size, alpha=0.7, edgecolors='black')
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('Genetic Resources', fontsize=label_fontsize)
        cbar.ax.tick_params(labelsize=tick_fontsize)

    ax4.set_xlabel('Genetic Compatibility', fontsize=label_fontsize)
    ax4.set_ylabel('Biological Quality', fontsize=label_fontsize)
    ax4.set_title('Final Pareto Front', fontsize=title_fontsize)
    ax4.tick_params(axis='both', labelsize=tick_fontsize)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)

    plt.suptitle('Evolution Progress with Resource Allocation', fontsize=30)
    plt.tight_layout()
    plt.show()

    # Final statistics
    print(f"\nFinal Pareto Front Statistics:")
    print(f"Average Genetic Compatibility: {avg_obj1[-1]:.4f}")
    print(f"Average Biological Quality: {avg_obj2[-1]:.4f}")
    print(f"Average Genetic Resources: {avg_genetic_res[-1]:.2f}")
    print(f"Average Biological Resources: {avg_biological_res[-1]:.2f}")

    if len(pareto_front_history) > 0:
        final_front = pareto_front_history[-1]
        if len(final_front) > 1:
            obj1_vals = [ind.objectives[0] for ind in final_front]
            obj2_vals = [ind.objectives[1] for ind in final_front]
            correlation = np.corrcoef(obj1_vals, obj2_vals)[0, 1]
            print(f"Correlation between objectives: {correlation:.3f}")
"""

def main():
    egg = Egg()
    P_t = generate_population()
    
    # Storage for Task 1 and Task 2
    saved_populations = []
    pareto_front_history = []
    generation_numbers = []
    
    # Initial evaluation
    fronts = evaluate_population(P_t, egg)
    plot_fronts(fronts)
    
    # Save initial state
    saved_populations.append([ind.copy() for ind in P_t])
    pareto_front_history.append([ind.copy() for ind in fronts[0]])
    generation_numbers.append(0)
    
    # Print initial resource distribution
    print("\nInitial Population Resource Distribution:")
    genetic_resources = [ind.genetic_resources for ind in P_t]
    print(f"Genetic Resources - Min: {min(genetic_resources):.1f}, "
          f"Max: {max(genetic_resources):.1f}, "
          f"Mean: {np.mean(genetic_resources):.1f}")

    for t in range(1, Config.NUM_OF_GENERATIONS + 1):
        print(f"\nGeneration NO: {t}")

        M_t = crowded_tournament_selection(P_t, Config.MATING_POOL_SIZE)
        Q_t = variation(M_t, Config.CROSSOVER_RATE, Config.MUTATION_RATE)
        R_t = Q_t + P_t
        fronts = evaluate_population(R_t, egg, t)
        P_t = rank_filtering(fronts, Config.POPULATION_SIZE)
        
        # Save populations and fronts at specified intervals
        if t % Config.SAVE_EACH_N_GENERATION == 0 or t == 2 or t == 4 or t == 6 or t == 8 or t == 15 or t == 25 or t == 35 or t == 45:
            saved_populations.append([ind.copy() for ind in P_t])
            pareto_front_history.append([ind.copy() for ind in fronts[0]])
            generation_numbers.append(t)
            print(f"  -> Saved population and Pareto front at generation {t}")


    
    # Task 1: Animate population evolution
    ani = animate_population_evolution(saved_populations, generation_numbers)
    
    # Task 2: Plot objective progression
    #plot_objective_progression(pareto_front_history, generation_numbers)
    
    # Final Pareto front visual
    plot_fronts(fronts)

if __name__ == "__main__":
    main()