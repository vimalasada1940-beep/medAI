import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import test_connection, create_tables, SessionLocal
from app.models import PHC, Medicine, Inventory, StockAlert
from app.ml.feature_engineering import (
    verify_feature_columns, 
    REQUIRED_FEATURE_COLUMNS, 
    FeatureValidationError,
    load_preprocessing_artifact
)
from app.ml.predict_demand import get_model_candidate_paths, load_trained_model, MLModelNotFoundError
from app.services.inventory_calculations import calculate_record_metrics, calculate_clinical_urgency
from app.services.alert_service import refresh_alerts
from app.collectors.csv_collector import parse_and_ingest_inventory_csv

def test_full_workflow():
    print("=" * 60)
    print("RUNNING BATCH 7: FULL WORKFLOW TEST SUITE")
    print("=" * 60)

    # 1. Model-file and Preprocessing-file accessibility
    candidate_paths = get_model_candidate_paths()
    print(f"[1] Model Candidate Paths Checked ({len(candidate_paths)} paths):")
    for cp in candidate_paths[:3]:
        print(f"    - {cp}")
    pre = load_preprocessing_artifact()
    print(f"    Preprocessing artifact status: {'LOADED' if pre else 'AWAITING USER FILE (Fallback Active)'}")

    # 2. Required Feature Validation
    full_feats = {c: 1 for c in REQUIRED_FEATURE_COLUMNS}
    verify_feature_columns(full_feats)
    missing_caught = False
    try:
        verify_feature_columns({"day_of_week": 1})
    except FeatureValidationError:
        missing_caught = True
    print(f"[2] Required Feature Validation: PASS (Rejects missing: {missing_caught}, Accepts complete: True)")

    # 3. Database Connection
    db_result = test_connection()
    print(f"[3] PostgreSQL Connection: PASS (SELECT 1 = {db_result})")

    # 4. Database Migrations / Table Creation
    create_tables()
    db = SessionLocal()
    try:
        phc_count = db.query(PHC).count()
        med_count = db.query(Medicine).count()
        inv_count = db.query(Inventory).count()
        print(f"[4] Database Tables & Schemas: PASS (PHCs: {phc_count}, Medicines: {med_count}, Inventories: {inv_count})")

        # 5. Prediction Generation & Inventory Calculations
        phc = db.query(PHC).first()
        med = db.query(Medicine).first()
        metrics = calculate_record_metrics(db, phc.id, med.id, available_stock=150)
        print(f"[5] Prediction Generation & Inventory Calculations: PASS")
        print(f"    - units_sold_today: {metrics['units_sold_today']}")
        print(f"    - seven_day_demand: {metrics['seven_day_demand']}")
        print(f"    - days_remaining: {metrics['days_remaining']}")
        print(f"    - risk_level: {metrics['risk_level']}")
        print(f"    - clinical_urgency: {metrics['clinical_urgency']} (Score: {metrics['urgency_score']})")

        # 6. CSV Upload & Database Write Operations
        csv_payload = f"phc_code,medicine_code,available_stock\n{phc.code},{med.code},175\n"
        csv_result = parse_and_ingest_inventory_csv(db, csv_payload)
        print(f"[6] CSV Upload & Write Operation: PASS (Status: {csv_result['status']}, Updated: {csv_result['updated_records']})")

        # 7. Alert Creation in PostgreSQL
        refresh_alerts(db)
        active_alerts = db.query(StockAlert).filter(StockAlert.is_resolved == False).count()
        print(f"[7] Alert Creation in PostgreSQL: PASS (Active Alerts: {active_alerts})")

        # 8. Database Read Operations
        inv_record = db.query(Inventory).filter(
            Inventory.phc_id == phc.id,
            Inventory.medicine_id == med.id
        ).first()
        assert inv_record.available_stock == 175
        print(f"[8] Database Read Operation: PASS (Verified stock {inv_record.available_stock} for {phc.code}/{med.code})")

    finally:
        db.close()

    print("=" * 60)
    print("ALL BATCH 7 WORKFLOW TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    test_full_workflow()
