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

mask = mpy.VideoClip(make_mask, duration=duration, ismask=True)
clip = mpy.VideoClip(make_frame, duration=duration)

clip = clip.set_mask(mask)

# the with_mask parameter is not on moviepy's master
# there's a pull request for it, but no one seems to be giving it attention
# i'm using a fork of moviepy with the pull request changes made
# https://github.com/Zulko/moviepy/pull/679
clip.write_videofile('coolTextEffects.mov',fps=24,codec='png',with_mask=True)