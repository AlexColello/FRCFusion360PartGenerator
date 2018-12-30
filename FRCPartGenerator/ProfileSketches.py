#Author: Alex Colello
# Contains the logic to sketch the various profiles for the part generator.

import adsk.core, adsk.fusion, adsk.cam, traceback


def getProfiles():
	return list(_profiles.keys())

def sketchProfile(profile, sketch):
	return _profiles[profile](sketch)

def drawCircle(sketch):
    
    origin = adsk.core.Point3D.create(0, 0, 0)
    
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(origin, 13.75/2)
    circleProfile = sketch.profiles.item(0)
    
    return circleProfile

def drawHex(sketch):
    
    origin = adsk.core.Point3D.create(0, 0, 0)
    
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(origin, 5)
    circleProfile = sketch.profiles.item(0)
    
    return circleProfile


_profiles = {
	'Circle': drawCircle,
	'Hex': drawHex,
}