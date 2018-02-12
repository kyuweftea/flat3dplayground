import numpy as np

# !!! BUGGY !!!
# returns cartesian curve that approximates bezier with P0(0,0), P1(x1,y1), P2(x2,y2), P3(1,1)
def bezierEaser(x1, y1, x2, y2):
	def ease(x):

		# find the parameter t that results in the given x
		t_s = np.roots([3 * (x1 - x2) + 1, 3 * (x2 - (2 * x1)), 3 * x1, -x])
		t = t_s[0]
		for t_i in t_s:
			if np.imag(t_i) **2 < np.imag(t) **2:
				t = t_i
		t = np.real(t)

		# evaluate the y coord with the parameter t
		y = np.polyval([3 * (y1 - y2) + 1, 3 * y2 - 6 * y1, 3 * y1, 0], t)
		return y

	return ease

def fancyBezierEase(t):
	return bezierEaser(1, 0, 0.5, 1)(t)

def smoothBezierEase(t):
	degree = 0.3334
	return bezierEaser(degree, 0, 1 - degree, 1)(t)

def sinEase(t):
	return 0.5 * (1 - np.cos(np.pi * t))

def linEase(t):
	return t

def quadEaser(out=False):
	def ease(t):
		if (out):
			return -(1-t)**2 + 1
		else:
			return t**2
	return ease

def quadInEase(t):
	return quadEaser(False)(t)

def quadOutEase(t):
	return quadEaser(True)(t)

def draw(ease):
	print '-'*80
	for x in map(lambda x: x/20.0, range(21)):
		# print "{:10.3f}".format(x), ease(x)
		print 'o'*int(80*ease(x))
	print '-'*80

# fancy
# draw(fancyBezierEase)

# in-out
# draw(smoothBezierEase)

# sinusoidal
# draw(sinEase)

#linear
# draw(linEase)

# quadratic in
# draw(quadInEase)

# quadratic out
# draw(quadOutEase)
