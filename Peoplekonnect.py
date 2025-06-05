import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="WinS Tracker", layout="wide")

# ---------- USER LOGIN SYSTEM ----------
USERS = {
    "sales1": "pass123",
    "sales2": "abc456"
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔐 Login to WinS Call Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

if not st.session_state.authenticated:
    login()
    st.stop()

# ---------- FILE UPLOAD OR LOAD ----------
st.title("📞 Women in Sales (WinS) Outreach Tracker")

user_file = f"{st.session_state.username}_wins_data.xlsx"

def clean_dataframe(df):
    # Drop unnecessary columns
    drop_cols = ['Unnamed: 0', 'Unnamed: 12', 'ROLE', 'Add to Campaign', 'Designation']
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # Rename for uniformity
    df.rename(columns={'Designation.1': 'Designation'}, inplace=True)

    # Drop empty rows
    df = df[df['Name'].notna() & df['Gender'].notna()]

    # Add new columns if not exist
    if 'Call Status' not in df.columns:
        df['Call Status'] = 'Not Called'
    if 'Feedback' not in df.columns:
        df['Feedback'] = ''

    return df.reset_index(drop=True)

if os.path.exists(user_file):
    df = pd.read_excel(user_file)
    df = clean_dataframe(df)
    st.success("✅ Loaded your previous session data.")
else:
    uploaded_file = st.file_uploader("📂 Upload WinS Excel File", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df = clean_dataframe(df)
    else:
        st.warning("Upload a new Excel file or wait for saved data to load.")
        st.stop()

# ---------- INTERACTION UI ----------
st.subheader("📋 Update Call Responses")

for idx in range(len(df)):
    with st.expander(f"{df.loc[idx, 'Name']} | {df.loc[idx, 'Designation']} | {df.loc[idx, 'Organisation']}"):
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**📧 Official Email:** {df.loc[idx, 'Official Email']}")
        col2.markdown(f"**📧 Personal Email:** {df.loc[idx, 'Personal Email']}")
        col3.markdown(f"**📞 Mobile:** {df.loc[idx, 'Mobile']}")

        loc_col, gen_col = st.columns(2)
        loc_col.markdown(f"**📍 Location:** {df.loc[idx, 'Location']}")
        gen_col.markdown(f"**👤 Gender:** {df.loc[idx, 'Gender']}")

        if pd.notna(df.loc[idx, 'Linkedin Profile']):
            st.markdown(f"[🔗 LinkedIn Profile]({df.loc[idx, 'Linkedin Profile']})")

        df.at[idx, "Call Status"] = st.selectbox(
            "📞 Call Status",
            ["Not Called", "Called - No Response", "Interested", "Will Promote", "Follow-up", "Not Interested"],
            key=f"status_{idx}",
            index=["Not Called", "Called - No Response", "Interested", "Will Promote", "Follow-up", "Not Interested"].index(df.loc[idx, "Call Status"])
        )

        df.at[idx, "Feedback"] = st.text_area(
            "📝 Feedback",
            value=df.loc[idx, "Feedback"],
            key=f"feedback_{idx}"
        )

# ---------- DASHBOARD ----------
st.subheader("📊 Summary Dashboard")

col1, col2 = st.columns(2)

with col1:
    call_dist = df["Call Status"].value_counts().reset_index()
    call_dist.columns = ["Call Status", "Count"]
    fig = px.pie(call_dist, names="Call Status", values="Count", title="Call Response Breakdown")
    st.plotly_chart(fig)

with col2:
    city_dist = df["Location"].dropna().value_counts().nlargest(10).reset_index()
    city_dist.columns = ["Location", "Count"]
    fig2 = px.bar(city_dist, x="Location", y="Count", title="Top 10 Locations")
    st.plotly_chart(fig2)

# ---------- SAVE & DOWNLOAD ----------
df.to_excel(user_file, index=False)
st.success("✅ Progress Saved Automatically")

with open(user_file, "rb") as f:
    st.download_button("📥 Download Updated File", f, file_name="WinS_Updated_Data.xlsx")

