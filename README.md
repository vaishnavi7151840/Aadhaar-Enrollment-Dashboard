# Aadhaar Enrollment Analysis Dashboard (Streamlit)

A simple and user-friendly dashboard built using **Python + Streamlit** to analyze Aadhaar enrollment data.  
It supports dataset upload, filtering, key metrics, visual graphs, and CSV downloads.

---

## Objective
To create an interactive dashboard that helps understand Aadhaar enrollment patterns across:
- Time (date/month/year trends)
- Geography (state/district/pincode)
- Age buckets (0–5, 5–17, 18+)

---

## Tech Stack
- Python
- Streamlit (UI)
- Pandas / NumPy (data processing)
- Matplotlib (graphs)

---

## Key Features
- Upload dataset (CSV / XLS / XLSX)
- Filters: Date range, State, District, Pincode (optional)
- KPIs: Total rows, Total enrollments, States count, Districts count
- Graphs: Trend graph, Age group totals, Top districts/states
- Download filtered data as CSV

---

## Dataset
Source: Kaggle (Aadhaar enrollment dataset)

## Project Structure
Aadhaar-Enrollment-Dashboard
├─ app.py
├─ model_logic.py
├─ requirements.txt

└─ README.md
