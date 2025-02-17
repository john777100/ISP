import numpy as np


import scipy.misc
import csv

PROCESS_ROW = 4
WIN_RADIUS = 1
PIC_ROW = 12
PIC_COL = 8

def temp_get_picture_numpy(mode="easy"):
	if(mode == "easy"):
		np.random.seed(0)
		image = np.random.randint(256, size = (PIC_ROW, PIC_COL))
	return image

def temp_append(rgb):
	print("rgb shape", rgb.shape)
	temp = np.concatenate((rgb[0:1,:,:],rgb),axis=0)
	print("temp shape", temp.shape)
	for i in range(1):
		print(temp[:,:,i])
	temp = np.concatenate((temp,[temp[-1,:,:]]),axis=0)
	print("temp shape", temp.shape)
	for i in range(1):
		print(temp[:,:,i])
	temp = np.concatenate((temp[:,0:1,:],temp),axis=1)
	print("temp shape", temp.shape)
	for i in range(1):
		print(temp[:,:,i])
	temp = np.concatenate((temp,temp[:,-1,:].reshape(temp.shape[0],1,3)),axis=1)
	print("temp shape", temp.shape)
	for i in range(1):
		print(temp[:,:,i])
	return temp

def temp_gen_demosaic_input_pattern(bayer, file_name='demosaic_input.pat'):
	with open(file_name, "w") as writer:
		for i in range(0, bayer.shape[0]-4 ,4):
			for j in range(bayer.shape[1]):
				for k in range(i,i+8,1):
					writer.write("{0:b}".format(bayer[k,j]).zfill(8)+'\n')

def temp_gen_denoise_input_pattern(rgb, file_name='denoise_input.pat'):
	with open(file_name, "w") as writer:
		for i in range(0,rgb.shape[0],PROCESS_ROW):
			big_row = temp_append(rgb)
			for j in range(big_row.shape[1]):
				for k in range(big_row.shape[0]):
					writer.write("{0:b}".format(big_row[k,j,0]).zfill(8)+" "+"{0:b}".format(big_row[k,j,1]).zfill(8)+" "+"{0:b}".format(big_row[k,j,2]).zfill(8)+'\n')

def temp_demosaic(bay, debug=0):
	r = np.zeros((bay.shape))
	g = np.zeros((bay.shape)) 
	b = np.zeros((bay.shape)) 
	last_row = bay.shape[0]
	last_col = bay.shape[1]
	for i in range(bay.shape[0]):
		for j in range(bay.shape[1]):
			if(i%2==0 and j%2==0): # red pixel
				r[i][j] = bay[i][j]
				if(j== last_col-1):
					assert 0 , "ERROR! bay pattern error"
				elif(i== last_row-1):
					assert 0 , "ERROR! bay pattern error"
				elif(i== 0 and j== 0):
					g[i][j] = (bay[i+1][j] + bay[i][j+1]) //2
					b[i][j] = bay[i+1][j+1]
				elif(i==0):
					g[i][j] = (bay[i][j-1] + bay[i][j+1] + bay[i+1][j]) //3
					b[i][j] = (bay[i+1][j-1] + bay[i+1][j+1]) //2
				elif(j==0):
					g[i][j] = (bay[i-1][j] + bay[i][j+1] + bay[i+1][j]) //3
					b[i][j] = (bay[i-1][j+1] + bay[i+1][j+1]) //2
				else:
					g[i][j] = (bay[i-1][j] + bay[i+1][j] + bay[i][j-1] + bay[i][j+1])//4
					b[i][j] = (bay[i-1][j-1] + bay[i+1][j+1] + bay[i+1][j-1] + bay[i-1][j+1])//4
			elif(i%2==1 and j%2==1): #blue pixel
				b[i][j] = bay[i][j]
				if(i==0):
					assert 0 , "ERROR! bay pattern error"
				elif(j==0):
					assert 0 , "ERROR! bay pattern error"
				elif(i==last_row-1 and j==last_col-1):
					r[i][j] = bay[i-1][j-1]
					g[i][j] = (bay[i-1][j] + bay[i][j-1]) //2
				elif(j==last_col-1):
					r[i][j] = (bay[i-1][j-1] + bay[i+1][j-1]) //2
					g[i][j] = (bay[i-1][j] + bay[i][j-1] + bay[i+1][j]) //3
				elif(i==last_row-1):
					r[i][j] = (bay[i-1][j-1] + bay[i-1][j+1]) //2
					g[i][j] = (bay[i-1][j] + bay[i][j-1] + bay[i][j+1]) //3
				else:
					r[i][j] = (bay[i-1][j-1] + bay[i+1][j+1] + bay[i+1][j-1] + bay[i-1][j+1])//4
					g[i][j] = (bay[i-1][j] + bay[i+1][j] + bay[i][j-1] + bay[i][j+1])//4
			else: # green pixel
				g[i][j] = bay[i][j]
				if(i==0):
					b[i][j] = bay[i+1][j]
				elif(j==0):
					b[i][j] = bay[i][j+1]
				elif(j==last_col-1):
					b[i][j] = (bay[i+1][j] + bay[i-1][j])//2
				elif(i==last_row-1):
					b[i][j] = (bay[i][j+1] + bay[i][j-1])//2
				if(i==last_row-1):
					r[i][j] = bay[i-1][j]
				elif(j==last_col-1):
					r[i][j] = bay[i][j-1]
				elif(j==0):
					r[i][j] = (bay[i+1][j] + bay[i-1][j])//2
				elif(i==0):
					r[i][j] = (bay[i][j+1] + bay[i][j-1])//2
				else:
					if(i%2==1 and j%2==0):
						r[i][j] = (bay[i-1][j] + bay[i+1][j])//2
						b[i][j] = (bay[i][j-1] + bay[i][j+1])//2
					else:
						b[i][j] = (bay[i-1][j] + bay[i+1][j])//2
						r[i][j] = (bay[i][j-1] + bay[i][j+1])//2
	return np.stack([r[1:last_row-1,1:last_col-1],g[1:last_row-1,1:last_col-1],b[1:last_row-1,1:last_col-1]],axis=2).astype(int)

def temp_denoise(rgb):
	result = np.zeros(rgb.shape)
	for i in range(WIN_RADIUS,rgb.shape[0]-WIN_RADIUS):
		for j in range(WIN_RADIUS,rgb.shape[1]-WIN_RADIUS):
			result[i-1,j-1,0] = np.average(rgb[i-1:i+2,j-1:j+2,0])
			result[i-1,j-1,1] = np.average(rgb[i-1:i+2,j-1:j+2,1])
			result[i-1,j-1,2] = np.average(rgb[i-1:i+2,j-1:j+2,2])

	return result[:-2,:-2,:].astype(int)

def temp_gen_denoise_golden_pattern(rgb, file_name='denoise_golden.pat'):
	with open(file_name, "w") as writer:
		for k in range(0,rgb.shape[0],4):
			for i in range(rgb.shape[1]):
				for j in range(k,k+4,1):
					writer.write("{0:b}".format(rgb[j,i,0]).zfill(8)+" "+"{0:b}".format(rgb[j,i,1]).zfill(8)+" "+"{0:b}".format(rgb[j,i,2]).zfill(8)+'\n')



rgb = temp_get_picture_numpy()
print("bayer\n",rgb)
dem_rgb = temp_demosaic(rgb)
print("demosaic")
for i in range(3):
	print(dem_rgb[:,:,i])
golden_rgb = temp_denoise(dem_rgb)
print("denoise")
for i in range(3):
	print(golden_rgb[:,:,i])
temp_gen_denoise_golden_pattern(golden_rgb)
temp_gen_demosaic_input_pattern(rgb)
