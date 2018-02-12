import gizeh as gz
import cairocffi as cr
import moviepy.editor as mpy

class Element2d(object):
	def __init__(self):
		pass
	def isPolygon(self):
		return False
	def isPolyline(self):
		return False
	def isDot(self):
		return False

class Polygon2d(Element2d):
	def __init__(self, points, fill=None):
		super(Polygon2d, self).__init__()
		self.points = points
		self.fill = fill
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
	def isPolyline(self):
		return True

class Dot2d(Element2d):
	def __init__(self, point, stroke=None, width=None):
		super(Dot2d, self).__init__()
		self.point = point
		self.stroke = stroke
		self.width = width
	def isDot(self):
		return True

class SurfaceAliased(gz.Surface, object):
	def __init__(self, scale, width, height):
		super(SurfaceAliased, self).__init__(width=width, height=height)
		self.scale = scale;
	def get_new_context(self):
		cxt = gz.Surface.get_new_context(self)
		cxt.set_antialias(cr.ANTIALIAS_NONE)
		return cxt

class Scene2d(object):
	def __init__(self, w, h, scale=1):
		self.w = scale*w
		self.h = scale*h
		self.elements = []
		self.scale = scale
	def addElem(self, elem):
		if (not (elem.isPolygon() or elem.isPolyline() or elem.isDot())):
			raise TypeError("cannot add element to scene")
		self.elements.append(elem)
	def get_gizeh_surface(self):
		surface = SurfaceAliased(scale=self.scale, width=int(self.w), height=int(self.h))
		for elem in self.elements:
			if (elem.isPolygon()):
				points = list(map(lambda x: (self.scale*x[0],self.scale*x[1]), elem.points))
				polygon = gz.polyline(points, fill=elem.fill, close_path=True)
				polygon.draw(surface)
			elif (elem.isPolyline()):
				points = list(map(lambda x: (self.scale*x[0],self.scale*x[1]), elem.points))
				polyline = gz.polyline(points, stroke=elem.stroke, stroke_width=self.scale*elem.width, close_path=elem.closed, line_cap=('butt' if elem.capbutt else 'round'))
				polyline.draw(surface)
			elif (elem.isDot()):
				dot = gz.circle(r=self.scale*elem.width/2.0, xy=(self.scale*elem.point[0],self.scale*elem.point[1]), fill=elem.stroke)
				dot.draw(surface)
			else:
				raise TypeError("cannot make gizeh element")
		return surface

def export_vid(name, make_surface, duration, fps=24):
	d = {
		't_prev': -1.0,
		'im': None
	}

	scale = make_surface(0).scale

	def update(t):
		if (t != d['t_prev']):
			surface = make_surface(t)
			d['im'] = surface.get_npimage(transparent=True)
			d['t_prev'] = t

	def make_frame(t):
		update(t)
		return d['im'][:,:,:3]

	def make_mask(t):
		update(t)
		return d['im'][:,:,3]/255.0

	mask = mpy.VideoClip(make_mask, duration=duration, ismask=True).resize(1.0/scale)
	clip = mpy.VideoClip(make_frame, duration=duration).set_mask(mask).resize(1.0/scale)
	clip.write_videofile("%s.mov" % name, fps=fps, codec='png', with_mask=True)
