import matplotlib.pyplot as plt
import numpy as np
import io
import os

def render_lecture_visual(topic, params=None):
    """Visualizes Statics concepts with High DPI (300) for crispness."""
    # Using 300 DPI for high-quality, non-blurry rendering
    fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=300)
    if params is None: params = {}
    
    ax.axhline(0, color='black', lw=1.5, zorder=2)
    ax.axvline(0, color='black', lw=1.5, zorder=2)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect('equal')
    
    limit = 100
    if topic == "Free Body Diagram":
        force = params.get('force', 50); theta = np.radians(params.get('theta', 45))
        ax.quiver(0, 0, force*np.cos(theta), force*np.sin(theta), color='blue', angles='xy', scale_units='xy', scale=1, label=r'$\vec{F}$')
        ax.plot(0, 0, 'ko', markersize=6); limit = 110
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

    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit)
    plt.tight_layout()
    buf = io.BytesIO()
    # Transparent background makes it look cleaner on the web
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

def render_problem_diagram(prob):
    """High-quality procedural drawing (300 DPI) for problem view."""
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=300)
    ax.set_aspect('equal')
    p_id = prob.get('id', '')

    if p_id == "S_1.1_1": # Mass suspended
        ax.plot([-25, 0], [0, 0], 'k-', lw=2)
        ax.plot([0, 20], [0, 20], 'k-', lw=2)
        ax.plot([0, 0], [0, -15], 'k-', lw=1.5)
        ax.add_patch(plt.Rectangle((-5, -25), 10, 10, color='gray', zorder=3))
        ax.text(0, -20, "50kg", ha='center', color='white', fontweight='bold', fontsize=7)
        ax.text(-18, 4, "A", fontsize=7); ax.text(12, 12, "B", fontsize=7)
        ax.set_xlim(-30, 30); ax.set_ylim(-30, 30)
    
    elif p_id == "S_1.1_2": # Cylinder Incline
        theta = np.radians(30)
        ax.plot([0, 50], [0, 50*np.tan(theta)], 'k-', lw=2.5)
        cx, cy = 25, 25*np.tan(theta) + 10
        ax.add_patch(plt.Circle((cx, cy), 10, color='blue', alpha=0.5))
        ax.text(cx, cy, "20kg", ha='center', fontsize=7)
        ax.set_xlim(0, 50); ax.set_ylim(0, 40)

    elif p_id == "S_1.4_1": # Seesaw
        ax.plot([-20, 40], [0, 0], 'brown', lw=5)
        ax.plot(0, -2, 'k^', markersize=8)
        ax.quiver(-20, 0, 0, -20, color='red', scale=1, scale_units='xy')
        ax.quiver(40, 0, 0, -10, color='blue', scale=1, scale_units='xy')
        ax.text(-20, 5, "10N", fontsize=7); ax.text(40, 5, "F?", fontsize=7)

    else:
        ax.text(0.5, 0.5, "Diagram", ha='center', transform=ax.transAxes, fontsize=8)

    ax.axis('off')
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
