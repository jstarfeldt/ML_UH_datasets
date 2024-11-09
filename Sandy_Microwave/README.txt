Hi! If you downloaded this you're probably looking to load the Microwave Dataset for cloud gap-filling. 
I've included a driver class with an example functionality of this module, but essentially everything
is handled by the Microwave_Loader class and its subclass iterator. 

The data is loaded from an h5 dataset, which is then converted to a numpy 3D array with shape (timeslice, lat, lon). 
Every day is a new dataset, so the loader has an iterator implemented to move through the data and perform various data 
analysis functions (plotting using the plot_data_single function, or numpy functions in a pandas dataframe in )