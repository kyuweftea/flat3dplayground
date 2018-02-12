import flat3d as f3d
import cairocffi
import io
import moviepy.editor as mpy

W,H = 1920,1080 # width, height, in pixels
duration = 1 # duration of the clip, in seconds

# scale = 1.0/4
scale = 4
# scale = 1
# scale = 8

def make_surface(t):
	# print t
	scene = f3d.Scene2d(w=W, h=H, scale=scale)
	scene.addElem(f3d.Polyline2d([(0,0), (500,600), (500, 800)], stroke=(0,0,1), width=5))
	scene.addElem(f3d.Polygon2d([(50,50), (70,60), (30, 100)], fill=(1,0,0)))
	scene.addElem(f3d.Polygon2d([(100,100), (70,60), (30, 100)], fill=(1,0,0)))
	scene.addElem(f3d.Dot2d((500, 600), stroke=(0, 1, 1), width=5))
	return scene.get_gizeh_surface()

f3d.export_vid('coolMyEffects', make_surface, duration)