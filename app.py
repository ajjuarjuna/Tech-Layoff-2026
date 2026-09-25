from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Tech Layoff Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Theme / styling
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: #05070D;
        color: #F8FAFC;
    }

    [data-testid="stSidebar"] {
        background: #0A0E18;
        border-right: 1px solid #1E293B;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #111827 0%, #0B1020 55%, #17104A 100%);
        border: 1px solid #26314A;
        margin-bottom: 1.25rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.25rem;
        color: #F8FAFC;
    }

    .hero p {
        margin: 0.45rem 0 0;
        color: #94A3B8;
        font-size: 1rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0.8rem 0 0.7rem;
    }

    div[data-testid="stMetric"] {
        background: #0B1020;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 12px 14px;
    }

    div[data-testid="stMetricLabel"] {
        color: #94A3B8;
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFC;
    }

    .insight {
        background: #0B1020;
        border-left: 3px solid #6366F1;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        color: #CBD5E1;
        margin-top: 0.5rem;
    }

    .small-note {
        color: #64748B;
        font-size: 0.82rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
PLOT_BG = "#05070D"
PAPER_BG = "#05070D"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
PURPLE = "#4338CA"
INDIGO = "#3730A3"
BLUE = "#3B82F6"
ORANGE = "#F59E0B"
GREEN = "#10B981"
RED = "#EF4444"

def style_fig(fig, height=480, title=None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT),
        title=dict(
            text=title,
            x=0.02,
            xanchor="left",
            font=dict(size=18, color="#F8FAFC")
        ) if title else None,
        height=height,
        margin=dict(l=55, r=25, t=65 if title else 25, b=55),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT)
        ),
        hoverlabel=dict(
            bgcolor="#111827",
            font_color="#F8FAFC"
        )
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#334155",
        tickfont=dict(color=MUTED)
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#334155",
        tickfont=dict(color=MUTED)
    )
    return fig

def fmt_int(x):
    return f"{int(round(x)):,}"

def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
    else:
        candidates = [
            "tech_layoffs_2026_tracker.csv",
            "tech_layoffs_2026_tracker(2).csv",
            "dataset/tech_layoffs_2026_tracker.csv",
            "data/tech_layoffs_2026_tracker.csv",
        ]
        data = None
        for path in candidates:
            try:
                data = pd.read_csv(path)
                break
            except FileNotFoundError:
                continue

        if data is None:
            return None

    # Same duplicate logic used in the notebooks
    duplicate_subset = [
        "company", "jobs_cut", "pct_workforce_cut", "sector",
        "country", "hq_city", "ai_cited", "company_revenue_2025_bn",
        "pre_layoff_headcount", "stock_change_day_pct",
        "simultaneous_ai_investment_bn"
    ]
    duplicate_subset = [c for c in duplicate_subset if c in data.columns]
    if duplicate_subset:
        data = data.drop_duplicates(subset=duplicate_subset).copy()

    data["layoff_date"] = pd.to_datetime(data["layoff_date"], errors="coerce")
    data["layoff_month"] = data["layoff_date"].dt.strftime("%b")
    data["month_no"] = data["layoff_date"].dt.month

    # Notebook logic: group AI-mentioned reasons into "AI"
    if "reason_stated" in data.columns:
        data["reason_AI"] = np.where(
            data["reason_stated"].fillna("").str.contains("AI", case=False),
            "AI",
            data["reason_stated"]
        )

    return data


# -----------------------------
# Load data
# -----------------------------
with st.sidebar:
    st.markdown("## 📊 Tech Layoff Intelligence")
    st.caption("Interactive analysis dashboard")

    uploaded = st.file_uploader(
        "Upload layoffs CSV",
        type=["csv"],
        help="If the CSV is in the same folder as app.py, you can leave this empty."
    )

df = load_data(uploaded)

if df is None:
    st.error(
        "CSV not found. Put `tech_layoffs_2026_tracker.csv` in the same folder as `app.py`, "
        "or upload the CSV from the sidebar."
    )
    st.stop()

# -----------------------------
# Sidebar navigation + filters
# -----------------------------
with st.sidebar:
    st.markdown("---")
    page = st.radio(
        "Analysis",
        [
            "Executive Overview",
            "Layoff Trends",
            "AI Impact",
            "Business Impact",
            "Risk Analysis",
            "Company Explorer",
            "Data View"
        ]
    )

    st.markdown("---")
    st.markdown("### Filters")

    sector_options = sorted(df["sector"].dropna().unique())
    selected_sectors = st.multiselect(
        "Sector",
        sector_options,
        default=sector_options
    )

    region_options = sorted(df["region"].dropna().unique())
    selected_regions = st.multiselect(
        "Region",
        region_options,
        default=region_options
    )

    ai_filter = st.selectbox(
        "AI-cited layoffs",
        ["All", "AI Cited", "Non-AI Cited"]
    )

filtered = df[
    df["sector"].isin(selected_sectors)
    & df["region"].isin(selected_regions)
].copy()

if ai_filter == "AI Cited":
    filtered = filtered[filtered["ai_cited"] == True]
elif ai_filter == "Non-AI Cited":
    filtered = filtered[filtered["ai_cited"] == False]

# -----------------------------
# Global KPIs
# -----------------------------
total_jobs = filtered["jobs_cut"].sum()
companies = filtered["company"].nunique()
ai_share = (
    filtered.loc[filtered["ai_cited"] == True, "jobs_cut"].sum() / total_jobs * 100
    if total_jobs else 0
)
avg_workforce_cut = filtered["laid_off_vs_headcount_pct"].mean()
avg_stock = filtered["stock_change_day_pct"].mean()
ai_investment = filtered["simultaneous_ai_investment_bn"].sum()

# -----------------------------
# Hero
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>Tech Layoff Intelligence</h1>
    <p>Data-driven analysis of workforce reductions, AI-cited layoffs, market reaction and sector vulnerability.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Executive Overview
# -----------------------------
if page == "Executive Overview":

    st.markdown('<div class="section-title">Executive Snapshot</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Jobs Cut", fmt_int(total_jobs))
    c2.metric("Companies", fmt_int(companies))
    c3.metric("AI-Cited Share", f"{ai_share:.1f}%")
    c4.metric("Avg Workforce Cut", f"{avg_workforce_cut:.1f}%")
    c5.metric("Avg 1-Day Stock Change", f"{avg_stock:.2f}%")

    st.markdown("### Layoff Scale")

    left, right = st.columns(2)

    with left:
        sector = (
            filtered.groupby("sector", as_index=False)["jobs_cut"]
            .sum()
            .sort_values("jobs_cut", ascending=True)
        )
        fig = px.bar(
            sector,
            x="jobs_cut",
            y="sector",
            orientation="h",
            text="jobs_cut"
        )
        fig.update_traces(
            marker_color=BLUE,
            texttemplate="%{text:,}",
            textposition="outside",
            cliponaxis=False
        )
        fig = style_fig(fig, 470, "Workforce Layoffs by Sector")
        fig.update_xaxes(title="Jobs Cut")
        fig.update_yaxes(title="")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        region = (
            filtered.groupby("region", as_index=False)["jobs_cut"]
            .sum()
            .sort_values("jobs_cut", ascending=False)
        )
        region["share"] = region["jobs_cut"] / region["jobs_cut"].sum() * 100
        fig = px.bar(
            region,
            x="region",
            y="share",
            text="share"
        )
        fig.update_traces(
            marker_color=PURPLE,
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False
        )
        fig = style_fig(fig, 470, "Share of Jobs Cut by Region")
        fig.update_yaxes(title="Share of Total Jobs Cut (%)")
        fig.update_xaxes(title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Key Observations")
    top_sector = sector.iloc[-1] if len(sector) else None
    top_company = (
        filtered.groupby("company", as_index=False)["jobs_cut"]
        .sum()
        .sort_values("jobs_cut", ascending=False)
        .iloc[0]
        if len(filtered) else None
    )

    observations = []
    if top_sector is not None:
        observations.append(
            f"**{top_sector['sector']}** accounts for the largest number of jobs cut in the selected data."
        )
    if top_company is not None:
        observations.append(
            f"**{top_company['company']}** has the largest recorded layoff event at **{fmt_int(top_company['jobs_cut'])} jobs**."
        )
    observations.append(
        f"AI-cited events represent **{ai_share:.1f}%** of jobs cut in the current filter selection."
    )

    for obs in observations:
        st.markdown(f'<div class="insight">{obs}</div>', unsafe_allow_html=True)

# -----------------------------
# Layoff Trends
# -----------------------------
elif page == "Layoff Trends":

    st.markdown('<div class="section-title">Layoff Trends & Workforce Impact</div>', unsafe_allow_html=True)

    monthly = (
        filtered.groupby(["month_no", "layoff_month"], as_index=False)["jobs_cut"]
        .sum()
        .sort_values("month_no")
    )

    fig = px.line(
        monthly,
        x="layoff_month",
        y="jobs_cut",
        markers=True,
        text="jobs_cut"
    )
    fig.update_traces(
        line=dict(color=PURPLE, width=3),
        marker=dict(size=9),
        texttemplate="%{text:,}",
        textposition="top center"
    )
    fig = style_fig(fig, 430, "Q1 2026 Layoff Frequency")
    fig.update_yaxes(title="Jobs Cut")
    fig.update_xaxes(title="")
    st.plotly_chart(fig, use_container_width=True)

    yearly = (
        filtered.groupby(["month_no", "layoff_month"], as_index=False)
        .agg(
            **{
                "2026": ("jobs_cut", "sum"),
                "2024": ("layoffs_2024", "sum"),
                "2025": ("layoffs_2025", "sum")
            }
        )
        .sort_values("month_no")
    )

    yearly_long = yearly.melt(
        id_vars=["month_no", "layoff_month"],
        value_vars=["2024", "2025", "2026"],
        var_name="Year",
        value_name="Jobs Cut"
    )

    fig = px.bar(
        yearly_long,
        x="layoff_month",
        y="Jobs Cut",
        color="Year",
        barmode="group",
        text_auto=True,
        color_discrete_map={
            "2024": "#2563EB",
            "2025": "#DC2626",
            "2026": ORANGE
        }
    )
    fig = style_fig(fig, 470, "Layoffs by Month: 2024 vs 2025 vs 2026")
    fig.update_xaxes(title="")
    st.plotly_chart(fig, use_container_width=True)

    sector_impact = (
        filtered.groupby("sector", as_index=False)["laid_off_vs_headcount_pct"]
        .mean()
        .sort_values("laid_off_vs_headcount_pct")
    )

    fig = px.bar(
        sector_impact,
        x="laid_off_vs_headcount_pct",
        y="sector",
        orientation="h",
        text="laid_off_vs_headcount_pct"
    )
    fig.update_traces(
        marker_color=BLUE,
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False
    )
    fig = style_fig(fig, 520, "Average Workforce Impact by Sector")
    fig.update_xaxes(title="Employees Laid Off (%)")
    fig.update_yaxes(title="")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# AI Impact
# -----------------------------
elif page == "AI Impact":

    st.markdown('<div class="section-title">AI-Cited Layoff Analysis</div>', unsafe_allow_html=True)

    ai_jobs = (
        filtered.groupby("ai_cited", as_index=False)["jobs_cut"]
        .sum()
    )
    ai_jobs["Label"] = ai_jobs["ai_cited"].map({
        True: "AI Cited",
        False: "Non-AI Cited"
    })

    c1, c2 = st.columns(2)

    with c1:
        fig = px.pie(
            ai_jobs,
            names="Label",
            values="jobs_cut",
            hole=0.58,
            color="Label",
            color_discrete_map={
                "AI Cited": ORANGE,
                "Non-AI Cited": INDIGO
            }
        )
        fig = style_fig(fig, 430, "AI-Cited vs Non-AI-Cited Share")
        fig.update_traces(
            textinfo="percent",
            textfont=dict(color="#000000", size=14)
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        stock = filtered.groupby("ai_cited")["stock_change_day_pct"].agg(
            mean="mean",
            median="median"
        ).reset_index()
        stock["Layoff Type"] = stock["ai_cited"].map({
            True: "AI Cited",
            False: "Non-AI Cited"
        })
        stock_long = stock.melt(
            id_vars=["Layoff Type"],
            value_vars=["mean", "median"],
            var_name="Statistic",
            value_name="Stock Change (%)"
        )

        fig = px.bar(
            stock_long,
            x="Layoff Type",
            y="Stock Change (%)",
            color="Statistic",
            barmode="group",
            text="Stock Change (%)",
            color_discrete_map={
                "mean": INDIGO,
                "median": ORANGE
            }
        )
        fig.add_hline(y=0, line_color="#CBD5E1", line_width=1)
        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False
        )
        fig = style_fig(fig, 430, "Mean vs Median Stock Reaction")
        st.plotly_chart(fig, use_container_width=True)

    size = (
        filtered.pivot_table(
            index="layoff_size_category",
            columns="ai_cited",
            values="jobs_cut",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
        .rename(columns={
            False: "Non-AI Cited",
            True: "AI Cited"
        })
    )

    size_long = size.melt(
        id_vars="layoff_size_category",
        var_name="Layoff Type",
        value_name="Jobs Cut"
    )

    fig = px.bar(
        size_long,
        x="Jobs Cut",
        y="layoff_size_category",
        color="Layoff Type",
        orientation="h",
        barmode="group",
        color_discrete_map={
            "Non-AI Cited": INDIGO,
            "AI Cited": ORANGE
        }
    )
    fig = style_fig(fig, 470, "AI-Cited vs Non-AI-Cited Layoffs by Size")
    fig.update_yaxes(title="")
    st.plotly_chart(fig, use_container_width=True)

    if "reason_AI" in filtered.columns:
        reasons = (
            filtered.groupby("reason_AI", as_index=False)["jobs_cut"]
            .sum()
            .sort_values("jobs_cut")
        )
        reasons["share"] = reasons["jobs_cut"] / reasons["jobs_cut"].sum() * 100

        fig = px.bar(
            reasons,
            x="reason_AI",
            y="share",
            text="share"
        )
        fig.update_traces(
            marker_color=PURPLE,
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False
        )
        fig = style_fig(fig, 500, "Distribution of Job Cuts by Reason")
        fig.update_xaxes(title="", tickangle=-35)
        fig.update_yaxes(title="Percentage of Total Job Cuts")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f'<div class="insight">In the selected data, AI-cited events account for '
        f'<b>{ai_share:.1f}%</b> of total jobs cut. The stock-reaction chart shows the '
        f'descriptive difference between the one-day reactions recorded in the dataset.</div>',
        unsafe_allow_html=True
    )

# -----------------------------
# Business Impact
# -----------------------------
elif page == "Business Impact":

    st.markdown('<div class="section-title">Company-Level Business Impact</div>', unsafe_allow_html=True)

    revenue = filtered[
        ["company", "jobs_cut", "company_revenue_2025_bn"]
    ].copy()

    fig = px.scatter(
        revenue,
        x="company_revenue_2025_bn",
        y="jobs_cut",
        size="jobs_cut",
        hover_name="company",
        text="company",
        color_discrete_sequence=[PURPLE]
    )
    fig.update_traces(
        textposition="top center",
        textfont=dict(size=10, color=TEXT),
        marker=dict(opacity=0.72)
    )
    fig = style_fig(fig, 520, "Layoffs vs 2025 Revenue")
    fig.update_xaxes(title="Revenue in USD Billion")
    fig.update_yaxes(title="Jobs Cut")
    st.plotly_chart(fig, use_container_width=True)

    investment = filtered[
        ["company", "jobs_cut", "simultaneous_ai_investment_bn"]
    ].copy()

    fig = px.scatter(
        investment,
        x="simultaneous_ai_investment_bn",
        y="jobs_cut",
        size="jobs_cut",
        hover_name="company",
        text="company",
        color_discrete_sequence=[INDIGO]
    )
    fig.update_traces(
        textposition="top center",
        textfont=dict(size=10, color=TEXT),
        marker=dict(opacity=0.72)
    )
    fig = style_fig(fig, 520, "AI Investment vs Jobs Cut")
    fig.update_xaxes(title="Simultaneous AI Investment (USD Billion)")
    fig.update_yaxes(title="Jobs Cut")
    st.plotly_chart(fig, use_container_width=True)

    top_layoffs = (
        filtered.groupby("company", as_index=False)["jobs_cut"]
        .sum()
        .sort_values("jobs_cut", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_layoffs.sort_values("jobs_cut"),
        x="jobs_cut",
        y="company",
        orientation="h",
        text="jobs_cut"
    )
    fig.update_traces(
        marker_color=BLUE,
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False
    )
    fig = style_fig(fig, 500, "Largest Recorded Layoff Events")
    fig.update_xaxes(title="Jobs Cut")
    fig.update_yaxes(title="")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="insight">The notebook analysis describes no clear relationship between '
        'simultaneous AI investment and jobs cut, and no clear strong relationship between '
        'company revenue and jobs cut in this dataset.</div>',
        unsafe_allow_html=True
    )

# -----------------------------
# Risk Analysis
# -----------------------------
elif page == "Risk Analysis":

    st.markdown('<div class="section-title">AI-Driven Layoff Vulnerability</div>', unsafe_allow_html=True)

    # Same methodology as Advance_Analysis notebook:
    # AI Layoff Intensity 40% + Layoff Impact 35% + AI Investment 25%
    ai_intensity = filtered.groupby("sector")["ai_cited"].mean().mul(100)
    layoff_impact = filtered.groupby("sector")["jobs_cut"].sum()
    ai_investment_by_sector = filtered.groupby("sector")[
        "simultaneous_ai_investment_bn"
    ].mean()

    risk = pd.DataFrame({
        "AI_Layoff_Intensity": ai_intensity,
        "Layoff_Impact": layoff_impact,
        "AI_Investment": ai_investment_by_sector
    }).dropna()

    if len(risk) >= 1:
        for col in ["AI_Layoff_Intensity", "Layoff_Impact", "AI_Investment"]:
            min_v = risk[col].min()
            max_v = risk[col].max()
            if max_v == min_v:
                risk[col] = 0
            else:
                risk[col] = (risk[col] - min_v) / (max_v - min_v) * 100

        risk["risk_score"] = (
            risk["AI_Layoff_Intensity"] * 0.40
            + risk["Layoff_Impact"] * 0.35
            + risk["AI_Investment"] * 0.25
        ).round(2)

        risk = risk.sort_values("risk_score", ascending=True)

        fig = px.bar(
            risk.reset_index(),
            x="risk_score",
            y="sector",
            orientation="h",
            text="risk_score"
        )
        fig.update_traces(
            marker_color=INDIGO,
            texttemplate="%{text:.2f}",
            textposition="outside",
            cliponaxis=False
        )
        fig = style_fig(fig, 560, "AI-Driven Layoff Vulnerability by Sector")
        fig.update_xaxes(title="Risk Score")
        fig.update_yaxes(title="")
        st.plotly_chart(fig, use_container_width=True)

        display_risk = risk.reset_index()[
            ["sector", "AI_Layoff_Intensity", "Layoff_Impact", "AI_Investment", "risk_score"]
        ].sort_values("risk_score", ascending=False)

        display_risk.columns = [
            "Sector",
            "AI Layoff Intensity",
            "Layoff Impact",
            "AI Investment",
            "Risk Score"
        ]

        st.dataframe(
            display_risk.style.format({
                "AI Layoff Intensity": "{:.1f}",
                "Layoff Impact": "{:.1f}",
                "AI Investment": "{:.1f}",
                "Risk Score": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Risk score follows the methodology used in the advanced notebook: "
            "40% AI layoff intensity, 35% layoff impact and 25% average AI investment. "
            "The components are Min-Max scaled within the current selection."
        )
    else:
        st.info("Not enough sector data for the risk calculation.")

# -----------------------------
# Company Explorer
# -----------------------------
elif page == "Company Explorer":

    st.markdown('<div class="section-title">Company Explorer</div>', unsafe_allow_html=True)

    company_options = sorted(filtered["company"].unique())
    selected_company = st.selectbox("Select a company", company_options)

    company_row = filtered[filtered["company"] == selected_company].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jobs Cut", fmt_int(company_row["jobs_cut"]))
    c2.metric("Workforce Cut", f"{company_row['laid_off_vs_headcount_pct']:.1f}%")
    c3.metric("Stock Change", f"{company_row['stock_change_day_pct']:.2f}%")
    c4.metric("AI Investment", f"${company_row['simultaneous_ai_investment_bn']:.1f}B")

    left, right = st.columns(2)

    with left:
        st.markdown("#### Company Profile")
        profile = pd.DataFrame({
            "Field": [
                "Sector", "Country", "HQ City", "Layoff Date",
                "AI Cited", "Layoff Size", "Revenue 2025"
            ],
            "Value": [
                company_row["sector"],
                company_row["country"],
                company_row["hq_city"],
                company_row["layoff_date"].strftime("%d %b %Y") if pd.notna(company_row["layoff_date"]) else "—",
                "Yes" if company_row["ai_cited"] else "No",
                company_row["layoff_size_category"],
                f"${company_row['company_revenue_2025_bn']:.1f}B"
            ]
        })
        st.dataframe(profile, use_container_width=True, hide_index=True)

    with right:
        st.markdown("#### Workforce & Role Impact")
        role_data = pd.DataFrame({
            "Field": [
                "Roles Most Affected",
                "Replacement Roles",
                "Reason",
                "CEO Quote"
            ],
            "Details": [
                company_row["roles_most_affected"],
                company_row["replacement_roles"],
                company_row["reason_stated"],
                company_row["ceo_quote"]
            ]
        })
        st.dataframe(role_data, use_container_width=True, hide_index=True)

# -----------------------------
# Data View
# -----------------------------
elif page == "Data View":

    st.markdown('<div class="section-title">Dataset Explorer</div>', unsafe_allow_html=True)

    st.write(
        f"Showing **{len(filtered):,}** rows from the current filter selection."
    )

    display_cols = [
        "company", "layoff_date", "jobs_cut", "pct_workforce_cut",
        "sector", "country", "ai_cited", "reason_stated",
        "company_revenue_2025_bn", "stock_change_day_pct",
        "simultaneous_ai_investment_bn", "layoff_size_category"
    ]
    display_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[display_cols].sort_values("jobs_cut", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data",
        data=csv,
        file_name="filtered_tech_layoffs.csv",
        mime="text/csv"
    )

st.markdown(
    '<div class="small-note">Source: Tech Layoff Analysis dataset provided for this project. '
    'Figures are descriptive summaries of the available records.</div>',
    unsafe_allow_html=True
)
