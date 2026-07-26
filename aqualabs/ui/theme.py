import customtkinter as ctk
import matplotlib.ticker as ticker

# ── MIDNIGHT OCEAN PALETTE ─────────────────────────────────────────────────
COLORS = {
    "bg":       "#171821",    # Main app background
    "surface":  "#21222D",    # Sidebar and Panel background
    "card":     "#21222D",    # Card Background
    "border":   "#21222D",    # Blend in border
    "accent":   "#08DAC1",    # Teal/Cyan
    "green":    "#2DE2AA",    # Neon green
    "amber":    "#F4BE37",    # Yellow
    "red":      "#F7604D",    # Bright red/orange
    "purple":   "#E14F9C",    # Pink/Magenta
    "text":     "#FFFFFF",    # Pure White Text
    "sub":      "#A0A0A0",    # Soft Grey text
    "muted":    "#36384A",    # Lighter grey for dividers/inputs
}

def style_matplotlib_axes(ax, xlabel="", ylabel="", title="", facecolor=None):
    fc = facecolor or COLORS["card"]
    ax.set_facecolor(COLORS["bg"])
    ax.figure.set_facecolor(fc)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.grid(which="major", color=COLORS["surface"], linewidth=0.8, linestyle="-")
    ax.grid(which="minor", color=COLORS["bg"], linewidth=0.4, linestyle="-")
    ax.tick_params(colors=COLORS["text"], labelsize=8, which="both")
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS["border"])
        spine.set_linewidth(1.5)
    ax.set_xlabel(xlabel, color=COLORS["text"], fontsize=9, fontweight="bold", labelpad=6)
    ax.set_ylabel(ylabel, color=COLORS["text"], fontsize=9, fontweight="bold", labelpad=6)
    if title:
        ax.set_title(title, color=COLORS["text"], fontsize=10, fontweight="bold", pad=8)

def annotate_point(ax, x, y, label, color):
    ax.plot(x, y, marker="v", color=color, markersize=10, zorder=5)
    ax.annotate(
        label, xy=(x, y), xytext=(10, 12), textcoords="offset points",
        fontsize=8, color=color, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc=COLORS["card"], ec=color, lw=1.5),
        arrowprops=dict(arrowstyle="-", color=color, lw=1.5),
    )
