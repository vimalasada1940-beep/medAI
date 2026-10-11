import os
import sys
from datetime import date, timedelta, datetime
import random

# Ensure parent path is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import SessionLocal, Base, engine
from app.models import PHC, Medicine, Inventory, DailyConsumption, StockAlert, RedistributionRequest, EmergencyIndent

DEMO_PHCS = [
    {
        "code": "PHC-001",
        "name": "Rampur Primary Health Centre",
        "district": "Rampur",
        "state": "Uttar Pradesh",
        "latitude": 28.8074,
        "longitude": 79.0274,
        "contact_person": "Dr. A. Sharma",
        "phone": "+91 9876543210"
    },
    {
        "code": "PHC-002",
        "name": "Bilaspur Community Health Centre",
        "district": "Rampur",
        "state": "Uttar Pradesh",
        "latitude": 28.8850,
        "longitude": 79.2680,
        "contact_person": "Dr. R. Verma",
        "phone": "+91 9876543211"
    },
    {
        "code": "PHC-003",
        "name": "Shahabad Sub-District Hospital",
        "district": "Rampur",
        "state": "Uttar Pradesh",
        "latitude": 28.5600,
        "longitude": 79.0400,
        "contact_person": "Dr. S. Khan",
        "phone": "+91 9876543212"
    },
    {
        "code": "PHC-004",
        "name": "Suar Rural Health Centre",
        "district": "Rampur",
        "state": "Uttar Pradesh",
        "latitude": 29.0200,
        "longitude": 79.0500,
        "contact_person": "Dr. P. Gupta",
        "phone": "+91 9876543213"
    },
    {
        "code": "PHC-005",
        "name": "Milak Primary Health Unit",
        "district": "Rampur",
        "state": "Uttar Pradesh",
        "latitude": 28.6100,
        "longitude": 79.1800,
        "contact_person": "Dr. M. Singh",
        "phone": "+91 9876543214"
    }
]

DEMO_MEDICINES = [
    {
        "code": "MED-PAR-500",
        "name": "Paracetamol 500mg",
        "category": "Analgesics & Antipyretics",
        "unit": "Tablets",
        "min_stock_level": 500,
        "safety_stock_level": 1000,
        "target_coverage_days": 30
    },
    {
        "code": "MED-AMO-500",
        "name": "Amoxicillin 500mg",
        "category": "Antibiotics",
        "unit": "Capsules",
        "min_stock_level": 300,
        "safety_stock_level": 600,
        "target_coverage_days": 30
    },
    {
        "code": "MED-ORS-21G",
        "name": "Oral Rehydration Salts (ORS)",
        "category": "Gastrointestinal",
        "unit": "Sachets",
        "min_stock_level": 200,
        "safety_stock_level": 400,
        "target_coverage_days": 30
    },
    {
        "code": "MED-MET-500",
        "name": "Metformin 500mg",
        "category": "Anti-Diabetic",
        "unit": "Tablets",
        "min_stock_level": 400,
        "safety_stock_level": 800,
        "target_coverage_days": 30
    },
    {
        "code": "MED-AML-005",
        "name": "Amlodipine 5mg",
        "category": "Cardiovascular",
        "unit": "Tablets",
        "min_stock_level": 300,
        "safety_stock_level": 600,
        "target_coverage_days": 30
    },
    {
        "code": "MED-AZI-250",
        "name": "Azithromycin 250mg",
        "category": "Antibiotics",
        "unit": "Tablets",
        "min_stock_level": 150,
        "safety_stock_level": 300,
        "target_coverage_days": 30
    }
]

def seed_database():
    print("[INIT] Initializing MediPulse Database Tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("[SEED] Seeding Primary Health Centres (PHCs)...")
        phc_objects = {}
        for phc_data in DEMO_PHCS:
            existing = db.query(PHC).filter(PHC.code == phc_data["code"]).first()
            if not existing:
                phc = PHC(**phc_data)
                db.add(phc)
                db.flush()
                phc_objects[phc.code] = phc
            else:
                phc_objects[existing.code] = existing

        print("[SEED] Seeding Medicine Catalog...")
        med_objects = {}
        for med_data in DEMO_MEDICINES:
            existing = db.query(Medicine).filter(Medicine.code == med_data["code"]).first()
            if not existing:
                med = Medicine(**med_data)
                db.add(med)
                db.flush()
                med_objects[med.code] = med
            else:
                med_objects[existing.code] = existing

        db.commit()

        # Seed Daily Consumption for the past 14 days
        print("[SEED] Generating 14-day synthetic consumption records...")
        today = date.today()
        random.seed(42) # Deterministic synthetic seed

        # Custom stock settings per PHC and medicine to demonstrate HIGH, MEDIUM, and LOW risk cases
        stock_scenarios = {
            ("PHC-001", "MED-PAR-500"): {"stock": 180, "daily_avg": 75},  # ~2.4 days -> HIGH RISK
            ("PHC-001", "MED-AMO-500"): {"stock": 250, "daily_avg": 50},  # 5.0 days -> MEDIUM RISK
            ("PHC-001", "MED-ORS-21G"): {"stock": 1200, "daily_avg": 30}, # 40 days -> STABLE / DONOR
            ("PHC-002", "MED-PAR-500"): {"stock": 2500, "daily_avg": 80}, # 31 days -> STABLE / DONOR
            ("PHC-002", "MED-AMO-500"): {"stock": 1800, "daily_avg": 45}, # 40 days -> STABLE / DONOR
            ("PHC-003", "MED-MET-500"): {"stock": 120, "daily_avg": 60},  # 2.0 days -> HIGH RISK
            ("PHC-004", "MED-AML-005"): {"stock": 310, "daily_avg": 55},  # 5.6 days -> MEDIUM RISK
            ("PHC-005", "MED-AZI-250"): {"stock": 95, "daily_avg": 40},   # 2.37 days -> HIGH RISK
        }

        for phc_code, phc_obj in phc_objects.items():
            for med_code, med_obj in med_objects.items():
                scenario = stock_scenarios.get((phc_code, med_code), {"stock": 1500, "daily_avg": 35})
                
                # Seed inventory if not existing
                inv = db.query(Inventory).filter(
                    Inventory.phc_id == phc_obj.id,
                    Inventory.medicine_id == med_obj.id
                ).first()

                if not inv:
                    inv = Inventory(
                        phc_id=phc_obj.id,
                        medicine_id=med_obj.id,
                        available_stock=scenario["stock"],
                        reserved_stock=0,
                        unit_cost=round(random.uniform(2.5, 45.0), 2),
                        batch_number=f"BATCH-{phc_obj.id}{med_obj.id}-2026",
                        expiry_date=today + timedelta(days=random.randint(180, 500))
                    )
                    db.add(inv)

                # Seed 14 days of consumption
                for day_offset in range(14, 0, -1):
                    rec_date = today - timedelta(days=day_offset)
                    existing_cons = db.query(DailyConsumption).filter(
                        DailyConsumption.phc_id == phc_obj.id,
                        DailyConsumption.medicine_id == med_obj.id,
                        DailyConsumption.record_date == rec_date
                    ).first()

                    if not existing_cons:
                        # Add slight noise around daily_avg
                        qty = max(0, int(random.gauss(scenario["daily_avg"], 5)))
                        cons = DailyConsumption(
                            phc_id=phc_obj.id,
                            medicine_id=med_obj.id,
                            record_date=rec_date,
                            quantity_consumed=qty
                        )
                        db.add(cons)

        db.commit()

        # Seed initial Stock Alerts
        print("[SEED] Seeding initial Stock Alerts...")
        # Check high risk stock-outs
        high_risk_cases = [
            ("PHC-001", "MED-PAR-500", "HIGH", 2.4, 75.0, "Paracetamol stock critical at Rampur PHC. Estimated stock-out in 2.4 days."),
            ("PHC-003", "MED-MET-500", "HIGH", 2.0, 60.0, "Metformin stock critical at Shahabad Sub-District Hospital. Estimated stock-out in 2.0 days."),
            ("PHC-005", "MED-AZI-250", "HIGH", 2.37, 40.0, "Azithromycin stock critical at Milak PHU. Estimated stock-out in 2.37 days."),
            ("PHC-001", "MED-AMO-500", "MEDIUM", 5.0, 50.0, "Amoxicillin stock low at Rampur PHC. Estimated stock-out in 5.0 days.")
        ]

        for phc_code, med_code, risk, days_rem, burn, msg in high_risk_cases:
            p_obj = phc_objects.get(phc_code)
            m_obj = med_objects.get(med_code)
            if p_obj and m_obj:
                existing_alert = db.query(StockAlert).filter(
                    StockAlert.phc_id == p_obj.id,
                    StockAlert.medicine_id == m_obj.id,
                    StockAlert.is_resolved == False
                ).first()
                if not existing_alert:
                    alert = StockAlert(
                        phc_id=p_obj.id,
                        medicine_id=m_obj.id,
                        alert_type="STOCKOUT_RISK",
                        risk_level=risk,
                        days_remaining=days_rem,
                        burn_rate=burn,
                        message=msg,
                        is_resolved=False
                    )
                    db.add(alert)

        db.commit()
        print("[SUCCESS] Database seeding complete! Demonstration data is ready.")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during database seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
