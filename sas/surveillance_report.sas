/**************************************************
* CDPH Disease Surveillance Weekly Report
*
* This SAS program generates weekly surveillance summaries
* that feed into R Shiny dashboards and Quarto reports.
*
* MIGRATION NOTE: This legacy SAS code is being transitioned
* to Python/R workflows. The output CSV format remains
* consistent to support the transition period.
*
* Output: data/sas_weekly_summary.csv
**************************************************/

/* Set library references */
LIBNAME cdph '/data/surveillance';
LIBNAME output '/data/reports';

/* Define reporting period */
%LET report_start = '01JAN2026'd;
%LET report_end = '07JAN2026'd;
%LET report_week = 1;
%LET report_year = 2026;

/* Read surveillance data */
DATA work.surveillance;
    SET cdph.disease_cases;
    WHERE report_date BETWEEN &report_start AND &report_end;

    /* Standardize condition names */
    condition_std = UPCASE(STRIP(condition));

    /* Calculate days to report */
    days_to_report = report_date - onset_date;

    /* Flag timeliness */
    IF days_to_report <= 3 THEN timeliness_flag = 'On Time';
    ELSE IF days_to_report <= 7 THEN timeliness_flag = 'Delayed';
    ELSE timeliness_flag = 'Late';
RUN;

/* Generate county-level summary */
PROC SQL;
    CREATE TABLE work.county_summary AS
    SELECT
        county,
        COUNT(*) AS total_cases,
        SUM(CASE WHEN hospitalized = 1 THEN 1 ELSE 0 END) AS hospitalizations,
        SUM(CASE WHEN icu_admission = 1 THEN 1 ELSE 0 END) AS icu_admissions,
        SUM(CASE WHEN outcome = 'Deceased' THEN 1 ELSE 0 END) AS deaths,
        SUM(CASE WHEN lab_confirmed = 1 THEN 1 ELSE 0 END) AS lab_confirmed,
        MEAN(days_to_report) AS avg_days_to_report FORMAT=5.1,
        SUM(CASE WHEN timeliness_flag = 'On Time' THEN 1 ELSE 0 END) / COUNT(*) * 100
            AS pct_timely FORMAT=5.1
    FROM work.surveillance
    GROUP BY county
    ORDER BY total_cases DESC;
QUIT;

/* Generate condition-level summary */
PROC SQL;
    CREATE TABLE work.condition_summary AS
    SELECT
        condition_std AS condition,
        COUNT(*) AS total_cases,
        SUM(CASE WHEN severity = 'Severe' THEN 1 ELSE 0 END) AS severe_cases,
        SUM(CASE WHEN hospitalized = 1 THEN 1 ELSE 0 END) AS hospitalizations,
        CALCULATED hospitalizations / COUNT(*) * 100 AS hosp_rate FORMAT=5.1,
        SUM(CASE WHEN is_outbreak_associated = 1 THEN 1 ELSE 0 END) AS outbreak_cases
    FROM work.surveillance
    GROUP BY condition_std
    ORDER BY total_cases DESC;
QUIT;

/* Generate age group analysis */
PROC SQL;
    CREATE TABLE work.age_summary AS
    SELECT
        age_group,
        COUNT(*) AS total_cases,
        SUM(CASE WHEN hospitalized = 1 THEN 1 ELSE 0 END) AS hospitalizations,
        CALCULATED hospitalizations / COUNT(*) * 100 AS hosp_rate FORMAT=5.1,
        SUM(CASE WHEN outcome = 'Deceased' THEN 1 ELSE 0 END) AS deaths,
        CALCULATED deaths / COUNT(*) * 100 AS cfr FORMAT=5.2
    FROM work.surveillance
    GROUP BY age_group;
QUIT;

/* Generate weekly trend data */
PROC SQL;
    CREATE TABLE work.daily_trend AS
    SELECT
        report_date,
        COUNT(*) AS daily_cases,
        SUM(CASE WHEN hospitalized = 1 THEN 1 ELSE 0 END) AS daily_hosp
    FROM work.surveillance
    GROUP BY report_date
    ORDER BY report_date;
QUIT;

/* Export summaries to CSV for R/Python consumption */
PROC EXPORT DATA=work.county_summary
    OUTFILE='/data/reports/sas_county_summary.csv'
    DBMS=CSV REPLACE;
RUN;

PROC EXPORT DATA=work.condition_summary
    OUTFILE='/data/reports/sas_condition_summary.csv'
    DBMS=CSV REPLACE;
RUN;

PROC EXPORT DATA=work.age_summary
    OUTFILE='/data/reports/sas_age_summary.csv'
    DBMS=CSV REPLACE;
RUN;

PROC EXPORT DATA=work.daily_trend
    OUTFILE='/data/reports/sas_daily_trend.csv'
    DBMS=CSV REPLACE;
RUN;

/* Create combined weekly summary for Quarto/Shiny */
DATA work.weekly_summary;
    LENGTH metric $50 value 8 category $30;

    /* Overall metrics */
    metric = 'Total Cases'; value = &total_cases; category = 'Overall'; OUTPUT;
    metric = 'Hospitalizations'; value = &total_hosp; category = 'Overall'; OUTPUT;
    metric = 'Deaths'; value = &total_deaths; category = 'Overall'; OUTPUT;
    metric = 'Lab Confirmed (%)'; value = &pct_lab; category = 'Quality'; OUTPUT;
    metric = 'Timely Reporting (%)'; value = &pct_timely; category = 'Quality'; OUTPUT;

    /* Week metadata */
    metric = 'Report Week'; value = &report_week; category = 'Metadata'; OUTPUT;
    metric = 'Report Year'; value = &report_year; category = 'Metadata'; OUTPUT;
RUN;

PROC EXPORT DATA=work.weekly_summary
    OUTFILE='/data/reports/sas_weekly_summary.csv'
    DBMS=CSV REPLACE;
RUN;

/* Generate formatted PDF report (legacy format) */
ODS PDF FILE='/data/reports/weekly_surveillance_report.pdf' STYLE=journal;

TITLE1 "California Department of Public Health";
TITLE2 "Weekly Disease Surveillance Report";
TITLE3 "Week &report_week, &report_year";

PROC PRINT DATA=work.county_summary NOOBS LABEL;
    LABEL county = 'County'
          total_cases = 'Total Cases'
          hospitalizations = 'Hospitalizations'
          deaths = 'Deaths'
          pct_timely = '% Timely';
    TITLE4 "Cases by County";
RUN;

PROC PRINT DATA=work.condition_summary NOOBS LABEL;
    LABEL condition = 'Condition'
          total_cases = 'Cases'
          severe_cases = 'Severe'
          hosp_rate = 'Hosp Rate (%)';
    TITLE4 "Cases by Condition";
RUN;

PROC SGPLOT DATA=work.daily_trend;
    SERIES X=report_date Y=daily_cases / MARKERS;
    XAXIS LABEL='Date';
    YAXIS LABEL='Daily Cases';
    TITLE 'Daily Case Trend';
RUN;

ODS PDF CLOSE;

/* Log completion */
%PUT NOTE: Weekly surveillance report generated successfully.;
%PUT NOTE: CSV outputs ready for R Shiny and Quarto consumption.;
%PUT NOTE: Report period: &report_start to &report_end;

/**************************************************
* MIGRATION NOTES FOR PYTHON/R TEAM:
*
* This SAS code outputs CSV files that can be read by:
* - R: read_csv("sas_weekly_summary.csv")
* - Python: pd.read_csv("sas_weekly_summary.csv")
*
* The Quarto report (reports/weekly_report.qmd) and
* R Shiny app (app.R) are designed to consume these
* CSV outputs during the transition period.
*
* Target state: Direct database queries in R/Python
* replacing SAS data steps and PROC SQL.
**************************************************/
