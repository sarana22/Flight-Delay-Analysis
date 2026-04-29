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

## 🚀 How to Run
```bash
pip install -r requirements.txt
python -m streamlit run app.py
Then open: http://localhost:8501

🛠️ Tools
Python, Pandas, Plotly, Streamlit