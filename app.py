"""
California Department of Public Health: Disease Surveillance Dashboard
Shiny for Python with AI-powered data exploration

Demonstrates:
- querychat for interactive data Q&A (productivity gains for data scientists)
- chatlas with AWS Bedrock for AI features
- Modern Python workflows replacing legacy SAS processes
- Databricks-ready data patterns

This project contains synthetic data created for demonstration purposes only.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from shiny import App, reactive, render, ui
from shinywidgets import render_widget, output_widget
import plotly.express as px
import plotly.graph_objects as go
from chatlas import ChatBedrockAnthropic
import querychat

# Configuration
DATA_PATH = Path(__file__).parent / "data"
CDPH_COLORS = {
    "primary": "#003366",      # California blue
    "secondary": "#FFD700",    # Gold
    "success": "#2E8B57",
    "warning": "#FF8C00",
    "danger": "#DC143C",
    "light": "#F0F8FF",
}

# Initialize chatlas client with AWS Bedrock
chat_client = ChatBedrockAnthropic(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_region="us-west-2",
    max_tokens=1024
)


def load_data():
    """Load all datasets."""
    if not (DATA_PATH / "disease_surveillance.csv").exists():
        import subprocess
        subprocess.run(["python", str(DATA_PATH / "generate_data.py")], check=True)

    surveillance = pd.read_csv(DATA_PATH / "disease_surveillance.csv")
    surveillance["report_date"] = pd.to_datetime(surveillance["report_date"])
    surveillance["onset_date"] = pd.to_datetime(surveillance["onset_date"])

    indicators = pd.read_csv(DATA_PATH / "health_indicators.csv")
    outbreaks = pd.read_csv(DATA_PATH / "outbreak_summary.csv")
    outbreaks["start_date"] = pd.to_datetime(outbreaks["start_date"])

    return surveillance, indicators, outbreaks


surveillance_df, indicators_df, outbreaks_df = load_data()

# Initialize querychat for interactive data Q&A
qc = querychat.QueryChat(
    data_source=surveillance_df,
    table_name="disease_surveillance",
    id="querychat",
    data_description="""California disease surveillance data containing reportable conditions.
    Key columns: county, condition, age_group, severity, hospitalized, lab_confirmed,
    is_outbreak_associated, data_source (includes Legacy SAS, Databricks, etc.), days_to_report.
    Use this to explore disease trends, outbreak patterns, and data quality metrics.
    Data spans 2024-2026 across 20 California counties.""",
    greeting="""Welcome to the CDPH Surveillance Data Assistant!

I can help you explore California's disease surveillance data. Try asking:
- "How many COVID-19 cases were reported in Los Angeles County?"
- "What's the hospitalization rate by age group?"
- "Show me conditions with the highest severity rates"
- "Filter to show only outbreak-associated cases"
- "Compare case counts between data sources (SAS vs Databricks)"

This AI assistant helps data scientists work more efficiently with large surveillance datasets.
""",
    client=chat_client
)


def generate_ai_summary(data_subset, context):
    """Generate AI-powered summary of surveillance data."""
    stats = {
        "total_cases": len(data_subset),
        "conditions": data_subset["condition"].value_counts().head(5).to_dict(),
        "hospitalization_rate": (data_subset["hospitalized"].sum() / len(data_subset) * 100) if len(data_subset) > 0 else 0,
        "lab_confirmed_rate": (data_subset["lab_confirmed"].sum() / len(data_subset) * 100) if len(data_subset) > 0 else 0,
        "avg_days_to_report": data_subset["days_to_report"].mean() if len(data_subset) > 0 else 0,
        "data_sources": data_subset["data_source"].value_counts().to_dict(),
    }

    prompt = f"""You are a public health epidemiologist analyzing California disease surveillance data.

Context: {context}

Data Summary:
- Total cases: {stats['total_cases']:,}
- Top conditions: {stats['conditions']}
- Hospitalization rate: {stats['hospitalization_rate']:.1f}%
- Lab confirmation rate: {stats['lab_confirmed_rate']:.1f}%
- Average days to report: {stats['avg_days_to_report']:.1f}
- Data sources: {stats['data_sources']}

Provide a concise epidemiological summary (under 200 words) highlighting:
1. Key trends and patterns
2. Areas of concern
3. Data quality observations (note the transition from Legacy SAS to modern sources)
4. Recommendations for public health action

Write in a professional tone suitable for a CDPH briefing."""

    try:
        response = chat_client.chat(prompt, echo="none")
        return str(response)
    except Exception as e:
        return f"Error generating AI summary: {str(e)}"


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Filters"),
        ui.input_select(
            "county",
            "County",
            choices=["All"] + sorted(surveillance_df["county"].unique().tolist()),
            selected="All"
        ),
        ui.input_select(
            "condition",
            "Condition",
            choices=["All"] + sorted(surveillance_df["condition"].unique().tolist()),
            selected="All"
        ),
        ui.input_date_range(
            "date_range",
            "Date Range",
            start=surveillance_df["report_date"].min(),
            end=surveillance_df["report_date"].max(),
        ),
        ui.hr(),
        ui.h4("Data Source"),
        ui.input_checkbox_group(
            "data_sources",
            "Include sources:",
            choices=surveillance_df["data_source"].unique().tolist(),
            selected=surveillance_df["data_source"].unique().tolist()
        ),
        ui.hr(),
        ui.download_button("download_data", "Export Data (CSV)", class_="btn-primary w-100"),
        width=280
    ),

    ui.navset_tab(
        ui.nav_panel(
            "Overview",
            ui.layout_columns(
                ui.value_box(
                    "Total Cases",
                    ui.output_text("total_cases"),
                    theme="primary",
                ),
                ui.value_box(
                    "Hospitalizations",
                    ui.output_text("total_hospitalizations"),
                    theme="warning",
                ),
                ui.value_box(
                    "Active Outbreaks",
                    ui.output_text("active_outbreaks"),
                    theme="danger",
                ),
                ui.value_box(
                    "Avg Days to Report",
                    ui.output_text("avg_reporting_time"),
                    theme="info",
                ),
                col_widths=[3, 3, 3, 3]
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Cases Over Time"),
                    output_widget("time_series_plot"),
                ),
                ui.card(
                    ui.card_header("Cases by County"),
                    output_widget("county_map"),
                ),
                col_widths=[7, 5]
            ),
        ),
        ui.nav_panel(
            "Conditions",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Condition Distribution"),
                    output_widget("condition_chart"),
                ),
                ui.card(
                    ui.card_header("Severity by Condition"),
                    output_widget("severity_chart"),
                ),
                col_widths=[6, 6]
            ),
            ui.card(
                ui.card_header("Detailed Case Data"),
                ui.output_data_frame("case_table"),
            ),
        ),
        ui.nav_panel(
            "Data Quality",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Data Source Distribution"),
                    output_widget("source_chart"),
                    ui.p("Track migration progress from Legacy SAS to modern data pipelines",
                         style="font-size: 0.85em; color: #666; margin-top: 10px;"),
                ),
                ui.card(
                    ui.card_header("Reporting Timeliness"),
                    output_widget("timeliness_chart"),
                ),
                col_widths=[6, 6]
            ),
            ui.card(
                ui.card_header("Lab Confirmation Rates by Source"),
                output_widget("lab_confirm_chart"),
            ),
        ),
        ui.nav_panel(
            "AI Summary",
            ui.card(
                ui.card_header("AI-Generated Epidemiological Summary"),
                ui.input_action_button("generate_summary", "Generate Summary", class_="btn-secondary mb-3"),
                ui.output_text_verbatim("ai_summary"),
                ui.p("Powered by Claude on AWS Bedrock via Positron",
                     style="font-size: 0.8em; color: #666; margin-top: 10px;"),
            ),
        ),
        ui.nav_panel(
            "AI Chat",
            ui.p("Ask questions about the surveillance data using natural language. "
                 "This demonstrates how AI assistants in Positron help data scientists "
                 "work more efficiently with large datasets.",
                 style="margin-bottom: 15px; color: #555;"),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Chat with Your Data"),
                    qc.ui(),
                    height="500px",
                ),
                ui.card(
                    ui.card_header("Filtered Data Preview"),
                    ui.output_data_frame("querychat_data"),
                ),
                col_widths=[6, 6]
            ),
        ),
        ui.nav_panel(
            "Outbreaks",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Outbreak Status"),
                    output_widget("outbreak_status_chart"),
                ),
                ui.card(
                    ui.card_header("Outbreaks by Type"),
                    output_widget("outbreak_type_chart"),
                ),
                col_widths=[6, 6]
            ),
            ui.card(
                ui.card_header("Outbreak Investigations"),
                ui.output_data_frame("outbreak_table"),
            ),
        ),
    ),
    title=ui.div(
        ui.img(src="https://www.cdph.ca.gov/PublishingImages/CDPHLogo.png", height="30px", style="margin-right: 10px;"),
        ui.span("CDPH Disease Surveillance Dashboard", style="font-weight: bold;"),
        ui.span(" | Powered by Positron + AI", style="font-size: 0.8em; color: #666;"),
    ),
    fillable=True,
)


def server(input, output, session):
    # Initialize querychat server
    qc_result = qc.server()

    @render.data_frame
    def querychat_data():
        return render.DataGrid(qc_result.df(), selection_mode="none")

    @reactive.calc
    def filtered_data():
        data = surveillance_df.copy()

        if input.county() != "All":
            data = data[data["county"] == input.county()]

        if input.condition() != "All":
            data = data[data["condition"] == input.condition()]

        if input.date_range():
            start, end = input.date_range()
            data = data[(data["report_date"] >= pd.Timestamp(start)) &
                       (data["report_date"] <= pd.Timestamp(end))]

        if input.data_sources():
            data = data[data["data_source"].isin(input.data_sources())]

        return data

    @render.text
    def total_cases():
        return f"{len(filtered_data()):,}"

    @render.text
    def total_hospitalizations():
        return f"{filtered_data()['hospitalized'].sum():,}"

    @render.text
    def active_outbreaks():
        active = outbreaks_df[outbreaks_df["status"].isin(["Active", "Under Investigation"])]
        return f"{len(active)}"

    @render.text
    def avg_reporting_time():
        return f"{filtered_data()['days_to_report'].mean():.1f} days"

    @render_widget
    def time_series_plot():
        data = filtered_data()
        daily = data.groupby(data["report_date"].dt.to_period("W")).size().reset_index()
        daily.columns = ["week", "cases"]
        daily["week"] = daily["week"].astype(str)

        fig = px.line(daily, x="week", y="cases",
                     title="Weekly Case Counts",
                     labels={"week": "Week", "cases": "Cases"})
        fig.update_layout(template="plotly_white", height=350)
        return fig

    @render_widget
    def county_map():
        data = filtered_data()
        county_counts = data.groupby("county").size().reset_index(name="cases")

        fig = px.bar(county_counts.sort_values("cases", ascending=True).tail(15),
                    x="cases", y="county", orientation="h",
                    title="Top 15 Counties by Case Count",
                    color="cases", color_continuous_scale="Blues")
        fig.update_layout(template="plotly_white", height=350, showlegend=False)
        return fig

    @render_widget
    def condition_chart():
        data = filtered_data()
        condition_counts = data.groupby("condition").size().reset_index(name="cases")

        fig = px.pie(condition_counts, values="cases", names="condition",
                    title="Cases by Condition")
        fig.update_layout(height=400)
        return fig

    @render_widget
    def severity_chart():
        data = filtered_data()
        severity = data.groupby(["condition", "severity"]).size().reset_index(name="cases")

        fig = px.bar(severity, x="condition", y="cases", color="severity",
                    title="Severity Distribution by Condition",
                    color_discrete_map={"Mild": "#2E8B57", "Moderate": "#FF8C00", "Severe": "#DC143C"})
        fig.update_layout(template="plotly_white", height=400, xaxis_tickangle=-45)
        return fig

    @render.data_frame
    def case_table():
        data = filtered_data().head(100)
        display_cols = ["case_id", "county", "condition", "age_group", "severity",
                       "hospitalized", "lab_confirmed", "report_date", "data_source"]
        return render.DataGrid(data[display_cols], selection_mode="none")

    @render_widget
    def source_chart():
        data = filtered_data()
        source_counts = data.groupby("data_source").size().reset_index(name="cases")

        colors = {
            "Legacy SAS": "#DC143C",
            "Databricks": "#003366",
            "Direct Entry": "#2E8B57",
            "Lab Feed": "#FF8C00",
            "Hospital EHR": "#FFD700"
        }

        fig = px.bar(source_counts.sort_values("cases", ascending=False),
                    x="data_source", y="cases",
                    title="Cases by Data Source",
                    color="data_source",
                    color_discrete_map=colors)
        fig.update_layout(template="plotly_white", height=350, showlegend=False)
        return fig

    @render_widget
    def timeliness_chart():
        data = filtered_data()
        timeliness = data.groupby("data_source")["days_to_report"].mean().reset_index()

        fig = px.bar(timeliness.sort_values("days_to_report"),
                    x="data_source", y="days_to_report",
                    title="Average Days to Report by Source",
                    color="days_to_report",
                    color_continuous_scale="RdYlGn_r")
        fig.update_layout(template="plotly_white", height=350)
        return fig

    @render_widget
    def lab_confirm_chart():
        data = filtered_data()
        lab_rates = data.groupby("data_source").agg(
            total=("case_id", "count"),
            confirmed=("lab_confirmed", "sum")
        ).reset_index()
        lab_rates["confirmation_rate"] = (lab_rates["confirmed"] / lab_rates["total"] * 100).round(1)

        fig = px.bar(lab_rates, x="data_source", y="confirmation_rate",
                    title="Lab Confirmation Rate by Data Source (%)",
                    color="confirmation_rate",
                    color_continuous_scale="Greens")
        fig.update_layout(template="plotly_white", height=350)
        return fig

    @render.text
    @reactive.event(input.generate_summary)
    def ai_summary():
        data = filtered_data()
        context = f"County: {input.county()}, Condition: {input.condition()}"
        return generate_ai_summary(data, context)

    @render_widget
    def outbreak_status_chart():
        status_counts = outbreaks_df.groupby("status").size().reset_index(name="count")

        fig = px.pie(status_counts, values="count", names="status",
                    title="Outbreak Investigation Status",
                    color="status",
                    color_discrete_map={
                        "Closed": "#2E8B57",
                        "Active": "#DC143C",
                        "Under Investigation": "#FF8C00"
                    })
        fig.update_layout(height=350)
        return fig

    @render_widget
    def outbreak_type_chart():
        type_counts = outbreaks_df.groupby("outbreak_type").agg(
            outbreaks=("outbreak_id", "count"),
            total_cases=("total_cases", "sum")
        ).reset_index()

        fig = px.bar(type_counts, x="outbreak_type", y=["outbreaks", "total_cases"],
                    title="Outbreaks by Type",
                    barmode="group")
        fig.update_layout(template="plotly_white", height=350)
        return fig

    @render.data_frame
    def outbreak_table():
        display_cols = ["outbreak_id", "outbreak_type", "condition", "county",
                       "setting", "status", "total_cases", "hospitalizations", "deaths"]
        return render.DataGrid(outbreaks_df[display_cols].sort_values("start_date", ascending=False),
                              selection_mode="none")

    @render.download(filename="cdph_surveillance_export.csv")
    def download_data():
        yield filtered_data().to_csv(index=False)


app = App(app_ui, server)
