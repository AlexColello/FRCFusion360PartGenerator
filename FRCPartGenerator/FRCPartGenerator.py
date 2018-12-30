#Author-Alex Colello
#Description-Generates a variety of commonly used parts for the FIRST Robotics Competition.

import adsk.core, adsk.fusion, adsk.cam, traceback, sys, os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
import ProfileSketches

import importlib
importlib.reload(ProfileSketches)

_app = None
_ui = None

handlers = []


class PartGeneratorCommandExecuteHandler(adsk.core.CommandEventHandler):
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
            
            profile = ProfileSketches.sketchProfile(selectedProfile, sketch)            
            distance = adsk.core.ValueInput.createByReal(distanceVal)  

            extrudeProfile(profile, distance, newComp)
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
class PartGeneratorCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
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
            
            profile = ProfileSketches.sketchProfile(selectedProfile, sketch)            
            distance = adsk.core.ValueInput.createByReal(distanceVal)  

            extrudeProfile(profile, distance, newComp)
            
            eventArgs.isValidResult = True            
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

        
class PartGeneratorCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):

        try:

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
            
            dropdownInput = inputs.addDropDownCommandInput('profileDropdown', 'Profile', adsk.core.DropDownStyles.LabeledIconDropDownStyle);
            dropdownItems = dropdownInput.listItems

            profileList = ProfileSketches.getProfiles()
            dropdownItems.add(profileList[0], True, '')
            for i in range(1, len(profileList)):
                dropdownItems.add(profileList[i], False, '')

            distanceValueInput = inputs.addDistanceValueCommandInput('distanceValue', 'Length', adsk.core.ValueInput.createByReal(1))
            distanceValueInput.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(0, 0, 1))
            distanceValueInput.expression = '1 in'
            distanceValueInput.hasMinimumValue = False
            distanceValueInput.hasMaximumValue = False
            
            # Connect to the execute event.
            onExecute = PartGeneratorCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
            # Connect to the execute preview event.
            onExecutePreview = PartGeneratorCommandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            handlers.append(onExecutePreview)
            
            # Connect to the validate inputs event.
            onValidateInputs = PartGeneratorCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            handlers.append(onValidateInputs)
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
class PartGeneratorCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
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
    

def extrudeProfile(profile, distance, component):
    
    extrudes = component.features.extrudeFeatures
    
    extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extentDistance = adsk.fusion.DistanceExtentDefinition.create(distance)        
    extrudeInput.setOneSideExtent(extentDistance, adsk.fusion.ExtentDirections.PositiveExtentDirection)

    extrudes.add(extrudeInput)
    
    _app.activeViewport.refresh()


def run(context):

    global _ui, _app
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
        onCommandCreated = PartGeneratorCommandCreatedHandler()
        shaftCmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)                

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
    global _app, _ui
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