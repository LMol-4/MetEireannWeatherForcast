#Program Name - Met Eireann Weather Forcast
#Author - Luke Molony
#Date - 1/10/2024
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import os

# Function to get weather forecast data
def get_weather_forecast(latitude, longitude):
    
    if os.path.exists('weather_forecast.txt'):
        os.remove('weather_forecast.txt')

    output_file = "weather_forecast.txt"
    
    # Define the base URL for the API
    base_url = "http://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast"
    
    # Get current UTC date and time using timezone-aware datetime
    current_time = datetime.now(timezone.utc)
    start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(days=1) - timedelta(seconds=1)

    # Format the timestamps to the required format (ISO 8601)
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")

    # Construct the full URL with latitude, longitude, from, and to times
    full_url = f"{base_url}?lat={latitude};long={longitude};from={start_time_str};to={end_time_str}"
    
    # Send the request to the API
    response = requests.get(full_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Data fetched successfully.")
        
        # Parse the XML content
        xml_data = response.content
        root = ET.fromstring(xml_data)
        
        # Temporary dictionary to store weather data by time
        weather_data = {}

        # Iterate over each 'time' element in the 'product' section
        for time_element in root.findall(".//time"):
            from_time = time_element.get('from')
            to_time = time_element.get('to')

            # Find the temperature, precipitation, humidity, and wind speed data in each 'time' tag
            temperature = time_element.find(".//temperature")
            precipitation = time_element.find(".//precipitation")
            humidity = time_element.find(".//humidity")
            wind_speed = time_element.find(".//windSpeed")
            
            # Initialize a dictionary for this time period if not already present
            if from_time not in weather_data:
                weather_data[from_time] = {"to_time": to_time, "temperature": None, "precipitation": None, "humidity": None, "wind_speed": None}

            # If temperature is found, add it to the dictionary
            if temperature is not None:
                weather_data[from_time]["temperature"] = f"{temperature.get('value')} {temperature.get('unit')}"

            # If precipitation is found, add it to the dictionary
            if precipitation is not None:
                weather_data[from_time]["precipitation"] = f"{precipitation.get('value')} {precipitation.get('unit')}"

            # If humidity is found, add it to the dictionary
            if humidity is not None:
                weather_data[from_time]["humidity"] = f"{humidity.get('value')} %"

            # If wind speed is found, add it to the dictionary
            if wind_speed is not None:
                wind_speed_value = wind_speed.get('mps')  # 'mps' stands for meters per second
                weather_data[from_time]["wind_speed"] = f"{wind_speed_value} m/s"
        
        # Open a text file in write mode and output weather data
        with open(output_file, 'w') as file:
            file.write(f"Weather forecast for {start_time.strftime('%Y-%m-%d')}\n")
            file.write("="*40 + "\n")
            
            # Iterate through the weather data and print all the data together
            for from_time, data in weather_data.items():
                to_time = data["to_time"]
                temperature = data["temperature"]
                precipitation = data["precipitation"]
                humidity = data["humidity"]
                wind_speed = data["wind_speed"]
                
                file.write(f"From {from_time} to {to_time}:\n")
                
                if temperature is not None:
                    file.write(f"  Temperature: {temperature}\n")
                
                if precipitation is not None:
                    file.write(f"  Precipitation: {precipitation}\n")
                
                if humidity is not None:
                    file.write(f"  Humidity: {humidity}\n")
                
                if wind_speed is not None:
                    file.write(f"  Wind Speed: {wind_speed}\n")
                
                file.write("\n")

        print(f"Data successfully written to {output_file}")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

# Example usage of the function
if __name__ == "__main__":

    # Define the coordinates for the location
    latitude = 53.3498    # Example: Dublin, Ireland
    longitude = -6.2603
    
    # Get the weather forecast data and write to the file
    get_weather_forecast(latitude, longitude)
