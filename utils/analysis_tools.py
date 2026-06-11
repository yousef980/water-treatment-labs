"""
Shared utilities for water treatment lab analysis.
Common functions for data processing, fitting, and visualization.
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import pearsonr


def calculate_r_squared(y_true, y_pred):
    """Calculate R² coefficient of determination."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)


def langmuir_isotherm(Ce, qmax, b):
    """Langmuir adsorption isotherm model."""
    return (qmax * b * Ce) / (1 + b * Ce)


def freundlich_isotherm(Ce, Kf, n):
    """Freundlich adsorption isotherm model."""
    return Kf * (Ce ** (1 / n))


def temkin_isotherm(Ce, A_T, B_tem):
    """Temkin adsorption isotherm model."""
    return (np.log(A_T * Ce)) / B_tem


def fit_langmuir(Ce, qe):
    """
    Fit Langmuir isotherm to equilibrium data.
    Returns: qmax, b, R²
    """
    # Linear regression: Ce/qe vs Ce
    y = Ce / qe
    slope, intercept = np.polyfit(Ce, y, 1)
    
    qmax = 1 / slope
    b = 1 / (intercept * qmax)
    
    # Calculate R²
    y_pred = (qmax * b * Ce) / (1 + b * Ce)
    r2 = calculate_r_squared(qe, y_pred)
    
    return qmax, b, r2


def fit_freundlich(Ce, qe):
    """
    Fit Freundlich isotherm to equilibrium data.
    Returns: Kf, n, R²
    """
    ln_Ce = np.log(Ce)
    ln_qe = np.log(qe)
    
    slope, intercept = np.polyfit(ln_Ce, ln_qe, 1)
    
    Kf = np.exp(intercept)
    n = 1 / slope
    
    # Calculate R²
    y_pred = Kf * (Ce ** (1 / n))
    r2 = calculate_r_squared(qe, y_pred)
    
    return Kf, n, r2


def fit_temkin(Ce, qe):
    """
    Fit Temkin isotherm to equilibrium data.
    Returns: A_T, B_tem, R²
    """
    ln_Ce = np.log(Ce)
    
    slope, intercept = np.polyfit(ln_Ce, qe, 1)
    
    B_tem = slope
    A_T = np.exp(intercept / B_tem) if B_tem != 0 else 0
    
    # Calculate R²
    y_pred = (np.log(A_T * Ce)) / B_tem
    r2 = calculate_r_squared(qe, y_pred)
    
    return A_T, B_tem, r2


def determine_best_isotherm(Ce, qe):
    """
    Compare all three isotherms and return the best fit.
    Returns: dict with results for each model and the best model name
    """
    qmax, b, r2_langmuir = fit_langmuir(Ce, qe)
    Kf, n, r2_freundlich = fit_freundlich(Ce, qe)
    A_T, B_tem, r2_temkin = fit_temkin(Ce, qe)
    
    results = {
        'Langmuir': {'qmax': qmax, 'b': b, 'R2': r2_langmuir},
        'Freundlich': {'Kf': Kf, 'n': n, 'R2': r2_freundlich},
        'Temkin': {'A_T': A_T, 'B_tem': B_tem, 'R2': r2_temkin}
    }
    
    best_model = max(results, key=lambda x: results[x]['R2'])
    
    return results, best_model


def turbidity_removal_efficiency(turbidity_initial, turbidity_final):
    """Calculate turbidity removal efficiency as percentage."""
    if turbidity_initial == 0:
        return 0
    return ((turbidity_initial - turbidity_final) / turbidity_initial) * 100


def chlorine_demand(applied_dose, residual_chlorine):
    """Calculate chlorine demand from applied dose and residual."""
    return applied_dose - residual_chlorine


def check_potability_criteria(fe_concentration, mn_concentration, 
                              fe_limit=0.2, mn_limit=0.05):
    """
    Check if water meets WHO potability criteria for Fe and Mn.
    Returns: dict with compliance status
    """
    fe_compliant = fe_concentration <= fe_limit
    mn_compliant = mn_concentration <= mn_limit
    overall_compliant = fe_compliant and mn_compliant
    
    return {
        'Fe_compliant': fe_compliant,
        'Mn_compliant': mn_compliant,
        'overall_potable': overall_compliant,
        'fe_status': f'{fe_concentration:.3f} mg/L (limit: {fe_limit} mg/L)',
        'mn_status': f'{mn_concentration:.3f} mg/L (limit: {mn_limit} mg/L)'
    }


def check_coliform_potability(total_coliforms, e_coli):
    """
    Check if water meets coliform potability standards.
    WHO standard: 0 CFU/100mL for both TC and E. coli
    Returns: bool
    """
    return (total_coliforms == 0) and (e_coli == 0)
