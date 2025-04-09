import ee
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import multiprocessing
from data import getResultGOES_new
import argparse

ee.Initialize(project='ee-jonstar', opt_url='https://earthengine-highvolume.googleapis.com')
#ee.Initialize(project='ee-my-mips', opt_url='https://earthengine-highvolume.googleapis.com')


edt = pytz.timezone('US/Eastern')

"""
Points of interest for each urban area.
KEY:
First and second points = Landsat
Third point = Sentinel
If the second point is zero, then there is only one Landsat image needed to cover that city and its surrounding area
The third point is defined near the city center. A circular region of 200 km is created around the third point
to filter Sentinel-1 images, ensuring all of the necessary images will be present.
"""
city_points = {
    'DMV':[ee.Geometry.Point(-76.6122, 39.2904), 0, ee.Geometry.Point(-76.863, 39.063)],
    'NYC':[ee.Geometry.Point(-73.274, 40.688), 0, ee.Geometry.Point(-73.979, 40.751)],
    'Atlanta':[ee.Geometry.Point(-84.039, 34.155), ee.Geometry.Point(-84.485, 33.641), ee.Geometry.Point(-84.38, 33.748)],
    'Miami':[ee.Geometry.Point(-80.267, 25.818), 0, ee.Geometry.Point(-80.267, 25.818)],
    'Chicago':[ee.Geometry.Point(-88.037, 41.826), 0, ee.Geometry.Point(-87.74, 41.78)],
    'Phoenix':[ee.Geometry.Point(-112.02, 33.46), 0, ee.Geometry.Point(-112.064, 33.487)],
    'Denver':[ee.Geometry.Point(-104.6, 39.6696), 0, ee.Geometry.Point(-104.985, 39.729)],
    'Seattle':[ee.Geometry.Point(-121.952, 47.546), 0, ee.Geometry.Point(-122.322, 47.59)],
    'San_Francisco':[ee.Geometry.Point(-122.179, 37.745), 0, ee.Geometry.Point(-122.365, 37.745)],
    'Los_Angeles':[ee.Geometry.Point(-118.365, 34.279), ee.Geometry.Point(-118.744, 33.383), ee.Geometry.Point(-122.365, 37.745)],
    'Toronto':[ee.Geometry.Point(-80.273, 43.289), ee.Geometry.Point(-79.609, 44.187), ee.Geometry.Point(-79.46, 43.616)],
    'Mexico_City':[ee.Geometry.Point(-99.101, 19.012), ee.Geometry.Point(-99.187, 20.084), ee.Geometry.Point(-99.129, 19.422)],
    'Las_Vegas':[ee.Geometry.Point(-115.162, 36.154), 0, ee.Geometry.Point(-115.161, 36.154)],
    'Salt_Lake_City':[ee.Geometry.Point(-111.896, 40.752), ee.Geometry.Point(-111.57, 41.37), ee.Geometry.Point(-111.896, 40.752)],
    'Dallas':[ee.Geometry.Point(-96.858, 32.789), 0, ee.Geometry.Point(-96.968, 32.794)],
    'Houston':[ee.Geometry.Point(-94.816, 30.034), ee.Geometry.Point(-95.356, 29.399), ee.Geometry.Point(-95.376, 29.758)],
    'New_Orleans':[ee.Geometry.Point(-90.102, 29.947), 0, ee.Geometry.Point(-90.102, 29.947)],
    'St_Louis':[ee.Geometry.Point(-90.505, 38.644), 0, ee.Geometry.Point(-90.205, 38.624)],
    'Minneapolis':[ee.Geometry.Point(-93.248, 44.969), 0, ee.Geometry.Point(-93.248, 44.969)],
    'Jacksonville':[ee.Geometry.Point(-81.357, 30.292), 0, ee.Geometry.Point(-81.651, 30.327)],
    'Charlotte':[ee.Geometry.Point(-80.797, 35.028), ee.Geometry.Point(-80.573, 35.63), ee.Geometry.Point(-80.842, 35.218)],
    'Philadelphia':[ee.Geometry.Point(-75.133, 39.938), 0, ee.Geometry.Point(-75.154, 39.939)],
    'San_Diego':[ee.Geometry.Point(-117.088, 32.647), 0, ee.Geometry.Point(-117.093, 32.578)],
    'San_Juan':[ee.Geometry.Point(-66.157, 18.392), 0, ee.Geometry.Point(-66.066, 18.407)],
    'Montreal':[ee.Geometry.Point(-73.589, 45.523), 0, ee.Geometry.Point(-73.59, 45.52)],
    'Guadalajara':[ee.Geometry.Point(-103.35, 20.663), 0, ee.Geometry.Point(-103.35, 20.663)],
    'Monterrey':[ee.Geometry.Point(-100.17, 25.897), 0, ee.Geometry.Point(-100.318, 25.711)],
    'Cancun':[ee.Geometry.Point(-86.592, 21.402), ee.Geometry.Point(-86.725, 20.709), ee.Geometry.Point(-86.85, 21.161)],
    'Billings':[ee.Geometry.Point(-108.5, 45.78), 0, ee.Geometry.Point(-108.504, 45.781)],
    'Guatemala_City':[ee.Geometry.Point(-90.527, 14.623), 0, ee.Geometry.Point(-90.527, 14.623)],
    'San_Jose':[ee.Geometry.Point(-84.082, 9.937), 0, ee.Geometry.Point(-84.082, 9.937)],
    'Havana':[ee.Geometry.Point(-82.36, 23.128), 0, ee.Geometry.Point(-82.36, 23.128)],
    'Santo_Domingo':[ee.Geometry.Point(-69.822, 18.681), 0, ee.Geometry.Point(-69.932, 18.468)],
    'Tegucigalpa':[ee.Geometry.Point(-87.206, 14.171), 0, ee.Geometry.Point(-87.197, 14.057)],
    'Managua':[ee.Geometry.Point(-86.269, 12.017), ee.Geometry.Point(-86.145, 12.349), ee.Geometry.Point(-86.239, 12.097)],
    'Panama_City':[ee.Geometry.Point(-79.522, 8.98), 0, ee.Geometry.Point(-79.522, 8.98)],
    'Bogota':[ee.Geometry.Point(-74.074, 4.697), 0, ee.Geometry.Point(-74.074, 4.697)],
    'Lima':[ee.Geometry.Point(-76.887, -11.835), ee.Geometry.Point(-76.99, -12.383), ee.Geometry.Point(-77.065, -12.066)],
    'Quito':[ee.Geometry.Point(-78.507, -.232), 0, ee.Geometry.Point(-78.507, -0.232)],
    'Santiago':[ee.Geometry.Point(-70.667, -33.46), 0, ee.Geometry.Point(-70.667, -33.46)],
    'Buenos_Aires':[ee.Geometry.Point(-58.543, -34.621), 0, ee.Geometry.Point(-58.458, -34.666)],
    'Sao_Paulo':[ee.Geometry.Point(-46.644, -23.564), 0, ee.Geometry.Point(-46.644, -23.564)],
    'Manaus':[ee.Geometry.Point(-60.037, -3.089), 0, ee.Geometry.Point(-60.037, -3.089)],
    'Punta_Arenas':[ee.Geometry.Point(-70.184, -53.342), 0, ee.Geometry.Point(-70.909, -53.157)],
    'La_Paz':[ee.Geometry.Point(-67.885, -17.004), ee.Geometry.Point(-67.965, -16.125), ee.Geometry.Point(-68.143, -16.522)],
    'Montevideo':[ee.Geometry.Point(-56.175, -34.902), 0, ee.Geometry.Point(-56.175, -34.902)],
    'Brasilia':[ee.Geometry.Point(-47.890, -15.799), 0, ee.Geometry.Point(-47.89, -15.799)],
    'Caracas':[ee.Geometry.Point(-66.898, 10.475), 0, ee.Geometry.Point(-66.907, 10.474)]
}

"""
Export coordinates for each urban area
KEY: [utm zone, boolean T/F for northern/southern hemisphere, utm x, utm y]
"""
export_coords = {
    'DMV':[18, True, 292000, 4372200],
    'NYC':[18, True, 562680, 4550000],
    'Phoenix':[12, True, 350000, 3749000],
    'Miami':[17, True, 503991, 2915332],
    'Chicago':[16, True, 386195, 4680677],
    'Denver':[13, True, 466349, 4442816],
    'Seattle':[10, True, 504628, 5311856],
    'San_Francisco':[10, True, 541523, 4206919],
    'Los_Angeles':[11, True, 352871, 3803787],
    'Atlanta':[16, True, 703143, 3787639],
    'Toronto':[17, True, 566749, 4867878],
    'Mexico_City':[14, True, 426738, 2202781],
    'Las_Vegas':[11, True, 618776, 4038562],
    'Salt_Lake_City':[12, True, 387959, 4539501],
    'Dallas':[14, True, 639754, 3678675],
    'Houston':[15, True, 221804, 3334492],
    'New_Orleans':[15, True, 717043, 3335222],
    'St_Louis':[15, True, 675752, 4320402],
    'Minneapolis':[15, True, 433510, 5031071],
    'Jacksonville':[17, True, 421321, 3375918],
    'Charlotte':[17, True, 463969, 3944648],
    'Philadelphia':[18, True, 445906, 4467022],
    'San_Diego':[11, True, 468102, 3666860],
    'San_Juan':[19, True, 732591, 2098412],
    'Montreal':[18, True, 557269, 5097647],
    'Guadalajara':[13, True, 621576, 2326245],
    'Monterrey':[14, True, 318956, 2885247],
    'Cancun':[16, True, 491502, 2369076],
    'Billings':[12, True, 655301, 5109344],
    'Guatemala_City':[15, True, 711929, 1659823],
    'San_Jose':[16, True, 772982, 1148166],
    'Havana':[17, 310663, True, 2566532],
    'Santo_Domingo':[19, True, 354586, 2108039],
    'Tegucigalpa':[16, True, 401921, 1598242],
    'Managua':[16, True, 524987, 1386278],
    'Panama_City':[17, True, 610881, 1043658],
    'Bogota':[18, True, 546553, 562185],
    'Lima':[18, False, 262348, 8709133],
    'Quito':[17, True, 730387, 29863],
    'Santiago':[19, False, 288729, 6352433],
    'Buenos_Aires':[21, 326030, 6204959],
    'Sao_Paulo':[23, False, 294104, 7446208],
    'Manaus':[20, False, 762402, 9705737],
    'Punta_Arenas':[19, False, 353001, 4162220],
    'La_Paz':[19, False, 548109, 8213756],
    'Montevideo':[21, False, 545458, 6223320],
    'Brasilia':[22, False, 799612, 8288848],
    'Caracas':[19, True, 686519, 1174917]
}


"""
Convert datetimes from your current timezone to a desired timezone.

dt (datetime): python datetime object
to_timezone (pytz timezone): timezone to convert to
local_timezone (pytz timezone): the timezone you are currently in. Python uses your computer's internal clock, so whatever your computer is on.
"""
def toTimezone(dt, to_timezone, local_timezone=edt):
    return local_timezone.normalize(local_timezone.localize(dt)).astimezone(to_timezone)


"""
Converts unix timestamp to YearMonthDayHourMinute date string.

timestamp (int): unix timetamp in microseconds
"""
def GOES_time_to_str(timestamp):
    return toTimezone(datetime.fromtimestamp(timestamp/1000), pytz.utc).strftime('%Y%m%d%H%M')


"""
Applies scale and offset factors for GOES imagery. All scale and offset values were taken straight from GEE to save compute.

image (ee.Image): GOES image to scale and offset.
"""
def scale_and_offset_GOES(image):
    #reflectances = image.select(['CMI_C01', 'CMI_C02', 'CMI_C03', 'CMI_C05', 'CMI_C06']).multiply(0.0002442)
    weight = 0.039316241
    bias = 173.14999
    brightness_temps = image.select(['CMI_C13', 'CMI_C14', 'CMI_C15', 'CMI_C16']).multiply(weight).add(bias)
    
    #return reflectances.addBands(srcImg=brightness_temps, names=['CMI_C14', 'CMI_C15'])
    return brightness_temps


"""
Preprocessing function for GOES images.

image (ee.Image): GOES image to process.
"""
def process_GOES(image):
    ######################################
    # GOES portion

    # Scaling and offset
    #image2 = ee.Image(feature.get('matched_img'))
    GOES_image = scale_and_offset_GOES(image)

    ######################################
    # Timestamp portion
    
    # Function to get time from GOES image\    
    def get_GOES_time(f):
        GOES_time = ee.Number(image.get('system:time_start'))       
        return f.set('timestamp', GOES_time)

    # Add timestamp back in
    #landsat_image = get_GOES_time(landsat_image)
    GOES_image = get_GOES_time(GOES_image)

    return GOES_image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='GOES_download',
                    description='Fast downloading for GOES images from GEE')
    parser.add_argument('--city', help='String of city from list of valid cities to make data for')
    parser.add_argument('--n', nargs='?', const=105120, help='Number of files to create')
    parser.add_argument('--startFile', nargs='?', const=0, help='File index to start from')
    parser.add_argument('--cpus', nargs='?', const=100, help='Number of CPU cores to run in parallel')
    args = parser.parse_args()
    
    # Pull points to make data for a specific city (look above for options)
    #city = 'DMV'
    city = args.city
    points = city_points[city]
    city_export = export_coords[city]

    # Initialize GOES ImageCollection and process the images
    GOES = ee.ImageCollection("NOAA/GOES/16/MCMIPF").filterDate('2022-01-01', '2024-01-01')
    processed = GOES.map(process_GOES)

    # Set variable for timestamps of GOES images
    g_times = pd.read_csv('/home/jonstar/urban_heat_dataset/GOES_times.csv').value
    #g_times = pd.read_csv('/Users/jonstar/Documents/heat_data/GOES_DMV/GOES_times_DMV.csv').value

    num = int(args.n)
    start = int(args.startFile)
    if num > 105120: # Largest number of files is length of processed list
        num = processed.size().getInfo()
    img_list = processed.toList(num, start)
    #file_prefix = f'/Users/jonstar/Documents/heat_data'
    if start < 30000:
        file_prefix = f'/home/jonstar/urban_heat_dataset/{city}/GOES'
    else:
        file_prefix = f'/home/jonstar/urban_heat_dataset/{city}/GOES2'

    indexes = np.arange(num)
    func = np.vectorize(GOES_time_to_str)
    time_strs = func(g_times[start:start+num])

    if city_export[1]:
        crs_prefix = '326' # Northern hemisphere
    else:
        crs_prefix = '327' # Southern hemisphere

    crs = f'EPSG:{crs_prefix}{city_export[0]}'
    point = ee.Geometry.Point([city_export[2]+30*2999/2,city_export[3]-30*2999/2], crs)
    region = point.buffer(distance=44000, proj=crs).bounds(proj=crs)

    inputs = [[ee.Image(img_list.get(int(i))), region, crs, f'{file_prefix}/GOES_image_{time_str}.tif'] for i, time_str in zip(indexes,time_strs)]

    print('Starting multiprocessing')

    nCPUs = int(args.cpus)
    pool = multiprocessing.Pool(nCPUs)
    pool.starmap(getResultGOES_new, inputs)
    pool.close()
    pool.join()
