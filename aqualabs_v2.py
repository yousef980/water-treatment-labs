"""
AQUALABS v2 — Advanced Water Treatment Processing Suite
Environmental Engineering Laboratory Tool
Yousef W. — M1 Génie de l'Environnement, Université Bouira

Fixes in v2:
  - Dual-model isotherm: auto-detects Langmuir vs Freundlich columns in one CSV
  - Drag-and-drop file import (tkinterdnd2 with fallback to dialog)
  - Labs 06–09 are fully implemented
  - Millimeter-paper style grid on all plots
  - Proper x/y axis labels on every graph
  - Annotations replaced with scatter markers + text boxes (no full-width lines)
  - Breakpoint / optimal dose shown with a small triangle marker, not axvline
  - Multi-table CSV: user picks which table to use via a dropdown
  - Export panel: PNG, CSV, PDF per graph
  - Startup splash to mask load time
  - Modernized UI: clean card layout, better typography, status bar
"""

import os
import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages

try:
    import openpyxl
except ImportError:
    pass

# ── optional drag-and-drop ──────────────────────────────────────────────────
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND = True
except ImportError:
    _DND = False

# ── palette ─────────────────────────────────────────────────────────────────
C = {
    "bg":       "#0d0f1a",
    "surface":  "#151824",
    "card":     "#1c2030",
    "border":   "#252a3a",
    "accent":   "#38bdf8",
    "green":    "#34d399",
    "amber":    "#fbbf24",
    "red":      "#f87171",
    "purple":   "#a78bfa",
    "text":     "#e2e8f0",
    "sub":      "#94a3b8",
    "muted":    "#475569",
    "mm_major": "#1e2840",
    "mm_minor": "#161c2e",
}

FONT_MONO  = ("Consolas",  9)
FONT_UI    = ("Segoe UI",  9)
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_HEAD  = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI",  8)

# ── millimeter-paper axes helper ────────────────────────────────────────────
def mm_axes(ax, xlabel="", ylabel="", title="", facecolor=None):
    fc = facecolor or C["card"]
    ax.set_facecolor(fc)
    ax.figure.set_facecolor(fc)
    # minor grid every 1 unit, major every 5
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.grid(which="major", color=C["mm_major"], linewidth=0.8, linestyle="-")
    ax.grid(which="minor", color=C["mm_minor"], linewidth=0.4, linestyle="-")
    ax.tick_params(colors=C["sub"], labelsize=8, which="both")
    for spine in ax.spines.values():
        spine.set_edgecolor(C["border"])
    ax.set_xlabel(xlabel, color=C["sub"], fontsize=9, labelpad=6)
    ax.set_ylabel(ylabel, color=C["sub"], fontsize=9, labelpad=6)
    if title:
        ax.set_title(title, color=C["text"], fontsize=9, fontweight="bold", pad=8)

def annotate_point(ax, x, y, label, color):
    """Small triangle marker + text box instead of full axvline."""
    ax.plot(x, y, marker="v", color=color, markersize=9, zorder=5)
    ax.annotate(
        label,
        xy=(x, y), xytext=(10, 12), textcoords="offset points",
        fontsize=8, color=color, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc=C["card"], ec=color, lw=0.8),
        arrowprops=dict(arrowstyle="-", color=color, lw=0.8),
    )

# ── multi-table CSV detector ─────────────────────────────────────────────────
def detect_tables(text):
    """Split a text file into separate numeric blocks separated by blank lines."""
    blocks, current = [], []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "":
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(stripped)
    if current:
        blocks.append("\n".join(current))
    # only keep blocks that contain at least 2 numeric rows
    valid = []
    for b in blocks:
        rows = [r for r in b.splitlines() if re.search(r"\d", r)]
        if len(rows) >= 2:
            valid.append(b)
    return valid

def parse_block_to_df(block):
    from io import StringIO
    try:
        df = pd.read_csv(StringIO(block))
        if df.shape[1] >= 2 and df.shape[0] >= 2:
            return df
    except Exception:
        pass
    numbers = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", block)]
    if len(numbers) < 4:
        return None
    half = len(numbers) // 2
    return pd.DataFrame({"Col1": numbers[:half], "Col2": numbers[half:]})

# ═══════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════
class AquaLabs(TkinterDnD.Tk if _DND else tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("AQUALABS v2 — Water Treatment Suite")
        self.geometry("1300x820")
        self.configure(bg=C["bg"])
        self.minsize(1000, 640)

        self._current_fig   = None   # track last matplotlib figure for export
        self._current_df    = None   # track last dataframe for CSV export
        self.current_frame  = None
        self.nav_history    = []

        self._show_splash()
        self._build_layout()
        self.navigate("Dashboard")

    # ── splash ───────────────────────────────────────────────────────────────
    def _show_splash(self):
        splash = tk.Toplevel(self)
        splash.overrideredirect(True)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = 420, 200
        splash.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        splash.configure(bg=C["surface"])
        tk.Label(splash, text="A Q U A L A B S", bg=C["surface"], fg=C["accent"],
                 font=("Consolas", 22, "bold")).pack(pady=(30, 6))
        tk.Label(splash, text="Water Treatment Laboratory Suite  v2",
                 bg=C["surface"], fg=C["sub"], font=FONT_UI).pack()
        bar_frame = tk.Frame(splash, bg=C["surface"])
        bar_frame.pack(pady=20, padx=40, fill="x")
        bar = ttk.Progressbar(bar_frame, length=340, mode="indeterminate")
        bar.pack()
        bar.start(12)
        splash.update()
        self.after(1800, splash.destroy)

    # ── layout ───────────────────────────────────────────────────────────────
    def _build_layout(self):
        # sidebar
        self.sidebar = tk.Frame(self, bg=C["surface"], width=256)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="AQUALABS", bg=C["surface"], fg=C["accent"],
                 font=("Consolas", 14, "bold")).pack(pady=(18, 2), anchor="w", padx=20)
        tk.Label(self.sidebar, text="Water Treatment Suite",
                 bg=C["surface"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", padx=20)

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=16, pady=10)

        nav_items = [
            ("⌂  Dashboard",                   "Dashboard"),
            ("01  Coagulation · Jar Test",      "JarTest"),
            ("02  Breakpoint Chlorination",     "Chlorination"),
            ("03  Suspended Solids",            "TSS"),
            ("04  Iron & Manganese Removal",    "IronManganese"),
            ("05  Nitrate Adsorption",          "Nitrate"),
            ("06  Lime-Soda Softening",         "LimeSoda"),
            ("07  Gram Staining",               "GramStaining"),
            ("08  Surface Hygiene",             "SurfaceHygiene"),
            ("09  Water Quality · Coliforms",   "WaterQuality"),
        ]

        self._nav_btns = {}
        for label, key in nav_items:
            btn = tk.Button(
                self.sidebar, text=label, anchor="w",
                bg=C["surface"], fg=C["text"],
                font=FONT_UI, bd=0, padx=18, pady=7,
                activebackground=C["card"], activeforeground=C["accent"],
                cursor="hand2",
                command=lambda k=key: self.navigate(k),
            )
            btn.pack(fill="x")
            self._nav_btns[key] = btn

        # footer nav
        tk.Frame(self.sidebar, bg=C["border"], height=1).pack(fill="x", padx=16, pady=8)
        tk.Button(self.sidebar, text="← Back", anchor="w",
                  bg=C["surface"], fg=C["sub"], font=FONT_UI, bd=0, padx=18, pady=6,
                  activebackground=C["card"], activeforeground=C["accent"],
                  cursor="hand2", command=self._go_back).pack(fill="x")
        tk.Button(self.sidebar, text="⌂  Home", anchor="w",
                  bg=C["surface"], fg=C["sub"], font=FONT_UI, bd=0, padx=18, pady=6,
                  activebackground=C["card"], activeforeground=C["accent"],
                  cursor="hand2", command=lambda: self.navigate("Dashboard")).pack(fill="x")

        # main workspace
        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="right", expand=True, fill="both")

        self.workspace = tk.Frame(right, bg=C["bg"])
        self.workspace.pack(expand=True, fill="both", padx=20, pady=(16, 0))

        # status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Frame(right, bg=C["surface"], height=26)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar, textvariable=self.status_var,
                 bg=C["surface"], fg=C["muted"], font=FONT_SMALL, anchor="w",
                 padx=12).pack(side="left")
        tk.Label(status_bar, text="AQUALABS v2  ·  Génie de l'Environnement",
                 bg=C["surface"], fg=C["muted"], font=FONT_SMALL, anchor="e",
                 padx=12).pack(side="right")

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    def _highlight_nav(self, key):
        for k, btn in self._nav_btns.items():
            btn.configure(bg=C["card"] if k == key else C["surface"],
                          fg=C["accent"] if k == key else C["text"])

    # ── navigation ───────────────────────────────────────────────────────────
    def navigate(self, key):
        if self.nav_history and self.nav_history[-1] == key:
            return
        self.nav_history.append(key)
        if len(self.nav_history) > 30:
            self.nav_history.pop(0)
        self._render(key)
        self._highlight_nav(key)

    def _go_back(self):
        if len(self.nav_history) <= 1:
            return
        self.nav_history.pop()
        self._render(self.nav_history[-1])
        self._highlight_nav(self.nav_history[-1])

    def _render(self, key):
        if self.current_frame:
            self.current_frame.destroy()
        plt.close("all")
        self._current_fig = None
        self._current_df  = None
        self.current_frame = tk.Frame(self.workspace, bg=C["bg"])
        self.current_frame.pack(expand=True, fill="both")
        {
            "Dashboard":    self._view_dashboard,
            "JarTest":      self._view_jartest,
            "Chlorination": self._view_chlorination,
            "TSS":          self._view_tss,
            "IronManganese":self._view_iron_manganese,
            "Nitrate":      self._view_nitrate,
            "LimeSoda":     self._view_limesoda,
            "GramStaining": self._view_gram_staining,
            "SurfaceHygiene":self._view_surface_hygiene,
            "WaterQuality": self._view_water_quality,
        }.get(key, self._view_dashboard)()

    # ── file import ──────────────────────────────────────────────────────────
    def _import_file(self, ce_entry=None, qe_entry=None,
                     x_entry=None, y_entry=None,
                     col_selector=None):
        """Universal import. Returns DataFrame or None."""
        path = filedialog.askopenfilename(
            filetypes=[
                ("All Lab Formats",  "*.csv *.xlsx *.xls *.txt"),
                ("CSV",              "*.csv"),
                ("Excel",            "*.xlsx *.xls"),
                ("Text",             "*.txt"),
            ]
        )
        if not path:
            return None
        return self._load_path(path, ce_entry, qe_entry, x_entry, y_entry)

    def _load_path(self, path, ce_entry=None, qe_entry=None,
                   x_entry=None, y_entry=None):
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".csv":
                text = open(path, encoding="utf-8", errors="replace").read()
                tables = detect_tables(text)
                if len(tables) > 1:
                    df = self._pick_table(tables)
                else:
                    from io import StringIO
                    df = pd.read_csv(StringIO(text))
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(path)
            elif ext == ".txt":
                text = open(path, encoding="utf-8", errors="replace").read()
                tables = detect_tables(text)
                df = self._pick_table(tables) if len(tables) > 1 else parse_block_to_df(text)
            else:
                df = None

            if df is None or df.shape[0] < 2:
                messagebox.showerror("Import Error", "File has fewer than 2 data rows.")
                return None

            self._current_df = df
            self._set_status(f"Loaded: {os.path.basename(path)}  ({len(df)} rows, {df.shape[1]} cols)")

            # populate entries
            col0 = df.iloc[:, 0].tolist()
            col1 = df.iloc[:, 1].tolist() if df.shape[1] > 1 else []

            def fill(entry, values):
                if entry:
                    entry.delete(0, tk.END)
                    entry.insert(0, ", ".join(str(v) for v in values))

            fill(ce_entry or x_entry, col0)
            fill(qe_entry or y_entry, col1)
            return df

        except Exception as e:
            messagebox.showerror("Import Error", str(e))
            return None

    def _pick_table(self, tables):
        """Ask user which table to use when multiple are detected."""
        win = tk.Toplevel(self)
        win.title("Multiple tables detected")
        win.configure(bg=C["surface"])
        win.geometry("500x340")
        win.grab_set()
        tk.Label(win, text=f"{len(tables)} data tables found in this file.",
                 bg=C["surface"], fg=C["text"], font=FONT_HEAD).pack(pady=(16, 4))
        tk.Label(win, text="Select the table to import:",
                 bg=C["surface"], fg=C["sub"], font=FONT_UI).pack()

        chosen = tk.IntVar(value=0)
        frame = tk.Frame(win, bg=C["surface"])
        frame.pack(fill="both", expand=True, padx=20, pady=8)

        canvas = tk.Canvas(frame, bg=C["surface"], bd=0, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=C["surface"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for i, t in enumerate(tables):
            preview = t[:120].replace("\n", " | ")
            rb = tk.Radiobutton(inner, text=f"Table {i+1}: {preview}…",
                                variable=chosen, value=i,
                                bg=C["surface"], fg=C["text"],
                                selectcolor=C["card"], font=FONT_SMALL,
                                anchor="w", wraplength=440)
            rb.pack(fill="x", pady=2)

        result = [None]

        def confirm():
            result[0] = parse_block_to_df(tables[chosen.get()])
            win.destroy()

        tk.Button(win, text="Use this table", bg=C["accent"], fg=C["bg"],
                  font=FONT_HEAD, bd=0, padx=16, pady=6,
                  command=confirm).pack(pady=10)
        win.wait_window()
        return result[0]

    # ── shared module layout ─────────────────────────────────────────────────
    def _module_layout(self, title):
        """Returns (ctrl_panel, display_panel)."""
        hdr = tk.Frame(self.current_frame, bg=C["bg"])
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text=title, bg=C["bg"], fg=C["text"],
                 font=FONT_TITLE).pack(side="left")

        body = tk.Frame(self.current_frame, bg=C["bg"])
        body.pack(expand=True, fill="both")

        ctrl = tk.Frame(body, bg=C["card"], width=252, padx=14, pady=14)
        ctrl.pack(side="left", fill="y", padx=(0, 14))
        ctrl.pack_propagate(False)

        disp = tk.Frame(body, bg=C["card"], padx=8, pady=8)
        disp.pack(side="left", expand=True, fill="both")

        return ctrl, disp

    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=C["card"], fg=C["sub"],
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(6, 1))

    def _entry(self, parent, default=""):
        e = tk.Entry(parent, bg=C["surface"], fg=C["text"], bd=0,
                     insertbackground=C["accent"],
                     highlightthickness=1, highlightcolor=C["accent"],
                     highlightbackground=C["border"], font=FONT_MONO)
        e.pack(fill="x", pady=(0, 2))
        e.insert(0, default)
        return e

    def _btn(self, parent, text, color, command):
        return tk.Button(parent, text=text, bg=color, fg=C["bg"],
                         font=FONT_HEAD, bd=0, pady=7, cursor="hand2",
                         activebackground=C["text"], command=command).pack(fill="x", pady=3)

    def _import_btn(self, parent, **kw):
        tk.Button(parent, text="📂  Import file (CSV / Excel / TXT)",
                  bg=C["surface"], fg=C["accent"], font=FONT_UI, bd=0,
                  pady=6, cursor="hand2",
                  command=lambda: self._import_file(**kw)).pack(fill="x", pady=(0, 10))

    def _clear_disp(self, disp):
        for w in disp.winfo_children():
            w.destroy()

    # ── export panel ─────────────────────────────────────────────────────────
    def _export_panel(self, parent):
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", pady=8)
        tk.Label(parent, text="Export", bg=C["card"], fg=C["sub"],
                 font=FONT_SMALL).pack(anchor="w")
        row = tk.Frame(parent, bg=C["card"])
        row.pack(fill="x", pady=3)
        for label, cmd in [("PNG", self._export_png),
                            ("PDF", self._export_pdf),
                            ("CSV", self._export_csv)]:
            tk.Button(row, text=label, bg=C["surface"], fg=C["accent"],
                      font=FONT_SMALL, bd=0, padx=10, pady=4,
                      cursor="hand2", command=cmd).pack(side="left", padx=2)

    def _export_png(self):
        if not self._current_fig:
            messagebox.showinfo("Export", "Run an analysis first."); return
        path = filedialog.asksaveasfilename(defaultextension=".png",
               filetypes=[("PNG Image", "*.png")])
        if path:
            self._current_fig.savefig(path, dpi=180, bbox_inches="tight",
                                      facecolor=self._current_fig.get_facecolor())
            self._set_status(f"Saved PNG → {path}")

    def _export_pdf(self):
        if not self._current_fig:
            messagebox.showinfo("Export", "Run an analysis first."); return
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
               filetypes=[("PDF Document", "*.pdf")])
        if path:
            with PdfPages(path) as pdf:
                pdf.savefig(self._current_fig, bbox_inches="tight",
                            facecolor=self._current_fig.get_facecolor())
            self._set_status(f"Saved PDF → {path}")

    def _export_csv(self):
        if self._current_df is None:
            messagebox.showinfo("Export", "No data to export yet."); return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
               filetypes=[("CSV File", "*.csv")])
        if path:
            self._current_df.to_csv(path, index=False)
            self._set_status(f"Saved CSV → {path}")

    def _embed_fig(self, fig, disp):
        self._clear_disp(disp)
        self._current_fig = fig
        canvas = FigureCanvasTkAgg(fig, master=disp)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    # ══════════════════════════════════════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════
    def _view_dashboard(self):
        tk.Label(self.current_frame, text="Laboratory Dashboard",
                 bg=C["bg"], fg=C["text"], font=FONT_TITLE).pack(anchor="w", pady=(0, 4))
        tk.Label(self.current_frame,
                 text="M1 Environmental Engineering  ·  Université Akli Mohand Oulhadj – Bouira",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(0, 14))

        canvas = tk.Canvas(self.current_frame, bg=C["bg"], bd=0, highlightthickness=0)
        sb = ttk.Scrollbar(self.current_frame, orient="vertical", command=canvas.yview)
        gf = tk.Frame(canvas, bg=C["bg"])
        gf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=gf, anchor="nw", width=920)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        modules = [
            ("01", "Coagulation & Jar Test",
             "Turbidity removal curve · optimal coagulant dose detection", C["accent"], "JarTest"),
            ("02", "Breakpoint Chlorination",
             "Chlorine demand curve · breakpoint identification", C["amber"], "Chlorination"),
            ("03", "Suspended Solids (TSS)",
             "Gravimetric MES determination · filter differential mass", C["green"], "TSS"),
            ("04", "Iron & Manganese Removal",
             "Oxidation-precipitation-filtration groundwater workflow", C["purple"], "IronManganese"),
            ("05", "Nitrate Adsorption Kinetics",
             "Langmuir & Freundlich isotherm fitting · dual-model from one file", C["accent"], "Nitrate"),
            ("06", "Lime-Soda Softening",
             "TH / TAC / hardness reduction · Ca(OH)₂ & Na₂CO₃ dosing", C["green"], "LimeSoda"),
            ("07", "Gram Staining",
             "G+/G− identification · morphology data entry & summary", C["amber"], "GramStaining"),
            ("08", "Surface Hygiene",
             "Swab colony count tracking · contamination index", C["purple"], "SurfaceHygiene"),
            ("09", "Water Quality · Coliforms",
             "MPN / colony count · potability assessment vs. OMS/Algerian norms", C["red"], "WaterQuality"),
        ]

        for num, name, desc, accent, route in modules:
            card = tk.Frame(gf, bg=C["card"], padx=16, pady=12)
            card.pack(fill="x", pady=3)
            left = tk.Frame(card, bg=C["card"])
            left.pack(side="left", fill="both", expand=True)
            tk.Label(left,
                     text=f"  {num}  ", bg=accent, fg=C["bg"],
                     font=("Consolas", 9, "bold")).pack(side="left",
                                                        anchor="n", pady=2, padx=(0, 10))
            info = tk.Frame(left, bg=C["card"])
            info.pack(side="left", fill="both")
            tk.Label(info, text=name, bg=C["card"], fg=C["text"],
                     font=FONT_HEAD, anchor="w").pack(anchor="w")
            tk.Label(info, text=desc, bg=C["card"], fg=C["sub"],
                     font=FONT_SMALL, anchor="w").pack(anchor="w")
            tk.Button(card, text="Open →", bg=C["surface"], fg=accent,
                      font=FONT_SMALL, bd=0, padx=10, pady=4, cursor="hand2",
                      command=lambda r=route: self.navigate(r)).pack(side="right", anchor="center")

    # ══════════════════════════════════════════════════════════════════════════
    #  01 · JAR TEST
    # ══════════════════════════════════════════════════════════════════════════
    def _view_jartest(self):
        ctrl, disp = self._module_layout("01 · Coagulation & Flocculation — Jar Test")
        self._import_btn(ctrl, x_entry=None, y_entry=None)  # will wire below

        self._label(ctrl, "Coagulant dose (mg/L)  — comma separated")
        ex = self._entry(ctrl, "10, 20, 30, 40, 50, 60")
        self._label(ctrl, "Residual turbidity (NTU)")
        ey = self._entry(ctrl, "14.2, 8.5, 1.8, 4.3, 9.1, 15.4")

        # rewire import button with actual entries
        ctrl.winfo_children()[0].configure(
            command=lambda: self._import_file(x_entry=ex, y_entry=ey))

        self._label(ctrl, "Coagulant type")
        coag_var = tk.StringVar(value="FeCl₃")
        ttk.Combobox(ctrl, textvariable=coag_var,
                     values=["FeCl₃", "Al₂(SO₄)₃", "PAC", "Other"],
                     state="readonly").pack(fill="x", pady=(0, 8))

        self._btn(ctrl, "▶  Run Analysis", C["green"],
                  lambda: self._run_jartest(ex, ey, coag_var, disp))
        self._export_panel(ctrl)

        # drag-and-drop
        if _DND:
            disp.drop_target_register(DND_FILES)
            disp.dnd_bind("<<Drop>>",
                lambda e: self._load_path(e.data.strip('{}'), x_entry=ex, y_entry=ey))
            tk.Label(disp, text="Drop a file here  or use Import above",
                     bg=C["card"], fg=C["muted"], font=FONT_SMALL).pack(expand=True)

    def _run_jartest(self, ex, ey, coag_var, disp):
        try:
            x = [float(v.strip()) for v in ex.get().split(",")]
            y = [float(v.strip()) for v in ey.get().split(",")]
            if len(x) != len(y): raise ValueError
        except Exception:
            messagebox.showerror("Input Error", "Doses and turbidities must match in length."); return

        df = pd.DataFrame({"Dose": x, "Turbidity": y})
        self._current_df = df
        opt = df.loc[df["Turbidity"].idxmin()]

        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        mm_axes(ax, xlabel=f"{coag_var.get()} dose (mg/L)",
                ylabel="Residual turbidity (NTU)",
                title="Turbidity Removal Curve — Jar Test")
        ax.plot(x, y, color=C["accent"], linewidth=1.8,
                marker="o", markersize=5, label="Turbidity")
        annotate_point(ax, opt["Dose"], opt["Turbidity"],
                       f"Optimal dose\n{opt['Dose']} mg/L → {opt['Turbidity']} NTU",
                       C["green"])
        ax.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=8, framealpha=0.8)
        plt.tight_layout()
        self._embed_fig(fig, disp)
        self._set_status(f"Optimal dose: {opt['Dose']} mg/L  |  Min turbidity: {opt['Turbidity']} NTU")

    # ══════════════════════════════════════════════════════════════════════════
    #  02 · BREAKPOINT CHLORINATION
    # ══════════════════════════════════════════════════════════════════════════
    def _view_chlorination(self):
        ctrl, disp = self._module_layout("02 · Breakpoint Chlorination")
        self._import_btn(ctrl)

        self._label(ctrl, "Chlorine dose applied (mg/L)")
        ex = self._entry(ctrl, "0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0")
        self._label(ctrl, "Total residual chlorine (mg/L)")
        ey = self._entry(ctrl, "0.4, 0.8, 1.1, 0.6, 0.2, 0.5, 1.0, 1.5")

        ctrl.winfo_children()[0].configure(
            command=lambda: self._import_file(x_entry=ex, y_entry=ey))

        self._btn(ctrl, "▶  Plot Breakpoint Curve", C["amber"],
                  lambda: self._run_chlorination(ex, ey, disp))
        self._export_panel(ctrl)

    def _run_chlorination(self, ex, ey, disp):
        try:
            x = [float(v.strip()) for v in ex.get().split(",")]
            y = [float(v.strip()) for v in ey.get().split(",")]
            if len(x) != len(y): raise ValueError
        except Exception:
            messagebox.showerror("Input Error", "Arrays must match in length."); return

        df = pd.DataFrame({"Dose": x, "Residual": y})
        self._current_df = df

        # breakpoint = minimum in the hump-trough region (skip first point)
        search = y[1:] if len(y) > 3 else y
        bp_idx = y.index(min(search[1:-1] if len(search) > 3 else search))

        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        mm_axes(ax, xlabel="Chlorine dose (mg/L)",
                ylabel="Total residual Cl (mg/L)",
                title="Breakpoint Chlorination Curve")

        # zones A B C D shading
        zones = [
            (0, x[1],        "#1a2a1a", "A: Cl₂ reacts\nwith organics"),
            (x[1], x[bp_idx],"#2a1a1a", "B: Chloramines\noxidised"),
            (x[bp_idx], x[-1],"#1a1a2a","C: Free residual\nchlorine"),
        ]
        for x0, x1, col, lbl in zones:
            ax.axvspan(x0, x1, alpha=0.3, color=col)
            ax.text((x0 + x1) / 2, max(y) * 0.92, lbl,
                    color=C["muted"], fontsize=7, ha="center")

        ax.plot(x, y, color=C["amber"], linewidth=1.8, marker="s",
                markersize=5, label="Total residual Cl")
        annotate_point(ax, x[bp_idx], y[bp_idx],
                       f"Breakpoint\n{x[bp_idx]} mg/L", C["red"])
        ax.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=8)
        plt.tight_layout()
        self._embed_fig(fig, disp)
        self._set_status(f"Breakpoint at {x[bp_idx]} mg/L  |  Min residual: {y[bp_idx]} mg/L")

    # ══════════════════════════════════════════════════════════════════════════
    #  03 · SUSPENDED SOLIDS (TSS)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_tss(self):
        ctrl, disp = self._module_layout("03 · Total Suspended Solids (MES) — Gravimetric")
        self._label(ctrl, "Sample volume V (mL)")
        ev  = self._entry(ctrl, "100")
        self._label(ctrl, "Clean filter mass m₁ (g)")
        em1 = self._entry(ctrl, "1.2435")
        self._label(ctrl, "Dried filter + residue mass m₂ (g)")
        em2 = self._entry(ctrl, "1.2488")
        self._label(ctrl, "Number of replicates")
        erep = self._entry(ctrl, "3")

        self._btn(ctrl, "▶  Calculate TSS", C["green"],
                  lambda: self._run_tss(ev, em1, em2, erep, disp))
        self._export_panel(ctrl)

    def _run_tss(self, ev, em1, em2, erep, disp):
        try:
            V    = float(ev.get())
            m1   = float(em1.get())
            m2   = float(em2.get())
            nrep = int(erep.get())
        except Exception:
            messagebox.showerror("Input Error", "Check all fields."); return

        tss = ((m2 - m1) * 1e6) / V   # mg/L
        self._current_df = pd.DataFrame({
            "Parameter": ["V (mL)", "m₁ (g)", "m₂ (g)", "Δm (g)", "TSS (mg/L)"],
            "Value":     [V, m1, m2, round(m2-m1, 4), round(tss, 2)],
        })

        self._clear_disp(disp)
        # result card
        frame = tk.Frame(disp, bg=C["card"])
        frame.pack(expand=True)
        tk.Label(frame, text="TSS Result", bg=C["card"], fg=C["sub"],
                 font=FONT_SMALL).pack(pady=(20, 4))
        tk.Label(frame, text=f"{tss:.2f} mg/L",
                 bg=C["card"], fg=C["green"], font=("Consolas", 28, "bold")).pack()
        tk.Label(frame, text=f"Δm = {(m2-m1)*1000:.2f} mg   ·   V = {V} mL   ·   n = {nrep} replicates",
                 bg=C["card"], fg=C["sub"], font=FONT_SMALL).pack(pady=(6, 20))

        # formula
        tk.Label(frame,
                 text="Formula:  TSS = (m₂ − m₁) × 10⁶ / V",
                 bg=C["card"], fg=C["muted"], font=FONT_MONO).pack()

        potable = "✔ Below 30 mg/L — meets WHO potability threshold" if tss < 30 \
                  else "✘ Exceeds 30 mg/L — treatment required"
        color = C["green"] if tss < 30 else C["red"]
        tk.Label(frame, text=potable, bg=C["card"], fg=color, font=FONT_UI).pack(pady=10)
        self._set_status(f"TSS = {tss:.2f} mg/L")

    # ══════════════════════════════════════════════════════════════════════════
    #  04 · IRON & MANGANESE REMOVAL
    # ══════════════════════════════════════════════════════════════════════════
    def _view_iron_manganese(self):
        ctrl, disp = self._module_layout("04 · Iron & Manganese Removal")
        self._label(ctrl, "Initial Fe²⁺ concentration C₀ (mg/L)")
        eC0  = self._entry(ctrl, "2.50")
        self._label(ctrl, "Final Fe concentration after treatment (mg/L)")
        eCf  = self._entry(ctrl, "0.12")
        self._label(ctrl, "Initial Mn²⁺ concentration (mg/L)")
        eMn0 = self._entry(ctrl, "0.45")
        self._label(ctrl, "Final Mn concentration (mg/L)")
        eMnf = self._entry(ctrl, "0.03")
        self._label(ctrl, "Treatment stages applied")
        stages_var = tk.StringVar(value="Aeration + Filtration")
        ttk.Combobox(ctrl, textvariable=stages_var,
                     values=["Aeration only", "Aeration + Filtration",
                             "Aeration + Chlorination + Filtration",
                             "KMnO₄ Oxidation + Filtration"],
                     state="readonly").pack(fill="x", pady=(0, 8))

        self._btn(ctrl, "▶  Evaluate Removal", C["purple"],
                  lambda: self._run_iron_mn(eC0, eCf, eMn0, eMnf, stages_var, disp))
        self._export_panel(ctrl)

    def _run_iron_mn(self, eC0, eCf, eMn0, eMnf, stages_var, disp):
        try:
            C0 = float(eC0.get()); Cf  = float(eCf.get())
            M0 = float(eMn0.get()); Mf = float(eMnf.get())
        except Exception:
            messagebox.showerror("Input Error", "Check all fields."); return

        fe_eff  = (C0 - Cf) / C0 * 100
        mn_eff  = (M0 - Mf) / M0 * 100
        fe_ok   = Cf <= 0.2
        mn_ok   = Mf <= 0.05

        self._current_df = pd.DataFrame({
            "Parameter":   ["Fe₀", "Fe_f", "Fe efficiency %", "Mn₀", "Mn_f", "Mn efficiency %"],
            "Value":       [C0, Cf, round(fe_eff,2), M0, Mf, round(mn_eff,2)],
        })

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 4), facecolor=C["card"])
        for ax, name, before, after, limit, unit in [
            (ax1, "Iron (Fe)", C0, Cf, 0.2, "mg/L"),
            (ax2, "Manganese (Mn)", M0, Mf, 0.05, "mg/L"),
        ]:
            mm_axes(ax, xlabel="Stage", ylabel=f"{name} ({unit})",
                    title=f"{name} Removal")
            ax.bar(["Before", "After"], [before, after],
                   color=[C["red"], C["green"]], width=0.4, zorder=3)
            ax.axhline(limit, color=C["amber"], linestyle="--", linewidth=1,
                       label=f"WHO limit {limit} {unit}")
            ax.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=7)
            for xi, val in enumerate([before, after]):
                ax.text(xi, val + 0.01, f"{val}", ha="center",
                        color=C["text"], fontsize=8)

        plt.suptitle(f"Treatment: {stages_var.get()}",
                     color=C["sub"], fontsize=8, y=1.01)
        plt.tight_layout()
        self._embed_fig(fig, disp)
        self._set_status(
            f"Fe removal: {fe_eff:.1f}%  {'✔' if fe_ok else '✘'}  |  "
            f"Mn removal: {mn_eff:.1f}%  {'✔' if mn_ok else '✘'}"
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  05 · NITRATE ADSORPTION — DUAL MODEL
    # ══════════════════════════════════════════════════════════════════════════
    def _view_nitrate(self):
        ctrl, disp = self._module_layout("05 · Nitrate Adsorption Kinetics — Langmuir & Freundlich")

        # mode
        mode_var = tk.StringVar(value="single")
        tk.Label(ctrl, text="Data mode", bg=C["card"], fg=C["sub"],
                 font=FONT_SMALL).pack(anchor="w", pady=(4, 2))
        mode_frame = tk.Frame(ctrl, bg=C["card"])
        mode_frame.pack(fill="x", pady=(0, 8))
        tk.Radiobutton(mode_frame, text="Single qe column",
                       variable=mode_var, value="single",
                       bg=C["card"], fg=C["text"], selectcolor=C["surface"],
                       font=FONT_SMALL).pack(side="left")
        tk.Radiobutton(mode_frame, text="Two qe columns (Lang | Freun)",
                       variable=mode_var, value="dual",
                       bg=C["card"], fg=C["text"], selectcolor=C["surface"],
                       font=FONT_SMALL).pack(side="left")

        self._import_btn(ctrl)

        self._label(ctrl, "Ce — equilibrium concentration (mg/L)")
        ece = self._entry(ctrl, "0.82, 1.54, 2.91, 4.63, 6.78, 9.12, 12.35, 16.20, 20.87")
        self._label(ctrl, "qe — Langmuir adsorbed capacity (mg/g)")
        eql = self._entry(ctrl, "0.13, 0.23, 0.40, 0.57, 0.74, 0.89, 1.04, 1.19, 1.31")
        self._label(ctrl, "qe — Freundlich column (leave blank if single)")
        eqf = self._entry(ctrl, "0.39, 0.49, 0.61, 0.72, 0.82, 0.91, 1.01, 1.12, 1.22")

        ctrl.winfo_children()[3].configure(   # import button
            command=lambda: self._import_nitrate(ece, eql, eqf, mode_var))

        self._btn(ctrl, "▶  Fit Isotherms", C["accent"],
                  lambda: self._run_nitrate(ece, eql, eqf, mode_var, disp))
        self._export_panel(ctrl)

    def _import_nitrate(self, ece, eql, eqf, mode_var):
        path = filedialog.askopenfilename(
            filetypes=[("All Lab Formats", "*.csv *.xlsx *.xls *.txt")])
        if not path: return
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".csv":
                text = open(path, encoding="utf-8", errors="replace").read()
                tables = detect_tables(text)
                from io import StringIO
                df = self._pick_table(tables) if len(tables) > 1 \
                     else pd.read_csv(StringIO(text))
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(path)
            else:
                text = open(path, encoding="utf-8", errors="replace").read()
                df = parse_block_to_df(text)

            if df is None or df.shape[0] < 2:
                messagebox.showerror("Import", "Not enough data rows."); return

            cols = df.shape[1]
            ece.delete(0, tk.END); ece.insert(0, ", ".join(str(v) for v in df.iloc[:,0]))
            eql.delete(0, tk.END); eql.insert(0, ", ".join(str(v) for v in df.iloc[:,1]))

            if cols >= 3:
                eqf.delete(0, tk.END); eqf.insert(0, ", ".join(str(v) for v in df.iloc[:,2]))
                mode_var.set("dual")
                self._set_status(f"Loaded {cols}-column file → dual-model mode activated")
            else:
                mode_var.set("single")
                self._set_status(f"Loaded 2-column file → single-model mode")

            self._current_df = df
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _run_nitrate(self, ece, eql, eqf, mode_var, disp):
        try:
            Ce  = np.array([float(v.strip()) for v in ece.get().split(",")])
            qeL = np.array([float(v.strip()) for v in eql.get().split(",")])
        except Exception:
            messagebox.showerror("Input Error", "Ce / qe (Langmuir) contain invalid values."); return

        dual = mode_var.get() == "dual" and eqf.get().strip()
        if dual:
            try:
                qeF = np.array([float(v.strip()) for v in eqf.get().split(",")])
                if len(qeF) != len(Ce): raise ValueError
            except Exception:
                messagebox.showerror("Input Error",
                    "Freundlich qe column length must match Ce."); return
        else:
            qeF = None

        # ── Langmuir linearization  Ce/qe = Ce/qmax + 1/(b*qmax) ──
        def langmuir_fit(ce, qe):
            y = ce / qe
            sl, ic = np.polyfit(ce, y, 1)
            qmax = 1 / sl
            b    = 1 / (ic * qmax)
            R2   = 1 - np.sum((y - (sl*ce+ic))**2) / np.sum((y - y.mean())**2)
            return qmax, b, sl, ic, R2

        # ── Freundlich linearization  ln(qe) = ln(Kf) + (1/n)*ln(Ce) ──
        def freundlich_fit(ce, qe):
            lce, lqe = np.log(ce), np.log(qe)
            sl, ic = np.polyfit(lce, lqe, 1)
            Kf = np.exp(ic)
            n  = 1 / sl
            R2 = 1 - np.sum((lqe-(sl*lce+ic))**2) / np.sum((lqe-lqe.mean())**2)
            return Kf, n, sl, ic, R2

        # ── fit both models on both datasets ──
        results = {}
        datasets = {"Langmuir data": (Ce, qeL)}
        if dual:
            datasets["Freundlich data"] = (Ce, qeF)

        for ds_name, (ce, qe) in datasets.items():
            try:
                qmax, b, sl_l, ic_l, r2_l = langmuir_fit(ce, qe)
                results[ds_name] = {"lang": (qmax, b, sl_l, ic_l, r2_l, ce, qe)}
            except Exception:
                pass
            try:
                Kf, n, sl_f, ic_f, r2_f = freundlich_fit(ce, qe)
                if ds_name not in results:
                    results[ds_name] = {}
                results[ds_name]["freun"] = (Kf, n, sl_f, ic_f, r2_f, ce, qe)
            except Exception:
                pass

        ncols = 2 if dual else 2
        nrows = len(datasets)
        fig, axes = plt.subplots(nrows, ncols, figsize=(8, 3.8 * nrows), facecolor=C["card"])
        if nrows == 1:
            axes = [axes]

        summary_lines = []

        for row, (ds_name, fits) in enumerate(results.items()):
            ax_l, ax_f = axes[row][0], axes[row][1]

            # Langmuir plot
            if "lang" in fits:
                qmax, b, sl_l, ic_l, r2_l, ce, qe = fits["lang"]
                y_plot = ce / qe
                mm_axes(ax_l, xlabel="Ce (mg/L)", ylabel="Ce / qe (g/L)",
                        title=f"Langmuir — {ds_name}  (R²={r2_l:.4f})")
                ax_l.scatter(ce, y_plot, color=C["accent"], s=30, zorder=4, label="Data")
                ce_line = np.linspace(ce.min(), ce.max(), 200)
                ax_l.plot(ce_line, sl_l*ce_line + ic_l, color=C["green"],
                          linewidth=1.5, linestyle="--", label="Linear fit")
                ax_l.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=7)
                summary_lines.append(
                    f"[{ds_name}] Langmuir: qmax={qmax:.3f} mg/g  b={b:.4f} L/mg  R²={r2_l:.4f}")
            else:
                ax_l.set_visible(False)

            # Freundlich plot
            if "freun" in fits:
                Kf, n, sl_f, ic_f, r2_f, ce, qe = fits["freun"]
                mm_axes(ax_f, xlabel="ln(Ce)", ylabel="ln(qe)",
                        title=f"Freundlich — {ds_name}  (R²={r2_f:.4f})")
                lce = np.log(ce)
                ax_f.scatter(lce, np.log(qe), color=C["amber"], s=30, zorder=4, label="Data")
                lce_line = np.linspace(lce.min(), lce.max(), 200)
                ax_f.plot(lce_line, sl_f*lce_line + ic_f, color=C["red"],
                          linewidth=1.5, linestyle=":", label="Linear fit")
                ax_f.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=7)
                summary_lines.append(
                    f"[{ds_name}] Freundlich: Kf={Kf:.4f}  1/n={sl_f:.4f}  n={n:.3f}  R²={r2_f:.4f}")
            else:
                ax_f.set_visible(False)

        plt.tight_layout(pad=1.6)
        self._embed_fig(fig, disp)
        self._set_status("  |  ".join(summary_lines[:2]))

        # summary text below graph
        for line in summary_lines:
            tk.Label(disp, text=line, bg=C["card"], fg=C["accent"],
                     font=FONT_SMALL).pack(anchor="w", padx=6)

    # ══════════════════════════════════════════════════════════════════════════
    #  06 · LIME-SODA SOFTENING
    # ══════════════════════════════════════════════════════════════════════════
    def _view_limesoda(self):
        ctrl, disp = self._module_layout("06 · Lime-Soda Chemical Softening")
        self._label(ctrl, "Total hardness TH₀ (mg CaCO₃/L)")
        eth0  = self._entry(ctrl, "320")
        self._label(ctrl, "Carbonate hardness TH_carb (mg CaCO₃/L)")
        ethc  = self._entry(ctrl, "180")
        self._label(ctrl, "Total alkalinity TAC (mg CaCO₃/L)")
        etac  = self._entry(ctrl, "200")
        self._label(ctrl, "Target residual hardness (mg CaCO₃/L)")
        etgt  = self._entry(ctrl, "50")
        self._label(ctrl, "Flow rate Q (m³/h)")
        eq    = self._entry(ctrl, "10")

        self._btn(ctrl, "▶  Calculate Reagent Doses", C["green"],
                  lambda: self._run_limesoda(eth0, ethc, etac, etgt, eq, disp))
        self._export_panel(ctrl)

    def _run_limesoda(self, eth0, ethc, etac, etgt, eq, disp):
        try:
            TH0  = float(eth0.get())
            THc  = float(ethc.get())
            TAC  = float(etac.get())
            TH_t = float(etgt.get())
            Q    = float(eq.get())
        except Exception:
            messagebox.showerror("Input Error", "Check all fields."); return

        # Non-carbonate hardness
        TH_nc = max(TH0 - THc, 0)
        # Ca(OH)₂ dose to remove carbonate hardness (MW Ca(OH)₂ = 74, CaCO₃ = 100)
        lime_dose  = TAC * (74 / 100)          # mg/L
        # Na₂CO₃ dose to remove non-carbonate hardness (MW Na₂CO₃ = 106)
        soda_dose  = TH_nc * (106 / 100)        # mg/L
        removal    = min((TH0 - TH_t) / TH0 * 100, 100)
        lime_kg_h  = lime_dose * Q / 1000
        soda_kg_h  = soda_dose * Q / 1000

        self._current_df = pd.DataFrame({
            "Parameter": ["TH₀", "TH_carb", "TH_nc", "TAC", "TH_target",
                          "Ca(OH)₂ dose mg/L", "Na₂CO₃ dose mg/L",
                          "Removal %", "Ca(OH)₂ kg/h", "Na₂CO₃ kg/h"],
            "Value": [TH0, THc, TH_nc, TAC, TH_t,
                      round(lime_dose,2), round(soda_dose,2),
                      round(removal,1), round(lime_kg_h,3), round(soda_kg_h,3)],
        })

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 4), facecolor=C["card"])

        # hardness breakdown bar
        mm_axes(ax1, xlabel="Hardness type", ylabel="mg CaCO₃/L",
                title="Hardness Composition")
        ax1.bar(["Total\nHardness", "Carbonate\nHardness", "Non-carbonate\nHardness", "Target"],
                [TH0, THc, TH_nc, TH_t],
                color=[C["red"], C["amber"], C["purple"], C["green"]], zorder=3)

        # reagent doses bar
        mm_axes(ax2, xlabel="Reagent", ylabel="Dose (mg/L)",
                title="Reagent Requirements")
        ax2.bar(["Ca(OH)₂\n(Lime)", "Na₂CO₃\n(Soda)"],
                [lime_dose, soda_dose],
                color=[C["accent"], C["green"]], zorder=3)
        for xi, val in enumerate([lime_dose, soda_dose]):
            ax2.text(xi, val + 1, f"{val:.1f}", ha="center",
                     color=C["text"], fontsize=9)

        plt.tight_layout()
        self._embed_fig(fig, disp)
        self._set_status(
            f"Ca(OH)₂: {lime_dose:.1f} mg/L ({lime_kg_h:.3f} kg/h)  |  "
            f"Na₂CO₃: {soda_dose:.1f} mg/L ({soda_kg_h:.3f} kg/h)  |  "
            f"Removal: {removal:.1f}%"
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  07 · GRAM STAINING
    # ══════════════════════════════════════════════════════════════════════════
    def _view_gram_staining(self):
        ctrl, disp = self._module_layout("07 · Gram Staining — Bacterial Identification")

        self._label(ctrl, "Sample / isolate ID")
        eid   = self._entry(ctrl, "Sample_01")
        self._label(ctrl, "Gram reaction")
        gram_var = tk.StringVar(value="Gram-positive (+)")
        ttk.Combobox(ctrl, textvariable=gram_var,
                     values=["Gram-positive (+)", "Gram-negative (−)", "Variable / indeterminate"],
                     state="readonly").pack(fill="x", pady=(0, 6))
        self._label(ctrl, "Cell morphology")
        morph_var = tk.StringVar(value="Coccus")
        ttk.Combobox(ctrl, textvariable=morph_var,
                     values=["Coccus", "Bacillus (rod)", "Spirillum", "Coccobacillus",
                             "Vibrio", "Spirochete", "Filamentous"],
                     state="readonly").pack(fill="x", pady=(0, 6))
        self._label(ctrl, "Arrangement")
        arr_var = tk.StringVar(value="Single")
        ttk.Combobox(ctrl, textvariable=arr_var,
                     values=["Single", "Diplo", "Tetrad", "Sarcina",
                             "Staphylo (cluster)", "Strepto (chain)"],
                     state="readonly").pack(fill="x", pady=(0, 6))
        self._label(ctrl, "Catalase test")
        cat_var = tk.StringVar(value="Positive (+)")
        ttk.Combobox(ctrl, textvariable=cat_var,
                     values=["Positive (+)", "Negative (−)", "Not tested"],
                     state="readonly").pack(fill="x", pady=(0, 8))

        self._btn(ctrl, "▶  Generate ID Summary", C["amber"],
                  lambda: self._run_gram(eid, gram_var, morph_var, arr_var, cat_var, disp))
        self._export_panel(ctrl)

    def _run_gram(self, eid, gram_var, morph_var, arr_var, cat_var, disp):
        sid    = eid.get().strip() or "Unknown"
        gram   = gram_var.get()
        morph  = morph_var.get()
        arr    = arr_var.get()
        cat    = cat_var.get()

        # simple genus suggestion logic
        gp = "+" in gram
        genus_hint = ""
        if gp and "Coccus" in morph:
            genus_hint = "→ Possible genus: Staphylococcus / Streptococcus / Micrococcus"
        elif gp and "Bacillus" in morph:
            genus_hint = "→ Possible genus: Bacillus / Lactobacillus / Clostridium"
        elif not gp and "Bacillus" in morph:
            genus_hint = "→ Possible genus: E. coli / Pseudomonas / Salmonella / Klebsiella"
        elif not gp and "Coccus" in morph:
            genus_hint = "→ Possible genus: Neisseria / Moraxella"

        self._current_df = pd.DataFrame({
            "Field":  ["Sample ID", "Gram", "Morphology", "Arrangement", "Catalase", "Genus hint"],
            "Result": [sid, gram, morph, arr, cat, genus_hint],
        })

        self._clear_disp(disp)
        card = tk.Frame(disp, bg=C["card"])
        card.pack(expand=True, padx=30, pady=20, fill="both")

        color = C["purple"] if gp else C["red"]
        tk.Label(card, text=sid, bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 2))
        tk.Label(card, text=gram, bg=C["card"], fg=color,
                 font=("Consolas", 20, "bold")).pack(anchor="w")

        for label, value in [("Morphology", morph), ("Arrangement", arr),
                              ("Catalase", cat), ("Genus hint", genus_hint)]:
            row = tk.Frame(card, bg=C["card"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{label}:", bg=C["card"], fg=C["sub"],
                     font=FONT_SMALL, width=14, anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=C["card"], fg=C["text"],
                     font=FONT_UI, anchor="w").pack(side="left")

        steps = [
            "1. Crystal violet (primary stain) — 60 s",
            "2. Gram's iodine (mordant) — 60 s",
            "3. Acetone/ethanol decolorizer — 10–15 s",
            "4. Safranin (counterstain) — 60 s",
            f"5. Result: {'PURPLE → G(+)' if gp else 'PINK/RED → G(−)'}",
        ]
        tk.Label(card, text="Protocol steps:", bg=C["card"], fg=C["sub"],
                 font=FONT_SMALL).pack(anchor="w", pady=(16, 2))
        for s in steps:
            tk.Label(card, text=s, bg=C["card"], fg=C["muted"],
                     font=FONT_MONO, anchor="w").pack(anchor="w")

        self._set_status(f"{sid} → {gram}  |  {morph}  |  {arr}")

    # ══════════════════════════════════════════════════════════════════════════
    #  08 · SURFACE HYGIENE
    # ══════════════════════════════════════════════════════════════════════════
    def _view_surface_hygiene(self):
        ctrl, disp = self._module_layout("08 · Surface Hygiene — Swab Colony Count")
        self._import_btn(ctrl)

        self._label(ctrl, "Surface labels  (comma separated)")
        elbl = self._entry(ctrl, "Bench A, Bench B, Door handle, Sink tap, Floor")
        self._label(ctrl, "Colony count (CFU/cm²)  — same order")
        ecfu = self._entry(ctrl, "12, 45, 87, 6, 120")
        self._label(ctrl, "Contamination threshold (CFU/cm²)")
        ethr = self._entry(ctrl, "50")

        ctrl.winfo_children()[0].configure(
            command=lambda: self._import_file(x_entry=elbl, y_entry=ecfu))

        self._btn(ctrl, "▶  Analyse Swab Results", C["purple"],
                  lambda: self._run_hygiene(elbl, ecfu, ethr, disp))
        self._export_panel(ctrl)

    def _run_hygiene(self, elbl, ecfu, ethr, disp):
        try:
            labels = [v.strip() for v in elbl.get().split(",")]
            cfus   = [float(v.strip()) for v in ecfu.get().split(",")]
            thr    = float(ethr.get())
            if len(labels) != len(cfus): raise ValueError
        except Exception:
            messagebox.showerror("Input Error", "Labels and CFU counts must match."); return

        df = pd.DataFrame({"Surface": labels, "CFU_per_cm2": cfus})
        self._current_df = df

        colors = [C["red"] if c > thr else C["green"] for c in cfus]

        fig, ax = plt.subplots(figsize=(6.5, 4), facecolor=C["card"])
        mm_axes(ax, xlabel="Surface", ylabel="CFU / cm²",
                title="Surface Contamination Index")
        bars = ax.bar(labels, cfus, color=colors, zorder=3)
        ax.axhline(thr, color=C["amber"], linestyle="--", linewidth=1.2,
                   label=f"Threshold: {thr} CFU/cm²")
        for bar, val in zip(bars, cfus):
            ax.text(bar.get_x() + bar.get_width()/2, val + 1,
                    str(int(val)), ha="center", color=C["text"], fontsize=8)
        ax.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=8)
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        self._embed_fig(fig, disp)

        n_fail = sum(1 for c in cfus if c > thr)
        self._set_status(
            f"{n_fail}/{len(cfus)} surfaces exceed {thr} CFU/cm²  |  "
            f"Max: {max(cfus):.0f} @ {labels[cfus.index(max(cfus))]}"
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  09 · WATER QUALITY — COLIFORMS
    # ══════════════════════════════════════════════════════════════════════════
    def _view_water_quality(self):
        ctrl, disp = self._module_layout("09 · Biological Water Quality — Coliform Tracking")
        self._label(ctrl, "Sample IDs (comma separated)")
        eid  = self._entry(ctrl, "S1, S2, S3, S4, S5")
        self._label(ctrl, "Total coliforms (CFU/100 mL)")
        etc  = self._entry(ctrl, "0, 12, 0, 45, 3")
        self._label(ctrl, "Fecal coliforms E. coli (CFU/100 mL)")
        efc  = self._entry(ctrl, "0, 0, 0, 8, 1")
        self._label(ctrl, "Sampling point")
        src_var = tk.StringVar(value="Distribution network")
        ttk.Combobox(ctrl, textvariable=src_var,
                     values=["Source water", "After treatment",
                             "Distribution network", "Consumer tap"],
                     state="readonly").pack(fill="x", pady=(0, 8))

        self._btn(ctrl, "▶  Assess Potability", C["red"],
                  lambda: self._run_water_quality(eid, etc, efc, src_var, disp))
        self._export_panel(ctrl)

    def _run_water_quality(self, eid, etc, efc, src_var, disp):
        try:
            ids  = [v.strip() for v in eid.get().split(",")]
            tc   = [float(v.strip()) for v in etc.get().split(",")]
            fc   = [float(v.strip()) for v in efc.get().split(",")]
            if len(ids) != len(tc) or len(tc) != len(fc): raise ValueError
        except Exception:
            messagebox.showerror("Input Error", "All three lists must be the same length."); return

        # WHO / Algerian norm: TC = 0 CFU/100 mL for treated water
        TC_LIMIT = 0 if "treatment" in src_var.get().lower() or "tap" in src_var.get().lower() else 100
        FC_LIMIT = 0

        df = pd.DataFrame({"Sample": ids, "Total_coliforms": tc, "Fecal_coliforms": fc})
        df["TC_pass"] = df["Total_coliforms"] <= TC_LIMIT
        df["FC_pass"] = df["Fecal_coliforms"] <= FC_LIMIT
        df["Potable"] = df["TC_pass"] & df["FC_pass"]
        self._current_df = df

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.5, 5.5), facecolor=C["card"])
        mm_axes(ax1, xlabel="Sample", ylabel="CFU / 100 mL",
                title=f"Total Coliforms — {src_var.get()}")
        tc_colors = [C["green"] if v <= TC_LIMIT else C["red"] for v in tc]
        ax1.bar(ids, tc, color=tc_colors, zorder=3)
        ax1.axhline(TC_LIMIT, color=C["amber"], linestyle="--",
                    linewidth=1, label=f"Limit {TC_LIMIT} CFU/100mL")
        ax1.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=7)

        mm_axes(ax2, xlabel="Sample", ylabel="E. coli CFU / 100 mL",
                title="Fecal Coliforms (E. coli)")
        fc_colors = [C["green"] if v == 0 else C["red"] for v in fc]
        ax2.bar(ids, fc, color=fc_colors, zorder=3)
        ax2.axhline(0, color=C["amber"], linestyle="--", linewidth=1,
                    label="Limit: 0 CFU/100 mL")
        ax2.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=7)

        plt.tight_layout()
        self._embed_fig(fig, disp)

        n_potable = df["Potable"].sum()
        self._set_status(
            f"{n_potable}/{len(ids)} samples potable  |  "
            f"Limit: TC ≤ {TC_LIMIT}  FC = 0  CFU/100 mL  [{src_var.get()}]"
        )


# ── entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = AquaLabs()
    app.mainloop()
