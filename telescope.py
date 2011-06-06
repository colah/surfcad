from surfcad import *

def screw(t):
	t = 3*t
	t = fmod(t,2*pi)
	t = 2*t
	if t < pi:
		return sin(t)
	else:
		return 0

F = STLFile("telescope-mirrortest.stl")

#mirror = circular_surface(lambda r,t: r**2/60+20, 30) # Parabolic Mirror
#side = cylinderical_surface(lambda t,h: 3*screw(t+h/50) + 30, 35) #Side with ridges to screw in to main tube
#handle = cylinderical_surface(lambda t,h: (20*cos(t),5*sin(t)), 10) #Eliptical dent in bottom for screwing in and out

#F.add(mirror.surface() ) 
#F.add(side.surface() ) 
#F.add(join(side.top_loop(), mirror.outer_loop() ) )

#F.add(handle.surface() )
#F.add(handle.top_loop().close() )

#F.add(join(side.bottom_loop(), handle.bottom_loop() ) )

mirror = circular_surface(lambda r,t: r**2/120+2.5, 30) # Parabolic Mirror
side = cylinderical_surface(lambda t,h: 30, 10)

F.add(mirror.surface() ) 
F.add(side.surface() ) 
F.add(side.bottom_loop().close())

F.end()
