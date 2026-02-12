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
        # Cable A is horizontal (to the left), Cable B is at 45 degrees (to the right)
        ax.plot([-25, 0], [0, 0], 'k-', lw=2) # Cable A (Horizontal)
        ax.plot([0, 20], [0, 20], 'k-', lw=2) # Cable B (45 deg)
        ax.plot([0, 0], [0, -15], 'k-', lw=2) # Weight line
        ax.add_patch(plt.Rectangle((-5, -25), 10, 10, color='gray', zorder=3))
        ax.text(0, -20, "50 kg", ha='center', va='center', color='white', fontweight='bold')
        ax.text(-20, 5, "A", fontweight='bold')
        ax.text(12, 15, "B (45°)", fontweight='bold')
        ax.set_xlim(-30, 30); ax.set_ylim(-30, 30)
    
    elif p_id == "S_1.1_2": # Cylinder on Incline
        theta = np.radians(30)
        ax.plot([0, 50], [0, 50*np.tan(theta)], 'k-', lw=3) # Incline surface
        ax.plot([0, 50], [0, 0], 'k--', alpha=0.3) # Horizontal ref
        # Center of cylinder
        cx, cy = 25, 25*np.tan(theta) + 10
        ax.add_patch(plt.Circle((cx, cy), 10, color='blue', alpha=0.5, lw=2))
        ax.text(cx, cy, "20 kg", ha='center', fontweight='bold')
        ax.set_xlim(0, 50); ax.set_ylim(0, 40)

    elif p_id == "S_1.1_3": # Beam with Pin and Cable
        ax.plot([0, 40], [0, 0], 'brown', lw=6) # The Beam
        ax.plot(0, 0, 'k^', markersize=12) # Pin at A
        ax.plot([40, 40], [0, 20], 'k--', lw=2) # Cable at B
        ax.text(0, -5, "A", fontweight='bold'); ax.text(40, -5, "B", fontweight='bold')
        ax.text(20, 5, "10 kg", ha='center')

    # --- S_1.2: Truss Problems ---
    elif "S_1.2" in p_id:
        if p_id == "S_1.2_1": # Simple Bridge Truss
            nodes = np.array([[0,0], [20,0], [40,0], [30,15], [10,15], [0,0]])
            ax.plot(nodes[:,0], nodes[:,1], 'k-o')
            ax.quiver(20, 0, 0, -15, color='red', scale=1, scale_units='xy') # Mid load
            ax.text(20, -20, "10 kN", ha='center', color='red')
        elif p_id == "S_1.2_2": # Triangle Truss 60 deg
            nodes = np.array([[0,0], [40,0], [20,34.6], [0,0]])
            ax.plot(nodes[:,0], nodes[:,1], 'k-o', lw=2)
            ax.quiver(20, 34.6, 0, -15, color='red', scale=1, scale_units='xy')
            ax.text(20, 40, "5 kN", ha='center')
        elif p_id == "S_1.2_3": # Pratt Truss ZFM
            ax.plot([0, 20, 40, 60, 40, 20, 0], [0, 0, 0, 0, 20, 20, 0], 'k-o')
            ax.plot([20, 20], [0, 20], 'k-'); ax.plot([40, 40], [0, 20], 'k-')
            ax.plot([20, 40], [20, 0], 'k-') # Diagonals
            ax.quiver(0, 0, 0, -15, color='red', scale=1, scale_units='xy')

    # --- S_1.3: Geometry ---
    elif "S_1.3" in p_id:
        if p_id == "S_1.3_1": # Rectangle Centroid
            ax.add_patch(plt.Rectangle((0, 0), 40, 60, color='cyan', alpha=0.3))
            ax.plot(20, 30, 'rx', markersize=10)
            ax.text(20, 35, r"$\bar{y}$?", color='red')
        elif p_id == "S_1.3_2": # Square Moment of Inertia
            ax.add_patch(plt.Rectangle((-10,-10), 20, 20, fill=False, lw=2))
            ax.axhline(0, color='red', linestyle='--')
            ax.text(0, 12, "a = 0.2m", ha='center')
        elif p_id == "S_1.3_3": # Circle Area
            ax.add_patch(plt.Circle((0, 0), 20, fill=True, color='green', alpha=0.2))
            ax.plot([-20, 20], [0, 0], 'k<->')
            ax.text(0, 5, "d = 0.5m", ha='center')

    # --- S_1.4: Equilibrium ---
    elif "S_1.4" in p_id:
        if p_id == "S_1.4_1": # Seesaw Balance
            ax.plot([-20, 40], [0, 0], 'brown', lw=8)
            ax.plot(0, -2, 'k^', markersize=15)
            ax.quiver(-20, 0, 0, -20, color='red', scale=1, scale_units='xy')
            ax.quiver(40, 0, 0, -10, color='blue', scale=1, scale_units='xy')
            ax.text(-20, 5, "10 N"); ax.text(40, 5, "F?")
        elif p_id == "S_1.4_2": # Cantilever Moment
            ax.plot([0, 40], [0, 0], 'k-', lw=10)
            ax.axvline(0, color='gray', lw=20, alpha=0.5) # Wall
            ax.quiver(40, 0, 0, -25, color='red', scale=1, scale_units='xy')
            ax.text(40, 5, "100 N")
        elif p_id == "S_1.4_3": # Log Carry
            ax.plot([0, 60], [0, 0], 'orange', lw=12) # The Log
            ax.quiver(0, 0, 0, 20, color='blue', scale=1, scale_units='xy', label='A')
            ax.quiver(40, 0, 0, 40, color='blue', scale=1, scale_units='xy', label='B')
            ax.quiver(30, 0, 0, -30, color='black', scale=1, scale_units='xy') # CG

    else:
        ax.text(0.5, 0.5, f"Diagram for {p_id}", ha='center', transform=ax.transAxes)

    ax.axis('off')
    plt.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format='png'); plt.close(fig); buf.seek(0)
    return buf
