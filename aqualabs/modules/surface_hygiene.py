from .base import BaseModule
from aqualabs.core.calculator import check_hygiene_compliance
from aqualabs.core.validator import ValidationError, InputValidator
from aqualabs.ui.theme import style_matplotlib_axes, COLORS
import tkinter as tk
import matplotlib.pyplot as plt

class SurfaceHygieneModule(BaseModule):
    """Lab 08: Surface Hygiene"""
    
    def get_metadata(self):
        return {
            'title': '08 · Surface Hygiene',
            'number': 8,
            'description': 'Assess surface swab hygiene compliance',
            'icon_color': COLORS['purple']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Surfaces Swabbed")
        self.lbl_entry = self._entry(ctrl_frame, "Bench, Tap, Floor")
        
        self._label(ctrl_frame, "CFU Count (Total)")
        self.cfu_entry = self._entry(ctrl_frame, "120, 45, 800")
        
        self._label(ctrl_frame, "Area Swabbed (cm²)")
        self.area_entry = self._entry(ctrl_frame, "100, 50, 100")
        
        self._label(ctrl_frame, "Facility Type (ISO Limit)")
        self.fac_var = tk.StringVar(value="Food Prep (Limit: 5 CFU/cm²)")
        tk.OptionMenu(ctrl_frame, self.fac_var, "Food Prep (Limit: 5 CFU/cm²)", "General Lab (Limit: 50 CFU/cm²)").pack(fill='x', pady=(0, 10))
        
        self._button(ctrl_frame, "▶ Analyse Hygiene Compliance", COLORS['purple'], self.run_analysis)
    
    def run_analysis(self):
        try:
            lbls = [v.strip() for v in self.lbl_entry.get().split(",")]
            cfus = InputValidator.parse_csv_input(self.cfu_entry.get(), len(lbls))
            areas = InputValidator.parse_csv_input(self.area_entry.get(), len(lbls))
        except ValidationError as e:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': str(e)}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        limit = 5.0 if "Food" in self.fac_var.get() else 50.0
        cfu_cm2 = check_hygiene_compliance(cfus, areas, limit)
        
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['card'])
        style_matplotlib_axes(ax, ylabel="CFU / cm²", title=f"Surface Hygiene Validation ({self.fac_var.get()})")
        
        colors = [COLORS["green"] if val <= limit else COLORS["red"] for val in cfu_cm2]
        bars = ax.bar(lbls, cfu_cm2, color=colors, zorder=3)
        ax.axhline(limit, color=COLORS["amber"], linestyle="--", linewidth=2, label=f"Limit: {limit} CFU/cm²")
        
        for bar, val in zip(bars, cfu_cm2):
            ax.text(bar.get_x() + bar.get_width()/2, val + (max(cfu_cm2)*0.02), f"{val:.1f}", ha="center", color=COLORS["text"], fontweight="bold")
            
        ax.legend(facecolor=COLORS['surface'], labelcolor=COLORS['text'])
        plt.tight_layout()
        
        self.current_result = {
            'status': 'success',
            'title': 'Surface Hygiene Analysis',
            'details': 'Compliance evaluated for specified surfaces.',
            'figures': [fig]
        }
        
        if self.frame: self.render_result(self.frame)
        return self.current_result
