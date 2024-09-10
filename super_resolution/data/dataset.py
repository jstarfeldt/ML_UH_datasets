import torch
import numpy
import os

from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.transforms import Compose

DATA_FOLDER_NAME = 'data'
TARGET_FOLDER_NAME = 'targets'
DATA_TAG = 'data'
TARGET_TAG = 'target'


class SuperResolutionDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.data_path = os.path.join(root_dir, DATA_FOLDER_NAME)
        self.target_path = os.path.join(root_dir, TARGET_FOLDER_NAME)
        self.transform = transform
        
        self.data = []
        self.targets = []
        
        for file in os.listdir(self.data_path):
            data_name = file
            target_name = data_name.replace(DATA_TAG, TARGET_TAG)
            
            if file.endswith('.npy'):
                self.data.append(numpy.load(os.path.join(self.data_path, data_name)))
                self.targets.append(numpy.load(os.path.join(self.target_path, target_name)))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        data = self.data[idx]
        target = self.targets[idx]

        if self.transform:
            data = self.transform(data)
            target = self.transform(target)

        return data, target