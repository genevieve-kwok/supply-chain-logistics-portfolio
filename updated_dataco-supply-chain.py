import os
import datetime
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual style
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

# ==========================================
# STEP 1: DATA PREPROCESSING & CLEANING
# ==========================================
def load_and_clean_data(dataco_path, output_path=None):
    print("--- STEP 1: LOADING & CLEANING DATA ---")
    
    # Load primary dataset
    df_dataco = pd.read_csv(dataco_path, encoding='latin1')
    print(f"Original DataCo Shape: {df_dataco.shape}")

    # 1.1 Parse Timestamps
    df_dataco['order_date'] = pd.to_datetime(df_dataco['order date (DateOrders)'])
    df_dataco['shipping_date'] = pd.to_datetime(df_dataco['shipping date (DateOrders)'])

    # 1.2 Datetime Feature Engineering
    df_dataco['order_year'] = df_dataco['order_date'].dt.year
    df_dataco['order_month'] = df_dataco['order_date'].dt.month
    df_dataco['order_dayofweek'] = df_dataco['order_date'].dt.day_name()
    df_dataco['order_hour'] = df_dataco['order_date'].dt.hour

    # 1.3 Calculate Delivery Delay Variance
    df_dataco['delivery_delay_days'] = (
        df_dataco['Days for shipping (real)'] - df_dataco['Days for shipment (scheduled)']
    )

    # 1.4 Handle Missing Values & Drop Completely Empty Columns
    if 'Product Description' in df_dataco.columns:
        df_dataco.drop(columns=['Product Description'], inplace=True)

    df_dataco['Customer Zipcode'] = df_dataco['Customer Zipcode'].fillna(0).astype(int)
    df_dataco['Order Zipcode'] = df_dataco['Order Zipcode'].fillna('Unknown')

    # 1.5 Calculate Customer Full Name
    df_dataco['Customer Name'] = (
        df_dataco['Customer Fname'].fillna('') + ' ' + df_dataco['Customer Lname'].fillna('')
    ).str.strip()

    print(f"Cleaned DataCo Shape: {df_dataco.shape}")

    # Save cleaned dataset to new CSV
    if output_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        output_path = f"DataCo_Cleaned_{timestamp}.csv"

    df_dataco.to_csv(output_path, index=False)
    print(f"--> Cleaned dataset saved as: '{output_path}'\n")

    return df_dataco


# ==========================================
# STEP 2: BUILD SQL TABLES & EXPORT CSVS
# ==========================================
def create_sql_exports(df_dataco):
    print("--- STEP 2: CREATING SQL TABLES & EXPORTING CSVS ---")
    
    # Establish SQLite Connection
    conn = sqlite3.connect("dataco_supply_chain_clean.db")
    
    # Load primary DataFrame into SQLite as a single staging table
    df_dataco.to_sql("dataco_staging", conn, if_exists="replace", index=False)

    # 2.1 Customer Segmentation Query
    query_customer = """
    SELECT 
        `Customer Id` AS customer_id,
        `Customer Segment` AS customer_segment,
        `Customer City` AS customer_city,
        `Customer Country` AS customer_country,
        COUNT(DISTINCT `Order Id`) AS total_orders,
        SUM(`Order Item Quantity`) AS total_items_purchased,
        ROUND(SUM(`Sales`), 2) AS total_lifetime_spend,
        ROUND(AVG(`Sales`), 2) AS avg_order_value
    FROM dataco_staging
    GROUP BY customer_id, customer_segment, customer_city, customer_country
    ORDER BY total_lifetime_spend DESC;
    """
    df_customers = pd.read_sql_query(query_customer, conn)
    df_customers.to_csv("customer_segmentation.csv", index=False)
    print("--> Saved 'customer_segmentation.csv'")

    # 2.2 Fulfillment & Logistics Efficiency Query
    query_fulfillment = """
    SELECT 
        `Shipping Mode` AS shipping_mode,
        COUNT(DISTINCT `Order Id`) AS total_shipments,
        ROUND(AVG(`Days for shipping (real)`), 2) AS avg_actual_shipping_days,
        ROUND(AVG(`Days for shipment (scheduled)`), 2) AS avg_scheduled_shipping_days,
        ROUND(AVG(delivery_delay_days), 2) AS avg_delay_days,
        SUM(CASE WHEN `Late_delivery_risk` = 1 THEN 1 ELSE 0 END) AS late_deliveries_count,
        ROUND(
            (SUM(CASE WHEN `Late_delivery_risk` = 1 THEN 1.0 ELSE 0.0 END) / COUNT(DISTINCT `Order Id`)) * 100, 
            2
        ) AS late_delivery_rate_pct
    FROM dataco_staging
    GROUP BY shipping_mode
    ORDER BY late_delivery_rate_pct DESC;
    """
    df_fulfillment = pd.read_sql_query(query_fulfillment, conn)
    df_fulfillment.to_csv("fulfillment_logistics_efficiency.csv", index=False)
    print("--> Saved 'fulfillment_logistics_efficiency.csv'")

    # 2.3 Sales & Profitability Analysis Query
    query_profitability = """
    SELECT 
        `Category Name` AS category_name,
        `Order Region` AS order_region,
        COUNT(DISTINCT `Order Id`) AS order_volume,
        ROUND(SUM(`Sales`), 2) AS gross_revenue,
        ROUND(SUM(`Order Profit Per Order`), 2) AS net_profit,
        ROUND(
            (SUM(`Order Profit Per Order`) / SUM(`Sales`)) * 100, 
            2
        ) AS profit_margin_pct
    FROM dataco_staging
    GROUP BY category_name, order_region
    HAVING gross_revenue > 0
    ORDER BY net_profit DESC;
    """
    df_profitability = pd.read_sql_query(query_profitability, conn)
    df_profitability.to_csv("sales_profitability.csv", index=False)
    print("--> Saved 'sales_profitability.csv'")

    conn.close()
    print("\nSuccess! All 3 CSV files are saved in your folder for Tableau.")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    DATACO_FILE = 'DataCoSupplyChainDataset.csv'
    
    # Run Pipeline
    df_cleaned = load_and_clean_data(DATACO_FILE)
    create_sql_exports(df_cleaned)