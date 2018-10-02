# Color detector from images using Python and OpenCV2
# Witten by Khakim Assidiqi
# on 30 september 2018 
# https://github.com/elybin/Color_Detector_from_Image_with_Python

# 1.Mengimport library yang dibutuhkan 
#	a. NumPy : adding support for large, multi-dimensional arrays and matrices. (pip install numpy)
#	b. Argparse : Ggenerates help and usage messages and issues errors when users give the program invalid arguments. (pip install argparse)
#	c. OpenCV : OpenCV is a library of programming functions mainly aimed at real-time computer vision. (pip install opencv-python) 
import numpy as np 
import argparse
import cv2

# 2. Buat fungsi untuk membuat kotak seleksi dan fungsi mengubah ukuran gambar 
def draw_boxx(img_src, lefttop, rightbottom, text, color):
	# draw the line 
	lefttop = (lefttop[0]-5, lefttop[1]-5)
	rightbottom = (rightbottom[0]+5, rightbottom[1]+5)
	cv2.rectangle(img_src, lefttop, rightbottom, color, 2)
	# put text there
	font = cv2.FONT_HERSHEY_SIMPLEX
	px = lefttop[0]+5 # x
	py = lefttop[1]+15 # y
	cv2.putText(img_src, text, (px, py), font, 0.4, color, 1, cv2.LINE_AA)

# fungsi untuk mengubah ukuran gambar
# source: https://stackoverflow.com/questions/44650888/resize-an-image-without-distortion-opencv
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized


#define boundaries 
# in hsv 
# Why HSV? 

# -> "HSV is a good color space for color detection. This is a hsv colormap for reference:"
# -> https://stackoverflow.com/questions/48528754/what-are-recommended-color-spaces-for-detecting-orange-color-in-open-cv

# "Because the R, G, and B components of an object's color in a digital image are all correlated with the 
# amount of light hitting the object, and therefore with each other, image descriptions in terms of those 
# components make object discrimination difficult. Descriptions in terms of hue/lightness/chroma or 
# hue/lightness/saturation are often more relevant."
# https://stackoverflow.com/questions/17063042/why-do-we-convert-from-rgb-to-hsv/17063317


# OpenCV HSV range is: H: 0 to 179 S: 0 to 255 V: 0 to 255
hsv_boundaries = [
	([155,50,50], [170,255,255], 'jambon'),
	([170,50,50], [179,255,255], 'merah'),
	([0, 50, 50], [13,255,255], 'oren'),
	([15,100,100], [36, 255, 255], 'kuning'),
	([40,50,50], [80, 255, 255], 'ijo'),
	([110,50,50], [150, 255, 255], 'biru'),
	([90,50,50], [100, 255, 255], 'biru muda'),
	([141,50,50], [160, 255, 255], 'ungu')
]
	

# 3. Ambil nama file dari argumen -i 
ap = argparse.ArgumentParser()
ap.add_argument("-i", help = "path to the image (ex: test7.jpg)")
args = vars(ap.parse_args())

# 4. Buka gambar dan ubah ukuran 
image = cv2.imread(args["image"])
image = image_resize(image, height = 600)
rgbimage = image

# 5. Ubah warna dari BGR ke HSV
image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 6. Karena pemilihan warna banyak maka ulang setiap batasan warna  
for (lower, upper, name) in hsv_boundaries:
	# create NumPy arrays from the boundaries
	color = upper
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	# find the colors within the specified boundaries and apply
	# the mask
	mask = cv2.inRange(image, lower, upper)
	output = cv2.bitwise_and(image, image, mask = mask)

	#Tracking the Red Color
	kernel = np.ones((9,9),np.uint8)
	#mask = cv2.inRange(hsv, lower, upper)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
	mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

 	# only proceed if at least one contour was found
	if len(cnts) > 0 :
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size. Correct this value for your obect's size
		if radius > 0.5:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points

			print "color detected: " + name + " di (x=" + str(x-radius) + ", y=" + str(y-radius) + ")"
			draw_boxx(rgbimage, (int(x-radius), int(y-radius)), (int(x+radius),int(y+radius)), name, (0,0,0))

			#cv2.circle(image, (int(x), int(y)), int(radius), (0,0,255), 2)
			#cv2.putText(image," ball", (int(x-radius),int(y-radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,(0,0,0),2)

	# show the images
	cv2.imshow("images rgb", rgbimage)
	cv2.waitKey(100)

#pause
cv2.waitKey(2000)

