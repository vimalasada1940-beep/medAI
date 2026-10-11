from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# --- PHC Schemas ---
class PHCBase(BaseModel):
    code: str = Field(..., max_length=20, examples=["PHC-001"])
    name: str = Field(..., max_length=100, examples=["Central PHC Rampur"])
    district: str = Field(..., max_length=50, examples=["Rampur"])
    state: str = Field(..., max_length=50, examples=["Uttar Pradesh"])
    latitude: float = Field(..., examples=[28.8074])
    longitude: float = Field(..., examples=[79.0274])
    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

class PHCCreate(PHCBase):
    pass

class PHCOut(PHCBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Medicine Schemas ---
class MedicineBase(BaseModel):
    code: str = Field(..., max_length=20, examples=["MED-PAR-500"])
    name: str = Field(..., max_length=100, examples=["Paracetamol 500mg"])
    category: str = Field(..., max_length=50, examples=["Analgesics"])
    unit: str = Field("Tablets", max_length=20)
    min_stock_level: int = Field(100, ge=0)
    safety_stock_level: int = Field(200, ge=0)
    target_coverage_days: int = Field(30, ge=1)

class MedicineCreate(MedicineBase):
    pass

class MedicineOut(MedicineBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Inventory Schemas ---
class InventoryBase(BaseModel):
    phc_id: int
    medicine_id: int
    available_stock: int = Field(..., ge=0)
    reserved_stock: int = Field(0, ge=0)
    unit_cost: float = Field(0.0, ge=0.0)
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryOut(InventoryBase):
    id: int
    last_updated: datetime
    phc: Optional[PHCOut] = None
    medicine: Optional[MedicineOut] = None
    burn_rate: Optional[float] = 0.0
    days_remaining: Optional[float] = None
    risk_level: Optional[str] = "LOW"
    status_label: Optional[str] = "STABLE"
    units_sold_today: Optional[float] = 0.0
    seven_day_demand: Optional[float] = 0.0
    clinical_urgency: Optional[str] = "ROUTINE"
    urgency_score: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)



# --- Daily Consumption Schemas ---
class DailyConsumptionBase(BaseModel):
    phc_id: int
    medicine_id: int
    record_date: date
    quantity_consumed: int = Field(..., ge=0)

class DailyConsumptionCreate(DailyConsumptionBase):
    pass

class DailyConsumptionOut(DailyConsumptionBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Stock Alert Schemas ---
class StockAlertOut(BaseModel):
    id: int
    phc_id: int
    medicine_id: int
    alert_type: str
    risk_level: str
    days_remaining: Optional[float] = None
    burn_rate: Optional[float] = None
    message: str
    is_resolved: bool
    created_at: datetime
    phc: Optional[PHCOut] = None
    medicine: Optional[MedicineOut] = None

    model_config = ConfigDict(from_attributes=True)


# --- Redistribution Request Schemas ---
class RedistributionRequestCreate(BaseModel):
    donor_phc_id: int
    recipient_phc_id: int
    medicine_id: int
    proposed_quantity: int = Field(..., gt=0)
    reason: str

class RedistributionRecommendationOut(BaseModel):
    donor_phc: PHCOut
    recipient_phc: PHCOut
    medicine: MedicineOut
    donor_available_stock: int
    donor_safety_stock: int
    surplus_available: int
    recipient_available_stock: int
    recipient_burn_rate: float
    recipient_days_remaining: Optional[float]
    recommended_transfer_quantity: int
    distance_km: float
    safety_validated: bool
    explanation: str

class RedistributionRequestOut(BaseModel):
    id: int
    donor_phc_id: int
    recipient_phc_id: int
    medicine_id: int
    proposed_quantity: int
    distance_km: float
    status: str
    reason: str
    requested_at: datetime
    updated_at: datetime
    donor_phc: Optional[PHCOut] = None
    recipient_phc: Optional[PHCOut] = None
    medicine: Optional[MedicineOut] = None

    model_config = ConfigDict(from_attributes=True)


# --- Emergency Indent Schemas ---
class EmergencyIndentCreate(BaseModel):
    phc_id: int
    medicine_id: int
    target_coverage_days: Optional[int] = 30
    reason: Optional[str] = "Automated early warning stock depletion indent"

class EmergencyIndentStatusUpdate(BaseModel):
    status: str = Field(..., examples=["APPROVED", "REJECTED", "DISPATCHED"])

class EmergencyIndentOut(BaseModel):
    id: int
    phc_id: int
    medicine_id: int
    requested_quantity: int
    target_coverage_days: int
    current_stock: int
    burn_rate: float
    status: str
    reason: str
    created_at: datetime
    updated_at: datetime
    phc: Optional[PHCOut] = None
    medicine: Optional[MedicineOut] = None

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Summary Schemas ---
class DashboardSummaryOut(BaseModel):
    total_phcs: int
    total_medicines: int
    medicines_at_risk: int
    high_risk_stockouts: int
    pending_redistributions: int
    pending_indents: int
    synthetic_notice: str = "DEMONSTRATION ONLY: Synthetic data for student prototype."
