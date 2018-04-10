import numpy as np
import gizeh as gz
import cairocffi as cr
import moviepy.editor as mpy
import xform as xf

class Clipper(object):
	def __init__(self):
		pass
	def contains(self, point):
		return True
	def intersect(self, pa, pb):
		return None
	def intersect(self, pa, pb):
		return None
	def isLineClipper(self):
		return False

class LineClipper(Clipper):
	def __init__(self, linepnt, linedir):
		super(Clipper, self).__init__()
		self.linepnt = linepnt
		self.linedir = linedir
	def contains(self, point):
		topoint = (point[0] - self.linepnt[0], point[1] - self.linepnt[1])
		return 0 >= self.linedir[0]*topoint[1] - topoint[0]*self.linedir[1]
	def intersect(self, pa, pb):
		tob = (pb[0] - pa[0], pb[1] - pa[1])
		t = (self.linedir[0]*(pa[1] - self.linepnt[1]) - self.linedir[1]*(pa[0] - self.linepnt[0])) / (self.linedir[1]*tob[0] - self.linedir[0]*tob[1])
		return (pa[0] + t*tob[0], pa[1] + t*tob[1])
	def isLineClipper(self):
		return True

class InverseClipper(Clipper):
	def __init__(self, inv):
		super(Clipper, self).__init__()
		self.inv = inv
	def contains(self, point):
		return not self.inv.contains(point)
	def intersect(self, pa, pb):
		return self.inv.intersect(pa, pb)
	def isLineClipper(self):
		return self.inv.isLineClipper()

class Element2d(object):
	def __init__(self):
		pass
	def tf(self, tf):
		pass
	def clip(self, clipper):
		pass
	def isPolygon(self):
		return False
	def isPolyline(self):
		return False
	def isDot(self):
		return False
	def isText(self):
		return False

class Polygon2d(Element2d):
	def __init__(self, points, fill=None):
		super(Polygon2d, self).__init__()
		self.points = points
		self.fill = fill
	def tf(self, tf):
		self.points = list(map(lambda x: xf.m(tf,x), self.points))
		return self
	def clip(self, clipper):
		if (clipper.isLineClipper()):
			if (len(self.points) > 0):
				newpoints = []
				S = self.points[-1]
				for E in self.points:
					if (clipper.contains(E)):
						if (not clipper.contains(S)):
							newpoints.append(clipper.intersect(S, E))
						newpoints.append(E)
					elif (clipper.contains(S)):
						newpoints.append(clipper.intersect(S, E))
					S = E
				self.points = newpoints
		return self
	def isPolygon(self):
		return True

class Polyline2d(Element2d):
	def __init__(self, points, stroke=None, width=None, closed=False, capbutt=False):
		super(Polyline2d, self).__init__()
		self.points = points
		self.stroke = stroke
		self.width = width
		self.closed = closed
		self.capbutt = capbutt
	def tf(self, tf):
		self.points = list(map(lambda x: xf.m(tf,x), self.points))
		return self
	def clip(self, clipper):
		if (clipper.isLineClipper()):
			# note: only works with single lines
			if (len(self.points) > 0):
				newpoints = []
				S = self.points[-1]
				for E in self.points:
					if (clipper.contains(E)):
						if (not clipper.contains(S)):
							newpoints.append(clipper.intersect(S, E))
						newpoints.append(E)
					elif (clipper.contains(S)):
						newpoints.append(clipper.intersect(S, E))
					S = E
				self.points = newpoints
		return self
	def isPolyline(self):
		return True

class Dot2d(Element2d):
	def __init__(self, point, stroke=None, width=None):
		super(Dot2d, self).__init__()
		self.point = point
		self.stroke = stroke
		self.width = width
		self.clipped = False
	def tf(self, tf):
		self.point = xf.m(tf, self.point)
		return self
	def clip(self, clipper):
		if (not clipper.contains(self.point)):
			self.clipped = True
		return self
	def isDot(self):
		return True

class Text2d(Element2d):
	def __init__(self, position, fill, txt, fontfamily, fontsize, bold=False, v_align="center", h_align="center"):
		super(Text2d, self).__init__()
		self.position = position
		self.fill = fill
		self.txt = txt
		self.fontfamily = fontfamily
		self.fontsize = fontsize
		self.fill = fill
		self.bold = bold
		self.v_align = v_align
		self.h_align = h_align
	def tf(self, tf):
		self.position = xf.m(tf, self.position)
		return self
	def isText(self):
		return True

class SurfaceAliased(gz.Surface, object):
	def __init__(self, scale, width, height):
		super(SurfaceAliased, self).__init__(width=width, height=height)
		self.scale = scale;
	def get_new_context(self):
		cxt = super(SurfaceAliased, self).get_new_context()
		cxt.set_antialias(cr.ANTIALIAS_NONE)
		return cxt

class Scene2d(object):
	def __init__(self, w, h, scale=1, transform=np.identity(3)):
		self.w = scale*w
		self.h = scale*h
		self.elements = []
		self.scale = scale
		self.transform = transform
	def addElem(self, elem):
		if (not (elem.isPolygon() or elem.isPolyline() or elem.isDot() or elem.isText())):
			raise TypeError("cannot add element to scene")
		self.elements.append(elem)
	def get_gizeh_surface(self):
		surface = SurfaceAliased(scale=self.scale, width=int(self.w), height=int(self.h))
		tf = np.matmul(xf.scale2d(self.scale), self.transform)
		for elem in self.elements:
			elem.tf(tf)
			gzelem = None
			if (elem.isPolygon()):
				if (len(elem.points) > 0):
					gzelem = gz.polyline(elem.points, fill=elem.fill, close_path=True)
			elif (elem.isPolyline()):
				if (len(elem.points) > 0):
					gzelem = gz.polyline(elem.points, stroke=elem.stroke, stroke_width=self.scale*elem.width, close_path=elem.closed, line_cap=('butt' if elem.capbutt else 'round'))
			elif (elem.isDot()):
				if (not elem.clipped):
					gzelem = gz.circle(r=self.scale*elem.width/2.0, xy=elem.point, fill=elem.stroke)
			elif (elem.isText()):
				gzelem = gz.text(xy=elem.position, fill=elem.fill, txt=elem.txt, fontfamily=elem.fontfamily, fontsize=self.scale*elem.fontsize, fontweight=("bold" if elem.bold else "normal"), v_align=elem.v_align, h_align=elem.h_align)
			else:
				raise TypeError("cannot make gizeh element")
			if (not (gzelem is None)):
				gzelem.draw(surface)
		return surface

def export_vid(name, make_scene, duration, fps=24):
	t_prev = [-1.0]
	im = [None]

	def make_surface(t):
		return make_scene(t).get_gizeh_surface()

	scale = make_surface(0).scale

	def update(t):
		if (t != t_prev[0]):
			surface = make_surface(t)
			im[0] = surface.get_npimage(transparent=True)
			t_prev[0] = t

	def make_frame(t):
		update(t)
		return im[0][:,:,:3]

	def make_mask(t):
		update(t)
		return im[0][:,:,3]/255.0

	mask = mpy.VideoClip(make_mask, duration=duration, ismask=True).resize(1.0/scale)
	clip = mpy.VideoClip(make_frame, duration=duration).set_mask(mask).resize(1.0/scale)
	clip.write_videofile("%s.mov" % name, fps=fps, codec='png', with_mask=True)

def export_img(name, scene):
	surface = scene.get_gizeh_surface()
	filename = "%s.png" % name
	surface.write_to_png(filename)
	print "[flat3D]", "Image ready:", filename
