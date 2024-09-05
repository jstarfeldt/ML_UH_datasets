import os
import numpy as np
import rioxarray as rxr
from tqdm import tqdm

def main():
    sample = '/fs/nexus-scratch/ayang115/dmv_dataset'

    for file in tqdm(os.listdir(os.path.join(sample, 'raw'))):
        raw = rxr.open_rasterio(os.path.join(sample, 'raw', file))
        npy = raw.to_numpy()
        
        np.save(os.path.join(sample, 'numpy', file.split('.')[0]+'.npy'), npy)
        
if __name__ == '__main__':
    main()
