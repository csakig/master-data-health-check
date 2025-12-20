![SAP Data Quality CI Pipeline](https://github.com/csakig/master-data-health-check/actions/workflows/ci_pipeline.yml/badge.svg)

# 🔍 Master Data Health Check Tool

An automated **Data Quality Validation System** built with Python and Streamlit. Designed to streamline data migration processes (e.g., SAP S/4HANA migrations) by identifying critical errors in master data files before loading.

## 🚀 Key Features

- **Automated Validation:** Instantly checks for:
  - Missing or invalid Email formats (Regex).
  - Duplicated Partner IDs.
  - Suspicious/Short VAT numbers.
- **Interactive Filtering:** Filter data dynamically by Country codes.
- **Smart Highlighting:** Visualizes specific erroneous cells in red within the dataset.
- **Reporting:** Generates downloadable Excel reports containing only the problematic rows.

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** (Frontend & UI)
- **Pandas** (Data Manipulation)
- **OpenPyXL** (Excel I/O)

## 📦 How to Run

1. Clone the repository:
   git clone https://github.com/csakig/master-data-health-check.git
2. Install dependencies:
   pip install -r requirements.txt
3. Run the app:
   streamlit run app.py

Created by csakig
