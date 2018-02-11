import gizeh

# initialize surface
surface = gizeh.Surface(width=320, height=260) # in pixels

# Now make a shape and draw it on the surface
circle = gizeh.circle(r=30, xy= [40,40], fill=(1,1,1))
circle.draw(surface)

# Now export the surface
surface.get_npimage() # returns a (width x height x 3) numpy array
surface.write_to_png("circle.png")
