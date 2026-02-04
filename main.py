import streamlit as st
import requests
import json

# Page config
st.set_page_config(layout="wide")

# Header
st.markdown("### REIS – Real Estate Intelligence System",)

st.divider()

# Property Details
st.subheader("Property Details")

col1, col2, col3, col4, col5 = st.columns([1.5,1.5,1.5,1.5,4])

with col1:
    with open("artifacts/locations.json", "r") as f:
     locations = json.load(f)    
    location = st.selectbox("Location",locations,index=None,placeholder="Select location")

with col2:
    bedrooms = st.selectbox("BHK Type",["1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"],
                            index=None,placeholder="Select BHK type")
   
with col3:
    resale = st.selectbox("Property Type",["New", "Old"],index=None,placeholder="Select property type")

with col4:
    area_sqft = st.number_input("Area (sqft)",min_value=300,step=50,value=None,placeholder="Enter built-up area")

with col5:
    amenities = st.multiselect("Amenities (optinal)",
        [
        "Lift",
        "Parking",
        "Power Backup",
        "Sports Facility",
        "Children Play area",
        "Gym",
        "Rain Water Harvesting",
        "Swimming Pool",
        "Nearby Shopping Mall",
        "Nearby School",
        "Nearby Hospital"
    ],
    placeholder="Select Amenities")

# Call to Action
left, center, right = st.columns([4, 1.5, 4])

with center:
    submit = st.button("Check Price & Insights", width="content")

st.divider()

if submit:

    # Validate required fields
    if location is None:
        st.warning("Please select a location")
        st.stop()

    if bedrooms is None:
        st.warning("Please select BHK type")
        st.stop()

    if resale is None:
        st.warning("Please select property type")
        st.stop()

    if area_sqft is None:
        st.warning("Please enter area in sqft")
        st.stop()

    # Convert BHK string to integer
    no_of_bedrooms = 5 if "5+" in bedrooms else int(bedrooms.split()[0])

    # Prepare payload
    payload = {
        "location": location,
        "area_sqft": area_sqft,
        "resale": resale,
        "no_of_bedrooms": no_of_bedrooms,
        "amenities": amenities
        }

    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            st.error("Unable to fetch prediction.")
        else:
            result = response.json()
            insights = result["insights"]

            left, center, right = st.columns([2, 4, 2])

            with center:
                # Estimated Price Card
                st.subheader("Estimated Market Price")
                st.write(f"### ₹ {int(result['estimated_price_lakhs'])} Lakhs")
                st.divider()

                # Insights 
                st.subheader("Market Insights")

                st.write(f"""  
                        📊 Houses in this area are mostly priced between ₹ {insights['price_range_lakhs'][0]} Lakhs and ₹ {insights['price_range_lakhs'][1]} Lakhs.\n          
                        📍 Within this range, most homes are priced around ₹ {insights['median_price_lakhs']} Lakhs.\n
                        📐 The usual price per square foot in this area is ₹ {insights["median_price_per_sqft"]}.""")
                
                st.divider()

                # Price Summary
                st.subheader("Price Summary")

                st.write("This estimated price reflects the value of a house with the details you selected,"
                         "based on past house prices in this area.")
             
                threshold = 0.05 *insights['median_price_lakhs']  # 5%

                if result['estimated_price_lakhs'] < insights['median_price_lakhs'] - threshold:
                    summary_text = (
                        "Prices in this area are generally higher than this estimate."
                        "This suggests the price shown here is on the lower side when compared to overall prices in the area."
                        "You can use it as a helpful starting point when checking similar houses."
                    )
                elif result['estimated_price_lakhs'] > insights['median_price_lakhs'] + threshold:
                    summary_text = (
                        "Prices in this area are generally lower than this estimate."
                        "This means the price shown here is on the higher side when compared to overall prices in the area."
                        "The estimate may be higher because the selected property has more or better features than a typical home in this area."
                        "Since the estimate reflects the details you selected, so it may help to compare carefully with similar houses before deciding."
                    )
                else:
                    summary_text = (
                        "This estimated price is close to what houses usually cost in this area."
                        "It suggests the price shown here is very similar to overall prices nearby."
                        "It can be used as a strong reference when checking whether a similar house price is reasonable."
                    )
                
                st.write(summary_text)

                st.caption(
                        "Note: This estimate is meant to help with decision making and may not reflect the exact value of a specific property."
                    )

    except requests.exceptions.RequestException:
        st.error("Backend API is not running.")

