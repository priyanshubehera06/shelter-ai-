"""
sources.py — Provenance registry and metadata for central and state regulatory frameworks.
"""

from typing import Dict, Any

REGULATION_SOURCES: Dict[str, Dict[str, Any]] = {
    "ENS_2021": {
        "title": "Eco-Niwas Samhita 2021 (Energy Conservation Building Code for Residential Buildings)",
        "issuing_body": "Bureau of Energy Efficiency (BEE), Ministry of Power, Govt of India",
        "url": "https://beeindia.gov.in/en/eco-niwas-samhita",
        "jurisdiction": "Central",
        "status": "verified"
    },
    "ECBC_2017": {
        "title": "Energy Conservation Building Code 2017 / ECSBC 2024",
        "issuing_body": "Bureau of Energy Efficiency (BEE)",
        "url": "https://beeindia.gov.in/en/energy-conservation-building-code",
        "jurisdiction": "Central",
        "status": "verified"
    },
    "NBC_2016": {
        "title": "National Building Code of India 2016",
        "issuing_body": "Bureau of Indian Standards (BIS)",
        "url": "https://www.bis.gov.in/",
        "jurisdiction": "Central",
        "status": "verified"
    }
}
