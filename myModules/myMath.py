from math import radians, cos, sin, asin, sqrt, atan2, degrees, pow

    # Earth radius in kilometers
EARTH_RADIUS = 6371.0; # kilo metres
# EARTH_RADIUS = 6371000; # metres
# EARTH_RADIUS = 6371.0
# EARTH_RADIUS = 6371.0

def extend_great_circle(lat, lon, bearing, distance):
    lat = radians(lat)
    lon = radians(lon)
    bearing = radians(bearing)
    new_lat = asin(sin(lat) * cos(distance / EARTH_RADIUS) + cos(lat) * sin(distance / EARTH_RADIUS) * cos(bearing))
    new_lon = lon + atan2(sin(bearing) * sin(distance / EARTH_RADIUS) * cos(lat), cos(distance / EARTH_RADIUS) - sin(lat) * sin(new_lat))
    new_lat = degrees(new_lat)
    new_lon = degrees(new_lon)
    return new_lat, new_lon

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    d_lon = lon2 - lon1
    x = sin(d_lon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(d_lon)
    initial_bearing = atan2(x, y)
    initial_bearing = degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360 - 90
    return bearing

# def extend_great_circle(lat, lon, bearing, distance):
#     lat = radians(lat)
#     lon = radians(lon)
#     bearing = radians(bearing)
#     new_lat = asin(sin(lat) * cos(distance / EARTH_RADIUS) + cos(lat) * sin(distance / EARTH_RADIUS) * cos(bearing))
#     new_lon = lon + atan2(sin(bearing) * sin(distance / EARTH_RADIUS) * cos(lat), cos(distance / EARTH_RADIUS) - sin(lat) * sin(new_lat))
#     new_lat = degrees(new_lat)
#     new_lon = degrees(new_lon)
#     return new_lat, new_lon

def getBearing(start_lat, start_lon, end_lat, end_lon):
    bearing = calculate_bearing(start_lat, start_lon, end_lat, end_lon)
    extension_distance = 100  # Distance in kilometers
    new_lat, new_lon = extend_great_circle(end_lat, end_lon, bearing, extension_distance)
    final_bearing = calculate_bearing(end_lat, end_lon, new_lat, new_lon)
    return new_lat, new_lon, bearing, final_bearing
          
################################################################################################
# angle is started from equator
def great_circle_angle(lat1, lon1, lat2, lon2):
    return great_circle_bearing(lat1, lon1, lat2, lon2) - 90

################################################################################################
def calculate_2d_angle(lon1, lat1, lon2, lat2): 
    # Calculate the differences 
    delta_x = lon2 - lon1
    delta_y = lat2 - lat1 
    
    # Calculate the angle in radians 
    angle_radians = atan2(delta_y, delta_x)
    
    # Convert the angle from radians to degrees
    angle_degrees = degrees(angle_radians)
    
    # Normalize the angle to the range [0, 360]
    angle_degrees = (angle_degrees + 360) % 360 - 90
    return angle_degrees

################################################################################################
# Formula: θ = atan2( sin Δλ ⋅ cos φ2 , cos φ1 ⋅ sin φ2 − sin φ1 ⋅ cos φ2 ⋅ cos Δλ )
# where	φ1,λ1 is the start point, φ2,λ2 the end point (Δλ is the difference in longitude)
# θ is started from North
def great_circle_bearing(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to radians
    φ1, λ1, φ2, λ2 = map(radians, [lat1, lon1, lat2, lon2])
    y = sin(λ2 - λ1) * cos(φ2)
    x = cos(φ1) * sin(φ2) - sin(φ1) * cos(φ2) * cos(λ2 - λ1)
    θ = atan2(y, x)
    bearing = (degrees(θ) + 360) % 360 # in degrees
    return bearing

################################################################################################
# Haversine: a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
#   formula: c = 2 ⋅ atan2( √a, √(1−a) )
#            d = EARTH_RADIUS ⋅ c
# where	φ is latitude, λ is longitude, EARTH_RADIUS is earth's radius (mean radius = 6,371km);
# note that angles need to be in radians to pass to trig functions!
def great_circle_distance(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    φ1, λ1, φ2, λ2 = map(radians, [lat1, lon1, lat2, lon2])
    Δφ = φ2 - φ1
    Δλ = λ2 - λ1

    a = sin(Δφ / 2) * sin(Δφ / 2) + cos(φ1) * cos(φ2) * sin(Δλ / 2) * sin(Δλ / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = EARTH_RADIUS * 1000 * c # in metres
    return d

################################################################################################
def great_circle_point(lat1, lon1, lat2, lon2, distance=1000000, distanceRatio=1.1, fromSea=False):
    bearing = great_circle_bearing(lat1, lon1, lat2, lon2)
    d = great_circle_distance(lat1, lon1, lat2, lon2)
    if fromSea:
        d += 500000
    else:
        d = max(distance, d) if distance != None else d * distanceRatio
    point = great_circle_point_by_distance(lat1, lon1, bearing, d)
    return point

################################################################################################
# Formula:	φ2 = asin( sin φ1 ⋅ cos δ + cos φ1 ⋅ sin δ ⋅ cos θ )
#           λ2 = λ1 + atan2( sin θ ⋅ sin δ ⋅ cos φ1, cos δ − sin φ1 ⋅ sin φ2 )
# where	φ is latitude, λ is longitude, θ is the bearing (clockwise from north), δ is the angular distance d/EARTH_RADIUS; 
# d being the distance travelled, EARTH_RADIUS the earth's radius
def great_circle_point_by_distance(lat1, lon1, bearing, distance):
    φ1, λ1 = map(radians, [lat1, lon1])
    δ = distance / EARTH_RADIUS / 1000
    θ = radians(bearing)
    φ2 = asin(sin(φ1) * cos(δ) + cos(φ1) * sin(δ) * cos(θ))
    λ2 = λ1 + atan2(sin(θ) * sin(δ) * cos(φ1), cos(δ) - sin(φ1) * sin(φ2))
    return [degrees(λ2), degrees(φ2)]

# Calculate the great circle distance between two points
# on the earth (specified in decimal degrees)
# calculate distance between points
################################################################################################
def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km


