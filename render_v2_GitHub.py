import matplotlib.pyplot as plt
import numpy as np
import io
import os

def render_lecture_visual(topic, params=None):
    """Visualizes Statics concepts with a strictly centered origin for the Lab view."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    if params is None: params = {}
    
    ax.axhline(0, color='black', lw=1.5, zorder=2)
    ax.axvline(0, color='black', lw=1.5, zorder=2)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect('equal')
    
    limit = 100
    if topic == "Free Body Diagram":
        force = params.get('force', 50); theta = np.radians(params.get('theta', 45))
        ax.quiver(0, 0, force*np.cos(theta), force*np.sin(theta), color='blue', angles='xy', scale_units='xy', scale=1, label=r'$\vec{F}$')
        ax.plot(0, 0, 'ko', markersize=12); limit = 110
    elif topic == "Truss":
        f_load = params.get('load', 50)
        ax.quiver(0, 0, 0, -f_load, color='red', angles='xy', scale_units='xy', scale=1, label='Load')
        ax.quiver(0, 0, -40, 40, color='green', angles='xy', scale_units='xy', scale=1)
        ax.quiver(0, 0, 40, 40, color='blue', angles='xy', scale_units='xy', scale=1)
        ax.plot(0, 0, 'ko', markersize=12)
    elif topic == "Geometric Properties":
        w, h = params.get('width', 40), params.get('height', 60)
        ax.add_patch(plt.Rectangle((-w/2, -h/2), w, h, fill=False, hatch='//', color='gray'))
        ax.plot(0, 0, 'rx', markersize=15, label='Centroid')
    elif topic == "Equilibrium":
        weight, dist = params.get('w', 50), params.get('d', 40)
        ax.plot([-dist, dist], [0, 0], 'brown', lw=10)
        ax.plot(0, -5, 'k^', markersize=20)
        ax.quiver(-dist, 0, 0, -weight, color='red', angles='xy', scale_units='xy', scale=1)

    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit)
    plt.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format='png'); plt.close(fig); buf.seek(0)
    return buf

def render_problem_diagram(prob):
    """Procedural drawing for the 12 Statics problems in the bank."""
    fig, ax = plt.subplots(figsize=(5, 5), dpi=120)
    ax.set_aspect('equal')
    p_id = prob.get('id', '')

    # --- S_1.1: FBD Problems ---
    if p_id == "S_1.1_1": # 50kg mass suspended
        ax.plot([-20, 0, 20], [20, 0, 20], 'k-', lw=2) # Cables
        ax.plot([0, 0], [0, -15], 'k-', lw=2) # Weight line
        ax.add_patch(plt.Rectangle((-5, -25), 10, 10, color='gray'))
        ax.text(0, -20, "50 kg", ha='center', color='white', fontweight='bold')
        ax.text(-15, 10, "A", fontweight='bold'); ax.text(15, 10, "B (45°)")
    
    elif p_id == "S_1.1_2": # Cylinder on Incline
        theta = np.radians(30)
        ax.plot([0, 40], [0, 40*np.tan(theta)], 'k-', lw=3) # Incline
        ax.add_patch(plt.Circle((20, 20*np.tan(theta)+8), 8, color='blue', alpha=0.6))
        ax.text(15, 20, "20 kg", fontweight='bold')

    # --- S_1.2: Truss Problems ---
    elif "S_1.2" in p_id:
        nodes = np.array([[0,0], [40,0], [20,30], [0,0]])
        ax.plot(nodes[:,0], nodes[:,1], 'k-o', lw=2)
        if p_id == "S_1.2_1": ax.quiver(20, 30, 0, -20, color='red', scale=1, scale_units='xy', label='10 kN')
        elif p_id == "S_1.2_2": ax.quiver(20, 30, 0, -20, color='red', scale=1, scale_units='xy', label='5 kN')

    # --- S_1.3: Geometry ---
    elif p_id == "S_1.3_1": # Rectangle Centroid
        ax.add_patch(plt.Rectangle((0, 0), 40, 60, fill=True, color='cyan', alpha=0.3))
        ax.axhline(0, color='black', lw=2)
        ax.annotate('', xy=(20, 30), xytext=(20, 0), arrowprops=dict(arrowstyle='<->'))
        ax.text(22, 15, r"$\bar{y}$")

    elif p_id == "S_1.3_3": # Circle Area
        ax.add_patch(plt.Circle((0, 0), 25, fill=False, color='blue', lw=2))
        ax.plot([-25, 25], [0, 0], 'k--')
        ax.text(0, 5, "d = 0.5m", ha='center')

    # --- S_1.4: Equilibrium ---
    elif p_id == "S_1.4_1": # Seesaw Balance
        ax.plot([-20, 40], [0, 0], 'brown', lw=8) # Beam
        ax.plot(0, -5, 'k^', markersize=20) # Pivot
        ax.quiver(-20, 0, 0, -10, color='red', scale=1, scale_units='xy')
        ax.quiver(40, 0, 0, -5, color='blue', scale=1, scale_units='xy')
        ax.text(-20, 5, "10N"); ax.text(40, 5, "F?")

    # Fallback/General
    else:
        ax.text(0.5, 0.5, f"Diagram for {p_id}\n(Procedural Render)", ha='center', transform=ax.transAxes)

    ax.axis('off')
    plt.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format='png'); plt.close(fig); buf.seek(0)
    return buf
