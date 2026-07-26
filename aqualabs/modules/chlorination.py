from .base import BaseModule
from aqualabs.core.calculator import identify_breakpoint
from aqualabs.core.validator import ValidationError, InputValidator
from aqualabs.ui.theme import style_matplotlib_axes, annotate_point, COLORS
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd

class ChlorinationModule(BaseModule):
    """Lab 02: Breakpoint Chlorination"""
    
    def get_metadata(self):
        return {
            'title': '02 · Breakpoint Chlorination',
            'number': 2,
            'description': 'Analyze chlorine breakpoint and CT value',
            'icon_color': COLORS['amber']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Contact Time (min)")
        self.ct_entry = self._entry(ctrl_frame, "30")
        
        self._label(ctrl_frame, "Temperature (°C)")
        self.temp_entry = self._entry(ctrl_frame, "20")
        
        self._label(ctrl_frame, "Chlorine Dose (mg/L)")
        self.dose_entry = self._entry(ctrl_frame, "0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0")
        
        self._label(ctrl_frame, "Total Residual Cl (mg/L)")
        self.residual_entry = self._entry(ctrl_frame, "0.4, 0.8, 1.1, 0.6, 0.2, 0.5, 1.0, 1.5")
        
        self._button(ctrl_frame, "▶ Analyze Breakpoint & CT", COLORS['amber'], self.run_analysis)
    
    def run_analysis(self):
        try:
            ct_min = float(self.ct_entry.get().strip())
            temp = float(self.temp_entry.get().strip())
            doses = InputValidator.parse_csv_input(self.dose_entry.get())
            residuals = InputValidator.parse_csv_input(self.residual_entry.get(), len(doses))
        except (ValidationError, ValueError) as e:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': str(e)}
            if self.frame: self.render_result(self.frame)
            return self.current_result
        
        try:
            bp_dose, bp_res = identify_breakpoint(doses, residuals)
        except ValueError as e:
            self.current_result = {'status': 'error', 'title': 'Analysis Error', 'details': str(e)}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        self.current_df = pd.DataFrame({'Dose': doses, 'Residual': residuals})
        
        ct_value = bp_res * ct_min
        
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['card'])
        style_matplotlib_axes(ax, xlabel='Chlorine dose (mg/L)', ylabel='Total residual Cl (mg/L)', title='Breakpoint Curve & Chloramine Destruction')
        ax.plot(doses, residuals, color=COLORS['amber'], linewidth=2.5, marker='s', markersize=6)
        
        bp_idx = doses.index(bp_dose)
        max_idx = residuals.index(max(residuals[:bp_idx]))
        
        ax.axvspan(0, doses[max_idx], alpha=0.1, color=COLORS['green'], label='Combined Cl Formation')
        ax.axvspan(doses[max_idx], bp_dose, alpha=0.1, color=COLORS['red'], label='Chloramine Destruction')
        ax.axvspan(bp_dose, max(doses), alpha=0.1, color=COLORS['accent'], label='Free Chlorine Residue')
        
        annotate_point(ax, bp_dose, bp_res, f'Breakpoint\n{bp_dose} mg/L', COLORS['red'])
        ax.legend(facecolor=COLORS['surface'], labelcolor=COLORS['text'], fontsize=8)
        plt.tight_layout()
        
        self.current_result = {
            'status': 'success',
            'title': f'Breakpoint Detected at Dose: {bp_dose} mg/L',
            'details': f'Chlorine Demand at BP: {bp_dose - bp_res:.2f} mg/L\nCalculated CT Value: {ct_value:.2f} mg·min/L (at {temp}°C)',
            'figures': [fig],
            'stats': {'bp_dose': bp_dose, 'bp_res': bp_res, 'ct_value': ct_value}
        }
        
        if self.frame:
            self.render_result(self.frame)
            
        return self.current_result
