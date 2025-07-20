# Import necessary libraries
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import certifi # Required for TiDB Cloud connection

# --- Page Configuration ---
st.set_page_config(
    page_title="Ola Ride Insights Dashboard",
    page_icon="🚕",
    layout="wide"
)

# --- Database Connection ---
@st.cache_resource
def get_db_connection():
    # Credentials for your TiDB Cloud database
    db_user = "2U7S3pVg1iTazSx.root"
    db_password = "WADf9MESS5MSLLuv"
    db_host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
    db_port = "4000"
    db_name = "ola_project"
    
    try:
        # The connection string for TiDB Cloud with SSL arguments
        engine = create_engine(
            f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
            connect_args={'ssl_ca': certifi.where()}
        )
        return engine
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

engine = get_db_connection()


# --- Main Application ---
st.title("🚕 Ola Ride Insights Dashboard")
st.markdown("An interactive dashboard to explore Ola ride data, powered by SQL queries and Power BI.")


# --- Power BI Dashboard Section ---
st.header("Power BI Interactive Dashboard")
st.markdown("This embedded dashboard provides a comprehensive visual overview of the ride data.")

# --- YOUR POWER BI LINK HAS BEEN ADDED HERE ---
power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiOTZiYTcxOTEtOTAxMC00OWEyLWFmODEtNzdhNDk1YzBjODA0IiwidCI6ImY4MDYwMTgxLWIxNzYtNDI5ZC05NGVlLWMzM2Y2N2FmOWRjMyJ9"
# Embed the Power BI report using an iframe component
st.components.v1.iframe(power_bi_url, height=600, scrolling=True)


# --- SQL Query Insights Section ---
st.header("SQL Query Insights")
st.markdown("Select a business question to retrieve specific insights directly from the database.")

sql_queries = {
    "1. Retrieve all successful bookings": """
        SELECT * FROM ride_details WHERE Booking_Status = 'Success';
    """,
    "2. Find the average ride distance for each vehicle type": """
        SELECT Vehicle_Type, AVG(Ride_Distance) AS Average_Distance
        FROM ride_details
        GROUP BY Vehicle_Type;
    """,
    "3. Get the total number of cancelled rides by customers": """
        SELECT COUNT(*) AS Total_Customer_Cancellations
        FROM ride_details
        WHERE Booking_Status = 'Canceled by Customer';
    """,
    "4. List the top 5 customers who booked the highest number of rides": """
        SELECT Customer_ID, COUNT(Booking_ID) AS Number_of_Rides
        FROM ride_details
        GROUP BY Customer_ID
        ORDER BY Number_of_Rides DESC
        LIMIT 5;
    """,
    "5. Get rides cancelled by drivers due to personal/car issues": """
        SELECT COUNT(*) AS Cancellations_Due_To_Personal_Car_Issues
        FROM ride_details
        WHERE Driver_Cancel_Reason = 'Personal & Car related issue';
    """,
    "6. Find the max and min driver ratings for Prime Sedan": """
        SELECT MAX(Driver_Ratings) AS Max_Rating, MIN(Driver_Ratings) AS Min_Rating
        FROM ride_details
        WHERE Vehicle_Type = 'Prime Sedan';
    """,
    "7. Retrieve all rides where payment was made using UPI": """
        SELECT * FROM ride_details WHERE Payment_Method = 'UPI';
    """,
    "8. Find the average customer rating per vehicle type": """
        SELECT Vehicle_Type, AVG(Customer_Rating) AS Average_Customer_Rating
        FROM ride_details
        GROUP BY Vehicle_Type;
    """,
    "9. Calculate the total booking value of successful rides": """
        SELECT SUM(Booking_Value) AS Total_Successful_Booking_Value
        FROM ride_details
        WHERE Booking_Status = 'Success';
    """,
    "10. List all incomplete rides along with the reason": """
        SELECT Booking_ID, Incomplete_Rides_Reason
        FROM ride_details
        WHERE Incomplete_Rides = 'Yes';
    """
}

# Create a dropdown menu for the user to select a question
selected_question = st.selectbox(
    "Choose a question to see the result:",
    options=list(sql_queries.keys())
)

# --- Execute and Display Query Results ---
if selected_question and engine is not None:
    # Get the corresponding SQL query
    query = sql_queries[selected_question]

    # Display the SQL query being executed
    st.markdown("#### SQL Query:")
    st.code(query, language='sql')

    try:
        # Execute the query and load the result into a DataFrame
        result_df = pd.read_sql(text(query), engine)

        # Display the result
        st.markdown("#### Result:")
        st.dataframe(result_df)

    except Exception as e:
        st.error(f"An error occurred while executing the query: {e}")