import os
import glob
import gdal
import requests

from bs4 import BeautifulSoup

#Crawl the NASA HLS webpage to extract all the .hdf files

# specify the URL of the archive here
archive_url = "https://hls.gsfc.nasa.gov/data/v1.4/S30/2017/11/S/K/V/"
#archive_url = "https://hls.gsfc.nasa.gov/data/v1.4/S30/2017/10/S/F/G/"
#archive_url = "https://hls.gsfc.nasa.gov/data/v1.4/S30/2017/10/S/E/J/"

def get_satellite_images():

	# create response object
	r = requests.get(archive_url)

	# create beautiful-soup object
	soup = BeautifulSoup(r.content,'html5lib')

	# find all links on web-page
	links = soup.findAll('a')

	# filter the link sending with hdf
	satellite_images = [archive_url + link['href'] for link in links if link['href'].endswith('hdf')]

	return satellite_images

def convert_to_geotiff(files):

	for file in files:
	    # convert to individual bands
	    os.system(str("gdal_translate -of GTiff -sds " + file + " tmp_outs.tif"))

	    print("Converting: " + str(file) + " to GeoTiff")

	    # merge into single GeoTiff
	    os.system("gdal_merge.py -separate -o " + file[:-4] + ".tif tmp_outs*tif")

	    # remove temporary files
	    os.system("rm tmp_outs*tif")


def download_hls_data(satellite_images):

	for image in satellite_images:
		'''Iterate through all images in satellite_images
		and download them one by one'''

		# obtain filename by splitting url and getting last string
		file_name = image.split('/')[-1]

		print("Downloading file: %s"%file_name)

		# create response object
		r = requests.get(image, stream = True)

		# download started
		with open(file_name, 'wb') as f:
			for chunk in r.iter_content(chunk_size = 1024*1024):
				if chunk:
					f.write(chunk)

	print("Download Completed")


if __name__ == "__main__":

	# getting all satellite images
	satellite_images = get_satellite_images()

	# download all HLS data
	download_hls_data(satellite_images)
	files = [x for x in glob.glob('*.hdf')]

	# convert hdf to Geotiff
	convert_to_geotiff(files)



