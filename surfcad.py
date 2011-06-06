
from math import *

resolution = 0.1 #must be float


def cross(a,b):
	return ( a[1]*b[2] - b[1]*a[2], a[2]*b[0] - b[2]*a[0], a[0]*b[1] - b[0]*a[1] )

def dot(a,b):
	return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

def norm(a):
	return (a[0]**2+a[1]**2+a[2]**2)**0.5

def scale(a,v):
	return (a*v[0], a*v[1], a*v[2])

def add(u,v):
	return (u[0]+v[0],u[1]+v[1],u[2]+v[2])

def srange(S):
	return map(lambda x: x*S[2], range(int(floor(S[0]/S[2])),int(floor(S[1]/S[2]))+1))

class STLFile:
	def __init__(self,fname):
		self.out = open(fname,'w')
		self.out.write("solid Default\n")
	def end(self):
		self.out.write("endsolid Default")
		self.out.close()
	def add_triangle(self, i):
		nav = scale(-1/3.,add(add(i[0],i[1]),i[2]))
		n = cross(add(i[1],nav),add(i[2],nav))
		un = norm(n)
		if un == 0:
			return
		n = (n[0]/un,n[1]/un,n[2]/un)
		self.out.write("  facet normal %s %s %s\n" % n)
		self.out.write("    outer loop\n")
		self.out.write("      vertex %s %s %s\n" % i[0])
		self.out.write("      vertex %s %s %s\n" % i[1])
		self.out.write("      vertex %s %s %s\n" % i[2])
		self.out.write("    endloop\n")
		self.out.write("  endfacet\n")
	def add_square(self, sq):
		self.add_triangle((sq[0],sq[1],sq[2]))
		self.add_triangle((sq[0],sq[2],sq[3]))
	def add(self, surfgen):
		for i in surfgen:
			if len(i) == 3:
				self.add_triangle(i)
			elif len(i) == 4:
				self.add_square(i)
			else:
				print "unknown primitive received by add"

class loop:
	def __init__(self,path):
		test = path(0)
		if isinstance(test, int) or isinstance(test, float):
			self.path = lambda t: (path(t)*cos(t), path(t)*sin(t), 0)
		elif len(test) == 2:
			self.path = lambda t: path(t) + (0,)
		else:
			self.path = path
	def center(self):
		return scale(1/4.,add(add(self.path(0.),self.path(pi/2.)),
		           add(self.path(pi),self.path(3.*pi/2.))))
	def close(self):
		T = srange([0,2*pi,resolution]) + [0]
		for t in range(len(T)-1):
			yield (self.path(T[t]), self.path(T[t+1]), self.center()) 

class circular_surface:
	def __init__(self, surf, radius):
		self.radius = float(radius)
		test = surf(0,0)
		if isinstance(test, int) or isinstance(test, float):
			self.surf = lambda r,t: (r*cos(t), r*sin(t), surf(r,t))
		else:
			self.surf = surf
	def outer_loop(self):
		return loop(lambda t: self.surf(self.radius, t) )
	def surface(self):
		R = srange([0.,self.radius, resolution]) + [self.radius]
		T = srange([0.,2*pi,resolution]) + [0]
		for r in range(len(R) - 1):
			for t in range(len(T) - 1):
				yield ( self.surf(R[r],   T[t]  ),
				        self.surf(R[r+1], T[t]  ),
				        self.surf(R[r+1], T[t+1]),
				        self.surf(R[r],   T[t+1]) )

class cylinderical_surface:
	def __init__(self, surf, height):
		self.height = float(height)
		test = surf(0,0)
		if isinstance(test, int) or isinstance(test, float):
			self.surf = lambda t,h: (surf(t,h)*cos(t), surf(t,h)*sin(t), h)
		elif len(test) == 2:
			self.surf = lambda t,h: surf(t,h) + (h,)
		else:
			self.surf = surf
	def bottom_loop(self):
		return loop(lambda t: self.surf(t,0))
	def top_loop(self):
		return loop(lambda t: self.surf(t,self.height))
	def surface(self):
		H = srange([0.,self.height, float(resolution)])+[self.height]
		T = srange([0.,2*pi,resolution]) + [2*pi]
		for h in range(len(H) - 1):
			for t in range(len(T) - 1):
				yield ( self.surf(T[t],   H[h]  ),
				        self.surf(T[t+1], H[h]  ),
				        self.surf(T[t+1], H[h+1]),
				        self.surf(T[t],   H[h+1]) )

def join(loop1, loop2):
	T = srange([0.,2*pi,resolution]) + [2*pi]
	for t in range(len(T)-1):
		yield ( loop1.path(T[t]),
		        loop1.path(T[t+1]),
		        loop2.path(T[t+1]),
		        loop2.path(T[t]) )


