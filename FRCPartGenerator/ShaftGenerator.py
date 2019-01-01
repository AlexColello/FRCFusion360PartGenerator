import adsk.core, adsk.fusion, adsk.cam, traceback, sys, os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
import ShaftProfiles

import importlib
importlib.reload(ShaftProfiles)

_app = None
_ui = None

handlers = []


class ShaftGeneratorCommandExecuteHandler(adsk.core.CommandEventHandler):
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
			selectedProfile = inputs.itemById('profileDropdown').selectedItem.name

			# add sketch
			sketches = newComp.sketches
			sketch = sketches.add(newComp.xYConstructionPlane)                
			
			profile = ShaftProfiles.sketchProfile(selectedProfile, sketch)            
			distance = adsk.core.ValueInput.createByReal(distanceVal)  

			# extrude the profile
			extrudes = newComp.features.extrudeFeatures
	
			extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
			extentDistance = adsk.fusion.DistanceExtentDefinition.create(distance)        
			extrudeInput.setOneSideExtent(extentDistance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
		
			extrudeFeature = extrudes.add(extrudeInput)
			
			materialName = ShaftProfiles.getMaterial(selectedProfile)			
			materialLibrary = _app.materialLibraries.itemByName('Fusion 360 Material Library')
			newMaterial = materialLibrary.materials.itemByName(materialName)
				
			body = extrudeFeature.bodies[0]	
			body.material = newMaterial				
				
			paintedInput = inputs.itemById('painted')		
				
			if paintedInput.isVisible:				
				sideAppearanceName = ShaftProfiles.getSideAppearance(selectedProfile, isPainted=paintedInput.value)
			else:
				sideAppearanceName = ShaftProfiles.getSideAppearance(selectedProfile)
			
			appearanceLibrary = _app.materialLibraries.itemByName('Fusion 360 Appearance Library')
			sideAppearance = appearanceLibrary.appearances.itemByName(sideAppearanceName)				
				
			for side in extrudeFeature.sideFaces:
				side.appearance = sideAppearance
						
			_app.activeViewport.refresh()
			
		except:
			if _ui:
				_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
	 
	 
class ShaftGeneratorCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
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
			selectedProfile = inputs.itemById('profileDropdown').selectedItem.name

			# add sketch
			sketches = newComp.sketches
			sketch = sketches.add(newComp.xYConstructionPlane)                
			
			profile = ShaftProfiles.sketchProfile(selectedProfile, sketch)            
			distance = adsk.core.ValueInput.createByReal(distanceVal)  

			# extrude the profile
			extrudes = newComp.features.extrudeFeatures
	
			extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
			extentDistance = adsk.fusion.DistanceExtentDefinition.create(distance)        
			extrudeInput.setOneSideExtent(extentDistance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
		
			extrudeFeature = extrudes.add(extrudeInput)
			
			materialName = ShaftProfiles.getMaterial(selectedProfile)			
			materialLibrary = _app.materialLibraries.itemByName('Fusion 360 Material Library')
			newMaterial = materialLibrary.materials.itemByName(materialName)
				
			body = extrudeFeature.bodies[0]	
			body.material = newMaterial				
				
			paintedInput = inputs.itemById('painted')		
				
			if paintedInput.isVisible:				
				sideAppearanceName = ShaftProfiles.getSideAppearance(selectedProfile, isPainted=paintedInput.value)
			else:
				sideAppearanceName = ShaftProfiles.getSideAppearance(selectedProfile)
			
			appearanceLibrary = _app.materialLibraries.itemByName('Fusion 360 Appearance Library')
			sideAppearance = appearanceLibrary.appearances.itemByName(sideAppearanceName)				
				
			for side in extrudeFeature.sideFaces:
				side.appearance = sideAppearance
						
			eventArgs.isValidResult = True

			_app.activeViewport.refresh()
			
		except:
			if _ui:
				_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

		
class ShaftGeneratorCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
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

			# Get the command
			cmd = eventArgs.command
		
			# Get the CommandInputs collection to create new command inputs.            
			inputs = cmd.commandInputs
			
			# Add dropdown for profiles
			dropdownInput = inputs.addDropDownCommandInput('profileDropdown', 'Profile', adsk.core.DropDownStyles.LabeledIconDropDownStyle);
			dropdownItems = dropdownInput.listItems

			profileList = ShaftProfiles.getProfiles()
			dropdownItems.add(profileList[0], True, '')
			for i in range(1, len(profileList)):
				dropdownItems.add(profileList[i], False, '')

			# Add distance input and manipulator
			distanceValueInput = inputs.addDistanceValueCommandInput('distanceValue', 'Length', adsk.core.ValueInput.createByReal(1))
			distanceValueInput.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(0, 0, 1))
			distanceValueInput.expression = '1 in'
			distanceValueInput.hasMinimumValue = False
			distanceValueInput.hasMaximumValue = False
			
			# Add checkbox for color
			inputs.addBoolValueInput('painted', 'Painted', True, '', True)			
			
			# Connect to the execute event.
			onExecute = ShaftGeneratorCommandExecuteHandler()
			cmd.execute.add(onExecute)
			handlers.append(onExecute)
			
			# Connect to the execute preview event.
			onExecutePreview = ShaftGeneratorCommandExecutePreviewHandler()
			cmd.executePreview.add(onExecutePreview)
			handlers.append(onExecutePreview)
			
			# Connect to the validate inputs event.
			onValidateInputs = ShaftGeneratorCommandValidateInputsHandler()
			cmd.validateInputs.add(onValidateInputs)
			handlers.append(onValidateInputs)
			
			# Connect to the input changed event.
			onInputChanged = ShaftGeneratorCommandInputChangedHandler()
			cmd.inputChanged.add(onInputChanged)
			handlers.append(onInputChanged)
			
		except:
			if _ui:
				_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
		

class ShaftGeneratorCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
	def __init__(self):
		super().__init__()
	def notify(self, args):
		eventArgs = adsk.core.InputChangedEventArgs.cast(args)
        
		# Check the value of the check box.
		changedInput = eventArgs.input
		if changedInput.id == 'profileDropdown':
			inputs = eventArgs.firingEvent.sender.commandInputs
			paintedInput = inputs.itemById('painted')
						
			# Change the visibility of the scale value input.
			if 'ThunderHex' in changedInput.selectedItem.name:
				paintedInput.isVisible = False
			else:
				paintedInput.isVisible = True


class ShaftGeneratorCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
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
