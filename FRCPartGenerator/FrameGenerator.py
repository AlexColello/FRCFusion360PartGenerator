import adsk.core, adsk.fusion, adsk.cam, traceback
import sys, os, importlib, json

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
import FrameProfiles

importlib.reload(FrameProfiles)

_app = None
_ui = None

handlers = []

profileFiles = None
allProfiles = None

def loadProfiles(profileDirectory):

	profiles = {}	
	files = os.listdir(profileDirectory)

	for filename in filter(lambda x: len(x) > 5 and x.endswith('.json'), files):
		filepath = os.path.join(profileDirectory, filename)
		with open(filepath, 'r') as file:
			try:
				jsonString = file.read()
				obj = json.loads(jsonString, object_hook=FrameProfiles.decodeProfile)
			except:
				_ui.messageBox('Error reading {} at {}:\n{}'.format(filename, filepath, traceback.format_exc()))
				continue
			if obj.id in allProfiles:
				_ui.messageBox('Skipping {}, a profile with id {} has already been loaded.'.format(filepath, obj.id))
			else:
				profiles[obj.id] = obj
				allProfiles[obj.id] = obj
				profileFiles[obj.id] = filepath

	return profiles

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
			
			table = inputs.itemById('profileTable')
			if table.rowCount > 0:
				selectedCommand = table.getInputAtPosition(table.selectedRow, 0)
				selectedProfileID = selectedCommand.name
				selectedProfile = allProfiles[selectedProfileID]
				profile = selectedProfile.drawSketch(sketch)
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

			global profileFiles, allProfiles
			profileFiles = {}
			allProfiles = {}

			includedDirectory = os.path.join(dir_path, 'Data', 'BoxTubeProfiles', 'Included')
			includedProfiles = loadProfiles(includedDirectory)
			includedProfileValues = list(includedProfiles.values())

			customDirectory = os.path.join(dir_path, 'Data', 'BoxTubeProfiles', 'Custom')
			customProfiles = loadProfiles(customDirectory)
			customProfileValues = list(customProfiles.values())

			# Get the command
			cmd = eventArgs.command
		
			# Get the CommandInputs collection to create new command inputs.            
			inputs = cmd.commandInputs


			table = inputs.addTableCommandInput('profileTable', 'Table', 1, '1')
			table.isFullWidth = True
			table.minimumVisibleRows = 1
			table.maximumVisibleRows = max(len(allProfiles), 5)
			table.columnSpacing = 1
			table.rowSpacing = 1
			table.tablePresentationStyle = adsk.core.TablePresentationStyles.nameValueTablePresentationStyle
			table.hasGrid = False
			table.isVisible = True

			tableInputs = table.commandInputs


			currentRow = 0
			for i in range(len(customProfileValues)):
				currentProfile = customProfileValues[i]
				profileInput = tableInputs.addStringValueInput('row{}'.format(currentRow), currentProfile.id, currentProfile.id)
				profileInput.isFullWidth = True
				profileInput.isReadOnly = True

				table.addCommandInput(profileInput, currentRow, 0)
				currentRow += 1

			for i in range(len(includedProfileValues)):
				currentProfile = includedProfileValues[i]
				profileInput = tableInputs.addStringValueInput('row{}'.format(currentRow), currentProfile.id, currentProfile.id)
				profileInput.isFullWidth = True
				profileInput.isReadOnly = True

				table.addCommandInput(profileInput, currentRow, 0)
				currentRow += 1
			
			table.selectedRow = 0


			# Add and remove buttons
			'''
			addButtonInput = tableInputs.addBoolValueInput(table.id + '_add', 'Add', False, '', True)
			table.addToolbarCommandInput(addButtonInput)
			deleteButtonInput = tableInputs.addBoolValueInput(table.id + '_delete', 'Delete', False, '', True)
			table.addToolbarCommandInput(deleteButtonInput)
			'''

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
			cmd.executePreview.add(onExecute)
			handlers.append(onExecute)
			
			# Connect to the validate inputs event.
			onValidateInputs = FrameGeneratorCommandValidateInputsHandler()
			cmd.validateInputs.add(onValidateInputs)
			handlers.append(onValidateInputs)

			onInputChanged = FrameGeneratorCommandInputChangedHandler()
			cmd.inputChanged.add(onInputChanged)
			handlers.append(onInputChanged)
			
		except:
			if _ui:
				_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class FrameGeneratorCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
	def __init__(self):
		super().__init__()

	def notify(self, args):
		eventArgs = adsk.core.InputChangedEventArgs.cast(args)
        
		changedInput = eventArgs.input
		previousInputs = eventArgs.inputs

		if 'row' in changedInput.id:
			table = previousInputs.itemById('profileTable')
			_, newRow, _, _, _ = table.getPosition(changedInput)
			table.selectedRow = newRow

			command = eventArgs.firingEvent.sender
			command.doExecutePreview()

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