# California Department of Public Health: Disease Surveillance Dashboard

A demonstration of modern data science workflows for public health surveillance, showcasing how Positron and AI assistants accelerate epidemiological analysis.

**DISCLAIMER:** This project contains synthetic data created for demonstration purposes only.

## Key Value Propositions

### 1. AI-Powered Productivity for Data Scientists

**"If AI can help those modeling things, handling large data..."**

This demo shows how Positron's integrated AI capabilities help data scientists:
- **querychat**: Ask questions about surveillance data in natural language
- **chatlas**: Generate epidemiological summaries automatically
- Reduce time from data to insight from hours to minutes

### 2. Positron: Your AI-Enabled IDE

Positron provides seamless LLM access for data scientists:
- Built-in AI assistant for code generation and debugging
- Direct integration with AWS Bedrock (enterprise-grade, secure)
- Natural language to SQL/pandas queries via querychat
- No context switching between tools

### 3. SAS Migration Support

The Positron assistant helps teams transitioning from SAS:
- Code translation assistance (SAS PROC → Python/R)
- Familiar statistical workflows in modern languages
- Side-by-side comparison capabilities
- See `sas/surveillance_report.sas` for migration example

This demo tracks data sources including "Legacy SAS" to visualize migration progress.

### 4. Databricks Integration

Ready for modern cloud data platforms:
- Data patterns compatible with Databricks Delta tables
- Spark-friendly aggregation approaches
- Cloud-native deployment via Posit Connect

### 5. Git and Azure DevOps Integration

Positron and Posit Connect support enterprise version control workflows:
- **Git integration** built into Positron IDE
- **Azure DevOps Repos** fully supported
- **CI/CD pipelines** for automated testing and deployment
- See [Azure DevOps Integration](#azure-devops-integration) section below

## Quick Start

### Python Shiny App (with AI features)

```bash
# Clone the repository
git clone <repo-url>
cd CDPH_PublicHealth

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Run the app
shiny run app.py --port 8050
```

### R Shiny App

```bash
# Install R packages (run once)
Rscript install_packages.R

# Run the app
R -e "shiny::runApp('app.R', port = 8051)"
```

### Quarto Report

```bash
# Render the weekly surveillance report
quarto render reports/weekly_surveillance.qmd

# With custom parameters
quarto render reports/weekly_surveillance.qmd \
  -P start_date:"2026-01-01" \
  -P end_date:"2026-01-31" \
  -P county:"Los Angeles"
```

## Features

### Python Shiny Dashboard (`app.py`)

- **Overview**: Key metrics, time series, geographic distribution
- **Conditions**: Disease-specific analysis with severity breakdowns
- **Data Quality**: Track SAS→Databricks migration, reporting timeliness
- **AI Summary**: Generate epidemiological briefings with Claude
- **AI Chat**: Interactive data exploration using querychat
- **Outbreaks**: Active investigation tracking

### R Shiny Dashboard (`app.R`)

- Full-featured surveillance dashboard in R
- Comparable functionality to Python version
- Demonstrates R/Python parity for team flexibility
- Integrates with SAS output files

### Quarto Report (`reports/weekly_surveillance.qmd`)

- Parameterized weekly surveillance summary
- Consumes data from SAS or direct sources
- Publication-ready tables with gt
- Interactive plotly visualizations

### SAS Integration (`sas/surveillance_report.sas`)

- Example legacy SAS workflow
- Generates CSV outputs for R/Python consumption
- Documents migration path to modern tools
- Shows parallel processing during transition

## Azure DevOps Integration

### Connecting Positron to Azure DevOps

Positron supports Azure DevOps Repos via standard Git:

```bash
# Clone from Azure DevOps
git clone https://dev.azure.com/your-org/your-project/_git/CDPH_PublicHealth

# Or add as remote to existing repo
git remote add azure https://dev.azure.com/your-org/your-project/_git/CDPH_PublicHealth
```

### Authentication Options

1. **Personal Access Token (PAT)**
   ```bash
   # Configure Git credential helper
   git config --global credential.helper store

   # Use PAT as password when prompted
   # Username: your-email@domain.com
   # Password: your-personal-access-token
   ```

2. **SSH Keys**
   ```bash
   # Add SSH key to Azure DevOps
   # Settings > SSH public keys > Add

   git clone git@ssh.dev.azure.com:v3/your-org/your-project/CDPH_PublicHealth
   ```

3. **Azure CLI Integration**
   ```bash
   az devops login
   az repos clone --repository CDPH_PublicHealth
   ```

### CI/CD Pipeline Example

Create `azure-pipelines.yml` for automated testing and deployment:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Test
    jobs:
      - job: PythonTests
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.11'

          - script: |
              pip install uv
              uv venv
              source .venv/bin/activate
              uv pip install -r requirements.txt
              python -c "from app import app; print('App loads successfully')"
            displayName: 'Test Python App'

      - job: RTests
        steps:
          - script: |
              Rscript install_packages.R
              R -e "shiny::runTests('.')"
            displayName: 'Test R App'

  - stage: Deploy
    dependsOn: Test
    condition: succeeded()
    jobs:
      - job: DeployToConnect
        steps:
          - script: |
              pip install rsconnect-python
              rsconnect deploy shiny . \
                --server $CONNECT_SERVER \
                --api-key $CONNECT_API_KEY \
                --title "CDPH Surveillance Dashboard"
            displayName: 'Deploy to Posit Connect'
            env:
              CONNECT_SERVER: $(CONNECT_SERVER)
              CONNECT_API_KEY: $(CONNECT_API_KEY)
```

### Azure DevOps + Posit Connect Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Azure DevOps   │────>│   CI/CD         │────>│  Posit Connect  │
│  Repos          │     │   Pipeline      │     │  (Production)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
   Developers              Automated               End Users
   push code              testing &              access apps
   via Positron           deployment             & reports
```

### Branch Protection

Configure in Azure DevOps:
- Require pull request reviews
- Build validation before merge
- Link work items to commits

## AWS Credentials Configuration

### Posit Workbench / Positron (Local Development)

```bash
# Using AWS CLI
aws configure

# Or environment variables
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-west-2"
```

### Posit Connect (Deployment)

1. Deploy the app
2. Navigate to **Settings** > **Vars** tab
3. Add:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION` = `us-west-2`

### Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:us-west-2::foundation-model/anthropic.*"
    }
  ]
}
```

## Deployment to Posit Connect

### Python App

**Files to include:**
- `app.py`
- `requirements.txt`
- `data/` (entire folder)

```bash
rsconnect deploy shiny . \
  --name your-connect-server \
  --title "CDPH Surveillance Dashboard" \
  --entrypoint app:app
```

### R App

```r
rsconnect::deployApp(".", appPrimaryDoc = "app.R")
```

### Quarto Report

```bash
quarto publish connect reports/weekly_surveillance.qmd
```

## Synthetic Data

- **9,256** disease surveillance records
- **20** California counties
- **10** reportable conditions
- **75** outbreak investigations
- **200** county health indicators
- Date range: 2024-2026

## Project Structure

```
CDPH_PublicHealth/
├── app.py                           # Python Shiny app (AI features)
├── app.R                            # R Shiny app
├── requirements.txt                 # Python dependencies
├── install_packages.R               # R package installer
├── README.md                        # This file
├── posit-README.md                  # Sales demo guide
├── .gitignore
├── data/
│   ├── generate_data.py             # Synthetic data generator
│   ├── disease_surveillance.csv
│   ├── health_indicators.csv
│   └── outbreak_summary.csv
├── sas/
│   └── surveillance_report.sas      # Legacy SAS example
└── reports/
    └── weekly_surveillance.qmd      # Quarto report
```

## Demo Talking Points

### For Data Scientists
- "This is what AI-assisted data exploration looks like in Positron"
- "Instead of writing queries, just ask questions in plain English"
- "The AI understands your data schema and can filter, aggregate, summarize"

### For Leadership
- "Productivity multiplier for epidemiologists and analysts"
- "Accelerates outbreak response with faster data insights"
- "Secure, enterprise-grade AI via AWS Bedrock"

### On SAS Migration
- "Positron's AI assistant helps translate SAS code to Python/R"
- "Track migration progress in the Data Quality tab"
- "SAS outputs feed directly into R/Python dashboards during transition"
- "See `sas/surveillance_report.sas` for the migration pattern"

### On Altair/Databricks
- "Complements your Databricks investment"
- "Connect directly to Delta tables"
- "Posit Connect provides the serving layer for dashboards and reports"
- "Different value prop than Altair - we're about the full workflow"

### On Azure DevOps
- "Positron has built-in Git support - works seamlessly with Azure DevOps"
- "Set up CI/CD pipelines for automated testing and deployment"
- "Branch protection and code review workflows supported"
- "Enterprise-ready version control integration"

---

*Built with Posit tools for California Department of Public Health.*
