from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from Preprocessing import get_model_features
from Insights import generate_reis_insights


# Create app
app = FastAPI()

# Loading saved model 
model = joblib.load("reis_svr_model.pkl")

# Input schema for input data validation
class PredictionInput(BaseModel):
    location: str
    area_sqft: int
    resale: str
    no_of_bedrooms: int
    amenities: list[str]


# Prediction route
@app.post("/predict")
def predict(data: PredictionInput):
    
    user_input = data.model_dump()

    # Preprocess user input
    feature_df = get_model_features(user_input)

    # Predict log price
    log_price = model.predict(feature_df)[0]

    # Convert to actual price
    price = np.exp(log_price)
    price_lakhs = round(price / 100000, 2)

    # Generating insights
    insights = generate_reis_insights(
        location=user_input["location"].lower()
        )

    # Return JSON
    return {
        "estimated_price_lakhs": price_lakhs,
        "insights": insights
    }


  