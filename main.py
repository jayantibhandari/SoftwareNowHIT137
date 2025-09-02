import pandas as pd      # pandas: for working with data tables and spreadsheets
import numpy as np      # numpy: for mathematical operations and arrays
import os               # os: for file and folder operations

# Define the path to the folder containing temperature CSV files
DATA_FOLDER = "/Users/jyotiadhikari/Desktop/SoftwareNow/Assignment 2/temperatures"

def load_data():
    """
    Load and combine temperature data from multiple CSV files.
    
    This function reads all CSV files in the temperatures folder, reshapes the data
    from wide format (months as columns) to long format (one row per station-month),
    and combines all years into a single DataFrame.
    
    Returns:
        pandas.DataFrame: Combined temperature data with columns for Date, Temperature, Station, etc.
    """
    # Initialize empty list to store data from all files
    all_data = []
    
    # Loop through each file in the temperatures directory
    for file in os.listdir(DATA_FOLDER):
        # Only process CSV files to avoid any other file types
        if file.endswith('.csv'):
            # Construct full file path
            file_path = os.path.join(DATA_FOLDER, file)
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            
            # Extract year from filename using regular expressions
            # Files are named like "stations_group_1992.csv", so we extract the 4-digit year
            import re
            year_match = re.search(r'(\d{4})', file)
            year = int(year_match.group(1)) if year_match else 1992
            
            # Define which columns contain station metadata vs temperature data
            # These columns contain station information that we want to keep
            id_cols = ['STATION_NAME', 'STN_ID', 'LAT', 'LON']
            
            # These columns contain temperature data for each month
            month_cols = ['January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December']
            
            # Reshape data from wide to long format using pandas melt()
            # This transforms 12 month columns into rows with Month and Temperature columns
            df_melted = pd.melt(df, 
                               id_vars=id_cols,           # Keep these columns as identifiers
                               value_vars=month_cols,     # Transform these columns to rows
                               var_name='Month',          # New column name for month names
                               value_name='Temperature')  # New column name for temperature values
            
            # Add year information to each row
            df_melted['Year'] = year
            
            # Create a mapping dictionary to convert month names to numbers
            # This is necessary because pandas needs numeric months to create dates
            month_mapping = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            
            # Apply the mapping to create numeric month column
            df_melted['Month_Num'] = df_melted['Month'].map(month_mapping)
            
            # Create proper datetime objects for time series analysis
            # We set day=1 for the first day of each month as a standard
            df_melted['Date'] = pd.to_datetime(
                df_melted[['Year', 'Month_Num']].rename(columns={'Month_Num': 'month'}).assign(day=1)
            )
            
            # Create a simplified station column for easier grouping in other functions
            df_melted['Station'] = df_melted['STATION_NAME']
            
            # Add this processed DataFrame to our collection
            all_data.append(df_melted)
    
    # Combine all DataFrames into one large DataFrame
    if all_data:
        # ignore_index=True creates a new continuous index across all data
        combined_data = pd.concat(all_data, ignore_index=True)
        return combined_data
    else:
        # Return empty DataFrame if no data was found
        return pd.DataFrame()

def seasonal_average(data):
    """
    Calculate average temperatures for each season across all stations and years.
    
    Seasons are defined according to Australian meteorological seasons:
    - Summer: December, January, February
    - Autumn: March, April, May  
    - Winter: June, July, August
    - Spring: September, October, November
    
    Args:
        data (pandas.DataFrame): Combined temperature data
    """
    # Ensure the Date column is properly formatted as datetime
    data['Date'] = pd.to_datetime(data['Date'])
    
    # Extract month number from date for seasonal grouping
    data['Month'] = data['Date'].dt.month
    
    # Define seasons using Australian meteorological definitions
    # Each season maps to a list of month numbers
    seasons = {
        "Summer": [12, 1, 2],    # Dec, Jan, Feb - hottest months
        "Autumn": [3, 4, 5],     # Mar, Apr, May - cooling down
        "Winter": [6, 7, 8],     # Jun, Jul, Aug - coldest months
        "Spring": [9, 10, 11]    # Sep, Oct, Nov - warming up
    }
    
    # Dictionary to store calculated seasonal averages
    results = {}
    
    # Calculate average temperature for each season
    for season, months in seasons.items():
        # Filter data for months belonging to current season
        season_data = data[data['Month'].isin(months)]['Temperature']
        
        # Remove any missing values (NaN) before calculating mean
        season_data = season_data.dropna()
        
        # Calculate the mean temperature for this season
        results[season] = season_data.mean()
    
    # Write results to output file
    # Using 'w' mode overwrites any existing file
    with open("average_temp.txt", "w") as f:
        for season, avg in results.items():
            # Format temperature to 1 decimal place with degree symbol
            f.write(f"{season}: {avg:.1f}°C\n")

def temperature_range(data):
    """
    Find the weather station(s) with the largest temperature range.
    
    Temperature range is calculated as the difference between the highest
    and lowest temperature recorded at each station across all years.
    
    Args:
        data (pandas.DataFrame): Combined temperature data
    """
    # Group data by station and get temperature statistics for each
    grouped = data.groupby("Station")["Temperature"]
    
    # Calculate temperature range for each station (max - min)
    ranges = grouped.max() - grouped.min()
    
    # Find the maximum range value across all stations
    max_range = ranges.max()
    
    # Find all stations that have this maximum range
    # (there could be multiple stations with the same max range)
    stations = ranges[ranges == max_range].index
    
    # Write results to output file
    with open("largest_temp_range_station.txt", "w") as f:
        for station in stations:
            # Get the actual max and min temperatures for this station
            max_temp = grouped.max()[station]
            min_temp = grouped.min()[station]
            
            # Write detailed information about the station's temperature range
            f.write(f"Station {station}: Range {max_range:.1f}°C "
                   f"(Max: {max_temp:.1f}°C, Min: {min_temp:.1f}°C)\n")

def temperature_stability(data):
    """
    Identify the most stable and most variable weather stations.
    
    Stability is measured using standard deviation - lower standard deviation
    indicates more consistent temperatures (more stable), while higher standard
    deviation indicates more variable temperatures.
    
    Args:
        data (pandas.DataFrame): Combined temperature data
    """
    # Group data by station and calculate temperature statistics
    grouped = data.groupby("Station")["Temperature"]
    
    # Calculate standard deviation for each station
    # Standard deviation measures how spread out the temperatures are
    stddevs = grouped.std()
    
    # Find the minimum and maximum standard deviations
    min_std = stddevs.min()  # Most stable (least variable)
    max_std = stddevs.max()  # Most variable (least stable)
    
    # Find all stations with minimum standard deviation (most stable)
    stable_stations = stddevs[stddevs == min_std].index
    
    # Find all stations with maximum standard deviation (most variable)
    variable_stations = stddevs[stddevs == max_std].index
    
    # Write results to output file
    with open("temperature_stability_stations.txt", "w") as f:
        # Write information about most stable stations
        for station in stable_stations:
            f.write(f"Most Stable: Station {station}: StdDev {min_std:.1f}°C\n")
        
        # Write information about most variable stations  
        for station in variable_stations:
            f.write(f"Most Variable: Station {station}: StdDev {max_std:.1f}°C\n")

# Main execution block - only runs when script is executed directly
if __name__ == "__main__":
    # Step 1: Load and process all temperature data from CSV files
    data = load_data()
    
    # Step 2: Calculate seasonal temperature averages
    seasonal_average(data)
    
    # Step 3: Find stations with largest temperature ranges
    temperature_range(data)
    
    # Step 4: Analyze temperature stability across stations
    temperature_stability(data)