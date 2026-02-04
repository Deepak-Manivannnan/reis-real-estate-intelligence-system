import json
import pandas as pd

# Load frozen artifacts
with open("artifacts/location_grouped_values.json", "r") as f:
    LOCATION_GROUPED_VALUES = json.load(f)

with open("artifacts/final_feature_columns.json", "r") as f:
    FINAL_FEATURE_COLUMNS = json.load(f)

# Amenity columns used during training 
amenity_feature = {
    "nearby school": "nearby_school_1km",
    "nearby hospital": "nearby_hospital_1km",
    "near by shopping mall": "nearby_mall_1km",
    "gym": "nearby_gym_1km",
    "swimming pool": "swimmingpool",
    "rain water harvesting": "rainwaterharvesting",
    "sports facility": "sportsfacility",
    "power backup": "powerbackup",
    "parking": "car parking",
    "children play area": "childrens_playarea",
    "lift": "liftavailable",
}


# Individual feature processors
def process_location(user_location):
    location = user_location.strip().lower()

    if location not in LOCATION_GROUPED_VALUES:
        location = "other"

    features = {}
    for loc in LOCATION_GROUPED_VALUES:
        col = f"loc_{loc}"
        features[col] = 1 if location == loc else 0

    return features


def process_area_sqft(area_sqft):
    area_sqft = float(area_sqft)
    if area_sqft <= 0:
        raise ValueError("Area sqft must be greater than 0")

    return {"area_sqft": area_sqft}


def process_resale(resale_input):
    resale_input = resale_input.strip().lower()

    if resale_input not in ["new", "old"]:
        raise ValueError("Resale must be 'new' or 'old'")

    return {"resale": 1 if resale_input == "old" else 0}


def process_bedrooms(no_of_bedrooms):
    no_of_bedrooms = int(no_of_bedrooms)
    if no_of_bedrooms < 1:
        raise ValueError("Number of bedrooms must be >= 1")

    return {"no_of_bedrooms": no_of_bedrooms}


def process_amenities(selected_amenities):
    if not isinstance(selected_amenities, list):
        raise ValueError("Amenities must be a list")

    amenity_score = 0

    for amenity in selected_amenities:
        key = amenity.strip().lower()

        if key in amenity_feature:
            amenity_score += 1

    return {"amenity_score": amenity_score}



# Combine all the features into a model-ready single-row DataFrame 
def get_model_features(user_input):
    
    features = {}

    features.update(process_location(user_input["location"]))
    features.update(process_area_sqft(user_input["area_sqft"]))
    features.update(process_resale(user_input["resale"]))
    features.update(process_bedrooms(user_input["no_of_bedrooms"]))
    features.update(process_amenities(user_input["amenities"]))

    feature_df = pd.DataFrame([features])

    # Align columns exactly how model was trained
    feature_df = feature_df.reindex(columns=FINAL_FEATURE_COLUMNS, fill_value=0)

    return feature_df
