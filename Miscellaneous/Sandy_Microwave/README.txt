Hi! If you downloaded this you're probably looking to load the Microwave Dataset for cloud gap-filling. 
I've included a driver class with an example functionality of this module, but essentially everything
is handled by the Microwave_Loader class and its subclass iterator. 

The data is loaded from an h5 dataset, which is then converted to a numpy 3D array with shape (timeslice, lat, lon). 
Every day is a new dataset, so the loader has an iterator implemented to move through the data and perform various data 
analysis functions (plotting using the plot_data_single function, or data exploration values in a pandas dataframe in get_dataframe_values).

You can change the step (# of days between iterations) using the interval parameter, and can specify an end_date (default 12/31) as a (month, day) tuple.
Required args are (month, day, year), in that order. Once the loader has been initialized, you can begin iteration by calling the iterate_data instance
method.