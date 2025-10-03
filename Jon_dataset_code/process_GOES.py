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

    # Calculate adjusted datetimes for the left and right edges of the image.
    # If the datetimes are across two days, values from two mw LST files need to be used.
    min_longitude = np.min(latlon_pts[:,:,0])
    max_longitude = np.max(latlon_pts[:,:,0])

    date_format = "%Y-%m-%dT%H:%M:%SZ"
    utc_dt = datetime.datetime.strptime(time, date_format)
    local_dt1 = utc_dt + datetime.timedelta(hours=(min_longitude/360)*24)
    date_str1 = f'{local_dt1.year}{stringify(local_dt1.month)}{stringify(local_dt1.day)}'
    local_dt2 = utc_dt + datetime.timedelta(hours=(max_longitude/360)*24)
    date_str2 = f'{local_dt2.year}{stringify(local_dt2.month)}{stringify(local_dt2.day)}'


    """
    Adjusts a datetime in UTC to local time based on how far it is from the Prime Meridian and
    calculates an index 0-96 of which 15-minute interval the time is in a day.

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

    # Accounting for rounding of values to timestep of following day
    if np.sum(time_indices<96) < 2025: 
        local_dt2 = local_dt2 + datetime.timedelta(days=1)
        date_str2 = f'{local_dt2.year}{stringify(local_dt2.month)}{stringify(local_dt2.day)}'

    # Accounting for files we do not have currently
    if date_str1 == '20211231' or date_str2 == '20211231' or date_str1 == '20220322' or date_str2 == '20220322':
        print('date string identifited')
        return

    if date_str1 != date_str2: # When data spans two days (two different files)
        dsMW = xr.open_dataset(f'/scratch/zt1/project/gcurbanheat/user/jonstar/mw_data/MW_LST_DTC_{date_str1}_x1y.h5', engine='h5netcdf')
        dsMW = dsMW.assign_coords(
            datetime=("phony_dim_0", pd.date_range(start=date_str1, periods=96, freq="15min")),
            longitude=("phony_dim_1", np.arange(-180,180,0.25)),
            latitude=("phony_dim_2", np.arange(-60,90,0.25)[::-1]))
 
        dsMW2 = xr.open_dataset(f'/scratch/zt1/project/gcurbanheat/user/jonstar/mw_data/MW_LST_DTC_{date_str2}_x1y.h5', engine='h5netcdf')
        dsMW2 = dsMW.assign_coords(
            datetime=("phony_dim_0", pd.date_range(start=date_str2, periods=96, freq="15min")),
            longitude=("phony_dim_1", np.arange(-180,180,0.25)),
            latitude=("phony_dim_2", np.arange(-60,90,0.25)[::-1]))    

        dsMW = xr.concat([dsMW.to_dataarray()[0], dsMW2.to_dataarray()[0]], dim='phony_dim_0') # Concatenate arrays to be continuous
        time_indices = np.where(time_indices>90, time_indices, time_indices+96) # Adjust time indices to be in continuous order
    else:
        dsMW = xr.open_dataset(f'/scratch/zt1/project/gcurbanheat/user/jonstar/mw_data/MW_LST_DTC_{date_str1}_x1y.h5', engine='h5netcdf')
        dsMW = dsMW.assign_coords(
            datetime=("phony_dim_0", pd.date_range(start=date_str1, periods=96, freq="15min")),
            longitude=("phony_dim_1", np.arange(-180,180,0.25)),
            latitude=("phony_dim_2", np.arange(-60,90,0.25)[::-1]))


    max_lon_index = np.where(dsMW['longitude'] == get_next_latlon_coord(np.max(latlon_pts[:,:,0]), True))[0][0]
    min_lon_index = np.where(dsMW['longitude'] == get_next_latlon_coord(np.min(latlon_pts[:,:,0]), False))[0][0]
    max_lat_index = np.where(dsMW['latitude'] == get_next_latlon_coord(np.max(latlon_pts[:,:,1]), True))[0][0]
    min_lat_index = np.where(dsMW['latitude'] == get_next_latlon_coord(np.min(latlon_pts[:,:,1]), False))[0][0]

    # Create microwave array for specific area
    # Remember: latitude decreases with index
    if date_str1 != date_str2: # Concatenation removes TB37V_LST_DTC variable
        mw_clipped = dsMW[np.min(time_indices):np.max(time_indices)+1,min_lon_index:max_lon_index+1,max_lat_index:min_lat_index+1]
        dsMW.close()
        dsMW2.close()
    else:
        mw_clipped = dsMW['TB37V_LST_DTC'][np.min(time_indices):np.max(time_indices)+1,min_lon_index:max_lon_index+1,max_lat_index:min_lat_index+1]
        dsMW.close()

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
    #try:
    geotiff_ds.to_netcdf(fname, format='NETCDF4', engine='h5netcdf')
    #except PermissionError:
    #    print('Excepted')
    #    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='GOES_download',
                    description='Fast downloading for GOES images from GEE')
    parser.add_argument('--city', help='String of city from list of valid cities to make data for')
    parser.add_argument('--cpus', nargs='?', const=32, help='Number of CPU cores to run in parallel')
    parser.add_argument('--section', nargs=1, help='Section of GOES files to process')
    args = parser.parse_args()
    
    # Pull points to make data for a specific city (look above for options)
    city = args.city
    city_zone = proj_zone[city]
    #utm_proj = Proj(proj="utm", zone=city_zone[0], datum="WGS84", northern=city_zone[1])
    if city_zone[1]:
        crs_prefix = '326'
    else:
        crs_prefix = '327'
    proj_code = f'EPSG:{crs_prefix}{city_zone[0]}'
    utm_proj = Proj(projparams=proj_code)

    if city in ['Seattle', 'San_Francisco', 'Los_Angeles', 'San_Diego', 'Phoenix', 'Las_Vegas', 'Salt_Lake_City']:
        GOES_west = True
    else:
        GOES_west = False
   
    if GOES_west:
        g_times = pd.read_csv('/home/jonstar/urban_heat_dataset/GOES_West_times.csv').value
        indices = [25268, 50775, 76786, 103146]
    else:
        g_times = pd.read_csv('/home/jonstar/urban_heat_dataset/GOES_East_times.csv').value
        indices = [25994, 52337, 78338, 104730]


    # Ensure there is a GOES directory made for the city and set it as the prefix to the filename
    section = int(args.section[0])
    if section == 1:
        suffix = '2022_1'
        start = 0
        end = indices[0]
    elif section == 2:
        suffix = '2022_2'
        start = indices[0]
        end = indices[1]
    elif section == 3:
        suffix = '2023_1'
        start = indices[1]
        end = indices[2]
    else:
        suffix = '2023_2'
        start = indices[2]
        end = indices[3]
    processed_dir = f'/scratch/zt1/project/mjmolina-prj/user/jonstar/processed_GOES_{city}_{suffix}'
    subprocess.call(['mkdir', '-p', processed_dir])


    def sort_func_GOES(s):
        return int(s.split('image_')[1].split('.tif')[0])

    GOES_tif_list = sorted(glob.glob(f'/scratch/zt1/project/gcurbanheat/user/jonstar/{city}_GOES/*.tif'), key=sort_func_GOES)
    dsG = rxr.open_rasterio(GOES_tif_list[0])
    geotiff_dsG = dsG.to_dataset('band')

    y, x = np.meshgrid(geotiff_dsG['y'], geotiff_dsG['x'])
    utm_coords = np.stack((x,y)).T.reshape(-1,2) # Get list of x, y coordinates following coordinate structure (x changes first)

    def stacked_to_latlon(pt):
        return utm_proj(pt[0], pt[1], inverse=True)

    latlon_pts_2km_1d = np.array(list(map(stacked_to_latlon, utm_coords)))
    latlon_pts_2km = latlon_pts_2km_1d.reshape((45,45,2))

    # Close opened datasets
    dsG.close()
    geotiff_dsG.close()

    file_index = np.arange(start, end)
    inputs = [[GOES_tif_list[i], datetime.datetime.fromtimestamp(g_times[i]/1000, datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ'), latlon_pts_2km, f'{processed_dir}/{city}_{GOES_tif_list[i].split('/')[-1].split('.')[0]}.nc'] for i in file_index]

    #print('Starting multiprocessing')

    start = datetime.datetime.now()
    nCPUs = int(args.cpus)
    pool = multiprocessing.Pool(nCPUs)
    pool.starmap(process_GOES_tif, inputs)
    pool.close()
    pool.join()

    time_diff = datetime.datetime.now() - start
    print(f'Total time: {time_diff.total_seconds()} seconds')
