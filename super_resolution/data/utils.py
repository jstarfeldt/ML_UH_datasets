import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rxr
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import datetime
import utm
from pyproj import CRS

from .classes import *

# Tiff processing
def create_tiles(arr, x_size, y_size, stride=256, fill=False):
    """
    Create tiles from a 3D array.
    """
    x_tiles = np.arange(0, arr.shape[-1]//stride)
    y_tiles = np.arange(0, arr.shape[-2]//stride)
    tiles = []
    
    for x in x_tiles:
        for y in y_tiles:
            tile = arr[::, x*stride:x*stride+x_size, y*stride:y*stride+y_size]
            if np.isnan(np.min(tile)) and fill: 
                tiles.append(np.zeros(tile.shape))
            elif np.isnan(np.min(tile)) and not fill: 
                continue
            else: 
                tiles.append(tile)
    
    return np.stack(tiles, axis=0)

def to_cloud_flag(num, flag_idx=6):
    """
    Convert a number to a cloud mask.
    """
    if np.isnan(num):
        return np.nan
    else:
        bit_string = f'{int(num):b}'
        if bit_string[flag_idx]==1:
            return 1
        else:  
            return 0
    
def cloud_percentage(mask):
    return np.sum(mask)/mask.size