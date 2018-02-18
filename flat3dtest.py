import flat3d as f3d
import cairocffi
import io
import moviepy.editor as mpy
import numpy as np
import ease
import xform as xf
from greek import *
from colour import *

W,H = 1920,1080 # width, height, in pixels
duration = 1 # duration of the clip, in seconds

scale = 1.0/4
# scale = 4
# scale = 1
# scale = 8

def make_surface(t):
	# print t
	myease = ease.fancyBezierEase
	scene = f3d.Scene2d(w=W, h=H, scale=scale, transform=xf.M(xf.translate2d(0, H), xf.scale2d(1, -1), xf.rotate2d(xf.rad(30*t))))
	scene.addElem(f3d.Polyline2d([(0,0), (500,600), (500, 800)], stroke=(0,0,1), width=5))
	scene.addElem(f3d.Polygon2d([(50+50*myease(t),50+50*myease(t)), (70+50*myease(t),60+50*myease(t)), (30+50*myease(t), 100+50*myease(t))], fill=(1,0,0)))
	scene.addElem(f3d.Polygon2d([(100+200*myease(t),100+200*myease(t)), (70+200*myease(t),60+200*myease(t)), (30+200*myease(t), 100+200*myease(t))], fill=(1,0,0)))
	scene.addElem(f3d.Dot2d((500-10*myease(t), 600-10*myease(t)), stroke=(0, 1, 1), width=5))
	scene.addElem(f3d.Text2d(position=(W/2,H/2), fill=colour['Green']['300'], txt="hello world! %s" % (greek['theta']), fontfamily="Neo Euler", fontsize=40))
	return scene.get_gizeh_surface()

f3d.export_vid('coolMyEffects', make_surface, duration)
# f3d.export_img('coolMyEffects', make_surface(0))