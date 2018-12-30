#Author-Alex Colello
#Description-Generates a variety of commonly used parts for the FIRST Robotics Competition.

import adsk.core, adsk.fusion, adsk.cam, traceback

_app = None
_ui = None

handlers = []
profile = None
profileName = ''

class PartGeneratorCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            _ui.messageBox("Command Execute Handler")
            
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # Get the values from the command inputs.
            inputs = eventArgs.command.commandInputs
            distanceVal = inputs.itemById('distanceValue').value             
            
            product = _app.activeProduct
            design = adsk.fusion.Design.cast(product)
            if not design:
                _ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
                return
        
            global newComp
            newComp = createNewComponent()
            if newComp is None:
                _ui.messageBox('New component failed to create', 'New Component Failed')
                return
                
            # add sketch
            sketches = newComp.sketches
            sketch = sketches.add(newComp.xYConstructionPlane)                
            
            circleProfile = drawCircle(sketch)            
            
            distance = adsk.core.ValueInput.createByReal(distanceVal)    
            extrudeProfile(circleProfile, distance, newComp)
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
class PartGeneratorCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):

        try:
            _ui.messageBox('preview')
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # Get the values from the command inputs.
            inputs = eventArgs.command.commandInputs
            distanceVal = inputs.itemById('distanceValue').value             
            
            product = _app.activeProduct
            design = adsk.fusion.Design.cast(product)
            if not design:
                _ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
                return
        
            global newComp
            newComp = createNewComponent()
            if newComp is None:
                _ui.messageBox('New component failed to create', 'New Component Failed')
                return
                
            # add sketch
            sketches = newComp.sketches
            sketch = sketches.add(newComp.xYConstructionPlane)                
            
            circleProfile = drawCircle(sketch)            
            
            distance = adsk.core.ValueInput.createByReal(distanceVal)    
            extrudeProfile(circleProfile, distance, newComp)
            
            eventArgs.isValidResult = True            
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

        
class PartGeneratorCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):

        try:
            _ui.messageBox("Command Create Handler")
            
            
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Get the command
            cmd = eventArgs.command
        
            # Get the CommandInputs collection to create new command inputs.            
            inputs = cmd.commandInputs
            
            dropdownInput = inputs.addDropDownCommandInput('dropdown', 'Dropdown', adsk.core.DropDownStyles.LabeledIconDropDownStyle);
            dropdownItems = dropdownInput.listItems
            dropdownItems.add('Item 1', True, '')
            dropdownItems.add('Item 2', False, '')        
            
            distanceValueInput = inputs.addDistanceValueCommandInput('distanceValue', 'DistanceValue', adsk.core.ValueInput.createByReal(1))
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

def drawCircle(sketch):
    
    origin = adsk.core.Point3D.create(0, 0, 0)
    
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(origin, 13.75/2)
    circleProfile = sketch.profiles.item(0)  
    
    global profile
    profile = circleProfile
    
    return circleProfile


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

        existingDef = _ui.commandDefinitions.itemById('frcHexShaft')
        if existingDef:
            existingDef.deleteMe()
            
        # Delete the control
        addinPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        hexControl = addinPanel.controls.itemById('frcHexShaft')
        if hexControl:
            hexControl.deleteMe()

        seperator = addinPanel.controls.itemById('frcSeperator')
        if seperator:
            seperator.deleteMe()                
            
        # Create the command definition.
        hexCmdDef = _ui.commandDefinitions.addButtonDefinition('frcHexShaft', 'Hex Shaft', 'Creates a hex shaft at a desired length.', './Resources/HexImages')

        # Connect to the command created event.
        onCommandCreated = PartGeneratorCommandCreatedHandler()
        hexCmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)                

        # Get the CREATE toolbar panel. 
        addinPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
                
        # Add a seperator first
        addinPanel.controls.addSeparator('frcSeperator', 'ExchangeAppStoreCommand', False)
        
        # Add the command below the Web command.
        addinPanel.controls.addCommand(hexCmdDef, 'frcSeperator', False)
        
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
        hexControl = addinPanel.controls.itemById('frcHexShaft')
        if hexControl:
            hexControl.deleteMe()

        seperator = addinPanel.controls.itemById('frcSeperator')
        if seperator:
            seperator.deleteMe()
    
        # Delete the command definition.                
        existingDef = _ui.commandDefinitions.itemById('frcHexShaft')
        if existingDef:
            existingDef.deleteMe()
    
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))