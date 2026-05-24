from pathlib import Path
import yaml
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "terrace.yaml"
OUT = ROOT / "outputs" / "geometry.png"

with DATA.open("r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

terrace_pts = [(p["x"], p["y"]) for p in cfg["terrace"]["outline"]]
roof_pts = [(p["x"], p["y"]) for p in cfg["roof"]["approximate_outer_roof_polygon"]]

fig, ax = plt.subplots(figsize=(8, 8))

ax.add_patch(Polygon(terrace_pts, closed=True, fill=False, linewidth=2, label="Terrace outline"))
ax.add_patch(Polygon(roof_pts, closed=True, alpha=0.08, label="High roof / slat zone"))
ax.plot(*zip(*(roof_pts + [roof_pts[0]])), linewidth=2)

for pole in cfg["poles"]["items"]:
    ax.add_patch(Circle((pole["x"], pole["y"]), cfg["poles"]["radius_m"], fill=False, linewidth=2))
    ax.text(pole["x"] + 0.08, pole["y"] + 0.08, pole["id"], fontsize=9)

door = cfg["door"]["center"]
ax.scatter([door["x"]], [door["y"]], marker="s")
ax.text(door["x"] + 0.1, door["y"], "door", fontsize=9)

wall = cfg["building_wall_obstructions"][0]["approximate_edge"]
ax.plot(
    [wall["start"]["x"], wall["end"]["x"]],
    [wall["start"]["y"], wall["end"]["y"]],
    linewidth=4,
    label="NE wall obstruction",
)

ax.set_aspect("equal", adjustable="box")
ax.set_xlabel("East / x [m]")
ax.set_ylabel("North / y [m]")
ax.set_title("Terrace geometry — north up")
ax.grid(True, linewidth=0.5)
ax.legend()
OUT.parent.mkdir(exist_ok=True)
plt.savefig(OUT, dpi=200, bbox_inches="tight")
plt.show()

print(f"Saved {OUT}")