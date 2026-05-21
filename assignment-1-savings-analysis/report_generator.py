"""
Report generator: produces output CSV and console summary dict.
"""

import pandas as pd


def generate_full_report(results: list[dict], output_path: str) -> pd.DataFrame:
    """Write full results to CSV and return the DataFrame."""
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    return df


def generate_summary(df: pd.DataFrame) -> dict:
    """Return a summary dict from the results DataFrame."""
    matched = df[df["matched_catalog_id"].notna() & (df["matched_catalog_id"] != "")]

    total_savings = matched["line_savings"].sum() if "line_savings" in matched.columns else 0.0
    annual_savings = total_savings  # quantities are already annual in sample data

    high = len(df[df["confidence_tier"] == "HIGH"])
    medium = len(df[df["confidence_tier"] == "MEDIUM"])
    low = len(df[df["confidence_tier"] == "LOW"])
    unmatched = len(df[df["matched_catalog_id"].isna() | (df["matched_catalog_id"] == "")])

    top_items = (
        matched.nlargest(5, "line_savings")[
            ["prospect_description", "matched_description", "line_savings"]
        ].to_dict(orient="records")
        if "line_savings" in matched.columns
        else []
    )

    return {
        "total_annual_savings": round(annual_savings, 2),
        "total_items": len(df),
        "matched_count": len(matched),
        "unmatched_count": unmatched,
        "high_confidence": high,
        "medium_confidence": medium,
        "low_confidence": low,
        "match_rate_pct": round(len(matched) / max(len(df), 1) * 100, 1),
        "top_savings_items": top_items,
    }
