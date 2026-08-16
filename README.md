# Keyword Priority Model

> An end-to-end data science and machine learning pipeline for analyzing, enriching, scoring, and prioritizing search keywords based on search volume, ranking position, estimated visits, CPC, SEO difficulty, paid difficulty, URL location, geographic information, and business category.

---

## 📌 Project Overview

The **Keyword Priority Model** is a data-driven system designed to identify and rank high-value keywords from large-scale keyword datasets.

The system processes raw keyword data, performs feature engineering, extracts geographic and business information from ranking URLs, calculates a unified priority score, categorizes keywords based on business importance, and generates ranked predictions for further analysis and decision-making.

The project is designed as a modular pipeline so that individual stages such as data processing, URL enrichment, feature engineering, scoring, model training, and evaluation can be maintained independently.

---

## 🎯 Objectives

The primary objectives of this project are:

- Process raw keyword datasets efficiently.
- Clean and standardize keyword-related data.
- Extract useful features from keyword metrics.
- Identify geographic information from ranking URLs.
- Detect business/service categories from URLs and keywords.
- Calculate keyword priority scores.
- Classify keywords into priority levels.
- Rank keywords based on their overall business value.
- Train and evaluate a machine learning model.
- Generate prediction datasets for downstream analysis.
- Create a reusable pipeline for multiple keyword sources.

---

## 🏗️ Project Architecture

```text
                    ┌──────────────────────┐
                    │     Raw Keyword      │
                    │       Datasets       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Data Processing   │
                    │   & Data Cleaning    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   URL Extraction &   │
                    │   Location Enrichment│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Feature Engineering  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Priority Scoring    │
                    │    & Categorization  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Model Training     │
                    │   & Evaluation       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Predictions & Ranked │
                    │       Keywords       │
                    └──────────────────────┘
```
# 📁 Project Structur 
Keyword-Priority-Model/
│
├── backend/
│   │
│   ├── data/
│   │   ├── raw/
│   │   │   ├── keywords _ tripadvisor.csv
│   │   │   └── zomato_keywords.csv
│   │   │
│   │   ├── processed/
│   │   │   ├── keywords _ tripadvisor_enriched.csv
│   │   │   ├── keywords _ tripadvisor_enriched_new.csv
│   │   │   └── zomato_keywords_enriched.csv
│   │   │
│   │   └── output/
│   │       ├── keywords _ tripadvisor_predictions.csv
│   │       └── zomato_keywords_predictions.csv
│   │
│   ├── model/
│   │   └── priority_model.pkl
│   │
│   ├── data_processing.py
│   ├── evaluate_model.py
│   ├── feature_engineering.py
│   ├── keyword_quality.py
│   ├── scoring.py
│   ├── train_model.py
│   ├── predict.py
│   ├── url_extraction.py
│   └── requirements.txt
│
├── .gitignore
└── README.md
