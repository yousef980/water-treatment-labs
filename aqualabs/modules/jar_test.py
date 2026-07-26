from .base import BaseModule
from aqualabs.core.calculator import calculate_turbidity_removal
from aqualabs.core.validator import ValidationError, InputValidator
from aqualabs.ui.theme import style_matplotlib_axes, annotate_point, COLORS
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd

class JarTestModule(BaseModule):
    """Lab 01: Jar Test - Coagulation & Flocculation"""
    
    def get_metadata(self):
        return {
            'title': '01 · Coagulation & Flocculation — Jar Test',
            'number': 1,
            'description': 'Optimize coagulant dosage for turbidity removal',
            'icon_color': COLORS['accent']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Coagulant dose (mg/L)")
        self.dose_entry = self._entry(ctrl_frame, "10, 20, 30, 40, 50, 60")
        
        self._label(ctrl_frame, "Residual turbidity (NTU)")
        self.turbidity_entry = self._entry(ctrl_frame, "14.2, 8.5, 1.8, 4.3, 9.1, 15.4")
        
        self._label(ctrl_frame, "Coagulant Type")
        self.coagulant_var = tk.StringVar(value="Aluminum Sulfate")
        tk.OptionMenu(ctrl_frame, self.coagulant_var, "Aluminum Sulfate", "Ferric Chloride", "PAC", "Ferrous Sulfate").pack(fill='x', pady=(0, 10))
        
        self._button(ctrl_frame, "▶ Run Analysis", COLORS['green'], self.run_analysis)
    
    def run_analysis(self):
        try:
            doses = InputValidator.parse_csv_input(self.dose_entry.get())
            turbidities = InputValidator.parse_csv_input(self.turbidity_entry.get(), len(doses))
        except ValidationError as e:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': str(e)}
            self.render_result(self.frame) # We need self.frame in render_result context but the abstract method doesn't take disp_frame, wait... 
            # Actually, the base class run_analysis doesn't render, it just returns a dict!
            return self.current_result
        
        opt_dose, opt_turb = calculate_turbidity_removal(doses, turbidities)
        self.current_df = pd.DataFrame({'Dose': doses, 'Turbidity': turbidities})
        
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['card'])
        style_matplotlib_axes(ax, xlabel='Coagulant Dose (mg/L)', ylabel='Residual Turbidity (NTU)', title='Turbidity Removal Optimization')
        ax.plot(doses, turbidities, 'o-', color=COLORS['accent'], linewidth=2.5, markersize=6)
        annotate_point(ax, opt_dose, opt_turb, f'Optimal\n{opt_dose} mg/L', COLORS['green'])
        ax.legend(facecolor=COLORS['surface'], labelcolor=COLORS['text'], fontsize=8)
        plt.tight_layout()
        
        self.current_result = {
            'status': 'success',
            'title': f'Optimal Dose: {opt_dose} mg/L',
            'details': f'Residual Turbidity: {opt_turb} NTU',
            'figures': [fig],
            'stats': {'num_points': len(doses), 'dose_range': f'{min(doses)}-{max(doses)} mg/L'}
        }
        
        if self.frame:
            self.render_result(self.frame)
            
        return self.current_result
