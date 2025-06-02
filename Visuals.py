import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm

def plot_fronts(fronts, title=""):
    """Visualize only Pareto fronts with distinct colors and larger fonts and dots."""
    fig, ax = plt.subplots(figsize=(8, 7))

    num_fronts = len(fronts)
    colormap = cm.get_cmap('nipy_spectral', num_fronts)

    for i, front in enumerate(fronts):
        x = [ind.objectives[0] for ind in front]
        y = [ind.objectives[1] for ind in front]
        ax.scatter(x, y, label=f"Front {i+1}", color=colormap(i), s=200, edgecolors='k')  # s=120 for bigger dots

    ax.set_xlabel("Genetic Compatibility (Objective 1)", fontsize=25)
    ax.set_ylabel("Biological Quality (Objective 2)", fontsize=25)
    ax.set_title(title, fontsize=20)
    ax.legend(fontsize=25)
    ax.grid(True)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.tick_params(axis='both', labelsize=20)

    plt.tight_layout()
    plt.show()



def plot_fronts_with_resources(fronts, title="Pareto Fronts with Resource Coloring"):
    """Plot Pareto fronts where color indicates resource allocation"""
    plt.figure(figsize=(12, 9))
    
    # Combine all fronts for consistent color scaling
    all_genetic_resources = []
    for front in fronts:
        all_genetic_resources.extend([ind.genetic_resources for ind in front])
    
    vmin = min(all_genetic_resources) if all_genetic_resources else 10
    vmax = max(all_genetic_resources) if all_genetic_resources else 90
    
    # Plot each front
    for i, front in enumerate(fronts):
        if len(front) == 0:
            continue
            
        x = [ind.objectives[0] for ind in front]
        y = [ind.objectives[1] for ind in front]
        colors = [ind.genetic_resources for ind in front]
        
        # Size based on front rank (front 1 is larger)
        sizes = 100 - i * 20 if i < 4 else 20
        
        scatter = plt.scatter(x, y, c=colors, cmap='RdBu_r', 
                            s=sizes, alpha=0.7, edgecolors='black',
                            vmin=vmin, vmax=vmax)
    
    plt.colorbar(scatter, label='Genetic Resources')
    plt.xlabel("Genetic Compatibility (Objective 1)", fontsize=12)
    plt.ylabel("Biological Quality (Objective 2)", fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    
    # Add diagonal line to show theoretical trade-off
    x_line = np.linspace(0, 1, 100)
    y_line = 1 - x_line
    plt.plot(x_line, y_line, 'k--', alpha=0.3, label='Perfect Trade-off')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def analyze_population_diversity(population):
    """Analyze and visualize diversity in the population"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))
    
    # Extract data
    obj1_values = [ind.objectives[0] for ind in population]
    obj2_values = [ind.objectives[1] for ind in population]
    genetic_res = [ind.genetic_resources for ind in population]
    biological_res = [ind.biological_resources for ind in population]
    hla_lengths = [len(ind.hla_profile) for ind in population]
    
    # 1. Objective space scatter
    scatter1 = ax1.scatter(obj1_values, obj2_values, c=genetic_res, 
                          cmap='viridis', s=50, alpha=0.6)
    ax1.set_xlabel('Genetic Compatibility')
    ax1.set_ylabel('Biological Quality')
    ax1.set_title('Objective Space')
    plt.colorbar(scatter1, ax=ax1, label='Genetic Resources')
    
    # 2. Resource distribution histogram
    ax2.hist([genetic_res, biological_res], bins=20, label=['Genetic', 'Biological'],
             alpha=0.7, color=['blue', 'red'])
    ax2.set_xlabel('Resources')
    ax2.set_ylabel('Count')
    ax2.set_title('Resource Distribution')
    ax2.legend()
    
    # 3. HLA profile length vs genetic resources
    ax3.scatter(genetic_res, hla_lengths, alpha=0.6)
    ax3.set_xlabel('Genetic Resources')
    ax3.set_ylabel('HLA Profile Length')
    ax3.set_title('HLA Complexity vs Resources')
    
    # Add theoretical line
    x_theory = np.linspace(10, 90, 100)
    y_theory = np.minimum(6, np.maximum(2, x_theory / 15))
    ax3.plot(x_theory, y_theory, 'r--', label='Theoretical Max')
    ax3.legend()
    
    # 4. Correlation matrix
    correlation_matrix = np.corrcoef([obj1_values, obj2_values, genetic_res])
    im = ax4.imshow(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    ax4.set_xticks([0, 1, 2])
    ax4.set_yticks([0, 1, 2])
    ax4.set_xticklabels(['Obj1', 'Obj2', 'Gen.Res.'])
    ax4.set_yticklabels(['Obj1', 'Obj2', 'Gen.Res.'])
    ax4.set_title('Correlation Matrix')
    
    # Add correlation values
    for i in range(3):
        for j in range(3):
            text = ax4.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                           ha="center", va="center", color="black")
    
    plt.colorbar(im, ax=ax4)
    
    plt.suptitle(f'Population Diversity Analysis (n={len(population)})', fontsize=16)
    plt.tight_layout()
    plt.show()
    
    # Print statistics
    print("\nPopulation Statistics:")
    print(f"Objective 1 - Min: {min(obj1_values):.3f}, Max: {max(obj1_values):.3f}, Mean: {np.mean(obj1_values):.3f}")
    print(f"Objective 2 - Min: {min(obj2_values):.3f}, Max: {max(obj2_values):.3f}, Mean: {np.mean(obj2_values):.3f}")
    print(f"Correlation between objectives: {np.corrcoef(obj1_values, obj2_values)[0,1]:.3f}")
    print(f"Average genetic resources: {np.mean(genetic_res):.1f}")
    print(f"Average HLA profile length: {np.mean(hla_lengths):.1f}")