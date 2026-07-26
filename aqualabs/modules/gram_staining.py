from .base import BaseModule
from aqualabs.core.calculator import identify_gram_bacteria
from aqualabs.ui.theme import COLORS
import tkinter as tk

class GramStainingModule(BaseModule):
    """Lab 07: Gram Staining & Morphology"""
    
    def get_metadata(self):
        return {
            'title': '07 · Gram Staining & Identification',
            'number': 7,
            'description': 'Identify pathogen group by morphology and staining',
            'icon_color': COLORS['amber']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Sample ID")
        self.id_entry = self._entry(ctrl_frame, "Isolate_A")
        
        self._label(ctrl_frame, "Gram Reaction")
        self.gram_var = tk.StringVar(value="Gram-positive (+)")
        tk.OptionMenu(ctrl_frame, self.gram_var, "Gram-positive (+)", "Gram-negative (-)").pack(fill='x', pady=(0, 10))
        
        self._label(ctrl_frame, "Morphology / Shape")
        self.morph_var = tk.StringVar(value="Cocci (Spherical)")
        tk.OptionMenu(ctrl_frame, self.morph_var, "Cocci (Spherical)", "Bacilli (Rods)", "Vibrio (Curved)", "Spirilla").pack(fill='x', pady=(0, 10))
        
        self._label(ctrl_frame, "Arrangement")
        self.arr_var = tk.StringVar(value="Pairs/Chains (Strepto-)")
        tk.OptionMenu(ctrl_frame, self.arr_var, "Pairs/Chains (Strepto-)", "Clusters (Staphylo-)", "Single/Random").pack(fill='x', pady=(0, 10))
        
        self._label(ctrl_frame, "Endospores Present?")
        self.spore_var = tk.StringVar(value="No")
        tk.OptionMenu(ctrl_frame, self.spore_var, "No", "Yes").pack(fill='x', pady=(0, 10))
        
        self._button(ctrl_frame, "▶ Identify Pathogen Group", COLORS['amber'], self.run_analysis)
    
    def run_analysis(self):
        eid = self.id_entry.get().strip()
        is_gp = "+" in self.gram_var.get()
        shape = self.morph_var.get()
        arr = self.arr_var.get()
        spores = self.spore_var.get() == "Yes"
        
        genus, desc = identify_gram_bacteria(is_gp, shape, arr, spores)
        
        status_color = "success" if is_gp else "error"
        title = f"Microbiological Report: {eid}\n{self.gram_var.get()}"
        
        details = f"Morphology: {shape} in {arr}\n"
        if spores:
            details += "[Endospores Confirmed]\n"
            
        details += f"\nProbable Genus Classification:\n{genus}"
        if desc:
            details += f"\n\n{desc}"
            
        self.current_result = {
            'status': status_color,
            'title': title,
            'details': details,
            'figures': []
        }
        
        if self.frame: self.render_result(self.frame)
        return self.current_result
