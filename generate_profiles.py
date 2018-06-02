# Usage
# python generate_profiles.py --image xyz.jpg or python detect_faces.py --all 

# imports
import numpy as np
import argparse
import cv2
from PIL import Image, ImageOps, ImageDraw, ImageFont
import os

# parsing the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", 
	help="path to input image")
ap.add_argument('--all', action='store_true',
	help="all the images in the current directory")
args = vars(ap.parse_args())

# loading model
net = cv2.dnn.readNetFromCaffe("Res/deploy.prototxt.txt", "Res/res10_300x300_ssd_iter_140000.caffemodel")

image_files = []
if args["all"]:
	image_files = [file for file in os.listdir(".") if file.lower().endswith(".png") or file.lower().endswith(".jpg") or file.lower().endswith(".jpeg")]
elif args["image"] is not None:
	image_files.append(args["image"])
# load the input image and construct an input blob for the image
# by resizing to a fixed 300x300 pixels and then normalizing it
# from https://www.pyimagesearch.com/2018/02/26/face-detection-with-opencv-and-deep-learning/
for image_file in image_files:
	print("Processing",image_file+"....")
	image = cv2.imread(image_file)
	(h, w) = image.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
		(300, 300), (104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the detections and predictions
	net.setInput(blob)
	detections = net.forward()

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the
		# prediction
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
		if confidence > 0.6:
			# compute the (x, y)-coordinates of the bounding box for the
			# object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")
			# find the larger dimension to find the offset and crop coordinates
			size = max(endY-startY,endX-startX)
			offset = int(size*0.3)
			y1 = startY-(abs((endY-startY)-size)//2)-offset
			y2 = endY+(abs((endY-startY)-size)//2)+offset
			x1 = startX-(abs((endX-startX)-size)//2)-offset
			x2 = endX+(abs((endX-startX)-size)//2)+offset
			# crop the image to the face
			cropimg = image[max(y1,0):y2-min(0,y1),max(x1,0):x2-min(0,x1)]
			# resize the cropped area according to the profile's required size
			face_size = (390,390)
			cropimg = cv2.resize(cropimg, face_size) 
			# convert openCV image to PIL image
			cropimg = cv2.cvtColor(cropimg, cv2.COLOR_BGR2RGB)
			im = Image.fromarray(cropimg)
			# create circular mask for the image
			big = (im.size[0] * 3, im.size[1] * 3)
			mask = Image.new('L', big, 0)
			draw = ImageDraw.Draw(mask) 
			draw.ellipse((0, 0) + big, fill=255)
			# resize and put mask onto the cropped image
			mask = mask.resize(im.size, Image.ANTIALIAS)
			im.putalpha(mask)
			# open profile file
			prof = Image.open("Res/profile.png")
			# define relative center position for the photo and pasting photo on profile
			W,H = prof.size
			w1, h1 = im.size
			x_pos = (W-w1)//2
			y_pos = 172
			prof.paste(im,(x_pos,y_pos),im)
			# find relative position of text write the name on profile
			draw = ImageDraw.Draw(prof)
			font = ImageFont.truetype("Res/CaviarDreams_Bold.ttf", 90)
			title = image_file.split('.')[0].split('-')
			name = title[0].split('_')
			try:
				designation = ' '.join(title[1].split('_'))
			except Exception as e:
				designation = ""
			text = ' '.join(name)
			filename = '_'.join(name)
			w1, h1 = draw.textsize(text.upper(),font)
			x_pos = (W-w1)//2
			y_pos = 610
			draw.text((x_pos, y_pos),text.upper(),fill='white',font=font)

			font = ImageFont.truetype("Res/CaviarDreams.ttf", 35)
			w1, h1 = draw.textsize(designation.upper(),font)
			x_pos = (W-w1)//2
			draw.text((x_pos, y_pos+120),designation.upper(),fill='white',font=font)
			directories = ['./Profiles/','./Faces/']
			for directory in directories:
				if not os.path.exists(directory):
					os.makedirs(directory)
			prof.save(directories[0]+filename+'_profile_'+str(i)+'.png')
			im.save(directories[1]+filename+'_face_'+str(i)+'.png')