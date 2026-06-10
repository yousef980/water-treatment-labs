"""
AQUALABS v2.2 — Advanced Water Treatment Processing Suite
Environmental Engineering Laboratory Tool
Developed by: Youcef Youcef

Fixes in v2.2 (Midnight Ocean Edition):
  - Black, deep blue, and emerald green palette with seamless borders
  - Lab 5: UI clipping fixed. Added Temkin Isotherm + Best Fit Auto-Verification
  - Lab 4 & 9: Explicit POTABLE / NON-POTABLE compliance stamps
  - Lab 7: Fixed Bacillus genus hint logic
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

# ── MIDNIGHT BLUE & EMERALD PALETTE ─────────────────────────────────────────
C = {
    "bg":       "#020617",    # Very Dark Slate (Almost Black)
    "surface":  "#0F172A",    # Deep Navy Blue
    "card":     "#1E293B",    # Slate Blue Panel
    "border":   "#38BDF8",    # Light Sky Blue edges
    "accent":   "#38BDF8",    # Cyan Blue
    "green":    "#10B981",    # Emerald Green (Passing)
    "amber":    "#F59E0B",    # Amber Yellow
    "red":      "#EF4444",    # Crimson Red (Failing)
    "purple":   "#8B5CF6",    # Violet
    "text":     "#F8FAFC",    # Pure White Text
    "sub":      "#94A3B8",    # Soft Blue-Grey text
    "muted":    "#475569",    # Dark Grey
    "mm_major": "#1E293B",    # Grid lines
    "mm_minor": "#0F172A",    # Sub-grid lines
}

FONT_MONO  = ("Consolas",  9)
FONT_UI    = ("Segoe UI",  9)
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_HEAD  = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI",  8)

def mm_axes(ax, xlabel="", ylabel="", title="", facecolor=None):
    fc = facecolor or C["card"]
    ax.set_facecolor("#020617")
    ax.figure.set_facecolor(fc)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.grid(which="major", color=C["mm_major"], linewidth=0.8, linestyle="-")
    ax.grid(which="minor", color=C["mm_minor"], linewidth=0.4, linestyle="-")
    ax.tick_params(colors=C["text"], labelsize=8, which="both")
    for spine in ax.spines.values():
        spine.set_edgecolor(C["border"])
        spine.set_linewidth(1.5)
    ax.set_xlabel(xlabel, color=C["text"], fontsize=9, fontweight="bold", labelpad=6)
    ax.set_ylabel(ylabel, color=C["text"], fontsize=9, fontweight="bold", labelpad=6)
    if title:
        ax.set_title(title, color=C["text"], fontsize=10, fontweight="bold", pad=8)

def annotate_point(ax, x, y, label, color):
    ax.plot(x, y, marker="v", color=color, markersize=10, zorder=5)
    ax.annotate(
        label, xy=(x, y), xytext=(10, 12), textcoords="offset points",
        fontsize=8, color=color, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc=C["card"], ec=color, lw=1.5),
        arrowprops=dict(arrowstyle="-", color=color, lw=1.5),
    )

def detect_tables(text):
    blocks, current = [], []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "":
            if current: blocks.append("\n".join(current)); current = []
        else: current.append(stripped)
    if current: blocks.append("\n".join(current))
    valid = [b for b in blocks if len([r for r in b.splitlines() if re.search(r"\d", r)]) >= 2]
    return valid

def parse_block_to_df(block):
    from io import StringIO
    try:
        df = pd.read_csv(StringIO(block))
        if df.shape[1] >= 2 and df.shape[0] >= 2: return df
    except Exception: pass
    numbers = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", block)]
    if len(numbers) < 4: return None
    half = len(numbers) // 2
    return pd.DataFrame({"Col1": numbers[:half], "Col2": numbers[half:]})

# ═══════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════
class AquaLabs(TkinterDnD.Tk if _DND else tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("AQUALABS v2.2 — Water Treatment Suite")
        self.geometry("1300x820")
        self.configure(bg=C["bg"])
        self.minsize(1100, 700)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=C["bg"], foreground=C["text"], fieldbackground=C["card"])
        style.configure("TProgressbar", background=C["accent"])

        self._current_fig   = None
        self._current_df    = None
        self.current_frame  = None
        self.nav_history    = []

        self._build_layout()
        self.navigate("Dashboard")

    def _build_layout(self):
        # Sidebar with seamless groove relief
        self.sidebar = tk.Frame(self, bg=C["surface"], width=260, bd=2, relief="groove")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="AQUALABS", bg=C["surface"], fg=C["text"],
                 font=("Consolas", 16, "bold")).pack(pady=(20, 2), anchor="w", padx=20)
        tk.Label(self.sidebar, text="Water Treatment Suite",
                 bg=C["surface"], fg=C["accent"], font=FONT_SMALL).pack(anchor="w", padx=20)

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=16, pady=15)

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
                font=FONT_UI, bd=0, padx=18, pady=8,
                activebackground=C["card"], activeforeground=C["accent"],
                cursor="hand2", command=lambda k=key: self.navigate(k),
            )
            btn.pack(fill="x", padx=5)
            self._nav_btns[key] = btn

        tk.Frame(self.sidebar, bg=C["card"], height=2).pack(fill="x", padx=16, pady=10)
        
        # main workspace
        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="right", expand=True, fill="both")

        self.workspace = tk.Frame(right, bg=C["bg"])
        self.workspace.pack(expand=True, fill="both", padx=20, pady=(16, 0))

        # Signature Bar
        signature_bar = tk.Frame(right, bg=C["surface"], height=30, bd=2, relief="groove")
        signature_bar.pack(fill="x", side="bottom")
        tk.Label(signature_bar, text="Developed by: Youcef Youcef  |  M1 Génie de l'Environnement — Université de Bouira",
                 bg=C["surface"], fg=C["accent"], font=("Arial", 9, "bold"), anchor="e", padx=15).pack(side="right", pady=4)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Frame(right, bg=C["bg"], height=26)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar, textvariable=self.status_var, bg=C["bg"], fg=C["green"], font=FONT_SMALL, anchor="w", padx=12).pack(side="left")

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    def _highlight_nav(self, key):
        for k, btn in self._nav_btns.items():
            btn.configure(bg=C["card"] if k == key else C["surface"], fg=C["accent"] if k == key else C["text"])

    def navigate(self, key):
        if self.nav_history and self.nav_history[-1] == key: return
        self.nav_history.append(key)
        self._render(key)
        self._highlight_nav(key)

    def _render(self, key):
        if self.current_frame: self.current_frame.destroy()
        plt.close("all")
        self._current_fig, self._current_df  = None, None
        self.current_frame = tk.Frame(self.workspace, bg=C["bg"])
        self.current_frame.pack(expand=True, fill="both")
        {
            "Dashboard": self._view_dashboard, "JarTest": self._view_jartest, "Chlorination": self._view_chlorination,
            "TSS": self._view_tss, "IronManganese": self._view_iron_manganese, "Nitrate": self._view_nitrate,
            "LimeSoda": self._view_limesoda, "GramStaining": self._view_gram_staining, 
            "SurfaceHygiene": self._view_surface_hygiene, "WaterQuality": self._view_water_quality,
        }.get(key, self._view_dashboard)()

    def _import_file(self, ce_entry=None, qe_entry=None, x_entry=None, y_entry=None, col_selector=None):
        path = filedialog.askopenfilename(filetypes=[("All Formats", "*.csv *.xlsx *.xls *.txt"), ("CSV", "*.csv"), ("Excel", "*.xlsx *.xls"), ("Text", "*.txt")])
        if not path: return None
        return self._load_path(path, ce_entry, qe_entry, x_entry, y_entry)

    def _load_path(self, path, ce_entry=None, qe_entry=None, x_entry=None, y_entry=None):
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".csv":
                text = open(path, encoding="utf-8", errors="replace").read()
                tables = detect_tables(text)
                if len(tables) > 1: df = self._pick_table(tables)
                else: from io import StringIO; df = pd.read_csv(StringIO(text))
            elif ext in (".xlsx", ".xls"): df = pd.read_excel(path)
            elif ext == ".txt":
                text = open(path, encoding="utf-8", errors="replace").read()
                tables = detect_tables(text)
                df = self._pick_table(tables) if len(tables) > 1 else parse_block_to_df(text)
            else: df = None

            if df is None or df.shape[0] < 2:
                messagebox.showerror("Import Error", "File has fewer than 2 data rows.")
                return None

            self._current_df = df
            self._set_status(f"Loaded: {os.path.basename(path)}  ({len(df)} rows)")
            col0 = df.iloc[:, 0].tolist()
            col1 = df.iloc[:, 1].tolist() if df.shape[1] > 1 else []
            def fill(entry, values):
                if entry: entry.delete(0, tk.END); entry.insert(0, ", ".join(str(v) for v in values))
            fill(ce_entry or x_entry, col0)
            fill(qe_entry or y_entry, col1)
            return df
        except Exception as e: messagebox.showerror("Import Error", str(e)); return None

    def _pick_table(self, tables):
        win = tk.Toplevel(self)
        win.title("Multiple tables detected")
        win.configure(bg=C["surface"])
        win.geometry("500x340")
        win.grab_set()
        tk.Label(win, text=f"{len(tables)} data tables found.", bg=C["surface"], fg=C["text"], font=FONT_HEAD).pack(pady=(16, 4))
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
            tk.Radiobutton(inner, text=f"Table {i+1}: {preview}…", variable=chosen, value=i, bg=C["surface"], fg=C["text"], selectcolor=C["card"], font=FONT_SMALL, anchor="w", wraplength=440).pack(fill="x", pady=2)
        result = [None]
        def confirm(): result[0] = parse_block_to_df(tables[chosen.get()]); win.destroy()
        tk.Button(win, text="Use this table", bg=C["accent"], fg=C["bg"], font=FONT_HEAD, bd=0, padx=16, pady=6, command=confirm).pack(pady=10)
        win.wait_window()
        return result[0]

    def _module_layout(self, title):
        hdr = tk.Frame(self.current_frame, bg=C["bg"])
        hdr.pack(fill="x", pady=(0, 10))
        tk.Label(hdr, text=title, bg=C["bg"], fg=C["text"], font=FONT_TITLE).pack(side="left")

        body = tk.Frame(self.current_frame, bg=C["bg"])
        body.pack(expand=True, fill="both")

        # Softened Groove Borders
        ctrl = tk.Frame(body, bg=C["card"], width=280, padx=14, pady=10, bd=2, relief="ridge")
        ctrl.pack(side="left", fill="y", padx=(0, 15))
        
        disp = tk.Frame(body, bg=C["card"], padx=10, pady=10, bd=2, relief="ridge")
        disp.pack(side="left", expand=True, fill="both")

        return ctrl, disp

    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=C["card"], fg=C["sub"], font=FONT_SMALL, anchor="w").pack(fill="x", pady=(5, 1))

    def _entry(self, parent, default=""):
        e = tk.Entry(parent, bg=C["surface"], fg=C["accent"], bd=1, insertbackground=C["accent"], highlightthickness=1, highlightcolor=C["accent"], highlightbackground=C["muted"], font=FONT_MONO)
        e.pack(fill="x", pady=(0, 2))
        e.insert(0, default)
        return e

    def _btn(self, parent, text, color, command):
        return tk.Button(parent, text=text, bg=color, fg=C["bg"], font=FONT_HEAD, bd=1, pady=6, cursor="hand2", activebackground=C["text"], command=command).pack(fill="x", pady=5)

    def _import_btn(self, parent, **kw):
        tk.Button(parent, text="📂 Import Data", bg=C["surface"], fg=C["text"], font=FONT_UI, bd=1, pady=4, cursor="hand2", command=lambda: self._import_file(**kw)).pack(fill="x", pady=(0, 5))

    def _clear_disp(self, disp):
        for w in disp.winfo_children(): w.destroy()

    def _export_panel(self, parent):
        tk.Frame(parent, bg=C["surface"], height=2).pack(fill="x", pady=8)
        tk.Label(parent, text="Export Results", bg=C["card"], fg=C["text"], font=FONT_SMALL).pack(anchor="w")
        row = tk.Frame(parent, bg=C["card"])
        row.pack(fill="x", pady=2)
        for label, cmd in [("PNG", self._export_png), ("PDF", self._export_pdf), ("CSV", self._export_csv)]:
            tk.Button(row, text=label, bg=C["surface"], fg=C["accent"], font=FONT_SMALL, bd=1, padx=6, pady=2, cursor="hand2", command=cmd).pack(side="left", expand=True, fill="x", padx=1)

    def _export_png(self):
        if not self._current_fig: return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if path: self._current_fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=self._current_fig.get_facecolor()); self._set_status(f"Saved PNG → {path}")

    def _export_pdf(self):
        if not self._current_fig: return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if path:
            with PdfPages(path) as pdf: pdf.savefig(self._current_fig, bbox_inches="tight", facecolor=self._current_fig.get_facecolor())
            self._set_status(f"Saved PDF → {path}")

    def _export_csv(self):
        if self._current_df is None: return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path: self._current_df.to_csv(path, index=False); self._set_status(f"Saved CSV → {path}")

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
        tk.Label(self.current_frame, text="Laboratory Dashboard", bg=C["bg"], fg=C["text"], font=FONT_TITLE).pack(anchor="w", pady=(0, 4))
        tk.Label(self.current_frame, text="M1 Environmental Engineering  ·  Université de Bouira", bg=C["bg"], fg=C["sub"], font=FONT_SMALL).pack(anchor="w", pady=(0, 14))

        canvas = tk.Canvas(self.current_frame, bg=C["bg"], bd=0, highlightthickness=0)
        sb = ttk.Scrollbar(self.current_frame, orient="vertical", command=canvas.yview)
        gf = tk.Frame(canvas, bg=C["bg"])
        gf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=gf, anchor="nw", width=920)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        modules = [
            ("01", "Coagulation & Jar Test", "Turbidity removal curve", C["accent"], "JarTest"),
            ("02", "Breakpoint Chlorination", "Chlorine demand curve", C["amber"], "Chlorination"),
            ("03", "Suspended Solids (TSS)", "Gravimetric MES determination", C["green"], "TSS"),
            ("04", "Iron & Manganese Removal", "Oxidation groundwater workflow", C["purple"], "IronManganese"),
            ("05", "Nitrate Adsorption Kinetics", "Langmuir, Freundlich, & Temkin models", C["accent"], "Nitrate"),
            ("06", "Lime-Soda Softening", "TH / TAC hardness reduction", C["green"], "LimeSoda"),
            ("07", "Gram Staining", "Identification morphology", C["amber"], "GramStaining"),
            ("08", "Surface Hygiene", "Swab colony contamination index", C["purple"], "SurfaceHygiene"),
            ("09", "Water Quality · Coliforms", "MPN potability assessment", C["red"], "WaterQuality"),
        ]

        for num, name, desc, accent, route in modules:
            card = tk.Frame(gf, bg=C["card"], padx=16, pady=12, bd=2, relief="groove")
            card.pack(fill="x", pady=4)
            left = tk.Frame(card, bg=C["card"])
            left.pack(side="left", fill="both", expand=True)
            tk.Label(left, text=f"  {num}  ", bg=accent, fg=C["bg"], font=("Consolas", 10, "bold")).pack(side="left", anchor="n", pady=2, padx=(0, 10))
            info = tk.Frame(left, bg=C["card"])
            info.pack(side="left", fill="both")
            tk.Label(info, text=name, bg=C["card"], fg=C["text"], font=FONT_HEAD, anchor="w").pack(anchor="w")
            tk.Label(info, text=desc, bg=C["card"], fg=C["sub"], font=FONT_SMALL, anchor="w").pack(anchor="w")
            tk.Button(card, text="Open Module", bg=C["surface"], fg=accent, font=FONT_SMALL, bd=1, padx=10, pady=4, cursor="hand2", command=lambda r=route: self.navigate(r)).pack(side="right")

    # ══════════════════════════════════════════════════════════════════════════
    #  LABS 01-03 (UNCHANGED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_jartest(self):
        ctrl, disp = self._module_layout("01 · Coagulation & Flocculation — Jar Test")
        self._import_btn(ctrl, x_entry=None, y_entry=None)
        self._label(ctrl, "Coagulant dose (mg/L)")
        ex = self._entry(ctrl, "10, 20, 30, 40, 50, 60")
        self._label(ctrl, "Residual turbidity (NTU)")
        ey = self._entry(ctrl, "14.2, 8.5, 1.8, 4.3, 9.1, 15.4")
        ctrl.winfo_children()[0].configure(command=lambda: self._import_file(x_entry=ex, y_entry=ey))
        coag_var = tk.StringVar(value="FeCl₃")
        ttk.Combobox(ctrl, textvariable=coag_var, values=["FeCl₃", "Al₂(SO₄)₃", "PAC", "Other"], state="readonly").pack(fill="x", pady=(0, 5))
        self._btn(ctrl, "▶  Run Analysis", C["green"], lambda: self._run_jartest(ex, ey, coag_var, disp))
        self._export_panel(ctrl)

    def _run_jartest(self, ex, ey, coag_var, disp):
        try:
            x, y = [float(v.strip()) for v in ex.get().split(",")], [float(v.strip()) for v in ey.get().split(",")]
        except Exception: return
        df = pd.DataFrame({"Dose": x, "Turbidity": y})
        self._current_df, opt = df, df.loc[df["Turbidity"].idxmin()]
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        mm_axes(ax, xlabel=f"{coag_var.get()} dose (mg/L)", ylabel="Residual turbidity (NTU)", title="Turbidity Removal")
        ax.plot(x, y, color=C["accent"], linewidth=2.5, marker="o", markersize=6, label="Turbidity")
        annotate_point(ax, opt["Dose"], opt["Turbidity"], f"Optimal\n{opt['Dose']} mg/L", C["green"])
        ax.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=8)
        plt.tight_layout(); self._embed_fig(fig, disp)
        self._set_status(f"Optimal dose: {opt['Dose']} mg/L")

    def _view_chlorination(self):
        ctrl, disp = self._module_layout("02 · Breakpoint Chlorination")
        ex = self._entry(ctrl, "0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0")
        ey = self._entry(ctrl, "0.4, 0.8, 1.1, 0.6, 0.2, 0.5, 1.0, 1.5")
        self._btn(ctrl, "▶ Plot Breakpoint", C["amber"], lambda: self._run_chlorination(ex, ey, disp))
        self._export_panel(ctrl)

    def _run_chlorination(self, ex, ey, disp):
        x, y = [float(v.strip()) for v in ex.get().split(",")], [float(v.strip()) for v in ey.get().split(",")]
        self._current_df = pd.DataFrame({"Dose": x, "Residual": y})
        bp_idx = y.index(min(y[1:-1]))
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        mm_axes(ax, xlabel="Chlorine dose (mg/L)", ylabel="Total residual Cl (mg/L)", title="Breakpoint Curve")
        ax.plot(x, y, color=C["amber"], linewidth=2.5, marker="s", markersize=6)
        annotate_point(ax, x[bp_idx], y[bp_idx], f"Breakpoint\n{x[bp_idx]} mg/L", C["red"])
        plt.tight_layout(); self._embed_fig(fig, disp)

    def _view_tss(self):
        ctrl, disp = self._module_layout("03 · Total Suspended Solids (MES)")
        ev, em1, em2, erep = self._entry(ctrl, "100"), self._entry(ctrl, "1.2435"), self._entry(ctrl, "1.2488"), self._entry(ctrl, "3")
        self._btn(ctrl, "▶ Calculate TSS", C["green"], lambda: self._run_tss(ev, em1, em2, erep, disp))
        self._export_panel(ctrl)

    def _run_tss(self, ev, em1, em2, erep, disp):
        V, m1, m2 = float(ev.get()), float(em1.get()), float(em2.get())
        tss = ((m2 - m1) * 1e6) / V
        self._current_df = pd.DataFrame({"Param": ["V", "m1", "m2", "TSS"], "Val": [V, m1, m2, tss]})
        self._clear_disp(disp)
        tk.Label(disp, text=f"{tss:.2f} mg/L", bg=C["card"], fg=C["accent"], font=("Consolas", 28, "bold")).pack(pady=40)

    # ══════════════════════════════════════════════════════════════════════════
    #  04 · IRON & MANGANESE REMOVAL
    # ══════════════════════════════════════════════════════════════════════════
    def _view_iron_manganese(self):
        ctrl, disp = self._module_layout("04 · Iron & Manganese Removal")
        self._label(ctrl, "Initial Fe²⁺ (mg/L)"); eC0  = self._entry(ctrl, "2.50")
        self._label(ctrl, "Final Fe (mg/L)"); eCf  = self._entry(ctrl, "0.12")
        self._label(ctrl, "Initial Mn²⁺ (mg/L)"); eMn0 = self._entry(ctrl, "0.45")
        self._label(ctrl, "Final Mn (mg/L)"); eMnf = self._entry(ctrl, "0.03")
        stages_var = tk.StringVar(value="Aeration + Filtration")
        ttk.Combobox(ctrl, textvariable=stages_var, values=["Aeration only", "Aeration + Filtration", "Aeration + Chlorination + Filtration", "KMnO₄ Oxidation + Filtration"], state="readonly").pack(fill="x", pady=(5, 5))

        self._btn(ctrl, "▶  Evaluate Potability", C["purple"], lambda: self._run_iron_mn(eC0, eCf, eMn0, eMnf, stages_var, disp))
        self._export_panel(ctrl)

    def _run_iron_mn(self, eC0, eCf, eMn0, eMnf, stages_var, disp):
        try: C0, Cf, M0, Mf = float(eC0.get()), float(eCf.get()), float(eMn0.get()), float(eMnf.get())
        except Exception: return
        fe_eff, mn_eff = (C0 - Cf)/C0 * 100, (M0 - Mf)/M0 * 100
        fe_ok, mn_ok = Cf <= 0.2, Mf <= 0.05
        is_potable = fe_ok and mn_ok

        self._current_df = pd.DataFrame({"Parameter": ["Fe₀", "Fe_f", "Mn₀", "Mn_f"], "Value": [C0, Cf, M0, Mf]})

        self._clear_disp(disp)
        
        # Giant Potability Banner
        banner_color = C["green"] if is_potable else C["red"]
        banner_text = "OVERALL STATUS: POTABLE (WHO COMPLIANT)" if is_potable else "OVERALL STATUS: NON-POTABLE (EXCEEDS LIMITS)"
        banner = tk.Frame(disp, bg=banner_color, pady=10)
        banner.pack(fill="x", side="top", pady=(0, 10))
        tk.Label(banner, text=banner_text, bg=banner_color, fg=C["bg"], font=("Arial", 14, "bold")).pack()

        # Graphs
        graph_frame = tk.Frame(disp, bg=C["card"])
        graph_frame.pack(expand=True, fill="both")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 4), facecolor=C["card"])
        for ax, name, before, after, limit, unit in [(ax1, "Iron (Fe)", C0, Cf, 0.2, "mg/L"), (ax2, "Manganese (Mn)", M0, Mf, 0.05, "mg/L")]:
            mm_axes(ax, xlabel="Stage", ylabel=f"{name} ({unit})", title=f"{name} Removal")
            ax.bar(["Before", "After"], [before, after], color=[C["red"], C["green"]], width=0.5, zorder=3)
            ax.axhline(limit, color=C["amber"], linestyle="--", linewidth=1.5, label=f"Limit: {limit}")
            ax.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=8)
            for xi, val in enumerate([before, after]): ax.text(xi, val + 0.02, f"{val}", ha="center", color=C["text"], fontsize=9, fontweight="bold")

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    # ══════════════════════════════════════════════════════════════════════════
    #  05 · NITRATE ADSORPTION — ADDED TEMKIN & BEST FIT VERIFIER
    # ══════════════════════════════════════════════════════════════════════════
    def _view_nitrate(self):
        ctrl, disp = self._module_layout("05 · Nitrate Adsorption Kinetics")

        # Create a scrollable canvas for controls so it NEVER clips the run button
        canvas = tk.Canvas(ctrl, bg=C["card"], highlightthickness=0)
        sb = ttk.Scrollbar(ctrl, orient="vertical", command=canvas.yview)
        inner_ctrl = tk.Frame(canvas, bg=C["card"])
        inner_ctrl.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner_ctrl, anchor="nw", width=250)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._import_btn(inner_ctrl)
        self._label(inner_ctrl, "Ce — equilibrium conc (mg/L)")
        ece = self._entry(inner_ctrl, "0.82, 1.54, 2.91, 4.63, 6.78, 9.12, 12.35, 16.20, 20.87")
        self._label(inner_ctrl, "qe — adsorbed capacity (mg/g)")
        eql = self._entry(inner_ctrl, "0.13, 0.23, 0.40, 0.57, 0.74, 0.89, 1.04, 1.19, 1.31")

        inner_ctrl.winfo_children()[0].configure(command=lambda: self._import_nitrate(ece, eql))

        # The Run button will now always be accessible!
        self._btn(inner_ctrl, "▶ Run Verification", C["accent"], lambda: self._run_nitrate(ece, eql, disp))
        self._export_panel(inner_ctrl)

    def _import_nitrate(self, ece, eql):
        df = self._import_file()
        if df is not None:
            ece.delete(0, tk.END); ece.insert(0, ", ".join(str(v) for v in df.iloc[:,0]))
            eql.delete(0, tk.END); eql.insert(0, ", ".join(str(v) for v in df.iloc[:,1]))

    def _run_nitrate(self, ece, eql, disp):
        try:
            Ce  = np.array([float(v.strip()) for v in ece.get().split(",")])
            qe  = np.array([float(v.strip()) for v in eql.get().split(",")])
        except Exception: return

        # 1. Langmuir
        y_L = Ce / qe
        sl_L, ic_L = np.polyfit(Ce, y_L, 1)
        qmax, b = 1/sl_L, 1/(ic_L * (1/sl_L))
        R2_L = 1 - np.sum((y_L - (sl_L*Ce+ic_L))**2) / np.sum((y_L - y_L.mean())**2)

        # 2. Freundlich
        lce, lqe = np.log(Ce), np.log(qe)
        sl_F, ic_F = np.polyfit(lce, lqe, 1)
        Kf, n = np.exp(ic_F), 1/sl_F
        R2_F = 1 - np.sum((lqe - (sl_F*lce+ic_F))**2) / np.sum((lqe - lqe.mean())**2)

        # 3. Temkin
        sl_T, ic_T = np.polyfit(lce, qe, 1)
        B_tem = sl_T
        AT = np.exp(ic_T / B_tem) if B_tem != 0 else 0
        R2_T = 1 - np.sum((qe - (sl_T*lce+ic_T))**2) / np.sum((qe - qe.mean())**2)

        # Auto-Verify Best Fit
        fits = {"Langmuir": R2_L, "Freundlich": R2_F, "Temkin": R2_T}
        best_model = max(fits, key=fits.get)

        self._clear_disp(disp)

        # Highlight Best Model
        banner = tk.Frame(disp, bg=C["surface"], bd=1, relief="ridge", pady=5)
        banner.pack(fill="x", pady=(0, 10))
        tk.Label(banner, text=f"VERIFIED BEST FIT MODEL: {best_model.upper()} (R² = {fits[best_model]:.4f})", 
                 bg=C["surface"], fg=C["accent"], font=("Arial", 12, "bold")).pack()

        # Render Graphs
        fig, axes = plt.subplots(1, 3, figsize=(10, 3.5), facecolor=C["card"])
        
        # Langmuir Plot
        mm_axes(axes[0], xlabel="Ce", ylabel="Ce / qe", title=f"Langmuir (R²={R2_L:.3f})")
        axes[0].scatter(Ce, y_L, color=C["accent"], s=30, zorder=4)
        ce_l = np.linspace(Ce.min(), Ce.max(), 100)
        axes[0].plot(ce_l, sl_L*ce_l + ic_L, color=C["green"], linestyle="--")

        # Freundlich Plot
        mm_axes(axes[1], xlabel="ln(Ce)", ylabel="ln(qe)", title=f"Freundlich (R²={R2_F:.3f})")
        axes[1].scatter(lce, lqe, color=C["amber"], s=30, zorder=4)
        lce_l = np.linspace(lce.min(), lce.max(), 100)
        axes[1].plot(lce_l, sl_F*lce_l + ic_F, color=C["red"], linestyle="--")

        # Temkin Plot
        mm_axes(axes[2], xlabel="ln(Ce)", ylabel="qe", title=f"Temkin (R²={R2_T:.3f})")
        axes[2].scatter(lce, qe, color=C["purple"], s=30, zorder=4)
        axes[2].plot(lce_l, sl_T*lce_l + ic_T, color=C["border"], linestyle="--")

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=disp)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

        # Stats Printout
        stats = tk.Frame(disp, bg=C["card"])
        stats.pack(fill="x", pady=5)
        tk.Label(stats, text=f"Langmuir: qm={qmax:.2f}, K_L={b:.3f}", bg=C["card"], fg=C["text"]).pack(side="left", expand=True)
        tk.Label(stats, text=f"Freundlich: Kf={Kf:.2f}, n={n:.2f}", bg=C["card"], fg=C["text"]).pack(side="left", expand=True)
        tk.Label(stats, text=f"Temkin: B={B_tem:.2f}, A_T={AT:.2f}", bg=C["card"], fg=C["text"]).pack(side="left", expand=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  06 · LIME-SODA SOFTENING (UNCHANGED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_limesoda(self):
        ctrl, disp = self._module_layout("06 · Lime-Soda Chemical Softening")
        self._label(ctrl, "Total hardness TH₀"); eth0  = self._entry(ctrl, "320")
        self._label(ctrl, "Carbonate hardness TH_carb"); ethc  = self._entry(ctrl, "180")
        self._label(ctrl, "Total alkalinity TAC"); etac  = self._entry(ctrl, "200")
        self._label(ctrl, "Target residual hardness"); etgt  = self._entry(ctrl, "50")
        self._label(ctrl, "Flow rate Q (m³/h)"); eq    = self._entry(ctrl, "10")
        self._btn(ctrl, "▶ Calculate Reagent", C["green"], lambda: self._run_limesoda(eth0, ethc, etac, etgt, eq, disp))
        self._export_panel(ctrl)

    def _run_limesoda(self, eth0, ethc, etac, etgt, eq, disp):
        TH0, THc, TAC, TH_t, Q = float(eth0.get()), float(ethc.get()), float(etac.get()), float(etgt.get()), float(eq.get())
        TH_nc, lime_dose, soda_dose = max(TH0 - THc, 0), TAC * 0.74, max(TH0 - THc, 0) * 1.06
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        mm_axes(ax, xlabel="Reagent", ylabel="Dose (mg/L)", title="Requirements")
        ax.bar(["Ca(OH)₂", "Na₂CO₃"], [lime_dose, soda_dose], color=[C["accent"], C["green"]], zorder=3)
        plt.tight_layout(); self._embed_fig(fig, disp)

    # ══════════════════════════════════════════════════════════════════════════
    #  07 · GRAM STAINING (Fixed Bacillus Logic)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_gram_staining(self):
        ctrl, disp = self._module_layout("07 · Gram Staining — Bacterial Identification")
        self._label(ctrl, "Sample / isolate ID"); eid = self._entry(ctrl, "Sample_01")
        self._label(ctrl, "Gram reaction"); gram_var = tk.StringVar(value="Gram-positive (+)")
        ttk.Combobox(ctrl, textvariable=gram_var, values=["Gram-positive (+)", "Gram-negative (−)"], state="readonly").pack(fill="x", pady=(0, 5))
        self._label(ctrl, "Cell morphology"); morph_var = tk.StringVar(value="Bacillus (rod)")
        ttk.Combobox(ctrl, textvariable=morph_var, values=["Coccus", "Bacillus (rod)", "Spirillum"], state="readonly").pack(fill="x", pady=(0, 5))
        self._btn(ctrl, "▶  Generate ID Summary", C["amber"], lambda: self._run_gram(eid, gram_var, morph_var, disp))

    def _run_gram(self, eid, gram_var, morph_var, disp):
        sid, gram, morph = eid.get(), gram_var.get(), morph_var.get()
        gp = "+" in gram
        
        # Fixed Genus Hint Logic matching explicit words
        genus_hint = "Unknown"
        if gp and "Coccus" in morph: genus_hint = "Staphylococcus / Streptococcus / Micrococcus"
        elif gp and "Bacillus" in morph: genus_hint = "Bacillus / Lactobacillus / Clostridium"
        elif not gp and "Bacillus" in morph: genus_hint = "E. coli / Pseudomonas / Salmonella"
        elif not gp and "Coccus" in morph: genus_hint = "Neisseria / Moraxella"

        self._clear_disp(disp)
        card = tk.Frame(disp, bg=C["surface"], bd=2, relief="groove")
        card.pack(expand=True, fill="both", padx=30, pady=30)
        color = C["purple"] if gp else C["red"]
        tk.Label(card, text=f"Sample: {sid}", bg=C["surface"], fg=C["text"], font=("Segoe UI", 16, "bold")).pack(pady=10)
        tk.Label(card, text=gram, bg=C["surface"], fg=color, font=("Consolas", 22, "bold")).pack()
        tk.Label(card, text=f"Morphology: {morph}", bg=C["surface"], fg=C["text"], font=FONT_HEAD).pack(pady=5)
        tk.Label(card, text=f"→ Possible Genus: {genus_hint}", bg=C["surface"], fg=C["accent"], font=("Segoe UI", 12, "bold")).pack(pady=20)

    # ══════════════════════════════════════════════════════════════════════════
    #  08 · SURFACE HYGIENE (UNCHANGED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_surface_hygiene(self):
        ctrl, disp = self._module_layout("08 · Surface Hygiene")
        self._label(ctrl, "Surfaces"); elbl = self._entry(ctrl, "Bench, Tap, Floor")
        self._label(ctrl, "CFU/cm²"); ecfu = self._entry(ctrl, "12, 6, 120")
        self._btn(ctrl, "▶ Analyse", C["purple"], lambda: self._run_hygiene(elbl, ecfu, disp))

    def _run_hygiene(self, elbl, ecfu, disp):
        lbls, cfus = [v.strip() for v in elbl.get().split(",")], [float(v.strip()) for v in ecfu.get().split(",")]
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        mm_axes(ax, title="Hygiene"); ax.bar(lbls, cfus, color=C["purple"], zorder=3)
        plt.tight_layout(); self._embed_fig(fig, disp)

    # ══════════════════════════════════════════════════════════════════════════
    #  09 · WATER QUALITY — EXPLICIT POTABILITY ADDED
    # ══════════════════════════════════════════════════════════════════════════
    def _view_water_quality(self):
        ctrl, disp = self._module_layout("09 · Biological Water Quality")
        self._label(ctrl, "Sample IDs"); eid  = self._entry(ctrl, "S1, S2, S3")
        self._label(ctrl, "Total coliforms"); etc  = self._entry(ctrl, "0, 12, 0")
        self._label(ctrl, "E. coli"); efc  = self._entry(ctrl, "0, 0, 0")
        self._btn(ctrl, "▶  Assess Potability", C["red"], lambda: self._run_water_quality(eid, etc, efc, disp))
        self._export_panel(ctrl)

    def _run_water_quality(self, eid, etc, efc, disp):
        try: ids, tc, fc = [v.strip() for v in eid.get().split(",")], [float(v.strip()) for v in etc.get().split(",")], [float(v.strip()) for v in efc.get().split(",")]
        except Exception: return

        df = pd.DataFrame({"Sample": ids, "TC": tc, "FC": fc})
        df["Potable"] = (df["TC"] == 0) & (df["FC"] == 0)
        overall_potable = df["Potable"].all()

        self._clear_disp(disp)

        # Giant Potability Banner
        banner_color = C["green"] if overall_potable else C["red"]
        banner_text = "ALL SAMPLES ARE POTABLE" if overall_potable else "WARNING: NON-POTABLE SAMPLES DETECTED"
        banner = tk.Frame(disp, bg=banner_color, pady=10)
        banner.pack(fill="x", side="top", pady=(0, 10))
        tk.Label(banner, text=banner_text, bg=banner_color, fg=C["bg"], font=("Arial", 14, "bold")).pack()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 5), facecolor=C["card"])
        mm_axes(ax1, ylabel="TC / 100 mL", title="Total Coliforms")
        ax1.bar(ids, tc, color=[C["green"] if v == 0 else C["red"] for v in tc], zorder=3)
        mm_axes(ax2, ylabel="FC / 100 mL", title="E. Coli")
        ax2.bar(ids, fc, color=[C["green"] if v == 0 else C["red"] for v in fc], zorder=3)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=disp)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

if __name__ == "__main__":
    app = AquaLabs()
    app.mainloop()
