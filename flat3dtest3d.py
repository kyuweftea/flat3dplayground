import flat3d as f3d
import xform as xf

W = 1920
H = 1080
duration = 1

# scale = 1.0/4
scale = 1.0
# scale = 4.0

def makescene(t):
	camera = f3d.Camera3d(position=(0,0,0), direction=(0,1,0), up=(0,0,1), fov=xf.rad(90), aspect=1)
	scene = f3d.Scene3d(w2d=W, h2d=H, scale2d=scale, camera=camera)
	scene.addElem(f3d.Line3d(points=[(-0.5,0.25,-0.6), (0.5,2,1)], stroke=(0,1,1), width=5))
	scene.addElem(f3d.Triangle3d(points=[(-1,1,-0.5), (1*t + 0*(1-t), 1*t + 0.25*(1-t), 0*t + -1*(1-t)), (0,1,1)], fill=(1,1,0)))
	scene.addElem(f3d.Dot3d(point=(-0.5,2*t,0.5), stroke=(0,1,1), width=5))
	scene.addElem(f3d.Triangle3d(points=[(-1,2,1), (0,0,-1), (1,1,0.5)], fill=(1,0,0)))
	return scene

f3d.export_vid('cool3dEffects', makescene, duration)
# f3d.export_img('cool3dEffects', makescene(0))