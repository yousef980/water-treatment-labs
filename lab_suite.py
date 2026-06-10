import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- UI POLISH: Set Dark Mode and Accent Color ---
ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

class LabSuiteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Environmental Engineering Lab Suite v1.1")
        self.geometry("900x650")
        
        # Header Label
        self.header = ctk.CTkLabel(self, text="Water Treatment & Microbiology Analytics", font=ctk.CTkFont(size=20, weight="bold"))
        self.header.pack(pady=(20, 10))

        # Create Modern Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill='both', padx=20, pady=(0, 20))
        
        # Add Tabs
        self.tab_jar = self.tabview.add("🧪 Mod 1: Jar Test Optimizer")
        self.tab_micro = self.tabview.add("🧫 Mod 9: Microbio CFU Calc")
        
        self.build_jar_test_tab()
        self.build_microbiology_tab()

    # ==========================================
    # MODULE 1: JAR TEST BUILDER
    # ==========================================
    def build_jar_test_tab(self):
        # Input Frame (Left Side)
        input_frame = ctk.CTkFrame(self.tab_jar)
        input_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(input_frame, text="Data Entry (6 Beakers)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=10)
        ctk.CTkLabel(input_frame, text="Dose (mg/L)").grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(input_frame, text="Turbidity (NTU)").grid(row=1, column=2, padx=5, pady=5)
        
        self.jar_inputs = []
        for i in range(6):
            ctk.CTkLabel(input_frame, text=f"B{i+1}:").grid(row=i+2, column=0, padx=10, pady=5)
            dose_entry = ctk.CTkEntry(input_frame, width=80)
            dose_entry.grid(row=i+2, column=1, padx=5, pady=5)
            turb_entry = ctk.CTkEntry(input_frame, width=80)
            turb_entry.grid(row=i+2, column=2, padx=5, pady=5)
            self.jar_inputs.append((dose_entry, turb_entry))
            
        calc_btn = ctk.CTkButton(input_frame, text="Generate Curve", command=self.calculate_jar_test, fg_color="#2FA572", hover_color="#1F7A52")
        calc_btn.grid(row=8, column=0, columnspan=3, pady=20)
        
        self.optimum_label = ctk.CTkLabel(input_frame, text="Optimum Dose: --\nMin Turbidity: --", font=ctk.CTkFont(weight="bold"))
        self.optimum_label.grid(row=9, column=0, columnspan=3, pady=10)

        # Graph Frame (Right Side)
        self.graph_frame = ctk.CTkFrame(self.tab_jar, fg_color="transparent")
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
            
            self.optimum_label.configure(text=f"🎯 Optimum Dose: {optimum['Dose']} mg/L\n📉 Min Turbidity: {optimum['Turbidity']} NTU", text_color="#2FA572")
            
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
                
            # Plotting with Dark Theme Styling
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(5, 4))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            ax.plot(df['Dose'], df['Turbidity'], marker='o', color='#2FA572', linewidth=2)
            ax.set_title('Coagulation Optimization Curve')
            ax.set_xlabel('Dose (mg/L)')
            ax.set_ylabel('Turbidity (NTU)')
            ax.grid(True, linestyle=':', alpha=0.5)
            
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except ValueError:
            messagebox.showerror("Input Error", "Please ensure all 6 beakers have valid numerical data.")

    # ==========================================
    # MODULE 9: MICROBIOLOGY BUILDER
    # ==========================================
    def build_microbiology_tab(self):
        # Center the inputs for a clean look
        frame = ctk.CTkFrame(self.tab_micro)
        frame.pack(padx=50, pady=50, fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="Tamarza Source CFU Calculator", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        input_grid = ctk.CTkFrame(frame, fg_color="transparent")
        input_grid.pack(pady=10)

        ctk.CTkLabel(input_grid, text="Colony Count (N):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.colony_entry = ctk.CTkEntry(input_grid, width=150)
        self.colony_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(input_grid, text="Volume in mL (V):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.volume_entry = ctk.CTkEntry(input_grid, width=150)
        self.volume_entry.insert(0, "0.1") 
        self.volume_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(input_grid, text="Dilution Factor:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.dilution_entry = ctk.CTkEntry(input_grid, width=150)
        self.dilution_entry.grid(row=2, column=1, padx=10, pady=10)
        
        calc_btn = ctk.CTkButton(frame, text="Calculate Biological Load", command=self.calculate_cfu)
        calc_btn.pack(pady=20)
        
        self.cfu_result_label = ctk.CTkLabel(frame, text="Result: --", font=ctk.CTkFont(size=16, weight="bold"))
        self.cfu_result_label.pack(pady=5)
        
        self.compliance_label = ctk.CTkLabel(frame, text="Status: --", font=ctk.CTkFont(size=16, weight="bold"))
        self.compliance_label.pack(pady=5)

    def calculate_cfu(self):
        try:
            n = float(self.colony_entry.get())
            v = float(self.volume_entry.get())
            d = float(self.dilution_entry.get())
            
            if v == 0 or d == 0:
                raise ValueError("Volume and Dilution cannot be zero.")
                
            cfu = n / (v * d)
            
            self.cfu_result_label.configure(text=f"Result: {cfu:.2e} CFU/mL")
            
            if cfu < 100:
                self.compliance_label.configure(text="Status: POTABLE (Pass)", text_color="#2FA572")
            else:
                self.compliance_label.configure(text="Status: NON-POTABLE (Disinfection Req.)", text_color="#FF4C4C")
                
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")

if __name__ == "__main__":
    app = LabSuiteApp()
    app.mainloop()
