from loader import Microwave_Loader

# load the microwave data and iterate thru it
loader = Microwave_Loader(day=1, month=6, year=2023, interval=1, end_date=(6, 19))
loader.iterate_data()


