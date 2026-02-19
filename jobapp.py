### Terminal commands to create and
# Step 1: Create a project folder
# mkdir my-streamlit-app
# cd my-streamlit-app
# Step 2: + Create the file environment.yml in your project folder:
# Step 3: Create a file environment.yml with the following content:conda env create -f environment.yml -- 
# Step 4: Activate the environment: conda activate streamlit_app
# Step 5: Verify installation: streamlit --version
# Pro tip: Verify you're in the right environment:
#  conda env list          # The active environment is marked with *
#  which python            # Should show a path inside your conda envs
# To deactivate when done: conda deactivate



# create a file jobapp.py
import streamlit as st

st.title("Hello, Job Seeker!")
st.write("This is Job search app.")

# To run the app, use the Terminal command:
# streamlit run jobapp.py

# browser will open at http://localhost:8501, but it might not work.

#2.2 Start jobapp.py and open the browser at http://localhost:8501

import streamlit as st

# Sets the page configuration
# You can set the page title and layout here
st.set_page_config(page_title="Singpare JobDashboard", layout="wide")

st.title("Singapore Job Dashboard")
st.caption("Code-along: building a usable dashboard from real job listings.")

st.header("Dashboard Overview")
st.subheader("What this app will show")
st.markdown("""
- Job volume after filtering
- Average salary
- Median of minimum Years Experience
- Industry and position levels trends
""")
#3.1 load directly first dataset, which is the cleaned job listing data 
import streamlit as st
import pandas as pd

# DATA_PATH = "./data/first_half_dataset.csv"
DATA_PATH = "./data/cleaned_data.csv"

df = pd.read_csv(DATA_PATH)

df = df.drop(columns=["categories"])
df["metadata_newPostingDate"] = pd.to_datetime(df["metadata_newPostingDate"])

# Lesson assumption:
# this dataset has already gone through EDA and basic cleaning.
# Here we focus on dashboard building, not data cleaning.
# We still set the datetime dtype explicitly for reliable filtering and charting.
# df["month"] = pd.to_datetime(df["month"]) -- dataset is correct datetime format.

#3.2 first data disply
st.write(f"Rows loaded: {len(df):,} | Columns: {len(df.columns)}")
st.dataframe(df.head(20), width="stretch")


#4.1 Sidebart controls
distinct_categories = sorted(
    df["category_text"]
      .fillna("")
      .str.split(" \\| ")   # split into list
      .explode()            # one category per row
      .loc[lambda x: x != ""]
      .unique()
)


unique_positionLevels = sorted(df["positionLevels"].dropna().unique())

#4.2 Create multi-selects for categories and position levels    
selected_cat = st.sidebar.multiselect("category_text", distinct_categories, default=[])
selected_positionLevels = st.sidebar.multiselect("Position Levels", unique_positionLevels, default=[])

# 4.3 Create a slider for average salary range
min_salary = int(df["average_salary"].min())
max_salary = int(df["average_salary"].max())

# create the slider widget in the slidebar:
salary_range = st.sidebar.slider(
    "Average Salary Range",
    min_value=min_salary,
    max_value=max_salary,
    value=(min_salary, max_salary),
    step=10000,
)
# Create date input for month range of new posting date
date_min = df["metadata_newPostingDate"].min().date()
date_max = df["metadata_newPostingDate"].max().date()

date_range = st.sidebar.date_input("Month Range", value=(date_min, date_max))

# The code for the entire sidebar section looks like this:


#4.2 Apply filters
filtered_df = df.copy()

# selected = ["Admin"]
# selected = ["Manufacturing"]
# selected_cat = ["Manufacturing", "Environment / Health"]

text = df["category_text"].fillna("")

# the lambda function returns True if all selected categories are in the text
mask = text.apply(lambda s: all(cat in s for cat in selected_cat   ))
filtered_df = df[mask]

if selected_cat:
    filtered_df = filtered_df[filtered_df["category_text"].isin(selected_cat)]

if selected_positionLevels:
    filtered_df = filtered_df[filtered_df["positionLevels"].isin(selected_positionLevels)]

filtered_df = filtered_df[
    filtered_df["average_salary"].between(salary_range[0], salary_range[1])
]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[filtered_df["metadata_newPostingDate"].between(
        pd.to_datetime(start_date), pd.to_datetime(end_date)
    )]
    
    # 4.3 Update the table to use filtered_df
    st.header("Filtered Results")
st.write(f"Matching rows: {len(filtered_df):,} | Columns: {len(filtered_df.columns)}")
st.dataframe(filtered_df.head(20), width="stretch")

#4.4 KPI row
st.header("Key Metrics")
# Create four columns for the metrics and unpack them
# We can then use each column to place a metric
col1, col2, col3, col4 = st.columns(4)

# Populate each column with a metric by passing label and value
col1.metric("Jobs", f"{len(filtered_df):,}")
col2.metric("Average Salary", f"${filtered_df['average_salary'].mean():,.0f}")
col3.metric("Median Salary", f"${filtered_df['average_salary'].median():,.0f}")
col4.metric("ience", f"{filtered_df['minimumYearsExperience'].median():.1f} years")


#5 add charts and data view
# 5.1 Main visuals
import plotly.express as px

st.header("Visual Analysis")

col_left, col_right = st.columns(2)

# Tells Streamlit to put the following content in the left column
with col_left:
    st.subheader("Average Job Salary by industry Categories")
    avg_price_by_town = (
        filtered_df.groupby("category_text", as_index=False)["average_salary"]
        .mean()
        .sort_values("average_salary", ascending=False)
        .head(10) # Top 10 towns only for clarity
    )
    # Create a Plotly bar chart with towns on x-axis and average salary on y-axis
    fig_town = px.bar(avg_price_by_town, x="category_text", y="average_salary")
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_town, width="stretch")

# Tells Streamlit to put the following content in the right column
with col_right:
    st.subheader("Jobs by position Levels")
    tx_by_flat = (
        filtered_df.groupby("positionLevels", as_index=False)
        .size()
        .rename(columns={"size": "category_text"})
        .sort_values("category_text", ascending=False)
    )
    # Create a Plotly bar chart with flat types on x-axis and transaction counts on y-axis
    fig_flat = px.bar(tx_by_flat, x="positionLevels", y="category_text")
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_flat, width="stretch")

    #5.2 Monthly tre
st.subheader("Monthly Median average Salary  Trend")
trend = (
    filtered_df.groupby("metadata_newPostingDate", as_index=False)["average_salary"]
    .median()
    .sort_values("metadata_newPostingDate")
)
# Create a Plotly line chart with month on x-axis and median average salary on y-axis
fig_trend = px.line(trend, x="metadata_newPostingDate", y="average_salary", markers=True)
# Display the Plotly chart in Streamlit
st.plotly_chart(fig_trend, width="stretch")

#5.3 
with st.expander("View Filtered Jobs"):
    st.dataframe(filtered_df, width="stretch", height=350)
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv,
        file_name="filtered_cleaned_data.csv",
        mime="text/csv",
    )

#6 add a rerun timestamp at the bottom
from datetime import datetime
print(f"🟢 Rerun at: {datetime.now()}")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["metadata_newPostingDate"] = pd.to_datetime(df["metadata_newPostingDate"])
    return df

df = load_data(DATA_PATH)

