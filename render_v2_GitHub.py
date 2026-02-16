import matplotlib.pyplot as plt
import numpy as np
import io
import os

def render_lecture_visual(topic, params=None):
    """Visualizes Statics concepts with High DPI (300) for crispness."""
    # Reduced figsize for cleaner UI, high DPI for sharpness
    fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=300)
    if params is None: params = {}
    
    # Standard Grid and Axis
    ax.axhline(0, color='black', lw=1.5, zorder=2)
    ax.axvline(0, color='black', lw=1.5, zorder=2)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect('equal')
    
    limit = 100
    
    if topic == "Free Body Diagram":
        force = params.get('force', 50)
        theta = np.radians(params.get('theta', 45))
        ax.quiver(0, 0, force*np.cos(theta), force*np.sin(theta), color='blue', 
                  angles='xy', scale_units='xy', scale=1, label=r'$\vec{F}$')
        ax.plot(0, 0, 'ko', markersize=6)
        limit = 110
    
    elif topic == "Truss":
        f_load = params.get('load', 50)
        ax.quiver(0, 0, 0, -f_load, color='red', angles='xy', scale_units='xy', scale=1)
        ax.quiver(0, 0, -40, 40, color='green', angles='xy', scale_units='xy', scale=1)
        ax.quiver(0, 0, 40, 40, color='blue', angles='xy', scale_units='xy', scale=1)
        ax.plot(0, 0, 'ko', markersize=6)
    
    elif topic == "Geometric Properties":
        w, h = params.get('width', 40), params.get('height', 60)
        ax.add_patch(plt.Rectangle((-w/2, -h/2), w, h, fill=False, hatch='//', color='gray', lw=1.5))
        ax.plot(0, 0, 'rx', markersize=10, markeredgewidth=2)
    
    elif topic == "Equilibrium":
        weight, dist = params.get('w', 50), params.get('d', 40)
        ax.plot([-dist, dist], [0, 0], 'brown', lw=6)
        ax.plot(0, -5, 'k^', markersize=10)
        ax.quiver(-dist, 0, 0, -weight, color='red', angles='xy', scale_units='xy', scale=1)

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

def render_problem_diagram(prob):
    """High-quality procedural drawing for Statics problems. 
       Reduced size by 30% (from 2.5 to 1.75)."""
    fig, ax = plt.subplots(figsize=(1.75, 1.75), dpi=300)
    ax.set_aspect('equal')
    p_id = prob.get('id', '')

    # --- S_1.1: FBD Problems ---
    if p_id == "S_1.1_1": 
        ax.plot([-25, 0], [0, 0], 'k-', lw=2) 
        ax.plot([0, 20], [0, 20], 'k-', lw=2) 
        ax.plot([0, 0], [0, -15], 'k-', lw=1.5) 
        ax.add_patch(plt.Rectangle((-5, -25), 10, 10, color='gray', zorder=3))
        ax.text(0, -20, "50kg", ha='center', va='center', color='white', fontweight='bold', fontsize=7)
        ax.text(-22, 3, "A", fontsize=7); ax.text(12, 12, "B (45°)", fontsize=7)
        ax.set_xlim(-30, 30); ax.set_ylim(-30, 30)
    
    elif p_id == "S_1.1_2": 
        theta = np.radians(30)
        ax.plot([0, 50], [0, 50*np.tan(theta)], 'k-', lw=2.5)
        ax.plot([0, 50], [0, 0], 'k--', alpha=0.3)
        cx, cy = 25, 25*np.tan(theta) + 10
        ax.add_patch(plt.Circle((cx, cy), 10, color='blue', alpha=0.5))
        ax.text(cx, cy, "20kg", ha='center', fontsize=7)
        ax.set_xlim(0, 50); ax.set_ylim(0, 40)

    elif p_id == "S_1.1_3": 
        ax.plot([0, 40], [0, 0], 'brown', lw=5)
        ax.plot(0, 0, 'k^', markersize=10)
        ax.plot([40, 40], [0, 25], 'k--', lw=1.5)
        ax.text(0, -6, "A", fontweight='bold', fontsize=7); ax.text(40, -6, "B", fontweight='bold', fontsize=7)
        ax.set_xlim(-10, 50); ax.set_ylim(-10, 30)

    # --- S_1.2: Truss Problems ---
    elif "S_1.2" in p_id:
        if p_id == "S_1.2_1": 
            nodes = np.array([[0,0], [20,0], [40,0], [30,15], [10,15], [0,0]])
            ax.plot(nodes[:,0], nodes[:,1], 'k-o', markersize=3)
            ax.quiver(20, 0, 0, -15, color='red', scale=1, scale_units='xy')
            ax.text(20, -10, "10kN", ha='center', fontsize=7, color='red')
        elif p_id == "S_1.2_2":
            nodes = np.array([[0,0], [40,0], [20,34.6], [0,0]])
            ax.plot(nodes[:,0], nodes[:,1], 'k-o', markersize=3)
            ax.quiver(20, 34.6, 0, -15, color='red', scale=1, scale_units='xy')
        elif p_id == "S_1.2_3":
            ax.plot([0, 20, 40, 60, 40, 20, 0], [0, 0, 0, 0, 20, 20, 0], 'k-o', markersize=3)
            ax.plot([20, 20], [0, 20], 'k-'); ax.plot([40, 40], [0, 20], 'k-')
            ax.text(30, -5, "Pratt Truss", ha='center', fontsize=7)

    # --- S_1.3: Geometry ---
    elif "S_1.3" in p_id:
        if p_id == "S_1.3_1": 
            ax.add_patch(plt.Rectangle((0, 0), 40, 60, color='cyan', alpha=0.3))
            ax.plot(20, 30, 'rx', markersize=10)
            ax.text(22, 30, r"$\bar{y}$", color='red', fontsize=9)
        elif p_id == "S_1.3_2":
            # Added missing Vector Diagram for a=0.2m square
            ax.add_patch(plt.Rectangle((0, 0), 20, 20, color='orange', alpha=0.3))
            ax.quiver(0, 0, 25, 0, color='black', scale=1, scale_units='xy', width=0.02)
            ax.quiver(0, 0, 0, 25, color='black', scale=1, scale_units='xy', width=0.02)
            ax.text(25, -2, "x", fontsize=7); ax.text(-2, 25, "y", fontsize=7)
            ax.text(10, 22, "a=0.2m", ha='center', fontsize=7)
            ax.set_xlim(-5, 30); ax.set_ylim(-5, 30)
        elif p_id == "S_1.3_3": 
            # Revised for L-shaped section (4x4, thickness 1)
            # Vertical segment (0,0) to (1,4)
            ax.add_patch(plt.Rectangle((0, 1), 1, 3, color='green', alpha=0.3))
            # Horizontal segment (0,0) to (4,1)
            ax.add_patch(plt.Rectangle((0, 0), 4, 1, color='green', alpha=0.3))
            # Dimension Lines
            ax.plot([-0.5, -0.5], [0, 4], 'k-', lw=0.8); ax.text(-1, 2, "4m", va='center', rotation=90, fontsize=6)
            ax.plot([0, 4], [-0.5, -0.5], 'k-', lw=0.8); ax.text(2, -1.2, "4m", ha='center', fontsize=6)
            ax.set_xlim(-1.5, 5); ax.set_ylim(-1.5, 5)

    # --- S_1.4: Equilibrium ---
    elif "S_1.4" in p_id:
        if p_id == "S_1.4_1": 
            ax.plot([-20, 40], [0, 0], 'brown', lw=6)
            ax.plot(0, -2, 'k^', markersize=10)
            ax.quiver(-20, 0, 0, -20, color='red', scale=1, scale_units='xy')
            ax.quiver(40, 0, 0, -10, color='blue', scale=1, scale_units='xy')
            ax.text(-20, 5, "10N", fontsize=7); ax.text(40, 5, "F?", fontsize=7)
        elif p_id == "S_1.4_2": 
            ax.plot([0, 40], [0, 0], 'k-', lw=8)
            ax.axvline(0, color='gray', lw=15, alpha=0.5)
            ax.quiver(40, 0, 0, -20, color='red', scale=1, scale_units='xy')
            ax.text(30, 5, "100N", fontsize=7)
        elif p_id == "S_1.4_3": 
            ax.plot([0, 60], [0, 0], 'orange', lw=10)
            ax.quiver(0, 0, 0, 15, color='blue', scale=1, scale_units='xy')
            ax.quiver(40, 0, 0, 30, color='blue', scale=1, scale_units='xy')
            ax.text(40, 15, "B", fontsize=7)

    else:
        ax.text(0.5, 0.5, "Diagram", ha='center', transform=ax.transAxes, fontsize=8)

    ax.axis('off')
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
