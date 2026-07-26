def calculate_turbidity_removal(doses: list, turbidities: list) -> tuple:
    if not doses or not turbidities or len(doses) != len(turbidities):
        raise ValueError("Invalid doses or turbidities array.")
    idx = turbidities.index(min(turbidities))
    return doses[idx], turbidities[idx]

def identify_breakpoint(doses: list, residuals: list) -> tuple:
    if len(residuals) < 3:
        raise ValueError("Need at least 3 points to identify breakpoint.")
    # Breakpoint is local minimum after peak
    bp_idx = residuals.index(min(residuals[1:-1]))
    return doses[bp_idx], residuals[bp_idx]

def calculate_tss(volume: float, m0: float, m1: float, m2: float = None) -> tuple:
    tss = ((m1 - m0) * 1e6) / volume
    vss = 0.0
    fss = 0.0
    has_vss = False
    
    if m2 is not None:
        vss = ((m1 - m2) * 1e6) / volume
        fss = tss - vss
        has_vss = True
        
    return tss, vss, fss, has_vss

def calculate_iron_manganese_removal(fe_init: float, mn_init: float, oxidant: str) -> tuple:
    ratios = {
        "Chlorine (Cl2)": (0.64, 1.30),
        "KMnO4": (0.94, 1.92),
        "Ozone (O3)": (0.43, 0.87),
        "Aeration Only (O2)": (0.14, 0.29)
    }
    if oxidant not in ratios:
        raise ValueError("Invalid oxidant type.")
    
    fe_ratio, mn_ratio = ratios[oxidant]
    fe_demand = fe_init * fe_ratio
    mn_demand = mn_init * mn_ratio
    return fe_demand, mn_demand, fe_demand + mn_demand

def calculate_lime_soda_dose(ca: float, mg: float, tac: float, co2: float, purity: float) -> tuple:
    ca_meq = ca / 50.0
    mg_meq = mg / 50.0
    tac_meq = tac / 50.0
    co2_meq = co2 / 22.0
    
    lime_meq = co2_meq + tac_meq + mg_meq
    th_meq = ca_meq + mg_meq
    nch_meq = max(th_meq - tac_meq, 0)
    soda_meq = nch_meq
    
    lime_pure_mg = lime_meq * 28.0
    soda_pure_mg = soda_meq * 53.0
    
    commercial_lime_mg = lime_pure_mg / (purity / 100.0)
    return lime_pure_mg, commercial_lime_mg, soda_pure_mg

def identify_gram_bacteria(is_gram_positive: bool, shape: str, arr: str, spores: bool) -> tuple:
    genus = "Unknown/Unclassified"
    desc = ""
    
    if is_gram_positive:
        if "Cocci" in shape:
            if "Clusters" in arr: genus = "Staphylococcus spp."
            elif "Chains" in arr: genus = "Streptococcus / Enterococcus"
            else: genus = "Micrococcus"
        elif "Bacilli" in shape:
            if spores: genus = "Bacillus (aerobic) or Clostridium (anaerobic)"
            else: genus = "Listeria / Corynebacterium / Lactobacillus"
    else:
        if "Bacilli" in shape:
            genus = "Enterobacteriaceae (E. coli, Salmonella, Klebsiella) or Pseudomonas"
        elif "Cocci" in shape:
            genus = "Neisseria / Moraxella"
        elif "Vibrio" in shape:
            genus = "Vibrio cholerae / Campylobacter"
            
    if not is_gram_positive and spores:
        desc = "⚠️ Warning: Gram-negative bacteria typically do not form endospores. Re-evaluate stain."
        
    return genus, desc

def check_hygiene_compliance(cfus: list, areas: list, limit: float) -> list:
    return [c / a for c, a in zip(cfus, areas)]

def check_potability_status(tc: list, fc: list, ent: list, is_drinking: bool) -> tuple:
    results = []
    for t, f, e in zip(tc, fc, ent):
        if is_drinking:
            results.append(t == 0 and f == 0 and e == 0)
        else:
            results.append(f <= 200 and e <= 35)
    return results, all(results)
