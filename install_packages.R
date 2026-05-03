#' Install required R packages for CDPH Disease Surveillance Dashboard
#'
#' Run this script once to install all dependencies:
#' Rscript install_packages.R

packages <- c(
  # Shiny and UI
  "shiny",
  "bslib",
  "DT",

  # Data manipulation
  "dplyr",
  "tidyr",
  "readr",
  "lubridate",

 # Visualization
  "ggplot2",
  "plotly",
  "scales",
  "RColorBrewer",

  # Reporting (for Quarto)
  "gt",
  "knitr",
  "rmarkdown"
)

# Install missing packages
install_if_missing <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    message(sprintf("Installing %s...", pkg))
    install.packages(pkg, repos = "https://cloud.r-project.org")
  } else {
    message(sprintf("%s already installed", pkg))
  }
}

invisible(lapply(packages, install_if_missing))

message("\nAll packages installed successfully!")
message("Run the app with: shiny::runApp('app.R')")
