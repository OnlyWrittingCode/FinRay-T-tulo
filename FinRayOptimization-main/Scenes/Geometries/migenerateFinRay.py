import gmsh
import numpy as np
import Constants
gmsh.initialize()

launchGUI = gmsh.fltk.run 
factory = gmsh.model.occ

def defineMeshSizes(lc=0.5):   
    #-------------------
    # MeshSizes 
    #-------------------

    gmsh.model.mesh.field.add("Box", 6)
    gmsh.model.mesh.field.setNumber(6, "VIn", lc)
    gmsh.model.mesh.field.setNumber(6, "VOut", lc)
    gmsh.model.mesh.field.setNumber(6, "XMin", -100)
    gmsh.model.mesh.field.setNumber(6, "XMax", 100)
    gmsh.model.mesh.field.setNumber(6, "YMin", 0)
    gmsh.model.mesh.field.setNumber(6, "YMax", 100)
    gmsh.model.mesh.field.setNumber(6, "ZMin", -3*100)
    gmsh.model.mesh.field.setNumber(6, "ZMax", 100)    
    gmsh.model.mesh.field.setNumber(6, "Thickness", 0.3)
     
    gmsh.model.mesh.field.setAsBackgroundMesh(6)
    
    gmsh.option.setNumber("Mesh.CharacteristicLengthExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthFromPoints", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthFromCurvature", 0)

def addLines(PointTags, Close=True):
    N = len(PointTags)
    EndIdx = N
    LineTags = [] 
    if Close is False:
        EndIdx = EndIdx-1
    for i in range(EndIdx):
        print(i)
        LineTags.append(factory.addLine(PointTags[i], PointTags[(i+1)%N]))
    
    return LineTags
        
        
InnerGripperHeight = (Constants.GripperWidth-Constants.WallThickness)/np.cos(Constants.Theta) 
Phi = np.arctan2(Constants.GripperWidth-Constants.WallThickness,InnerGripperHeight) 

P0 = factory.addPoint(Constants.GripperWidth-Constants.WallThickness, 0, 0)
P1 = factory.addPoint(Constants.GripperWidth, 0, 0)
P2= factory.addPoint(Constants.WallThickness, Constants.GripperHeight+Constants.GripperHeightGift,0)
P3= factory.addPoint(0, Constants.GripperHeight+Constants.GripperHeightGift,0)
P4 = factory.addPoint(0, InnerGripperHeight, 0)

PointTags = [P0,P1,P2,P3,P4]

BarPositions = np.linspace(0, InnerGripperHeight, Constants.NBars+2)

for BarPosition in BarPositions[1:-1]:
    print(f"BarPosition:{BarPosition}")
    StepWidth = 0.1
    
    BarTotalLength = np.tan(Phi)*BarPosition
    
    BarTopLength = np.tan(Phi)*(BarPosition-Constants.BarHeightThin/2)
    BarBottomLength = np.tan(Phi)*(BarPosition+Constants.BarHeightThin/2)
    
    if BarTotalLength < Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
        P1Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
        P2Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)
        P3Bar = factory.addPoint(BarBottomLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)
        
        PointTags += [P0Bar, P1Bar, P2Bar,P3Bar]
    
    if BarTotalLength > Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
        P1Bar = factory.addPoint(BarTopLength-Constants.BarThinLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
        P2Bar = factory.addPoint(BarTopLength-Constants.BarThinLength-StepWidth,InnerGripperHeight-(BarPosition-Constants.BarHeightThick/2),0)        
        P3Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition-Constants.BarHeightThick/2),0)
        P4Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition+Constants.BarHeightThick/2),0)        
        P5Bar = factory.addPoint(BarBottomLength-Constants.BarThinLength-StepWidth,InnerGripperHeight-(BarPosition+Constants.BarHeightThick/2),0)        
        P6Bar = factory.addPoint(BarBottomLength-Constants.BarThinLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)  
        P7Bar = factory.addPoint(BarBottomLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)
        
        PointTags += [P0Bar, P1Bar, P2Bar, P3Bar, P4Bar,P5Bar,P6Bar,P7Bar]


LineTags = addLines(PointTags)

print(LineTags)
WireTag = factory.addWire(LineTags)
SurfaceDimTag = (2,factory.addPlaneSurface([WireTag]))
ExtrudeOut = factory.extrude([SurfaceDimTag], 0, 0, Constants.Depth)
HalfDimTag = ExtrudeOut[1]
CopyDimTags = factory.copy([HalfDimTag])
factory.symmetrize(CopyDimTags, 1, 0, 0, 0)
factory.fuse(CopyDimTags, [HalfDimTag])
print(f"ExtrudeOut:{ExtrudeOut}")
factory.synchronize()

# defineMeshSizes(2)
gmsh.model.mesh.generate(3)
gmsh.write("FinRay.vtk")
gmsh.model.mesh.clear()
gmsh.model.mesh.generate(2)
gmsh.model.mesh.refine()
gmsh.model.mesh.refine()
gmsh.write("FinRay.stl")

factory.synchronize()

launchGUI()