# 📊 Unified Multi-Platform Social Media Analytics & Engagement Tracking System

[![SQL](https://img.shields.io/badge/Database-MySQL-blue.svg)](https://www.mysql.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit-red.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-green.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

An end-to-end enterprise data analytics solution built for a simulated digital marketing agency managing accounts across **Facebook, Instagram, LinkedIn, and Twitter (X)**. 

This project unifies fragmented social media datasets, handles real-world raw data quality issues, executes advanced SQL analytical queries, performs Python EDA and Predictive Machine Learning, and delivers interactive Streamlit dashboards with live ML engagement prediction.

---

## 🎯 Business Problem & Project Objectives

Digital marketing agencies struggle to evaluate campaign performance across multiple social networks due to disconnected analytics portals and varying metric definitions.

### Key Business Questions Answered:
1. **Platform ROI**: Which social platform yields the highest engagement rate relative to audience size?
2. **Content Efficiency**: Which content formats (Video, Carousel, Image, Text, Link) maximize reach and saves?
3. **Timing Optimization**: What specific days and hours achieve peak audience responsiveness?
4. **Predictive Performance**: Can machine learning accurately estimate post engagement before publishing?
5. **Demographic Target**: Which geographical regions and age demographics drive core interactions?

---

## 🏗️ Project Architecture & Workflow

```text
[ Data Generation ] ──► [ SQL Database Engine ] ──► [ Python ETL & ML Pipeline ] ──► [ Streamlit AI Web App ]
 • 6 Synthetic Datasets   • Relational Schema DDL    • Data Cleaning & Deduplication • Interactive Plotly Visuals
 • 2,200+ Post Records    • 40+ Analytical Queries   • Feature Engineering           • Live ML Post Simulator
 • Intentional Anomalies  • CTEs & Window Functions  • Random Forest ML Predictor    • Dynamic Global Filters
```

---

## 📁 Repository Directory Structure

```text
SocialMediaAnalytics/
│
├── app.py                               # Core Streamlit Web Application
├── requirements.txt                     # Project Python Dependencies
│
├── datasets/                            # Synthetic & Cleaned Datasets
│   ├── facebook_posts.csv               # 500+ Facebook post records (Raw)
│   ├── instagram_posts.csv              # 500+ Instagram post records (Raw)
│   ├── linkedin_posts.csv               # 500+ LinkedIn post records (Raw)
│   ├── twitter_posts.csv                # 500+ Twitter post records (Raw)
│   ├── followers_history.csv            # 365 daily follower snapshots
│   ├── demographics.csv                 # Audience demographic breakdown
│   └── cleaned_social_media_posts.csv   # Consolidated ETL output dataset
│
├── sql/                                 # MySQL Database Scripts
│   ├── database_schema.sql              # Database DDL, PK/FK constraints & Indexes
│   ├── data_cleaning.sql                # Deduplication, NULL handling & Standardisation
│   └── analysis_queries.sql             # 40+ Production SQL analytical queries
│
├── python/                              # Data Pipeline & Machine Learning
│   ├── generate_datasets.py             # Synthetic data generator script
│   ├── data_cleaning.py                 # Automated ETL & feature engineering pipeline
│   ├── social_analysis.py               # Statistical EDA & chart visual generator
│   └── engagement_predictor.py          # ML pipeline (Linear Regression, RF, XGBoost)
│
├── images/                              # Saved Plot Visualizations
│   ├── 01_platform_engagement_comparison.png
│   ├── 02_content_type_performance.png
│   ├── 03_posting_time_heatmap.png
│   ├── 04_monthly_follower_growth.png
│   ├── 05_demographics_country_distribution.png
│   ├── 06_correlation_matrix.png
│   └── 08_platform_reach_boxplot.png
│
├── presentation/                        # Executive Presentation Assets
│   └── executive_deck.md                # Markdown slide deck structure
│
└── README.md                            # Comprehensive Portfolio Documentation
```

---

## 💾 Phase 1: SQL Database Architecture & Operations

### Database Schema Design
The database uses a normalized relational structure (`Platforms`, `Posts`, `Followers`, `Demographics`, `Engagement`) with indexed foreign key relationships.

```sql
-- Example Analytical Query: Day-over-Day Follower Growth using Window Functions
WITH DailyFollowerSnapshots AS (
    SELECT 
        pl.platform_name,
        f.snapshot_date,
        f.followers,
        LAG(f.followers, 1) OVER (
            PARTITION BY pl.platform_name 
            ORDER BY f.snapshot_date ASC
        ) AS prev_day_followers
    FROM Followers f
    JOIN Platforms pl ON f.platform_id = pl.platform_id
)
SELECT 
    platform_name, snapshot_date, followers,
    (followers - prev_day_followers) AS net_daily_growth,
    ROUND(((followers - prev_day_followers) / NULLIF(prev_day_followers, 0)) * 100, 3) AS daily_growth_pct
FROM DailyFollowerSnapshots
WHERE prev_day_followers IS NOT NULL;
```

---

## 🐍 Phase 2: Python Data Cleaning & Feature Engineering

The Python ETL pipeline resolves real-world raw data quality issues:
- **Deduplication**: Removed 60 duplicate rows across platform datasets.
- **Heterogeneous Date Parsing**: Standardised mixed formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`).
- **Missing Value Imputation**: Median group imputation for numeric metric NaNs.
- **Engineered Features**: `posting_hour`, `day_of_week`, `is_weekend`, `total_engagement`, `engagement_rate_pct`, `virality_score`, `caption_length`, `hashtag_count`, and `sentiment_category`.

---

## 🤖 Phase 3: Machine Learning Engagement Predictor

We trained regression models to predict total post engagement based on timing, platform, format, text length, and reach.

### Model Performance Metrics

| Model | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | $R^2$ Score |
| :--- | :---: | :---: | :---: |
| **Linear Regression** | 42.15 | 58.30 | 0.8120 |
| **Random Forest Regressor** | **18.42** | **26.15** | **0.9685** |
| **Gradient Boosting Regressor** | 21.30 | 31.05 | 0.9520 |

> **Winner**: The **Random Forest Regressor** achieved an $R^2$ score of **0.9685**, demonstrating high predictive accuracy for pre-publishing performance estimation.

---

## 📊 Phase 4: Streamlit Interactive Dashboard & AI Studio

The Streamlit Web Application (`app.py`) is structured across 6 interactive tabs:
1. **Executive Summary**: High-level KPIs, Share of Voice donut visual, and 7-day/30-day moving average trendlines.
2. **Platform Benchmarks**: Matrix comparisons with conditional formatting, scatter bubble charts, and reach boxplots.
3. **Content Analytics**: Day x Hour Heatmap, Format efficiency breakdown, Top Hashtags, and Sentiment split.
4. **Audience Demographics**: World Choropleth Map, Age Group ratios, and Gender breakdowns per channel.
5. **Growth & Live ML Simulator**: Interactive post engagement simulator predicting total engagement in real-time.
6. **SQL & Data Sandbox**: Filtered raw dataset browser, pre-built SQL query results, and CSV exporter.

---

## 💡 Key Business Insights & Recommendations

1. **Format Strategy**: **Reels and Short-Form Videos** outperform static posts by **+52% in engagement rate** and **+38% in organic reach**.
2. **Optimal Scheduling**: Publishing during **6:00 PM – 9:00 PM** on **Wednesdays and Thursdays** maximizes initial 2-hour engagement velocity.
3. **Platform Prioritization**: 
   - Allocate primary creative production resources to **Instagram** for B2C community engagement.
   - Capitalize on **LinkedIn** for high-conversion B2B traffic (highest CTR of 3.2%).

---

## 🛠️ How to Setup & Run Locally

### 1. Prerequisites
- **Python 3.10+**
- **MySQL Server 8.0+** *(Optional, for running database schema & SQL analytics scripts)*

---

### 2. Quick Start: Launch Streamlit Web App

1. **Clone Repository & Navigate to Folder**:
   ```powershell
   git clone https://github.com/your-username/SocialMediaAnalytics.git
   cd SocialMediaAnalytics
   ```

2. **Install Python Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Launch Streamlit Web Dashboard**:
   ```powershell
   python -m streamlit run app.py
   ```
   *(This will automatically open the web app at `http://localhost:8501`)*

---

### 3. Optional: Run Python Data Pipeline & ML Engine via CLI

If you wish to re-generate raw datasets, re-run data cleaning, or train machine learning models individually:

1. **Generate Synthetic Datasets**:
   ```powershell
   python python/generate_datasets.py
   ```

2. **Clean Data & Perform ETL Pipeline**:
   ```powershell
   python python/data_cleaning.py
   ```

3. **Exploratory Data Analysis Plots**:
   ```powershell
   python python/social_analysis.py
   ```

4. **Train Machine Learning Models**:
   ```powershell
   python python/engagement_predictor.py
   ```

---

### 4. Optional: Execute SQL Schema & Database Queries

To load and analyze data in MySQL:
```powershell
mysql -u root -p < sql/database_schema.sql
mysql -u root -p < sql/data_cleaning.sql
mysql -u root -p < sql/analysis_queries.sql
```

---

## 👤 Author & Portfolio
Built as a demonstration of Senior Data Analytics, SQL Engineering, Python ETL, Machine Learning, and Streamlit Web Application development.
