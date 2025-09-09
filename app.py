import os
import streamlit as st
import pandas as pd
import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit UI setup
st.set_page_config(page_title="Job Profile Report", layout="wide")
st.title(" Job Profile Report")
st.caption("Interactive version of the original SQL-based report")

# Sidebar filters
job_id = st.sidebar.text_input("Enter Job ID(s) separated by comma", "402")
company_id = st.sidebar.number_input("Company ID", min_value=1, value=1)
business_entity_id = 1

# Process job_id input
job_ids = "','".join(job_id.split(',')).strip()
job_ids_sql = f"('{job_ids}')" if job_ids else "NULL"

# Database connection
@st.cache_resource
def get_connection():
    DRIVER = os.getenv("SQL_DRIVER")
    SERVER = os.getenv("SQL_SERVER")
    DB = os.getenv("SQL_DATABASE")
    USER = os.getenv("SQL_USER")
    PWD = os.getenv("SQL_PWD")

    return pyodbc.connect(
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DB};"
        f"UID={USER};"
        f"PWD={PWD};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

# Build WHERE clause properly
if job_id.strip():
    job_ids_list = "', '".join(job_id.strip().split(','))
    job_ids_condition = f"Job_Title.ID IN ('{job_ids_list}')"
else:
    job_ids_condition = "1=1"  # No filtering by Job ID

# Final SQL Query
query = f"""
DECLARE @Company_ID INT = 1, @Business_Entity_ID INT = 1

SELECT
    Job_Title.Code,
    Job_Title.ID,
    Job_Title.Ar_Name AS Ar_Job,
    Job_Title.En_Name AS En_Job,
    Job_Title_Family.Ar_Name AS Ar_Family,
    Job_Title_Family.En_Name AS En_Family,
    Job_Title_Parent.Ar_Name AS Ar_Parent,
    Job_Title_Parent.En_Name AS En_Parent,
    Job_Grade.Ar_Name AS Ar_Grade,
    Job_Grade.En_Name AS En_Grade,
    Job_Grade.MAX_SALARY,
    Job_Grade.Middel_Salary,
    Job_Grade.MIN_SALARY,
    Total_Man_Power.Org_ID,
    org.Ar_Name AS Ar_Org,
    org.En_Name AS En_Org,
    Total_Man_Power.Total_Man_Power,
    ISNULL(Assigned.Total_Assigned, 0) AS Total_Assigned,
    CASE
        WHEN Total_Man_Power.Total_Man_Power > 0 THEN
            ISNULL(Total_Man_Power.Total_Man_Power - Assigned.Total_Assigned, Total_Man_Power.Total_Man_Power)
        ELSE
            Total_Man_Power.Total_Man_Power
    END AS Still_Required
FROM Core_Job_Title Job_Title
LEFT JOIN Core_Job_Title_Family Job_Title_Family
    ON Job_Title_Family.ID = Job_Title.Job_Family_ID AND Job_Title.Is_Delete = 0 AND Job_Title_Family.Is_Delete = 0
LEFT JOIN Core_Job_Title Job_Title_Parent
    ON Job_Title_Parent.ID = Job_Title.ParentJobTitleID AND Job_Title_Parent.Is_Delete = 0
LEFT JOIN Core_Grade Job_Grade
    ON Job_Grade.ID = Job_Title.Grade_ID AND Job_Grade.Is_Delete = 0
INNER JOIN (
    SELECT org_job.Job_Title_ID, org_job.Org_ID, SUM(max_employee) AS Total_Man_Power
    FROM core_org_job_title org_job
    WHERE company_ID = @Company_ID
    GROUP BY org_job.Job_Title_ID, org_job.Org_ID
) Total_Man_Power
    ON Total_Man_Power.Job_Title_ID = Job_Title.ID
LEFT JOIN (
    SELECT a.Job_Title_ID, b.Org_ID, SUM(CAST(a.Is_Manpower_Affected AS INT)) AS Total_Assigned
    FROM Core_Person_Instance_job_title a
    INNER JOIN Core_Person_Instance_Org b ON a.Person_Instance_Org_ID = b.Id
    WHERE a.Is_Manpower_Affected = 1
    AND GETDATE() BETWEEN a.From_Date AND a.To_Date
    AND GETDATE() BETWEEN b.From_Date AND b.To_Date
    AND a.Company_ID = @Company_ID AND b.Company_ID = @Company_ID
    AND a.Business_Entity_ID = @Business_Entity_ID AND b.Business_Entity_ID = @Business_Entity_ID
    GROUP BY a.Job_Title_ID, b.Org_ID
) Assigned
    ON Assigned.Job_Title_ID = Job_Title.ID AND Assigned.Org_ID = Total_Man_Power.Org_ID
INNER JOIN Core_Org org ON org.ID = Total_Man_Power.Org_ID
WHERE {job_ids_condition}
"""

# Run query
with get_connection() as conn:
    df = pd.read_sql(query, conn)

# Display table
st.dataframe(df, use_container_width=True)

# Optional download
st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name="job_profile_report.csv", mime="text/csv")
