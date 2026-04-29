# ✈️ Airline Flight Delay Analysis

## 📊 Overview
This project analyzes U.S. flight delays, cancellations, routes, and delay causes.  
It includes data analysis in a Jupyter notebook and an interactive dashboard built with Streamlit.

---

## 🎯 Objectives
- Identify delay patterns across airlines and routes  
- Analyze delay causes (weather, carrier, etc.)  
- Explore trends over time  
- Build an interactive dashboard for visualization  

---

## Dataset and Data Cleaning
The dataset is based on U.S. airline flight delay records from the Bureau of Transportation Statistics (BTS). It includes airline, origin, destination, arrival delay, cancellation, and delay cause information.

- Converted flight dates to datetime format
- Renamed carrier column for consistency
- Filled missing delay-cause values with 0
- Created route, season, delay category, and delay-rate features

---

## 🧠 Features
- Delay rate calculation (`Is_Delayed`)
- Delay categories (minor → extreme)
- Route-level analysis (Origin → Destination)
- Time-based features (month, day, season)

---

## 📊 Dashboard Features
- Filters (airline, year, airport)
- Multiple views (trends, routes, causes)
- Interactive Plotly charts (hover, zoom)

---

## Limitations
- Delay causes may be incomplete for some records
- External factors like detailed weather and airport congestion are not included
- This project is descriptive, not predictive

---

## 🚀 How to Run
```bash
pip install -r requirements.txt
python -m streamlit run app.py
Then open: http://localhost:8501

🛠️ Tools
Python, Pandas, Plotly, Streamlit

---

