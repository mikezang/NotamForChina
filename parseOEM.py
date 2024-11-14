from timeit import timeit
import math
from datetime import timedelta, datetime
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from geopy.distance import geodesic
from re import match
from astropy.time import Time, TimeDelta
from astropy import units as u
from poliastro.twobody import Orbit
from poliastro.bodies import Earth
import requests
import numpy as np

from myModules import myUtils
from myModules import myNet

################################################################################################
def isStartsWithDate(dateStr):
    pattern = r'^\d{4}-\d{2}-\d{2}'
    return match(pattern, dateStr)

################################################################################################
def parseLastDataOemFile(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        line = lines[-1]
        line = line.strip()
        parts = line.split()
        try:
            timestamp = datetime.strptime(parts[0], '%Y-%m-%dT%H:%M:%S.%f')
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            vx, vy, vz = float(parts[4]), float(parts[5]), float(parts[6])

            r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
            latitude = math.degrees(math.asin(z / r))
            longitude = math.degrees(math.atan2(y, x))

            # Parse timestamp and position/velocity vectors
            r_vec = [x, y, z]  # Position (km)
            v_vec = [vx, vy, vz]  # Velocity (km/s)

            # Convert timestamp to astropy time
            epoch = Time(parts[0], format='isot', scale='utc')

            # Create the orbit object with initial state vector (r, v)
            orbit = Orbit.from_vectors(Earth, r_vec * u.km, v_vec * u.km / u.s, epoch=epoch)
        except (ValueError, IndexError) as e:
            # Handle any malformed lines or conversion issues
            print(f"Error processing line: {line}. Error: {e}")
    return timestamp, latitude, longitude, orbit

################################################################################################
def parseOemFile(file_path):
    timestamps = []
    latitudes = []
    longitudes = []
    orbits = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()

            if not isStartsWithDate(line):
                continue

            parts = line.split()
            try:
                timestamp = datetime.strptime(parts[0], '%Y-%m-%dT%H:%M:%S.%f')
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                vx, vy, vz = float(parts[4]), float(parts[5]), float(parts[6])

                r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
                latitude = math.degrees(math.asin(z / r))
                longitude = math.degrees(math.atan2(y, x))

                # Parse timestamp and position/velocity vectors
                r_vec = [x, y, z]  # Position (km)
                v_vec = [vx, vy, vz]  # Velocity (km/s)

                # Convert timestamp to astropy time
                epoch = Time(parts[0], format='isot', scale='utc')

                # Create the orbit object with initial state vector (r, v)
                orbit = Orbit.from_vectors(Earth, r_vec * u.km, v_vec * u.km / u.s, epoch=epoch)

                timestamps.append(timestamp)
                latitudes.append(latitude)
                longitudes.append(longitude)
                orbits.append(orbit)
            except (ValueError, IndexError) as e:
                # Handle any malformed lines or conversion issues
                print(f"Error processing line: {line}. Error: {e}")
    return timestamps, latitudes, longitudes, orbits

################################################################################################
def propagate_orbit(orbit, start_date, days):
    """
    Propagates the orbit for the specified number of days into the future.
    Args:
    - orbit: Initial Orbit object.
    - start_date (datetime): Start date for propagation.
    - days (int): Number of days to propagate into the future.
    Returns:
    - times (list): List of astropy Time objects corresponding to future propagation times.
    - positions (list): List of spacecraft positions (r vectors) at each time.
    """
    # Define the start time and end time
    start_time = Time(start_date)
    epoch = orbit.epoch
    time_from_epoch_to_start = (start_time - epoch).to(u.s)
    num_steps = 100
    total_seconds = days * 24 * 3600
    time_step = total_seconds / num_steps * u.s 
    times = [time_from_epoch_to_start + i * time_step for i in range(num_steps)]
    positions = [orbit.propagate(time).r for time in times]  # r vectors at each time
    return times, positions

################################################################################################
def calculate_flyover(target_long, target_lat, orbit, start_date, days):
    """
    Calculates the spacecraft's flyover times, azimuth, and altitude over a given location.
    Args:
    - target_long: Target longitude in degrees.
    - target_lat: Target latitude in degrees.
    - orbit: Initial orbit object.
    - start_date: Start date for propagation.
    - days: Number of days to propagate into the future.
    Returns:
    - Dictionary with start time, end time, highest point time, azimuth, and altitude.
    """
    # Observer location (on Earth's surface)
    location = EarthLocation(lat=target_lat, lon=target_long)
    # Propagate the orbit
    times, positions = propagate_orbit(orbit, start_date, days)
    # Store the flyover details
    flyover_data = {
        'start_time': None,
        'end_time': None,
        'highest_time': None,
        'highest_altitude': -90,  # Lowest possible altitude
        'azimuth_at_highest': None
    }
    # Check the azimuth and altitude at each time step
    for i, (time, position) in enumerate(zip(times, positions)):
        # Convert position to SkyCoord object (in ECI coordinates)
        sat_coord = SkyCoord(x=position[0], y=position[1], z=position[2], representation_type='cartesian', frame='gcrs', obstime=time)
        # Convert satellite position to the AltAz frame for the observer
        altaz = sat_coord.transform_to(AltAz(obstime=time, location=location))
        altitude = altaz.alt.degree
        azimuth = altaz.az.degree
        # Check if satellite is above the horizon (altitude > 0)
        if altitude > 0 and flyover_data['start_time'] is None:
            flyover_data['start_time'] = time
        # Update end time and highest point
        if altitude > 0:
            flyover_data['end_time'] = time
            # Update highest point
            if altitude > flyover_data['highest_altitude']:
                flyover_data['highest_altitude'] = altitude
                flyover_data['highest_time'] = time
                flyover_data['azimuth_at_highest'] = azimuth
    return flyover_data

################################################################################################
def downloadZipFile(url, savePath='/temp/'):
    response = requests.get(url)

    if response.status_code == 200:
        with open(savePath, 'wb') as file:
            file.write(response.content)
            print(f'Save to {savePath}!')
    else:
        print(f'Failed to download {response.status_code}')

CSS_MAIN_URL = 'https://www.cmse.gov.cn/'
CSS_DOWNLOAD_URL = CSS_MAIN_URL + 'gfgg/zgkjzgdcs/'
CSS_OEM_ZIP_URL  = CSS_DOWNLOAD_URL + 'YYMM/W020241021391306489470.zip'
CSS_OEM_ZIP_XPATH_DIV = '//div[@class="TRS_Editor"]'
FILE_PATH = './temp'
################################################################################################
def downloadOEM(mainUrl=CSS_DOWNLOAD_URL):
    print('下载OEM数据...')
    with myNet.getFirefoxDriver() as driver:
        driver.set_page_load_timeout(123)
        driver.get(mainUrl)
        # WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, XPATH_DIV)))
        # divs = driver.find_elements(By.XPATH, XPATH_DIV)
        myNet.elementXPath(driver, 120, CSS_OEM_ZIP_XPATH_DIV)
        div = myNet.findElementByXPath(driver, CSS_OEM_ZIP_XPATH_DIV)
        href = div.get_attribute('href')
        if href:
            url = f'{mainUrl}{href}'
            filename = href.split('/')[0]
            savePath = f'{FILE_PATH}/{filename}'
            try:
                downloadZipFile(url, savePath)
            except Exception as e:
                print('下载OEM失败！')
                print('使用既存OEM数据...')
    return 

################################################################################################
def rv_to_tle(position, velocity):
    # Constants
    mu = 398600.4418  # Earth’s gravitational parameter in km^3/s^2
    # Convert position and velocity to numpy arrays
    r = np.array(position)  # Position vector (x, y, z) in km
    v = np.array(velocity)  # Velocity vector (vx, vy, vz) in km/s
    # Calculate the orbital parameters
    r_mag = np.linalg.norm(r)
    v_mag = np.linalg.norm(v)
    h = np.cross(r, v)  # Specific angular momentum
    h_mag = np.linalg.norm(h)
    # Calculate semi-major axis
    a = 1 / ((2 / r_mag) - (v_mag**2 / mu))
    # Calculate eccentricity
    e_vec = (np.cross(v, h) / mu) - (r / r_mag)
    e = np.linalg.norm(e_vec)
    # Calculate inclination
    i = np.arccos(h[2] / h_mag)
    # Calculate right ascension of the ascending node (RAAN)
    n = np.cross([0, 0, 1], h)
    n_mag = np.linalg.norm(n)
    if n_mag == 0:
        RAAN = 0
    else:
        RAAN = np.arctan2(n[1], n[0])
    # Calculate argument of perigee
    if e > 0:
        arg_of_perigee = np.arctan2(e_vec[2], np.dot(n, e_vec))
    else:
        arg_of_perigee = 0
    # Calculate true anomaly
    if e > 0:
        true_anomaly = np.arctan2(np.dot(r, v) / r_mag, 1 - (r_mag / a))
    else:
        true_anomaly = 0
    # Convert to degrees
    i = np.degrees(i)
    RAAN = np.degrees(RAAN)
    arg_of_perigee = np.degrees(arg_of_perigee)
    true_anomaly = np.degrees(true_anomaly)
    # Format TLE (example values for TLE fields)
    # 1 48274U 21035A   23235.00000000  .00026913  00000-0  31615-3 0  9991
    # 2 48274  41.4737 109.7400 0010191 216.7096 157.5884 15.61068452132289
    satellite_number = "48274"
    classification = "U"
    launch_year = "23235.00000000"
    launch_number = ".00026913"
    piece_of_launch = "A"
    # Mean motion calculation
    n = np.sqrt(mu / a**3)  # Mean motion in rad/s
    n = n * (86400 / (2 * np.pi))  # Convert to rev/day
    # TLE format
    line1 = f"{satellite_number}{classification} {launch_year}{launch_number}{piece_of_launch} {n:.8f} {i:.8f} {RAAN:.8f} {arg_of_perigee:.8f} {true_anomaly:.8f}"
    line2 = f"{satellite_number} {n:.8f} {e:.8f} {arg_of_perigee:.8f} {i:.8f} {RAAN:.8f}"
    return line1.strip(), line2.strip()

################################################################################################
def main():
    file_path = '/zang/Python/RocketLaunch/data/CSS_OEM_20240927000644_0001.dat'
    target_long, target_lat = 100.3, 40.96667  # 酒泉经纬度
    position = (7000, 0, 0)  # km
    velocity = (0, 7.12, 0)  # km/s
    tle_line1, tle_line2 = rv_to_tle(position, velocity)
    print(tle_line1)
    print(tle_line2)

    # start_date = '2024-10-01T00:00:00'
    # days = 30
    # timestamps, lats, longs, orbits = parseOemFile(file_path)
    # timestamp, lat, long, orbit = parseLastDataOemFile(file_path)
    # print(f'{str(timestamp) = }, {lat = }, {long = }')
    # print(f'{orbit = }')
    # flyover_data = calculate_flyover(target_long, target_lat, orbit, start_date, days)
    # print(f"Start Time: {flyover_data['start_time']}, "
    #     f"End Time: {flyover_data['end_time']}, "
    #     f"Highest Point Time: {flyover_data['highest_time']}, "
    #     f"Azimuth at Highest Point: {flyover_data['azimuth_at_highest']}, "
    #     f"Highest Altitude: {flyover_data['highest_altitude']} degrees")

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")