# Posit Demo: California Department of Public Health

## Customer Context

**Organization:** California Department of Public Health (CDPH)
**Industry:** Government / Public Health
**Current Tools:** SAS (migrating away), evaluating Altair
**Infrastructure:** Moving to Databricks
**Key Contacts:** Data scientists, epidemiologists, IT leadership

## Strategic Positioning

### Primary Message: Positron Enables LLM Access for Data Scientists

**"If AI can help those modeling things, handling large data..."**

Position Positron as the bridge between their data science team and enterprise AI:
- Not just an IDE—it's an AI-enabled productivity platform
- Direct integration with AWS Bedrock (enterprise security)
- querychat turns natural language into data insights

### Secondary Messages

1. **SAS Migration Support**: Positron assistant helps translate SAS → Python/R
2. **Databricks Compatibility**: Ready for their cloud data platform investment
3. **Altair Complement**: Different value prop—we're about productivity, not just visualization

## Demo Strategy

### Opening (5 min)

Start with the productivity angle:

> "Your data scientists spend hours writing queries, cleaning data, building reports. What if they could just ask questions in plain English and get answers immediately?"

Show the AI Chat tab first—this is the hook.

### Core Demo Flow (25 min)

#### 1. AI Chat Tab (10 min) - THE HERO FEATURE

```
"Show me COVID-19 cases in Los Angeles County"
"What's the hospitalization rate by age group?"
"Compare case counts between Legacy SAS and Databricks data sources"
"Filter to show only severe cases in the Bay Area"
```

**Talking points:**
- "This is querychat—it understands your data schema"
- "No SQL, no pandas—just ask what you want to know"
- "Works on datasets of any size, connects to Databricks"
- "This is what AI-assisted data science looks like in Positron"

#### 2. Data Quality Tab (5 min) - SAS MIGRATION ANGLE

Show the data source distribution chart:

> "Notice you can track migration progress right in the dashboard. As more data flows through Databricks instead of Legacy SAS, you'll see this shift in real-time."

Show reporting timeliness by source:

> "And you can measure data quality improvements—modern pipelines typically show faster reporting times."

#### 3. AI Summary Tab (5 min)

Click "Generate Summary" and watch Claude produce an epidemiological briefing:

> "Instead of an analyst spending 30 minutes writing a summary, AI generates a draft in seconds. The human reviews and refines—that's the productivity multiplier."

#### 4. Overview/Conditions Tabs (5 min)

Quick tour of traditional dashboard features:
- Time series trends
- Geographic distribution
- Condition breakdowns

> "All the standard surveillance capabilities, but now supercharged with AI."

### Positron Assistant Demo (10 min)

Switch to Positron IDE:

1. **Code Generation**
   ```
   Type: "# function to calculate attack rate from case and population data"
   ```
   Show Copilot-style completion

2. **SAS Translation** (if they're interested)
   ```
   "Help me translate this SAS PROC FREQ to Python pandas"
   ```
   Paste a simple SAS example, show the translation

3. **Debugging Assistance**
   > "When something goes wrong, the assistant explains errors in plain English"

### Databricks Integration Points (5 min)

> "This demo uses CSV files, but the patterns translate directly to Databricks:"

- querychat can connect to Spark DataFrames
- Posit Connect handles authentication and serving
- Same dashboard, different data source

### Closing (5 min)

Return to value prop:

> "Your epidemiologists shouldn't be writing SQL queries during an outbreak. They should be asking questions and getting answers. That's what Positron and these AI tools enable."

## Objection Handling

### "We're evaluating Altair"

> "Altair is great for visualization. We're talking about something different—the full data science workflow from exploration to production. Positron is where your data scientists live; Altair might be one output. They're complementary, not competitive."

### "We're committed to Databricks"

> "Perfect. Posit Connect deploys directly to your infrastructure and connects to Databricks. We're the productivity layer on top of your data platform—chatlas and querychat work with Spark DataFrames just like pandas."

### "AI concerns—security, accuracy"

> "Three things: First, AWS Bedrock means your data stays in your AWS account—no third-party exposure. Second, AI generates drafts that humans review—it's augmentation, not automation. Third, querychat translates to actual code you can inspect."

### "We have existing SAS investments"

> "The Positron assistant actively helps with migration. Show it SAS code, ask for Python equivalent. Your team keeps their statistical knowledge; they just express it in modern languages. And you can track migration progress right in dashboards like this one."

### "Our team doesn't know Python"

> "That's exactly why AI assistants matter. Instead of learning pandas syntax, they describe what they want. The AI writes the code. They review and learn. It's the fastest way to upskill a team."

## Azure DevOps Integration Talk Track

### Opening
> "I noticed you're using Azure DevOps. Positron has native Git support, so your team can work directly with Azure Repos without changing their workflow."

### Key Points

1. **Seamless Integration**
   > "Clone from Azure DevOps, commit, push, create PRs - all from within Positron. No separate Git client needed."

2. **CI/CD Pipelines**
   > "Set up Azure Pipelines to automatically test and deploy to Posit Connect. Every push triggers validation, every merge to main deploys to production."

3. **Branch Protection**
   > "Require code reviews before merging. Link commits to Azure Boards work items. Full audit trail for compliance."

4. **Enterprise Security**
   > "PAT tokens, SSH keys, or Azure CLI auth - whatever your security team prefers."

### Demo (if time permits)
Show the Git panel in Positron:
- Stage changes
- Commit with message
- Push to Azure DevOps
- Show commit in Azure DevOps web UI

### Handoff
> "We can provide a sample `azure-pipelines.yml` that sets up CI/CD for Shiny apps and Quarto reports."

## Technical Requirements

### Demo Environment

**Python App:**
```bash
cd CDPH_PublicHealth
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
shiny run app.py --port 8050
```

**R App:**
```bash
Rscript install_packages.R
R -e "shiny::runApp('app.R', port = 8051)"
```

**Quarto Report:**
```bash
quarto render reports/weekly_surveillance.qmd
```

### AWS Credentials
Ensure Bedrock access is configured before the demo.

### Fallback
If AI features fail, the dashboard still works—you just lose the AI Summary and Chat tabs. Focus on the "this is what it looks like" messaging.

## Follow-Up Materials

1. **This repository** - They can run it themselves
2. **Posit Connect trial** - Deploy and share internally
3. **Positron download** - Free, get them using it
4. **Bedrock setup guide** - If they want to enable AI features

## Success Metrics

- [ ] Demo completed
- [ ] AI Chat tab resonated (watch for engagement)
- [ ] SAS migration angle landed
- [ ] Databricks compatibility understood
- [ ] Positron download requested
- [ ] Connect trial initiated
- [ ] Technical follow-up scheduled

---

*Demo created by Posit Solutions Engineering*
