import gizeh
import moviepy.editor as mpy
import numpy as np

W,H = 1920,1080 # width, height, in pixels
duration = 2 # duration of the clip, in seconds

def make_surface(t):
    surface = gizeh.Surface(W,H)
    radius = W*(1+ (t*(duration-t))**2 )/6
    circle = gizeh.circle(radius, xy = (W/2,H/2), fill=(1,0,0))
    circle.draw(surface)
    return surface

def make_frame(t):
    surface = make_surface(t)
    return surface.get_npimage()

def make_mask(t):
    surface = make_surface(t)
    return surface.get_npimage(transparent=True)[:,:,3]/255.0

# np.set_printoptions(threshold=np.nan)
# print make_mask(0)
# quit()

imagemask = mpy.ImageClip("pentmask.png", ismask=True)

mask = mpy.VideoClip(make_mask, duration=duration, ismask=True)
clip = mpy.VideoClip(make_frame, duration=duration)

# np.set_printoptions(threshold=np.nan)
# print imagemask.get_frame(0)
# quit()

# np.set_printoptions(threshold=np.nan)
# print mask.get_frame(0)
# quit()


print type(mask)
print mask.ismask

clip = clip.set_mask(mask)


print type(clip.mask)
# quit()

# clip.write_gif("circle.gif",fps=15, opt="OptimizePlus", fuzz=10)
# clip.write_videofile('coolTextEffects.mov',fps=24,codec='png')
clip.write_videofile('coolTextEffects.mov',fps=24,codec='png',with_mask=True)