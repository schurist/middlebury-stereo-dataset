import os
import glob
import cv2
import numpy as np
import pickle
import json

# Read links from txt file
links_file_name = "dataset_links.txt"
download_files = False
perform_conversion = True
create_pickles = False
download_path = os.path.dirname(__file__)

def parse_array_from_string(arr_str: str) -> np.ndarray:
	arr_str = arr_str.replace('[', '')
	arr_str = arr_str.replace(']', '')
	cols = arr_str.split(';')
	rows = []
	for col in cols:
		rows.append(np.fromstring(col, sep=' '))

	return np.asarray(rows)

if download_files:
	# Download all selected links to local drive
	with open(links_file_name, 'r') as links_file:

		link = links_file.readline()

		while link:
			print(link)
			# download file
			ret = os.system('wget -c ' + link)
			if ret == 0:
				link = links_file.readline()

	# unzipping all downloaded file
	# Getting all filenames


zip_names = glob.glob(os.path.join(download_path, '*.zip'))

for filename in zip_names:
	os.system('unzip ' + filename) # unzipping
	# os.system('rm ' + filename) # removing zip file to save space

# # Converting PFM to PNG 
filenames = glob.glob(os.path.join(download_path, '*-perfect')) # All unzip filenames

if perform_conversion:
	print('PFM to PNG conversion ...')
	for filename in filenames:

		# Removing -sd.pfm since I am not interested in those
		sd_pfm_files = glob.glob(filename + '/*-sd.pfm')
		for sd_pfm_file in sd_pfm_files:
			os.system('rm ' + sd_pfm_file)

		# Converting PFM to PNG
		pfm_files = glob.glob(filename + '/*.pfm')
		for pfm_file in pfm_files:
			png_filename = pfm_file[:-4] # removing .pfm to be replaced by PNG
			os.system('convert ' + pfm_file + ' ' + png_filename + '.png')
			os.system('rm ' + pfm_file)

		# removing pgm files since I am not interested in those
		pgm_files = glob.glob(filename + '/*.pgm')
		for pgm_file in pgm_files:
			os.system('rm ' + pgm_file)
		# removing lightning images (E & L) since I am not interested in those
		lightning_file = glob.glob(filename + '/*1L.png')
		os.system('rm ' + lightning_file[0])
		lightning_file = glob.glob(filename + '/*1E.png')
		os.system('rm ' + lightning_file[0])

		print('TXT to JSON conversion ...')

		calib_txt = os.path.join(download_path, filename, "calib.txt")
		calib_json = {}

		txt_file = open(calib_txt, 'r') 
		lines = txt_file.readlines() 

		for line in lines:
			line = line.replace('\\n', '')
			key, value = line.split("=")
			if value.startswith('['):
				print("Parsing array")
				cam_array = parse_array_from_string(value)
				with open(os.path.join(download_path, filename, "{}.pickle".format(key)), "wb") as pickle_out:
					pickle.dump(cam_array, pickle_out)
			else:
				calib_json[key] = float(value)

		print(calib_json)
		with open(os.path.join(download_path, filename, "calib.json"), 'w') as fp:
			json.dump(calib_json, fp)

if create_pickles:
	## Creation of the pickle
	depth_imgs = []
	gray_imgs  = []

	for filename in filenames:
		png_depth_files = glob.glob(filename + '/disp*.png')
		png_im_files = glob.glob(filename + '/im*.png')
		for png_depth_file, png_im_file  in zip(png_depth_files, png_im_files):
			# Adding depth file
			depth = cv2.imread(png_depth_file, 0) # read as gray img
			depth = depth / 255.0  # normalizing
			depth_imgs.append(depth)
			# Adding im file as gray
			im = cv2.imread(png_im_file, 0) # read as gray image
			im = im / 255.0 # normalizing
			gray_imgs.append(im)

	# File lists are ready, let's save them into a pickle
	# Saving depth images
	with open(os.path.join(dataset_dir, 'depth.pickle'), "wb") as pickle_out:
		pickle.dump(depth_imgs, pickle_out)

	# Saving gray images
	with open(os.path.join(dataset_dir, 'gray.pickle'), "wb") as pickle_out:
		pickle.dump(gray_imgs, pickle_out)

# Done