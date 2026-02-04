import pandas as pd

# Load cleaned dataset 
df=pd.read_csv("cleaned_chennai_dataset.csv")

df["location"] = df["location"].str.strip().str.lower()

# Group rare locations to avoid unreliable statistics
locations_count = df.groupby("location").size().sort_values(ascending=False)

rare_locations = locations_count[locations_count < 20].index.tolist()

df["location_grouped"] = df["location"].apply(lambda x : "other" if x in rare_locations else x)

# Create price per sqft column 
df["price_per_sqft"] = df["price"]/df["area_sqft"]

# Filter dataset for a given location
def get_filtered_df(location):
    if location not in df["location_grouped"].values:
        location = "other"                    
    filtered_df = df[df["location_grouped"]==location]
    return filtered_df

# Get median price for the location (in lakhs)
def get_location_median(location):                  
    filtered_df = get_filtered_df(location)
    if filtered_df.empty:
        return None
    else:
        median_price = filtered_df["price"].median()/100000
        return round(median_price,2)
        
# Get typical price range (25th–75th percentile) in lakhs     
def get_location_price_range(location):
    filtered_df = get_filtered_df(location)
    if filtered_df.empty:
        return None  
    else:
        price_range = (int(filtered_df["price"].quantile(0.25)/100000),int(filtered_df["price"].quantile(0.75)/100000))
        print("PRICE RANGE:", price_range)

        return price_range  

# Get median price per sqft for the location
def get_location_median_price_per_sqft(location):
    filtered_df = get_filtered_df(location)
    if filtered_df.empty:
        return None
    else:
        price_per_sqft = filtered_df["price_per_sqft"].median()
        return int(price_per_sqft)
                        
# get all insights into a single dictionary   
def generate_reis_insights(location): 
    info={}

    median_price = get_location_median(location)
    info["median_price_lakhs"] = median_price

    price_range = get_location_price_range(location)
    info["price_range_lakhs"] = price_range

    price_per_sqft = get_location_median_price_per_sqft(location)
    info["median_price_per_sqft"] = price_per_sqft

    return info