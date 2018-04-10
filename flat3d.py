import numpy as np
import gizeh as gz
import cairocffi as cr
import moviepy.editor as mpy
import xform as xf

class Scene(object):
	def __init__(self):
		pass

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

class Scene2d(Scene):
	def __init__(self, w, h, scale=1, transform=np.identity(3)):
		super(Scene3d, self).__init__()
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

class Element3d(object):
	def __init__(self):
		pass
	def tf(self, tf):
		pass
	def isTriangle(self):
		return False
	def isLine(self):
		return False
	def isDot(self):
		return False

class Triangle3d(Element3d):
	def __init__(self, points, fill=None):
		super(Triangle3d, self).__init__()
		if (len(points) != 3):
			raise ValueError("3D Triangles need 3 points, but %d were given" % len(points))
		self.points = points
		self.fill = fill
	def tf(self, tf):
		self.points = list(map(lambda x: xf.m(tf,x), self.points))
		return self
	def isTriangle(self):
		return True

class Line3d(Element3d):
	def __init__(self, points, fill=None):
		super(Line3d, self).__init__()
		if (len(points) != 2):
			raise ValueError("3D Lines need 2 points, but %d were given" % len(points))
		self.points = points
		self.fill = fill
	def tf(self, tf):
		self.points = list(map(lambda x: xf.m(tf,x), self.points))
		return self
	def isLine(self):
		return True

class Dot3d(Element3d):
	def __init__(self, point, fill=None):
		super(Dot3d, self).__init__()
		self.point = point
		self.fill = fill
	def tf(self, tf):
		self.point = xf.m(tf, self.point)
		return self
	def isDot(self):
		return True

class Camera3d(object):
	def __init__(self, position, direction, up, fov, aspect):
		self.position = position
		self.direction = direction
		self.up = up
		self.fov = fov
		self.aspect = aspect

class Tree(object):
	def __init__(self, data=None, left=None, right=None):
		self.data = data
		self.left = left
		self.right = right

class GeoNode(object):
	def __init__(self, elem3d, clipper):
		if (elem3d.isTriangle()):
			self.plane = xf.Plane(elem3d.points[0],
			                      xf.cross((elem3d.points[1][0] - elem3d.points[0][0], elem3d.points[1][1] - elem3d.points[0][1], elem3d.points[1][2] - elem3d.points[0][2]),
			                   	           (elem3d.points[2][0] - elem3d.points[2][0], elem3d.points[2][1] - elem3d.points[2][1], elem3d.points[2][2] - elem3d.points[2][2])))
			self.elem = Polyline2d([(elem3d.points[0][0], elem3d.points[0][1]), (elem3d.points[1][0], elem3d.points[1][1]), (elem3d.points[2][0], elem3d.points[2][1])],
				                   stroke=(1,0,0))
		elif (elem3d.isLine()):
			linedir = (elem3d.points[1][0] - elem3d.points[0][0], elem3d.points[1][1] - elem3d.points[0][1], elem3d.points[1][2] - elem3d.points[0][2])
			zaxis = (0, 0, 1)
			self.plane = xf.Plane(elem3d.points[0],
			                      xf.cross(xf.cross(linedir, zaxis), linedir))
			self.elem = Polyline2d([(elem3d.points[0][0], elem3d.points[0][1]), (elem3d.points[1][0], elem3d.points[1][1])]
			                       stroke=(1,1,1), width=2)
		elif (elem3d.isDot()):
			self.plane = xf.Plane(elem3d.point, (0, 0, 1))
			self.elem = Dot2d((elem3d.point[0], elem3d.point[1]), stroke=(0,1,0), width=2)
		else
			raise TypeError("not 3D element")
		self.elem.clip(clipper)
	def hasGeometry(self):
		if (self.elem.isPolygon()):
			return len(self.elem.points) > 0
		elif (self.elem.isPolyline()):
			return len(self.elem.points) > 0
		elif (self.elem.isDot()):
			return not self.elem.clipped
		else
			raise TypeError("not 2D element")

class Scene3d(Scene):
	def __init__(self, w2d, h2d, scale2d=1, transform=np.identity(4), camera=None):
		super(Scene3d, self).__init__()
		self.w2d = w2d
		self.h2d = h2d
		self.scale2d = scale2d
		self.transform = transform
		self.elements = []
		self.camera = camera
	def addElem(self, elem):
		if (not (elem.isTriangle() or elem.isLine() or elem.isDot())):
			raise TypeError("cannot add element to scene")
		self.elements.append(elem)
	def insertToTree(tree, elem3d):
		# do this
	def get_gizeh_surface(self):
		tf = self.transform
		v_x = xf.norm3d(xf.cross(self.camera.direction, self.camera.up))
		v_y = xf.norm3d(xf.cross(v_x, self.camera.direction))
		v_z = xf.norm3d(xf.cross(v_x, v_y))
		v_r_inv = [[v_x[0], v_y[0], v_z[0], 0],
		           [v_x[1], v_y[1], v_z[1], 0],
		           [v_x[2], v_y[2], v_z[2], 0],
		           [     0,      0,      0, 1]]
		v = xf.M(xf.translate3d(-self.camera.position[0], -self.camera.position[1], -self.camera.position[2]), np.linalg.inv(v_r_inv))
		scene2d = Scene2d(w=self.w2d, h=self.h2d, scale=scale2d, transform=xf.M(xf.translate2d(self.w2d/2.0, self.h2d/2.0), xf.scale2d(self.w2d/2.0, -self.h2d/2.0)))
		
		# make tree
		for elem in self.elements:
			elem.tf(tf)
			elem.tf(v)


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
