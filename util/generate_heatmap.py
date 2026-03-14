import matplotlib.pyplot as plt
import seaborn as sns


def generate_heatmap(coords_list, title, minimap_width, minimap_height):
    """
    Takes a list of (x, y) coordinates and generates a smooth density heatmap.
    """
    # Failsafe if the list is empty
    if not coords_list:
        print(f"No data to plot for {title}!")
        return

    # Split our list of (x,y) tuples into two separate lists for the graph
    x_coords = [point[0] for point in coords_list]
    y_coords = [point[1] for point in coords_list]

    # Set up the canvas
    plt.figure(figsize=(8, 6))

    # Create the smooth heatmap using Seaborn
    # 'cmap' sets the colour scheme. 'magma' gives that classic dark-to-bright-yellow look.
    sns.kdeplot(x=x_coords, y=y_coords, cmap="magma", fill=True, bw_adjust=0.5)

    # Lock the graph size to match the exact pixel dimensions of your minimap
    plt.xlim(0, minimap_width)

    # We invert the Y-axis!
    # Why? Because in images, Y=0 is the TOP of the screen. In graphs, Y=0 is usually the BOTTOM.
    plt.ylim(minimap_height, 0)

    # Add titles and labels
    plt.title(title)
    plt.xlabel("Minimap X")
    plt.ylabel("Minimap Y")

    # Show the final beautiful graph!
    plt.show()