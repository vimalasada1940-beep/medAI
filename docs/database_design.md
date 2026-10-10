# MediPulse Database Design 🗄️

## PostgreSQL Schema Architecture
MediPulse uses PostgreSQL managed via pgAdmin as its sole relational database. SQLite files (e.g. `medipulse.db`) are unused and excluded via `.gitignore`.

---

## Entity Relationship Summary

```
+------------+       +---------------+       +-------------------+
|    phcs    | 1───N |   inventory   | N───1 |     medicines     |
+------------+       +---------------+       +-------------------+
      │                      │                         │
      │ 1                    │                         │
      │                      ▼                         │
      ├───────────N ▶ daily_consumption ◀──────────────┤ N
      │                                                │
      ├───────────N ▶   stock_alerts    ◀──────────────┤ N
      │                                                │
      ├───────────N ▶ emergency_indents ◀──────────────┤ N
      │                                                │
      └───────────N ▶ redistribution_requests ─────────┘ N
```

---

## Main Tables & Columns

1. **`phcs`**: Primary Health Centre metadata (id, code, name, district, state, latitude, longitude, contact_person, phone).
2. **`medicines`**: Medicine catalog (id, code, name, category, unit, min_stock_level, safety_stock_level, target_coverage_days).
3. **`inventory`**: Available stock per PHC & medicine (id, phc_id, medicine_id, available_stock, reserved_stock, unit_cost, batch_number, expiry_date).
4. **`daily_consumption`**: Daily usage records (id, phc_id, medicine_id, record_date, quantity_consumed).
5. **`stock_alerts`**: Active warnings (id, phc_id, medicine_id, alert_type, risk_level, days_remaining, burn_rate, message, is_resolved).
6. **`redistribution_requests`**: Proposed transfers (id, donor_phc_id, recipient_phc_id, medicine_id, proposed_quantity, distance_km, status, reason).
7. **`emergency_indents`**: Procurement indents (id, phc_id, medicine_id, requested_quantity, target_coverage_days, current_stock, burn_rate, status, reason).
