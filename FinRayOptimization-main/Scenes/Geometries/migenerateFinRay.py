import gmsh
import numpy as np
import Constants

# Inicializar Gmsh
gmsh.initialize()

# Definir la interfaz gráfica
launchGUI = gmsh.fltk.run
factory = gmsh.model.occ

def addLines(PointTags, Close=True):
    N = len(PointTags)
    EndIdx = N if Close else N - 1
    LineTags = []
    for i in range(EndIdx):
        LineTags.append(factory.addLine(PointTags[i], PointTags[(i + 1) % N]))
    return LineTags

# Calcular alturas y ángulos
InnerGripperHeight = (Constants.GripperWidth - Constants.WallThickness) / np.cos(Constants.Theta)
Phi = np.arctan2(Constants.GripperWidth - Constants.WallThickness, InnerGripperHeight)

# ---------------------------
# Definición de Puntos para la Garra Completa
# ---------------------------

# Puntos de la pared interna
P0_inner = factory.addPoint(Constants.GripperWidth - Constants.WallThickness, 0, 0)
P1_inner = factory.addPoint(Constants.GripperWidth, 0, 0)
P2_inner = factory.addPoint(Constants.WallThickness, Constants.GripperHeight + Constants.GripperHeightGift, 0)
P3_inner = factory.addPoint(0, Constants.GripperHeight + Constants.GripperHeightGift, 0)
P4_inner = factory.addPoint(0, InnerGripperHeight, 0)
PointTags_inner = [P0_inner, P1_inner, P2_inner, P3_inner, P4_inner]

# Puntos de la pared externa (mismas coordenadas que la interna)
PointTags_outer = PointTags_inner.copy()

# Crear líneas para la pared interna y externa
LineTags_inner = addLines(PointTags_inner)
LineTags_outer = LineTags_inner.copy()

# Crear wires y superficies para las paredes interna y externa
WireTag_inner = factory.addWire(LineTags_inner)
SurfaceTag_inner = factory.addPlaneSurface([WireTag_inner])

WireTag_outer = factory.addWire(LineTags_outer)
SurfaceTag_outer = factory.addPlaneSurface([WireTag_outer])

# ---------------------------
# Creación de Barras Internas
# ---------------------------

PointTags_bars = []
BarPositions = np.linspace(0, InnerGripperHeight, Constants.NBars + 2)

for BarPosition in BarPositions[1:-1]:
    StepWidth = 0.1
    BarTotalLength = np.tan(Phi) * BarPosition
    BarTopLength = np.tan(Phi) * (BarPosition - Constants.BarHeightThin / 2)
    BarBottomLength = np.tan(Phi) * (BarPosition + Constants.BarHeightThin / 2)
    PointTags_bar = []

    if BarTotalLength < Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P1Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P2Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        P3Bar = factory.addPoint(BarBottomLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        PointTags_bar = [P0Bar, P1Bar, P2Bar, P3Bar]
    else:
        P0Bar = factory.addPoint(BarTopLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P1Bar = factory.addPoint(BarTopLength - Constants.BarThinLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P2Bar = factory.addPoint(BarTopLength - Constants.BarThinLength - StepWidth, InnerGripperHeight - (BarPosition - Constants.BarHeightThick / 2), 0)
        P3Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition - Constants.BarHeightThick / 2), 0)
        P4Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition + Constants.BarHeightThick / 2), 0)
        P5Bar = factory.addPoint(BarBottomLength - Constants.BarThinLength - StepWidth, InnerGripperHeight - (BarPosition + Constants.BarHeightThick / 2), 0)
        P6Bar = factory.addPoint(BarBottomLength - Constants.BarThinLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        P7Bar = factory.addPoint(BarBottomLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        PointTags_bar = [P0Bar, P1Bar, P2Bar, P3Bar, P4Bar, P5Bar, P6Bar, P7Bar]

    # Crear líneas para la barra
    LineTags_bar = addLines(PointTags_bar)
    # Crear wire y superficie para la barra
    WireTag_bar = factory.addWire(LineTags_bar)
    SurfaceTag_bar = factory.addPlaneSurface([WireTag_bar])
    PointTags_bars.append(SurfaceTag_bar)

# ---------------------------
# Extrusión de Superficies
# ---------------------------

# Extruir la pared interna y externa
Extrude_inner = factory.extrude([(2, SurfaceTag_inner)], 0, 0, Constants.Depth)
Extrude_outer = factory.extrude([(2, SurfaceTag_outer)], 0, 0, Constants.DepthOuter)

Vol_inner = Extrude_inner[1][1]
Vol_outer = Extrude_outer[1][1]

# Alinear la pared externa con la interna en el eje Z
DepthDifference = Constants.DepthOuter - Constants.Depth
factory.translate([(3, Vol_outer)], 0, 0, -DepthDifference)

# Extruir las barras internas y fusionarlas con el volumen interno
Volumes_bars = []
for SurfaceTag_bar in PointTags_bars:
    Extrude_bar = factory.extrude([(2, SurfaceTag_bar)], 0, 0, Constants.Depth)
    Vol_bar = Extrude_bar[1][1]
    Volumes_bars.append((3, Vol_bar))

factory.synchronize()
Solid_inner = factory.fuse([(3, Vol_inner)], Volumes_bars, removeObject=True, removeTool=True)[0]

# Fusionar el sólido interno con la pared externa
factory.synchronize()
Solid_combined = factory.fuse(Solid_inner, [(3, Vol_outer)], removeObject=True, removeTool=True)[0]

# Copiar y reflejar el sólido combinado para crear la garra completa
CopyDimTags = factory.copy(Solid_combined)
factory.symmetrize(CopyDimTags, 1, 0, 0, 0)

# Fusionar las dos mitades para obtener la garra completa
factory.synchronize()
FullGripper = factory.fuse(Solid_combined, CopyDimTags, removeObject=True, removeTool=True)[0]

# Duplicar y posicionar la garra completa
DuplicatedGripper = factory.copy(FullGripper)
factory.rotate(DuplicatedGripper, 0, 0, 0, 0, 1, 0, np.pi)
factory.translate(DuplicatedGripper, 0, 0, -3)

# Fusionar ambas garras
factory.synchronize()
TotalGripper = factory.fuse(FullGripper, DuplicatedGripper, removeObject=True, removeTool=True)[0]

# Añadir la garra como un grupo físico
gmsh.model.addPhysicalGroup(3, [vol[1] for vol in TotalGripper], tag=1, name="Gripper")

# ---------------------------
# Funciones para Crear Ranuras
# ---------------------------

def create_inclined_slot(slot_width, slot_height, slot_depth, inclination_angle, position):
    slot = factory.addBox(0, 0, 0, slot_width, slot_height, slot_depth)
    slot_volume = [(3, slot)]
    factory.synchronize()
    factory.rotate(slot_volume, 0, 0, 0, 0, 0, 1, -0.30)
    factory.translate(slot_volume, *position)
    factory.synchronize()
    return slot_volume

def create_inclined_slot2(slot_width, slot_height, slot_depth, inclination_angle, position):
    slot = factory.addBox(0, 0, 0, 1, 0.5, 20)
    slot_volume = [(3, slot)]
    factory.synchronize()
    factory.rotate(slot_volume, 0, 0, 0, 0, 0, 1, -0.30)
    factory.translate(slot_volume, *position)
    factory.synchronize()
    return slot_volume

# ---------------------------
# Creación de las Ranuras
# ---------------------------

# Definir las posiciones para las ranuras inclinadas
slot_positions = [
    (Constants.SlotX, Constants.SlotY, Constants.SlotZ),
    (Constants.SlotX, Constants.SlotY, 0),
    (Constants.SlotX, Constants.SlotY, -3),
    (Constants.SlotX, Constants.SlotY, -6)
]

# Crear las ranuras inclinadas
slot_volumes = []
for i, pos in enumerate(slot_positions):
    slot_volume = create_inclined_slot(
        slot_width=Constants.SlotWidth,
        slot_height=Constants.SlotHeight,
        slot_depth=Constants.SlotDepth,
        inclination_angle=0,
        position=pos
    )
    slot_volumes.append(slot_volume)
    gmsh.model.addPhysicalGroup(3, [slot_volume[0][1]], tag=2 + i, name=f"SlotPrism_{i+1}")

# Definir las posiciones para las ranuras verticales
vertical_positions = [
    (-26, 25, -10),
    (-22, 38, -10),
    (-18, 51, -10),
    (-13.9695768086, 64, -10),
    (-9.9555257087, 77, -10),
    (-5.9414746088, 90, -10)
]

# Crear las ranuras verticales
for i, pos in enumerate(vertical_positions):
    vertical_slot = create_inclined_slot2(
        slot_width=Constants.SlotWidth,
        slot_height=Constants.SlotHeight,
        slot_depth=Constants.SlotDepth,
        inclination_angle=0,
        position=pos
    )
    slot_volumes.append(vertical_slot)
    gmsh.model.addPhysicalGroup(3, [vertical_slot[0][1]], tag=6 + i, name=f"Vertical_{i+1}")

# ---------------------------
# Realizar las Operaciones de Corte Secuenciales
# ---------------------------

# Inicializar el modelo de la garra para cortes
gripper = TotalGripper

# Cortar cada ranura secuencialmente
for slot_volume in slot_volumes:
    factory.synchronize()
    gripper = factory.cut(gripper, slot_volume, removeObject=True, removeTool=True)[0]

# Añadir el modelo final como un grupo físico
gmsh.model.addPhysicalGroup(3, [vol[1] for vol in gripper], tag=20, name="GripperWithSlots")

# ---------------------------
# Generación de la Malla y Exportación
# ---------------------------

# Generar la malla 3D
gmsh.model.mesh.generate(3)

# Exportar a VTK y STL
gmsh.write("FinRay.vtk")
gmsh.write("FinRay.stl")

# Lanzar la interfaz gráfica para visualizar la geometría
launchGUI()

# Finalizar Gmsh
gmsh.finalize()
