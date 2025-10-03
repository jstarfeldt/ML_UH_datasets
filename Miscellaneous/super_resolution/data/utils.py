import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import datetime

from .classes import *
from .dataset import *
from tqdm import tqdm

# Tiff processing
def create_tiles(arr, x_size, y_size, stride=None, fill=False):
    """
    Create tiles from a 3D array.
    """
    if stride is None:
        stride = x_size
    
    x_len = arr.shape[-2]
    y_len = arr.shape[-1]
    x_pos = 0 
    y_pos = 0
    tiles = []
    
    while x_pos+x_size < x_len:
        while y_pos+y_size < y_len:
            tile = arr[::, x_pos:x_pos+x_size, y_pos:y_pos+y_size]
            x_pos = x_pos + stride
            y_pos = y_pos + stride 
            
            if np.isnan(np.min(tile)) and fill: 
                tiles.append(np.zeros(tile.shape))
            elif np.isnan(np.min(tile)) and not fill: 
                continue
            else: 
                tiles.append(tile)
    
    return np.stack(tiles, axis=0)

def to_cloud_flag(num, flag_idx=LANDSAT_CLOUD_FLAG_BIT):
    
    """
    Convert a number to a cloud mask.
    """
    if np.isnan(num):
        return np.nan
    else:
        bit_string = f'{int(num):b}'
        if bit_string[flag_idx]==1:
            return CLOUD_FLAG
        else:  
            return NON_CLOUD_FLAG
    
def cloud_percentage(mask):
    return np.sum(mask)/mask.size

def generate_tiles(arr, x_size, y_size, stride=256, fill=False, filter_clouds=False, cloud_threshold=None):
    """
    Generate tiles from a 3D array.
    """
    assert filter_clouds and cloud_threshold is not None, "Please provide a cloud threshold."
    
    tiles = create_tiles(arr, x_size, y_size, stride=stride, fill=fill)
    
    if not filter_clouds: 
        return tiles
    
    cloud_mask = np.vectorize(to_cloud_flag)
    tile_shape = tiles[0].shape
    for tile in tqdm(tiles):
        tile_cloud_mask = cloud_mask(tile[LANDSAT_CLOUD_MASK_BAND_IDX])
        if cloud_percentage(tile_cloud_mask) > cloud_threshold:
            tiles.remove(tile)
            assert tile.shape == tile_shape, "Tile shape mismatch."
    
    return tiles

def generate_dataset(raw_path, save_path, input_bands, target_bands, x_size, y_size, stride=256, fill=False, filter_clouds=False, cloud_threshold=None):
    """
    Generate a dataset from a 3D array.
    """
    data_path = os.path.join(save_path, DATA_FOLDER_NAME)
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        
    target_path = os.path.join(save_path, TARGET_FOLDER_NAME)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    
    id = 0
    print("Generating dataset...")
    for image in os.listdir(raw_path):
        data = np.load(os.path.join(raw_path, image))
        tiles = generate_tiles(data, x_size, y_size, stride=stride, fill=fill, filter_clouds=filter_clouds, cloud_threshold=cloud_threshold)
    
        for tile in tiles:
            np.save(os.path.join(data_path, "{}_{}.npy".format(id, DATA_TAG)), tile[input_bands])
            np.save(os.path.join(target_path, "{}_{}.npy".format(id, TARGET_TAG)), tile[target_bands])
            id += 1
    
    assert len(os.listdir(data_path)) == len(os.listdir(target_path)), "Data and target mismatch."
    
    return len(os.listdir(data_path))
    
        
            
             