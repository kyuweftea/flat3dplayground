import numpy as np

def scale2d(x, y=None):
	if (y is None):
		y = x
	return [[x, 0, 0],
	        [0, y, 0],
	        [0, 0, 1]]

def translate2d(x, y):
	return [[1, 0, x],
	        [0, 1, y],
	        [0, 0, 1]]

def rotate2d(a):
	return [[ np.cos(a), -np.sin(a), 0],
	        [ np.sin(a),  np.cos(a), 0],
	        [         0,          0, 1]]

def rad(a):
	return np.deg2rad(a)

def scale3d(x, y=None, z=None):
	if (y is None):
		y = x
		if (z is None):
			z = x
	elif (z is None):
		z = 1
	return [[x, 0, 0, 0],
	        [0, y, 0, 0],
	        [0, 0, z, 0],
	        [0, 0, 0, 1]]

def translate3d(x, y, z):
	return [[1, 0, 0, x],
	        [0, 1, 0, y],
	        [0, 0, 1, z],
	        [0, 0, 0, 1]]

def rotateX3d(a):
	return [[         1,          0,          0, 0],
	        [         0,  np.cos(a), -np.sin(a), 0],
	        [         0,  np.sin(a),  np.cos(a), 0],
	        [         0,          0,          0, 1]]

def rotateY3d(a):
	return [[ np.cos(a),          0,  np.sin(a), 0],
	        [         0,          1,          0, 0],
	        [-np.sin(a),          0,  np.cos(a), 0],
	        [         0,          0,          0, 1]]

def rotateZ3d(a):
	return [[ np.cos(a), -np.sin(a),          0, 0],
	        [ np.sin(a),  np.cos(a),          0, 0],
	        [         0,          0,          0, 0],
	        [         0,          0,          0, 1]]

def m(xf, p, suffix=1):
	_p = list(p)
	_p.append(suffix)
	return np.matmul(xf, _p)[:len(p)]

def M(*xf_s):
	result = np.identity(len(xf_s[0]))
	for xf in xf_s:
		result = np.matmul(result, xf)
	return result