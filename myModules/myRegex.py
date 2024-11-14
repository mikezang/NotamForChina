from re import compile, split, match, VERBOSE, IGNORECASE

def match_notam_coordinates(text):
    """
    Matches various coordinate formats commonly found in NOTAMs.
    Supports:
    - Compact degrees and minutes (e.g., 'N1234E12345')
    - Degrees, minutes, seconds (e.g., '174800N1152300E', '174800.00N1152300.00E')
    - Degrees with decimal minutes (e.g., '17.48N115.23E', '1744.48N11533.23E')
    - Degrees, minutes, with hyphen separators (e.g., '37-42.4N120-10.8E', '18-18.60N118-09.46E')
    - Degrees, minutes, and seconds with hyphen separators (e.g., '37-42-46N120-10-98E')
    :param text: The text containing coordinates.
    :return: A list of matched coordinates.
    """
    pattern = compile(r'''
        (?<!\d)  # Ensure the coordinate is not preceded by a number
        (?:
            # 1. Compact Degrees and Minutes (e.g., 'N1234E12345')
            (?P<compact_deg_min>[NS]\d{4,5}[EW]\d{5,6}) |
            # 2. Degrees, Minutes, and Seconds (e.g., '174800N1152300E')
            (?P<deg_min_sec>\d{4,6}(?:\.\d+)?[NS]\d{5,7}(?:\.\d+)?[EW]) |
            # 3. Degrees with Decimal Minutes (e.g., '17.48N115.23E', '1744.48N11533.23E')
            (?P<deg_dec_min>\d{1,3}\.\d+[NS]\d{1,3}\.\d+[EW]) |
            # 4. Hyphen-separated Degrees, Minutes (e.g., '37-42.4N120-10.8E', '18-18.60N118-09.46E')
            (?P<deg_min_hyphen>\d{1,3}-\d{1,2}(?:\.\d+)?[NS]\d{1,3}-\d{1,2}(?:\.\d+)?[EW]) |
            # 5. Hyphen-separated Degrees, Minutes, and Seconds (e.g., '37-42-46N120-10-98E')
            (?P<deg_min_sec_hyphen>\d{1,3}-\d{1,2}-\d{1,2}(?:\.\d+)?[NS]\d{1,3}-\d{1,2}-\d{1,2}(?:\.\d+)?[EW])
        )
    ''', VERBOSE | IGNORECASE)
    # Find all matches in the input text
    matches = pattern.findall(text)
    # Flatten and filter out empty matches from the tuple results
    coordinates = [match for group in matches for match in group if match]
    return coordinates

def convert_coordinate_to_float(coord: str) -> tuple:
    """
    Convert a coordinate in various formats to decimal degrees (float).
    Supports multiple formats including:
        "N1234E1234",
        "N1234E12345",
        "N123456E123456",
        "N123456E1234560",
        "174800.0N1152300.0E",
        "174800.00N1152300.00E",
        "1748N1523E",
        "174800N152300E",
        "174800N1152300E",
        "17.48N115.23E",
        "1744.48N11533.23E",
        "37-42-46N120-10-98E"
        "37-42.4N120-10.8E",
        "18-18.60N118-09.46E",
    :param coord: Coordinate string containing both latitude and longitude.
    :return: Tuple with (latitude, longitude) in decimal degrees.
    """
    # Regex pattern to match latitude and longitude components
    pattern = compile(r'([NS])(\d{2,7}(?:\.\d+)?)([NS])|([EW])(\d{2,7}(?:\.\d+)?)([EW])')
    matches = pattern.findall(coord.upper())
    latitude, longitude = None, None
    for match in matches:
        if match[0]:  # This indicates the first part is a latitude (e.g., N1234 or 1234N)
            coord_part = match[0]
            direction = match[1]
        else:  # This indicates the second part is a longitude (e.g., E4321 or 4321E)
            coord_part = match[3]
            direction = match[2]
        decimal_degrees = _convert_single_coordinate(coord_part, direction)
        # Assign to latitude or longitude based on the direction
        if direction in ['N', 'S']:
            latitude = decimal_degrees
        elif direction in ['E', 'W']:
            longitude = decimal_degrees
    return latitude, longitude

def _convert_single_coordinate(coord_part: str, direction: str) -> float:
    """
    Convert a coordinate part to decimal degrees.
    :param coord_part: Numeric part of the coordinate.
    :param direction: Direction (N/S/E/W).
    :return: Decimal degrees as a float.
    """
    # Handle degrees-minutes-seconds logic
    if len(coord_part) == 6:
        degrees = float(coord_part[:2])
        minutes = float(coord_part[2:4])
        seconds = float(coord_part[4:])
    elif len(coord_part) == 7:
        degrees = float(coord_part[:3])
        minutes = float(coord_part[3:5])
        seconds = float(coord_part[5:])
    else:
        # For compact coordinates (2 or 3 degrees)
        degrees = float(coord_part[:2])
        minutes = float(coord_part[2:4]) if len(coord_part) > 2 else 0
        seconds = float(coord_part[4:]) if len(coord_part) > 4 else 0
    # Convert to decimal degrees
    decimal_degrees = degrees + minutes / 60 + seconds / 3600
    # Adjust for direction: S and W should result in negative values
    if direction in ['S', 'W']:
        decimal_degrees = -abs(decimal_degrees)
    return decimal_degrees

# Example Usage
coordinates = [
    "N1234E12345",
    "174800.00N1152300.00E",
    "174800N1152300E",
    "174800N152300E",
    "1748N1523E",
    "17.48N115.23E",
    "1744.48N11533.23E",
    "37-42.4N120-10.8E",
    "18-18.60N118-09.46E",
    "37-42-46N120-10-98E"
]
for coord in coordinates:
    print(f"{coord}: {convert_coordinate_to_float(coord)}")
