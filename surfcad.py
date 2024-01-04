# coding=UTF-8

from math import *

"""surfcad is still a work in progress. Documentation is poor at this point, features are limited and API subject to change."""


resolution = 0.05 #must be float


def _v_cross(a,b):
	return ( a[1]*b[2] - b[1]*a[2], a[2]*b[0] - b[2]*a[0], a[0]*b[1] - b[0]*a[1] )

def _v_dot(a,b):
	return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

def _v_norm(a):
	return (a[0]**2+a[1]**2+a[2]**2)**0.5

def _v_scale(a,v):
	return (a*v[0], a*v[1], a*v[2])

def _v_add(u,v):
	return (u[0]+v[0],u[1]+v[1],u[2]+v[2])

def srange(S):
	return list(map(lambda x: x*S[2], range(int(floor(S[0]/S[2])),int(floor(S[1]/S[2]))+1)))

class STLFile:
	def __init__(self,fname):
		self.out = open(fname,'w')
		self.out.write("solid Default\n")
	def end(self):
		self.out.write("endsolid Default")
		self.out.close()
	def add_triangle(self, i):
		nav = _v_scale(-1/3.,_v_add(_v_add(i[0],i[1]),i[2]))
		n = _v_cross(_v_add(i[1],nav),_v_add(i[2],nav))
		un = _v_norm(n)
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
		"""Add a surface to your STL object.
		   surfgen -- a generator that returns tuples. 3 tuples are interpreted as triangles, 4 tuples as squares.
		"""
		for i in surfgen:
			if len(i) == 3:
				self.add_triangle(i)
			elif len(i) == 4:
				self.add_square(i)
			else:
				print("unknown primitive received by add")

class loop:
	def __init__(self,path):
		""" Create a loop. 
		path -- the path of the loop; should be a function from [0,2π] to ℝ 
		        (in which case it is iterpreted as radius), ℝ² (in which case it is
			interpreted as points on a plane) or ℝ³ (points in space).
		"""
		test = path(0)
		if isinstance(test, int) or isinstance(test, float):
			self.path = lambda t: (path(t)*cos(t), path(t)*sin(t), 0)
		elif len(test) == 2:
			self.path = lambda t: path(t) + (0,)
		else:
			self.path = path
	def center(self):
		""" Aproximated center of the loop in ℝ³"""
		return _v_scale(1/4.,_v_add(_v_add(self.path(0.),self.path(pi/2.)),
		           _v_add(self.path(pi),self.path(3.*pi/2.))))
	def close(self):
		""" Returns a surface closing the loop"""
		T = srange([0,2*pi,resolution]) + [0]
		for t in range(len(T)-1):
			yield (self.path(T[t]), self.path(T[t+1]), self.center()) 

class Surface:
	surf = lambda x: (0,0,0)
	def clone(self):
		pass

class circular_surface(Surface):
	def __init__(self, surf, radius):
		self.radius = float(radius)
		test = surf(0,0)
		if isinstance(test, int) or isinstance(test, float):
			self.surf = lambda r,t: (r*cos(t), r*sin(t), surf(r,t))
		else:
			self.surf = surf
	def clone(self):
		return circular_surface(self.surf,self.radius)
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

class cylinderical_surface(Surface):
	def __init__(self, surf, height):
		self.height = float(height)
		test = surf(0,0)
		if isinstance(test, int) or isinstance(test, float):
			self.surf = lambda t,h: (surf(t,h)*cos(t), surf(t,h)*sin(t), h)
		elif len(test) == 2:
			self.surf = lambda t,h: surf(t,h) + (h,)
		else:
			self.surf = surf
	def clone(self):
		return cylinderical_surface(self.surf, self.height)
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


class Transform:
	def __init__(self, t):
		self.t = t
	def __mul__(self, obj):
		if isinstance(obj,Transform):
			return Transform(lambda x: self.t(obj.t(x)) )
		elif isinstance(obj,loop):
			return loop(lambda x: self.t(obj.path(x)) )
		else:
			obj = obj.clone()
			surf = obj.surf #to force a deep copy of the function and prevent infinit recursion.
			obj.surf = lambda a,b: self.t(surf(a,b))
			return obj

def scale(s):
	if isinstance(s, list) or isinstance(s, tuple):
		if len(s) == 0:
			s = (1,1,1)
		elif len(s) == 1:
			s += (1,1)
		elif len(s) == 2:
			s += (1,)
		return Transform(lambda x: (s[0]*x[0], s[1]*x[1], s[2]*x[2]) )
	if isinstance(s, int) or isinstance(s, float):
		return scale([s,s,s])

def translate(s):
	if isinstance(s, list) or isinstance(type(s), tuple):
		if len(s) == 0:
			s = (1,1,1)
		elif len(s) == 1:
			s += (1,1)
		elif len(s) == 2:
			s += (1,)
		return Transform(lambda x: (s[0]+x[0], s[1]+x[1], s[2]+x[2]) )
	if isinstance(s, int) or isinstance(s, float):
		return translate([s,s,s])


def rotatez(t):
	return Transform(lambda x: (x[0]*cos(t)-x[1]*sin(t), x[0]*sin(t)+x[1]*cos(t), x[2] ) )

def twistz(t):
	return Transform(lambda x: (x[0]*cos(t*x[2])-x[1]*sin(t*x[2]), x[0]*sin(t*x[2])+x[1]*cos(t*x[2]), x[2] ) )

