import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from .base import BaseModule
from aqualabs.core.validator import ValidationError, InputValidator
from aqualabs.ui.theme import style_matplotlib_axes, COLORS

# Import from utils (ensure sys.path or relative path works, we'll use absolute)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.analysis_tools import fit_langmuir, fit_freundlich

class NitrateAdsorptionModule(BaseModule):
    """Lab 05: Nitrate Adsorption Kinetics & Isotherms"""
    
    def get_metadata(self):
        return {
            'title': '05 · Nitrate Adsorption Kinetics',
            'number': 5,
            'description': 'Model adsorption kinetics and equilibrium isotherms',
            'icon_color': COLORS['accent']
        }
    
    def build_controls(self, ctrl_frame):
        self._label(ctrl_frame, "Time t (min) [For Kinetics]")
        self.t_entry = self._entry(ctrl_frame, "10, 20, 30, 45, 60, 90, 120")
        
        self._label(ctrl_frame, "Adsorbed qt (mg/g) [For Kinetics]")
        self.qt_entry = self._entry(ctrl_frame, "0.4, 0.65, 0.82, 0.95, 1.05, 1.15, 1.20")
        
        self._button(ctrl_frame, "▶ Analyze Kinetics", COLORS['accent'], self.run_kinetics)
        
        tk.Frame(ctrl_frame, height=2, bg=COLORS['surface']).pack(fill="x", pady=10)
        
        self._label(ctrl_frame, "Equilibrium Ce (mg/L) [For Isotherms]")
        self.ce_entry = self._entry(ctrl_frame, "0.82, 1.54, 2.91, 4.63, 6.78")
        
        self._label(ctrl_frame, "Equilibrium qe (mg/g) [For Isotherms]")
        self.qe_entry = self._entry(ctrl_frame, "0.13, 0.23, 0.40, 0.57, 0.74")
        
        self._button(ctrl_frame, "▶ Analyze Isotherms", COLORS['green'], self.run_analysis)
        
    def run_kinetics(self):
        try:
            t = np.array(InputValidator.parse_csv_input(self.t_entry.get()))
            qt = np.array(InputValidator.parse_csv_input(self.qt_entry.get(), len(t)))
        except ValidationError as e:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': str(e)}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        qe_exp = qt.max()
        valid = qt < qe_exp
        t_valid = t[valid]
        qt_valid = qt[valid]
        
        if len(t_valid) > 2:
            y_pfo = np.log(qe_exp - qt_valid)
            sl_pfo, ic_pfo = np.polyfit(t_valid, y_pfo, 1)
            R2_PFO = 1 - np.sum((y_pfo - (sl_pfo*t_valid+ic_pfo))**2) / np.sum((y_pfo - y_pfo.mean())**2)
            k1 = -sl_pfo
        else:
            R2_PFO, k1, y_pfo, sl_pfo, ic_pfo = 0, 0, [], 0, 0
            
        y_pso = t / qt
        sl_pso, ic_pso = np.polyfit(t, y_pso, 1)
        R2_PSO = 1 - np.sum((y_pso - (sl_pso*t+ic_pso))**2) / np.sum((y_pso - y_pso.mean())**2)
        qe_calc = 1 / sl_pso
        k2 = 1 / (ic_pso * (qe_calc**2))
        
        best = "Pseudo-Second Order" if R2_PSO > R2_PFO else "Pseudo-First Order"
        details = f"PFO: R²={R2_PFO:.4f} | k1={k1:.4f} min⁻¹\n"
        details += f"PSO: R²={R2_PSO:.4f} | k2={k2:.4f} g/mg·min | qe={qe_calc:.2f} mg/g"
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5), facecolor=COLORS['card'])
        if len(t_valid) > 2:
            style_matplotlib_axes(ax1, xlabel="Time (min)", ylabel="ln(qe - qt)", title="Pseudo-First Order")
            ax1.scatter(t_valid, y_pfo, color=COLORS["accent"])
            ax1.plot(t_valid, sl_pfo*t_valid + ic_pfo, color=COLORS["green"], linestyle="--")
            
        style_matplotlib_axes(ax2, xlabel="Time (min)", ylabel="t/qt", title="Pseudo-Second Order")
        ax2.scatter(t, y_pso, color=COLORS["amber"])
        ax2.plot(t, sl_pso*t + ic_pso, color=COLORS["red"], linestyle="--")
        plt.tight_layout()
        
        self.current_result = {
            'status': 'success',
            'title': f'Best Kinetic Fit: {best}',
            'details': details,
            'figures': [fig]
        }
        
        if self.frame: self.render_result(self.frame)
        return self.current_result
        
    def run_analysis(self):
        # By default run isotherms as it satisfies the ABC requirement and the primary inputs Ce, qe
        try:
            ce = np.array(InputValidator.parse_csv_input(self.ce_entry.get()))
            qe = np.array(InputValidator.parse_csv_input(self.qe_entry.get(), len(ce)))
        except ValidationError as e:
            self.current_result = {'status': 'error', 'title': 'Invalid Input', 'details': str(e)}
            if self.frame: self.render_result(self.frame)
            return self.current_result
            
        qmax, b, r2_langmuir = fit_langmuir(ce, qe)
        Kf, n, r2_freundlich = fit_freundlich(ce, qe)
        
        best = "Langmuir" if r2_langmuir > r2_freundlich else "Freundlich"
        details = f"Langmuir: R²={r2_langmuir:.4f} | qmax={qmax:.2f} mg/g | KL={b:.3f} L/mg\n"
        details += f"Freundlich: R²={r2_freundlich:.4f} | Kf={Kf:.2f} | n={n:.2f}"
        
        y_L = ce / qe
        sl_L, ic_L = np.polyfit(ce, y_L, 1)
        
        lce, lqe = np.log(ce), np.log(qe)
        sl_F, ic_F = np.polyfit(lce, lqe, 1)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5), facecolor=COLORS['card'])
        style_matplotlib_axes(ax1, xlabel="Ce", ylabel="Ce / qe", title="Langmuir")
        ax1.scatter(ce, y_L, color=COLORS["accent"])
        ax1.plot(ce, sl_L*ce + ic_L, color=COLORS["green"], linestyle="--")
        
        style_matplotlib_axes(ax2, xlabel="ln(Ce)", ylabel="ln(qe)", title="Freundlich")
        ax2.scatter(lce, lqe, color=COLORS["amber"])
        ax2.plot(lce, sl_F*lce + ic_F, color=COLORS["red"], linestyle="--")
        plt.tight_layout()
        
        self.current_result = {
            'status': 'success',
            'title': f'Best Isotherm Fit: {best}',
            'details': details,
            'figures': [fig]
        }
        
        if self.frame: self.render_result(self.frame)
        return self.current_result
