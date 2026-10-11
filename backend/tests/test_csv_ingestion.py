import pytest
from app.collectors.csv_collector import (
    validate_csv_columns,
    parse_and_validate_csv,
    CSVValidationError,
    REQUIRED_INVENTORY_COLUMNS,
    REQUIRED_CONSUMPTION_COLUMNS
)

def test_missing_inventory_columns_validation():
    # Only phc_code provided, missing medicine_code and available_stock
    bad_headers = ["phc_code", "daily_burn_rate"]
    with pytest.raises(CSVValidationError) as excinfo:
        validate_csv_columns(bad_headers, expected_type="inventory")
    
    err = excinfo.value
    assert "medicine_code" in err.missing_columns
    assert "available_stock" in err.missing_columns

def test_missing_consumption_columns_validation():
    # Missing quantity_consumed
    bad_headers = ["phc_code", "medicine_code", "record_date"]
    with pytest.raises(CSVValidationError) as excinfo:
        validate_csv_columns(bad_headers, expected_type="consumption")
    
    err = excinfo.value
    assert "quantity_consumed" in err.missing_columns

def test_auto_detect_valid_inventory_columns():
    headers = ["phc_code", "medicine_code", "available_stock", "batch_number"]
    detected = validate_csv_columns(headers, expected_type="auto")
    assert detected == "inventory"

def test_auto_detect_valid_consumption_columns():
    headers = ["phc_code", "medicine_code", "record_date", "quantity_consumed"]
    detected = validate_csv_columns(headers, expected_type="auto")
    assert detected == "consumption"
