import requests
import pandas as pd

url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
response = requests.get(url)

if response.status_code == 200:
    raw_data = response.json()
    earthquakes = raw_data['result']
    
    for eq in earthquakes:
        coords = eq.get('geojson', {}).get('coordinates', [0, 0])
        eq['lng'] = coords[0] 
        eq['lat'] = coords[1]  
        
    df = pd.DataFrame(earthquakes)
    
    print(f"Successfully loaded {len(df)} recent earthquakes.")
    
    cleaned_df = df[['title', 'mag', 'depth', 'date_time', 'lat', 'lng']]
    
    csv_filename = "guncel_veriler.csv"
    cleaned_df.to_csv(csv_filename, index=False)
    
    print(f"Data saved successfully to {csv_filename}")
else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")