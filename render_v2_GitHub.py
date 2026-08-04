import io
import os
import matplotlib.pyplot as plt
import numpy as np


def render_lecture_visual(topic, params=None):
    """Visualizes Statics concepts with High DPI (300) for crispness."""
    fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=300)
    if params is None:
        params = {}

    ax.axhline(0, color="gray", lw=1.5, zorder=2)
    ax.axvline(0, color="gray", lw=1.5, zorder=2)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.set_aspect("equal")

    limit = 100

    if topic == "Free Body Diagram":
        force = params.get("force", 50)
        theta = np.radians(params.get("theta", 45))
        ax.quiver(
            0,
            0,
            force * np.cos(theta),
            force * np.sin(theta),
            color="#00E5FF",
            angles="xy",
            scale_units="xy",
            scale=1,
            label=r"$\vec{F}$",
            zorder=3,
        )
        ax.plot(0, 0, "ro", markersize=6, zorder=4)
        limit = 110

    elif topic == "Truss":
        f_load = params.get("load", 50)
        ax.quiver(
            0,
            0,
            0,
            -f_load,
            color="#FF5252",
            angles="xy",
            scale_units="xy",
            scale=1,
            zorder=3,
        )
        ax.quiver(
            0,
            0,
            -40,
            40,
            color="#69F0AE",
            angles="xy",
            scale_units="xy",
            scale=1,
            zorder=3,
        )
        ax.quiver(
            0,
            0,
            40,
            40,
            color="#448AFF",
            angles="xy",
            scale_units="xy",
            scale=1,
            zorder=3,
        )
        ax.plot(0, 0, "ko", markersize=6, zorder=4)

    elif topic == "Geometric Properties":
        w, h = params.get("width", 40), params.get("height", 60)
        ax.add_patch(
            plt.Rectangle(
                (-w / 2, -h / 2),
                w,
                h,
                fill=True,
                facecolor="#37474F",
                edgecolor="white",
                hatch="//",
                lw=1.5,
            )
        )
        ax.plot(0, 0, "rx", markersize=10, markeredgewidth=2, zorder=4)

    elif topic == "Equilibrium":
        weight, dist = params.get("w", 50), params.get("d", 40)
        ax.plot([-dist, dist], [0, 0], "#8D6E63", lw=6)
        ax.plot(0, -5, "w^", markersize=10, zorder=4)
        ax.quiver(
            -dist,
            0,
            0,
            -weight,
            color="#FF5252",
            angles="xy",
            scale_units="xy",
            scale=1,
            zorder=3,
        )

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf


def render_problem_diagram(prob):
    """High-quality procedural drawing for Statics problems."""
    fig, ax = plt.subplots(figsize=(2.2, 2.2), dpi=300)
    ax.set_aspect("equal")
    p_id = prob.get("id", "")

    # --- S_1.1: FBD Problems ---
    if p_id == "S_1.1_1":
        # Cable A & Cable B & Mass cable
        ax.plot([-25, 0], [0, 0], color="#00E5FF", lw=2.5, zorder=2)
        ax.plot([0, 20], [0, 20], color="#00E5FF", lw=2.5, zorder=2)
        ax.plot([0, 0], [0, -12], color="#00E5FF", lw=2, zorder=2)

        # Support walls
        ax.plot([-25, -25], [-10, 10], color="gray", lw=4)
        ax.plot([14, 24], [26, 14], color="gray", lw=4)

        # Mass block
        ax.add_patch(
            plt.Rectangle(
                (-7, -22), 14, 10, color="#2C3E50", ec="white", lw=1, zorder=3
            )
        )
        ax.text(
            0,
            -17,
            "50kg",
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            fontsize=6.5,
        )

        ax.plot(0, 0, "ro", markersize=4, zorder=4)
        ax.text(
            -12,
            3,
            "Cable A",
            color="white",
            fontsize=6.5,
            fontweight="bold",
            ha="center",
        )
        ax.text(
            10,
            8,
            r"Cable B ($45^\circ$)",
            color="white",
            fontsize=6.5,
            fontweight="bold",
            ha="center",
        )
        ax.set_xlim(-30, 30)
        ax.set_ylim(-26, 28)

    elif p_id == "S_1.1_2":
        # Incline plane setup
        theta = np.radians(30)
        x_max, y_max = 40, 40 * np.tan(theta)

        # Ramp wedge surface
        ax.plot([0, x_max], [0, y_max], color="white", lw=2.5, zorder=2)
        ax.plot([0, x_max], [0, 0], color="gray", lw=1.5, ls="--")
        ax.plot([x_max, x_max], [0, y_max], color="gray", lw=1.5, ls="--")

        # Block placed on incline surface
        bx, by = 20, 20 * np.tan(theta)
        ax.plot(bx, by, "bs", markersize=14, zorder=3)
        ax.text(
            bx,
            by + 6,
            "20kg",
            ha="center",
            va="center",
            color="white",
            fontsize=6.5,
            fontweight="bold",
        )
        ax.text(
            8,
            2,
            r"$30^\circ$",
            color="#00E5FF",
            fontsize=7,
            fontweight="bold",
        )
        ax.set_xlim(-5, 45)
        ax.set_ylim(-5, 30)

    elif p_id == "S_1.1_3":
        # Cantilever Beam with wall support
        ax.plot([-5, -5], [-12, 12], color="gray", lw=4)  # Fixed Wall
        ax.plot([ -5, 35], [0, 0], color="#8D6E63", lw=6, zorder=2)  # Beam

        # Point Load at end B
        ax.quiver(
            35,
            0,
            0,
            -15,
            color="#FF5252",
            scale=1,
            scale_units="xy",
            angles="xy",
            zorder=3,
        )
        ax.text(
            -5,
            4,
            "A (Fixed)",
            fontweight="bold",
            fontsize=6.5,
            color="white",
            ha="center",
        )
        ax.text(
            35,
            5,
            "B (Load)",
            fontweight="bold",
            fontsize=6.5,
            color="white",
            ha="center",
        )
        ax.set_xlim(-12, 45)
        ax.set_ylim(-20, 15)

    # --- S_1.2: Truss Problems ---
    elif "S_1.2" in p_id:
        if p_id == "S_1.2_1":
            nodes = np.array(
                [[0, 0], [20, 0], [40, 0], [30, 15], [10, 15], [0, 0]]
            )
            ax.plot(
                nodes[:, 0], nodes[:, 1], "w-o", lw=1.5, markersize=4, zorder=2
            )
            ax.quiver(
                20,
                0,
                0,
                -12,
                color="#FF5252",
                scale=1,
                scale_units="xy",
                angles="xy",
                zorder=3,
            )
            ax.text(
                20,
                -8,
                "10kN",
                ha="center",
                fontsize=7,
                color="#FF5252",
                fontweight="bold",
            )
            ax.set_xlim(-5, 45)
            ax.set_ylim(-18, 22)

        elif p_id == "S_1.2_2":
            nodes = np.array([[0, 0], [40, 0], [20, 34.6], [0, 0]])
            ax.plot(
                nodes[:, 0], nodes[:, 1], "w-o", lw=1.5, markersize=4, zorder=2
            )
            ax.quiver(
                20,
                34.6,
                0,
                -15,
                color="#FF5252",
                scale=1,
                scale_units="xy",
                angles="xy",
                zorder=3,
            )
            ax.set_xlim(-5, 45)
            ax.set_ylim(-5, 42)

        elif p_id == "S_1.2_3":
            ax.plot(
                [0, 20, 40, 60, 40, 20, 0],
                [0, 0, 0, 0, 20, 20, 0],
                "w-o",
                lw=1.5,
                markersize=4,
                zorder=2,
            )
            ax.plot([20, 20], [0, 20], "w-", lw=1.5)
            ax.plot([40, 40], [0, 20], "w-", lw=1.5)
            ax.text(
                30,
                -8,
                "Pratt Truss",
                ha="center",
                fontsize=7,
                color="white",
                fontweight="bold",
            )
            ax.set_xlim(-5, 65)
            ax.set_ylim(-12, 28)

    # --- S_1.3: Geometry ---
    elif "S_1.3" in p_id:
        if p_id == "S_1.3_1":
            ax.add_patch(
                plt.Rectangle(
                    (0, 0),
                    40,
                    60,
                    facecolor="#00BCD4",
                    edgecolor="white",
                    alpha=0.4,
                )
            )
            ax.plot(20, 30, "rx", markersize=10, markeredgewidth=2)
            ax.text(
                22,
                30,
                r"$\bar{y}$",
                color="#FF5252",
                fontsize=9,
                fontweight="bold",
            )
            ax.set_xlim(-5, 45)
            ax.set_ylim(-5, 65)

        elif p_id == "S_1.3_2":
            ax.add_patch(
                plt.Rectangle(
                    (0, 0),
                    20,
                    20,
                    facecolor="#FF9800",
                    edgecolor="white",
                    alpha=0.4,
                )
            )
            ax.quiver(
                0, 0, 25, 0, color="white", scale=1, scale_units="xy", width=0.015
            )
            ax.quiver(
                0, 0, 0, 25, color="white", scale=1, scale_units="xy", width=0.015
            )
            ax.text(25, -2, "x", fontsize=7, color="white")
            ax.text(-3, 25, "y", fontsize=7, color="white")
            ax.text(
                10,
                22,
                "a=0.2m",
                ha="center",
                fontsize=7,
                color="white",
                fontweight="bold",
            )
            ax.set_xlim(-8, 32)
            ax.set_ylim(-8, 32)

        elif p_id == "S_1.3_3":
            ax.add_patch(
                plt.Rectangle(
                    (0, 1),
                    1,
                    3,
                    facecolor="#4CAF50",
                    edgecolor="white",
                    alpha=0.4,
                )
            )
            ax.add_patch(
                plt.Rectangle(
                    (0, 0),
                    4,
                    1,
                    facecolor="#4CAF50",
                    edgecolor="white",
                    alpha=0.4,
                )
            )
            ax.plot([-0.5, -0.5], [0, 4], "w-", lw=0.8)
            ax.text(
                -1.2,
                2,
                "4m",
                va="center",
                rotation=90,
                fontsize=6.5,
                color="white",
            )
            ax.plot([0, 4], [-0.5, -0.5], "w-", lw=0.8)
            ax.text(2, -1.2, "4m", ha="center", fontsize=6.5, color="white")
            ax.set_xlim(-2, 5)
            ax.set_ylim(-2, 5)

    # --- S_1.4: Equilibrium ---
    elif "S_1.4" in p_id:
        if p_id == "S_1.4_1":
            ax.plot([-20, 40], [0, 0], color="#8D6E63", lw=6, zorder=2)
            ax.plot(0, -2, "w^", markersize=8, zorder=3)  # Fulcrum Support
            ax.quiver(
                -20,
                0,
                0,
                -15,
                color="#FF5252",
                scale=1,
                scale_units="xy",
                angles="xy",
                zorder=4,
            )
            ax.quiver(
                40,
                0,
                0,
                -10,
                color="#00E5FF",
                scale=1,
                scale_units="xy",
                angles="xy",
                zorder=4,
            )
            ax.text(-20, 5, "10N", fontsize=7, color="white", fontweight="bold")
            ax.text(40, 5, "F?", fontsize=7, color="white", fontweight="bold")
            ax.set_xlim(-28, 48)
            ax.set_ylim(-20, 12)

        elif p_id == "S_1.4_2":
            ax.plot([0, 40], [0, 0], color="#8D6E63", lw=6, zorder=2)
            ax.plot([-2, -2], [-10, 10], color="gray", lw=4)  # Left Wall Pin
            ax.quiver(
                40,
                0,
                0,
                -15,
                color="#FF5252",
                scale=1,
                scale_units="xy",
                angles="xy",
                zorder=3,
            )
            ax.text(
                32,
                5,
                "100N",
                fontsize=7,
                color="white",
                fontweight="bold",
            )
            ax.set_xlim(-8, 48)
            ax.set_ylim(-20, 12)

        elif p_id == "S_1.4_3":
            # Log carry beam representation
            ax.plot([0, 60], [0, 0], color="#FFB74D", lw=8, zorder=2)
            # Reaction force at A
            ax.quiver(
                0,
                0,
                0,
                15,
                color="#00E5FF",
                scale=1,
                scale_units="xy",
                angles="xy",
                zorder=3,
            )
            ax.text(
                0,
                18,
                "A",
                fontsize=7,
                ha="center",
                color="white",
                fontweight="bold",
            )
            # Reaction force at B
            ax.quiver(
                40,
                0,
                0,
                15,
                color="#00E5FF",
                scale=1,
                scale_units="xy",
                angles="xy",
                zorder=3,
            )
            ax.text(
                40,
                18,
                "B",
                fontsize=7,
                ha="center",
                color="white",
                fontweight="bold",
            )
            # Center of Gravity Weight
            ax.quiver(
                30,
                0,
                0,
                -20,
                color="#FF5252",
                scale=1,
                scale_units="xy",
                angles="xy",
                zorder=3,
            )
            ax.text(
                30,
                -25,
                "60kg",
                fontsize=7,
                ha="center",
                color="white",
                fontweight="bold",
            )
            ax.set_xlim(-10, 70)
            ax.set_ylim(-32, 28)

    else:
        ax.text(
            0.5,
            0.5,
            "Diagram",
            ha="center",
            transform=ax.transAxes,
            fontsize=8,
            color="white",
        )

    ax.axis("off")
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
