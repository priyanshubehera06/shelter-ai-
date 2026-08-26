def calculate_mcda_shelter_score(
    pmv_score,
    comfort_compliance_pct,
    carbon_intensity_kg_m2,
    capex_inr,
    thermal_mass_kj_m2k,
    energy_savings_pct
):
    """
    Computes a 5-pillar Multi-Criteria Decision Analysis (MCDA) Sustainability Score (0-100 scale).
    """
    # 1. Thermal Comfort Pillar
    pmv_error = abs(pmv_score)
    comfort_pillar = max(0.0, min(100.0, 100.0 - (pmv_error * 25.0) + (comfort_compliance_pct * 0.25)))
    
    # 2. Carbon Footprint Pillar (Target: < 50 kgCO2/m2 = 100%, > 200 kgCO2/m2 = 0%)
    carbon_pillar = max(0.0, min(100.0, (1.0 - max(0.0, carbon_intensity_kg_m2 - 30.0) / 170.0) * 100.0))
    
    # 3. Cost Affordability Pillar (Target CapEx <= 80,000 INR for rapid relief)
    cost_pillar = max(0.0, min(100.0, (1.0 - max(0.0, capex_inr - 50000.0) / 120000.0) * 100.0))
    
    # 4. Structural Resilience & Thermal Mass (Target thermal mass ~200-400 kJ/m2K)
    resilience_pillar = max(0.0, min(100.0, (thermal_mass_kj_m2k / 350.0) * 100.0))
    
    # 5. Energy Efficiency Pillar
    efficiency_pillar = max(0.0, min(100.0, energy_savings_pct * 1.05))
    
    # Overall Weighted Score
    overall_score = round(
        0.30 * comfort_pillar +
        0.20 * carbon_pillar +
        0.20 * cost_pillar +
        0.15 * resilience_pillar +
        0.15 * efficiency_pillar, 1
    )
    
    if overall_score >= 85:
        grade, badge_color = "A+ (Excellent Passive Design)", "#2ecc71"
    elif overall_score >= 75:
        grade, badge_color = "A (High Performance)", "#27ae60"
    elif overall_score >= 65:
        grade, badge_color = "B (Moderate Passive Design)", "#f39c12"
    elif overall_score >= 50:
        grade, badge_color = "C (Basic Standard)", "#e67e22"
    else:
        grade, badge_color = "D (Needs Optimization)", "#e74c3c"
        
    return {
        "overall_score": overall_score,
        "grade": grade,
        "badge_color": badge_color,
        "pillars": {
            "Thermal Comfort": round(comfort_pillar, 1),
            "Low Carbon Footprint": round(carbon_pillar, 1),
            "Cost Affordability": round(cost_pillar, 1),
            "Structural Mass & Resilience": round(resilience_pillar, 1),
            "Energy Efficiency": round(efficiency_pillar, 1)
        }
    }
