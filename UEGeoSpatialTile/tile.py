# pip3 install pillow
# pip3 install imageio
# pip3 install numpy
# pip3 install requests
 
from PIL import Image, ImageFilter
import numpy as np
import imageio
import os
import pathlib
import requests


MINUS = 2 ** 24
LIMIT = 2 ** 23
R = 2 ** 16
G = 2 ** 8
TILE_SZ = 256

max_h = 0
min_h = 0

def downloadTile(zoom, x, y):

	url = f'https://cyberjapandata.gsi.go.jp/xyz/dem5a_png/{zoom}/{x}/{y}.png'
	print(url)
	resp = requests.get(url)
	folder = 'color'
	fname = ''
	if resp.status_code == 200:

		os.makedirs(folder,exist_ok=True)
		contentType = resp.headers['Content-Type']
		fname = f'{zoom}_{x}_{y}.png'

		out_path = os.path.join(folder, fname)
		with open(out_path, 'wb') as out_path:
			out_path.write(resp.content)
			out_path.close()

	return fname

def downloadMatrixTiles(zoom, x, y, matrix):

	row = []
	col = []

	for _y in range(matrix):
		for _x in range(matrix):
			fname = downloadTile(zoom, x+_x, y+_y)
			col.append(fname)
		row.append(col)
		col = []
	
	print(row)
	return row



def makeGrayPngFiles( matrix ):
	
	row = []
	col = []
	sz = len(matrix)
	folder = 'gray'
	os.makedirs(folder,exist_ok=True)

	for _y in range(sz):
		for _x in range(sz):
			gray_fname = convGray16( folder, matrix[_y][_x],'png')
			col.append(gray_fname)
		row.append(col)
		col = []
	
	print(row)
	return row

def makeGrayPngFiles( matrix ):
	
	row = []
	col = []
	sz = len(matrix)
	folder = 'gray'
	os.makedirs(folder,exist_ok=True)

	for _y in range(sz):
		for _x in range(sz):
			gray_fname = convGray16( folder, matrix[_y][_x],'png')
			col.append(gray_fname)
		row.append(col)
		col = []
	
	print(row)
	return row

def convGray16(folder, path, ftype):

	fname = pathlib.Path(path)
	fname = fname.stem

	gray16 = np.arange(65536,dtype=np.uint16).reshape(TILE_SZ, TILE_SZ)

	if ftype == 'tiff':
		out_fname = f'./{folder}/gray_{fname}.tif'
		Image.fromarray(gray16).save(out_fname)
		tiff = Image.open(out_fname) 
		img2 = np.array(tiff)
		tiff.close()
	else:
		out_fname = f'./{folder}/gray_{fname}.png'
		imageio.imwrite(out_fname, gray16)
		img2 = imageio.imread(out_fname)

	try:
		img = Image.open(f'./color/{path}')
		print(img.format, img.size, img.mode)

		imgArray = np.array(img)
		for y in range(img.size[0]):
			for x in range(img.size[1]):
				r,g,b = imgArray[y][x]
				h = R*r + G*g + b
				if h < LIMIT:
					h = h
				elif h == LIMIT:
					h = 0 # NA
				elif h > LIMIT:
					h = (h - MINUS)

				h = h/100 # unit meter
				img2[y][x] = h
				#print(val)

		Image.fromarray(img2).save(out_fname)

	except Exception as ex:

		for y in range(256):
			for x in range(256):
				h = 0 # NA
				img2[y][x] = h
		Image.fromarray(img2).save(out_fname)

	return out_fname


def convGrayRatio(in_file, out_file):

	max_h = 0
	min_h = 0

	img = Image.open( f'{in_file}' )
	for y in range(img.height):
		for x in range(img.width):

			r,g,b = img.getpixel((x, y))
			h = R*r + G*g + b
			if h < LIMIT:
				h = h
			elif h == LIMIT:
				h = 0 # NA
			elif h > LIMIT:
				h = (h - MINUS) / 10

			if max_h < h:
				max_h = h
			# if min_h > h:
			# 	min_h = h


	gray16 = np.arange(img.width**2, dtype=np.uint16).reshape(img.width, img.height)
	imageio.imwrite(out_file, gray16)
	img2 = imageio.imread(out_file)

	for y in range(img.height):
		for x in range(img.width):

			r,g,b = img.getpixel((x, y))
			h = R*r + G*g + b
			if h < LIMIT:
				h = h
			elif h == LIMIT:
				h = 0 # NA
			elif h > LIMIT:
				h = (h - MINUS) / 10

			max_h
			img2[y][x] = (h/max_h)*65535

	Image.fromarray(img2).save(out_file)



def makeTile( files ,out_file):
	
	#n*n = 1,4,9,18,25...
	n = len(files)
	print(n) 

	gray16 = np.arange((TILE_SZ*n)**2,dtype=np.uint16).reshape(TILE_SZ*n,TILE_SZ*n)
	if out_file == None:
		out_fname = 'tile.png'
	else:
		out_fname = out_file

	imageio.imwrite(out_fname, gray16)
	img2 = imageio.imread(out_fname)

	row = 0
	for f in files:
		for _n in range(n):
			img = Image.open(f[_n])
			print(f[_n])
			print(_n)
			imgArray = np.array(img)

			for y in range(img.size[0]):
				for x in range(img.size[1]):
					h = imgArray[y][x]
					img2[y+(TILE_SZ*row)][x+(TILE_SZ*_n)] = h
		row = row + 1

	Image.fromarray(img2).save(out_fname)


def makeTileColor( folder, files, out_file):
	
	# n*n = 1,4,9,18,25...
	n = len(files)
	print(n) 
	dst = Image.new('RGB', (n*TILE_SZ, n*TILE_SZ))
	
	row = 0
	for f in files:
		for _n in range(n):
			try:
				img = Image.open( f'{folder}{f[_n]}' )
				dst.paste( img, ( _n*TILE_SZ, row*TILE_SZ))
			except Exception as ex:
				print(f'no file. {f[_n]}')
		
		row = row + 1

	if out_file == None:
		out_fname = 'tile_rgb.png'
	else:
		out_fname = out_file
	dst.save(out_fname)


	

# FUJI
# mat = downloadMatrixTiles(14, 14505, 6468, 4)
# makeTileColor('./color/', mat, 'fuji_color.png')
# convGrayRatio('fuji_color.png','fuji_gray.png')

# mat_gray = makeGrayPngFiles(mat)
# makeTile(mat_gray,'fuji.png')

# 津久井湖
#mat = downloadMatrixTiles(14, 14529, 6455, 4)
# mat = downloadMatrixTiles(14, 14528, 6455, 8)
# mat_gray = makeGrayPngFiles(mat)
# makeTile( mat_gray, 'sagami_16.png')

# mat = downloadMatrixTiles(14, 14528, 6459, 4)
# mat_gray = makeGrayPngFiles(mat)
# makeTile( mat_gray, 'sagami2.png')

# 三宅島
mat = downloadMatrixTiles(14, 14539, 6537, 6)
makeTileColor('./color/', mat, 'miyake_color.png')
convGrayRatio('miyake_color.png','miyake_gray.png')

# mat_gray = makeGrayPngFiles(mat)
# makeTile(mat_gray)

# 浅間山
# mat = downloadMatrixTiles(14, 14494, 6409, 6)
# mat_gray = makeGrayPngFiles(mat)
# makeTile(mat_gray)

#マラソン
# mat = downloadMatrixTiles(14, 14492, 6402, 4)
# mat_gray = makeGrayPngFiles(mat)
# makeTile(mat_gray)

