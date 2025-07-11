# app.py (Navigation Name Corrected)

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Ultimate Ola Insights Dashboard",
    page_icon="✨",
    layout="wide"
)

# --- 2. Initialize Session State & Custom Styling ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
st.markdown('<h1 style="color: #8B0000;">🚗 Ultimate Ola Insights Dashboard</h1>', unsafe_allow_html=True)


# --- 3. DATABASE CONNECTION & DATA LOADING ---
@st.cache_resource
def create_db_engine():
    db_user = 'root'
    db_password_raw = 'Akshay@200' 
    db_password_encoded = quote_plus(db_password_raw) 
    db_host = '127.0.0.1'
    db_name = 'ola_project'
    try:
        return create_engine(f"mysql+mysqlconnector://{db_user}:{db_password_encoded}@{db_host}/{db_name}")
    except Exception as e:
        st.error(f"🔴 Error connecting to database: {e}")
        return None

@st.cache_data
def load_data(_engine):
    if _engine:
        try:
            query = "SELECT * FROM ride_details" 
            df = pd.read_sql(query, _engine)
            df['booking_timestamp'] = pd.to_datetime(df['booking_timestamp'])
            return df
        except Exception as e:
            st.error(f"🔴 Error loading data: {e}")
    return pd.DataFrame()

engine = create_db_engine()
df_original = load_data(engine)

# --- 4. SIDEBAR NAVIGATION & FILTERS ---
st.sidebar.title("Navigation")
# Using consistent names in the radio options
page_options = ('Home', 'Vehicle & Customer Insights', 'Payment & Ride Completion')
page = st.sidebar.radio("Go to:", page_options, key='page')
st.sidebar.markdown("---")
st.sidebar.header("Dashboard Filters ⚙️")

# Initialize df_filtered
df_filtered = df_original.copy()

if not df_original.empty:
    min_date = df_original['booking_timestamp'].min().date()
    max_date = df_original['booking_timestamp'].max().date()
    start_date, end_date = st.sidebar.date_input("Select Date Range:", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    vehicle_options = ['All'] + sorted(df_original['Vehicle_Type'].unique().tolist())
    selected_vehicle = st.sidebar.selectbox("Select Vehicle Type:", vehicle_options)
    
    status_options = ['All'] + sorted(df_original['Booking_Status'].unique().tolist())
    selected_status = st.sidebar.selectbox("Select Booking Status:", status_options)

    df_filtered = df_original[
        (df_original['booking_timestamp'].dt.date >= start_date) &
        (df_original['booking_timestamp'].dt.date <= end_date)
    ]
    if selected_vehicle != 'All':
        df_filtered = df_filtered[df_filtered['Vehicle_Type'] == selected_vehicle]
    if selected_status != 'All':
        df_filtered = df_filtered[df_filtered['Booking_Status'] == selected_status]

# --- Functions to change pages (with corrected names) ---
def go_to_home(): st.session_state.page = 'Home'
def go_to_vehicle_customer(): st.session_state.page = 'Vehicle & Customer Insights'
def go_to_payment_completion(): st.session_state.page = 'Payment & Ride Completion' # Corrected Name

# --- 5. Main App Logic (Page Display) ---
if st.session_state.page == 'Home':
    st.markdown("Welcome! Use the sidebar or click a button below to dive into a specific analysis.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.button("Analyze Vehicle & Customer Insights", on_click=go_to_vehicle_customer, use_container_width=True)
    with col2:
        st.button("Analyze Payment & Ride Completion", on_click=go_to_payment_completion, use_container_width=True)

    st.header("Key Metrics for Selected Filters")
    
    if not df_filtered.empty:
        col1, col2, col3, col4 = st.columns(4)
        successful_rides = df_filtered[df_filtered['Booking_Status'] == 'Success']
        col1.metric("Successful Bookings", f"{successful_rides.shape[0]:,}")
        col2.metric("Value of Successful Bookings", f"₹{successful_rides['Booking_Value'].sum():,.0f}")
        customer_cancels = df_filtered[df_filtered['Booking_Status'] == 'Canceled by Customer'].shape[0]
        col3.metric("Rides Cancelled by Customer", f"{customer_cancels:,}")
        driver_cancels_reason = df_filtered[df_filtered['Driver_Cancel_Reason'] == 'Personal & Car related issue'].shape[0]
        col4.metric("Driver Cancels (Personal/Car Issues)", f"{driver_cancels_reason:,}")
    else:
        st.warning("No data for the selected filters.")

# Using the corrected name in the elif check
elif st.session_state.page == 'Vehicle & Customer Insights':
    st.title("🚗 Vehicle & Customer Insights")
    st.markdown("The charts below update based on the filters you select in the sidebar.")
    st.markdown("---")
    
    if not df_filtered.empty:
        # ... (The rest of the code for this page remains the same) ...
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Vehicle Performance Radar")
            avg_metrics_df = df_filtered.groupby('Vehicle_Type').agg(avg_distance=('Ride_Distance', 'mean'), avg_rating=('Customer_Rating', 'mean')).reset_index()
            fig = go.Figure()
            for _, row in avg_metrics_df.iterrows():
                fig.add_trace(go.Scatterpolar(r=[row['avg_distance'], row['avg_rating']], theta=['Avg. Distance (km)', 'Avg. Customer Rating'], fill='toself', name=row['Vehicle_Type']))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 50])), showlegend=True, title="Avg. Distance vs. Avg. Rating")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Top Customer's Ride Count")
            top_customer = df_filtered['Customer_ID'].value_counts().nlargest(1).reset_index()
            top_customer.columns = ['Customer_ID', 'ride_count']
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=top_customer['ride_count'][0],
                domain={'x': [0, 1], 'y': [0, 1]}, title={'text': f"Top Customer: {top_customer['Customer_ID'][0]}"},
                gauge={'axis': {'range': [None, top_customer['ride_count'][0] + 10]}, 'bar': {'color': "darkred"}}))
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.subheader("Prime Sedan Driver Ratings")
        prime_sedan_df = df_filtered[df_filtered['Vehicle_Type'] == 'Prime Sedan']
        if not prime_sedan_df.empty:
            min_r, max_r = st.columns(2)
            min_r.metric("Min Rating", f"{prime_sedan_df['Driver_Ratings'].min():.1f} ⭐")
            max_r.metric("Max Rating", f"{prime_sedan_df['Driver_Ratings'].max():.1f} ⭐")
        else:
            st.info("No Prime Sedan data for the current filter selection.")
    else:
        st.warning("No data for the selected filters.")

# Using the corrected name in the elif check
elif st.session_state.page == 'Payment & Ride Completion':
    st.title("💸 Payment & Ride Completion Analysis")
    st.markdown("The charts below update based on the filters you select in the sidebar.")
    st.markdown("---")

    if not df_filtered.empty:
        # ... (The rest of the code for this page remains the same) ...
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Payment Method Analysis")
            payment_counts = df_filtered['Payment_Method'].value_counts().reset_index()
            payment_counts.columns = ['Payment_Method', 'count']
            fig_q7 = px.bar_polar(payment_counts, r="count", theta="Payment_Method", color="Payment_Method",
                                  template="plotly_dark", title="Distribution of Payment Methods",
                                  color_discrete_sequence=px.colors.sequential.Plasma_r)
            st.plotly_chart(fig_q7, use_container_width=True)
        with col2:
            st.subheader("Reasons for Incomplete Rides")
            incomplete_df = df_filtered[df_filtered['Incomplete_Rides'] == 'Yes']
            if not incomplete_df.empty:
                reason_counts = incomplete_df['Incomplete_Rides_Reason'].value_counts().reset_index()
                fig_q10 = px.treemap(reason_counts, path=['Incomplete_Rides_Reason'], values='count', 
                                     title="Breakdown of Incomplete Ride Reasons",
                                     color='count', color_continuous_scale='Reds')
                st.plotly_chart(fig_q10, use_container_width=True)
            else:
                st.info("No incomplete rides for the current filter selection.")
    else:
        st.warning("No data for the selected filters.")