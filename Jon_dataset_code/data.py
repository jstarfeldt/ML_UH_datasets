import ee
import requests
import multiprocessing
from retry import retry

ee.Initialize(project='ee-jonstar', opt_url='https://earthengine-highvolume.googleapis.com')
#ee.Initialize(project='ee-my-mips', opt_url='https://earthengine-highvolume.googleapis.com')


@retry(tries=10, delay=1, backoff=2)
def getResultGOES_new(image, region, crs, filename, verbose=False):
    """
    Handle the HTTP requests to download an image.

    Args:
        img_list (ee.List): GOES image to export, uncropped.
        city_export (tuple-like): Tuple of [UTM zone number, boolean T/F for northern/southern hemisphere, utm x coordinate, utm y coordinate] giving city export parameters
        filename (str): Name of the file to save the export data in. '.tif' Should be included at the end of the file name.
        verbose (boolean): Whether or not to print out the filename when export is done.
    """

    # Fetch the URL from which to download the image.
    url = image.getDownloadURL({
        'bands':['CMI_C13', 'CMI_C14', 'CMI_C15', 'CMI_C16'],
        'crs':crs,
        'region':region, 'scale':2000,
        'format': 'GEO_TIFF', 'filePerBand':False})
    #print('url made')

    # Handle downloading the actual pixels.
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        #print('Unsuccessful request')
        raise r.raise_for_status()
    #print('request successful')

    with open(filename, 'wb') as out_file:
        out_file.write(r.content)
    if verbose:
        print("Done: ", filename)
