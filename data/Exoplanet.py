import requests
import pandas as pd
import os

# API key
API_KEY = ''

# URL to request data on exoplanets
url = f"https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+pscomppars+where+disc_facility+like+%27%25TESS%25%27+order+by+pl_orbper+desc&format=json&api_key={API_KEY}"

try:
    # Request
    response = requests.get(url)
    response.raise_for_status()

    # Checking the content of the response
    if response.text.strip():
        data = response.json()
        df = pd.DataFrame(data)

        # Selecting the desired columns
        columns_to_keep = [
            'pl_name', 'hostname', 'st_spectype','pl_orbper', 'pl_rade', 'pl_bmasse',
            'pl_dens','sy_dist', 'pl_eqt', 'st_teff', 'st_mass'
        ]
        df = df[columns_to_keep]

        # Rename the columns
        df.rename(columns={
            'pl_rade': 'pl_radius',
            'pl_bmasse': 'pl_mass',
            'sy_dist': 'to_star_distance',
            'pl_orbper': 'pl_orbital_period',
            'pl_eqt': 'equilibrium_temperature_pl',
            'st_teff': 'star_effective_temperature',
            'pl_dens': 'pl_density',
            'hostname': 'host_star'
        }, inplace=True)

        # Data cleaning delete rows with missing values in key columns
        df.dropna(subset=['pl_name', 'host_star','pl_orbital_period', 'pl_radius', 'pl_mass', 'to_star_distance', 'star_effective_temperature'], inplace=True)

        # Convert numeric columns to valid types
        numeric_columns = ['pl_orbital_period', 'pl_radius', 'pl_mass', 'to_star_distance', 'star_effective_temperature', 'pl_density', 'equilibrium_temperature_pl', 'st_mass']
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

        # Get the path to the directory where the current file is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "cleaned_tess_exoplanets_data.json")
        df.to_json(output_path, orient='records', lines=True)
        print(f"The cleared data has been successfully saved to a file '{output_path}'.")
    else:
        print("The server returned an empty response.")
except requests.exceptions.RequestException as e:
    print(f"Error when requesting data: {e}")
except ValueError as e:
    print(f"Error during JSON processing: {e}")