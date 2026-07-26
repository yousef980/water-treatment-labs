from .base import BaseModule
from aqualabs.core.calculator import check_potability_status
from aqualabs.core.validator import ValidationError, InputValidator
from aqualabs.ui.theme import style_matplotlib_axes, COLORS
import tkinter as tk
import matplotlib.pyplot as plt

class WaterQualityModule(BaseModule):
    """Lab 09: Biological Water Quality"""
    
    def get_metadata(self):
        return {
            'title': '09 · Biological Water Quality',
            'number': 9,
            'description': 'Assess microbiological potability standards',
            'icon_color': COLORS['red']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Sample IDs")
        self.id_entry = self._entry(ctrl_frame, "S1, S2, S3")
        
        self._label(ctrl_frame, "Total Coliforms (CFU/100mL)")
        self.tc_entry = self._entry(ctrl_frame, "0, 12, 5")
        
        self._label(ctrl_frame, "Fecal Coliforms/E.coli (CFU/100mL)")
        self.fc_entry = self._entry(ctrl_frame, "0, 0, 2")
        
        self._label(ctrl_frame, "Enterococci (CFU/100mL)")
        self.ent_entry = self._entry(ctrl_frame, "0, 0, 0")
        
        self._label(ctrl_frame, "Standard Assessed Against")
        self.std_var = tk.StringVar(value="Drinking Water (WHO)")
        tk.OptionMenu(ctrl_frame, self.std_var, "Drinking Water (WHO)", "Recreational/Bathing Water").pack(fill='x', pady=(0, 10))
        
        self._button(ctrl_frame, "▶ Assess Potability / Quality", COLORS['red'], self.run_analysis)
    
    def run_analysis(self):
        try:
            ids = [v.strip() for v in self.id_entry.get().split(",")]
            tc = InputValidator.parse_csv_input(self.tc_entry.get(), len(ids))
            fc = InputValidator.parse_csv_input(self.fc_entry.get(), len(ids))
            ent = InputValidator.parse_csv_input(self.ent_entry.get(), len(ids))
        except ValidationError as e:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': str(e)}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        is_drinking = "Drinking" in self.std_var.get()
        results, overall = check_potability_status(tc, fc, ent, is_drinking)
        
        status_color = "success" if overall else "error"
        title = "ALL SAMPLES COMPLIANT" if overall else "WARNING: NON-COMPLIANT SAMPLES DETECTED"
        
        fig, axes = plt.subplots(1, 3, figsize=(10, 3.5), facecolor=COLORS['card'])
        
        style_matplotlib_axes(axes[0], title="Total Coliforms")
        axes[0].bar(ids, tc, color=[COLORS["green"] if (v==0 if is_drinking else True) else COLORS["red"] for v in tc])
        
        style_matplotlib_axes(axes[1], title="Fecal Coliforms")
        axes[1].bar(ids, fc, color=[COLORS["green"] if (v==0 if is_drinking else v<=200) else COLORS["red"] for v in fc])
        if not is_drinking: axes[1].axhline(200, color=COLORS["amber"], linestyle="--")
        
        style_matplotlib_axes(axes[2], title="Enterococci")
        axes[2].bar(ids, ent, color=[COLORS["green"] if (v==0 if is_drinking else v<=35) else COLORS["red"] for v in ent])
        if not is_drinking: axes[2].axhline(35, color=COLORS["amber"], linestyle="--")
        
        plt.tight_layout()
        
        self.current_result = {
            'status': status_color,
            'title': title,
            'details': f"Standard: {self.std_var.get()}",
            'figures': [fig]
        }
        
        if self.frame: self.render_result(self.frame)
        return self.current_result
