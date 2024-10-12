import numpy as np
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
import astropy.units as u
# from poliastro.frames import EME2000

def parse_oem_file(file_path):
    epochs = []
    positions = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('2024'):
                parts = line.split()
                epochs.append(Time(parts[0]))
                positions.append([float(parts[1]), float(parts[2]), float(parts[3])])
    positions = np.array(positions) * u.km
    return epochs, positions

def calculate_highest_altitude(oem_file, target_longitude, target_latitude, date):
    observer_location = EarthLocation.from_geodetic(lon=target_longitude, lat=target_latitude)
    epochs, positions = parse_oem_file(oem_file)
    target_day_start = Time(f"{date}T00:00:00")
    target_day_end = Time(f"{date}T23:59:59")
    # max_altitude = -90  # Initialize with a very low altitude
    # max_altitude_time = None
    altitudes = []

    for i, (epoch, position) in enumerate(zip(epochs, positions)):
        if target_day_start <= epoch <= target_day_end:
            # position = positions[i]
            sat_coord = SkyCoord(x=position[0], y=position[1], z=position[2], representation_type='cartesian', frame='gcrs', obstime=epoch)
            # sat_coord = SkyCoord(x=position[0], y=position[1], z=position[2], representation_type='cartesian', frame='icrs', obstime=epoch)
            altaz_frame = AltAz(obstime=epoch, location=observer_location)
            sat_altaz = sat_coord.transform_to(altaz_frame)
            altitude = sat_altaz.alt.deg
            azimush = sat_altaz.az.deg
            if altitude > 30:
                altitudes.append((epoch, altitude, azimush))
    #         if altitude > max_altitude:
    #             max_altitude = altitude
    #             max_altitude_time = epoch
    # return max_altitude, max_altitude_time
    return altitudes

# Example usage
timezoneJapan = 9 * u.hour
timezoneShanghai = 8 * u.hour
oem_file = '/zang/Python/RocketLaunch/data/CSS_OEM_20240927000644_0001.dat'
target_longitude = 100.3      # Longitude of target (in degrees)
target_latitude = 40.96667    # Latitude of target (in degrees)
observation_time = '2024-10-02'
altitudes = calculate_highest_altitude(oem_file, target_longitude, target_latitude, observation_time)
# altitude, time_of_max_altitude = calculate_highest_altitude(oem_file, target_longitude, target_latitude, observation_time)
for altitude in altitudes:
    print(f"{altitude[0] + timezoneJapan}, {altitude[1]:04.1f}, {altitude[2]:05.1f}")