import os 
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.utils import *

def main():
    raw_path = '/fs/nexus-scratch/ayang115/dmv_dataset/numpy'
    save_path = '/fs/nexus-scratch/ayang115/dmv_dataset/datasets/goes_landsat_0.75'
    input_bands = [7, 8, 9]
    target_bands = [0, 1, 2]

    x_size = 256
    y_size = 256
    stride = 128
    fill = False
    filter_clouds = True
    cloud_threshold = 0.75
        
    dataset_len = generate_dataset(raw_path, save_path, input_bands, target_bands, x_size, y_size, stride, fill, filter_clouds, cloud_threshold)  
    
    with open(os.path.join(save_path, 'dataset_config.json'), 'w') as f:
        json.dump({
            'raw_path': raw_path,
            'save_path': save_path,
            'input_bands': input_bands,
            'target_bands': target_bands,
            'x_size': x_size,
            'y_size': y_size,
            'stride': stride,
            'fill': fill,
            'filter_clouds': filter_clouds,
            'cloud_threshold': cloud_threshold,
            'dataset_len': dataset_len
        }, f) 
    
if __name__ == '__main__':
    main()