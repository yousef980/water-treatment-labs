import sys
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import openpyxl
except ImportError:
    pass


class EliteWaterSuite(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AQUALABS: Advanced Water Treatment Processing Core")
        self.geometry("1240x780")
        self.configure(bg="#0f111a")

        # Color Palette Design Schema (Modern Dark Matrix)
        self.clr_bg      = "#0f111a"
        self.clr_card    = "#1a1d29"
        self.clr_sidebar = "#090a0f"
        self.clr_accent  = "#00d2ff"
        self.clr_success = "#00ff87"
        self.clr_text    = "#e2e8f0"
        self.clr_muted   = "#64748b"

        self.navigation_history = []
        self.current_frame = None

        self.build_framework_layout()
        self.navigate_to("Dashboard")

    # ------------------------------------------------------------------
    # EXPANDED UNIVERSAL FILE INGESTION MATRIX (.csv, .xlsx, etc)
    # ------------------------------------------------------------------
    def import_laboratory_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Lab Formats",          "*.csv *.xlsx *.xls *.txt *.md *.docx"),
                ("Comma Separated Values",   "*.csv"),
                ("Excel Spreadsheets",       "*.xlsx *.xls"),
                ("Text & Markdown Records",  "*.txt *.md"),
                ("Word Documents",           "*.docx"),
            ]
        )
        if not file_path:
            return None

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(file_path)
                messagebox.showinfo("Success",
                    f"Imported CSV data sheet successfully!\nLoaded {len(df)} data points.")
                return df

            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(file_path)
                messagebox.showinfo("Success",
                    f"Imported Excel file successfully!\nLoaded {len(df)} data points.")
                return df

            elif ext in (".txt", ".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return self.parse_text_matrix(content)

            elif ext == ".docx":
                import zipfile
                import xml.etree.ElementTree as ET
                doc = zipfile.ZipFile(file_path)
                xml_content = doc.read("word/document.xml")
                root = ET.fromstring(xml_content)
                namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                text_runs = [
                    node.text for node in root.findall(".//w:t", namespaces) if node.text
                ]
                full_text = " ".join(text_runs)
                return self.parse_text_matrix(full_text)

        except Exception as err:
            messagebox.showerror("Ingestion Error",
                f"Could not parse file structure.\nDetails: {err}")
            return None

    def parse_text_matrix(self, text):
        numbers = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]
        if len(numbers) < 2:
            return None
        if len(numbers) % 2 != 0:
            half = len(numbers) // 2
            if half == 0:
                return None
            return pd.DataFrame({"Dose": numbers[:half], "Value": numbers[half:]})
        return pd.DataFrame({"Dose": numbers[0::2], "Value": numbers[1::2]})

    # ------------------------------------------------------------------
    # FRAMEWORK INFRASTRUCTURE & SIDEBAR NAVIGATION ROUTING MAP
    # ------------------------------------------------------------------
    def build_framework_layout(self):
        self.sidebar = tk.Frame(self, bg=self.clr_sidebar, width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = tk.Label(
            self.sidebar, text="A Q U A L A B S",
            bg=self.clr_sidebar, fg=self.clr_accent,
            font=("Consolas", 15, "bold"),
        )
        logo.pack(pady=20, anchor="w", padx=25)

        links = [
            ("Unified Main Dashboard",           "Dashboard"),
            ("01. Coagulation (Jar Test)",        "JarTest"),
            ("02. Breakpoint Chlorination",       "Chlorination"),
            ("03. Suspended Solids (TSS)",        "SuspendedSolids"),
            ("04. Iron & Manganese Removal",      "IronManganese"),
            ("05. Nitrate Adsorption Kinetics",   "NitrateAdsorption"),
            ("06. Lime-Soda Softening",           "LimeSoda"),
            ("07. Gram Staining Microbiology",    "GramStaining"),
            ("08. Surface Hygiene Monitoring",    "SurfaceHygiene"),
            ("09. Water Contamination Tracking",  "WaterContamination"),
        ]

        canvas_sb   = tk.Canvas(self.sidebar, bg=self.clr_sidebar, bd=0, highlightthickness=0)
        scrollbar_sb = ttk.Scrollbar(self.sidebar, orient="vertical", command=canvas_sb.yview)
        self.scroll_frame = tk.Frame(canvas_sb, bg=self.clr_sidebar)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas_sb.configure(scrollregion=canvas_sb.bbox("all")),
        )
        canvas_sb.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=260)
        canvas_sb.configure(yscrollcommand=scrollbar_sb.set)

        canvas_sb.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar_sb.pack(side="right", fill="y")

        for display_name, routing_target in links:
            btn = tk.Button(
                self.scroll_frame, text=display_name,
                bg=self.clr_sidebar, fg=self.clr_text,
                font=("Segoe UI", 9), bd=0,
                activebackground="#12141c", activeforeground=self.clr_accent,
                anchor="w", padx=10, pady=8,
                command=lambda t=routing_target: self.navigate_to(t),
            )
            btn.pack(fill="x", pady=1)

        footer_pane = tk.Frame(self.sidebar, bg=self.clr_sidebar, height=110)
        footer_pane.pack(side="bottom", fill="x", padx=15, pady=10)

        back_btn = tk.Button(
            footer_pane, text="<- Universal Track-Back",
            bg="#161924", fg=self.clr_text,
            font=("Segoe UI", 9, "bold"), bd=0,
            activebackground=self.clr_accent, pady=8,
            command=self.execute_track_back,
        )
        back_btn.pack(fill="x", pady=2)

        home_btn = tk.Button(
            footer_pane, text="[MainMenu] Universal Home",
            bg=self.clr_accent, fg=self.clr_sidebar,
            font=("Segoe UI", 9, "bold"), bd=0,
            activebackground=self.clr_success, pady=8,
            command=lambda: self.navigate_to("Dashboard"),
        )
        home_btn.pack(fill="x", pady=2)

        self.workspace = tk.Frame(self, bg=self.clr_bg)
        self.workspace.pack(side="right", expand=True, fill="both", padx=25, pady=20)

    def navigate_to(self, view_name):
        if self.navigation_history and self.navigation_history[-1] == view_name:
            return
        self.navigation_history.append(view_name)
        if len(self.navigation_history) > 25:
            self.navigation_history.pop(0)
        self.render_view_by_target(view_name)

    def execute_track_back(self):
        if len(self.navigation_history) <= 1:
            messagebox.showinfo("Navigation", "Base layer active.")
            return
        self.navigation_history.pop()
        self.render_view_by_target(self.navigation_history[-1])

    def render_view_by_target(self, view_name):
        if self.current_frame:
            self.current_frame.destroy()
        plt.close("all")

        self.current_frame = tk.Frame(self.workspace, bg=self.clr_bg)
        self.current_frame.pack(expand=True, fill="both")

        views = {
            "Dashboard":        self.draw_dashboard_view,
            "JarTest":          self.draw_jartest_view,
            "Chlorination":     self.draw_chlorination_view,
            "SuspendedSolids":  self.draw_suspended_solids_view,
            "IronManganese":    lambda: self.draw_generic_placeholder(
                                    "04. Iron & Manganese Groundwater Removal"),
            "NitrateAdsorption": self.draw_nitrate_adsorption_view,
            "LimeSoda":         lambda: self.draw_generic_placeholder(
                                    "06. Chemical Precipitation Softening (Lime-Soda)"),
            "GramStaining":     lambda: self.draw_generic_placeholder(
                                    "07. Microbiology Identification (Gram Staining)"),
            "SurfaceHygiene":   lambda: self.draw_generic_placeholder(
                                    "08. Surface Hygiene Monitor & Swab Analysis"),
            "WaterContamination": lambda: self.draw_generic_placeholder(
                                    "09. Biological Water Quality Coliform Tracking"),
        }
        views.get(view_name, self.draw_dashboard_view)()

    # ------------------------------------------------------------------
    # MAIN CORE VISUAL DASHBOARD SUMMARY PANELS
    # ------------------------------------------------------------------
    def draw_dashboard_view(self):
        title = tk.Label(
            self.current_frame,
            text="Laboratory Automation Ecosystem Core",
            bg=self.clr_bg, fg=self.clr_text,
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor="w", pady=(5, 2))

        desc = tk.Label(
            self.current_frame,
            text="Master of Environmental Engineering Laboratory Suite Dashboard Console.",
            bg=self.clr_bg, fg=self.clr_muted,
            font=("Segoe UI", 9),
        )
        desc.pack(anchor="w", pady=(0, 15))

        canvas_db   = tk.Canvas(self.current_frame, bg=self.clr_bg, bd=0, highlightthickness=0)
        scrollbar_db = ttk.Scrollbar(self.current_frame, orient="vertical", command=canvas_db.yview)
        grid_frame  = tk.Frame(canvas_db, bg=self.clr_bg)

        grid_frame.bind(
            "<Configure>",
            lambda e: canvas_db.configure(scrollregion=canvas_db.bbox("all")),
        )
        canvas_db.create_window((0, 0), window=grid_frame, anchor="nw", width=880)
        canvas_db.configure(yscrollcommand=scrollbar_db.set)
        canvas_db.pack(side="left", fill="both", expand=True)
        scrollbar_db.pack(side="right", fill="y")

        modules = [
            ("01. Coagulation Processing Engine",
             "Jar Test curves with automated data handling vectors.", "JarTest"),
            ("02. Breakpoint Disinfection Model",
             "Chemical dosing trajectories for water sanitation processing.", "Chlorination"),
            ("03. Gravimetric Analytics Matrix",
             "Total Suspended Solids filter assay tracking workflows.", "SuspendedSolids"),
            ("04. Iron & Manganese Removal",
             "Oxidation and precipitation extraction processing from aquifers.", "IronManganese"),
            ("05. Nitrate Adsorption Kinetics",
             "Adsorption isothermal data modeling matrices.", "NitrateAdsorption"),
            ("06. Lime-Soda Precipitation Softening",
             "Automated carbonate hardness calculation matrices.", "LimeSoda"),
            ("07. Gram Staining Microbiology",
             "Microscopic morphology data metrics documentation modules.", "GramStaining"),
            ("08. Surface Hygiene Assessment",
             "Sanitation monitoring swabbing analytics.", "SurfaceHygiene"),
            ("09. Biological Water Contamination",
             "Coliform colony calculations and tracking pipelines.", "WaterContamination"),
        ]

        for name, details, route in modules:
            card = tk.Frame(grid_frame, bg=self.clr_card, bd=0, padx=15, pady=12)
            card.pack(fill="x", pady=4)

            lbl_name = tk.Label(card, text=name,
                                bg=self.clr_card, fg=self.clr_accent,
                                font=("Segoe UI", 11, "bold"))
            lbl_name.pack(anchor="w")

            lbl_det = tk.Label(card, text=details,
                               bg=self.clr_card, fg=self.clr_text,
                               font=("Segoe UI", 9), justify="left")
            lbl_det.pack(anchor="w", pady=2)

            launch_btn = tk.Button(
                card, text="Open Workspace ->",
                bg="#242938", fg=self.clr_accent,
                font=("Segoe UI", 8, "bold"), bd=0, padx=10, pady=4,
                command=lambda r=route: self.navigate_to(r),
            )
            launch_btn.pack(anchor="e", pady=(2, 0))

    # ------------------------------------------------------------------
    # SHARED LAYOUT HELPER
    # ------------------------------------------------------------------
    def setup_module_base_layout(self, title_text):
        title = tk.Label(
            self.current_frame, text=title_text,
            bg=self.clr_bg, fg=self.clr_text,
            font=("Segoe UI", 14, "bold"),
        )
        title.pack(anchor="w", pady=(5, 15))

        pane = tk.Frame(self.current_frame, bg=self.clr_bg)
        pane.pack(expand=True, fill="both")

        self.ctrl_panel = tk.Frame(pane, bg=self.clr_card, width=260, padx=15, pady=15)
        self.ctrl_panel.pack(side="left", fill="y", padx=(0, 15))
        self.ctrl_panel.pack_propagate(False)

        self.display_panel = tk.Frame(pane, bg=self.clr_card, padx=10, pady=10)
        self.display_panel.pack(side="left", expand=True, fill="both")

    def clear_display_canvas(self):
        for widget in self.display_panel.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------
    # MODULE DATA LOG WORKSPACE CONTROLLERS
    # ------------------------------------------------------------------

    # --- 01. Jar Test ---
    def draw_jartest_view(self):
        self.setup_module_base_layout("01. Coagulation & Flocculation Optimization (Jar Test)")

        upload_btn = tk.Button(
            self.ctrl_panel, text="[Open] Auto-Ingest Lab File",
            bg="#242938", fg=self.clr_accent,
            font=("Segoe UI", 9, "bold"), bd=0, pady=8,
            command=self.handle_jar_file_import,
        )
        upload_btn.pack(fill="x", pady=(5, 10))

        tk.Label(self.ctrl_panel, text="Manual Dosing Entries (mg/L):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.entry_x = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                                bd=1, insertbackground="white")
        self.entry_x.pack(fill="x", pady=(2, 8))
        self.entry_x.insert(0, "10, 20, 30, 40, 50, 60")

        tk.Label(self.ctrl_panel, text="Observed Residual Turbidity (NTU):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.entry_y = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                                bd=1, insertbackground="white")
        self.entry_y.pack(fill="x", pady=(2, 15))
        self.entry_y.insert(0, "14.2, 8.5, 1.8, 4.3, 9.1, 15.4")

        proc_btn = tk.Button(
            self.ctrl_panel, text="[Run] Run Analysis Pipeline",
            bg=self.clr_success, fg=self.clr_sidebar,
            font=("Segoe UI", 10, "bold"), bd=0, pady=8,
            command=self.execute_jar_math,
        )
        proc_btn.pack(fill="x")

    def handle_jar_file_import(self):
        df = self.import_laboratory_file()
        if df is not None and len(df) >= 2:
            self.entry_x.delete(0, tk.END)
            self.entry_y.delete(0, tk.END)
            self.entry_x.insert(0, ", ".join(str(x) for x in df.iloc[:, 0].tolist()))
            self.entry_y.insert(0, ", ".join(str(y) for y in df.iloc[:, 1].tolist()))

    def execute_jar_math(self):
        try:
            x  = [float(i.strip()) for i in self.entry_x.get().split(",")]
            y  = [float(i.strip()) for i in self.entry_y.get().split(",")]
            df = pd.DataFrame({"Dose": x, "Turbidity": y})
            opt = df.loc[df["Turbidity"].idxmin()]
        except Exception:
            messagebox.showerror("Error", "Invalid numeric sequencing layout.")
            return

        self.clear_display_canvas()

        fig, ax = plt.subplots(figsize=(5, 3.5), facecolor=self.clr_card)
        ax.set_facecolor(self.clr_card)
        ax.plot(df["Dose"], df["Turbidity"], marker="o", color=self.clr_accent, linewidth=2)
        ax.axvline(x=opt["Dose"], color=self.clr_success, linestyle="--")
        ax.set_title("Turbidity Optimization Curve", color=self.clr_text,
                     fontsize=10, fontweight="bold")
        ax.tick_params(colors=self.clr_text, labelsize=8)
        ax.grid(True, color="#2d3142", linestyle=":")
        ax.text(opt["Dose"] + 1, opt["Turbidity"] + 2,
                f"Optimal: {opt['Dose']} mg/L",
                color=self.clr_success, fontweight="bold", fontsize=9)

        canvas = FigureCanvasTkAgg(fig, master=self.display_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    # --- 02. Breakpoint Chlorination ---
    def draw_chlorination_view(self):
        self.setup_module_base_layout("02. Breakpoint Chlorination Curve Simulator")

        upload_btn = tk.Button(
            self.ctrl_panel, text="[Open] Auto-Ingest Lab File",
            bg="#242938", fg=self.clr_accent,
            font=("Segoe UI", 9, "bold"), bd=0, pady=8,
            command=self.handle_chlorine_file_import,
        )
        upload_btn.pack(fill="x", pady=(5, 10))

        tk.Label(self.ctrl_panel, text="Chlorine Dose Applied (mg/L):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.cl_dose = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                                bd=1, insertbackground="white")
        self.cl_dose.pack(fill="x", pady=(2, 8))
        self.cl_dose.insert(0, "0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0")

        tk.Label(self.ctrl_panel, text="Measured Total Residual Cl (mg/L):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.cl_res = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                               bd=1, insertbackground="white")
        self.cl_res.pack(fill="x", pady=(2, 15))
        self.cl_res.insert(0, "0.4, 0.8, 1.1, 0.6, 0.2, 0.5, 1.0, 1.5")

        run_btn = tk.Button(
            self.ctrl_panel, text="[Run] Plot Disinfection Kinetics",
            bg=self.clr_accent, fg=self.clr_sidebar,
            font=("Segoe UI", 10, "bold"), bd=0, pady=8,
            command=self.execute_chlorine_math,
        )
        run_btn.pack(fill="x")

    def handle_chlorine_file_import(self):
        df = self.import_laboratory_file()
        if df is not None and len(df) >= 2:
            self.cl_dose.delete(0, tk.END)
            self.cl_res.delete(0, tk.END)
            self.cl_dose.insert(0, ", ".join(str(x) for x in df.iloc[:, 0].tolist()))
            self.cl_res.insert(0, ", ".join(str(y) for y in df.iloc[:, 1].tolist()))

    def execute_chlorine_math(self):
        try:
            x = [float(i.strip()) for i in self.cl_dose.get().split(",")]
            y = [float(i.strip()) for i in self.cl_res.get().split(",")]
        except Exception:
            messagebox.showerror("Error", "Check data entry spacing.")
            return

        self.clear_display_canvas()

        fig, ax = plt.subplots(figsize=(5, 3.5), facecolor=self.clr_card)
        ax.set_facecolor(self.clr_card)
        ax.plot(x, y, marker="s", color="#ffb703", linewidth=2, label="Total Residual Cl")
        breakpoint_idx = y.index(min(y[2:6])) if len(y) > 5 else 4
        ax.axvline(x=x[breakpoint_idx], color="#ff0055", linestyle=":",
                   label=f"Breakpoint ({x[breakpoint_idx]} mg/L)")
        ax.set_title("Breakpoint Chemistry Profile", color=self.clr_text,
                     fontsize=10, fontweight="bold")
        ax.tick_params(colors=self.clr_text, labelsize=8)
        ax.grid(True, color="#2d3142", linestyle=":")
        ax.legend(facecolor=self.clr_sidebar, labelcolor=self.clr_text, fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=self.display_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    # --- 03. Suspended Solids ---
    def draw_suspended_solids_view(self):
        self.setup_module_base_layout("03. Gravimetric Analysis: TSS Calculations")

        tk.Label(self.ctrl_panel, text="Sample Volume (mL):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.ss_vol = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                               bd=1, insertbackground="white")
        self.ss_vol.pack(fill="x", pady=(2, 8))
        self.ss_vol.insert(0, "100")

        tk.Label(self.ctrl_panel, text="Clean Filter Mass (g):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.ss_w1 = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                              bd=1, insertbackground="white")
        self.ss_w1.pack(fill="x", pady=(2, 8))
        self.ss_w1.insert(0, "1.2435")

        tk.Label(self.ctrl_panel, text="Dried Residue Filter Weight (g):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.ss_w2 = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                              bd=1, insertbackground="white")
        self.ss_w2.pack(fill="x", pady=(2, 15))
        self.ss_w2.insert(0, "1.2488")

        run_btn = tk.Button(
            self.ctrl_panel, text="[Run] Compute TSS Metrics",
            bg=self.clr_success, fg=self.clr_sidebar,
            font=("Segoe UI", 10, "bold"), bd=0, pady=8,
            command=self.execute_solids_math,
        )
        run_btn.pack(fill="x")

    def execute_solids_math(self):
        try:
            vol = float(self.ss_vol.get()) / 1000.0
            w1  = float(self.ss_w1.get())
            w2  = float(self.ss_w2.get())
            tss_mg_l = ((w2 - w1) * 1_000_000) / (vol * 1000)
        except Exception:
            messagebox.showerror("Error", "Review entries.")
            return

        self.clear_display_canvas()
        out_lbl = tk.Label(
            self.display_panel,
            text=f"Total Suspended Solids (TSS):\n\n{tss_mg_l:.2f} mg/L",
            bg=self.clr_card, fg=self.clr_success,
            font=("Consolas", 16, "bold"),
        )
        out_lbl.pack(expand=True)

    # --- 05. Nitrate Adsorption Kinetics ---
    def draw_nitrate_adsorption_view(self):
        self.setup_module_base_layout("05. Nitrate Adsorption Kinetics Modeling")

        upload_btn = tk.Button(
            self.ctrl_panel, text="[Open] Auto-Ingest Adsorption File",
            bg="#242938", fg=self.clr_accent,
            font=("Segoe UI", 9, "bold"), bd=0, pady=8,
            command=self.handle_adsorption_file_import,
        )
        upload_btn.pack(fill="x", pady=(5, 10))

        tk.Label(self.ctrl_panel, text="Equilibrium Conc. Ce (mg/L):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.ads_ce = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                               bd=1, insertbackground="white")
        self.ads_ce.pack(fill="x", pady=(2, 8))
        self.ads_ce.insert(0, "1.2, 2.5, 4.8, 8.2, 12.5")

        tk.Label(self.ctrl_panel, text="Adsorbed Capacity qe (mg/g):",
                 bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.ads_qe = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text,
                               bd=1, insertbackground="white")
        self.ads_qe.pack(fill="x", pady=(2, 15))
        self.ads_qe.insert(0, "0.45, 0.78, 1.15, 1.42, 1.65")

        run_btn = tk.Button(
            self.ctrl_panel, text="[Run] Fit Isotherm Models",
            bg=self.clr_success, fg=self.clr_sidebar,
            font=("Segoe UI", 10, "bold"), bd=0, pady=8,
            command=self.execute_adsorption_math,
        )
        run_btn.pack(fill="x")

    def handle_adsorption_file_import(self):
        df = self.import_laboratory_file()
        if df is not None and len(df) >= 2:
            self.ads_ce.delete(0, tk.END)
            self.ads_qe.delete(0, tk.END)
            self.ads_ce.insert(0, ", ".join(str(x) for x in df.iloc[:, 0].tolist()))
            self.ads_qe.insert(0, ", ".join(str(y) for y in df.iloc[:, 1].tolist()))

    def execute_adsorption_math(self):
        import numpy as np

        try:
            Ce = np.array([float(i.strip()) for i in self.ads_ce.get().split(",")])
            qe = np.array([float(i.strip()) for i in self.ads_qe.get().split(",")])
            if len(Ce) != len(qe):
                raise ValueError("Array length mismatch")
        except Exception:
            messagebox.showerror("Error", "Ce and qe arrays must be of equal numeric length.")
            return

        self.clear_display_canvas()

        # Linearized Langmuir
        y_lang    = Ce / qe
        slope_l, intercept_l = np.polyfit(Ce, y_lang, 1)
        qmax      = 1.0 / slope_l
        b_const   = 1.0 / (intercept_l * qmax)

        # Linearized Freundlich
        slope_f, intercept_f = np.polyfit(np.log(Ce), np.log(qe), 1)
        Kf        = np.exp(intercept_f)
        n_const   = 1.0 / slope_f

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 3.8), facecolor=self.clr_card)
        ax1.set_facecolor(self.clr_card)
        ax2.set_facecolor(self.clr_card)

        ax1.scatter(Ce, y_lang, color=self.clr_accent, label="Data")
        ax1.plot(Ce, slope_l * Ce + intercept_l, color=self.clr_success, linestyle="--")
        ax1.set_title("Langmuir Linear Fit", color=self.clr_text, fontsize=9, fontweight="bold")
        ax1.tick_params(colors=self.clr_text, labelsize=7)
        ax1.set_xlabel("Ce (mg/L)",   color=self.clr_muted, fontsize=8)
        ax1.set_ylabel("Ce/qe (g/L)", color=self.clr_muted, fontsize=8)

        ax2.scatter(np.log(Ce), np.log(qe), color="#ffb703", label="Data")
        ax2.plot(np.log(Ce), slope_f * np.log(Ce) + intercept_f, color="#ff0055", linestyle=":")
        ax2.set_title("Freundlich Linear Fit", color=self.clr_text, fontsize=9, fontweight="bold")
        ax2.tick_params(colors=self.clr_text, labelsize=7)
        ax2.set_xlabel("ln(Ce)", color=self.clr_muted, fontsize=8)
        ax2.set_ylabel("ln(qe)", color=self.clr_muted, fontsize=8)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.display_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", pady=(0, 40))

        summary = (
            f"Langmuir: qmax = {qmax:.2f} mg/g, b = {b_const:.3f} L/mg  |  "
            f"Freundlich: Kf = {Kf:.2f}, n = {n_const:.2f}"
        )
        summary_lbl = tk.Label(
            self.display_panel, text=summary,
            bg=self.clr_card, fg=self.clr_accent,
            font=("Segoe UI", 9, "bold"),
        )
        summary_lbl.place(relx=0.5, rely=0.95, anchor="center")

    # ------------------------------------------------------------------
    # LAYOUT PLATFORM PLACEHOLDER INFRASTRUCTURE
    # ------------------------------------------------------------------
    def draw_generic_placeholder(self, module_name):
        self.setup_module_base_layout(module_name)
        lbl = tk.Label(
            self.display_panel,
            text="[Active Ingest Node]\nReady to receive analytical variables from laboratory equipment logsheets.",
            bg=self.clr_card, fg=self.clr_muted,
            font=("Segoe UI", 10, "italic"),
        )
        lbl.pack(expand=True)


# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------
if __name__ == "__main__":
    app = EliteWaterSuite()
    app.mainloop()
