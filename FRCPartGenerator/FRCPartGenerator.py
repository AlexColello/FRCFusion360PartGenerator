#Author-Alex Colello
#Description-Generates a variety of commonly used parts for the FIRST Robotics Competition.

import adsk.core, adsk.fusion, adsk.cam, traceback

handlers = []

class PartGeneratorCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox("Command Create Handler")

def createNewComponent():
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component

def makeAll():
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
        return
    currentDesignType = design.designType

    global newComp
    newComp = createNewComponent()
    if newComp is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return
        
    # add sketch
    sketches = newComp.sketches
    sketch = sketches.add(newComp.xYConstructionPlane)      
    
    origin = adsk.core.Point3D.create(0, 0, 0)
    
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(origin, 13.75/2)
        
    app.activeViewport.refresh()

def run(context):
    
        ui = None
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
    
            existingDef = ui.commandDefinitions.itemById('frcHexShaft')
            if existingDef:
                existingDef.deleteMe()
                
            # Create the command definition.
            hexCmdDef = ui.commandDefinitions.addButtonDefinition('frcHexShaft', 'Hex Shaft', 'Creates a hex shaft at a desired length.', './Resources/HexImages')
    
            # Connect to the command created event.
            onCommandCreated = PartGeneratorCommandCreatedHandler()
            hexCmdDef.commandCreated.add(onCommandCreated)
            handlers.append(onCommandCreated)                
    
            # Get the CREATE toolbar panel. 
            addinPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
                    
            # Add a seperator first
            addinPanel.controls.addSeparator('frcSeperator', 'ExchangeAppStoreCommand', False)
            
            # Add the command below the Web command.
            addinPanel.controls.addCommand(hexCmdDef, 'frcSeperator', False)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    
def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
    
        # Delete the control
        createPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cutoutsControl = createPanel.controls.itemById('frcHexShaft')
        if cutoutsControl:
            cutoutsControl.deleteMe()

        seperator = createPanel.controls.itemById('frcSeperator')
        if seperator:
            seperator.deleteMe()
    
        # Delete the command definition.                
        existingDef = ui.commandDefinitions.itemById('frcHexShaft')
        if existingDef:
            existingDef.deleteMe()
    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))