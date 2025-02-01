import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px 
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# Database Connection
def get_connection():
    mydb_conn = pymysql.connect(
     host = 'localhost',
     user = 'root',
     password = 'root',
     database = 'healthcare_data'
    )
    return mydb_conn

# Query Functions

def get_healthcare_data(query_type):
    conn = get_connection()
    
    if query_type == 'Trends in Admission Over Time':
        query = """
            SELECT COUNT(patient_id) AS total_admissions,
            MONTH(Admit_Date) aS MONTH_ADDMISIONS
            FROM HEALTHCARE
            group by MONTH(Admit_Date)
            ORDER BY
                MONTH(Admit_Date);
        """
    elif query_type == 'Diagnosis Frequency Analysis':
        query = """
             select Diagnosis , count(*) As diagnosis_count
                FROM healthcare
                GROUP BY
                    diagnosis
                ORDER BY
                    diagnosis_count  DESC
                    LIMIT 5;
        """
    elif query_type == 'Bed Occupancy Analysis':
        query = """
            SELECT Bed_Occupancy,
            COUNT(Bed_Occupancy) AS occupancy_count,
            (COUNT(Bed_Occupancy)*100 / (select COUNT(Bed_Occupancy) fROM healthcare )) As occupancy_percentage
            FROM healthcare
            Group by Bed_Occupancy
            order by occupancy_count;

        """
    elif query_type == 'Length of Stay Distribution':
        query = """
            SELECT  Bed_Occupancy,
            max(datediff(Discharge_Date, Admit_Date)) As maximumn_length,
                Avg(datediff(Discharge_Date, Admit_Date))As avg_length
            from healthcare
            group by  Bed_Occupancy;
        """
    elif query_type == 'Seasonal Admission Patterns':
        query = """
            SELECT 
            CASE 
                WHEN MONTH(Admit_Date) IN (12, 1, 2) THEN 'Winter'
                WHEN MONTH(Admit_Date) IN (3, 4, 5) THEN 'Spring'
                WHEN MONTH(Admit_Date) IN (6, 7, 8) THEN 'Summer'
                ELSE 'Fall'
            END AS season,
            SUM(Billing_Amount) AS total_revenue
        FROM 
            healthcare
        GROUP BY 
            season
        ORDER BY 
            total_revenue DESC;
        """
    elif query_type == 'Doctor-wise Patient Count':
        query = """
             SELECT Doctor ,COUNT(Patient_ID) As patient_count
            from healthcare
            group by Doctor
            order by patient_count DESC;
        """
    elif query_type == 'Monthly Revenue Trends':
        query = """
                SELECT 
                MONTH(Admit_Date) AS month,
                SUM(Billing_Amount) AS total_revenue,
                AVG(Billing_Amount) AS avg_revenue_per_patient
            FROM healthcare
            GROUP BY month
            ORDER BY month;
         """
    elif query_type == 'Test Frequency Analysis':
        query = """
            SELECT Test ,COUNT(*) As test_count
            from healthcare
            group by Test
            order by test_count DESC;
         """  
    elif query_type == 'Diagnosis and Cost Analysis':
        query = """
            SELECT 
            Diagnosis, 
            AVG(Billing_Amount) AS avg_billing,
            SUM(Billing_Amount) As total_billing
        FROM 
            healthcare
        GROUP BY 
            Diagnosis
        ORDER BY 
            avg_billing DESC
        LIMIT 5;
         """
    elif query_type == 'Analyzing Yearly Patients and Billing amount':
        query = """
            SELECT 
            EXTRACT(YEAR FROM Admit_Date) AS admission_year,
            Doctor,
            Diagnosis,
            COUNT(DISTINCT Patient_ID) AS total_patients,
            SUM(Billing_Amount) AS total_billing_amount,
            AVG(Billing_Amount) AS avg_billing_per_patient,
            COUNT(DISTINCT Test) AS total_tests_per_patient,
            AVG(Feedback) AS avg_feedback
        FROM 
            healthcare
        GROUP BY 
            EXTRACT(YEAR FROM Admit_Date), Doctor, Diagnosis
        ORDER BY 
            admission_year DESC, total_billing_amount DESC;
         """  
    elif query_type == 'Patient-Diagnosis-Test admit-year-wise Billing Analysis':
        query = """
            SELECT 
            Patient_ID, 
            Diagnosis, Test,
            EXTRACT(YEAR FROM Admit_Date) AS admission_year,
            SUM(Billing_Amount) AS total_billing_amount,
            SUM(Health_Insurance_Amount) AS total_insurance_covered,
            (SUM(Health_Insurance_Amount) * 100.0 / SUM(Billing_Amount)) AS insurance_coverage_percentage
        FROM 
            healthcare
        GROUP BY 
            Patient_ID, Diagnosis,Test, admission_year
        ORDER BY 
            total_billing_amount DESC;
         """    
    elif query_type == 'Length of Stay and Billing Correlation':
        query = """
           SELECT 
            EXTRACT(YEAR FROM Admit_Date) AS admission_year,
            AVG(DATEDIFF(Discharge_Date, Admit_Date)) AS avg_length_of_stay,
            SUM(Billing_Amount) AS total_billing_amount
        FROM 
            healthcare
        GROUP BY 
            admission_year
        ORDER BY 
            avg_length_of_stay DESC;
         """    
    
    elif query_type == 'Insurance Coverage vs. Billing Trends by Diagnosis':
        query = """
          SELECT 
        Diagnosis,
        SUM(Billing_Amount) AS total_billing_amount,
        SUM(Health_Insurance_Amount) AS total_insurance_covered,
        (SUM(Health_Insurance_Amount) * 100.0 / SUM(Billing_Amount)) AS insurance_coverage_percentage
    FROM 
        healthcare
    GROUP BY 
        Diagnosis
    ORDER BY 
        insurance_coverage_percentage DESC;
         """    
         
    elif query_type == 'Doctor Performance Feedback by Diagnosis':
        query = """
        SELECT 
        Doctor, Diagnosis,
            Feedback,
            COUNT(DISTINCT Patient_ID) AS total_patients,
            SUM(Billing_Amount) AS total_billing_amount
        FROM 
            healthcare
        GROUP BY 
            Doctor, Diagnosis, Feedback
        ORDER BY 
            Feedback DESC;
        """          
    elif query_type == 'Average Billing vs. Length of Stay by Diagnosis':
        query = """
                SELECT 
            Diagnosis, 
            AVG(DATEDIFF(Discharge_Date, Admit_Date)) AS avg_length_of_stay, 
            AVG(Billing_Amount) AS avg_billing_amount
        FROM 
            healthcare
        GROUP BY 
            Diagnosis
        ORDER BY 
            avg_billing_amount DESC;

        """          
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Streamlit configuration
st.set_page_config(layout="wide")
st.title("Healthcare Data Visualization and Exploration")

# Sidebar Menu using selectbox
menu_option = st.sidebar.selectbox('Main Menu', ['Home', 'Data Visualization'])

if menu_option == 'Home':
    st.header("Welcome to Healthcare Visualization Dashboard!")
    st.write("Explore various insights and analysis on PhonePe transaction data.")

if menu_option == 'Data Visualization':
    st.header("Data Visualization")
    col1,col2 = st.columns(2)
    with col1:
        dropdown = st.selectbox('Select one option', [
            "Trends in Admission Over Time",
            "Diagnosis Frequency Analysis",
            "Bed Occupancy Analysis",
            "Length of Stay Distribution",
            "Seasonal Admission Patterns",
            "Doctor-wise Patient Count",
            "Test Frequency Analysis",
            "Monthly Revenue Trends",
            "Diagnosis and Cost Analysis",
            "Analyzing Yearly Patients and Billing amount",
            "Patient-Diagnosis-Test admit-year-wise Billing Analysis",
            "Length of Stay and Billing Correlation",
            "Insurance Coverage vs. Billing Trends by Diagnosis",
            "Doctor Performance Feedback by Diagnosis",
            "Average Billing vs. Length of Stay by Diagnosis"

         ])

    if dropdown == "Trends in Admission Over Time":
            df = get_healthcare_data(query_type="Trends in Admission Over Time")
            fig_admit = px.bar(
                            df,
                            x= 'MONTH_ADDMISIONS',
                            y = 'total_admissions',
                            barmode="group",
                            title="Analyze monthly patient admissions",
                            color_discrete_sequence=px.colors.sequential.Aggrnyl
                        )
            fig_admit.update_layout(
                            xaxis_title="Month Admissions",
                            yaxis_title="Total admits",
                            xaxis_tickangle=90,
                            width = 1200
                        )
            st.plotly_chart(fig_admit)

    elif dropdown == "Diagnosis Frequency Analysis":
            df = get_healthcare_data(query_type="Diagnosis Frequency Analysis")
            fig_diagnosis_count = px.bar(
                            df,
                            x= 'Diagnosis',
                            y = 'diagnosis_count',
                            title="Analyze top 5 most common diagnoses",
                            color_discrete_sequence=px.colors.sequential.Agsunset_r
                        )
            fig_diagnosis_count.update_layout(
                            xaxis_title="Diagnosis",
                            yaxis_title="Total Diagnosis count",
                            xaxis_tickangle=90,
                            width = 1200
                        )
            st.plotly_chart(fig_diagnosis_count)
            
    elif dropdown == 'Bed Occupancy Analysis':
            df = get_healthcare_data(query_type="Bed Occupancy Analysis")
            fig_bed = px.bar(
                            df,
                            x= 'Bed_Occupancy',
                            y = 'occupancy_count',
                            title="Distribution of bed occupancy types",
                            labels={'Bed_Occupancy': 'Bed Occupancy', 'occupancy_count': 'Occupancy Count'},
                            color='occupancy_percentage',
                            color_discrete_sequence=px.colors.sequential.Viridis
                        )
            fig_bed.update_layout(
                            xaxis_title="Bed Occupancy Type",
                            yaxis_title="Total Occupancy count",
                            xaxis_tickangle=60,
                            width = 1000
                        )
            st.plotly_chart(fig_bed)
            
    elif dropdown == 'Length of Stay Distribution':
            df = get_healthcare_data(query_type="Length of Stay Distribution")
            fig_len_stay = px.pie(
            df,
            names='Bed_Occupancy',
            values='avg_length',
            title="Average Length of Stay Distribution by Bed Occupancy",
            labels={"Bed_Occupancy": "Bed Occupancy", 'avg_length': 'Average Length of Stay'}
            )

            st.plotly_chart(fig_len_stay)
            
    elif dropdown == 'Seasonal Admission Patterns':
            df = get_healthcare_data(query_type="Seasonal Admission Patterns")
            fig_season_admit = px.bar(
            df, 
            x='season', 
            y='total_revenue', 
            title="Total Revenue by Season", 
            labels={"season": "Season", "total_revenue": "Total Revenue"},
            color='season',
            color_discrete_sequence=px.colors.sequential.RdBu
            )

            fig_season_admit.update_layout(
                            xaxis_title="Seasons",
                            yaxis_title="Total Revenue",
                            xaxis_tickangle=60,
                            width = 1000
                        )
            st.plotly_chart(fig_season_admit)
            
    elif dropdown == 'Doctor-wise Patient Count':
            df = get_healthcare_data(query_type="Doctor-wise Patient Count")
            fig_doctor_pcount = px.bar(
            df,
            x='Doctor',
            y='patient_count',
            title="Patient Count by Doctor",
            labels={"Doctor": "Doctor", "patient_count": "Patient Count"},
            color='Doctor',  # Color bars by doctor
            color_discrete_sequence=px.colors.qualitative.Set3
            )

            fig_doctor_pcount.update_layout(
                            xaxis_title="Doctors",
                            yaxis_title="Total Patient count",
                            xaxis_tickangle=60
                        )
            st.plotly_chart(fig_doctor_pcount)
            
    elif dropdown == 'Test Frequency Analysis':
            df = get_healthcare_data(query_type="Test Frequency Analysis")
            # Create a bar plot using Plotly
            fig_test_count = px.bar(
                    df,
                    x='test_count',
                    y='Test',
                    title="Test Count by Test Type",
                    labels={"Test": "Test", "test_count": "Test Count"},
                    color='test_count',  # Color bars by count value
                    color_continuous_scale=px.colors.sequential.Cividis
                )
            fig_test_count.update_layout(
                    title="Test Count by Test Type",
                    xaxis_title="Test Count",
                    yaxis_title="Test Type"
                )

                # Display the plot
            st.plotly_chart(fig_test_count)

    elif dropdown == 'Monthly Revenue Trends':
            df = get_healthcare_data(query_type="Monthly Revenue Trends")
            fig_revenue = px.line(
            df,
            x='month',
            y=['total_revenue', 'avg_revenue_per_patient'],
            title="Monthly Total Revnue and Average Revenue per Patient",
            labels={"month": "Month", "total_revenue": "Total Revenue", "avg_revenue_per_patient": "Avg Revenue per Patient"},
            markers=True
            )
            fig_revenue.update_layout(
                xaxis_title="Month",
                yaxis_title="Revenue"
            )
            st.plotly_chart(fig_revenue)
            
    elif dropdown == 'Diagnosis and Cost Analysis':
            df = get_healthcare_data(query_type="Diagnosis and Cost Analysis")
            fig_diagnosis_billing = px.bar(
            df,
            x='Diagnosis',
            y='avg_billing',
            barmode = 'group',
            title="Average billing Amount per patient for each diagnosis",
            labels={"Diagnosis": "Diagnosis", "avg_billing": "Average Billing Amount"},
            color='avg_billing',
            width = 800,
            color_continuous_scale=px.colors.sequential.dense
            )
            fig_diagnosis_billing.update_layout(
                xaxis_title="Diagnosis",
                yaxis_title="Average Billing Amount"
            )

            # Display the plot
            st.plotly_chart(fig_diagnosis_billing)
            
    elif dropdown == 'Analyzing Yearly Patients and Billing amount':
            df = get_healthcare_data(query_type="Analyzing Yearly Patients and Billing amount")
            fig_yearly_bill = px.bar(
            df,
            x='admission_year',
            y=['total_billing_amount','total_patients'],
            title="Analyzing Yearly Patients and Billing amount",
            facet_col= 'Doctor',
            barmode='group',
            labels={'admission_year': 'Year', 'total_billing_amount': 'Total Billing Amount'},
            color_continuous_scale=px.colors.sequential.RdBu
            )
            fig_yearly_bill.update_layout(
                xaxis_title="year",
                yaxis_title="Billing Amount"
            )

            # Display the plot
            st.plotly_chart(fig_yearly_bill)
            
    elif dropdown == 'Patient-Diagnosis-Test admit-year-wise Billing Analysis':
           df = get_healthcare_data(query_type="Patient-Diagnosis-Test admit-year-wise Billing Analysis")
           fig_patient_diagnosis = px.bar(
            df,
            x='admission_year',
            y='total_billing_amount',
            facet_col= 'Test',
            color='Diagnosis',
            barmode='group',
            title="Yearly Patient Diagnosis Test Billing Analysis",
            labels={'admission_year': 'Year', 'total_billing_amount': 'Total Billing Amount'},
            color_continuous_scale=px.colors.sequential.PuBu
            )
           fig_patient_diagnosis.update_layout(
                xaxis_title="year",
                yaxis_title="Billing Amount",
                bargap=0.2,
                height=600, 
                width=1400
            )

            # Display the plot
           st.plotly_chart(fig_patient_diagnosis)
        
    elif dropdown == 'Length of Stay and Billing Correlation':
           df = get_healthcare_data(query_type="Length of Stay and Billing Correlation") 
           # Create a bar chart
           fig = px.bar(
                df,
                x='avg_length_of_stay',
                y='total_billing_amount',
                color='admission_year',
                title="Avg Length of Stay vs Total Billing Amount by Admission Year",
                labels={'admission_year': 'Admission Year', 'total_billing_amount': 'Total Billing Amount', 'avg_length_of_stay':'Avg length of stay(Days)'},
                color_continuous_scale=px.colors.sequential.Viridis,
                height=600,
                width=1000
            )
           fig.update_layout(
                xaxis_title="Avg length of stay(Days)",
                yaxis_title="Total Billing Amount",
                bargap=0.3,
                template="plotly_white"
            )
            # Display the plot
           st.plotly_chart(fig)
    
    elif dropdown =='Insurance Coverage vs. Billing Trends by Diagnosis':
        df = get_healthcare_data(query_type= 'Insurance Coverage vs. Billing Trends by Diagnosis')
        col1, col2 = st.columns(2)
        with col1:
            fig_billing= px.bar(
                df,
                x = 'Diagnosis',
                y = 'total_billing_amount',
                title="Total Billing Amount by Diagnosis",
                labels= {'total_billing_amount':'Total Billing amount'},
                color='Diagnosis',
                color_continuous_scale= px.colors.sequential.Aggrnyl
            )
            
            fig_billing.update_layout(
                xaxis_title="Diagnosis",
                yaxis_title="Total Billing Amount",
                bargap=0.3
            )
            st.plotly_chart(fig_billing)
            
        with col2:
           fig_coverage = px.pie(
                df,
                names='Diagnosis',
                values='insurance_coverage_percentage',
                title="Insurance Coverage Percentage by Diagnosis",
                color='Diagnosis',
                hole= 0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
           st.plotly_chart(fig_coverage)
           
    elif dropdown == 'Doctor Performance Feedback by Diagnosis':
        df = get_healthcare_data(query_type='Doctor Performance Feedback by Diagnosis')
        fig_doctor_performance = px.scatter(df, 
                 x='total_billing_amount', 
                 y='Feedback', 
                 color='Doctor',
                 size='total_patients', 
                 hover_name='Diagnosis',
                 title="Doctor Performance Feedback vs Billing Amount",
                 labels={'total_billing_amount': 'Total Billing Amount', 'Feedback': 'Patient Feedback'})
        
        st.plotly_chart(fig_doctor_performance)
    
    elif dropdown == 'Average Billing vs. Length of Stay by Diagnosis':
        df = get_healthcare_data(query_type= 'Average Billing vs. Length of Stay by Diagnosis')
        fig = px.scatter(df, 
                 x='avg_length_of_stay', 
                 y='avg_billing_amount', 
                 color='Diagnosis', 
                 size='avg_billing_amount',
                 hover_name='Diagnosis',
                 title="Average Billing Amount vs Length of Stay by Diagnosis",
                 labels={'avg_length_of_stay': 'Average Length of Stay (Days)', 
                         'avg_billing_amount': 'Average Billing Amount'}) 
        st.plotly_chart(fig)
        
            
                


                    
