from pathlib import Path
import json
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "data" / "construction.jpeg"
OUT = ROOT / "outputs" / "digitized_points.json"

# Construction drawing real dimensions
TERRACE_W = 5.3   # left → right in drawing
TERRACE_H = 4.3   # top → bottom in drawing

img = mpimg.imread(IMAGE)

fig, ax = plt.subplots(figsize=(10, 12))
ax.imshow(img)
ax.set_title(
    "Click terrace corners in this order: TOP-LEFT, TOP-RIGHT, BOTTOM-RIGHT, BOTTOM-LEFT"
)
plt.axis("on")

clicked = plt.ginput(4, timeout=0)
plt.close()

labels = ["top_left", "top_right", "bottom_right", "bottom_left"]
pixel_corners = dict(zip(labels, clicked))

print("Pixel terrace corners:")
for k, v in pixel_corners.items():
    print(k, v)

# Simple bilinear approximation for rectangle-ish plan image
# For now use affine mapping from top-left/top-right/bottom-left.
tl = pixel_corners["top_left"]
tr = pixel_corners["top_right"]
bl = pixel_corners["bottom_left"]

def pixel_to_original(px, py):
    # Solve p = tl + a*(tr-tl) + b*(bl-tl)
    vx = (tr[0] - tl[0], tr[1] - tl[1])
    vy = (bl[0] - tl[0], bl[1] - tl[1])
    dx = px - tl[0]
    dy = py - tl[1]

    det = vx[0] * vy[1] - vx[1] * vy[0]
    a = (dx * vy[1] - dy * vy[0]) / det
    b = (vx[0] * dy - vx[1] * dx) / det

    return {
        "x_original": a * TERRACE_W,
        "y_original": b * TERRACE_H,
    }

def original_to_north_up(x, y):
    # Original drawing:
    # x = left → right
    # y = top → bottom
    #
    # Original top-right corner points north.
    s = math.sqrt(2)
    return {
        "x": (x + y) / s,
        "y": (x - y + TERRACE_H) / s,
    }

features = {}

feature_sets = [
    ("poles", 4, "Click the 4 pole centers"),
    ("roof_corners", 4, "Click roof outer corners"),
    ("wall_points", 2, "Click NE wall obstruction start and end"),
    ("door_center", 1, "Click door center"),
]

for name, count, title in feature_sets:
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.imshow(img)
    ax.set_title(title)
    plt.axis("on")
    pts = plt.ginput(count, timeout=0)
    plt.close()

    converted = []
    for px, py in pts:
        orig = pixel_to_original(px, py)
        north = original_to_north_up(orig["x_original"], orig["y_original"])
        converted.append({
            "pixel": {"x": px, "y": py},
            "original_drawing": orig,
            "north_up": north,
        })

    features[name] = converted

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({
    "pixel_corners": pixel_corners,
    "features": features,
}, indent=2), encoding="utf-8")

print(f"Saved {OUT}")