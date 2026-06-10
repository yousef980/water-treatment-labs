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
        self.geometry("1200x750")
        self.configure(bg="#0f111a") 
        
        self.clr_bg = "#0f111a"
        self.clr_card = "#1a1d29"
        self.clr_sidebar = "#090a0f"
        self.clr_accent = "#00d2ff"     
        self.clr_success = "#00ff87"    
        self.clr_text = "#e2e8f0"
        self.clr_muted = "#64748b"
        
        self.navigation_history = []
        self.current_frame = None
        
        self.build_framework_layout()
        self.navigate_to("Dashboard")

    def import_laboratory_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("All Valid Lab Files", "*.xlsx *.xls *.txt *.md *.docx"),
                       ("Excel Spreadsheets", "*.xlsx *.xls"),
                       ("Text & Markdown Records", "*.txt *.md"),
                       ("Word Documents", "*.docx")]
        )
        if not file_path:
            return None
            
        ext = os.path.splitext(file_path).lower()
        try:
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                messagebox.showinfo("Success", f"Imported Excel file successfully!\nLoaded {len(df)} data points.")
                return df
                
            elif ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self.parse_text_matrix(content)
                
            elif ext == '.docx':
                import zipfile
                import xml.etree.ElementTree as ET
                doc = zipfile.ZipFile(file_path)
                xml_content = doc.read('word/document.xml')
                root = ET.fromstring(xml_content)
                namespaces = {'w': 'http://openxmlformats.org'}
                text_runs = [node.text for node in root.findall('.//w:t', namespaces) if node.text]
                full_text = " ".join(text_runs)
                return self.parse_text_matrix(full_text)
                
        except Exception as err:
            messagebox.showerror("Ingestion Error", f"Could not parse file structure.\nDetails: {err}")
            return None

    def parse_text_matrix(self, text):
        numbers = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]
        if len(numbers) < 2 or len(numbers) % 2 != 0:
            half = len(numbers) // 2
            if half == 0: return None
            return pd.DataFrame({"Dose": numbers[:half], "Value": numbers[half:]})
        
        doses = numbers[0::2]
        values = numbers[1::2]
        return pd.DataFrame({"Dose": doses, "Value": values})

    def build_framework_layout(self):
        self.sidebar = tk.Frame(self, bg=self.clr_sidebar, width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        logo = tk.Label(self.sidebar, text="A Q U A L A B S", bg=self.clr_sidebar, fg=self.clr_accent, font=("Consolas", 15, "bold"))
        logo.pack(pady=25, anchor="w", padx=25)
        
        links = [
            ("Unified Dashboard", "Dashboard"),
            ("Coagulation (Jar Test)", "JarTest"),
            ("Breakpoint Disinfection", "Chlorination"),
            ("Gravimetric Analytics", "SuspendedSolids")
        ]
        
        for display_name, routing_target in links:
            btn = tk.Button(self.sidebar, text=f"  {display_name}", bg=self.clr_sidebar, fg=self.clr_text,
                            font=("Segoe UI", 10), bd=0, activebackground="#12141c", activeforeground=self.clr_accent,
                            anchor="w", padx=10, pady=12, command=lambda t=routing_target: self.navigate_to(t))
            btn.pack(fill="x", padx=10, pady=2)
            
        separator = tk.Frame(self.sidebar, bg="#1e2230", height=1)
        separator.pack(fill="x", side="bottom", pady=(0, 80))
        
        back_btn = tk.Button(self.sidebar, text="<- Universal Track-Back", bg="#161924", fg=self.clr_text,
                             font=("Segoe UI", 9, "bold"), bd=0, activebackground=self.clr_accent, pady=10,
                             command=self.execute_track_back)
        back_btn.pack(fill="x", side="bottom", padx=15, pady=5)

        home_btn = tk.Button(self.sidebar, text="[MainMenu] Universal Home", bg=self.clr_accent, fg=self.clr_sidebar,
                             font=("Segoe UI", 9, "bold"), bd=0, activebackground=self.clr_success, pady=10,
                             command=lambda: self.navigate_to("Dashboard"))
        home_btn.pack(fill="x", side="bottom", padx=15, pady=5)

        self.workspace = tk.Frame(self, bg=self.clr_bg)
        self.workspace.pack(side="right", expand=True, fill="both", padx=30, pady=25)

    def navigate_to(self, view_name):
        if self.navigation_history and self.navigation_history[-1] == view_name:
            return 
            
        self.navigation_history.append(view_name)
        if len(self.navigation_history) > 20: 
            self.navigation_history.pop(0) 
            
        self.render_view_by_target(view_name)

    def execute_track_back(self):
        if len(self.navigation_history) <= 1:
            messagebox.showinfo("Navigation", "You are at the home dashboard layer.")
            return
        self.navigation_history.pop() 
        previous_view = self.navigation_history[-1]
        self.render_view_by_target(previous_view)

    def render_view_by_target(self, view_name):
        if self.current_frame:
            self.current_frame.destroy()
        plt.close('all')
        
        self.current_frame = tk.Frame(self.workspace, bg=self.clr_bg)
        self.current_frame.pack(expand=True, fill="both")
        
        if view_name == "Dashboard":
            self.draw_dashboard_view()
        elif view_name == "JarTest":
            self.draw_jartest_view()
        elif view_name == "Chlorination":
            self.draw_chlorination_view()
        elif view_name == "SuspendedSolids":
            self.draw_suspended_solids_view()

    def draw_dashboard_view(self):
        title = tk.Label(self.current_frame, text="Laboratory Automation Ecosystem Core", bg=self.clr_bg, fg=self.clr_text, font=("Segoe UI", 18, "bold"))
        title.pack(anchor="w", pady=(10, 5))
        
        desc = tk.Label(self.current_frame, text="Select an engineering module to calculate variables or plot kinetics profiles.", bg=self.clr_bg, fg=self.clr_muted, font=("Segoe UI", 10))
        desc.pack(anchor="w", pady=(0, 30))
        
        grid_frame = tk.Frame(self.current_frame, bg=self.clr_bg)
        grid_frame.pack(fill="x", pady=10)
        
        modules = [
            ("Coagulation Processing Engine (Jar Test)", "Optimize chemical dosing values and identify colloid restabilization thresholds using dynamic optimization modeling curves.", "JarTest"),
            ("Breakpoint Disinfection Simulator", "Analyze active free chlorine parameters and simulate active combined mono/dichloramine curve trajectories.", "Chlorination"),
            ("Gravimetric Analytics Matrix (TSS / TDS)", "Process precise volatile vs mineral analytical weight metrics for standard filter assays.", "SuspendedSolids")
        ]
        
        for name, details, route in modules:
            card = tk.Frame(grid_frame, bg=self.clr_card, bd=0, padx=20, pady=20)
            card.pack(fill="x", pady=8)
            
            lbl_name = tk.Label(card, text=name, bg=self.clr_card, fg=self.clr_accent, font=("Segoe UI", 12, "bold"))
            lbl_name.pack(anchor="w")
            
            lbl_det = tk.Label(card, text=details, bg=self.clr_card, fg=self.clr_text, font=("Segoe UI", 9), wraplength=800, justify="left")
            lbl_det.pack(anchor="w", pady=5)
            
            launch_btn = tk.Button(card, text="Initialize Workspace ->", bg="#242938", fg=self.clr_accent, font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6, command=lambda r=route: self.navigate_to(r))
            launch_btn.pack(anchor="e", pady=(5, 0))

    def draw_jartest_view(self):
        self.setup_module_base_layout("Coagulation & Flocculation Optimization (Jar Test)")
        
        upload_btn = tk.Button(self.ctrl_panel, text="[Open] Auto-Ingest Lab Logsheet", bg="#242938", fg=self.clr_accent, font=("Segoe UI", 9, "bold"), bd=0, pady=8, command=self.handle_jar_file_import)
        upload_btn.pack(fill="x", pady=(10, 15))
        
        tk.Label(self.ctrl_panel, text="Manual Dosing Entries (mg/L):", bg=self.clr_card, fg=self.clr_text, font=("Segoe UI", 9)).pack(anchor="w")
        self.entry_x = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text, bd=1, insertbackground="white")
        self.entry_x.pack(fill="x", pady=(2, 10))
        self.entry_x.insert(0, "10, 20, 30, 40, 50, 60")
        
        tk.Label(self.ctrl_panel, text="Observed Residual Turbidity (NTU):", bg=self.ctrl_card, fg=self.clr_text, font=("Segoe UI", 9)).pack(anchor="w")
        self.entry_y = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text, bd=1, insertbackground="white")
        self.entry_y.pack(fill="x", pady=(2, 20))
        self.entry_y.insert(0, "14.2, 8.5, 1.8, 4.3, 9.1, 15.4")
        
        proc_btn = tk.Button(self.ctrl_panel, text="[Run] Run Analysis Pipeline", bg=self.clr_success, fg=self.clr_sidebar, font=("Segoe UI", 10, "bold"), bd=0, pady=8, command=self.execute_jar_math)
        proc_btn.pack(fill="x")

    def handle_jar_file_import(self):
        df = self.import_laboratory_file()

# -------------------------------------------------------------
    # FILE HANDLING & JAR TEST EXECUTION MATRIX
    # -------------------------------------------------------------
    def handle_jar_file_import(self):
        df = self.import_laboratory_file()
        if df is not None and len(df) >= 2:
            self.entry_x.delete(0, tk.END)
            self.entry_y.delete(0, tk.END)
            self.entry_x.insert(0, ", ".join([str(x) for x in df.iloc[:, 0].tolist()]))
            self.entry_y.insert(0, ", ".join([str(y) for y in df.iloc[:, 1].tolist()]))

    def execute_jar_math(self):
        try:
            x = [float(i.strip()) for i in self.entry_x.get().split(",")]
            y = [float(i.strip()) for i in self.entry_y.get().split(",")]
            df = pd.DataFrame({"Dose": x, "Turbidity": y})
            opt = df.loc[df["Turbidity"].idxmin()]
        except Exception:
            messagebox.showerror("Error", "Invalid numeric sequencing arrays.")
            return
            
        self.clear_display_canvas()
        
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=self.clr_card)
        ax.set_facecolor(self.clr_card)
        ax.plot(df["Dose"], df["Turbidity"], marker="o", color=self.clr_accent, linewidth=2)
        ax.axvline(x=opt["Dose"], color=self.clr_success, linestyle="--")
        
        ax.set_title("Turbidity Clean Optimization Curve", color=self.clr_text, fontsize=11, fontweight="bold")
        ax.tick_params(colors=self.clr_text)
        ax.set_xlabel("Dose (mg/L)", color=self.clr_muted)
        ax.set_ylabel("Turbidity (NTU)", color=self.clr_muted)
        ax.grid(True, color="#2d3142", linestyle=":")
        
        ax.text(opt["Dose"] + 1, opt["Turbidity"] + 2, f"Optimal Dose: {opt['Dose']} mg/L", color=self.clr_success, fontweight="bold")
        
        canvas = FigureCanvasTkAgg(fig, master=self.display_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    # -------------------------------------------------------------
    # BREAKPOINT DISINFECTION WORKSPACE
    # -------------------------------------------------------------
    def draw_chlorination_view(self):
        self.setup_module_base_layout("Breakpoint Chlorination Curve Simulator")
        
        # Added file ingestion support here to match your Jar Test pipeline capabilities
        upload_btn = tk.Button(self.ctrl_panel, text="[Open] Auto-Ingest Lab Logsheet", bg="#242938", fg=self.clr_accent, font=("Segoe UI", 9, "bold"), bd=0, pady=8, command=self.handle_chlorine_file_import)
        upload_btn.pack(fill="x", pady=(10, 15))
        
        tk.Label(self.ctrl_panel, text="Chlorine Dose Applied (mg/L):", bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.cl_dose = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text, bd=1, insertbackground="white")
        self.cl_dose.pack(fill="x", pady=(2, 10))
        self.cl_dose.insert(0, "0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0")
        
        tk.Label(self.ctrl_panel, text="Measured Total Residual Cl (mg/L):", bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.cl_res = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text, bd=1, insertbackground="white")
        self.cl_res.pack(fill="x", pady=(2, 20))
        self.cl_res.insert(0, "0.4, 0.8, 1.1, 0.6, 0.2, 0.5, 1.0, 1.5")
        
        run_btn = tk.Button(self.ctrl_panel, text="[Run] Plot Disinfection Kinetics", bg=self.clr_accent, fg=self.clr_sidebar, font=("Segoe UI", 10, "bold"), bd=0, pady=8, command=self.execute_chlorine_math)
        run_btn.pack(fill="x")

    def handle_chlorine_file_import(self):
        df = self.import_laboratory_file()
        if df is not None and len(df) >= 2:
            self.cl_dose.delete(0, tk.END)
            self.cl_res.delete(0, tk.END)
            self.cl_dose.insert(0, ", ".join([str(x) for x in df.iloc[:, 0].tolist()]))
            self.cl_res.insert(0, ", ".join([str(y) for y in df.iloc[:, 1].tolist()]))

    def execute_chlorine_math(self):
        try:
            x = [float(i.strip()) for i in self.cl_dose.get().split(",")]
            y = [float(i.strip()) for i in self.cl_res.get().split(",")]
        except Exception:
            messagebox.showerror("Error", "Check numeric parameter fields.")
            return
            
        self.clear_display_canvas()
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=self.clr_card)
        ax.set_facecolor(self.clr_card)
        ax.plot(x, y, marker="s", color="#ffb703", linewidth=2, label="Total Residual Chlorine")
        
        breakpoint_idx = y.index(min(y[2:6])) if len(y) > 5 else 4
        ax.axvline(x=x[breakpoint_idx], color="#ff0055", linestyle=":", label=f"Breakpoint ({x[breakpoint_idx]} mg/L)")
        
        ax.set_title("Classical Breakpoint Chemistry Profile", color=self.clr_text, fontsize=11, fontweight="bold")
        ax.tick_params(colors=self.clr_text)
        ax.grid(True, color="#2d3142", linestyle=":")
        ax.legend(facecolor=self.clr_sidebar, labelcolor=self.clr_text)
        
        canvas = FigureCanvasTkAgg(fig, master=self.display_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    # -------------------------------------------------------------
    # GRAVIMETRIC ANALYSIS WORKSPACE (TSS)
    # -------------------------------------------------------------
    def draw_suspended_solids_view(self):
        self.setup_module_base_layout("Gravimetric Analysis: TSS & TDS Calculations")
        
        tk.Label(self.ctrl_panel, text="Sample Volume (mL):", bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.ss_vol = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text, bd=1, insertbackground="white")
        self.ss_vol.pack(fill="x", pady=(2, 10))
        self.ss_vol.insert(0, "100")
        
        tk.Label(self.ctrl_panel, text="Clean Filter Weight (g):", bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.ss_w1 = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text, bd=1, insertbackground="white")
        self.ss_w1.pack(fill="x", pady=(2, 10))
        self.ss_w1.insert(0, "1.2435")
        
        tk.Label(self.ctrl_panel, text="Dried Filter + Residue Weight (g):", bg=self.clr_card, fg=self.clr_text).pack(anchor="w")
        self.ss_w2 = tk.Entry(self.ctrl_panel, bg=self.clr_bg, fg=self.clr_text, bd=1, insertbackground="white")
        self.ss_w2.pack(fill="x", pady=(2, 20))
        self.ss_w2.insert(0, "1.2488")
        
        run_btn = tk.Button(self.ctrl_panel, text="[Run] Compute TSS Metrics", bg=self.clr_success, fg=self.clr_sidebar, font=("Segoe UI", 10, "bold"), bd=0, pady=8, command=self.execute_solids_math)
        run_btn.pack(fill="x")

    def execute_solids_math(self):
        try:
            vol = float(self.ss_vol.get()) / 1000.0
            w1 = float(self.ss_w1.get())
            w2 = float(self.ss_w2.get())
            tss_mg_l = ((w2 - w1) * 1000000) / (vol * 1000)
        except Exception:
            messagebox.showerror("Error", "Review numerical mass entries.")
            return
            
        self.clear_display_canvas()
        out_lbl = tk.Label(self.display_panel, text=f"Total Suspended Solids (TSS):\n\n{tss_mg_l:.2f} mg/L", bg=self.clr_card, fg=self.clr_success, font=("Consolas", 18, "bold"))
        out_lbl.pack(expand=True)

    # -------------------------------------------------------------
    # LAYOUT PLATFORM BOILERPLATE GENERATORS
    # -------------------------------------------------------------
    def setup_module_base_layout(self, title_text):
        header = tk.Label(self.current_frame, text=title_text, bg=self.clr_bg, fg=self.clr_text, font=("Segoe UI", 14, "bold"))
        header.pack(anchor="w", pady=(0, 15))
        
        self.split_pane = tk.Frame(self.current_frame, bg=self.clr_bg)
        self.split_pane.pack(expand=True, fill="both")
        
        self.ctrl_panel = tk.Frame(self.split_pane, bg=self.clr_card, width=340, padx=20, pady=25)
        self.ctrl_panel.pack(side="left", fill="y", padx=(0, 20))
        self.ctrl_panel.pack_propagate(False)
        
        self.display_panel = tk.Frame(self.split_pane, bg=self.clr_card, bd=0)
        self.display_panel.pack(side="right", expand=True, fill="both")

    def clear_display_canvas(self):
        for widget in self.display_panel.winfo_children():
            widget.destroy()

# -------------------------------------------------------------
# CORE ENTRY ROUTINE RUN METHOD
# -------------------------------------------------------------
if __name__ == "__main__":
    app = EliteWaterSuite()
    app.mainloop()
