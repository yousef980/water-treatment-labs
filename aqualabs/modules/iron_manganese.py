from .base import BaseModule
from aqualabs.core.calculator import calculate_iron_manganese_removal
from aqualabs.ui.theme import style_matplotlib_axes, COLORS
import tkinter as tk
import matplotlib.pyplot as plt

class IronManganeseModule(BaseModule):
    """Lab 04: Iron & Manganese Removal"""
    
    def get_metadata(self):
        return {
            'title': '04 · Iron & Manganese Removal',
            'number': 4,
            'description': 'Calculate oxidant demand for metal removal',
            'icon_color': COLORS['purple']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Initial Fe²⁺ (mg/L)")
        self.fe_entry = self._entry(ctrl_frame, "2.50")
        
        self._label(ctrl_frame, "Initial Mn²⁺ (mg/L)")
        self.mn_entry = self._entry(ctrl_frame, "0.45")
        
        self._label(ctrl_frame, "Water pH & ORP (mV)")
        self.ph_orp_entry = self._entry(ctrl_frame, "7.2, 150")
        
        self._label(ctrl_frame, "Oxidant Used")
        self.ox_var = tk.StringVar(value="Chlorine (Cl2)")
        tk.OptionMenu(ctrl_frame, self.ox_var, "Chlorine (Cl2)", "KMnO4", "Ozone (O3)", "Aeration Only (O2)").pack(fill='x', pady=(0, 10))
        
        self._button(ctrl_frame, "▶ Calculate Oxidant Demand", COLORS['purple'], self.run_analysis)
    
    def run_analysis(self):
        try:
            fe = float(self.fe_entry.get().strip())
            mn = float(self.mn_entry.get().strip())
            
            ph_orp = self.ph_orp_entry.get().split(',')
            ph = float(ph_orp[0].strip())
            orp = float(ph_orp[1].strip())
            
            oxidant = self.ox_var.get()
        except ValueError:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': 'Please ensure inputs are valid numbers.'}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        try:
            fe_demand, mn_demand, total_demand = calculate_iron_manganese_removal(fe, mn, oxidant)
        except ValueError as e:
            self.current_result = {'status': 'error', 'title': 'Analysis Error', 'details': str(e)}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        warning = ""
        if oxidant == "Aeration Only (O2)":
            if ph < 7.5: warning += "⚠️ Fe oxidation by O2 is slow below pH 7.5. "
            if ph < 9.5 and mn > 0: warning += "⚠️ Mn oxidation by O2 requires pH > 9.5! "
            
        details = f"Oxidant Required: {oxidant}\n"
        details += f"Theoretical Fe Demand: {fe_demand:.2f} mg/L\n"
        details += f"Theoretical Mn Demand: {mn_demand:.2f} mg/L\n"
        details += f"Total Stoichiometric Demand: {total_demand:.2f} mg/L\n"
        
        if warning:
            details += f"\n{warning}"
            
        fig, ax = plt.subplots(figsize=(6, 3.5), facecolor=COLORS['card'])
        style_matplotlib_axes(ax, ylabel="Demand (mg/L)", title="Oxidant Consumption Breakdown")
        bars = ax.bar(["Iron (Fe)", "Manganese (Mn)"], [fe_demand, mn_demand], color=[COLORS["red"], COLORS["purple"]], zorder=3)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05, f"{height:.2f}", ha="center", color=COLORS["text"], fontweight="bold")
            
        plt.tight_layout()
        
        self.current_result = {
            'status': 'success',
            'title': 'Oxidant Demand Calculation',
            'details': details,
            'figures': [fig],
            'stats': {'total_demand': total_demand}
        }
        
        if self.frame:
            self.render_result(self.frame)
            
        return self.current_result
