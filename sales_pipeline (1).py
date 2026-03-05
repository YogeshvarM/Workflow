"""
sales_pipeline.py

Sales data processing pipeline for quarterly reporting.
Processes raw transaction data, enriches with customer segments,
calculates commissions, and generates summary reports.

NOTE: This file is intentionally written with pandas anti-patterns
(iterrows, apply axis=1, python loops over DataFrames) to demonstrate
the pandas-to-polars migration workflow.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# 1. DATA LOADING
# ---------------------------------------------------------------------------

def load_transactions(n_rows: int = 500_000) -> pd.DataFrame:
    """Generate a synthetic transactions dataset."""
    np.random.seed(42)

    regions = ["North", "South", "East", "West", "Central"]
    products = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Service Pro", "Service Basic"]
    channels = ["Online", "Retail", "Partner", "Direct"]
    reps = [f"REP-{str(i).zfill(4)}" for i in range(1, 201)]

    df = pd.DataFrame({
        "transaction_id": [f"TXN-{str(i).zfill(8)}" for i in range(1, n_rows + 1)],
        "date": pd.date_range("2023-01-01", periods=n_rows, freq="min"),
        "rep_id": np.random.choice(reps, n_rows),
        "region": np.random.choice(regions, n_rows),
        "product": np.random.choice(products, n_rows),
        "channel": np.random.choice(channels, n_rows),
        "quantity": np.random.randint(1, 50, n_rows),
        "unit_price": np.round(np.random.uniform(10.0, 500.0, n_rows), 2),
        "discount_pct": np.round(np.random.uniform(0, 0.35, n_rows), 2),
        "customer_id": np.random.randint(1000, 9999, n_rows),
        "is_return": np.random.choice([True, False], n_rows, p=[0.05, 0.95]),
    })

    return df


def load_customer_segments() -> pd.DataFrame:
    """Generate a synthetic customer segments lookup table."""
    np.random.seed(99)
    customer_ids = list(range(1000, 9999))

    segments = np.random.choice(
        ["Enterprise", "Mid-Market", "SMB", "Startup", "Government"],
        len(customer_ids),
        p=[0.10, 0.20, 0.40, 0.20, 0.10],
    )
    credit_scores = np.random.randint(300, 850, len(customer_ids))

    return pd.DataFrame({
        "customer_id": customer_ids,
        "segment": segments,
        "credit_score": credit_scores,
        "lifetime_value": np.round(np.random.uniform(500, 100_000, len(customer_ids)), 2),
    })


def load_commission_rates() -> pd.DataFrame:
    """Commission rate table by product and channel."""
    rows = []
    products = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Service Pro", "Service Basic"]
    channels = ["Online", "Retail", "Partner", "Direct"]
    rates = {
        "Widget A":       {"Online": 0.08, "Retail": 0.06, "Partner": 0.10, "Direct": 0.07},
        "Widget B":       {"Online": 0.07, "Retail": 0.05, "Partner": 0.09, "Direct": 0.06},
        "Gadget X":       {"Online": 0.12, "Retail": 0.09, "Partner": 0.14, "Direct": 0.11},
        "Gadget Y":       {"Online": 0.11, "Retail": 0.08, "Partner": 0.13, "Direct": 0.10},
        "Service Pro":    {"Online": 0.15, "Retail": 0.12, "Partner": 0.18, "Direct": 0.14},
        "Service Basic":  {"Online": 0.10, "Retail": 0.08, "Partner": 0.12, "Direct": 0.09},
    }
    for product in products:
        for channel in channels:
            rows.append({
                "product": product,
                "channel": channel,
                "commission_rate": rates[product][channel],
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. ANTI-PATTERN: iterrows() for row-by-row revenue calculation
# ---------------------------------------------------------------------------

def calculate_revenue_slow(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate net revenue for each transaction.
    
    BUG: Uses iterrows() which is extremely slow on large DataFrames.
    Should be a vectorised operation.
    """
    revenues = []
    discounted_prices = []
    net_amounts = []

    for idx, row in df.iterrows():
        gross = row["quantity"] * row["unit_price"]
        discount = gross * row["discount_pct"]
        net = gross - discount

        if row["is_return"]:
            net = -abs(net)

        revenues.append(gross)
        discounted_prices.append(discount)
        net_amounts.append(net)

    df["gross_revenue"] = revenues
    df["discount_amount"] = discounted_prices
    df["net_revenue"] = net_amounts

    return df


# ---------------------------------------------------------------------------
# 3. ANTI-PATTERN: apply(axis=1) for complex row-wise logic
# ---------------------------------------------------------------------------

def _classify_deal_size(row) -> str:
    """Classify a single transaction by deal size tier."""
    amount = row["net_revenue"]
    segment = row.get("segment", "Unknown")

    if segment == "Enterprise":
        if amount > 5000:
            return "Mega"
        elif amount > 2000:
            return "Large"
        elif amount > 500:
            return "Medium"
        else:
            return "Small"
    elif segment in ("Mid-Market", "Government"):
        if amount > 3000:
            return "Large"
        elif amount > 1000:
            return "Medium"
        else:
            return "Small"
    else:
        if amount > 2000:
            return "Large"
        elif amount > 500:
            return "Medium"
        else:
            return "Small"


def classify_deals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add deal size classification to each transaction.
    
    BUG: Uses apply(axis=1) which is slow because it calls a Python
    function for every single row instead of using vectorised operations.
    """
    df["deal_size"] = df.apply(_classify_deal_size, axis=1)
    return df


# ---------------------------------------------------------------------------
# 4. ANTI-PATTERN: Python for-loop with .loc for conditional updates
# ---------------------------------------------------------------------------

def apply_regional_adjustments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply regional tax and bonus adjustments.
    
    BUG: Iterates row by row using .loc[] which is painfully slow.
    Each .loc access is an expensive pandas operation.
    """
    df["tax_rate"] = 0.0
    df["regional_bonus"] = 0.0
    df["adjusted_revenue"] = 0.0

    for i in range(len(df)):
        region = df.loc[i, "region"]
        net = df.loc[i, "net_revenue"]

        if region == "North":
            tax = 0.08
            bonus = 50.0 if net > 1000 else 0.0
        elif region == "South":
            tax = 0.07
            bonus = 75.0 if net > 1500 else 0.0
        elif region == "East":
            tax = 0.09
            bonus = 40.0 if net > 800 else 0.0
        elif region == "West":
            tax = 0.065
            bonus = 60.0 if net > 1200 else 0.0
        else:  # Central
            tax = 0.075
            bonus = 55.0 if net > 1000 else 0.0

        df.loc[i, "tax_rate"] = tax
        df.loc[i, "regional_bonus"] = bonus
        df.loc[i, "adjusted_revenue"] = net * (1 - tax) + bonus

    return df


# ---------------------------------------------------------------------------
# 5. ANTI-PATTERN: groupby().apply() with a heavy Python function
# ---------------------------------------------------------------------------

def calculate_rep_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate performance metrics per sales rep.
    
    BUG: Uses groupby().apply() with a complex Python function.
    This prevents pandas from using its internal C optimizations.
    """

    def _rep_stats(group: pd.DataFrame) -> pd.Series:
        total_revenue = group["net_revenue"].sum()
        avg_deal = group["net_revenue"].mean()
        deal_count = len(group)
        return_rate = group["is_return"].sum() / deal_count if deal_count > 0 else 0
        top_product = group.groupby("product")["net_revenue"].sum().idxmax()
        regions_covered = group["region"].nunique()

        # Arbitrary performance score
        score = (total_revenue / 10000) * (1 - return_rate) * (regions_covered / 5)

        return pd.Series({
            "total_revenue": total_revenue,
            "avg_deal_size": avg_deal,
            "deal_count": deal_count,
            "return_rate": return_rate,
            "top_product": top_product,
            "regions_covered": regions_covered,
            "performance_score": round(score, 2),
        })

    result = df.groupby("rep_id").apply(_rep_stats).reset_index()
    return result


# ---------------------------------------------------------------------------
# 6. ANTI-PATTERN: Multiple inefficient merges + iterrows commission calc
# ---------------------------------------------------------------------------

def calculate_commissions(
    transactions: pd.DataFrame,
    commission_rates: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate commission for each transaction by looking up rates.
    
    BUG: After merging, uses iterrows() to apply bonus multipliers
    instead of vectorised conditional logic.
    """
    # Merge is fine, but what follows is not
    merged = transactions.merge(
        commission_rates,
        on=["product", "channel"],
        how="left",
    )

    commissions = []
    for idx, row in merged.iterrows():
        base_commission = row["net_revenue"] * row["commission_rate"]

        # Bonus multiplier based on deal size
        if row.get("deal_size") == "Mega":
            multiplier = 1.5
        elif row.get("deal_size") == "Large":
            multiplier = 1.25
        elif row.get("deal_size") == "Medium":
            multiplier = 1.1
        else:
            multiplier = 1.0

        # Penalty for returns
        if row["is_return"]:
            multiplier *= 0.0  # No commission on returns

        commissions.append(round(base_commission * multiplier, 2))

    merged["commission"] = commissions
    return merged


# ---------------------------------------------------------------------------
# 7. ANTI-PATTERN: Repeated filtering + concat in a loop
# ---------------------------------------------------------------------------

def generate_quarterly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary report broken down by quarter.
    
    BUG: Loops through quarters, filters, aggregates, and concats
    one at a time. Should be a single group_by operation.
    """
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year

    summaries = []

    for year in df["year"].unique():
        for quarter in sorted(df["quarter"].unique()):
            chunk = df[(df["year"] == year) & (df["quarter"] == quarter)]

            if len(chunk) == 0:
                continue

            summary = {
                "year": year,
                "quarter": quarter,
                "total_transactions": len(chunk),
                "total_revenue": chunk["net_revenue"].sum(),
                "avg_deal_size": chunk["net_revenue"].mean(),
                "total_returns": chunk["is_return"].sum(),
                "unique_customers": chunk["customer_id"].nunique(),
                "unique_reps": chunk["rep_id"].nunique(),
                "top_region": chunk.groupby("region")["net_revenue"].sum().idxmax(),
                "top_product": chunk.groupby("product")["net_revenue"].sum().idxmax(),
            }
            summaries.append(summary)

    return pd.DataFrame(summaries)


# ---------------------------------------------------------------------------
# 8. ANTI-PATTERN: Building a DataFrame row by row with append/concat
# ---------------------------------------------------------------------------

def flag_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag transactions that look anomalous.
    
    BUG: Builds a result DataFrame one row at a time using concat.
    This is O(n^2) memory because each concat copies the entire frame.
    """
    anomalies = pd.DataFrame()

    mean_revenue = df["net_revenue"].mean()
    std_revenue = df["net_revenue"].std()
    threshold = mean_revenue + (3 * std_revenue)

    for idx, row in df.iterrows():
        flags = []

        # Flag 1: Revenue outlier
        if abs(row["net_revenue"]) > threshold:
            flags.append("revenue_outlier")

        # Flag 2: Extremely high discount
        if row["discount_pct"] > 0.30:
            flags.append("high_discount")

        # Flag 3: High quantity with high discount (possible fraud)
        if row["quantity"] > 40 and row["discount_pct"] > 0.25:
            flags.append("possible_fraud")

        # Flag 4: Return with high value
        if row["is_return"] and abs(row["net_revenue"]) > 5000:
            flags.append("high_value_return")

        if flags:
            flagged = row.to_frame().T
            flagged["anomaly_flags"] = ",".join(flags)
            anomalies = pd.concat([anomalies, flagged], ignore_index=True)

    return anomalies


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def run_pipeline():
    """Execute the full sales data pipeline."""
    print("=" * 60)
    print("SALES PIPELINE - Starting")
    print("=" * 60)

    # Load data
    print("\n[1/8] Loading transactions...")
    transactions = load_transactions(n_rows=100_000)  # Use 100k for demo
    print(f"      Loaded {len(transactions):,} transactions")

    print("[2/8] Loading customer segments...")
    customers = load_customer_segments()
    print(f"      Loaded {len(customers):,} customer records")

    print("[3/8] Loading commission rates...")
    rates = load_commission_rates()
    print(f"      Loaded {len(rates):,} rate entries")

    # Enrich with customer data
    print("\n[4/8] Enriching with customer segments...")
    transactions = transactions.merge(customers, on="customer_id", how="left")

    # Process
    print("[5/8] Calculating revenue (iterrows - SLOW)...")
    import time
    start = time.time()
    transactions = calculate_revenue_slow(transactions)
    elapsed = time.time() - start
    print(f"      Done in {elapsed:.1f}s")

    print("[6/8] Classifying deals (apply axis=1 - SLOW)...")
    start = time.time()
    transactions = classify_deals(transactions)
    elapsed = time.time() - start
    print(f"      Done in {elapsed:.1f}s")

    print("[7/8] Applying regional adjustments (loc loop - SLOW)...")
    start = time.time()
    transactions = apply_regional_adjustments(transactions)
    elapsed = time.time() - start
    print(f"      Done in {elapsed:.1f}s")

    # Commissions
    print("[8/8] Calculating commissions (iterrows - SLOW)...")
    start = time.time()
    transactions = calculate_commissions(transactions, rates)
    elapsed = time.time() - start
    print(f"      Done in {elapsed:.1f}s")

    # Reports
    print("\n--- Generating Reports ---")

    print("  Rep performance...")
    rep_perf = calculate_rep_performance(transactions)

    print("  Quarterly summary...")
    quarterly = generate_quarterly_summary(transactions)

    print("  Anomaly detection (this will be very slow)...")
    start = time.time()
    # Only run on a sample for demo purposes
    anomalies = flag_anomalies(transactions.head(10_000).reset_index(drop=True))
    elapsed = time.time() - start
    print(f"  Anomalies found: {len(anomalies):,} in {elapsed:.1f}s")

    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Total transactions processed: {len(transactions):,}")
    print(f"  Total revenue: ${transactions['net_revenue'].sum():,.2f}")
    print(f"  Total commissions: ${transactions['commission'].sum():,.2f}")
    print(f"  Sales reps: {rep_perf['rep_id'].nunique()}")
    print(f"  Quarters covered: {len(quarterly)}")
    print(f"  Anomalies flagged: {len(anomalies):,}")

    return {
        "transactions": transactions,
        "rep_performance": rep_perf,
        "quarterly_summary": quarterly,
        "anomalies": anomalies,
    }


if __name__ == "__main__":
    results = run_pipeline()
