import cv2

from util.minimap_data import get_minimap_roi, get_opponents


def test_find_opponents():
    img = cv2.imread("screenshots/minimap_visible_1.png")
    roi = get_minimap_roi(img)
    opponents = get_opponents(roi, debug=False)

    # while True:
    #     # waitKey(0) freezes the programme indefinitely until a key is pressed
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    #
    #     # Clean up the windows so they don't get stuck on your screen!
    # cv2.destroyAllWindows()

    assert len(opponents) == 11

def test_find_opponents2():
    img = cv2.imread("screenshots/minimap_visible_2.png")
    roi = get_minimap_roi(img)
    opponents = get_opponents(roi, debug=False)

    assert len(opponents) == 11

def test_find_opponents3():
    img = cv2.imread("screenshots/minimap_visible_3.png")
    roi = get_minimap_roi(img)
    opponents = get_opponents(roi, debug=False)

    assert len(opponents) == 10

def test_find_opponents4():
    img = cv2.imread("screenshots/minimap_visible_4.png")
    roi = get_minimap_roi(img)
    opponents = get_opponents(roi, debug=True)

    while True:
        # waitKey(0) freezes the programme indefinitely until a key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Clean up the windows so they don't get stuck on your screen!
    cv2.destroyAllWindows()

    assert len(opponents) == 10