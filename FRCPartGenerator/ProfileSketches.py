#Author: Alex Colello
# Contains the logic to sketch the various profiles for the part generator.

import adsk.core, adsk.fusion, adsk.cam, math


def getProfiles():

	return [
		'0.5" Hex',
		'0.375" Hex',
		'0.5" ThunderHex',
		'0.375" ThunderHex',
	]

def sketchProfile(profile, sketch):
	return _profiles[profile].drawSketch(sketch)

def getSideAppearance(profile, **kwargs):
	if 'isPainted' in kwargs:
		return _profiles[profile].getSideAppearance(kwargs['isPainted'])
	else:
		return _profiles[profile].getSideAppearance()

def getMaterial(profile):
	return _profiles[profile].getMaterial()

class Hex():
	
	size = 0    
	
	def __init__(self, size):
		self.size = size * 2.54
	
	def drawSketch(self, sketch):
		
		origin = adsk.core.Point3D.create(0, 0, 0)
		
		size = self.size / math.sqrt(3) * 2
		
		vertices = []
		for i in range(0, 6):
			vertex = adsk.core.Point3D.create(origin.x + (size/2) * math.cos(math.pi * i / 3), origin.y + (size/2) * math.sin(math.pi * i / 3),0)
			vertices.append(vertex)
		
		for i in range(0, 6):
			sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[(i+1) %6], vertices[i])
		
		profile = sketch.profiles[0]
		return profile

	def getMaterial(self):
		return 'Aluminum 7075'
		
	def getSideAppearance(self, isPainted=True):
		if isPainted:
			return 'Paint - Enamel Glossy (Black)'
		else:
			return 'Aluminum - Satin'

class ThunderHex(Hex):
	
	innerDiameter = 0
	outerDiameter = 0 
	
	def __init__(self, isSmall):
		if isSmall:
			self.innerDiameter = 0.165*2.54
			self.outerDiameter = 1.025
			super().__init__(0.375)
		else:
			self.innerDiameter = 0.201*2.54
			self.outerDiameter = 1.375
			super().__init__(0.5)

	def drawSketch(self, sketch):
		
		Hex.drawSketch(self, sketch)
		
		origin = adsk.core.Point3D.create(0, 0, 0)
		
		circles = sketch.sketchCurves.sketchCircles
		circles.addByCenterRadius(origin, self.outerDiameter/2.0) # Outer radius
		circles.addByCenterRadius(origin, self.innerDiameter/2.0) # Inner hole
		
		profile = max(sketch.profiles, key=lambda x : x.areaProperties().area)
		
		return profile

_profiles = {
	'0.5" Hex': Hex(0.5),
	'0.375" Hex': Hex(0.375),
	'0.5" ThunderHex': ThunderHex(False),
	'0.375" ThunderHex': ThunderHex(True),
}