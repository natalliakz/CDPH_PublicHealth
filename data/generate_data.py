"""
Generate synthetic public health surveillance data for California Department of Public Health demo.
Mimics disease surveillance, outbreak tracking, and health indicator monitoring.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

# California counties
COUNTIES = [
    "Los Angeles", "San Diego", "Orange", "Riverside", "San Bernardino",
    "Santa Clara", "Alameda", "Sacramento", "Contra Costa", "Fresno",
    "San Francisco", "Ventura", "San Mateo", "Kern", "San Joaquin",
    "Stanislaus", "Sonoma", "Tulare", "Santa Barbara", "Monterey"
]

# Disease conditions for surveillance
CONDITIONS = [
    "Influenza", "COVID-19", "RSV", "Norovirus", "Salmonella",
    "Hepatitis A", "Pertussis", "Measles", "Tuberculosis", "West Nile Virus"
]

# Age groups
AGE_GROUPS = ["0-4", "5-17", "18-44", "45-64", "65+"]

# Data sources (simulating SAS migration context)
DATA_SOURCES = ["Legacy SAS", "Databricks", "Direct Entry", "Lab Feed", "Hospital EHR"]


def generate_surveillance_data(n_records=10000):
    """Generate disease surveillance case data."""
    records = []

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 4, 30)
    date_range = (end_date - start_date).days

    for i in range(n_records):
        county = random.choice(COUNTIES)
        condition = random.choice(CONDITIONS)
        age_group = random.choice(AGE_GROUPS)

        # Seasonal patterns for respiratory diseases
        report_date = start_date + timedelta(days=random.randint(0, date_range))
        month = report_date.month

        # Higher respiratory cases in winter
        if condition in ["Influenza", "COVID-19", "RSV"]:
            if month in [11, 12, 1, 2]:
                if random.random() > 0.3:
                    continue  # Skip some to create seasonal pattern

        # Outbreak simulation for certain conditions
        is_outbreak = random.random() < 0.05

        # Case severity
        if age_group in ["0-4", "65+"]:
            severity_weights = [0.3, 0.4, 0.3]  # Higher severity for vulnerable
        else:
            severity_weights = [0.6, 0.3, 0.1]
        severity = random.choices(["Mild", "Moderate", "Severe"], weights=severity_weights)[0]

        # Hospitalization
        hosp_prob = {"Mild": 0.02, "Moderate": 0.15, "Severe": 0.6}[severity]
        hospitalized = random.random() < hosp_prob

        # Lab confirmation
        lab_confirmed = random.random() < 0.75

        # Days to report (data quality metric)
        days_to_report = int(np.random.exponential(3)) + 1

        records.append({
            "case_id": f"CA-{2024 + i // 5000}-{i:06d}",
            "county": county,
            "condition": condition,
            "age_group": age_group,
            "sex": random.choice(["Male", "Female"]),
            "report_date": report_date,
            "onset_date": report_date - timedelta(days=random.randint(1, 7)),
            "severity": severity,
            "hospitalized": hospitalized,
            "icu_admission": hospitalized and severity == "Severe" and random.random() < 0.3,
            "outcome": random.choices(
                ["Recovered", "Recovering", "Deceased"],
                weights=[0.92, 0.06, 0.02] if severity != "Severe" else [0.7, 0.15, 0.15]
            )[0],
            "lab_confirmed": lab_confirmed,
            "is_outbreak_associated": is_outbreak,
            "outbreak_id": f"OB-{report_date.year}-{random.randint(1, 50):03d}" if is_outbreak else None,
            "data_source": random.choices(
                DATA_SOURCES,
                weights=[0.3, 0.25, 0.15, 0.2, 0.1]  # SAS still significant
            )[0],
            "days_to_report": days_to_report,
            "reporter_region": random.choice(["Northern", "Bay Area", "Central", "Southern"]),
        })

    return pd.DataFrame(records)


def generate_health_indicators():
    """Generate county-level health indicators."""
    records = []

    indicators = [
        ("life_expectancy", 75, 85, "years"),
        ("infant_mortality_rate", 2, 8, "per 1,000"),
        ("vaccination_rate_flu", 30, 70, "percent"),
        ("vaccination_rate_covid", 50, 90, "percent"),
        ("obesity_rate", 15, 40, "percent"),
        ("diabetes_prevalence", 5, 15, "percent"),
        ("uninsured_rate", 3, 15, "percent"),
        ("poverty_rate", 5, 25, "percent"),
        ("air_quality_index", 20, 150, "AQI"),
        ("drinking_water_violations", 0, 10, "count"),
    ]

    for county in COUNTIES:
        # County characteristics affect indicators
        if county in ["San Francisco", "Santa Clara", "San Mateo"]:
            wealth_factor = 0.8  # Better outcomes
        elif county in ["Fresno", "Kern", "Tulare"]:
            wealth_factor = 1.2  # More challenges
        else:
            wealth_factor = 1.0

        for indicator, low, high, unit in indicators:
            # Some indicators are "lower is better"
            if indicator in ["infant_mortality_rate", "obesity_rate", "diabetes_prevalence",
                           "uninsured_rate", "poverty_rate", "air_quality_index", "drinking_water_violations"]:
                value = low + (high - low) * wealth_factor * random.uniform(0.7, 1.3)
            else:
                value = high - (high - low) * wealth_factor * random.uniform(0.7, 1.3)

            value = max(low * 0.8, min(high * 1.2, value))

            records.append({
                "county": county,
                "indicator": indicator,
                "value": round(value, 2),
                "unit": unit,
                "year": 2025,
                "data_source": random.choice(["Census", "BRFSS", "Vital Stats", "CalHHS"]),
                "confidence_interval_low": round(value * 0.9, 2),
                "confidence_interval_high": round(value * 1.1, 2),
            })

    return pd.DataFrame(records)


def generate_outbreak_summary():
    """Generate outbreak investigation summaries."""
    records = []

    outbreak_types = [
        ("Foodborne", ["Salmonella", "Norovirus", "Hepatitis A"]),
        ("Respiratory", ["Influenza", "COVID-19", "RSV", "Pertussis"]),
        ("Vector-borne", ["West Nile Virus"]),
        ("Vaccine-preventable", ["Measles", "Pertussis"]),
    ]

    settings = ["Restaurant", "School", "Healthcare Facility", "Community Event",
                "Long-term Care", "Childcare", "Workplace", "Prison/Jail"]

    for i in range(75):
        outbreak_type, conditions = random.choice(outbreak_types)
        condition = random.choice(conditions)

        start_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 850))
        duration = random.randint(7, 90)

        case_count = random.randint(5, 200)
        hosp_count = int(case_count * random.uniform(0.05, 0.25))
        death_count = int(hosp_count * random.uniform(0, 0.1))

        records.append({
            "outbreak_id": f"OB-{start_date.year}-{i+1:03d}",
            "outbreak_type": outbreak_type,
            "condition": condition,
            "county": random.choice(COUNTIES),
            "setting": random.choice(settings),
            "start_date": start_date,
            "end_date": start_date + timedelta(days=duration) if random.random() > 0.2 else None,
            "status": random.choice(["Closed", "Closed", "Closed", "Active", "Under Investigation"]),
            "total_cases": case_count,
            "hospitalizations": hosp_count,
            "deaths": death_count,
            "attack_rate": round(random.uniform(5, 50), 1),
            "source_identified": random.random() < 0.7,
            "investigation_lead": f"EPI-{random.randint(100, 999)}",
            "data_quality_score": round(random.uniform(0.6, 1.0), 2),
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    print("Generating synthetic CDPH surveillance data...")

    surveillance = generate_surveillance_data()
    indicators = generate_health_indicators()
    outbreaks = generate_outbreak_summary()

    surveillance.to_csv("data/disease_surveillance.csv", index=False)
    indicators.to_csv("data/health_indicators.csv", index=False)
    outbreaks.to_csv("data/outbreak_summary.csv", index=False)

    print(f"Generated {len(surveillance)} surveillance records")
    print(f"Generated {len(indicators)} health indicator records")
    print(f"Generated {len(outbreaks)} outbreak records")
    print("Saved to data/ directory")
