import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import plotly.graph_objects as go

# Load the trained model
model_ev = joblib.load("ev_model.pkl")
model_petrol = joblib.load("petrol_model.pkl")

st.set_page_config(layout="wide")

st.title('Kenderaan Elektrik: Jumlah Kos Alat Pemilikan')

st.write("Kalkulator interaktif yang membolehkan pengguna membandingkan kos pemilikan dan penggunaan kereta petrol dan kereta elektrik, serta melihat bagaimana perubahan faktor tertentu mempengaruhi keputusan." \
"Masukkan butiran kereta di bawah untuk meramal Jumlah Kos Pemilikan (TCO) setiap tahun.")

st.divider()

selected = option_menu(
    menu_title=None,
    options=["TCO Calculator", "Carbon Emission Calculator"],
    orientation = "horizontal",
)

col1, col2 = st.columns(2)

#column left
with col1:
    annual_distance = st.slider("Estimation Annual Driving Distance (km)", 1000, 50000, 38000)
    #car_type = st.selectbox("Type", ["SUV", "Sedan", "MPV", "Hatchback"])

    st.markdown("<h4 style='text-align: center;'>Purchasing costs</h4>", unsafe_allow_html=True)
    
    nested_col3, nested_col4 = st.columns(2)
    with nested_col3:
        nested_col3.write("Elektrik")
        vehicle_cost_EV = nested_col3.number_input('Car Price (RM)', 10000, 5000000, 123800, key="EV")
        roadtax_tax_EV = nested_col3.slider('Road tax', 0, 1000, 0, key='roadtax tax EV')
        #register_tax_EV = nested_col3.slider('Registration tax', 0, 1000, 50, key='registration tax EV')
        residual_value_EV = nested_col3.slider("Residual Value (RM)", 1000, 225000, 61900, key='residual EV')
        home_charging_install = nested_col3.selectbox("Home Charging Installation",['Yes', 'No'])
        
        if home_charging_install == "Yes":
            home_charging_install = 8000
        else:
            home_charging_install = 0
         
        
    with nested_col4:
        nested_col4.write("Petrol")
        vehicle_cost_P = nested_col4.number_input('Car Price (RM)', 10000, 5000000, 128800)
        roadtax_tax_P = nested_col4.slider('Road tax', 0.0, 1000.0, 359.7, key='road tax')
        #register_tax_P = nested_col4.slider('Registration tax', 0, 1000, 50, key='registration tax')
        residual_value_P = nested_col4.slider("Residual Value (RM)", 1000, 225000, 64400)
        
    st.markdown("<h4 style='text-align: center;'>Operating costs</h4>", unsafe_allow_html=True)

    nested_col5, nested_col6 = st.columns(2)
    with nested_col5:
        nested_col5.write("Elektrik")
        #ann_reg_fee_EV = nested_col5.slider("Annual Registration Fee RM", min_value=10, max_value=1000, key='annual registration fee')
        insurance_per_year_EV = nested_col5.slider("Insurans (RM)", 100.0, 10000.0, 3466.6, key='EV insuran')
        maintenance_per_year_EV = nested_col5.slider("Maintenance (RM)", 0, 10000, 563, key='EV maintenance')
        energy_efficiency = nested_col5.slider("Electric Efficiency (Kwh/100km)", 0.00, 20.00, 15.60, key='EV battery')
        electric_cost_day = nested_col5.slider("Electricity day charging cost RM/kWh", 0.00, 1.00, 0.55, key='electric day cost')
        electric_cost_night = nested_col5.slider("Electricity night charging cost RM/kWh", 0.00, 1.00, 0.44, key='electric night cost')
        electric_cost_fast = nested_col5.slider("Electricity fast charging cost RM/kWh", 0.00, 2.00, 1.20, key='electric fast cost')
        day_charging = nested_col5.slider("Share of day charging %", 0.00, 1.00, 0.1, key='share day')
        night_charging = nested_col5.slider("Share of night charging %", 0.00, 1.00, 0.8, key='share night')
        fast_charging = nested_col5.slider("Share of fast charging %", 0.00, 1.00, 0.1, key='share fast')

        ee = energy_efficiency*(annual_distance/100)
        annual_electric_expenditure = (ee*electric_cost_day*day_charging)+(ee*electric_cost_night*night_charging)+(ee*electric_cost_fast*fast_charging)

    with nested_col6:
        nested_col6.write("Petrol")
        #ann_reg_fee_P = nested_col6.slider("Annual Registration Fee RM", min_value=10, max_value=1000, key='annual registration fee P')
        insurance_per_year = nested_col6.slider("Insurans (RM)", 100.0, 10000.0, 3661.9)
        maintenance_per_year = nested_col6.slider("Maintenance (RM)", 0, 10000, 6000)
        fuel_efficiency = nested_col6.slider("Fuel Efficiency (L/100km)", 0.00, 10.00, 7.8)
        fuel_cost = nested_col6.slider("Fuel cost (RM/L)", 0.00, 5.00, 2.05, key='fuel cost')
        
        annual_fuel_expenditure = (fuel_efficiency*(annual_distance/100))*fuel_cost

    st.markdown("<h4 style='text-align: center;'>Financing costs</h4>", unsafe_allow_html=True)

    nested_col7, nested_col8 = st.columns(2)
    with nested_col7:
        nested_col7.write("Elektrik")
        depo_EV = nested_col7.slider("Down payment %", min_value=10, max_value=1000, key='EV depo')
        loan_EV = nested_col7.slider("Loan rate %", min_value=10, max_value=1000, key='EV loan')
        loan_length_EV = nested_col7.slider("Loan length YEARS", min_value=10, max_value=1000, key='EV loan length')
                
    with nested_col8:
        nested_col8.write("Petrol")
        depo = nested_col8.slider("Down payment %", min_value=10, max_value=1000, key='depo')
        loan = nested_col8.slider("Loan rate %", min_value=10, max_value=1000, key='loan')
        loan_length = nested_col8.slider("Loan length YEARS", min_value=10, max_value=1000, key='loan length')

# Predict button
if st.button('Predict'):
    #set for 10 years prediction
    years = list(range(1, 11))
    ev_tco, petrol_tco = [], []
    ev_cum, petrol_cum = [], []
    
    #Initialize variable
    CO2_reduction = 0 
    cum_ev = 0
    cum_petrol = 0
    
    for year in years:
        #Create a DataFrame for EV model input
        input_ev = pd.DataFrame({
            'Annual driving distance':[annual_distance],'Fuel type':[1], 'Car price':[vehicle_cost_EV],
            'Road tax fee per year':[roadtax_tax_EV], 'Insurance fee per year':[insurance_per_year_EV],
            'Maintenance cost per year':[maintenance_per_year_EV],'Residual value':[residual_value_EV],
            'Home charging installation':[home_charging_install],'EV Energy Efficiency':[energy_efficiency],
            'Electric day charging cost':[electric_cost_day], 'Electric night charging cost':[electric_cost_night],
            'Electric fast charging cost':[electric_cost_fast], 'Share of day charging':[day_charging], 
            'Share of night charging':[night_charging], 'Share of fast charging':[fast_charging], 
            'Annual electric expenditure':[annual_electric_expenditure], 'Year':[year]
        })

        #Create a DataFrame for petrol model input
        input_petrol = pd.DataFrame({
            'Annual driving distance':[annual_distance],'Fuel type':[0], 'Car price':[vehicle_cost_P],
            'Road tax fee per year':[roadtax_tax_P], 'Insurance fee per year':[insurance_per_year],
            'Maintenance cost per year':[maintenance_per_year],'Residual value':[residual_value_P],
            'Fuel efficiency':[fuel_efficiency], 'Fuel cost':[fuel_cost], 
            'Annual fuel expenditure':[annual_fuel_expenditure], 'Year':[year]
        })

        # Calculate estimated CO2 emissions (assuming avg CO2 emission per liter petrol = 2.3 kg)
        if fuel_cost != 0:
            CO2_emission_petrol = (annual_fuel_expenditure / fuel_cost) * 2.3  # 2.3 kg CO₂ per liter
        else:
            print("Error: Fuel cost cannot be zero!")
        
        CO2_emission_ev = (annual_electric_expenditure / 0.216) * 0.4  # Est. 0.4 kg/kWh and RM0.216/kWh
        CO2_reduction = CO2_emission_petrol - CO2_emission_ev
       
        #Predict
        ev_pred = model_ev.predict(input_ev)[0]  # Get prediction
        petrol_pred = model_petrol.predict(input_petrol)[0]

        # Calculate cumulative costs
        cum_ev += ev_pred[0]  # Annual cost
        cum_petrol += petrol_pred[0]
        
        #append
        ev_tco.append(ev_pred[0])  # Annual cost
        ev_cum.append(ev_pred[1])  # Cumulative (or sum manually if needed)
        petrol_tco.append(petrol_pred[0])
        petrol_cum.append(petrol_pred[1])

    #column right
    with col2:
        col2.subheader("Estimated Total Cost of Ownership (TCO)")
        st.success(f"Annual carbon emission reduction: {CO2_reduction:,.2f} kg CO2")

        nested_col9, nested_col10 = st.columns(2)
        with nested_col9:
            nested_col9.write('Battery electric TCO')
            nested_col9.success(f"Estimated TCO per year: MYR {ev_tco[-1]:,.2f}")
            nested_col9.success(f"Cumulative cost for 10 years: MYR {ev_cum[-1]:,.2f}")

        with nested_col10:
            nested_col10.write('Petrol TCO')
            nested_col10.success(f"Estimated TCO per year: MYR {petrol_tco[-1]:,.2f}")
            nested_col10.success(f"Cumulative cost for 10 years: MYR {petrol_cum[-1]:,.2f}")

        # Plot 10-year trend
        st.subheader("10-Year Cumulative Cost Trend")
        fig, ax = plt.subplots()
        ax.plot(years, ev_cum, label="EV", marker="o")
        ax.plot(years, petrol_cum, label="Petrol", marker="o")
        ax.set_xlabel("Year")
        ax.set_ylabel("Cumulative Cost (RM)")
        ax.legend()
        st.pyplot(fig)
