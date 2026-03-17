import cv2
import numpy as np

def empty_callback(value):
    pass


def setup_colour_debugger(window_name, default_lower, default_upper):
    """
    Creates the window and the sliders ONCE before the video loop starts.
    default_lower and default_upper should be lists like [0, 0, 0] and [255, 255, 255]
    """
    cv2.namedWindow(window_name)

    # Create the Lower Bound sliders
    cv2.createTrackbar("Min B", window_name, default_lower[0], 255, empty_callback)
    cv2.createTrackbar("Min G", window_name, default_lower[1], 255, empty_callback)
    cv2.createTrackbar("Min R", window_name, default_lower[2], 255, empty_callback)

    # Create the Upper Bound sliders
    cv2.createTrackbar("Max B", window_name, default_upper[0], 255, empty_callback)
    cv2.createTrackbar("Max G", window_name, default_upper[1], 255, empty_callback)
    cv2.createTrackbar("Max R", window_name, default_upper[2], 255, empty_callback)


def setup_multiple_colour_debugger(window_name, default_lower, default_upper):
    """
    Creates the window and the sliders ONCE before the video loop starts.
    Forces a specific window size so the sliders never disappear!
    """
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    amount_of_colours = len(default_lower)

    # 2. Force the window size!
    # 500 pixels wide is good for the sliders.
    # We calculate the height dynamically: roughly 45 pixels per slider.
    window_height = (amount_of_colours * 6) * 45
    cv2.resizeWindow(window_name, 500, window_height)

    for i in range(amount_of_colours):
        # Create the Lower Bound sliders
        cv2.createTrackbar(f"Min B {i}", window_name, default_lower[i][0], 255, empty_callback)
        cv2.createTrackbar(f"Min G {i}", window_name, default_lower[i][1], 255, empty_callback)
        cv2.createTrackbar(f"Min R {i}", window_name, default_lower[i][2], 255, empty_callback)

        # Create the Upper Bound sliders
        cv2.createTrackbar(f"Max B {i}", window_name, default_upper[i][0], 255, empty_callback)
        cv2.createTrackbar(f"Max G {i}", window_name, default_upper[i][1], 255, empty_callback)
        cv2.createTrackbar(f"Max R {i}", window_name, default_upper[i][2], 255, empty_callback)


def apply_colour_debugger(window_name, roi, zoom_scale=2):
    """
    Reads the BGR sliders, applies the mask, and shows a padded comparison.
    Separates the sliders from the visuals to stop them disappearing!
    """
    # 1. Read the current position of all 6 sliders
    min_b = cv2.getTrackbarPos("Min B", window_name)
    min_g = cv2.getTrackbarPos("Min G", window_name)
    min_r = cv2.getTrackbarPos("Min R", window_name)

    max_b = cv2.getTrackbarPos("Max B", window_name)
    max_g = cv2.getTrackbarPos("Max G", window_name)
    max_r = cv2.getTrackbarPos("Max R", window_name)

    lower_bound = np.array([min_b, min_g, min_r])
    upper_bound = np.array([max_b, max_g, max_r])

    # 2. Apply the maths to create the mask and result
    mask = cv2.inRange(roi, lower_bound, upper_bound)
    result = cv2.bitwise_and(roi, roi, mask=mask)

    # Convert the 1-channel mask to 3-channel BGR
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # 3. --- THE PADDING MAGIC ---
    pad = 10
    p_roi = cv2.copyMakeBorder(roi, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    p_mask = cv2.copyMakeBorder(mask_bgr, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    p_res = cv2.copyMakeBorder(result, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    # 4. Dynamic Stacking
    is_wide_image = roi.shape[1] > roi.shape[0]

    if is_wide_image:
        # Wide slices stack top-to-bottom
        display_panel = np.vstack((p_roi, p_mask, p_res))
    else:
        # Tall slices stack side-by-side
        display_panel = np.hstack((p_roi, p_mask, p_res))

    cv2.putText(display_panel, "Or|Ma|Res", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 255, 255), 1)

    # Add one final outer border around the entire panel
    final_padded_panel = cv2.copyMakeBorder(display_panel, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    # 5. Zoom and Display in the separate visuals window
    height, width = final_padded_panel.shape[:2]
    zoomed_panel = cv2.resize(final_padded_panel, (width * zoom_scale, height * zoom_scale))

    viewer_window_name = f"{window_name} - Visuals"
    cv2.imshow(viewer_window_name, zoomed_panel)

    return lower_bound, upper_bound

def apply_multi_colour_debugger(window_name, roi, amount, zoom_scale=2):
    """
    Reads multiple sets of sliders and builds a UI.
    Separates the sliders from the image to prevent them from disappearing!
    """
    lower_bounds = []
    upper_bounds = []


    # 1. Gather all the slider values
    for i in range(amount):
        min_b = cv2.getTrackbarPos(f"Min B {i}", window_name)
        min_g = cv2.getTrackbarPos(f"Min G {i}", window_name)
        min_r = cv2.getTrackbarPos(f"Min R {i}", window_name)

        max_b = cv2.getTrackbarPos(f"Max B {i}", window_name)
        max_g = cv2.getTrackbarPos(f"Max G {i}", window_name)
        max_r = cv2.getTrackbarPos(f"Max R {i}", window_name)

        lower_bounds.append(np.array([min_b, min_g, min_r]))
        upper_bounds.append(np.array([max_b, max_g, max_r]))

    display_panels = []
    master_mask = np.zeros(roi.shape[:2], dtype=np.uint8)

    # Check if the ROI is wider than it is tall
    is_wide_image = roi.shape[1] > roi.shape[0]

    pad = 10

    # 2. Process each individual colour range
    for i in range(amount):
        lower = lower_bounds[i]
        upper = upper_bounds[i]

        current_mask = cv2.inRange(roi, lower, upper)
        master_mask = cv2.bitwise_or(master_mask, current_mask)

        current_result = cv2.bitwise_and(roi, roi, mask=current_mask)
        mask_bgr = cv2.cvtColor(current_mask, cv2.COLOR_GRAY2BGR)

        p_roi = cv2.copyMakeBorder(roi, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        p_mask = cv2.copyMakeBorder(mask_bgr, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        p_res = cv2.copyMakeBorder(current_result, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])

        # Build the internal group layout
        if is_wide_image:
            # If wide, stack the three images on top of each other
            panel = np.vstack((p_roi, p_mask, p_res))
        else:
            # If tall, stack the three images side-by-side
            panel = np.hstack((p_roi, p_mask, p_res))

        # Add a black background box so the text is always readable!
        cv2.putText(panel, f"Colour {i}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 255, 0), 1)
        display_panels.append(panel)

    # 3. --- THE MASTER SECTION ---
    master_result = cv2.bitwise_and(roi, roi, mask=master_mask)
    master_mask_bgr = cv2.cvtColor(master_mask, cv2.COLOR_GRAY2BGR)

    p_master_roi = cv2.copyMakeBorder(roi, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    p_master_mask = cv2.copyMakeBorder(master_mask_bgr, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    p_master_res = cv2.copyMakeBorder(master_result, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    if is_wide_image:
        master_panel = np.vstack((p_master_roi, p_master_mask, p_master_res))
    else:
        master_panel = np.hstack((p_master_roi, p_master_mask, p_master_res))

    cv2.putText(master_panel, "MASTER COMBINED", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 255), 1)
    display_panels.append(master_panel)

    # 4. --- THE FINAL ASSEMBLY ---
    # We now ALWAYS stack the different colour groups vertically
    display_panel = np.vstack(display_panels)

    final_padded_panel = cv2.copyMakeBorder(display_panel, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    # 5. Zoom and Display
    height, width = final_padded_panel.shape[:2]
    zoomed_panel = cv2.resize(final_padded_panel, (width * zoom_scale, height * zoom_scale))

    # THE FIX: Show the visuals in a SEPARATE window so the sliders stay safe!
    viewer_window_name = f"{window_name} - Visuals"
    cv2.imshow(viewer_window_name, zoomed_panel)

    return lower_bounds, upper_bounds, master_mask