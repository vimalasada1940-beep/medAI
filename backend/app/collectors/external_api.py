from typing import Dict, Any, List
from datetime import date

def fetch_external_phc_data_mock() -> List[Dict[str, Any]]:
    """
    Mock adapter for external PHC health portal sync.
    Operates 100% offline using synthetic demonstration data without paid API keys.
    """
    return [
        {
            "phc_code": "PHC-001",
            "medicine_code": "MED-PAR-500",
            "available_stock": 180,
            "sync_status": "OK",
            "last_synced": str(date.today()),
            "notice": "DEMONSTRATION ONLY: Synthetic offline API adapter."
        },
        {
            "phc_code": "PHC-002",
            "medicine_code": "MED-PAR-500",
            "available_stock": 2500,
            "sync_status": "OK",
            "last_synced": str(date.today()),
            "notice": "DEMONSTRATION ONLY: Synthetic offline API adapter."
        }
    ]
