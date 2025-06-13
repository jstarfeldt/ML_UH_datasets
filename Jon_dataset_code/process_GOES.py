import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rxr
import glob
import datetime
from pyproj import Proj, Transformer
import os
from scipy import interpolate
import multiprocessing
import argparse
import subprocess


"""
Export coordinates for each urban area
KEY: [utm zone, T/F Northern Hemisphere]
"""
proj_zone = {
    'DMV':[18, True], 'NYC':[18, True], 'Phoenix':[12, True], 'Miami':[17, True], 'Chicago':[16, True], 'Denver':[13, True],
    'Seattle':[10, True], 'San_Francisco':[10, True], 'Los_Angeles':[11, True], 'Atlanta':[16, True], 'Toronto':[17, True],
    'Mexico_City':[14, True], 'Las_Vegas':[11, True], 'Salt_Lake_City':[12, True], 'Dallas':[14, True], 'Houston':[15, True],
    'New_Orleans':[15, True], 'St_Louis':[15, True], 'Minneapolis':[15, True], 'Jacksonville':[17, True], 'Charlotte':[17, True],
    'Philadelphia':[18, True], 'San_Diego':[11, True], 'San_Juan':[19, True], 'Montreal':[18, True], 'Guadalajara':[13, True],
    'Monterrey':[14, True], 'Cancun':[16, True], 'Billings':[12, True], 'Guatemala_City':[15, True], 'San_Jose':[16, True],
    'Havana':[17, True], 'Santo_Domingo':[19, True], 'Tegucigalpa':[16, True], 'Managua':[16, True], 'Panama_City':[17, True],
    'Bogota':[18, True], 'Lima':[18, False], 'Quito':[17, True], 'Santiago':[19, False], 'Buenos_Aires':[21, False],
    'Sao_Paulo':[23, False], 'Manaus':[20, False], 'Punta_Arenas':[19, False],
    'La_Paz':[19, False], 'Montevideo':[21, False], 'Brasilia':[22, False], 'Caracas':[19, True]
}


"""
Processing of individual .tif files.

Performs a variety of tasks on the data to make it more easy to read and understand.

Attributes:
    tif (str): Path where tif file is located.
    time (str): Date and time of when the data was collected format YYYY-MM-DDThh:mm:ssZ.
    latlon_pts (float array): (45,45,2) Array of (longitude, latitude) points at each point on the utm grid.
    fname (str): Full path of where to store the file, including a filename ending in '.nc'.
    coord_bounds (tuple or list, optional): Coordinate bounds if you wish to filter the data by location. Order should be
                                    (longitude minimum, longitude maximum, latitude minimum, latitude maximum).
"""
def process_GOES_tif(tif, time, latlon_pts, fname, coord_bounds=None):
    #########################################################################################################
    # Open file and rename variables
    dsG = rxr.open_rasterio(tif)
    geotiff_ds = dsG.to_dataset('band')
    geotiff_ds = geotiff_ds.rename({1:'GOES_C13_LWIR', 2:'GOES_C14_LWIR',
                                      3:'GOES_C15_LWIR', 4:'GOES_C16_LWIR'})
    geotiff_ds = geotiff_ds.assign_coords({'datetime':time})

    #########################################################################################################
    # Process microwave data
    """
    Returns the value rounded up or down to the nearest 0.25.

    Attributes:
        n (float): latitude or longitude coordinate.
        above (boolean): True for round up, False for round down.
    """
    def get_next_latlon_coord(n, above=True):
        if above:
            return np.ceil(n*4)/4
        else:
            return np.floor(n*4)/4

    """
    Returns an integer as a str, adding a zero in front if it is a single digit.

    Attributes:
        num (int): Integer to turn into a string.
    """
    def stringify(num):
        if num >= 0 and num < 10:
            return f'0{num}'
        else:
            return str(num)

    
    longitude = latlon_pts[22,22,0]
    
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    utc_dt = datetime.datetime.strptime(time, date_format)
    local_dt = utc_dt + datetime.timedelta(hours=(longitude/360)*24)
    date_str = f'{local_dt.year}{stringify(local_dt.month)}{stringify(local_dt.day)}'

    """
    Adjusts a datetime in UTC to local time based on how far it is from the Prime Meridian and
    calculates an index 0-95 of which 15-minute interval the time is in a day.

    Attributes:
        longitude (float): Longitude value.
        dt (python datetime object): Datetime with a time in UTC.
    """
    def time_adjust(longitude, dt=utc_dt):
        local_dt = dt + datetime.timedelta(hours=(longitude/360)*24) # Adjusting for global local time
        time_index = local_dt.hour*4 + round(local_dt.minute/15+local_dt.second/3600) # Used in selection of datetime index from mw file (every 15 minutes)
        return time_index

    func = np.vectorize(time_adjust)
    time_indices = func(latlon_pts[:,:,0])
    
    dsMW = xr.open_dataset(f'/home/jonstar/scratch.gcurbanheat/mw_data/MW_LST_DTC_{date_str}_x1y.h5', 
                          engine='h5netcdf')
    dsMW = dsMW.assign_coords(
                datetime=("phony_dim_0", pd.date_range(start=date_str, periods=96, freq="15min")),
                longitude=("phony_dim_1", np.arange(-180,180,0.25)),
                latitude=("phony_dim_2", np.arange(-60,90,0.25)[::-1]))
    #dsMW = dsMW.rename({'phony_dim_0':'datetime', 'phony_dim_1':'longitude', 'phony_dim_2':'latitude'})

    max_lon_index = np.where(dsMW['longitude'] == get_next_latlon_coord(np.max(latlon_pts[:,:,0]), True))[0][0]
    min_lon_index = np.where(dsMW['longitude'] == get_next_latlon_coord(np.min(latlon_pts[:,:,0]), False))[0][0]
    max_lat_index = np.where(dsMW['latitude'] == get_next_latlon_coord(np.max(latlon_pts[:,:,1]), True))[0][0]
    min_lat_index = np.where(dsMW['latitude'] == get_next_latlon_coord(np.min(latlon_pts[:,:,1]), False))[0][0]

    # Create microwave array for specific area
    # Remember: latitude decreases with index
    mw_clipped = dsMW['TB37V_LST_DTC'][np.min(time_indices):np.max(time_indices)+1,min_lon_index:max_lon_index+1,max_lat_index:min_lat_index+1]

    y, x = np.meshgrid(mw_clipped['latitude'], mw_clipped['longitude'])
    mw_latlons = np.stack((x,y)).T.reshape(-1,2)

    interpolated_arrays = []
    for arr in mw_clipped:
        mw_interpolated = interpolate.griddata(mw_latlons, arr.T.values.reshape(-1)/50, latlon_pts, method='nearest')
        interpolated_arrays.append(mw_interpolated)
    interpolated_array = np.stack(interpolated_arrays) # Interpolated microwave values from each time index n of shape (n,45,45)
    interpolated_indices = time_indices-np.min(time_indices) # Array of shape (45,45) that select time indices from the value array
    
    # Index the first dimension of the value array
    mw_interpolated = interpolated_array[interpolated_indices, np.arange(45)[:, None], np.arange(45)]

    geotiff_ds['microwave_LST'] = (('y','x'), mw_interpolated)

    # Flip coordinates so latitude increases with index
    geotiff_ds = geotiff_ds.reindex(y=geotiff_ds.y[::-1])

    #########################################################################################################
    # Optional filtering by lat/lon
    if coord_bounds:
        geotiff_ds = geotiff_ds.sel(longitude=slice(coord_bounds[0], coord_bounds[1])).sel(latitude=slice(coord_bounds[3], coord_bounds[2]))

    #########################################################################################################
    geotiff_ds.to_netcdf(fname)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='GOES_download',
                    description='Fast downloading for GOES images from GEE')
    parser.add_argument('--city', help='String of city from list of valid cities to make data for')
    parser.add_argument('--cpus', nargs='?', const=30, help='Number of CPU cores to run in parallel')
    args = parser.parse_args()
    
    # Pull points to make data for a specific city (look above for options)
    #city = 'DMV'
    city = args.city
    city_zone = proj_zone[city]
    utm_proj = Proj(proj="utm", zone=city_zone[0], datum="WGS84", northern=city_zone[1])

    # Ensure there is a GOES directory made for the city and set it as the prefix to the filename
    processed_dir = f'/home/jonstar/urban_heat_dataset/{city}/processed_GOES'
    subprocess.call(['mkdir', '-p', processed_dir])
   
    if city in ['Seattle', 'San_Francisco', 'Los_Angeles', 'San_Diego', 'Phoenix', 'Las_Vegas', 'Salt_Lake_City']:
        g_times = pd.read_csv('/home/jonstar/urban_heat_dataset/GOES_West_times.csv').value
    else:
        g_times = pd.read_csv('/home/jonstar/urban_heat_dataset/GOES_East_times.csv').value

    def sort_func_GOES(s):
        return int(s.split('image_')[1].split('.tif')[0])

    GOES_tif_list = glob.glob(f'/home/jonstar/urban_heat_dataset/{city}/GOES/*.tif')
    GOES_tif_list = sorted(GOES_tif_list, key=sort_func_GOES)

    dsG = rxr.open_rasterio(GOES_tif_list[0])
    geotiff_dsG = dsG.to_dataset('band')

    y, x = np.meshgrid(geotiff_dsG['y'], geotiff_dsG['x'])
    utm_coords = np.stack((x,y)).T.reshape(-1,2) # Get list of x, y coordinates following coordinate structure (x changes first)

    def stacked_to_latlon(pt):
        return utm_proj(pt[0], pt[1], inverse=True)

    latlon_pts_2km_1d = np.array(list(map(stacked_to_latlon, utm_coords)))
    latlon_pts_2km = latlon_pts_2km_1d.reshape((45,45,2))

    file_index = np.arange(len(GOES_tif_list))
    processed_dir = f'/home/jonstar/urban_heat_dataset/{city}/processed_GOES'
    inputs = [[GOES_tif_list[i], datetime.datetime.fromtimestamp(g_times[i]/1000, datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'), latlon_pts_2km, f'{processed_dir}/{GOES_tif_list[i].split('/')[-1].split('.')[0]}.nc'] for i in file_index]

    print('Starting multiprocessing')

    start = datetime.datetime.now()
    nCPUs = int(args.cpus)
    pool = multiprocessing.Pool(nCPUs)
    pool.starmap(process_GOES_tif, inputs)
    pool.close()
    pool.join()

    time_diff = datetime.datetime.now() - start
    print(f'Total time: {time_diff.total_seconds()} seconds')
