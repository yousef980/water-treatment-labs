from .base import BaseModule
from aqualabs.core.calculator import calculate_tss
from aqualabs.ui.theme import style_matplotlib_axes, COLORS
import tkinter as tk
import matplotlib.pyplot as plt

class SuspendedSolidsModule(BaseModule):
    """Lab 03: Total Suspended Solids (TSS) & VSS"""
    
    def get_metadata(self):
        return {
            'title': '03 · Total Suspended Solids (TSS) & VSS',
            'number': 3,
            'description': 'Calculate TSS, VSS and FSS via gravimetric analysis',
            'icon_color': COLORS['green']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Volume Filtered (mL)")
        self.vol_entry = self._entry(ctrl_frame, "100")
        
        self._label(ctrl_frame, "Filter Paper Weight (g) [m0]")
        self.m0_entry = self._entry(ctrl_frame, "0.1250")
        
        self._label(ctrl_frame, "Weight after 105°C (g) [m1]")
        self.m1_entry = self._entry(ctrl_frame, "0.1374")
        
        self._label(ctrl_frame, "Weight after 550°C (g) [m2] (Optional)")
        self.m2_entry = self._entry(ctrl_frame, "0.1292")
        
        self._button(ctrl_frame, "▶ Calculate TSS & VSS", COLORS['green'], self.run_analysis)
    
    def run_analysis(self):
        try:
            vol = float(self.vol_entry.get().strip())
            m0 = float(self.m0_entry.get().strip())
            m1 = float(self.m1_entry.get().strip())
            
            m2_str = self.m2_entry.get().strip()
            m2 = float(m2_str) if m2_str else None
        except ValueError:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': 'Please ensure all required inputs are valid numbers.'}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        tss, vss, fss, has_vss = calculate_tss(vol, m0, m1, m2)
        
        figs = []
        details = f"Total Suspended Solids (TSS): {tss:.2f} mg/L\n\n"
        
        if has_vss:
            details += f"Volatile Suspended Solids (VSS): {vss:.2f} mg/L ({vss/tss*100:.1f}%)\n"
            details += f"Fixed Suspended Solids (FSS): {fss:.2f} mg/L ({fss/tss*100:.1f}%)"
            
            fig, ax = plt.subplots(figsize=(5, 3), facecolor=COLORS['card'])
            style_matplotlib_axes(ax, title="Solids Composition")
            ax.pie([vss, fss], labels=["Volatile (Organic)", "Fixed (Inorganic)"], 
                   colors=[COLORS["amber"], COLORS["sub"]], autopct='%1.1f%%', 
                   textprops={'color': COLORS["bg"], 'weight': 'bold'})
            plt.tight_layout()
            figs.append(fig)
        else:
            details += "VSS not calculated (no 550°C data provided)"
            
        self.current_result = {
            'status': 'success',
            'title': 'Gravimetric Analysis Results',
            'details': details,
            'figures': figs,
            'stats': {'tss': tss, 'vss': vss, 'fss': fss}
        }
        
        if self.frame:
            self.render_result(self.frame)
            
        return self.current_result
