# MediPulse: Project Overview 🏥⚡

## Executive Summary
MediPulse is a 3rd-year B.Tech AI & Data Science student decision-support prototype designed to mitigate medicine stock-outs in Primary Health Centres (PHCs). By tracking consumption patterns, calculating 7-day daily burn rates, predicting days to depletion, detecting demand acceleration, recommending safe inter-PHC stock transfers, and generating emergency indents, MediPulse empowers health officials to make timely, data-driven decisions.

> **Disclaimer**: MediPulse is a student decision-support prototype built for demonstration and research purposes. It is **not** a clinically validated or officially deployed government system. Automated transfers are disabled; all actions require human authorization.

---

## Key Problem Addressed
Rural Primary Health Centres frequently face unexpected stock-outs of essential medicines (e.g., Paracetamol, Amoxicillin, Metformin) due to:
1. Delayed paper-based reporting.
2. Sudden demand spikes during seasonal outbreaks.
3. Lack of visibility into nearby PHCs holding surplus inventory.

---

## Core Features
1. **Real-time Stock Tracking**: Comprehensive view of available stock across all PHCs.
2. **Dynamic Burn Rate Engine**: Computes average daily consumption over 7-day rolling windows.
3. **Early Warning Risk Classification**:
   - **HIGH Risk**: Stock depletion estimated in $\le 3$ days.
   - **MEDIUM Warning**: Stock depletion estimated in $4 - 7$ days.
   - **LOW Risk**: Stock adequate for $> 7$ days.
4. **Demand Acceleration Detection**: Identifies sharp increases in consumption (e.g., 1.5x increase in 7 days).
5. **Smart Redistribution Engine**: Identifies nearby donor PHCs with surplus stock exceeding safety thresholds.
6. **Emergency Indent Generation**: Computes target 30-day coverage indents when redistribution is insufficient.
7. **ML Demand Forecasting**: scikit-learn RandomForestRegressor model trained on temporal consumption features.
