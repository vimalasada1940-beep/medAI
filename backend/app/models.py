from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Numeric, Boolean, Date, DateTime, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db import Base

class PHC(Base):
    __tablename__ = "phcs"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    district = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    inventories = relationship("Inventory", back_populates="phc", cascade="all, delete-orphan")
    daily_consumptions = relationship("DailyConsumption", back_populates="phc", cascade="all, delete-orphan")
    alerts = relationship("StockAlert", back_populates="phc", cascade="all, delete-orphan")
    indents = relationship("EmergencyIndent", back_populates="phc", cascade="all, delete-orphan")

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=False, default="Tablets")
    min_stock_level = Column(Integer, nullable=False, default=100)
    safety_stock_level = Column(Integer, nullable=False, default=200)
    target_coverage_days = Column(Integer, nullable=False, default=30)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    inventories = relationship("Inventory", back_populates="medicine", cascade="all, delete-orphan")
    daily_consumptions = relationship("DailyConsumption", back_populates="medicine", cascade="all, delete-orphan")
    alerts = relationship("StockAlert", back_populates="medicine", cascade="all, delete-orphan")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    phc_id = Column(Integer, ForeignKey("phcs.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    available_stock = Column(Integer, nullable=False, default=0)
    reserved_stock = Column(Integer, nullable=False, default=0)
    unit_cost = Column(Numeric(10, 2), default=0.00)
    batch_number = Column(String(50), nullable=True)
    expiry_date = Column(Date, nullable=True)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('phc_id', 'medicine_id', name='unique_phc_medicine'),)

    # Relationships
    phc = relationship("PHC", back_populates="inventories")
    medicine = relationship("Medicine", back_populates="inventories")

class DailyConsumption(Base):
    __tablename__ = "daily_consumption"

    id = Column(Integer, primary_key=True, index=True)
    phc_id = Column(Integer, ForeignKey("phcs.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    record_date = Column(Date, nullable=False)
    quantity_consumed = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('phc_id', 'medicine_id', 'record_date', name='unique_phc_med_date'),)

    # Relationships
    phc = relationship("PHC", back_populates="daily_consumptions")
    medicine = relationship("Medicine", back_populates="daily_consumptions")

class StockAlert(Base):
    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    phc_id = Column(Integer, ForeignKey("phcs.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False) # 'STOCKOUT_RISK', 'CONSUMPTION_ACCELERATION'
    risk_level = Column(String(20), nullable=False) # 'HIGH', 'MEDIUM', 'LOW'
    days_remaining = Column(Numeric(8, 2), nullable=True)
    burn_rate = Column(Numeric(8, 2), nullable=True)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    phc = relationship("PHC", back_populates="alerts")
    medicine = relationship("Medicine", back_populates="alerts")

class RedistributionRequest(Base):
    __tablename__ = "redistribution_requests"

    id = Column(Integer, primary_key=True, index=True)
    donor_phc_id = Column(Integer, ForeignKey("phcs.id", ondelete="CASCADE"), nullable=False)
    recipient_phc_id = Column(Integer, ForeignKey("phcs.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    proposed_quantity = Column(Integer, nullable=False)
    distance_km = Column(Numeric(8, 2), default=0.0)
    status = Column(String(20), nullable=False, default="PROPOSED") # 'PROPOSED', 'APPROVED', 'REJECTED', 'COMPLETED'
    reason = Column(Text, nullable=False)
    requested_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    donor_phc = relationship("PHC", foreign_keys=[donor_phc_id])
    recipient_phc = relationship("PHC", foreign_keys=[recipient_phc_id])
    medicine = relationship("Medicine")

class EmergencyIndent(Base):
    __tablename__ = "emergency_indents"

    id = Column(Integer, primary_key=True, index=True)
    phc_id = Column(Integer, ForeignKey("phcs.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    requested_quantity = Column(Integer, nullable=False)
    target_coverage_days = Column(Integer, nullable=False, default=30)
    current_stock = Column(Integer, nullable=False, default=0)
    burn_rate = Column(Numeric(8, 2), default=0.0)
    status = Column(String(20), nullable=False, default="PENDING") # 'PENDING', 'APPROVED', 'REJECTED', 'DISPATCHED'
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    phc = relationship("PHC", back_populates="indents")
    medicine = relationship("Medicine")
