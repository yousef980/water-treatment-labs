import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LabSuiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Environmental Engineering Lab Suite v1.0")
        self.root.geometry("800x600")
        
        # Create a notebook (Tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # --- TAB 1: JAR TEST ---
        self.tab_jar = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_jar, text="🧪 Mod 1: Jar Test Optimizer")
        self.build_jar_test_tab()
        
        # --- TAB 2: MICROBIOLOGY ---
        self.tab_micro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_micro, text="🧫 Mod 9: Microbio CFU Calc")
        self.build_microbiology_tab()

    # ==========================================
    # MODULE 1: JAR TEST BUILDER
    # ==========================================
    def build_jar_test_tab(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.tab_jar, text="Data Entry (6 Beakers)")
        input_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        ttk.Label(input_frame, text="Dose (mg/L)").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="Turbidity (NTU)").grid(row=0, column=2, padx=5, pady=5)
        
        self.jar_inputs = []
        for i in range(6):
            ttk.Label(input_frame, text=f"Beaker {i+1}:").grid(row=i+1, column=0, padx=5, pady=5)
            dose_entry = ttk.Entry(input_frame, width=10)
            dose_entry.grid(row=i+1, column=1, padx=5, pady=5)
            turb_entry = ttk.Entry(input_frame, width=10)
            turb_entry.grid(row=i+1, column=2, padx=5, pady=5)
            self.jar_inputs.append((dose_entry, turb_entry))
            
        calc_btn = ttk.Button(input_frame, text="Generate Optimal Curve", command=self.calculate_jar_test)
        calc_btn.grid(row=7, column=0, columnspan=3, pady=20)
        
        self.optimum_label = ttk.Label(input_frame, text="Optimum Dose: -- mg/L\nMin Turbidity: -- NTU", font=('Arial', 10, 'bold'))
        self.optimum_label.grid(row=8, column=0, columnspan=3, pady=10)

        # Graph Frame
        self.graph_frame = ttk.Frame(self.tab_jar)
        self.graph_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    def calculate_jar_test(self):
        data = []
        try:
            for i, (dose_ent, turb_ent) in enumerate(self.jar_inputs):
                dose = float(dose_ent.get())
                turb = float(turb_ent.get())
                data.append({'Dose': dose, 'Turbidity': turb})
                
            df = pd.DataFrame(data)
            optimum = df.loc[df['Turbidity'].idxmin()]
            
            self.optimum_label.config(text=f"🎯 Optimum Dose: {optimum['Dose']} mg/L\n📉 Min Turbidity: {optimum['Turbidity']} NTU")
            
            # Clear previous graph
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
                
            # Plotting inside Tkinter
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(df['Dose'], df['Turbidity'], marker='o', color='#1f77b4', linewidth=2, linestyle='-')
            ax.set_title('Coagulation Optimization Curve')
            ax.set_xlabel('Coagulant Dose (mg/L)')
            ax.set_ylabel('Residual Turbidity (NTU)')
            ax.grid(True, linestyle=':')
            
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except ValueError:
            messagebox.showerror("Input Error", "Please ensure all 6 beakers have valid numerical data.")

    # ==========================================
    # MODULE 9: MICROBIOLOGY BUILDER
    # ==========================================
    def build_microbiology_tab(self):
        frame = ttk.LabelFrame(self.tab_micro, text="CFU & Potability Calculator (Tamarza Source)")
        frame.pack(padx=20, pady=20, fill="x")
        
        ttk.Label(frame, text="Colony Count (N):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.colony_entry = ttk.Entry(frame)
        self.colony_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(frame, text="Seeded Volume in mL (V):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.volume_entry = ttk.Entry(frame)
        self.volume_entry.insert(0, "0.1") # Default value
        self.volume_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(frame, text="Dilution Factor (e.g., 0.001):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.dilution_entry = ttk.Entry(frame)
        self.dilution_entry.grid(row=2, column=1, padx=10, pady=10)
        
        calc_btn = ttk.Button(frame, text="Calculate Biological Load", command=self.calculate_cfu)
        calc_btn.grid(row=3, column=0, columnspan=2, pady=15)
        
        self.cfu_result_label = ttk.Label(frame, text="", font=('Arial', 12, 'bold'))
        self.cfu_result_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.compliance_label = ttk.Label(frame, text="", font=('Arial', 12, 'bold'))
        self.compliance_label.grid(row=5, column=0, columnspan=2, pady=5)

    def calculate_cfu(self):
        try:
            n = float(self.colony_entry.get())
            v = float(self.volume_entry.get())
            d = float(self.dilution_entry.get())
            
            if v == 0 or d == 0:
                raise ValueError("Volume and Dilution cannot be zero.")
                
            cfu = n / (v * d)
            
            # Format scientific notation beautifully
            self.cfu_result_label.config(text=f"Result: {cfu:.2e} CFU/mL")
            
            if cfu < 100:
                self.compliance_label.config(text="Status: POTABLE (Pass)", foreground="green")
            else:
                self.compliance_label.config(text="Status: NON-POTABLE (Disinfection Req.)", foreground="red")
                
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LabSuiteApp(root)
    root.mainloop()
