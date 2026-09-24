# Tech Layoff Analysis

An exploratory data analysis project focused on understanding technology layoffs, the reasons behind job cuts, AI-related layoffs, company revenue, AI investments, and stock market reactions.

The project combines Python-based data analysis with an interactive Streamlit dashboard.

---

## 📌 Project Overview

This project analyzes technology layoff data, with the current dataset covering the **first quarter (Q1) of 2026 — January to March**.

The analysis is divided into two parts:

1. Basic Analysis
2. Advanced Analysis

Both analyses are available through the Streamlit dashboard.

---

## 🔍 Analysis Covered

### 01. Basic Analysis

The basic analysis focuses on understanding the dataset and identifying major patterns in layoffs.

#### Dataset Overview

- Number of companies
- Total jobs cut
- Number of records
- Number of columns

#### Data Cleaning

- Duplicate record identification and removal
- Date conversion
- Basic data type inspection
- Creation of an AI-related reason classification

#### Workforce Cuts by Sector

Analyzes total jobs cut across different technology sectors to identify sectors with larger workforce reductions.

#### AI Investment vs Jobs Cut

Examines the relationship between companies' simultaneous AI investments and the number of jobs cut.

The analysis also highlights companies with higher AI investments and checks whether larger AI investments are associated with larger layoffs.

#### Revenue vs Jobs Cut

Compares company revenue with the number of jobs cut to check whether companies with higher revenue also show larger layoffs.

#### AI-related Job Cuts

Breaks down total job cuts based on the stated reason and calculates the percentage contribution of different reasons to overall layoffs.

---

## 📈 Advanced Analysis

The advanced analysis goes deeper into time-based patterns, AI involvement, stock movement, company size, and sector-level trends.

### Q1 2026 Layoff Frequency

Analyzes monthly job cuts during the first quarter of 2026.

### Monthly Layoffs Across Years

Compares monthly layoff activity across **2024, 2025, and 2026** to identify changes in layoff patterns over time.

### AI-Cited vs Non-AI-Cited Layoffs

Compares layoffs where AI was cited as a factor against layoffs where AI was not cited.

The analysis looks at both the size of layoffs and their overall share.

### Stock Reaction

Examines stock price movement associated with companies announcing layoffs.

### AI-Driven Layoff Vulnerability by Sector

Looks at the distribution of AI-cited layoffs across different technology sectors.

### Company-level AI Investment and Job Cuts

Provides a company-level comparison of simultaneous AI investment and the number of jobs cut.

---

## 💡 Key Findings

Some observations from the analysis include:

- AI-related reasons account for a significant share of total jobs cut in the dataset.
- Companies making large AI investments do not consistently show proportionally larger layoffs.
- Revenue alone does not show a clear relationship with the number of jobs cut.
- Some companies appear as outliers when comparing AI investment with layoffs.
- Layoff activity varies across sectors and months.
- AI-cited layoffs can be compared with non-AI-cited layoffs to understand how frequently AI is associated with workforce reductions.

These findings are based on the dataset used in this project and should not be interpreted as evidence of causation.

---

## 🛠 Tools & Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Streamlit
- Jupyter Notebook

---

## 📂 Project Structure

```text
Tech Layoff Analysis/
│
├── app.py
├── tech_layoffs_2026_tracker.csv
├── Loading&cleaning&basicAnalysis.ipynb
├── Advance_Analysis.ipynb
├── requirements.txt
└── README.md
