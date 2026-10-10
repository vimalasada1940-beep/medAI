-- MediPulse Database Schema (PostgreSQL)
-- Prototype Decision Support System for PHC Medicine Stock Management

DROP TABLE IF EXISTS emergency_indents CASCADE;
DROP TABLE IF EXISTS redistribution_requests CASCADE;
DROP TABLE IF EXISTS stock_alerts CASCADE;
DROP TABLE IF EXISTS daily_consumption CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS medicines CASCADE;
DROP TABLE IF EXISTS phcs CASCADE;

-- 1. Primary Health Centres (PHCs) Table
CREATE TABLE phcs (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    district VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Medicines Catalog Table
CREATE TABLE medicines (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'Tablets',
    min_stock_level INT NOT NULL DEFAULT 100,
    safety_stock_level INT NOT NULL DEFAULT 200,
    target_coverage_days INT NOT NULL DEFAULT 30,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. PHC Inventory Table
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    phc_id INT NOT NULL REFERENCES phcs(id) ON DELETE CASCADE,
    medicine_id INT NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    available_stock INT NOT NULL CHECK (available_stock >= 0),
    reserved_stock INT NOT NULL DEFAULT 0 CHECK (reserved_stock >= 0),
    unit_cost NUMERIC(10, 2) DEFAULT 0.00,
    batch_number VARCHAR(50),
    expiry_date DATE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_phc_medicine UNIQUE (phc_id, medicine_id)
);

-- 4. Daily Consumption Table
CREATE TABLE daily_consumption (
    id SERIAL PRIMARY KEY,
    phc_id INT NOT NULL REFERENCES phcs(id) ON DELETE CASCADE,
    medicine_id INT NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    quantity_consumed INT NOT NULL CHECK (quantity_consumed >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_phc_med_date UNIQUE (phc_id, medicine_id, record_date)
);

-- 5. Stock Alerts Table
CREATE TABLE stock_alerts (
    id SERIAL PRIMARY KEY,
    phc_id INT NOT NULL REFERENCES phcs(id) ON DELETE CASCADE,
    medicine_id INT NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL, -- 'STOCKOUT_RISK', 'CONSUMPTION_ACCELERATION'
    risk_level VARCHAR(20) NOT NULL, -- 'HIGH', 'MEDIUM', 'LOW'
    days_remaining NUMERIC(8, 2),
    burn_rate NUMERIC(8, 2),
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Inter-PHC Redistribution Requests Table
CREATE TABLE redistribution_requests (
    id SERIAL PRIMARY KEY,
    donor_phc_id INT NOT NULL REFERENCES phcs(id) ON DELETE CASCADE,
    recipient_phc_id INT NOT NULL REFERENCES phcs(id) ON DELETE CASCADE,
    medicine_id INT NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    proposed_quantity INT NOT NULL CHECK (proposed_quantity > 0),
    distance_km NUMERIC(8, 2) DEFAULT 0.0,
    status VARCHAR(20) NOT NULL DEFAULT 'PROPOSED', -- 'PROPOSED', 'APPROVED', 'REJECTED', 'COMPLETED'
    reason TEXT NOT NULL,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Emergency Indents Table
CREATE TABLE emergency_indents (
    id SERIAL PRIMARY KEY,
    phc_id INT NOT NULL REFERENCES phcs(id) ON DELETE CASCADE,
    medicine_id INT NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    requested_quantity INT NOT NULL CHECK (requested_quantity > 0),
    target_coverage_days INT NOT NULL DEFAULT 30,
    current_stock INT NOT NULL DEFAULT 0,
    burn_rate NUMERIC(8, 2) DEFAULT 0.0,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED', 'DISPATCHED'
    reason TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices for query performance
CREATE INDEX idx_inventory_phc_med ON inventory(phc_id, medicine_id);
CREATE INDEX idx_daily_consumption_date ON daily_consumption(phc_id, medicine_id, record_date);
CREATE INDEX idx_alerts_phc ON stock_alerts(phc_id, is_resolved);
