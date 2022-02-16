# cityGenerator.py

import maya.cmds as cmds
import random
import math

from datetime import datetime
random.seed( datetime.now() )

# Delete Base Plane Function
def deleteBasePlane(name):
    
    if cmds.objExists( name ):
        cmds.delete( name )

# Base Plane Generator Function
def createBasePlane(width, height):
    
    deleteBasePlane('basePlane')
    deleteBasePlane('originalBasePlane')
        
    # Create base plane
    basePlane = cmds.polyPlane( sx=width*2, sy=height*2, w=width, h=height, name='originalBasePlane' )
    
    # Clear old buildings
    deleteCity()

# Copy Base Plane Function
def copyBasePlane():
    
    cmds.showHidden( 'originalBasePlane' )
    cmds.duplicate( 'originalBasePlane', name='basePlane' )
    cmds.hide( 'originalBasePlane' )

# Delete buildings function
def deleteCity():

    buildings = cmds.ls( 'cityBuilding*' )
    if len( buildings ) > 0:
        cmds.delete( buildings )

# City Generator Function
def createCity(width, height, maxHeight, spacingIntensity):
    
    # Delete old buildings
    deleteCity()
    deleteBasePlane('basePlane')
    
    # Copy base plane incase modified
    copyBasePlane()
    
    # Calculate number of vertices for building placement
    numVerts = (width * 2 + 1) * (height * 2 + 1)
    print(numVerts)
    
    # Calculate number of buildings
    numBuildings = int(math.ceil(numVerts / 2.0))
    print(numBuildings)
    
    # Calculate number of faces
    numFaces = (width * 2) * (height * 2)
    print(numFaces)
    
    maxWidth = spacingIntensity/10.0
    maxDepth = maxWidth
    
    oddRow = width + 1
    evenRow = width * 2 + 1
    if width > height:
        maxDimension = width
    else:
        maxDimension = height
    
    baseHeight = 0.25
    
    # Extrude base plane
    cmds.select( 'basePlane*' )
    cmds.polyExtrudeFacet( localTranslateZ=baseHeight )
    
    # Add locator to center of each building quadrant
    for i in range (0, numVerts):
        # Skip every other row of verts
        # Skip every other vert of those selected rows
        if (i % 2) == 0:
            currPos = cmds.xform('basePlane*.vtx[%s]' % (i), q=True, t=True, ws=True)
            x = currPos[0]
            y = currPos[1]
            z = currPos[2]
            
            # Randomly determine building height within range
            currBuildingHeight = random.randint(1, maxHeight)
            
            # Create and place new building
            currBuilding = cmds.polyCube( sx=4, sy=currBuildingHeight * 5, sz=4, w=maxWidth, h=currBuildingHeight, d=maxDepth, name='building#' )
            cmds.move(x, y + currBuildingHeight/2.0 + baseHeight, z, currBuilding)
            
    # Delete buildings not on specified vertices of grid
    for j in range (1, numBuildings + 1):
        if j <= oddRow:
            cmds.delete('building%s' % (j))
        for k in range (1, maxDimension + 1):
            if (j > k * evenRow) and (j <= k * evenRow + oddRow):
                cmds.delete('building%s' % (j))
        # Rename buildings
        if cmds.objExists('building%s' % (j)):
            cmds.rename('building%s' % (j), 'cityBuilding')
    cmds.rename('cityBuilding', 'cityBuilding0')
            
    # Select roads across width
    widthStep = (width * 2) * 2
    randomRoadStart = random.randrange(0, numFaces, widthStep)
    print(randomRoadStart)
    for a in range (0, numFaces):
        if (a >= randomRoadStart) and (a < randomRoadStart + widthStep):
            cmds.select('basePlane*.f[%s]' % (a), add=True)
    
    fullNumBuildings = width * height        
    buildingRowNum = randomRoadStart / widthStep
    print(buildingRowNum)
    for b in range (0, fullNumBuildings):
        if (b >= buildingRowNum * width) and (b < buildingRowNum * width + width):
            if cmds.objExists('cityBuilding%s' % (b)):
                cmds.delete('cityBuilding%s' % (b))
                    
    # Select roads across height
    heightStep = 2
    randomRoadStart = random.randrange(0, width * 2, heightStep)
    print(randomRoadStart)
    for a in range (0, numFaces):
        if ((a % (widthStep / 2)) == randomRoadStart) or ((a % (widthStep / 2)) == (randomRoadStart + 1)):
            cmds.select('basePlane*.f[%s]' % (a), add=True)
            
    buildingColNum = randomRoadStart / heightStep
    print(buildingColNum)
    for b in range (0, fullNumBuildings):
        if ((b % width) == buildingColNum):
            if cmds.objExists('cityBuilding%s' % (b)):
                cmds.delete('cityBuilding%s' % (b))
                
    # Extrude road
    cmds.polyExtrudeFacet( offset=0.1, localTranslateZ=-(baseHeight - (baseHeight / 5)) )
                
# UI Window
class cityGeneratorUI():
    
    # Constructor
    def __init__(self):
        
        self.windowID = 'cityGeneratorWindow'
    
        # Check if window already open & close it
        if cmds.window( self.windowID, exists=True ):
            cmds.deleteUI( self.windowID )
        
        # Create new window
        self.window = cmds.window( self.windowID, title='City Generator', resizeToFitChildren=True)
        cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1,125), (2,115), (3,50) ], columnOffset=[ (1,'right',3) ] )
        
        # Formatting - Blank row
        cmds.separator( h=15, style='none' )
        cmds.separator( h=15, style='none' )
        cmds.separator( h=15, style='none' )
        
        # Building foundation dimensions
        cmds.text( label='City Width' )
        self.cityWidth = cmds.intField( minValue=5, maxValue=25, value=5 )
        cmds.separator( h=10, style='none' )
        
        cmds.text( label='City Height' )
        self.cityHeight = cmds.intField( minValue=5, maxValue=25, value=5 )
        cmds.separator( h=10, style='none' )
        
        # Formatting - Blank row
        cmds.separator( h=10, style='none' )
        cmds.separator( h=10, style='none' )
        cmds.separator( h=10, style='none' )
        
        # Generate city base plane button
        cmds.separator( h=15, style='none' )
        cmds.button( label = "Generate Ground", command=self.groundSpecs )
        cmds.separator( h=15, style='none' )
        
        # Formatting - Blank row
        cmds.separator( h=10, style='none' )
        cmds.separator( h=10, style='none' )
        cmds.separator( h=10, style='none' )
        
        cmds.text( label='Max Building Height' )
        self.maxBuildingHeight = cmds.intField( minValue=0, maxValue=10, value=3 )
        cmds.separator( h=10, style='none' )
        
        cmds.text( label='Max Base Size' )
        self.buildingSpacing = cmds.intField( minValue=0, maxValue=10, value=5 )
        cmds.separator( h=10, style='none' )
        
        # Formatting - Blank row
        cmds.separator( h=10, style='none' )
        cmds.separator( h=10, style='none' )
        cmds.separator( h=10, style='none' )
        
        # Generate buildings button
        cmds.button( label = "Clear Buildings", command=self.deleteCity )
        cmds.button( label = "Generate Buildings", command=self.citySpecs )
        cmds.separator( h=15, style='none' )
        
        # Formatting - Blank row
        cmds.separator( h=15, style='none' )
        cmds.separator( h=15, style='none' )
        cmds.separator( h=15, style='none' )
        
        # Display window   
        cmds.showWindow()
        
    def groundSpecs(self, *args):
        
        # Base plane dimensions
        cityWidth = cmds.intField( self.cityWidth, query=True, value=True)
        cityHeight = cmds.intField( self.cityHeight, query=True, value=True)
        
        print(cityWidth, cityHeight)
        
        # Function call
        createBasePlane(cityWidth, cityHeight)
        
    def citySpecs(self, *args):
        
        # Building specs
        cityWidth = cmds.intField( self.cityWidth, query=True, value=True)
        cityHeight = cmds.intField( self.cityHeight, query=True, value=True)
        maxBuildingHeight = cmds.intField( self.maxBuildingHeight, query=True, value=True)
        buildingSpacing = cmds.intField( self.buildingSpacing, query=True, value=True)
        
        print(cityWidth, cityHeight, maxBuildingHeight, buildingSpacing)
        
        # Function call
        createCity(cityWidth, cityHeight, maxBuildingHeight, buildingSpacing)
    
    def deleteCity(self, *args):
        
        # Function call
        deleteCity()
    
# UI Instantiation   
window = cityGeneratorUI()