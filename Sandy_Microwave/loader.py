import h5py
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.backends.backend_pdf import PdfPages
from  matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os
import pandas as pd

class Microwave_Loader:
    '''
        This class allows us to load microwave data beginning on a certain date.
        TODO: see plot colorbars, range of values is a bit strange atm
    '''

    NUM_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    def __init__(self, month: int = 1, day: int = 1, year: int = 2023, interval: int = 1, end_date: tuple[int, int] = (12, 31)) -> None:
        # raise error on invalid value, otherwise initialize class variables    
        self.check_params(month, day, year, interval, end_date)
        # init class instance vars
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
    
    def iterate_data(self, plot_data: bool = True) -> None:
        '''
            Main function of the loader, starts on our initialized date and goes until end_date
            Takes steps of [interval] days with each iteration, plots data and saves to PDF
        '''
        year_iter = self.Year_Iterator(self.month, self.day, self.interval, self.end_date)
        filename_middle = str(year_iter)
       
        # load a dataframe which we use to write some important values, write the column names to CSV
        df = pd.DataFrame(columns=["Date", "Min_Temp", "Max_Temp", "Hot_Temps", "Cold_Temps"])
        self.write_to_csv(df, False, True)
        pdf = PdfPages("Microwave_Plots.pdf")

        # do while loop: loads & plots at least 1 day of data
        while(True):
            # get our h5py dataset from formatted date filename, convert to numpy
            dataset_filename = self.get_dataset_filename(filename_middle)
            dataset = self.get_dataset(dataset_filename)

            if (plot_data): 
                self.plot_data_single(dataset, *year_iter.get_date_tuple(), pdf)

            # each dataframe is a row of important values that we write to a csv
            df = self.get_dataframe_values(dataset, (*year_iter.get_date_tuple(), self.year))
            self.write_to_csv(df)
            
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
        return np.array(f["TB37V_LST_DTC"])
    
    def get_dataset_filename(self, filename_middle: str) -> str:
        '''
            Creates filename for Microwave Data based on the current date, given by filename_middle
        '''
        # these two always stay the same for all files
        #filename_base = f"{os.getcwd()}\\mw_lst_{str(self.year)}\\MW_LST_DTC_{str(self.year)}"
        filename_base = f"{os.getcwd()}/mw_data/MW_LST_DTC_{str(self.year)}"
        filename_end = "_x1y.h5"
        return f"{filename_base}{filename_middle}{filename_end}"
    
    def get_dataframe_values(self, dataset: np.array, date: tuple[int, int, int]) -> pd.DataFrame:
        '''
            Testing function to see data that falls within a certain range
            Appends found values to a pandas dataframe, csv will be saved after iteration
        '''
        return pd.DataFrame({
            "Date": self.format_date_tuple(date),
            "Min Temp": [np.min(dataset)],
            "Max Temp": [np.max(dataset)],
            "Hot_Temps": [np.count_nonzero(dataset >= 20000)],
            "Cold_Temps": [np.count_nonzero(dataset <= 2500)]
        })
    
    def write_to_csv(self, df: pd.DataFrame, header_msg: bool = False, column_labels: bool = False) -> None:
        '''
            Writes our dataframe to CSV with optional message, header labels
            TODO: fix the CSV header, doesn't print correctly
        '''
        mode = "w" if column_labels else "a"
        with open("Microwave_Values.csv", "a") as file:
            if (header_msg): 
                start_date_str = self.format_date_tuple((self.month, self.day, self.year))
                end_date_str = self.format_date_tuple((self.end_date[0], self.end_date[1], self.year))
                file.write(f"Notable values starting on: {start_date_str} and ending on: {end_date_str}")
            df.to_csv("Microwave_Values.csv", sep='|', mode=mode, index=False, encoding='utf-8', header=column_labels)
        file.close()
    
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

    def format_date_tuple(self, date: tuple[int, int, int]) -> str:
        '''
            MM/dd/yyyy tuple expected
        '''
        return f"{date[0]}/{date[1]}/{date[2]}"
  
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

            # month, day tuple represents our stopping date
            self.end_date = end_date
        
        def __str__(self) -> str:
            '''
                Formats the current date stored by the iterator as MMdd
                Adds leading 0s if necessary
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
                Increments (month, day) by [interval] number of days 
            '''
            return self.iterate_day(*self.iterate_month(month, day, interval))
        
        def iterate_day(self, month: int, day: int, interval: int) -> tuple[int, int]:
            '''
                Adds [interval] days, wraps around the month if necessary
            '''
            if ((day + interval) > self.NUM_DAYS[month-1]):
                return (month + 1, (day + interval) % self.NUM_DAYS[month-1])
            return (month, day + interval)
        
        def iterate_month(self, month: int, day: int, init_interval: int) -> tuple[int, int, int]:
            '''
                Really only necessary for increments greater than the length of a month (28+ days)
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
                Number of days left in given month starting on given day
            '''
            return self.NUM_DAYS[month-1] - day + 1

        def has_next(self) -> bool:
            '''
                True if we can iterate again by [interval] days
            '''
            # perform a "test iteration" to see if we go out of bounds, return based on result
            month, day = self.perform_iteration(self.month, self.day, self.interval)
            if (self.out_of_bounds_mo(month) or self.out_of_bounds_day(month, day)):
                return False
            return True
        
        def out_of_bounds_day(self, month: int, day: int) -> bool:
            '''
                Returns whether given day is past the end date
            '''
            return (month == self.end_date[0] and day > self.end_date[1])
        
        def out_of_bounds_mo(self, month: int) -> bool:
            '''
                Returns whether given month is past the end date
            '''
            return month > self.end_date[0]
        
        def __next__(self) -> str:
            '''
                Iterates once, stores state in month, day vars
            '''
            self.month, self.day = \
            self.perform_iteration(self.month, self.day, self.interval)
            return str(self)
        
        def get_date_tuple(self) -> tuple[int, int]:
            '''
                Date as a tuple for ease of access
            '''
            return (self.month, self.day)
        


    
