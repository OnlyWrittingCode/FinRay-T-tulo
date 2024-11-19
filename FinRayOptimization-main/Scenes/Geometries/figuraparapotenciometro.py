import gmsh

gmsh.initialize()
gmsh.model.add("RealBase") 
# P1 = gmsh.model.occ.addPoint(0,0,0)
# P2 = gmsh.model.occ.addPoint(50,0,0)
# P3 = gmsh.model.occ.addPoint(50,10,0)
# P4 = gmsh.model.occ.addPoint(0,10,0)

# L1 = gmsh.model.occ.addLine(P1, P2) 
# L2 = gmsh.model.occ.addLine(P2, P3) 
# L3 = gmsh.model.occ.addLine(P3, P4) 
# L4 = gmsh.model.occ.addLine(P4, P1) 

# WireTag = gmsh.model.occ.addWire([L1,L2,L3,L4])

# SurfaceTag = gmsh.model.occ.addPlaneSurface([WireTag])

# ExtrudeTag = gmsh.model.occ.extrude([(2,SurfaceTag)], 0, 0, 20)
CajaBase = gmsh.model.occ.addBox(0, 0, 0, 91, 22, 5)

CajaLateral = gmsh.model.occ.addBox(0, 0, 0, -20, 22, 18+5)
#Box2Tag = gmsh.model.occ.addBox(0, -10, 0, -10, 20, 20, tag=1001)

#IMpresion de tag solo para saber cual es cada uno 
#print(BoxTag)
#print(Box2Tag)

#sirve para mostrar en interfaz de gmsh cada vez que se actualiza la figura
#gmsh.model.occ.synchronize()
#gmsh.fltk.run()

#FUSE se usa para juntar figuras    

FuseOut = gmsh.model.occ.fuse([(3,CajaBase)], [(3,CajaLateral)])

CylinderTag = gmsh.model.occ.addCylinder(-10, 22-6, 18, 0, 0, 12, 3.55)
CylinderTag2 = gmsh.model.occ.addCylinder(-14, 6, 18, 0, 0, 12, 3.55)

FuseOut2 = gmsh.model.occ.fuse([(3,CajaBase)], [(3,CylinderTag)])

#print(FuseOut2)
FuseOut3 = gmsh.model.occ.fuse([(3,4)], [(3,CylinderTag2)])


#print(FuseOut)
#LShapeDimTag = FuseOut[0][0]
#print(LShapeDimTag)


#CylinderTag = gmsh.model.occ.addCylinder(0, 0, 0, 5, 0, 30, 5)

#COrtar una figura de otra 
#gmsh.model.occ.cut([LShapeDimTag], [(3,CylinderTag)])

gmsh.model.occ.synchronize()
gmsh.model.mesh.generate(2)

gmsh.write("BasePotencio.step")

gmsh.fltk.run()