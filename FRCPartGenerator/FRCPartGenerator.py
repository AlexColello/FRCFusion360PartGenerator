#Author-Alex Colello
#Description-Generates a variety of commonly used parts for the FIRST Robotics Competition.

import adsk.core, adsk.fusion, adsk.cam, traceback, sys, os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
import ShaftGenerator

import importlib
importlib.reload(ShaftGenerator)


def run(context):

	try:
		_app = adsk.core.Application.get()
		_ui = _app.userInterface

		existingDef = _ui.commandDefinitions.itemById('frcShaftGenerator')
		if existingDef:
			existingDef.deleteMe()
			
		# Delete the control
		addinPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
		shaftControl = addinPanel.controls.itemById('frcShaftGenerator')
		if shaftControl:
			shaftControl.deleteMe()

		seperator = addinPanel.controls.itemById('frcSeperator')
		if seperator:
			seperator.deleteMe()                
			
		# Create the command definition.
		shaftCmdDef = _ui.commandDefinitions.addButtonDefinition('frcShaftGenerator', 'Shaft', 'Creates a variety of types of shafts at a desired length.', './Resources/ShaftImages')

		# Connect to the command created event.
		onCommandCreated = ShaftGenerator.ShaftGeneratorCommandCreatedHandler()
		shaftCmdDef.commandCreated.add(onCommandCreated)
		ShaftGenerator.handlers.append(onCommandCreated)                

		# Get the CREATE toolbar panel. 
		addinPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
				
		# Add a seperator first
		addinPanel.controls.addSeparator('frcSeperator', 'ExchangeAppStoreCommand', False)
		
		# Add the command below the Web command.
		addinPanel.controls.addCommand(shaftCmdDef, 'frcSeperator', False)
		
	except:
		if _ui:
			_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
	
def stop(context):

	try:
		_app = adsk.core.Application.get()
		_ui  = _app.userInterface
	
		# Delete the control
		addinPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
		shaftControl = addinPanel.controls.itemById('frcShaftGenerator')
		if shaftControl:
			shaftControl.deleteMe()

		seperator = addinPanel.controls.itemById('frcSeperator')
		if seperator:
			seperator.deleteMe()
	
		# Delete the command definition.                
		existingDef = _ui.commandDefinitions.itemById('frcShaftGenerator')
		if existingDef:
			existingDef.deleteMe()
	
	except:
		if _ui:
			_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))