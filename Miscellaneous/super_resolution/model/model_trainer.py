import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from torch.utils.data import DataLoader
from model.model import *
from data.dataset import SuperResolutionDataset
from data.utils import *

class SRTrainer:
    def __init__(self, args) -> None:
        self.args = args 
        
        # Load and prepare dataset
        self.train_loader, self.val_loader, self.test_loader = self.load_dataset(args.data_path, args.batch_size, args.num_workers)        
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def load_dataset(self, data_path, batch_size, num_workers):
        train_dataset = SuperResolutionDataset(data_path, 'train')
        val_dataset = SuperResolutionDataset(data_path, 'val')
        test_dataset = SuperResolutionDataset(data_path, 'test')
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
        
        return train_loader, val_loader, test_loader