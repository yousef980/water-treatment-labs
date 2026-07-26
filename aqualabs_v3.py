"""
AQUALABS v3.0 — Advanced Water Treatment Processing Suite
Environmental Engineering Laboratory Tool
Developed by: Youcef Youcef

Version 3.0:
- CustomTkinter UI Overhaul (Midnight Ocean theme)
- Comprehensive Domain Enhancements for all 9 modules
"""

import os
import re
import sys
import numpy as np
import pandas as pd
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox

# ── MIDNIGHT OCEAN PALETTE ─────────────────────────────────────────────────
C = {
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

# Configure CustomTkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def mm_axes(ax, xlabel="", ylabel="", title="", facecolor=None):
    fc = facecolor or C["card"]
    ax.set_facecolor(C["bg"])
    ax.figure.set_facecolor(fc)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.grid(which="major", color=C["surface"], linewidth=0.8, linestyle="-")
    ax.grid(which="minor", color=C["bg"], linewidth=0.4, linestyle="-")
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

# ═══════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════
class AquaLabs(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AQUALABS v3.0 — Water Treatment Suite")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        self.configure(fg_color=C["bg"])

        self._current_fig = None
        self._current_df = None
        self.current_frame = None
        self.nav_history = []

        self._build_layout()
        self.navigate("Dashboard")

    def _build_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=C["surface"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.sidebar, text="AQUALABS", font=("Consolas", 24, "bold"), text_color=C["text"]).grid(row=0, column=0, padx=20, pady=(30, 2), sticky="w")
        ctk.CTkLabel(self.sidebar, text="Water Treatment Suite", font=("Segoe UI", 12), text_color=C["accent"]).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

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
        row_idx = 2
        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w", fg_color="transparent",
                text_color=C["text"], font=("Segoe UI", 14), hover_color=C["card"],
                corner_radius=6, command=lambda k=key: self.navigate(k)
            )
            btn.grid(row=row_idx, column=0, padx=15, pady=5, sticky="ew")
            self._nav_btns[key] = btn
            row_idx += 1

        # Main Workspace
        self.main_container = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        
        self.workspace = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.workspace.pack(expand=True, fill="both", padx=30, pady=30)

        # Bottom Bar
        bottom_bar = ctk.CTkFrame(self.main_container, height=40, fg_color=C["surface"], corner_radius=0)
        bottom_bar.pack(fill="x", side="bottom")
        
        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(bottom_bar, textvariable=self.status_var, text_color=C["green"], font=("Segoe UI", 12)).pack(side="left", padx=20)
        ctk.CTkLabel(bottom_bar, text="Developed by: Youcef Youcef | M1 Environmental Engineering", text_color=C["accent"], font=("Segoe UI", 12, "bold")).pack(side="right", padx=20)

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    def _highlight_nav(self, key):
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(fg_color=C["card"], text_color=C["accent"])
            else:
                btn.configure(fg_color="transparent", text_color=C["text"])

    def navigate(self, key):
        if self.nav_history and self.nav_history[-1] == key: return
        self.nav_history.append(key)
        self._highlight_nav(key)
        self._render(key)

    def _render(self, key):
        if self.current_frame: self.current_frame.destroy()
        plt.close("all")
        self._current_fig, self._current_df = None, None
        
        self.current_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.current_frame.pack(expand=True, fill="both")
        
        route_map = {
            "Dashboard": self._view_dashboard,
            "JarTest": self._view_jartest,
            "Chlorination": self._view_chlorination,
            "TSS": self._view_tss,
            "IronManganese": self._view_iron_manganese,
            "Nitrate": self._view_nitrate,
            "LimeSoda": self._view_limesoda,
            "GramStaining": self._view_gram_staining,
            "SurfaceHygiene": self._view_surface_hygiene,
            "WaterQuality": self._view_water_quality,
        }
        
        func = route_map.get(key)
        if func:
            func()
        else:
            ctk.CTkLabel(self.current_frame, text=f"Module '{key}' is under construction.", font=("Segoe UI", 24)).pack(pady=100)

    def _module_layout(self, title):
        hdr = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(hdr, text=title, font=("Segoe UI", 24, "bold"), text_color=C["text"]).pack(side="left")

        body = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        body.pack(expand=True, fill="both")

        ctrl = ctk.CTkFrame(body, fg_color=C["card"], width=320, corner_radius=20)
        ctrl.pack(side="left", fill="y", padx=(0, 20))
        
        disp = ctk.CTkFrame(body, fg_color=C["card"], corner_radius=20)
        disp.pack(side="left", expand=True, fill="both")

        # Make ctrl scrollable if needed
        ctrl_scroll = ctk.CTkScrollableFrame(ctrl, fg_color="transparent", width=300)
        ctrl_scroll.pack(expand=True, fill="both", padx=10, pady=10)

        return ctrl_scroll, disp

    def _label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Segoe UI", 12), text_color=C["sub"]).pack(anchor="w", pady=(10, 2))

    def _entry(self, parent, default=""):
        e = ctk.CTkEntry(parent, font=("Consolas", 12), fg_color=C["surface"], border_color=C["muted"], text_color=C["text"])
        e.pack(fill="x", pady=(0, 5))
        e.insert(0, default)
        return e

    def _btn(self, parent, text, color, command):
        ctk.CTkButton(parent, text=text, fg_color=color, text_color=C["bg"], font=("Segoe UI", 14, "bold"), hover_color=C["text"], command=command).pack(fill="x", pady=15)

    def _clear_disp(self, disp):
        for w in disp.winfo_children(): w.destroy()

    def _embed_fig(self, fig, disp):
        self._clear_disp(disp)
        self._current_fig = fig
        canvas = FigureCanvasTkAgg(fig, master=disp)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

    # ══════════════════════════════════════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════
    def _view_dashboard(self):
        ctk.CTkLabel(self.current_frame, text="Laboratory Dashboard", font=("Segoe UI", 28, "bold"), text_color=C["text"]).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.current_frame, text="M1 Environmental Engineering · Université de Bouira", font=("Segoe UI", 14), text_color=C["sub"]).pack(anchor="w", pady=(0, 20))

        scroll_frame = ctk.CTkScrollableFrame(self.current_frame, fg_color="transparent")
        scroll_frame.pack(expand=True, fill="both")

        modules = [
            ("01", "Coagulation & Jar Test", "Calculate G-value, RPM, pH adj, & Turbidity removal", C["accent"], "JarTest"),
            ("02", "Breakpoint Chlorination", "Free/Combined Chlorine, CT value, Demand curve", C["amber"], "Chlorination"),
            ("03", "Suspended Solids (TSS)", "TSS & VSS (Volatile) gravimetric determination", C["green"], "TSS"),
            ("04", "Iron & Manganese Removal", "Oxidant dosing (Cl2, KMnO4, O3), pH/ORP workflow", C["purple"], "IronManganese"),
            ("05", "Nitrate Adsorption Kinetics", "Isotherms (Langmuir, Freundlich) & Kinetic models", C["accent"], "Nitrate"),
            ("06", "Lime-Soda Softening", "Pure CaO/Ca(OH)2 scaling & Mg2+ hardness reduction", C["green"], "LimeSoda"),
            ("07", "Gram Staining", "Advanced shape/spore identification flowchart", C["amber"], "GramStaining"),
            ("08", "Surface Hygiene", "ISO compliant swab colony contamination index", C["purple"], "SurfaceHygiene"),
            ("09", "Biological Water Quality", "MPN, Fecal Coliforms & Streptococci potability", C["red"], "WaterQuality"),
        ]

        for i, (num, name, desc, accent, route) in enumerate(modules):
            card = ctk.CTkFrame(scroll_frame, fg_color=C["card"], corner_radius=20, border_width=0)
            card.pack(fill="x", pady=8)
            
            ctk.CTkLabel(card, text=f" {num} ", font=("Consolas", 16, "bold"), fg_color=accent, text_color=C["bg"], corner_radius=8).pack(side="left", padx=20, pady=20)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", padx=10, pady=15)
            ctk.CTkLabel(info, text=name, font=("Segoe UI", 16, "bold"), text_color=C["text"]).pack(anchor="w")
            ctk.CTkLabel(info, text=desc, font=("Segoe UI", 12), text_color=C["sub"]).pack(anchor="w")
            
            ctk.CTkButton(card, text="Open Module", fg_color=C["bg"], text_color=accent, corner_radius=8, hover_color=C["surface"], command=lambda r=route: self.navigate(r)).pack(side="right", padx=20)

    # ══════════════════════════════════════════════════════════════════════════
    #  01 · COAGULATION & JAR TEST (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_jartest(self):
        ctrl, disp = self._module_layout("01 · Coagulation & Flocculation — Jar Test")
        
        self._label(ctrl, "Sample Initial pH & Alkalinity (mg/L)")
        eph_alk = self._entry(ctrl, "7.2, 120")
        
        self._label(ctrl, "Coagulation / Rapid Mix (RPM, Time in sec)")
        ecoag = self._entry(ctrl, "150, 45")
        
        self._label(ctrl, "Flocculation / Slow Mix (RPM, Time in min)")
        efloc = self._entry(ctrl, "30, 20")
        
        self._label(ctrl, "Coagulant dose (mg/L)")
        ex = self._entry(ctrl, "10, 20, 30, 40, 50, 60")
        
        self._label(ctrl, "Residual turbidity (NTU)")
        ey = self._entry(ctrl, "14.2, 8.5, 1.8, 4.3, 9.1, 15.4")
        
        self._label(ctrl, "Coagulant Type")
        coag_var = ctk.CTkOptionMenu(ctrl, values=[
            "Aluminum Sulfate (Alum)", "Ferric Chloride (FeCl3)", 
            "Ferric Sulfate", "Ferrous Sulfate", 
            "Polyaluminum Chloride (PAC)", "Sodium Aluminate"
        ], fg_color=C["surface"], button_color=C["accent"], button_hover_color=C["text"])
        coag_var.pack(fill="x", pady=(0, 10))

        self._btn(ctrl, "▶ Run Advanced Analysis", C["green"], lambda: self._run_jartest(eph_alk, ecoag, efloc, ex, ey, coag_var, disp))

    def _run_jartest(self, eph_alk, ecoag, efloc, ex, ey, coag_var, disp):
        try:
            ph_alk_str = eph_alk.get().split(",")
            pH = float(ph_alk_str[0].strip())
            Alk = float(ph_alk_str[1].strip())
            
            coag_str = ecoag.get().split(",")
            coag_rpm = float(coag_str[0].strip())
            coag_sec = float(coag_str[1].strip())
            
            floc_str = efloc.get().split(",")
            floc_rpm = float(floc_str[0].strip())
            floc_min = float(floc_str[1].strip())
            
            x = [float(v.strip()) for v in ex.get().split(",")]
            y = [float(v.strip()) for v in ey.get().split(",")]
        except Exception: 
            messagebox.showerror("Input Error", "Please ensure all inputs are valid comma-separated numbers.")
            return

        df = pd.DataFrame({"Dose": x, "Turbidity": y})
        self._current_df, opt = df, df.loc[df["Turbidity"].idxmin()]
        opt_dose = opt["Dose"]
        
        coag_type = coag_var.get()
        alk_modifier = 0
        ph_range = (6.0, 8.0)
        
        if "Alum" in coag_type:
            alk_modifier = -0.45; ph_range = (5.5, 7.5)
        elif "FeCl3" in coag_type:
            alk_modifier = -0.92; ph_range = (5.0, 8.5)
        elif "Ferric Sulfate" in coag_type:
            alk_modifier = -0.75; ph_range = (4.0, 11.0)
        elif "Ferrous Sulfate" in coag_type:
            alk_modifier = -0.90; ph_range = (8.5, 11.0)
        elif "PAC" in coag_type:
            alk_modifier = -0.15; ph_range = (6.0, 8.5)
        elif "Sodium Aluminate" in coag_type:
            alk_modifier = 0.80; ph_range = (6.0, 8.5) # Adds alkalinity
            
        rem_alk = Alk + (alk_modifier * opt_dose)
        
        warnings = []
        if not (ph_range[0] <= pH <= ph_range[1]):
            warnings.append(f"⚠️ pH {pH} is outside optimal range ({ph_range[0]}-{ph_range[1]}) for {coag_type}.")
        if rem_alk < 30:
            warnings.append(f"⚠️ Residual alkalinity too low ({rem_alk:.1f} mg/L). Buffering required!")

        # Mixing Energy Estimation (G-value heuristic placeholder for standard stirrer)
        G_coag = coag_rpm * 1.5 
        G_floc = floc_rpm * 1.5
        
        self._clear_disp(disp)
        
        # Stats Banner
        banner = ctk.CTkFrame(disp, fg_color=C["surface"], corner_radius=8)
        banner.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(banner, text=f"Optimal Dose: {opt_dose} mg/L", font=("Segoe UI", 18, "bold"), text_color=C["green"]).pack(pady=(10, 0))
        
        mixing_text = f"Coagulation: {coag_sec} sec @ ~{G_coag:.0f} s⁻¹  |  Flocculation: {floc_min} min @ ~{G_floc:.0f} s⁻¹"
        ctk.CTkLabel(banner, text=mixing_text, text_color=C["text"]).pack()
        
        alk_change = "Added" if alk_modifier > 0 else "Consumed"
        ctk.CTkLabel(banner, text=f"Alk {alk_change}: {abs(alk_modifier * opt_dose):.1f} mg/L | Remaining Alk: {rem_alk:.1f} mg/L", text_color=C["accent"]).pack()
        
        if warnings:
            for w in warnings:
                ctk.CTkLabel(banner, text=w, text_color=C["amber"], font=("Segoe UI", 12, "bold")).pack(pady=(2, 0))
        else:
            ctk.CTkLabel(banner, text="✓ pH and Alkalinity within optimal parameters.", text_color=C["green"]).pack(pady=(2, 0))
        
        # Padding
        ctk.CTkFrame(banner, fg_color="transparent", height=10).pack()

        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        # Format the label nicely so it isn't too long on the axis
        c_short = coag_type.split("(")[0].strip()
        mm_axes(ax, xlabel=f"{c_short} Dose (mg/L)", ylabel="Residual Turbidity (NTU)", title="Turbidity Removal & Optimal Dosing")
        ax.plot(x, y, color=C["accent"], linewidth=2.5, marker="o", markersize=6, label="Turbidity")
        annotate_point(ax, opt["Dose"], opt["Turbidity"], f"Optimal\n{opt_dose} mg/L", C["green"])
        ax.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=8)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=disp)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)
        self._set_status(f"Jar Test Analysis Complete - Optimal {c_short} Dose: {opt_dose} mg/L")

    # ══════════════════════════════════════════════════════════════════════════
    #  02 · BREAKPOINT CHLORINATION (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_chlorination(self):
        ctrl, disp = self._module_layout("02 · Breakpoint Chlorination")
        
        self._label(ctrl, "Contact Time (min)")
        ect = self._entry(ctrl, "30")
        
        self._label(ctrl, "Temperature (°C)")
        etemp = self._entry(ctrl, "20")
        
        self._label(ctrl, "Chlorine Dose (mg/L)")
        ex = self._entry(ctrl, "0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0")
        
        self._label(ctrl, "Total Residual Cl (mg/L)")
        ey = self._entry(ctrl, "0.4, 0.8, 1.1, 0.6, 0.2, 0.5, 1.0, 1.5")
        
        self._btn(ctrl, "▶ Analyze Breakpoint & CT", C["amber"], lambda: self._run_chlorination(ect, etemp, ex, ey, disp))

    def _run_chlorination(self, ect, etemp, ex, ey, disp):
        try:
            CT_min = float(ect.get())
            temp = float(etemp.get())
            x = [float(v.strip()) for v in ex.get().split(",")]
            y = [float(v.strip()) for v in ey.get().split(",")]
        except:
            return
            
        df = pd.DataFrame({"Dose": x, "Residual": y})
        self._current_df = df
        
        # Identify Breakpoint (local minimum after the peak)
        bp_idx = y.index(min(y[1:-1]))
        bp_dose = x[bp_idx]
        bp_res = y[bp_idx]
        
        # Calculate CT value at breakpoint dose
        CT_value = bp_res * CT_min
        
        self._clear_disp(disp)
        
        banner = ctk.CTkFrame(disp, fg_color=C["surface"], corner_radius=8)
        banner.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(banner, text=f"Breakpoint Detected at Dose: {bp_dose} mg/L", font=("Segoe UI", 18, "bold"), text_color=C["amber"]).pack(pady=(10, 0))
        ctk.CTkLabel(banner, text=f"Chlorine Demand at BP: {bp_dose - bp_res:.2f} mg/L", text_color=C["text"]).pack()
        ctk.CTkLabel(banner, text=f"Calculated CT Value: {CT_value:.2f} mg·min/L (at {temp}°C)", text_color=C["accent"]).pack(pady=(0, 10))

        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        mm_axes(ax, xlabel="Chlorine dose (mg/L)", ylabel="Total residual Cl (mg/L)", title="Breakpoint Curve & Chloramine Destruction")
        ax.plot(x, y, color=C["amber"], linewidth=2.5, marker="s", markersize=6)
        
        # Highlight regions
        ax.axvspan(0, x[y.index(max(y[:bp_idx]))], alpha=0.1, color=C["green"], label="Combined Cl Formation")
        ax.axvspan(x[y.index(max(y[:bp_idx]))], bp_dose, alpha=0.1, color=C["red"], label="Chloramine Destruction")
        ax.axvspan(bp_dose, max(x), alpha=0.1, color=C["accent"], label="Free Chlorine Residue")
        
        annotate_point(ax, bp_dose, bp_res, f"Breakpoint\n{bp_dose} mg/L", C["red"])
        ax.legend(facecolor=C["surface"], labelcolor=C["text"], fontsize=8)
        
        plt.tight_layout()
        self._embed_fig(fig, disp)

    # ══════════════════════════════════════════════════════════════════════════
    #  03 · TOTAL SUSPENDED SOLIDS (TSS) & VSS (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_tss(self):
        ctrl, disp = self._module_layout("03 · Total Suspended Solids (TSS) & VSS")
        
        self._label(ctrl, "Volume Filtered (mL)")
        ev = self._entry(ctrl, "100")
        
        self._label(ctrl, "Filter Paper Weight (g) [m0]")
        em0 = self._entry(ctrl, "0.1250")
        
        self._label(ctrl, "Weight after 105°C (g) [m1]")
        em1 = self._entry(ctrl, "0.1374")
        
        self._label(ctrl, "Weight after 550°C (g) [m2] (Optional)")
        em2 = self._entry(ctrl, "0.1292")
        
        self._btn(ctrl, "▶ Calculate TSS & VSS", C["green"], lambda: self._run_tss(ev, em0, em1, em2, disp))

    def _run_tss(self, ev, em0, em1, em2, disp):
        try:
            V = float(ev.get())
            m0 = float(em0.get())
            m1 = float(em1.get())
            m2_str = em2.get().strip()
        except: return

        # TSS = (m1 - m0) / V * 1e6 (mg/L)
        tss = ((m1 - m0) * 1e6) / V
        
        has_vss = False
        vss = 0
        if m2_str:
            try:
                m2 = float(m2_str)
                # VSS = (m1 - m2) / V * 1e6
                vss = ((m1 - m2) * 1e6) / V
                has_vss = True
            except: pass

        self._clear_disp(disp)
        
        banner = ctk.CTkFrame(disp, fg_color=C["surface"], corner_radius=8)
        banner.pack(fill="x", padx=30, pady=30)
        
        ctk.CTkLabel(banner, text="Gravimetric Analysis Results", font=("Segoe UI", 20, "bold"), text_color=C["text"]).pack(pady=(20, 10))
        ctk.CTkLabel(banner, text=f"Total Suspended Solids (TSS): {tss:.2f} mg/L", font=("Consolas", 24, "bold"), text_color=C["accent"]).pack(pady=5)
        
        if has_vss:
            fss = tss - vss
            ctk.CTkLabel(banner, text=f"Volatile Suspended Solids (VSS): {vss:.2f} mg/L ({vss/tss*100:.1f}%)", font=("Consolas", 20, "bold"), text_color=C["amber"]).pack(pady=5)
            ctk.CTkLabel(banner, text=f"Fixed Suspended Solids (FSS): {fss:.2f} mg/L ({fss/tss*100:.1f}%)", font=("Consolas", 20, "bold"), text_color=C["sub"]).pack(pady=(5, 20))
            
            fig, ax = plt.subplots(figsize=(5, 3), facecolor=C["card"])
            mm_axes(ax, title="Solids Composition")
            ax.pie([vss, fss], labels=["Volatile (Organic)", "Fixed (Inorganic)"], colors=[C["amber"], C["sub"]], autopct='%1.1f%%', textprops={'color':C["bg"], 'weight':'bold'})
            plt.tight_layout()
            self._embed_fig(fig, disp)
        else:
            ctk.CTkLabel(banner, text="VSS not calculated (no 550°C data provided)", text_color=C["sub"]).pack(pady=(5, 20))


    # ══════════════════════════════════════════════════════════════════════════
    #  04 · IRON & MANGANESE REMOVAL (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_iron_manganese(self):
        ctrl, disp = self._module_layout("04 · Iron & Manganese Removal")
        self._label(ctrl, "Initial Fe²⁺ (mg/L)")
        eC0 = self._entry(ctrl, "2.50")
        self._label(ctrl, "Initial Mn²⁺ (mg/L)")
        eMn0 = self._entry(ctrl, "0.45")
        self._label(ctrl, "Water pH & ORP (mV)")
        eph = self._entry(ctrl, "7.2, 150")
        
        self._label(ctrl, "Oxidant Used")
        ox_var = ctk.CTkOptionMenu(ctrl, values=["Chlorine (Cl2)", "KMnO4", "Ozone (O3)", "Aeration Only (O2)"], fg_color=C["surface"], button_color=C["purple"])
        ox_var.pack(fill="x", pady=(0, 10))

        self._btn(ctrl, "▶ Calculate Oxidant Demand", C["purple"], lambda: self._run_iron_mn(eC0, eMn0, eph, ox_var, disp))

    def _run_iron_mn(self, eC0, eMn0, eph, ox_var, disp):
        try:
            Fe = float(eC0.get())
            Mn = float(eMn0.get())
            ph_orp = eph.get().split(",")
            pH = float(ph_orp[0].strip())
            orp = float(ph_orp[1].strip())
            oxidant = ox_var.get()
        except: return

        # Stoichiometric relations (mg Oxidant per mg Metal)
        # Fe: Cl2 (0.64), KMnO4 (0.94), O3 (0.43), O2 (0.14)
        # Mn: Cl2 (1.30), KMnO4 (1.92), O3 (0.87), O2 (0.29)
        ratios = {
            "Chlorine (Cl2)": (0.64, 1.30),
            "KMnO4": (0.94, 1.92),
            "Ozone (O3)": (0.43, 0.87),
            "Aeration Only (O2)": (0.14, 0.29)
        }
        
        fe_ratio, mn_ratio = ratios[oxidant]
        fe_demand = Fe * fe_ratio
        mn_demand = Mn * mn_ratio
        total_demand = fe_demand + mn_demand
        
        # pH/ORP kinetics warning
        warning = ""
        if oxidant == "Aeration Only (O2)":
            if pH < 7.5: warning += "⚠️ Fe oxidation by O2 is slow below pH 7.5. "
            if pH < 9.5 and Mn > 0: warning += "⚠️ Mn oxidation by O2 requires pH > 9.5! "

        self._clear_disp(disp)
        
        banner = ctk.CTkFrame(disp, fg_color=C["surface"], corner_radius=8)
        banner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(banner, text=f"Oxidant Required: {oxidant}", font=("Segoe UI", 18, "bold"), text_color=C["purple"]).pack(pady=(10, 5))
        ctk.CTkLabel(banner, text=f"Theoretical Fe Demand: {fe_demand:.2f} mg/L", text_color=C["text"]).pack()
        ctk.CTkLabel(banner, text=f"Theoretical Mn Demand: {mn_demand:.2f} mg/L", text_color=C["text"]).pack()
        ctk.CTkLabel(banner, text=f"Total Stoichiometric Demand: {total_demand:.2f} mg/L", font=("Segoe UI", 16, "bold"), text_color=C["accent"]).pack(pady=(5, 10))
        
        if warning:
            ctk.CTkLabel(banner, text=warning, text_color=C["amber"], font=("Segoe UI", 12, "bold"), wraplength=400).pack(pady=(0, 10))

        # Render Bar Chart
        fig, ax = plt.subplots(figsize=(6, 3.5), facecolor=C["card"])
        mm_axes(ax, ylabel="Demand (mg/L)", title="Oxidant Consumption Breakdown")
        ax.bar(["Iron (Fe)", "Manganese (Mn)"], [fe_demand, mn_demand], color=[C["red"], C["purple"]], zorder=3)
        for i, v in enumerate([fe_demand, mn_demand]):
            ax.text(i, v + 0.05, f"{v:.2f}", ha="center", color=C["text"], fontweight="bold")
        plt.tight_layout()
        self._embed_fig(fig, disp)


    # ══════════════════════════════════════════════════════════════════════════
    #  05 · NITRATE ADSORPTION KINETICS (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_nitrate(self):
        ctrl, disp = self._module_layout("05 · Nitrate Adsorption Kinetics")
        
        self._label(ctrl, "Time t (min) [For Kinetics]")
        et = self._entry(ctrl, "10, 20, 30, 45, 60, 90, 120")
        
        self._label(ctrl, "Adsorbed qt (mg/g) [For Kinetics]")
        eqt = self._entry(ctrl, "0.4, 0.65, 0.82, 0.95, 1.05, 1.15, 1.20")
        
        self._btn(ctrl, "▶ Analyze Kinetics", C["accent"], lambda: self._run_nitrate_kinetics(et, eqt, disp))
        
        ctk.CTkFrame(ctrl, height=2, fg_color=C["surface"]).pack(fill="x", pady=10)
        
        self._label(ctrl, "Equilibrium Ce (mg/L) [For Isotherms]")
        ece = self._entry(ctrl, "0.82, 1.54, 2.91, 4.63, 6.78")
        self._label(ctrl, "Equilibrium qe (mg/g) [For Isotherms]")
        eqe = self._entry(ctrl, "0.13, 0.23, 0.40, 0.57, 0.74")
        
        self._btn(ctrl, "▶ Analyze Isotherms", C["green"], lambda: self._run_nitrate_isotherms(ece, eqe, disp))

    def _run_nitrate_kinetics(self, et, eqt, disp):
        try:
            t = np.array([float(v.strip()) for v in et.get().split(",")])
            qt = np.array([float(v.strip()) for v in eqt.get().split(",")])
        except: return
        
        qe_exp = qt.max()
        
        # Pseudo First Order: ln(qe - qt) = ln(qe) - k1 * t
        # (Requires qe - qt > 0)
        valid = qt < qe_exp
        t_valid = t[valid]
        qt_valid = qt[valid]
        
        if len(t_valid) > 2:
            y_pfo = np.log(qe_exp - qt_valid)
            sl_pfo, ic_pfo = np.polyfit(t_valid, y_pfo, 1)
            R2_PFO = 1 - np.sum((y_pfo - (sl_pfo*t_valid+ic_pfo))**2) / np.sum((y_pfo - y_pfo.mean())**2)
            k1 = -sl_pfo
        else:
            R2_PFO, k1 = 0, 0
            
        # Pseudo Second Order: t/qt = 1/(k2 * qe^2) + t/qe
        y_pso = t / qt
        sl_pso, ic_pso = np.polyfit(t, y_pso, 1)
        R2_PSO = 1 - np.sum((y_pso - (sl_pso*t+ic_pso))**2) / np.sum((y_pso - y_pso.mean())**2)
        qe_calc = 1 / sl_pso
        k2 = 1 / (ic_pso * (qe_calc**2))

        self._clear_disp(disp)
        banner = ctk.CTkFrame(disp, fg_color=C["surface"], corner_radius=8)
        banner.pack(fill="x", padx=10, pady=10)
        
        best = "Pseudo-Second Order" if R2_PSO > R2_PFO else "Pseudo-First Order"
        ctk.CTkLabel(banner, text=f"Best Kinetic Fit: {best}", font=("Segoe UI", 18, "bold"), text_color=C["accent"]).pack(pady=(10, 0))
        ctk.CTkLabel(banner, text=f"PFO: R²={R2_PFO:.4f} | k1={k1:.4f} min⁻¹", text_color=C["text"]).pack()
        ctk.CTkLabel(banner, text=f"PSO: R²={R2_PSO:.4f} | k2={k2:.4f} g/mg·min | qe={qe_calc:.2f} mg/g", text_color=C["text"]).pack(pady=(0, 10))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5), facecolor=C["card"])
        if len(t_valid) > 2:
            mm_axes(ax1, xlabel="Time (min)", ylabel="ln(qe - qt)", title="Pseudo-First Order")
            ax1.scatter(t_valid, y_pfo, color=C["accent"])
            ax1.plot(t_valid, sl_pfo*t_valid + ic_pfo, color=C["green"], linestyle="--")
            
        mm_axes(ax2, xlabel="Time (min)", ylabel="t/qt", title="Pseudo-Second Order")
        ax2.scatter(t, y_pso, color=C["amber"])
        ax2.plot(t, sl_pso*t + ic_pso, color=C["red"], linestyle="--")
        
        plt.tight_layout()
        self._embed_fig(fig, disp)

    def _run_nitrate_isotherms(self, ece, eqe, disp):
        # Existing logic modernized
        try:
            Ce = np.array([float(v.strip()) for v in ece.get().split(",")])
            qe = np.array([float(v.strip()) for v in eqe.get().split(",")])
        except: return
        
        y_L = Ce / qe
        sl_L, ic_L = np.polyfit(Ce, y_L, 1)
        R2_L = 1 - np.sum((y_L - (sl_L*Ce+ic_L))**2) / np.sum((y_L - y_L.mean())**2)
        
        lce, lqe = np.log(Ce), np.log(qe)
        sl_F, ic_F = np.polyfit(lce, lqe, 1)
        R2_F = 1 - np.sum((lqe - (sl_F*lce+ic_F))**2) / np.sum((lqe - lqe.mean())**2)

        self._clear_disp(disp)
        banner = ctk.CTkFrame(disp, fg_color=C["surface"], corner_radius=8)
        banner.pack(fill="x", padx=10, pady=10)
        
        best = "Langmuir" if R2_L > R2_F else "Freundlich"
        ctk.CTkLabel(banner, text=f"Best Isotherm Fit: {best}", font=("Segoe UI", 18, "bold"), text_color=C["green"]).pack(pady=(10, 0))
        ctk.CTkLabel(banner, text=f"Langmuir: R²={R2_L:.4f} | qmax={1/sl_L:.2f} mg/g | KL={1/(ic_L/sl_L):.3f} L/mg", text_color=C["text"]).pack()
        ctk.CTkLabel(banner, text=f"Freundlich: R²={R2_F:.4f} | Kf={np.exp(ic_F):.2f} | n={1/sl_F:.2f}", text_color=C["text"]).pack(pady=(0, 10))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5), facecolor=C["card"])
        mm_axes(ax1, xlabel="Ce", ylabel="Ce / qe", title="Langmuir")
        ax1.scatter(Ce, y_L, color=C["accent"])
        ax1.plot(Ce, sl_L*Ce + ic_L, color=C["green"], linestyle="--")
        
        mm_axes(ax2, xlabel="ln(Ce)", ylabel="ln(qe)", title="Freundlich")
        ax2.scatter(lce, lqe, color=C["amber"])
        ax2.plot(lce, sl_F*lce + ic_F, color=C["red"], linestyle="--")
        
        plt.tight_layout()
        self._embed_fig(fig, disp)


    # ══════════════════════════════════════════════════════════════════════════
    #  06 · LIME-SODA SOFTENING (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_limesoda(self):
        ctrl, disp = self._module_layout("06 · Lime-Soda Chemical Softening")
        
        self._label(ctrl, "Calcium Hardness (Ca²⁺) as mg/L CaCO3")
        eca = self._entry(ctrl, "200")
        self._label(ctrl, "Magnesium Hardness (Mg²⁺) as mg/L CaCO3")
        emg = self._entry(ctrl, "120")
        self._label(ctrl, "Total Alkalinity (TAC) as mg/L CaCO3")
        etac = self._entry(ctrl, "200")
        self._label(ctrl, "CO2 concentration (mg/L)")
        eco2 = self._entry(ctrl, "15")
        
        self._label(ctrl, "Lime Purity (%)")
        epur = self._entry(ctrl, "85")
        
        self._btn(ctrl, "▶ Calculate Reagent Doses", C["green"], lambda: self._run_limesoda(eca, emg, etac, eco2, epur, disp))

    def _run_limesoda(self, eca, emg, etac, eco2, epur, disp):
        try:
            Ca = float(eca.get())
            Mg = float(emg.get())
            TAC = float(etac.get())
            CO2 = float(eco2.get())
            purity = float(epur.get()) / 100.0
        except: return
        
        # Calculations expressed in meq/L first for stoichiometric precision
        # 1 meq/L CaCO3 = 50 mg/L CaCO3
        ca_meq = Ca / 50.0
        mg_meq = Mg / 50.0
        tac_meq = TAC / 50.0
        co2_meq = CO2 / 22.0 # CO2 eq weight is ~22
        
        # Lime Demand (CaO): Needs to neutralize CO2, HCO3- (TAC), and precipitate Mg
        # Dose in meq/L
        lime_meq = co2_meq + tac_meq + mg_meq
        
        # Soda Demand (Na2CO3): Needs to precipitate Non-Carbonate Hardness (NCH)
        # TH = Ca + Mg. NCH = TH - TAC. If TAC > TH, NCH = 0
        th_meq = ca_meq + mg_meq
        nch_meq = max(th_meq - tac_meq, 0)
        soda_meq = nch_meq
        
        # Convert back to mg/L of actual pure reagent
        # Eq wt: CaO = 28, Na2CO3 = 53
        lime_pure_mg = lime_meq * 28.0
        soda_pure_mg = soda_meq * 53.0
        
        # Factor in purity for commercial Lime
        commercial_lime_mg = lime_pure_mg / purity
        
        self._clear_disp(disp)
        
        banner = ctk.CTkFrame(disp, fg_color=C["surface"], corner_radius=8)
        banner.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(banner, text="Barometric Dose Requirements", font=("Segoe UI", 20, "bold"), text_color=C["text"]).pack(pady=(10, 5))
        ctk.CTkLabel(banner, text=f"Lime (CaO) Pure Dose: {lime_pure_mg:.1f} mg/L", font=("Consolas", 16, "bold"), text_color=C["accent"]).pack()
        ctk.CTkLabel(banner, text=f"Commercial Lime Dose ({purity*100}%): {commercial_lime_mg:.1f} mg/L", font=("Consolas", 18, "bold"), text_color=C["green"]).pack(pady=5)
        ctk.CTkLabel(banner, text=f"Soda (Na₂CO₃) Dose: {soda_pure_mg:.1f} mg/L", font=("Consolas", 16, "bold"), text_color=C["amber"]).pack(pady=(5, 10))

        fig, ax = plt.subplots(figsize=(6, 3), facecolor=C["card"])
        mm_axes(ax, ylabel="Dose (mg/L)", title="Softening Reagents Required")
        ax.bar(["Commercial Lime", "Soda Ash"], [commercial_lime_mg, soda_pure_mg], color=[C["green"], C["amber"]], zorder=3)
        plt.tight_layout()
        self._embed_fig(fig, disp)


    # ══════════════════════════════════════════════════════════════════════════
    #  07 · GRAM STAINING & MORPHOLOGY (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_gram_staining(self):
        ctrl, disp = self._module_layout("07 · Gram Staining & Identification")
        
        self._label(ctrl, "Sample ID")
        eid = self._entry(ctrl, "Isolate_A")
        
        self._label(ctrl, "Gram Reaction")
        gram_var = ctk.CTkOptionMenu(ctrl, values=["Gram-positive (+)", "Gram-negative (-)"], fg_color=C["surface"])
        gram_var.pack(fill="x", pady=(0, 10))
        
        self._label(ctrl, "Morphology / Shape")
        morph_var = ctk.CTkOptionMenu(ctrl, values=["Cocci (Spherical)", "Bacilli (Rods)", "Vibrio (Curved)", "Spirilla"], fg_color=C["surface"])
        morph_var.pack(fill="x", pady=(0, 10))
        
        self._label(ctrl, "Arrangement")
        arr_var = ctk.CTkOptionMenu(ctrl, values=["Pairs/Chains (Strepto-)", "Clusters (Staphylo-)", "Single/Random"], fg_color=C["surface"])
        arr_var.pack(fill="x", pady=(0, 10))
        
        self._label(ctrl, "Endospores Present?")
        spore_var = ctk.CTkOptionMenu(ctrl, values=["No", "Yes"], fg_color=C["surface"])
        spore_var.pack(fill="x", pady=(0, 10))

        self._btn(ctrl, "▶ Identify Pathogen Group", C["amber"], lambda: self._run_gram(eid, gram_var, morph_var, arr_var, spore_var, disp))

    def _run_gram(self, eid, gram_var, morph_var, arr_var, spore_var, disp):
        gp = "+" in gram_var.get()
        shape = morph_var.get()
        arr = arr_var.get()
        spores = spore_var.get() == "Yes"
        
        genus = "Unknown/Unclassified"
        desc = ""
        
        if gp:
            if "Cocci" in shape:
                if "Clusters" in arr: genus = "Staphylococcus spp."
                elif "Chains" in arr: genus = "Streptococcus / Enterococcus"
                else: genus = "Micrococcus"
            elif "Bacilli" in shape:
                if spores: genus = "Bacillus (aerobic) or Clostridium (anaerobic)"
                else: genus = "Listeria / Corynebacterium / Lactobacillus"
        else: # Gram-negative
            if "Bacilli" in shape:
                genus = "Enterobacteriaceae (E. coli, Salmonella, Klebsiella) or Pseudomonas"
            elif "Cocci" in shape:
                genus = "Neisseria / Moraxella"
            elif "Vibrio" in shape:
                genus = "Vibrio cholerae / Campylobacter"
                
        if not gp and spores:
            desc = "⚠️ Warning: Gram-negative bacteria typically do not form endospores. Re-evaluate stain."

        self._clear_disp(disp)
        card = ctk.CTkFrame(disp, fg_color=C["surface"], corner_radius=12)
        card.pack(expand=True, fill="both", padx=40, pady=40)
        
        color = C["purple"] if gp else C["red"]
        
        ctk.CTkLabel(card, text=f"Microbiological Report: {eid.get()}", font=("Segoe UI", 24, "bold"), text_color=C["text"]).pack(pady=(30, 20))
        
        ctk.CTkLabel(card, text=gram_var.get(), font=("Consolas", 32, "bold"), text_color=color).pack()
        ctk.CTkLabel(card, text=f"Morphology: {shape} in {arr}", font=("Segoe UI", 16), text_color=C["sub"]).pack(pady=10)
        
        if spores:
            ctk.CTkLabel(card, text="[Endospores Confirmed]", font=("Segoe UI", 14, "bold"), text_color=C["amber"]).pack()
            
        ctk.CTkLabel(card, text="Probable Genus Classification:", font=("Segoe UI", 14), text_color=C["text"]).pack(pady=(30, 5))
        ctk.CTkLabel(card, text=genus, font=("Segoe UI", 22, "bold"), text_color=C["accent"]).pack()
        
        if desc:
            ctk.CTkLabel(card, text=desc, font=("Segoe UI", 12, "bold"), text_color=C["amber"]).pack(pady=20)


    # ══════════════════════════════════════════════════════════════════════════
    #  08 · SURFACE HYGIENE (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_surface_hygiene(self):
        ctrl, disp = self._module_layout("08 · Surface Hygiene")
        
        self._label(ctrl, "Surfaces Swabbed")
        elbl = self._entry(ctrl, "Bench, Tap, Floor")
        self._label(ctrl, "CFU Count (Total)")
        ecfu = self._entry(ctrl, "120, 45, 800")
        self._label(ctrl, "Area Swabbed (cm²)")
        earea = self._entry(ctrl, "100, 50, 100")
        
        self._label(ctrl, "Facility Type (ISO Limit)")
        fac_var = ctk.CTkOptionMenu(ctrl, values=["Food Prep (Limit: 5 CFU/cm²)", "General Lab (Limit: 50 CFU/cm²)"], fg_color=C["surface"])
        fac_var.pack(fill="x", pady=(0, 10))

        self._btn(ctrl, "▶ Analyse Hygiene Compliance", C["purple"], lambda: self._run_hygiene(elbl, ecfu, earea, fac_var, disp))

    def _run_hygiene(self, elbl, ecfu, earea, fac_var, disp):
        try:
            lbls = [v.strip() for v in elbl.get().split(",")]
            cfus = [float(v.strip()) for v in ecfu.get().split(",")]
            areas = [float(v.strip()) for v in earea.get().split(",")]
            limit = 5.0 if "Food" in fac_var.get() else 50.0
        except: return
        
        cfu_cm2 = [c/a for c, a in zip(cfus, areas)]
        
        self._clear_disp(disp)
        
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=C["card"])
        mm_axes(ax, ylabel="CFU / cm²", title=f"Surface Hygiene Validation ({fac_var.get()})")
        
        colors = [C["green"] if val <= limit else C["red"] for val in cfu_cm2]
        bars = ax.bar(lbls, cfu_cm2, color=colors, zorder=3)
        ax.axhline(limit, color=C["amber"], linestyle="--", linewidth=2, label=f"Limit: {limit} CFU/cm²")
        
        for bar, val in zip(bars, cfu_cm2):
            ax.text(bar.get_x() + bar.get_width()/2, val + (max(cfu_cm2)*0.02), f"{val:.1f}", ha="center", color=C["text"], fontweight="bold")
            
        ax.legend(facecolor=C["surface"], labelcolor=C["text"])
        plt.tight_layout()
        self._embed_fig(fig, disp)


    # ══════════════════════════════════════════════════════════════════════════
    #  09 · BIOLOGICAL WATER QUALITY (ENHANCED)
    # ══════════════════════════════════════════════════════════════════════════
    def _view_water_quality(self):
        ctrl, disp = self._module_layout("09 · Biological Water Quality")
        
        self._label(ctrl, "Sample IDs")
        eid = self._entry(ctrl, "S1, S2, S3")
        self._label(ctrl, "Total Coliforms (CFU/100mL)")
        etc = self._entry(ctrl, "0, 12, 5")
        self._label(ctrl, "Fecal Coliforms/E.coli (CFU/100mL)")
        efc = self._entry(ctrl, "0, 0, 2")
        self._label(ctrl, "Enterococci (CFU/100mL)")
        eent = self._entry(ctrl, "0, 0, 0")
        
        self._label(ctrl, "Standard Assessed Against")
        std_var = ctk.CTkOptionMenu(ctrl, values=["Drinking Water (WHO)", "Recreational/Bathing Water"], fg_color=C["surface"])
        std_var.pack(fill="x", pady=(0, 10))

        self._btn(ctrl, "▶ Assess Potability / Quality", C["red"], lambda: self._run_water_quality(eid, etc, efc, eent, std_var, disp))

    def _run_water_quality(self, eid, etc, efc, eent, std_var, disp):
        try:
            ids = [v.strip() for v in eid.get().split(",")]
            tc = [float(v.strip()) for v in etc.get().split(",")]
            fc = [float(v.strip()) for v in efc.get().split(",")]
            ent = [float(v.strip()) for v in eent.get().split(",")]
            is_drinking = "Drinking" in std_var.get()
        except: return

        # Potability rules
        # Drinking: TC = 0, FC = 0, Ent = 0
        # Recreational: less strict, e.g., FC < 200, Ent < 35 (simplified)
        results = []
        for t, f, e in zip(tc, fc, ent):
            if is_drinking:
                ok = (t == 0 and f == 0 and e == 0)
            else:
                ok = (f <= 200 and e <= 35)
            results.append(ok)
            
        overall = all(results)
        
        self._clear_disp(disp)
        
        banner_color = C["green"] if overall else C["red"]
        banner_text = "ALL SAMPLES COMPLIANT" if overall else "WARNING: NON-COMPLIANT SAMPLES DETECTED"
        
        banner = ctk.CTkFrame(disp, fg_color=banner_color, corner_radius=8)
        banner.pack(fill="x", padx=10, pady=(10, 20))
        ctk.CTkLabel(banner, text=banner_text, font=("Arial", 16, "bold"), text_color=C["bg"]).pack(pady=10)

        fig, axes = plt.subplots(1, 3, figsize=(10, 3.5), facecolor=C["card"])
        
        mm_axes(axes[0], title="Total Coliforms")
        axes[0].bar(ids, tc, color=[C["green"] if (v==0 if is_drinking else True) else C["red"] for v in tc])
        
        mm_axes(axes[1], title="Fecal Coliforms")
        axes[1].bar(ids, fc, color=[C["green"] if (v==0 if is_drinking else v<=200) else C["red"] for v in fc])
        if not is_drinking: axes[1].axhline(200, color=C["amber"], linestyle="--")
        
        mm_axes(axes[2], title="Enterococci")
        axes[2].bar(ids, ent, color=[C["green"] if (v==0 if is_drinking else v<=35) else C["red"] for v in ent])
        if not is_drinking: axes[2].axhline(35, color=C["amber"], linestyle="--")
        
        plt.tight_layout()
        self._embed_fig(fig, disp)


if __name__ == "__main__":
    app = AquaLabs()
    app.mainloop()
