import pytest
from aqualabs.core.calculator import (
    calculate_turbidity_removal,
    identify_breakpoint,
    calculate_tss,
    calculate_iron_manganese_removal,
    calculate_lime_soda_dose,
    identify_gram_bacteria,
    check_hygiene_compliance,
    check_potability_status,
)

class TestTurbidityRemoval:
    def test_finds_optimum(self):
        doses = [10, 20, 30, 40, 50, 60]
        turbidities = [14.2, 8.5, 1.8, 4.3, 9.1, 15.4]
        opt_dose, opt_turb = calculate_turbidity_removal(doses, turbidities)
        assert opt_dose == 30
        assert opt_turb == 1.8
    
    def test_insufficient_data_raises_error(self):
        with pytest.raises(ValueError):
            calculate_turbidity_removal([10], [])

class TestBreakpointChlorination:
    def test_identifies_breakpoint(self):
        doses = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        residuals = [0.4, 0.8, 1.1, 0.6, 0.2, 0.5, 1.0, 1.5]
        bp_dose, bp_res = identify_breakpoint(doses, residuals)
        assert bp_dose == 2.5
        assert bp_res == 0.2
        
    def test_insufficient_data(self):
        with pytest.raises(ValueError):
            identify_breakpoint([0.5, 1.0], [0.4, 0.8])

class TestSuspendedSolids:
    def test_tss_vss_calculation(self):
        tss, vss, fss, has_vss = calculate_tss(100, 0.1250, 0.1374, 0.1292)
        assert round(tss, 2) == 124.00
        assert round(vss, 2) == 82.00
        assert round(fss, 2) == 42.00
        assert has_vss is True
        
    def test_tss_only_calculation(self):
        tss, vss, fss, has_vss = calculate_tss(100, 0.1250, 0.1374, None)
        assert round(tss, 2) == 124.00
        assert has_vss is False

class TestIronManganeseRemoval:
    def test_chlorine_demand(self):
        fe, mn, total = calculate_iron_manganese_removal(2.5, 0.45, "Chlorine (Cl2)")
        assert round(fe, 2) == 1.60
        assert round(mn, 2) == 0.58
        assert round(total, 2) == 2.19
        
    def test_invalid_oxidant(self):
        with pytest.raises(ValueError):
            calculate_iron_manganese_removal(2.5, 0.45, "Unknown")

class TestLimeSodaSoftening:
    def test_reagent_doses(self):
        lime, comm_lime, soda = calculate_lime_soda_dose(200, 120, 200, 15, 85)
        # 200/50 = 4 meq/L Ca, 120/50 = 2.4 meq/L Mg, 200/50 = 4 meq/L TAC, 15/22 = 0.6818 meq/L CO2
        # lime = 0.6818 + 4 + 2.4 = 7.0818 * 28 = 198.29
        assert round(lime, 1) == 198.3
        assert round(soda, 1) == 127.2 # NCH = TH (6.4) - TAC (4) = 2.4 * 53 = 127.2

class TestGramStaining:
    def test_gram_positive_staph(self):
        genus, _ = identify_gram_bacteria(True, "Cocci (Spherical)", "Clusters (Staphylo-)", False)
        assert genus == "Staphylococcus spp."
        
    def test_gram_negative_ecoli(self):
        genus, _ = identify_gram_bacteria(False, "Bacilli (Rods)", "Single/Random", False)
        assert genus == "Enterobacteriaceae (E. coli, Salmonella, Klebsiella) or Pseudomonas"

class TestHygieneCompliance:
    def test_compliance(self):
        res = check_hygiene_compliance([120, 45, 800], [100, 50, 100], 5.0)
        assert res == [1.2, 0.9, 8.0]

class TestPotabilityStatus:
    def test_drinking_water(self):
        tc = [0, 12, 5]
        fc = [0, 0, 2]
        ent = [0, 0, 0]
        results, overall = check_potability_status(tc, fc, ent, True)
        assert results == [True, False, False]
        assert overall is False
