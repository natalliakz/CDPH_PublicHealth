#' California Department of Public Health: Disease Surveillance Dashboard
#' R Shiny Implementation
#'
#' This R Shiny app complements the Python version and demonstrates:
#' - Reading outputs from legacy SAS workflows
#' - Modern R-based surveillance analytics
#' - Integration with Quarto reports
#'
#' DISCLAIMER: This project contains synthetic data for demonstration only.

library(shiny)
library(bslib)
library(dplyr)
library(tidyr)
library(ggplot2)
library(plotly)
library(DT)
library(readr)
library(lubridate)
library(scales)

# Configuration
CDPH_COLORS <- list(
  primary = "#003366",
  secondary = "#FFD700",
  success = "#2E8B57",

  warning = "#FF8C00",
  danger = "#DC143C"
)

# Load data
load_data <- function() {
  surveillance <- read_csv("data/disease_surveillance.csv", show_col_types = FALSE) |>
    mutate(
      report_date = as.Date(report_date),
      onset_date = as.Date(onset_date),
      report_week = floor_date(report_date, "week"),
      report_month = floor_date(report_date, "month")
    )

  indicators <- read_csv("data/health_indicators.csv", show_col_types = FALSE)
  outbreaks <- read_csv("data/outbreak_summary.csv", show_col_types = FALSE) |>
    mutate(start_date = as.Date(start_date))

  list(
    surveillance = surveillance,
    indicators = indicators,
    outbreaks = outbreaks
  )
}

data <- load_data()

# UI
ui <- page_sidebar(
  title = div(
    span("CDPH Disease Surveillance", style = "font-weight: bold;"),
    span(" | R Shiny", style = "font-size: 0.8em; color: #666;")
  ),
  theme = bs_theme(
    primary = CDPH_COLORS$primary,
    secondary = CDPH_COLORS$secondary,
    bootswatch = "flatly"
  ),

  sidebar = sidebar(
    width = 280,
    h4("Filters"),
    selectInput(
      "county",
      "County",
      choices = c("All", sort(unique(data$surveillance$county))),
      selected = "All"
    ),
    selectInput(
      "condition",
      "Condition",
      choices = c("All", sort(unique(data$surveillance$condition))),
      selected = "All"
    ),
    dateRangeInput(
      "date_range",
      "Date Range",
      start = min(data$surveillance$report_date),
      end = max(data$surveillance$report_date)
    ),
    hr(),
    h4("Data Source"),
    checkboxGroupInput(
      "data_sources",
      "Include sources:",
      choices = unique(data$surveillance$data_source),
      selected = unique(data$surveillance$data_source)
    ),
    hr(),
    downloadButton("download_data", "Export CSV", class = "btn-primary w-100")
  ),

  navset_tab(
    nav_panel(
      "Overview",
      layout_columns(
        value_box(
          title = "Total Cases",
          value = textOutput("total_cases"),
          theme = "primary"
        ),
        value_box(
          title = "Hospitalizations",
          value = textOutput("total_hosp"),
          theme = "warning"
        ),
        value_box(
          title = "Active Outbreaks",
          value = textOutput("active_outbreaks"),
          theme = "danger"
        ),
        value_box(
          title = "Avg Days to Report",
          value = textOutput("avg_days"),
          theme = "info"
        ),
        col_widths = c(3, 3, 3, 3)
      ),
      layout_columns(
        card(
          card_header("Weekly Case Trend"),
          plotlyOutput("trend_plot", height = "350px")
        ),
        card(
          card_header("Cases by County"),
          plotlyOutput("county_plot", height = "350px")
        ),
        col_widths = c(7, 5)
      )
    ),

    nav_panel(
      "Conditions",
      layout_columns(
        card(
          card_header("Condition Distribution"),
          plotlyOutput("condition_pie", height = "400px")
        ),
        card(
          card_header("Severity by Condition"),
          plotlyOutput("severity_plot", height = "400px")
        ),
        col_widths = c(6, 6)
      ),
      card(
        card_header("Case Details"),
        DTOutput("case_table")
      )
    ),

    nav_panel(
      "Data Quality",
      layout_columns(
        card(
          card_header("Data Source Distribution"),
          plotlyOutput("source_plot", height = "350px"),
          p("Track migration progress from Legacy SAS to modern pipelines",
            style = "font-size: 0.85em; color: #666; margin-top: 10px;")
        ),
        card(
          card_header("Reporting Timeliness"),
          plotlyOutput("timeliness_plot", height = "350px")
        ),
        col_widths = c(6, 6)
      ),
      card(
        card_header("Lab Confirmation by Source"),
        plotlyOutput("lab_confirm_plot", height = "300px")
      )
    ),

    nav_panel(
      "Health Indicators",
      card(
        card_header("County Health Indicators"),
        selectInput(
          "indicator_select",
          "Select Indicator:",
          choices = unique(data$indicators$indicator)
        ),
        plotlyOutput("indicator_plot", height = "400px")
      ),
      card(
        card_header("Indicator Data"),
        DTOutput("indicator_table")
      )
    ),

    nav_panel(
      "Outbreaks",
      layout_columns(
        card(
          card_header("Outbreak Status"),
          plotlyOutput("outbreak_status", height = "350px")
        ),
        card(
          card_header("Outbreaks by Type"),
          plotlyOutput("outbreak_type", height = "350px")
        ),
        col_widths = c(6, 6)
      ),
      card(
        card_header("Outbreak Investigations"),
        DTOutput("outbreak_table")
      )
    )
  )
)

# Server
server <- function(input, output, session) {

  # Reactive filtered data
  filtered_data <- reactive({
    df <- data$surveillance

    if (input$county != "All") {
      df <- df |> filter(county == input$county)
    }

    if (input$condition != "All") {
      df <- df |> filter(condition == input$condition)
    }

    df <- df |>
      filter(
        report_date >= input$date_range[1],
        report_date <= input$date_range[2],
        data_source %in% input$data_sources
      )

    df
  })

  # Value boxes
  output$total_cases <- renderText({
    format(nrow(filtered_data()), big.mark = ",")
  })

  output$total_hosp <- renderText({
    format(sum(filtered_data()$hospitalized), big.mark = ",")
  })

  output$active_outbreaks <- renderText({
    active <- data$outbreaks |>
      filter(status %in% c("Active", "Under Investigation"))
    nrow(active)
  })

  output$avg_days <- renderText({
    sprintf("%.1f days", mean(filtered_data()$days_to_report, na.rm = TRUE))
  })

  # Trend plot
  output$trend_plot <- renderPlotly({
    weekly <- filtered_data() |>
      group_by(report_week) |>
      summarise(cases = n(), .groups = "drop")

    p <- ggplot(weekly, aes(x = report_week, y = cases)) +
      geom_line(color = CDPH_COLORS$primary, linewidth = 1) +
      geom_point(color = CDPH_COLORS$primary, size = 2) +
      labs(x = "Week", y = "Cases") +
      theme_minimal()

    ggplotly(p)
  })

  # County plot
  output$county_plot <- renderPlotly({
    county_data <- filtered_data() |>
      group_by(county) |>
      summarise(cases = n(), .groups = "drop") |>
      arrange(desc(cases)) |>
      head(15)

    p <- ggplot(county_data, aes(x = reorder(county, cases), y = cases, fill = cases)) +
      geom_col() +
      coord_flip() +
      scale_fill_gradient(low = "#cce5ff", high = CDPH_COLORS$primary) +
      labs(x = NULL, y = "Cases") +
      theme_minimal() +
      theme(legend.position = "none")

    ggplotly(p)
  })

  # Condition pie
  output$condition_pie <- renderPlotly({
    cond_data <- filtered_data() |>
      group_by(condition) |>
      summarise(cases = n(), .groups = "drop")

    plot_ly(cond_data, labels = ~condition, values = ~cases, type = "pie",
            marker = list(colors = RColorBrewer::brewer.pal(10, "Set3")))
  })

  # Severity plot
  output$severity_plot <- renderPlotly({
    sev_data <- filtered_data() |>
      group_by(condition, severity) |>
      summarise(cases = n(), .groups = "drop")

    p <- ggplot(sev_data, aes(x = condition, y = cases, fill = severity)) +
      geom_col(position = "dodge") +
      scale_fill_manual(values = c(
        "Mild" = CDPH_COLORS$success,
        "Moderate" = CDPH_COLORS$warning,
        "Severe" = CDPH_COLORS$danger
      )) +
      labs(x = NULL, y = "Cases", fill = "Severity") +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))

    ggplotly(p)
  })

  # Case table
  output$case_table <- renderDT({
    filtered_data() |>
      select(case_id, county, condition, age_group, severity,
             hospitalized, lab_confirmed, report_date, data_source) |>
      head(100) |>
      datatable(options = list(pageLength = 10, scrollX = TRUE))
  })

  # Data source plot
  output$source_plot <- renderPlotly({
    source_data <- filtered_data() |>
      group_by(data_source) |>
      summarise(cases = n(), .groups = "drop") |>
      arrange(desc(cases))

    colors <- c(
      "Legacy SAS" = CDPH_COLORS$danger,
      "Databricks" = CDPH_COLORS$primary,
      "Direct Entry" = CDPH_COLORS$success,
      "Lab Feed" = CDPH_COLORS$warning,
      "Hospital EHR" = CDPH_COLORS$secondary
    )

    p <- ggplot(source_data, aes(x = reorder(data_source, -cases), y = cases, fill = data_source)) +
      geom_col() +
      scale_fill_manual(values = colors) +
      labs(x = NULL, y = "Cases") +
      theme_minimal() +
      theme(legend.position = "none")

    ggplotly(p)
  })

  # Timeliness plot
  output$timeliness_plot <- renderPlotly({
    time_data <- filtered_data() |>
      group_by(data_source) |>
      summarise(avg_days = mean(days_to_report, na.rm = TRUE), .groups = "drop") |>
      arrange(avg_days)

    p <- ggplot(time_data, aes(x = reorder(data_source, avg_days), y = avg_days, fill = avg_days)) +
      geom_col() +
      scale_fill_gradient(low = CDPH_COLORS$success, high = CDPH_COLORS$danger) +
      labs(x = NULL, y = "Avg Days to Report") +
      theme_minimal() +
      theme(legend.position = "none")

    ggplotly(p)
  })

  # Lab confirmation plot
  output$lab_confirm_plot <- renderPlotly({
    lab_data <- filtered_data() |>
      group_by(data_source) |>
      summarise(
        total = n(),
        confirmed = sum(lab_confirmed),
        rate = confirmed / total * 100,
        .groups = "drop"
      )

    p <- ggplot(lab_data, aes(x = data_source, y = rate, fill = rate)) +
      geom_col() +
      scale_fill_gradient(low = "#ffffcc", high = CDPH_COLORS$success) +
      labs(x = NULL, y = "Lab Confirmation Rate (%)") +
      theme_minimal() +
      theme(legend.position = "none")

    ggplotly(p)
  })

  # Indicator plot
  output$indicator_plot <- renderPlotly({
    ind_data <- data$indicators |>
      filter(indicator == input$indicator_select)

    p <- ggplot(ind_data, aes(x = reorder(county, value), y = value, fill = value)) +
      geom_col() +
      geom_errorbar(aes(ymin = confidence_interval_low, ymax = confidence_interval_high),
                    width = 0.2) +
      coord_flip() +
      scale_fill_viridis_c() +
      labs(x = NULL, y = unique(ind_data$unit)) +
      theme_minimal() +
      theme(legend.position = "none")

    ggplotly(p)
  })

  # Indicator table
  output$indicator_table <- renderDT({
    data$indicators |>
      filter(indicator == input$indicator_select) |>
      select(county, value, unit, confidence_interval_low, confidence_interval_high, data_source) |>
      datatable(options = list(pageLength = 10))
  })

  # Outbreak status
  output$outbreak_status <- renderPlotly({
    status_data <- data$outbreaks |>
      group_by(status) |>
      summarise(count = n(), .groups = "drop")

    colors <- c(
      "Closed" = CDPH_COLORS$success,
      "Active" = CDPH_COLORS$danger,
      "Under Investigation" = CDPH_COLORS$warning
    )

    plot_ly(status_data, labels = ~status, values = ~count, type = "pie",
            marker = list(colors = unname(colors[status_data$status])))
  })

  # Outbreak type
  output$outbreak_type <- renderPlotly({
    type_data <- data$outbreaks |>
      group_by(outbreak_type) |>
      summarise(
        outbreaks = n(),
        total_cases = sum(total_cases),
        .groups = "drop"
      ) |>
      pivot_longer(cols = c(outbreaks, total_cases), names_to = "metric", values_to = "value")

    p <- ggplot(type_data, aes(x = outbreak_type, y = value, fill = metric)) +
      geom_col(position = "dodge") +
      labs(x = NULL, y = "Count", fill = "Metric") +
      theme_minimal()

    ggplotly(p)
  })

  # Outbreak table
  output$outbreak_table <- renderDT({
    data$outbreaks |>
      select(outbreak_id, outbreak_type, condition, county, setting,
             status, total_cases, hospitalizations, deaths) |>
      arrange(desc(total_cases)) |>
      datatable(options = list(pageLength = 10, scrollX = TRUE))
  })

  # Download handler
  output$download_data <- downloadHandler(
    filename = function() {
      paste0("cdph_surveillance_", Sys.Date(), ".csv")
    },
    content = function(file) {
      write_csv(filtered_data(), file)
    }
  )
}

shinyApp(ui, server)
