# h5py stuff
import h5py

# plotting etc
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# not needed for now
import os
import functools
import math

'''
This class allows us to load microwave data beginning on a certain date.
TODO: add functionality to actually plot and save to PDF
TODO: allow us to iterate a variable number of days per month
'''

class Microwave_Loader:
    
    def __init__(self, month: int = 1, day: int = 1, year: int = 2023) -> None:
        # track the current date
        self.month = month
        self.day = day
        self.year = year

    '''
    Called on init, loads up the data in the given 
    '''
    def iterate_data(self) -> None:
        year_iter = self.Year_Iterator(self.month, self.day)
        filename_middle = str(year_iter)
        print(f"initial formatted date: {filename_middle}")

        # do while loop to execute at least first day of loading data & plotting
        while(True):
            dataset_filename = self.get_dataset_filename(filename_middle)
            print(f"Dataset filename: {dataset_filename}")
            dataset = self.get_dataset(dataset_filename)
            plot = self.plot_data(dataset, *year_iter.get_date_tuple())
            plt.show() # not sure if this works
            # need to save plot sometime
            if (not(year_iter.has_next())):
                break
            
            filename_middle: str = next(year_iter.get_date())
    
    '''
    Convert filename string into 3D microwave data
    
    :param filename: string representing our full path to the microwave data file (1 day of data)
    :returns: np array represnting our data (shape is (time slice, lat, lon))
    '''
    def get_dataset(self, filename: str) -> np.array:
        f = h5py.File(filename, 'r')
        dataset_location = "TB37V_LST_DTC"
        return np.array(f[dataset_location])
    '''
    Iterates through filenames by updating month, day instance vars
    
    :param update: whether we want to update the day (only false when we first call this)
    :returns: str representing the next file we will process
    '''
    
    def get_dataset_filename(self, filename_middle: str) -> str:
        # these two always stay the same for all files
        filename_base = f"{os.getcwd()}\\mw_lst_{str(self.year)}\\MW_LST_DTC_{str(self.year)}"
        filename_end = "_x1y.h5"
        return f"{filename_base}{filename_middle}{filename_end}"

    '''
    Plots our data from 2 evenly-spaced time slices (morning, evening)

    :param dataset: microwave dataset as np array
    :returns: pyplot (matplotlib) object representing the two plotted time slices

    TODO: make it so that we don't just have hardcoded times of day
    '''
    def plot_data(self, dataset: np.array, month: int, day: int) -> plt.figure:
        # right now I only support 2 plots per day, evenly spaced
        fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(12, 12), dpi=80)
        plt.subplots_adjust(wspace=0.3)
        
        # start of day plot
        ax1.imshow(dataset[24].T)
        ax1.set_title(f"Morning on: {month}/{day}")
        ax1.set_xlabel("Latitude")
        ax1.set_ylabel("Longitude")
        
        # end of day plot
        ax2.imshow(dataset[72].T)
        ax2.set_title(f"Evening on: {month}/{day}")
        ax2.set_xlabel("Latitude")
        ax2.set_ylabel("Longitude")
        return fig

    '''
    Handles iteration through days of the year. 
    TODO: add functionality for variable step length (i.e. throughout the day and throughout the year)
    '''
    class Year_Iterator:

        NUM_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        def __init__(self, start_month: int, start_day: int) -> None:
            # track date
            self.day = start_day
            self.month = start_month

        def __str__(self) -> str:
            
            # formats month, day for filename use
            def stringify_date(date: int) -> str:
                toReturn = ""
                if (date < 10):
                    toReturn += "0"
                return toReturn + str(date)
            
            return f"{stringify_date(self.month)}{stringify_date(self.day)}"
        '''
        Calculates the bounds of iterations based on a full year of data
        
        :returns: int representing how many days we will iterate over
        
        TODO: add in an interval/step functionality 
        '''
        
        # increment the day, wrap month if necessary
        def update_day(self) -> None:
            days_this_month: int = self.NUM_DAYS[self.month-1]
            self.day += 1
            # after day iteration we may pass into a new month 
            if (self.day > days_this_month):
                self.month += 1
                self.day = self.day % days_this_month # should always be 1
            # wrap around to Jan if we pass Dec
            if (self.month == 13):
                self.month = 1
                self.day = self.day % days_this_month # should always be 1

        '''
        Iterates then returns the date string
        '''
        def get_date(self):
            while (self.has_next):
                self.update_day()
                yield str(self)

        '''
        We use this in our loader functions
        '''
        def get_date_tuple(self) -> tuple[int, int]:
            return self.month, self.day
        
        '''
        Iterator-style fcn to determine whether we have remaining days in year
        :returns: boolean indicating whether we can continue iteration
        '''
        def has_next(self) -> bool:
            return (not(self.day == 31 and self.month == 12))


    
