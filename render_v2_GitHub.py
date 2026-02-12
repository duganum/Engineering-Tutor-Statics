import matplotlib.pyplot as plt
import numpy as np
import io
import os

def render_lecture_visual(topic, params=None):
    """Visualizes Statics concepts with a strictly centered origin for the Lab view."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    if params is None: params = {}
    
    # Grid and Origin Settings
    ax.axhline(0, color='black', lw=1.5, zorder=2)
    ax.axvline(0, color='black', lw=1.5, zorder=2)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect('equal')
    
    limit = 100 # Default limit

    # 1. Free Body Diagram: Vector Components
    if topic == "Free Body Diagram":
        force = params.get('force', 50)
        theta = np.radians(params.get('theta', 45))
        fx, fy = force * np.cos(theta), force * np.sin(theta)
        
        ax.quiver(0, 0, fx, fy, color='blue', angles='xy', scale_units='xy', scale=1, label=r'$\vec{F}$')
        ax.plot([fx, fx], [0, fy], 'k--', alpha=0.4) 
        ax.plot(0, 0, 'ko', markersize=12) 
        limit = 110
        ax.set_title(r"FBD: Force Resolution $F_x, F_y$")

    # 2. Truss: Method of Joints
    elif topic == "Truss":
        f_load = params.get('load', 50) 
        ax.quiver(0, 0, 0, -f_load, color='red', angles='xy', scale_units='xy', scale=1, label='Load')
        ax.quiver(0, 0, -40, 40, color='green', angles='xy', scale_units='xy', scale=1, label='Member AC')
        ax.quiver(0, 0, 40, 40, color='blue', angles='xy', scale_units='xy', scale=1, label='Member AB')
        ax.plot(0, 0, 'ko', markersize=12) 
        limit = 100
        ax.set_title(r"Truss: Equilibrium at Joint A ($\sum F = 0$)")

    # 3. Geometric Properties: Centroids
    elif topic == "Geometric Properties":
        w = params.get('width', 40)
        h = params.get('height', 60)
        ax.add_patch(plt.Rectangle((-w/2, -h/2), w, h, fill=False, hatch='//', color='gray'))
        ax.plot(0, 0, 'rx', markersize=15, markeredgewidth=3, label='Centroid')
        limit = 100
        ax.set_title(r"Geometry: Centroid $(\bar{x}, \bar{y})$")

    # 4. Equilibrium: Moment and Lever
    elif topic == "Equilibrium":
        weight = params.get('w', 50)
        dist = params.get('d', 40)
        ax.plot([-dist, dist], [0, 0], 'brown', lw=10)
        ax.plot(0, -5, 'k^', markersize=20)
        ax.quiver(-dist, 0, 0, -weight, color='red', angles='xy', scale_units='xy', scale=1)
        ax.text(-dist, 5, "Weight", ha='center')
        limit = 100
        ax.set_title(r"Equilibrium: Moment Balance $\sum M = 0$")

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    if topic != "Geometric Properties": ax.legend(loc='upper right')
    
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def render_problem_diagram(prob):
    """Generates a dynamic vector diagram for specific Statics problems."""
    fig, ax = plt.subplots(figsize=(5, 5), dpi=120)
    ax.set_aspect('equal')
    ax.axis('off')

    p_id = prob.get('id', '')
    cat = prob.get('category', '').lower()

    # Generic Vector Problem Rendering
    if "vector" in cat or "fbd" in cat:
        ax.axhline(0, color='black', lw=1)
        ax.axvline(0, color='black', lw=1)
        # Draw a sample force based on problem targets or standard 45 deg
        ax.quiver(0, 0, 40, 40, color='blue', angles='xy', scale_units='xy', scale=1)
        ax.text(25, 25, r"$\vec{F}$", fontsize=12, color='blue')
        ax.set_xlim(-10, 60); ax.set_ylim(-10, 60)

    # Truss Problem Rendering
    elif "truss" in cat:
        pts = np.array([[0,0], [40,0], [20,30], [0,0]])
        ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2)
        ax.text(20, 35, "Joint C", ha='center')
        ax.quiver(20, 30, 0, -20, color='red', scale=1, scale_units='xy')
        ax.set_xlim(-10, 50); ax.set_ylim(-10, 50)

    # Default for unidentified problems
    else:
        ax.text(0.5, 0.5, "Refer to Problem Statement\nfor Geometry", ha='center', transform=ax.transAxes)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf
