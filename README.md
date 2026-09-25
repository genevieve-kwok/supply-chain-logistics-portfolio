# supply-chain-logistics-portfolio
An end-to-end data analytics project evaluating global logistics performance, inventory optimization, and customer segmentation. This repository features an automated Python/SQLite ETL pipeline and multi-faceted Tableau dashboards designed to drive commercial and operational decision-making.

## Project Overview:
In modern supply chains, operational efficiency and customer value must be evaluated in tandem. This project takes raw transactional and logistics data, cleans and processes it through a programmatic data pipeline, and transforms it into interactive business intelligence dashboards.

### Core Objectives:
* **Fulfillment & Logistics Efficiency:** Track shipping delays, modal performance, and fulfillment bottlenecks across regions.
* **Sales & Profitability Analysis:** Identify margin drivers, high-revenue product categories, and regional profitability gaps.
* **Customer Segmentation & CLV:** Analyze customer purchasing behavior, order frequency, and lifetime spend tiers.

## Technical Tools
* **Data Processing & Pipeline:** Python (`pandas`, `sqlite3`)
* **Database Management:** SQLite (local relational data storage)
* **Data Visualization & BI:** Tableau Desktop (`.twbx`)
* **Version Control:** Git & GitHub

## Repository Structure

```text
supply-chain-logistics-portfolio/
│
├── data_processing.py                # Automated Python ETL script & SQLite data pipeline
├── customer_segmentation.csv         # Processed customer metrics & value tiers
├── fulfillment_logistics_efficiency.csv# Logistics performance & shipping delay metrics
├── sales_profitability.csv           # Revenue, cost, and margin breakdowns
├── Global_SupplyChain_Performance_...# Tableau Packaged Workbook (.twbx)
├── .gitignore                        # Excludes local databases and system caches
└── README.md                         # Project documentation
