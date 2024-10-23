Hi! If you downloaded this you're probably looking to load the Microwave Dataset for cloud gap-filling. 
I've included a driver class with an example functionality of this module, but essentially everything
is handled by the Microwave_Loader class and its subclass iterator. 

Right now it seems like there are some issues with my plot_data function, since the brightness of the data (microwave temperature)
is uniform across the world (when there are obvious variations all over). There are also some holes in the data that appear seemmingly randomly, 
but granted I am only plotting 2 time slices per day.

One big limitation right now is that matplotlib's PDF API only allows for 20 plots at a time, which is super frustrating. I want to find a different
way to save my plots but until then it's hard to see real trends. 

In the future I'd also like to add a way to change the step in iteration so that we aren't just plotting
every day of every month since our starting date. 