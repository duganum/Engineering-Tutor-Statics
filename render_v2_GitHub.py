import matplotlib.pyplot as plt
import numpy as np
import io
import os

def render_lecture_visual(topic, params=None):
    """Visualizes Statics concepts with a reduced size (3x3) for a cleaner UI."""
    # Reduced figsize from (6,6) to (3,3)
    fig, ax = plt.subplots(figsize=(3, 3), dpi=150)
    if params is None: params = {}
    
    ax.axhline(0, color='black', lw=1.5, zorder=2)
    ax.axvline(0, color='black', lw=1.5, zorder=2)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect('equal')
    
    limit = 100
    if topic == "Free Body Diagram":
        force = params.get('force', 50); theta = np.radians(params.get('theta', 45))
        ax.quiver(0, 0, force*np.cos(theta), force*np.sin(theta), color='blue', angles='xy', scale_units='xy', scale=1, label=r'$\vec{F}$')
        ax.plot(0, 0, 'ko', markersize=8); limit = 110 # Slightly smaller marker
    elif topic == "Truss":
        f_load = params.get('load', 50)
        ax.quiver(0, 0, 0, -f_load, color='red', angles='xy', scale_units='xy', scale=1, label='Load')
        ax.quiver(0, 0, -40, 40, color='green', angles='xy', scale_units='xy', scale=1)
        ax.quiver(0, 0, 40, 40, color='blue', angles='xy', scale_units='xy', scale=1)
        ax.plot(0, 0, 'ko', markersize=8)
    elif topic == "Geometric Properties":
        w, h = params.get('width', 40), params.get('height', 60)
        ax.add_patch(plt.Rectangle((-w/2, -h/2), w, h, fill=False, hatch='//', color='gray'))
        ax.plot(0, 0, 'rx', markersize=10, label='Centroid')
    elif topic == "Equilibrium":
        weight, dist = params.get('w', 50), params.get('d', 40)
        ax.plot([-dist, dist], [0, 0], 'brown', lw=6) # Thinner beam for smaller plot
        ax.plot(0, -5, 'k^', markersize=12)
        ax.quiver(-dist, 0, 0, -weight, color='red', angles='xy', scale_units='xy', scale=1)

    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit)
    plt.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format='png'); plt.close(fig); buf.seek(0)
    return buf

def render_problem_diagram(prob):
    """Procedural drawing reduced to (2.5x2.5) for optimal chat integration."""
    # Reduced figsize from (5,5) to (2.5,2.5)
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=120)
    ax.set_aspect('equal')
    p_id = prob.get('id', '')

    # --- S_1.1: FBD Problems ---
    if p_id == "S_1.1_1": # 50kg mass suspended
        ax.plot([-25, 0], [0, 0], 'k-', lw=2) # Cable A (Horizontal)
        ax.plot([0, 20], [0, 20], 'k-', lw=2) # Cable B (45 deg)
        ax.plot([0, 0], [0, -15], 'k-', lw=2) # Weight line
        ax.add_patch(plt.Rectangle((-5, -25), 10, 10, color='gray', zorder=3))
        ax.text(0, -20, "50kg", ha='center', va='center', color='white', fontweight='bold', fontsize=8)
        ax.text(-20, 5, "A", fontsize=8); ax.text(12, 15, "B (45°)", fontsize=8)
        ax.set_xlim(-30, 30); ax.set_ylim(-30, 30)
    
    elif p_id == "S_1.1_2": # Cylinder on Incline
        theta = np.radians(30)
        ax.plot([0, 50], [0, 50*np.tan(theta)], 'k-', lw=2)
        cx, cy = 25, 25*np.tan(theta) + 10
        ax.add_patch(plt.Circle((cx, cy), 10, color='blue', alpha=0.5))
        ax.text(cx, cy, "20kg", ha='center', fontsize=8)
        ax.set_xlim(0, 50); ax.set_ylim(0, 40)

    elif p_id == "S_1.1_3": # Beam with Pin and Cable
        ax.plot([0, 40], [0, 0], 'brown', lw=4)
        ax.plot(0, 0, 'k^', markersize=8)
        ax.plot([40, 40], [0, 20], 'k--', lw=1)
        ax.text(0, -5, "A", fontsize=8); ax.text(40, -5, "B", fontsize=8)
        ax.set_xlim(-10, 50); ax.set_ylim(-10, 30)

    # --- S_1.2: Truss Problems ---
    elif "S_1.2" in p_id:
        if p_id == "S_1.2_1": 
            nodes = np.array([[0,0], [20,0], [40,0], [30,15], [10,15], [0,0]])
            ax.plot(nodes[:,0], nodes[:,1], 'k-o', markersize=3)
            ax.quiver(20, 0, 0, -15, color='red', scale=1, scale_units='xy')
        elif p_id == "S_1.2_2":
            nodes = np.array([[0,0], [40,0], [20,34.6], [0,0]])
            ax.plot(nodes[:,0], nodes[:,1], 'k-o', markersize=3)
            ax.quiver(20, 34.6, 0, -15, color='red', scale=1, scale_units='xy')

    # --- S_1.3: Geometry ---
    elif "S_1.3" in p_id:
        if p_id == "S_1.3_1": 
            ax.add_patch(plt.Rectangle((0, 0), 40, 60, color='cyan', alpha=0.3))
            ax.plot(20, 30, 'rx', markersize=8)
        elif p_id == "S_1.3_3": 
            ax.add_patch(plt.Circle((0, 0), 20, fill=True, color='green', alpha=0.2))
            ax.text(0, 0, "d=0.5m", ha='center', fontsize=8)

    # --- S_1.4: Equilibrium ---
    elif "S_1.4" in p_id:
        if p_id == "S_1.4_1": 
            ax.plot([-20, 40], [0, 0], 'brown', lw=6)
            ax.plot(0, -2, 'k^', markersize=10)
            ax.quiver(-20, 0, 0, -20, color='red', scale=1, scale_units='xy')
            ax.quiver(40, 0, 0, -10, color='blue', scale=1, scale_units='xy')
        elif p_id == "S_1.4_2":
            ax.plot([0, 40], [0, 0], 'k-', lw=6)
            ax.axvline(0, color='gray', lw=10, alpha=0.5)
            ax.quiver(40, 0, 0, -20, color='red', scale=1, scale_units='xy')

    else:
        ax.text(0.5, 0.5, "Diagram", ha='center', transform=ax.transAxes, fontsize=8)

    ax.axis('off')
    plt.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format='png', transparent=True); plt.close(fig); buf.seek(0)
    return buf
