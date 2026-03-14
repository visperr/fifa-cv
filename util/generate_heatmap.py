import math

import cv2
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
import numpy as np

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


def generate_better_heatmap(coords_list, title):
    """
    Overlays a professional, smooth density heatmap onto a custom football field template.
    """
    if not coords_list:
        print(f"No data to plot for {title}!")
        return

    # 1. LOAD AND SIZE THE BACKGROUND FIELD IMAGE
    # ---------------------------------------------------------
    # Use cv2.imread for consistent image loading with the rest of your pipeline
    field_img = cv2.imread("minimap_clean.png")
    if field_img is None:
        print(f"Error: Could not load field image")
        return

    # Matplotlib expects RGB, so convert if cv2 loaded as BGR
    if field_img.ndim == 3:  # If color image
        field_img = cv2.cvtColor(field_img, cv2.COLOR_BGR2RGB)

    # Get the exact dimensions of the template to set the coordinate system
    img_height, img_width = field_img.shape[:2]

    # 2. SEPARATE AND COORDINATE DATA
    # ---------------------------------------------------------
    x_coords = [point[0] for point in coords_list]
    y_coords = [point[1] for point in coords_list]

    # 3. CONFIGURE THE MATPLOTLIB CANVAS
    # ---------------------------------------------------------
    # figsize ensures a good balance between data detail and final image quality
    plt.figure(figsize=(15, 9))

    # Create an axis that spans the entire figure
    ax = plt.gca()

    # 4. DRAW THE BACKGROUND LAYER
    # ---------------------------------------------------------
    # The crucial 'extent' parameter maps the physical image size (pixels)
    # into Matplotlib's mathematical coordinate space [xmin, xmax, ymin, ymax]
    ax.imshow(field_img, extent=[0, img_width, img_height, 0], aspect='auto')

    # 5. DRAW THE DATA LAYER (THE HEATMAP)
    # ---------------------------------------------------------
    # Use plt.hexbin() for a blazing fast and beautiful hexagonal binning.
    # It’s great for creating smooth, high-density areas that look like "glow."
    # gridsize=50 dictates how detailed the heatmap is.
    # 'cmap' sets the color scheme ('YlOrRd' is classic 'yellow-orange-red' glow).
    # 'alpha=0.6' makes the heatmap 60% transparent so you can see the pitch lines.
    # 'edgecolors='none'' hides the hex borders for a seamless, glowing effect.
    # hb = ax.hexbin(x_coords, y_coords, gridsize=50, cmap='YlOrRd',
    #                bins='log', alpha=0.6, edgecolors='none')

    # 4. CREATE A CUSTOM FADING COLOUR MAP
    # ---------------------------------------------------------
    # Get the standard 'magma' colours (256 steps of colour)
    base_cmap = plt.get_cmap('magma')
    color_array = base_cmap(np.arange(256))

    # Modify the 'Alpha' channel (transparency).
    # This makes the lowest values 0% visible, smoothly fading up to 100% visible.
    color_array[:, -1] = np.linspace(0.0, 1.0, 256)

    # Save our new custom colour map
    transparent_magma = mcolors.ListedColormap(color_array)

    # 5. DRAW THE DATA LAYER (THE SMOOTH HEATMAP)
    # ---------------------------------------------------------
    # 'levels=100' tells the maths to draw 100 smooth contour layers (higher = smoother)
    # 'thresh=0.05' tells it to keep the lowest 5% of the data completely transparent,
    # so the heatmap doesn't accidentally paint your entire pitch in a faint colour!

    sns.kdeplot(
        x=x_coords,
        y=y_coords,
        ax=ax,  # Forces Seaborn to draw exactly on top of your pitch image!
        fill=True,  # Fills the contours with solid colour
        cmap=transparent_magma,  # 'magma' or 'inferno' are fantastic for smooth, dark-to-bright glows
        levels=100,
        bw_adjust=0.5
    )

    # 6. FINAL GRAPH CONFIGURATION
    # ---------------------------------------------------------
    plt.title(title, fontsize=16)

    # Lock the visual coordinate limits to match your minimap crop
    plt.xlim(0, img_width)

    # Standard image (0,0) is TOP, so we must invert y-axis to match visual 'up'
    plt.ylim(img_height, 0)

    # Clean up the output so it looks like a proper image graphic
    plt.grid(False)  # Turn off the graph paper lines
    plt.tight_layout()  # Compress margins
    plt.axis('off')
    plt.show()
    # Show the gorgeous, complete graphic!
    plt.show()


def generate_heatmap_dashboard(data_dict):
    """
    Takes a dictionary of coordinate lists and plots them in a professional grid.
    Example input: {"Ball Heatmap": ball_coords, "Opponent Heatmap": opp_coords}
    """
    # 1. LOAD THE BACKGROUND FIELD
    # ---------------------------------------------------------
    field_img = cv2.imread("minimap_clean.png")
    if field_img is None:
        print(f"Error: Could not load field image")
        return

    if field_img.ndim == 3:
        field_img = cv2.cvtColor(field_img, cv2.COLOR_BGR2RGB)

    img_height, img_width = field_img.shape[:2]

    # 2. CALCULATE THE GRID LAYOUT
    # ---------------------------------------------------------
    num_plots = len(data_dict)
    cols = 2  # We will use a standard 2-column layout
    rows = math.ceil(num_plots / cols)  # Automatically calculate needed rows

    # Create the massive dashboard canvas!
    # figsize scales dynamically based on how many rows we need.
    fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(16, 6 * rows))

    # Flatten the 2D grid of axes into a simple 1D list so it is easy to loop through
    if num_plots > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    # 3. CREATE THE FADING COLOUR MAP ONCE
    # ---------------------------------------------------------
    base_cmap = plt.get_cmap('magma')
    color_array = base_cmap(np.arange(256))
    color_array[:, -1] = np.linspace(0.0, 1.0, 256)  # Alpha fade trick!
    transparent_magma = mcolors.ListedColormap(color_array)

    # 4. LOOP THROUGH THE DATA AND DRAW THE GRID
    # ---------------------------------------------------------
    for i, (title, coords) in enumerate(data_dict.items()):
        ax = axes[i]  # Select the specific grid square

        # Draw the pitch template on this specific square
        ax.imshow(field_img, extent=[0, img_width, img_height, 0], aspect='auto')

        if coords:  # Failsafe: Only do the heavy maths if we actually have data points!
            x_coords = [point[0] for point in coords]
            y_coords = [point[1] for point in coords]

            # Draw the smooth, fading heatmap
            sns.kdeplot(
                x=x_coords,
                y=y_coords,
                ax=ax,
                fill=True,
                cmap=transparent_magma,
                levels=100,
                bw_adjust=0.25
            )

        # Tidy up the specific grid square
        ax.set_title(title, fontsize=16, fontweight='bold', color='#333333')
        ax.set_xlim(0, img_width)
        ax.set_ylim(img_height, 0)
        ax.axis('off')  # Remove the ugly border and numbers

    # 5. CLEAN UP EMPTY SQUARES
    # ---------------------------------------------------------
    # If we have an odd number of plots (e.g., 3 plots in a 2x2 grid),
    # we need to make the 4th square completely invisible.
    for j in range(num_plots, len(axes)):
        axes[j].axis('off')

    # Remove extra whitespace between the grid squares
    plt.tight_layout()

    # Show the magnificent dashboard!
    plt.show()