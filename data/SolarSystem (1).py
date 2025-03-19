import requests
import os
import json
import re

# URL API NASA Horizons
url = "https://ssd.jpl.nasa.gov/api/horizons.api"

# ID planets
planet_ids = {
    "199": "Меркурий",
    "299": "Венера",
    "399": "Земля",
    "499": "Марс",
    "599": "Юпитер",
    "699": "Сатурн",
    "799": "Уран",
    "899": "Нептун",
    "999": "Плутон",
    "2000001": "Церера",
    "1000012": "Комета Хейла-Боппа"
}

# General enquiry parameters
base_params = {
    "format": "json",
    "OBJ_DATA": "YES",
    "MAKE_EPHEM": "NO",
}

# Function for parsing `result`
def parse_result(result_text):
    data = {}

    # Checking if the required information is available
    if not result_text:
        return {}
    clean_text = re.sub(r'\s+', ' ', result_text)

    # Regular expressions to search for all parameters
    patterns = {
        "radius_km": r"(?i)Vol\. mean radius \(km\)\s*=\s*([\d.]+)(?:\+-[\d.]+)?",
        "equatorial_radius_km": r"Equ\. radius, km\s*=\s*([\d.]+)",
        "polar_radius_km": r"Polar axis, km\s*=\s*([\d.]+)",
        "density_g_cm^3": r"Density,? \(?g/cm\^3\)?\s*=\s*([\d.]+)",
        "density_g_cm^-3": r"Density \(?g cm\^-3\)?\s*=\s*([\d.]+)",
        "density_g_Neptune_cm3": r"Density\s*(?:\(R=\d+\s*km\))?\s*=\s*([\d.]+)\s*g/cm\^3",
        "mass_kg x10^22": r"Mass x10\^22 \(kg\)\s*=\s*([\d.]+)",
        "mass_kg x10^23": r"Mass x10\^23 \(kg\)\s*=\s*([\d.]+)",
        "mass_kg x10^24": r"Mass x10\^24 \(kg\)\s*=\s*([\d.]+)",
        "mass_kg x10^26": r"Mass x\s*10\^26 \(kg\)\s*=\s*([\d.]+)",
        "gravity_polar_m_s2": r"g_p, m/s\^2 \(polar\)\s*=\s*([\d.]+)",
        "gravity_equator_m_s2": r"g_e, m/s\^2 \(equatorial\)\s*=\s*([\d.]+)",
        "gravity_mean_m_s^2": r"g_o, m/s\^2\s*=\s*([\d.]+)",
        "gravity_mean_km^3_s^2": r"GM \(km\^3/s\^2\)\s*=\s*([\d.+-]+)",
        "escape_velocity_km_s": r"Escape velocity\s*=\s*([\d.]+) km/s",
        "sidereal_rotation_period_hr": r"Mean sidereal day, hr\s*=\s*([\d.]+)",
        "mean_solar_day_sec": r"Mean solar day 2000.0, s\s*=\s*([\d.]+)",
        "obliquity_deg": r"Obliquity to orbit, deg\s*=\s*([\d.]+)",
        "mean_surface_temp_K": r"Mean surface temp \(Ts\), K\s*=\s*([\d.]+)",
        "mean_temp_K": r"(?i)Mean Temperature\s*\(K\)\s*=\s*([\d.]+)",
        "atmos_temp_K": r"(?i)Atmos\. temp\. \(1 bar\)\s*=\s*([\d.]+)(?:\+-[\d.]+)?\s*K",
        "albedo": r"(?i)Geometric albedo\s*=\s*([\d.+-]+)",
        "orbital_period_days": r"Sidereal\s*(orb\.?\s*per\.?\s*(?:\w*)?)?\s*period\s*(?:[.,]?\s*[dD])?\s*=\s*([\d.]+)\s*d",
        "orbital_speed_km_s": r"Orbital speed, km/s\s*=\s*([\d.]+)"
    }

    # Find for parameters
    for key, pattern in patterns.items():
        match = re.search(pattern, clean_text)
        if match:
            data[key] = float(match.group(1)) 

    return data

# JSON
script_dir = os.path.dirname(os.path.abspath(__file__))

all_planets_data = []

try:
    for planet_id, planet_name in planet_ids.items():
        params = base_params.copy()
        params["COMMAND"] = planet_id 

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "result" not in data:
            print(f"Error: API did not return ‘result’ for {planet_name}")
            continue

        # Parsing text `result`
        parsed_data = parse_result(data["result"])
        # Writing the data
        all_planets_data.append({
            "planet_id": planet_id,
            "planet_name": planet_name,
            "physical_characteristics": parsed_data
        })

    # Save JSON
    output_path = os.path.join(script_dir, "structured_planet_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_planets_data, f, ensure_ascii=False, indent=4)

    print(f"The data is stored in '{output_path}'.")
except requests.exceptions.RequestException as e:
    print(f"Error when requesting data: {e}")
except ValueError as e:
    print(f"Processing error JSON: {e}")
