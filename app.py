from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Tech Layoff Analysis", page_icon="📊", layout="wide")

st.title("📊 Tech Layoff Analysis")
st.caption("Analysis based on the Loading & Cleaning & Basic Analysis notebook")

# -----------------------------
# Data Loading
# -----------------------------
st.sidebar.header("Data")
uploaded_file = st.sidebar.file_uploader("Upload the tech layoffs CSV", type=["csv"])
default_file = Path("tech_layoffs_2026_tracker.csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif default_file.exists():
    df = pd.read_csv(default_file)
else:
    st.info("Upload your `tech_layoffs_2026_tracker.csv` file from the sidebar to view the analysis.")
    st.stop()

# -----------------------------
# Cleaning
# -----------------------------
duplicate_columns = [
    "company", "jobs_cut", "pct_workforce_cut", "sector", "country",
    "hq_city", "ai_cited", "company_revenue_2025_bn", "pre_layoff_headcount",
    "stock_change_day_pct", "simultaneous_ai_investment_bn"
]

duplicate_count = df.duplicated(subset=duplicate_columns).sum()
df = df.drop_duplicates(subset=duplicate_columns).copy()
df["layoff_date"] = pd.to_datetime(df["layoff_date"], errors="coerce")
df["reason_AI"] = df["reason_stated"].apply(lambda x: "AI" if "AI" in str(x) else x)


# -----------------------------
# Page Navigation
# -----------------------------
st.sidebar.divider()
page = st.sidebar.radio(
    "Analysis",
    ["Basic Analysis", "Advanced Analysis"]
)

if page == "Basic Analysis":

    # -----------------------------
    # Overview
    # -----------------------------
    st.header("Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Companies", df["company"].nunique())
    col2.metric("Total Jobs Cut", f"{df['jobs_cut'].sum():,.0f}")
    col3.metric("Rows", f"{len(df):,}")
    col4.metric("Columns", f"{df.shape[1]:,}")

    st.divider()

    # -----------------------------
    # Data Cleaning
    # -----------------------------
    st.header("Data Cleaning")
    col1, col2, col3 = st.columns(3)
    col1.metric("Original Rows", len(df) + duplicate_count)
    col2.metric("Duplicate Rows Removed", duplicate_count)
    col3.metric("Rows After Cleaning", len(df))

    with st.expander("View Data Types"):
        dtype_df = pd.DataFrame({"Column": df.columns, "Data Type": df.dtypes.astype(str).values})
        st.dataframe(dtype_df, use_container_width=True)

    with st.expander("View Cleaned Dataset"):
        st.dataframe(df, use_container_width=True)

    st.info(
        "The notebook identified duplicate records using company and layoff-related "
        "columns, removed them, and converted `layoff_date` from string to datetime."
    )

    st.divider()

    # -----------------------------
    # 1. Sector Analysis
    # -----------------------------
    st.header("1. Workforce Cut Based on Sectors")
    sector_job_cuts = df.groupby("sector")["jobs_cut"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    norm = mpl.colors.PowerNorm(gamma=0.5, vmin=sector_job_cuts.min(), vmax=sector_job_cuts.max())
    colors = mpl.cm.Blues(norm(sector_job_cuts.values))
    ax.barh(sector_job_cuts.index, sector_job_cuts.values, height=0.8, color=colors)
    ax.tick_params(axis="y", labelsize=9)

    for i, value in enumerate(sector_job_cuts.values):
        ax.text(value + max(sector_job_cuts.values) * 0.01, i, f"{value:,.0f}", va="center", size=9)

    ax.grid(False)
    ax.set_xlabel("Number of Jobs")
    ax.set_title("Workforce Layoffs in Different Sectors")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    with st.expander("View Sector Data"):
        st.dataframe(sector_job_cuts.sort_values(ascending=False).rename("jobs_cut"), use_container_width=True)

    st.divider()

    # -----------------------------
    # 2. AI Investment vs Jobs Cut
    # -----------------------------
    st.header("2. AI Investment vs Jobs Cut")
    ai_investment_job_cut = df[["company", "simultaneous_ai_investment_bn", "jobs_cut"]].sort_values("simultaneous_ai_investment_bn")
    top5_investors = ai_investment_job_cut.tail(5).index.to_list()

    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=ai_investment_job_cut,
        x="simultaneous_ai_investment_bn",
        y="jobs_cut",
        size="jobs_cut",
        sizes=(50, 500),
        alpha=0.7,
        legend=False,
        ax=ax
    )

    for index in top5_investors:
        row = ai_investment_job_cut.loc[index]
        ax.text(row["simultaneous_ai_investment_bn"] + 2, row["jobs_cut"], row["company"], size=9)

    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x / 1000:.0f}K"))
    ax.tick_params(axis="y", which="major", left=True, right=False, length=6, width=1.2, color="black")
    ax.tick_params(axis="x", which="major", bottom=True, right=False, length=6, width=1.2, color="black")
    sns.despine(ax=ax)
    ax.set_title("AI Investment vs Jobs Cut", size=13)
    ax.set_ylabel("Number of Layoffs", size=9)
    ax.set_xlabel("USD in Billions Invested by Companies", size=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Notebook Insights")
    st.markdown(
        "- Major tech companies making massive AI investments (over $40 billion) "
        "all show significant layoffs of 15,000 or more, though the highest "
        "spenders don't necessarily have the most layoffs."
    )
    st.markdown(
        "- No clear relationship is observed between simultaneous AI investment "
        "and the number of jobs cut."
    )
    st.markdown(
        "- Oracle stands out as an outlier, recording the highest number of layoffs "
        "(~30K) despite a mid-tier AI investment level (~$40B), indicating aggressive "
        "operational restructuring relative to its spending."
    )

    st.divider()

    # -----------------------------
    # 3. Revenue vs Jobs Cut
    # -----------------------------
    st.header("3. Revenue vs Jobs Cut")
    df_rev_jc = df[["company", "jobs_cut", "company_revenue_2025_bn"]]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x / 1000:.0f}K"))
    sns.scatterplot(data=df_rev_jc, x="company_revenue_2025_bn", y="jobs_cut", ax=ax)

    comp_list = df_rev_jc.sort_values("jobs_cut", ascending=False).head(5)["company"].to_list()
    for company in comp_list:
        row = df_rev_jc[df_rev_jc["company"] == company].iloc[0]
        ax.text(row["company_revenue_2025_bn"] + 5, row["jobs_cut"] + 100, company)

    sns.despine(ax=ax)
    ax.set_title("Variation in Layoffs by Revenue Last Year")
    ax.set_ylabel("Number of Jobs")
    ax.set_xlabel("Revenue in USD Billion")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Notebook Insight")
    st.write(
        "There is no clear or strong correlation between a company's revenue "
        "and the number of jobs cut in their layoffs. The data shows that "
        "layoff sizes are driven by other company-specific factors rather "
        "than being directly proportional to how much revenue a company generates."
    )

    st.divider()

    # -----------------------------
    # 4. AI-related Job Cuts
    # -----------------------------
    st.header("4. How Many Jobs Are Replaced by AI")
    df_cut_count = df.groupby("reason_AI")[["jobs_cut"]].sum()
    total_jobs_cut = df["jobs_cut"].sum()
    df_cut_count["total_jobs_cut"] = total_jobs_cut
    df_cut_count["percentage_job_cut_reason"] = (
        df_cut_count["jobs_cut"] / df_cut_count["total_jobs_cut"] * 100
    ).round(2)
    df_cut_count_p = df_cut_count.sort_values("percentage_job_cut_reason")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df_cut_count_p.index, df_cut_count_p["percentage_job_cut_reason"])

    for i, value in enumerate(df_cut_count_p["percentage_job_cut_reason"]):
        ax.text(value + 0.2, i, f"{value:.2f}%", va="center")

    ax.set_xlabel("Percentage of Total Job Cuts")
    ax.set_ylabel("")
    ax.set_title("Job Cuts by Reason")
    sns.despine(ax=ax)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Notebook Insight")
    st.write(
        "AI-related reasons account for 61.88% of total job cuts, significantly "
        "higher than any individual non-AI reason. The remaining cuts are mainly "
        "associated with bureaucracy reduction, restructuring, cost reduction, "
        "and market slowdown."
    )

    with st.expander("View Breakdown"):
        st.dataframe(
            df_cut_count_p[["jobs_cut", "percentage_job_cut_reason"]].sort_values(
                "percentage_job_cut_reason", ascending=False
            ),
            use_container_width=True
        )

else:
    # ========================================================
    # ADVANCED ANALYSIS
    # Based on Advance_Analysis.ipynb
    # ========================================================

    st.title("📈 Advanced Analysis")
    st.caption("Analysis based on the Advance_Analysis notebook")

    # --------------------------------------------------------
    # 1. Q1 2026 Layoff Frequency
    # --------------------------------------------------------
    st.header("1. Q1 2026 Layoff Frequency")

    df["layoff_month"] = df["layoff_date"].dt.strftime("%b")

    df_month = (
        df.groupby("layoff_month")["jobs_cut"]
        .sum()
        .reset_index()
    )

    df_month["month_no"] = pd.to_datetime(
        df_month["layoff_month"],
        format="%b"
    ).dt.month

    df_month = (
        df_month
        .sort_values("month_no")
        .drop(columns="month_no")
        .set_index("layoff_month")
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    df_month.plot(
        kind="line",
        marker="o",
        legend=False,
        ax=ax
    )

    ax.set_title("First Quarter Layoffs 2026")
    ax.set_xlabel("")
    ax.set_ylabel("Number of Jobs Cut")
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: f"{x/1000:.0f}K")
    )

    for i, value in enumerate(df_month["jobs_cut"]):
        ax.text(
            i + 0.03,
            value,
            f"{value:,.0f}",
            va="bottom"
        )

    sns.despine(ax=ax)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "February saw a sharp spike in reported layoffs, largely driven by "
        "Oracle, while March returned to a much lower level."
    )

    st.divider()

    # --------------------------------------------------------
    # 2. Layoffs by Month - 2024, 2025 and 2026
    # --------------------------------------------------------
    st.header("2. Layoffs in Each Month — 2024 vs 2025 vs 2026")

    df_months_years = (
        df.groupby("layoff_month")[
            ["jobs_cut", "layoffs_2024", "layoffs_2025"]
        ]
        .sum()
        .reset_index()
    )

    df_months_years["month_no"] = pd.to_datetime(
        df_months_years["layoff_month"],
        format="%b"
    ).dt.month

    df_months_years = (
        df_months_years
        .sort_values("month_no")
        .drop(columns="month_no")
        .rename(
            columns={
                "jobs_cut": "2026",
                "layoffs_2024": "2024",
                "layoffs_2025": "2025"
            }
        )
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    df_months_years.plot(
        kind="bar",
        x="layoff_month",
        ax=ax
    )

    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: f"{x/1000:.0f}K")
    )

    ax.set_title("Layoffs in Each Year by Month")
    ax.set_ylabel("Jobs Cut")
    ax.set_xlabel("")

    plt.xticks(rotation=0)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "Q1 2026 shows a significantly higher level of reported layoffs "
        "compared with Q1 2024 and Q1 2025, with the gap widening sharply "
        "in February. However, the February spike is heavily influenced "
        "by Oracle's large layoff event, while March still remains "
        "substantially above the previous two years."
    )

    st.divider()

    # --------------------------------------------------------
    # 3. AI-Cited vs Non-AI-Cited Layoffs by Size
    # --------------------------------------------------------
    st.header("3. AI-Cited vs Non-AI-Cited Layoffs by Size")

    df_pivoted_size = (
        df.pivot_table(
            index="layoff_size_category",
            columns="ai_cited",
            values="jobs_cut",
            aggfunc="sum"
        )
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    df_pivoted_size.plot(
        kind="barh",
        ax=ax
    )

    ax.set_title("AI-Cited vs Non-AI-Cited Layoffs by Size")
    ax.set_xlabel("Jobs Cut")
    ax.set_ylabel("")
    ax.legend(title="AI-Cited")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "AI-cited layoffs were more prominent in higher-size categories, "
        "exceeding non-AI layoffs in both Large and Mega layoffs, while "
        "non-AI layoffs were higher in Small and Medium categories. "
        "However, the Mega AI category is heavily influenced by Oracle's "
        "30K job reduction."
    )

    st.divider()

    # --------------------------------------------------------
    # 4. AI-Cited vs Non-AI-Cited Share
    # --------------------------------------------------------
    st.header("4. AI-Cited vs Non-AI-Cited Total Jobs Cut")

    ai_contribution = df.groupby("ai_cited")["jobs_cut"].sum()
    ai_contribution.index = ["AI-Cited" if x else "Non-AI-Cited" for x in ai_contribution.index]

    fig, ax = plt.subplots(figsize=(4, 4))

    ai_contribution.plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=90,
        radius=0.7,
        ax=ax
    )

    ax.set_ylabel("")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "AI-cited layoffs accounted for 61.9% of total jobs cut, compared "
        "with 38.1% for non-AI-cited layoffs."
    )

    st.divider()

    # --------------------------------------------------------
    # 5. Stock Reaction
    # --------------------------------------------------------
    st.header("5. Stock Reaction to AI-Cited vs Non-AI-Cited Layoffs")

    stock_stats = (
        df.groupby("ai_cited")["stock_change_day_pct"]
        .agg(mean="mean", median="median")
    )

    stock_stats.index = ["Non-AI Cited", "AI Cited"]

    fig, ax = plt.subplots(figsize=(8, 5))

    stock_stats.plot(
        kind="bar",
        ax=ax
    )

    ax.axhline(0, linewidth=0.8)
    ax.set_xlabel("Layoff Type")
    ax.set_ylabel("Stock Change (%)")
    ax.set_title("Mean vs Median Stock Reaction")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Statistic")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "AI-cited layoffs were associated with a positive stock reaction, "
        "with both mean and median changes around +1.9%. In contrast, "
        "non-AI-cited layoffs showed a slight negative reaction, with a "
        "mean of -0.15% and median of -0.3%."
    )

    st.divider()

    # --------------------------------------------------------
    # 6. AI-Driven Layoff Vulnerability by Sector
    # --------------------------------------------------------
    st.header("6. AI-Driven Layoff Vulnerability by Sector")

    ai_intensity = (
        df.groupby("sector")["ai_cited"]
        .mean()
        .mul(100)
    )

    layoff_impact = (
        df.groupby("sector")["jobs_cut"]
        .sum()
    )

    ai_investment = (
        df.groupby("sector")["simultaneous_ai_investment_bn"]
        .mean()
    )

    risk = pd.DataFrame({
        "AI_Layoff_Intensity": ai_intensity,
        "Layoff_Impact": layoff_impact,
        "AI_Investment": ai_investment
    }).dropna()

    # Same Min-Max scaling logic used in the notebook
    for column in [
        "AI_Layoff_Intensity",
        "Layoff_Impact",
        "AI_Investment"
    ]:
        col_min = risk[column].min()
        col_max = risk[column].max()

        if col_max == col_min:
            risk[column] = 0
        else:
            risk[column] = (
                (risk[column] - col_min)
                / (col_max - col_min)
                * 100
            )

    risk["risk_score"] = (
        risk["AI_Layoff_Intensity"] * 0.4
        + risk["Layoff_Impact"] * 0.35
        + risk["AI_Investment"] * 0.25
    ).round(2)

    risk = risk.sort_values("risk_score", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 6))

    risk["risk_score"].plot(
        kind="barh",
        ax=ax
    )

    ax.set_xlabel("Risk Score")
    ax.set_ylabel("")
    ax.set_title("AI-Driven Layoff Vulnerability by Sector")
    ax.invert_yaxis()

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "The notebook's composite score combines AI layoff intensity, "
        "layoff impact and AI investment using weights of 40%, 35% and "
        "25%, respectively."
    )

    with st.expander("View Sector Risk Calculation"):
        st.dataframe(risk, use_container_width=True)

    st.divider()

    # --------------------------------------------------------
    # 7. Company-level AI Spend vs Jobs Cut
    # --------------------------------------------------------
    st.header("7. Company-level AI Spend vs Jobs Cut")

    company_ai = (
        df[
            [
                "company",
                "jobs_cut",
                "simultaneous_ai_investment_bn"
            ]
        ]
        .sort_values("jobs_cut")
    )

    st.dataframe(
        company_ai,
        use_container_width=True,
        hide_index=True
    )

