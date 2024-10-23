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
    
    def __init__(self, month: int = 1, day: int = 1, year: int = 2023, interval: int = 1) -> None:
        # track the current date
        self.month = month
        self.day = day
        self.year = year

        # number of days between iteration
        self.interval = interval

    # purely for testing
    def iterate_two(self) -> None:
        year_iter = self.Year_Iterator(self.month, self.day, self.interval)
        filename_middle = str(year_iter)
        print(f"initial formatted date: {filename_middle}")

        while(True):
            dataset_filename = self.get_dataset_filename(filename_middle)
            print(f"Dataset filename: {dataset_filename}")
            # dataset = self.get_dataset(dataset_filename)
            
            # need to save plot sometime
            if (not(year_iter.has_next())):
                break
            
            filename_middle: str = next(year_iter)

    '''
    Called on init, loads up the data in the given 
    TODO: fix wrapping around with iterator (went from 2023-12-30 to 2023-04-13 with interval of 5)
    '''
    def iterate_data(self) -> None:
        # year iterator increments date and returns a string date to be used in filename
        year_iter = self.Year_Iterator(self.month, self.day, self.interval)
        filename_middle = str(year_iter)
        print(f"initial formatted date: {filename_middle}")
        pdf = PdfPages("Microwave_Plots.pdf")

        # do while loop to execute at least first day of loading data & plotting
        while(True):
            dataset_filename = self.get_dataset_filename(filename_middle)
            print(f"Dataset filename: {dataset_filename}")
            dataset = self.get_dataset(dataset_filename)
            self.plot_data(dataset, *year_iter.get_date_tuple(), pdf)
            
            # need to save plot sometime
            if (not(year_iter.has_next())):
                pdf.close()
                break
            
            filename_middle: str = next(year_iter)
    
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
    def plot_data(self, dataset: np.array, month: int, day: int, pdf: PdfPages) -> plt.figure:
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

        pdf.savefig()
        return fig

    '''
    Handles iteration through days of the year. 
    '''
    class Year_Iterator:

        NUM_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        def __init__(self, start_month: int, start_day: int, interval: int = 1) -> None:
            # track date
            self.day = start_day
            self.month = start_month
            self.interval = interval

        '''
        :returns: str representing month/day with leading 0s, if necessary
        '''
        def __str__(self) -> str:
            # formats month, day for filename use
            def stringify_date(date: int) -> str:
                toReturn = ""
                if (date < 10):
                    toReturn += "0"
                return toReturn + str(date)
            
            return f"{stringify_date(self.month)}{stringify_date(self.day)}"
        
        '''
        Increments day

        TODO: fix variable step for special case: step is larger than a whole month
        '''
        def perform_iteration(self, month: int, day: int, interval: int) -> tuple[int, int]:
            return self.iterate_day(*self.iterate_month(month, day, interval))
        
        def iterate_day(self, month: int, day: int, interval: int) -> tuple[int, int]:
            if ((day + interval) > self.NUM_DAYS[month-1]):
                return (month + 1, (day + interval) % self.NUM_DAYS[month-1])
            return (month, day + interval)
        
        def iterate_month(self, month: int, day: int, init_interval: int) -> tuple[int, int, int]:
            interval = init_interval
            # for intervals greater than a month, we go month by month
            while (interval > self.NUM_DAYS[month-1]):
                interval -= self.get_days_left(month, day)
                day = 1
                month += 1

                # preventing OOB error
                if (month >= 13):
                    break

            return month, day, interval

        '''
        :returns: Number of days left in current month
        '''
        def get_days_left(self, month: int, day: int) -> int:
            return self.NUM_DAYS[month-1] - day + 1

        '''
        If we would go out of bounds, we do not have a next item
        :returns: boolean representing whether we go past the end of the year
        '''
        def has_next(self) -> bool:
            # try and update the day, if we go too far return false
            month, *unused = self.perform_iteration(self.month, self.day, self.interval)
            if (month >= 13):
                return False
            return True

        '''
        Iterates the day if it's within the bounds of the year and returns result
        :returns: str representing the date (used in microwave data filename)
        '''
        def __next__(self) -> str:
            # if (self.has_next):
            #     self.month, self.day = \
            #     self.perform_iteration(self.month, self.day, self.interval)
            self.month, self.day = \
            self.perform_iteration(self.month, self.day, self.interval)
            return str(self)

        '''
        We use this in our loader functions
        :returns: tuple of (month, day)
        '''
        def get_date_tuple(self) -> tuple[int, int]:
            return (self.month, self.day)
        


    
