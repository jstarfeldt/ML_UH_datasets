# h5py stuff
import h5py

# plotting etc
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import functools
import math

'''
This class allows us to load microwave data beginning on a certain date.
TODO: add functionality to actually plot and save to PDF
TODO: allow us to iterate a variable number of days per month
'''

class Microwave_Loader:

    NUM_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    def __init__(self, month: int = 1, day: int = 1, year: int = 2023) -> None:
        # track the current date
        self.month = month
        self.day = day
        self.year = year
        # load the data from the dataset in the given month and day
        self.load_and_plot_data()

    '''
    Called on init, loads up the data in the given 
    '''
    def load_and_plot_data(self) -> None:
        # num_days is the number of days we will iterate through
        num_days: int = self.get_days_in_year() # smth wrong with this

                # create our dataset filename without incrementing day value, on desired date
        dataset_filename = self.update_dataset_filename(False)
        
        # iterate thru each day
        for i in range(num_days):
            # retrieve our dataset and plot it
            print(f"filename: {dataset_filename}")
            dataset = self.get_dataset_from_filename(dataset_filename)
            plot = self.plot_data(dataset)

            # update the filename and (month, day) using the proper interval
            dataset_filename = self.update_dataset_filename(True)

    # allows us to know how many days to add per month
    def get_monthly_intervals(self) -> list[int]:
        return [math.ceil(item / self.days_per_mo) for item in self.NUM_DAYS]
        # for item in self.NUM_DAYS:
        #     intervals.append(int(item / self.days_per_mo))
        # return intervals

    # want to have different PDFs for each month
    def create_pdf_filename(self, filename_middle: str = "0101") -> str:
        pdf_name_base = r"/content/drive/MyDrive/Urban_Heat/Start_End_Day_Microwave"
        pdf_name_middle = filename_middle[0:2]
        pdf_name_end = ".pdf"
        return pdf_name_base + pdf_name_middle + pdf_name_end
    
    '''
    Convert filename string into 3D microwave data
    
    :param filename: string representing our full path to the microwave data file (1 day of data)
    :returns: np array represnting our data (shape is (time slice, lat, lon))
    '''
    def get_dataset_from_filename(self, filename: str) -> np.array:
        f = h5py.File(filename, 'r')
        dataset_location = "TB37V_LST_DTC"
        return np.array(f[dataset_location]).T
    
    '''
    Iterates through filenames by updating month, day instance vars
    
    :param update: whether we want to update the day (only false when we first call this)
    :returns: str representing the next file we will process
    '''
    def update_dataset_filename(self, update: bool = True) -> str:
        # these two always stay the same for all files
        FILENAME_BASE = f"Sandy_Microwave\\mw_lst_{str(self.year)}\\MW_LST_DTC_{str(self.year)}"
        FILENAME_END = "_x1y.h5"

        # convert a day/month value to a string
        def stringify_date(date: int) -> str:
            toReturn = ""
            if (date < 10):
                toReturn += "0"
            return toReturn + str(date)

        # increment the day, wrap month if necessary
        def update_day() -> None:
            days_this_month = self.NUM_DAYS[self.month-1]
            if (update):
                self.day += 1
            # change month if necessary, make day 
            if (self.day > days_this_month):
                self.month += 1
                self.day = self.day % days_this_month # should always be 1
            if (self.month == 13):
                self.month = 1
                self.day = self.day % days_this_month # should always be 1
            return

        update_day()

        return str(FILENAME_BASE + stringify_date(self.month) + stringify_date(self.day) + FILENAME_END)
    
    '''
    Plots our data from 2 evenly-spaced time slices (morning, evening)

    :param dataset: microwave dataset as np array
    :returns: pyplot (matplotlib) object representing the two plotted time slices
    '''
    def plot_data(self, dataset: np.array) -> plt.figure:
        # right now I only support 2 plots per day, evenly spaced
        f, (ax1, ax2) = plt.subplots(1, 2)
        
        # start of day plot
        ax1.imshow(dataset[24])
        ax1.set_title(f"Morning on: {self.month}/{self.day}")
        ax1.set_xlabel("Latitude")
        ax1.set_ylabel("Longitude")
        
        # end of day plot
        ax2.imshow(dataset[72])
        ax2.set_title(f"Evening on: {self.month}/{self.day}")
        ax2.set_xlabel("Latitude")
        ax2.set_ylabel("Longitude")
        return f
    
    '''
    Finds the number of files we will iterate through from our start date

    :returns: number of days in year starting from start date
    '''
    def get_days_in_year(self) -> int:
        days_left = 0
        first_month = True

        # calculate number of days left based on what month/day we are starting on
        for month_days in (self.NUM_DAYS[self.month-1:]):
            if (first_month):
                days_left += month_days - self.day
                first_month = False
            else:
                days_left += month_days
        
        return days_left + 1