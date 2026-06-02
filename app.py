import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lead Qualification Agent", layout="wide")

st.title("AI Lead Qualification Agent")
st.write("Prototype for scoring, classifying, and recommending next actions for inbound leads.")

# -----------------------------
# Sample Data
# -----------------------------
sample_data = [
    {
        "Lead Name": "John Smith",
        "Job Title": "VP Marketing",
        "Company": "Acme SaaS",
        "Industry": "SaaS",
        "Employees": 750,
        "Source": "LinkedIn Ads",
        "Pages Visited": "Pricing, Demo, Case Study",
        "Email Opens": 5,
        "Form Fills": 2
    },
    {
        "Lead Name": "Priya Mehta",
        "Job Title": "Marketing Executive",
        "Company": "Small Agency",
        "Industry": "Agency",
        "Employees": 25,
        "Source": "Google Ads",
        "Pages Visited": "Blog",
        "Email Opens": 1,
        "Form Fills": 0
    },
    {
        "Lead Name": "David Lee",
        "Job Title": "Chief Revenue Officer",
        "Company": "Enterprise Tech",
        "Industry": "Technology",
        "Employees": 2500,
        "Source": "Webinar",
        "Pages Visited": "Demo, Pricing, Integrations",
        "Email Opens": 8,
        "Form Fills": 3
    }
]

df = pd.DataFrame(sample_data)

# -----------------------------
# Scoring Logic
# -----------------------------
def score_lead(row):
    score = 0
    reasons = []

    title = str(row["Job Title"]).lower()
    industry = str(row["Industry"]).lower()
    employees = int(row["Employees"])
    pages = str(row["Pages Visited"]).lower()
    email_opens = int(row["Email Opens"])
    form_fills = int(row["Form Fills"])
    source = str(row["Source"]).lower()

    # Job title scoring
    if any(x in title for x in ["vp", "chief", "cmo", "cro", "director", "head"]):
        score += 25
        reasons.append("senior decision-maker title")

    # Industry scoring
    if any(x in industry for x in ["saas", "technology", "software", "enterprise"]):
        score += 20
        reasons.append("strong ICP industry fit")

    # Company size scoring
    if employees >= 500:
        score += 20
        reasons.append("company size matches ICP")
    elif employees >= 100:
        score += 10
        reasons.append("mid-market company size")

    # Page intent scoring
    if "pricing" in pages:
        score += 15
        reasons.append("visited pricing page")
    if "demo" in pages:
        score += 15
        reasons.append("visited demo page")
    if "case study" in pages or "integrations" in pages:
        score += 10
        reasons.append("engaged with high-intent content")

    # Engagement scoring
    if email_opens >= 5:
        score += 10
        reasons.append("high email engagement")
    elif email_opens >= 2:
        score += 5
        reasons.append("moderate email engagement")

    if form_fills >= 2:
        score += 10
        reasons.append("multiple form submissions")
    elif form_fills == 1:
        score += 5
        reasons.append("single form submission")

    # Source scoring
    if source in ["linkedin ads", "webinar", "google ads"]:
        score += 5
        reasons.append("qualified acquisition source")

    score = min(score, 100)

    if score >= 80:
        status = "SQL - Sales Ready"
        action = "Route to sales immediately and create follow-up task."
    elif score >= 60:
        status = "MQL - High Priority"
        action = "Send to SDR team and enroll in product-focused nurture."
    elif score >= 40:
        status = "Nurture"
        action = "Add to email nurture sequence and monitor future engagement."
    else:
        status = "Low Priority"
        action = "Keep in awareness campaign and retargeting audience."

    return pd.Series({
        "Lead Score": score,
        "Status": status,
        "Reasoning": ", ".join(reasons),
        "Recommended Action": action
    })

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Upload Lead Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

st.sidebar.write("CSV columns needed:")
st.sidebar.code(
    "Lead Name, Job Title, Company, Industry, Employees, Source, Pages Visited, Email Opens, Form Fills"
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

# -----------------------------
# Main App
# -----------------------------
st.subheader("Input Lead Data")
st.dataframe(df, use_container_width=True)

if st.button("Run Lead Qualification Agent"):
    results = df.apply(score_lead, axis=1)
    final_df = pd.concat([df, results], axis=1)

    st.subheader("Agent Output")
    st.dataframe(final_df, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Leads", len(final_df))
    col2.metric("Sales Ready Leads", len(final_df[final_df["Status"] == "SQL - Sales Ready"]))
    col3.metric("MQL Leads", len(final_df[final_df["Status"] == "MQL - High Priority"]))
    col4.metric("Avg Lead Score", round(final_df["Lead Score"].mean(), 1))

    st.subheader("Priority Leads")
    priority_df = final_df[final_df["Lead Score"] >= 60]
    st.dataframe(priority_df, use_container_width=True)

    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Scored Leads CSV",
        data=csv,
        file_name="scored_leads.csv",
        mime="text/csv"
    )
