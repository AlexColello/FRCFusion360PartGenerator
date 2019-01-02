

class HoleProfile():

	offset = 0
	edgeDistance = 0
	spacing = 0
	diameter = 0


class FrameObject():

	width = 0
	height = 0
	wallThickness = 0

	def __init__(self):
		self.verticleHoles = []
		self.horizontalHoles = []


class RectangularTubing(FrameObject):

	def __init__(self):
		super().__init__()

	def drawSketch(self, sketch):

		origin = adsk.core.Point3D.create(0, 0, 0)
		
		size = self.size / math.sqrt(3) * 2
		
		innerVertices = []
		outerVertices = []
		for i in range(0, 4):

			xSign = 1 - 2 * (((i + 1) % 4) // 2)
			ySign = 1 - 2 * (i // 2)

			outerVertex = adsk.core.Point3D.create(origin.x + xSign*(self.width/2.0), origin.y + ySign*(self.height/2.0), 0)
			outerVertices.append(outerVertex)

			innerVertex = adsk.core.Point3D.create(origin.x + xSign*(self.width/2.0 - self.wallThickness), origin.y + ySign*(self.height/2.0 - self.wallThickness), 0)
			innerVertices.append(innerVertex)
		
		for i in range(0, 4):
			sketch.sketchCurves.sketchLines.addByTwoPoints(outerVertices[(i+1) % 4], outerVertices[i])
			sketch.sketchCurves.sketchLines.addByTwoPoints(innerVertices[(i+1) % 4], innerVertices[i])
		
		profile = sketch.profiles[0]
		return profile
