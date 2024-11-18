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
        EndIdx = EndIdx - 1
    for i in range(EndIdx):
        print(i)
        LineTags.append(factory.addLine(PointTags[i], PointTags[(i + 1) % N]))

    return LineTags

InnerGripperHeight = (Constants.GripperWidth - Constants.WallThickness) / np.cos(Constants.Theta)
Phi = np.arctan2(Constants.GripperWidth - Constants.WallThickness, InnerGripperHeight)

P0 = factory.addPoint(Constants.GripperWidth - Constants.WallThickness, 0, 0)
P1 = factory.addPoint(Constants.GripperWidth, 0, 0)
P2 = factory.addPoint(Constants.WallThickness, Constants.GripperHeight + Constants.GripperHeightGift, 0)
P3 = factory.addPoint(0, Constants.GripperHeight + Constants.GripperHeightGift, 0)
P4 = factory.addPoint(0, InnerGripperHeight, 0)

PointTags = [P0, P1, P2, P3, P4]

BarPositions = np.linspace(0, InnerGripperHeight, Constants.NBars + 2)

for BarPosition in BarPositions[1:-1]:
    print(f"BarPosition:{BarPosition}")
    StepWidth = 0.1

    BarTotalLength = np.tan(Phi) * BarPosition

    BarTopLength = np.tan(Phi) * (BarPosition - Constants.BarHeightThin / 2)
    BarBottomLength = np.tan(Phi) * (BarPosition + Constants.BarHeightThin / 2)

    if BarTotalLength < Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P1Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P2Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        P3Bar = factory.addPoint(BarBottomLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)

        PointTags += [P0Bar, P1Bar, P2Bar, P3Bar]

    if BarTotalLength > Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P1Bar = factory.addPoint(BarTopLength - Constants.BarThinLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P2Bar = factory.addPoint(BarTopLength - Constants.BarThinLength - StepWidth, InnerGripperHeight - (BarPosition - Constants.BarHeightThick / 2), 0)
        P3Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition - Constants.BarHeightThick / 2), 0)
        P4Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition + Constants.BarHeightThick / 2), 0)
        P5Bar = factory.addPoint(BarBottomLength - Constants.BarThinLength - StepWidth, InnerGripperHeight - (BarPosition + Constants.BarHeightThick / 2), 0)
        P6Bar = factory.addPoint(BarBottomLength - Constants.BarThinLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        P7Bar = factory.addPoint(BarBottomLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)

        PointTags += [P0Bar, P1Bar, P2Bar, P3Bar, P4Bar, P5Bar, P6Bar, P7Bar]

LineTags = addLines(PointTags)

print(LineTags)
WireTag = factory.addWire(LineTags)
SurfaceDimTag = (2, factory.addPlaneSurface([WireTag]))
ExtrudeOut = factory.extrude([SurfaceDimTag], 0, 0, Constants.Depth)
HalfDimTag = ExtrudeOut[1]
CopyDimTags = factory.copy([HalfDimTag])
factory.symmetrize(CopyDimTags, 1, 0, 0, 0)
# Fusionar las dos mitades y asignar el resultado a 'FullGripper'
FullGripper = factory.fuse(CopyDimTags, [HalfDimTag])[0]
print(f"ExtrudeOut:{ExtrudeOut}")
factory.synchronize()

# === Añadir el cilindro inclinado ===

# Definir el ángulo de inclinación en grados (negativo para inclinar hacia abajo)
inclination_angle_deg = -40  # Ajusta este valor según la inclinación deseada
inclination_angle_rad = np.radians(inclination_angle_deg)

# Definir el radio y longitud del cilindro
ChannelRadius = 0.3  # Ajusta este valor al radio deseado
ChannelLength = Constants.GripperWidth + 30  # Aumenta la longitud para asegurar que atraviesa la garra

# Calcular los componentes del vector dirección del cilindro
dx = ChannelLength * np.cos(inclination_angle_rad)
dy = ChannelLength * np.sin(inclination_angle_rad)
dz = 0  # Mantener en cero para inclinación en el plano X-Y

# Posición del cilindro: lo colocamos en el centro en Y y Z
cylinder_center_y = (Constants.GripperHeight + Constants.GripperHeightGift) / 2
cylinder_center_z = Constants.Depth / 2

# Posición inicial del cilindro
x_base = -18  # Comienza un poco antes de la garra en X
y_base = cylinder_center_y  # Centro en Y
z_base = cylinder_center_z  # Centro en Z

# Crear el cilindro inclinado
Channel = factory.addCylinder(
    x_base,
    y_base,
    z_base,
    dx,
    dy,
    dz,
    ChannelRadius
)

factory.synchronize()

# === Realizar la operación de corte para crear el agujero ===

# Obtenemos el tag del volumen de la garra fusionada
# FullGripper es una lista de entidades resultantes de la fusión
# Necesitamos extraer los volúmenes resultantes

# Obtener todos los volúmenes (dim=3)
all_volumes = gmsh.model.getEntities(dim=3)
print("Volúmenes:", all_volumes)

# Asumimos que el primer volumen es la garra completa
gripper_volume_tag = all_volumes[0][1]

# Realizar el corte
GripperWithHole = factory.cut(
    [(3, gripper_volume_tag)],
    [(3, Channel)],
    removeTool=True
)

factory.synchronize()

# === Generar la malla y exportar los archivos ===

# Generar la malla 3D
gmsh.model.mesh.generate(3)

# Exportar los archivos
gmsh.model.mesh.generate(3)
gmsh.write("FinRay_with_Hole.vtk")
gmsh.model.mesh.clear()
gmsh.model.mesh.generate(2)
gmsh.model.mesh.refine()
gmsh.model.mesh.refine()
gmsh.write("FinRay_with_Hole.stl")

# Opcional: Mostrar la geometría en la interfaz gráfica
launchGUI()

# Finalizar Gmsh
gmsh.finalize()