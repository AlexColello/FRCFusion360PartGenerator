#Author-Alex Colello
#Description-Generates a variety of commonly used parts for the FIRST Robotics Competition.

import adsk.core, adsk.fusion, adsk.cam, traceback, sys, os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
import ShaftGenerator
import FrameGenerator

import importlib
importlib.reload(ShaftGenerator)
importlib.reload(FrameGenerator)


def deletePrevious():
	_app = adsk.core.Application.get()
	_ui = _app.userInterface

	existingDef = _ui.commandDefinitions.itemById('frcShaftGenerator')
	if existingDef:
		existingDef.deleteMe()

	existingDef = _ui.commandDefinitions.itemById('frcBoxTubeGenerator')
	if existingDef:
		existingDef.deleteMe()

	# Delete the control
	createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')	
	shaftControl = createPanel.controls.itemById('frcShaftGenerator')
	if shaftControl:
		shaftControl.deleteMe()
	
	seperator = createPanel.controls.itemById('frcBoxTubeGenerator')
	if seperator:
		seperator.deleteMe()

	seperator = createPanel.controls.itemById('frcSeperator')
	if seperator:
		seperator.deleteMe()


def run(context):

	try:
		_app = adsk.core.Application.get()
		_ui = _app.userInterface

		deletePrevious()              
			
		# Get the CREATE toolbar panel. 
		createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
				
		# Add a seperator first
		createPanel.controls.addSeparator('frcSeperator', 'PrimitivePipe', False)

		# Create the command definition.
		shaftCmdDef = _ui.commandDefinitions.addButtonDefinition('frcShaftGenerator', 'Shaft', 'Creates a variety of types of shafts at a desired length.', './Resources/ShaftImages')

		# Connect to the command created event.
		onCommandCreated = ShaftGenerator.ShaftGeneratorCommandCreatedHandler()
		shaftCmdDef.commandCreated.add(onCommandCreated)
		ShaftGenerator.handlers.append(onCommandCreated)                

		# Add the command below the Pipe command.
		createPanel.controls.addCommand(shaftCmdDef, 'frcSeperator', False)

		# Create the command definition.
		boxCmdDef = _ui.commandDefinitions.addButtonDefinition('frcBoxTubeGenerator', 'Box Tube', 'Creates a box tube of a desired length.', './Resources/MainImages')

		# Connect to the command created event.
		onCommandCreated = FrameGenerator.FrameGeneratorCommandCreatedHandler()
		boxCmdDef.commandCreated.add(onCommandCreated)
		FrameGenerator.handlers.append(onCommandCreated)                

		# Add the command below the Pipe command.
		createPanel.controls.addCommand(boxCmdDef, 'frcSeperator', False)
		
	except:
		if _ui:
			_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
	
def stop(context):

	try:
		deletePrevious()
	
	except:
		if _ui:
			_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))