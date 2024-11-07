# h5py stuff
import h5py

# plotting etc
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.backends.backend_pdf import PdfPages
from  matplotlib.colors import LinearSegmentedColormap
import numpy as np

# not needed for now
import os
import functools
import math



class Microwave_Loader:
    '''
        This class allows us to load microwave data beginning on a certain date.
        TODO: see plot colorbars, range of values is a bit strange atm
        TODO: check for missing values (see email and slack)
    '''

    NUM_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    def __init__(self, month: int = 1, day: int = 1, year: int = 2023, interval: int = 1, end_date: tuple[int, int] = (12, 31)) -> None:
        # raise error on invalid value, otherwise initialize class variables    
        try:
            self.check_params(month, day, year, interval, end_date)
        except(ValueError):
            pass
        self.month = month
        self.day = day
        self.year = year
        self.interval = interval
        self.end_date = end_date

    
    def check_params(self, month: int, day: int, year: int, interval: int, end_date: tuple[int, int]) -> bool:
        '''
            Validity check for params, errors if we initialize wrong
        '''
        def invalid_mo(month: int):
            return (month > 12 or month < 1)
        
        def invalid_day(month: int, day: int):
            return (day > self.NUM_DAYS[month-1] or day < 1)
        
        to_return = False
        
        # handling month, year errors
        if (invalid_mo(month)): 
            raise(ValueError("Invalid month."))
        elif(year < 2022 or year > 2023): 
            raise(ValueError("Invalid year."))
        elif (invalid_day(month, day)):
            raise(ValueError("Invalid day."))
        elif (interval > 365):
            raise(ValueError("Invalid interval."))
        elif (invalid_mo(end_date[0]) or invalid_day(*end_date)):
            raise(ValueError("Invalid end date."))
        else: 
            to_return = True
        return to_return  

    
    def iterate_data(self) -> None:
        '''
            Main function of the loader, starts on our initialized date and goes until end_date
            Takes steps of [interval] days with each iteration, plots data and saves to PDF
        '''
        # year iterator increments date and returns a string date to be used in filename
        year_iter = self.Year_Iterator(self.month, self.day, self.interval, self.end_date)
        filename_middle = str(year_iter)
        print(f"initial formatted date: {filename_middle}")
        pdf = PdfPages("Microwave_Plots.pdf")

        # do while loop: loads & plots at least 1 day of data
        while(True):
            dataset_filename = self.get_dataset_filename(filename_middle)
            print(f"Dataset filename: {dataset_filename}")
            dataset = self.get_dataset(dataset_filename)
            self.plot_data_single(dataset, *year_iter.get_date_tuple(), pdf)
            
            # once we are done iterating, stop the loop and save plots to pdf
            if (not(year_iter.has_next())):
                pdf.close()
                break
            
            filename_middle = next(year_iter)
    
   
    def get_dataset(self, filename: str) -> np.array:
        '''
            Extract microwave as a 3D array from given file
        '''
        f = h5py.File(filename, 'r')
        dataset_location = "TB37V_LST_DTC"
        return np.array(f[dataset_location])
    
    def get_dataset_filename(self, filename_middle: str) -> str:
        '''
            Creates filename for Microwave Data based on the current date, given by filename_middle
        '''
        # these two always stay the same for all files
        filename_base = f"{os.getcwd()}\\mw_lst_{str(self.year)}\\MW_LST_DTC_{str(self.year)}"
        filename_end = "_x1y.h5"
        return f"{filename_base}{filename_middle}{filename_end}"

   
    def plot_data_double(self, dataset: np.array, month: int, day: int, pdf: PdfPages) -> plt.figure:
        '''
            Plots our data from 2 evenly-spaced time slices (morning, evening)

            :param dataset: microwave dataset as np array
            :returns: pyplot (matplotlib) object representing the two plotted time slices

            TODO: make it so that we don't just have hardcoded times of day
        '''
        # right now I only support 2 plots per day, evenly spaced
        fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(12, 12), dpi=80)
        plt.subplots_adjust(wspace=0.3)
        
        # start of day plot
        ax1.imshow(dataset[24].T)
        ax1.set_title(f"Morning on: {month}/{day}")
        ax1.set_xlabel("Latitude")
        ax1.set_ylabel("Longitude")
        # plt.colorbar(label="Microwave Temp", orientation="horizontal") 
        
        # end of day plot
        ax2.imshow(dataset[72].T)
        ax2.set_title(f"Evening on: {month}/{day}")
        ax2.set_xlabel("Latitude")
        ax2.set_ylabel("Longitude")
        # plt.colorbar(label="Microwave Temp", orientation="horizontal") 

        pdf.savefig()
        return fig
    
    
    def plot_data_single(self, dataset: np.array, month: int, day: int, pdf: PdfPages) -> plt.figure:
        '''
            Plots a single timeslice of the given dataset (1 day of data)
        '''
        fig, ax = plt.subplots()
        plot = ax.imshow(dataset[48].T, cmap="RdYlGn_r")
        ax.set_title(label=f"Midday on: {month}/{day}")
        ax.set_xlabel("Latitude")
        ax.set_ylabel("Longitude")
        plt.colorbar(orientation="vertical", mappable=plot)
        pdf.savefig()

    
    class Year_Iterator:
        '''
            Handles iteration through days of the year. 
        '''

        NUM_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        def __init__(self, start_month: int, start_day: int, interval: int = 1, end_date: tuple[int, int] = (12, 31)) -> None:
            # track date
            self.day = start_day
            self.month = start_month
            self.interval = interval

            # month, day represents our stopping date
            self.end_date = end_date

        
        def __str__(self) -> str:
            '''
                :returns: str representing month/day with leading 0s, if necessary
            '''
            # formats month, day for filename use
            def stringify_date(date: int) -> str:
                toReturn = ""
                if (date < 10):
                    toReturn += "0"
                return toReturn + str(date)
            
            return f"{stringify_date(self.month)}{stringify_date(self.day)}"
        
        
        def perform_iteration(self, month: int, day: int, interval: int) -> tuple[int, int]:
            '''
                Increments our date (month, day) by [interval] number of days 
            '''
            return self.iterate_day(*self.iterate_month(month, day, interval))
        
        def iterate_day(self, month: int, day: int, interval: int) -> tuple[int, int]:
            '''
                Add interval to day, return new date
            '''
            if ((day + interval) > self.NUM_DAYS[month-1]):
                return (month + 1, (day + interval) % self.NUM_DAYS[month-1])
            return (month, day + interval)
        
        def iterate_month(self, month: int, day: int, init_interval: int) -> tuple[int, int, int]:
            '''
                For increments greater than a month, this lets us iterate
                TODO: check for bugs now that (month >= 13) check is gone
            '''
            interval = init_interval
            # for intervals greater than a month, we go month by month
            while (interval > self.NUM_DAYS[month-1]):
                interval -= self.get_days_left(month, day)
                day = 1
                month += 1

            return month, day, interval

        
        def get_days_left(self, month: int, day: int) -> int:
            '''
                :returns: Number of days left in current month
            '''
            return self.NUM_DAYS[month-1] - day + 1

        
        def has_next(self) -> bool:
            '''
                :returns: boolean representing whether we go past end date after one iteration
            '''
            # try and update the day, if we go too far return false
            month, day = self.perform_iteration(self.month, self.day, self.interval)
            if (self.out_of_bounds_mo(month) or self.out_of_bounds_day(month, day)):
                return False
            return True
        
        def out_of_bounds_day(self, month, day) -> bool:
            '''
                Determines whether we are out of bounds of iteration w.r.t the end day
            '''
            return (month == self.end_date[0] and day > self.end_date[1])
        
        def out_of_bounds_mo(self, month) -> bool:
            '''
                Determines whether we are out of bounds of iteration w.r.t the end month
            '''
            return month > self.end_date[0]

        
        def __next__(self) -> str:
            '''
                Iterates the day and stores in instance variable date tuple
                :returns: str representing the date (used in microwave data filename)
            '''
            self.month, self.day = \
            self.perform_iteration(self.month, self.day, self.interval)
            return str(self)

        
        def get_date_tuple(self) -> tuple[int, int]:
            '''
                We use this in our loader functions
                :returns: tuple of (month, day)
            '''
            return (self.month, self.day)
        


    
