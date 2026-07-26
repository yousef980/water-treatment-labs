from .base import BaseModule
from aqualabs.core.calculator import calculate_lime_soda_dose
from aqualabs.ui.theme import style_matplotlib_axes, COLORS
import tkinter as tk
import matplotlib.pyplot as plt

class LimeSodaModule(BaseModule):
    """Lab 06: Lime-Soda Chemical Softening"""
    
    def get_metadata(self):
        return {
            'title': '06 · Lime-Soda Chemical Softening',
            'number': 6,
            'description': 'Calculate reagent doses for water softening',
            'icon_color': COLORS['green']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Calcium Hardness (Ca²⁺) as mg/L CaCO3")
        self.ca_entry = self._entry(ctrl_frame, "200")
        
        self._label(ctrl_frame, "Magnesium Hardness (Mg²⁺) as mg/L CaCO3")
        self.mg_entry = self._entry(ctrl_frame, "120")
        
        self._label(ctrl_frame, "Total Alkalinity (TAC) as mg/L CaCO3")
        self.tac_entry = self._entry(ctrl_frame, "200")
        
        self._label(ctrl_frame, "CO2 concentration (mg/L)")
        self.co2_entry = self._entry(ctrl_frame, "15")
        
        self._label(ctrl_frame, "Lime Purity (%)")
        self.pur_entry = self._entry(ctrl_frame, "85")
        
        self._button(ctrl_frame, "▶ Calculate Reagent Doses", COLORS['green'], self.run_analysis)
    
    def run_analysis(self):
        try:
            ca = float(self.ca_entry.get().strip())
            mg = float(self.mg_entry.get().strip())
            tac = float(self.tac_entry.get().strip())
            co2 = float(self.co2_entry.get().strip())
            purity = float(self.pur_entry.get().strip())
        except ValueError:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': 'Please ensure inputs are valid numbers.'}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        lime_pure, lime_comm, soda = calculate_lime_soda_dose(ca, mg, tac, co2, purity)
        
        details = f"Lime (CaO) Pure Dose: {lime_pure:.1f} mg/L\n"
        details += f"Commercial Lime Dose ({purity}%): {lime_comm:.1f} mg/L\n"
        details += f"Soda (Na₂CO₃) Dose: {soda:.1f} mg/L"
        
        fig, ax = plt.subplots(figsize=(6, 3), facecolor=COLORS['card'])
        style_matplotlib_axes(ax, ylabel="Dose (mg/L)", title="Softening Reagents Required")
        ax.bar(["Commercial Lime", "Soda Ash"], [lime_comm, soda], color=[COLORS["green"], COLORS["amber"]], zorder=3)
        plt.tight_layout()
        
        self.current_result = {
            'status': 'success',
            'title': 'Barometric Dose Requirements',
            'details': details,
            'figures': [fig]
        }
        
        if self.frame: self.render_result(self.frame)
        return self.current_result
