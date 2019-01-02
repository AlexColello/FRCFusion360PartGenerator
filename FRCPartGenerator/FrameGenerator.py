import adsk.core, adsk.fusion, adsk.cam, traceback
import sys, os, importlib, json

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
import FrameProfiles

importlib.reload(FrameProfiles)

_app = None
_ui = None
profiles = None

handlers = []


def loadProfiles():

	profileDirectory = os.path.join(dir_path, 'Data', 'BoxTubeProfiles')

	files = os.listdir(profileDirectory)

	global profiles
	profiles = []

	for filename in files:
		filepath = os.path.join(profileDirectory, filename)
		with open(filepath, 'r') as file:
			jsonString = file.read()
			obj = json.loads(jsonString, object_hook=FrameProfiles.decodeProfile)
			profiles.append(obj)



class FrameGeneratorCommandExecuteHandler(adsk.core.CommandEventHandler):
	def __init__(self):
		super().__init__()
		
	def notify(self, args):
		try:
			
			eventArgs = adsk.core.CommandEventArgs.cast(args)            
		
			newComp = createNewComponent()
			if newComp is None:
				_ui.messageBox('New component failed to create', 'New Component Failed')
				return
				
			# Get the values from the command inputs.
			inputs = eventArgs.command.commandInputs
			distanceVal = inputs.itemById('distanceValue').value 

			# add sketch
			sketches = newComp.sketches
			sketch = sketches.add(newComp.xYConstructionPlane)                
			
			boxProfile = profiles[0]
			profile = boxProfile.drawSketch(sketch)            
			distance = adsk.core.ValueInput.createByReal(distanceVal)  

			# extrude the profile
			extrudes = newComp.features.extrudeFeatures
	
			extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
			extentDistance = adsk.fusion.DistanceExtentDefinition.create(distance)        
			extrudeInput.setOneSideExtent(extentDistance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
		
			extrudeFeature = extrudes.add(extrudeInput)
						
			_app.activeViewport.refresh()
			
		except:
			if _ui:
				_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
	 
	 
class FrameGeneratorCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
	def __init__(self):
		super().__init__()
		
	def notify(self, args):

		try:
			eventArgs = adsk.core.CommandEventArgs.cast(args)            
		
			newComp = createNewComponent()
			if newComp is None:
				_ui.messageBox('New component failed to create', 'New Component Failed')
				return
				
			# Get the values from the command inputs.
			inputs = eventArgs.command.commandInputs
			distanceVal = inputs.itemById('distanceValue').value 

			# add sketch
			sketches = newComp.sketches
			sketch = sketches.add(newComp.xYConstructionPlane)                
			
			boxProfile = profiles[0]
			profile = boxProfile.drawSketch(sketch)            
			distance = adsk.core.ValueInput.createByReal(distanceVal)  

			# extrude the profile
			extrudes = newComp.features.extrudeFeatures

			extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
			extentDistance = adsk.fusion.DistanceExtentDefinition.create(distance)        
			extrudeInput.setOneSideExtent(extentDistance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
		
			extrudeFeature = extrudes.add(extrudeInput)
						
			eventArgs.isValidResult = True

			_app.activeViewport.refresh()
			
		except:
			if _ui:
				_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

		
class FrameGeneratorCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
	def __init__(self):
		super().__init__()
		
	def notify(self, args):

		try:

			global _app, _ui
			_app = adsk.core.Application.get()
			_ui  = _app.userInterface

			eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
			
			product = _app.activeProduct
			design = adsk.fusion.Design.cast(product)
			if not design:
				_ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
				return

			loadProfiles()

			# Get the command
			cmd = eventArgs.command
		
			# Get the CommandInputs collection to create new command inputs.            
			inputs = cmd.commandInputs

			# Add distance input and manipulator
			distanceValueInput = inputs.addDistanceValueCommandInput('distanceValue', 'Length', adsk.core.ValueInput.createByReal(1))
			distanceValueInput.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(0, 0, 1))
			distanceValueInput.expression = '1 in'
			distanceValueInput.hasMinimumValue = False
			distanceValueInput.hasMaximumValue = False		
			
			# Connect to the execute event.
			onExecute = FrameGeneratorCommandExecuteHandler()
			cmd.execute.add(onExecute)
			handlers.append(onExecute)
			
			# Connect to the execute preview event.
			onExecutePreview = FrameGeneratorCommandExecutePreviewHandler()
			cmd.executePreview.add(onExecutePreview)
			handlers.append(onExecutePreview)
			
			# Connect to the validate inputs event.
			onValidateInputs = FrameGeneratorCommandValidateInputsHandler()
			cmd.validateInputs.add(onValidateInputs)
			handlers.append(onValidateInputs)
			
		except:
			if _ui:
				_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class FrameGeneratorCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
	def __init__(self):
		super().__init__()
	def notify(self, args):
		try:
			eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
			inputs = eventArgs.firingEvent.sender.commandInputs
			
			distance = inputs.itemById('distanceValue').value
			if distance == 0:
				eventArgs.areInputsValid = False
			else:
				eventArgs.areInputsValid = True
		except:
			if _ui:
				_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def createNewComponent():
	
	# Get the active design.
	product = _app.activeProduct
	design = adsk.fusion.Design.cast(product)
	activeComp = design.activeComponent
	allOccs = activeComp.occurrences
	newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
	
	return newOcc.component