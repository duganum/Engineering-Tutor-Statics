import matplotlib.pyplot as plt
import numpy as np
import os
import io

def render_problem_diagram(prob_id):
    """Generates precise FBDs and geometric diagrams for Statics problems."""
    pid = str(prob_id).strip()
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set_aspect('equal')
    found = False

    # --- S_1.1: Equilibrium & FBD ---
    if pid.startswith("S_1.1"):
        if pid == "S_1.1_1": # 50kg mass cables
            ax.plot(0, 0, 'ko', markersize=8)
            ax.annotate('', xy=(-1.5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='blue'))
            ax.annotate('', xy=(1.2, 1.2), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='green'))
            ax.annotate('', xy=(0, -1.5), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red'))
            ax.text(-1.4, 0.2, '$T_A$', color='blue'); ax.text(1.0, 1.3, '$T_B (45^\circ)$', color='green')
            ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.1_2": # Cylinder on Incline
            theta = np.radians(30)
            ax.plot([-2, 2], [2*np.tan(-theta), -2*np.tan(-theta)], 'k-', lw=2) 
            ax.add_patch(plt.Circle((0, 0.5), 0.5, color='gray', alpha=0.5)) 
            ax.annotate('', xy=(0.5*np.sin(theta), 0.5+0.5*np.cos(theta)), xytext=(0, 0.5), 
                        arrowprops=dict(arrowstyle='->', color='red')) 
            ax.set_xlim(-2, 2); ax.set_ylim(-1, 2)
            found = True
        elif pid == "S_1.1_3": # Beam with Pin and Cable
            ax.plot([0, 3], [0, 0], 'brown', lw=6) 
            ax.plot(0, 0, 'k^', markersize=10) 
            ax.annotate('', xy=(3, 2), xytext=(3, 0), arrowprops=dict(arrowstyle='-', ls='--')) 
            ax.set_xlim(-0.5, 4); ax.set_ylim(-1, 3)
            found = True

    # --- S_1.2: Truss Analysis ---
    elif pid.startswith("S_1.2"):
        if pid == "S_1.2_1": # Simple Bridge Truss
            pts = np.array([[0,0], [2,2], [4,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o')
            ax.set_xlim(-0.5, 4.5); ax.set_ylim(-1, 3)
            found = True
        elif pid == "S_1.2_2": # Triangle Truss
            pts = np.array([[0,0], [1, 1.73], [2,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o')
            ax.set_xlim(-0.5, 2.5); ax.set_ylim(-0.5, 2.5)
            found = True
        elif pid == "S_1.2_3": # Simple Pratt
            ax.plot([0,1,2,3], [0,1,1,0], 'k-o'); ax.plot([0,3], [0,0], 'k-o')
            ax.set_xlim(-0.5, 3.5); ax.set_ylim(-0.5, 2)
            found = True

    # --- S_1.3: Geometric Properties ---
    elif pid.startswith("S_1.3"):
        if pid == "S_1.3_1":
            ax.add_patch(plt.Rectangle((0,0), 4, 6, fill=False, hatch='/'))
            ax.plot(2, 3, 'rx', markersize=10) 
            ax.set_xlim(-1, 5); ax.set_ylim(-1, 7)
            found = True
        elif pid == "S_1.3_2":
            ax.add_patch(plt.Rectangle((-0.1, -0.1), 0.2, 0.2, color='orange', alpha=0.3))
            ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1)
            ax.set_xlim(-0.2, 0.2); ax.set_ylim(-0.2, 0.2)
            found = True
        elif pid == "S_1.3_3":
            ax.add_patch(plt.Circle((0,0), 0.25, color='blue', alpha=0.2))
            ax.set_xlim(-0.5, 0.5); ax.set_ylim(-0.5, 0.5)
            found = True

    # --- S_1.4: Moments & Equilibrium ---
    elif pid.startswith("S_1.4"):
        if pid == "S_1.4_1":
            ax.plot([-2, 4], [0, 0], 'k', lw=4); ax.plot(0, -0.2, 'k^', markersize=15)
            ax.set_xlim(-3, 5); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.4_2":
            ax.plot([0, 3], [0, 0], 'gray', lw=8); ax.axvline(0, color='black', lw=10)
            ax.set_xlim(-1, 4); ax.set_ylim(-2, 2)
            found = True

    if not found:
        ax.text(0.5, 0.5, f"Diagram\n{pid}", color='gray', ha='center', va='center')
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.axis('off')
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def render_lecture_visual(topic, params=None):
    """Visualizes derivation components for Statics lectures."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    if params is None: params = {}
    
    # Standard Statics Grid
    ax.axhline(0, color='black', lw=1.5, zorder=2)
    ax.axvline(0, color='black', lw=1.5, zorder=2)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect('equal')
    
    if topic == "Method of Joints":
        # Visualizing force equilibrium at a single truss joint
        f1, f2 = params.get('f1', 10), params.get('f2', 10)
        angle = np.radians(params.get('angle', 30))
        
        # Draw forces acting on the joint
        ax.quiver(0, 0, -f1, 0, color='blue', angles='xy', scale_units='xy', scale=1, label=r'$F_1$')
        ax.quiver(0, 0, f2*np.cos(angle), f2*np.sin(angle), color='red', angles='xy', scale_units='xy', scale=1, label=r'$F_2$')
        ax.plot(0, 0, 'ko', markersize=10) # The Joint
        
        limit = max(f1, f2) + 5
        ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit)
        ax.set_title(r"Truss Joint Equilibrium: $\sum F_x = 0, \sum F_y = 0$")
        ax.legend()

    elif topic == "Moment Arm":
        force = params.get('force', 20)
        dist = params.get('dist', 4)
        ax.plot([0, dist], [0, 0], 'brown', lw=10, label='Beam') # Beam
        ax.quiver(dist, 0, 0, -force, color='red', angles='xy', scale_units='xy', scale=1, label='Force')
        ax.plot(0, 0, 'k^', markersize=15) # Pivot
        ax.set_title(r"Moment Calculation: $M = F \cdot d$")
        ax.set_xlim(-1, dist+2); ax.set_ylim(-force-5, 5)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
