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
    EndIdx = N
    if not Close:
        EndIdx -= 1
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

# ---------------------------
# Creación de Líneas
# ---------------------------

# Crear líneas para la pared interna
LineTags_inner = addLines(PointTags_inner)

# Crear líneas para la pared externa (mismas que la interna)
LineTags_outer = LineTags_inner.copy()

# ---------------------------
# Creación de Wires y Superficies
# ---------------------------

# Wire y superficie para la pared interna
WireTag_inner = factory.addWire(LineTags_inner)
SurfaceTag_inner = factory.addPlaneSurface([WireTag_inner])

# Wire y superficie para la pared externa
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

    if BarTotalLength < Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P1Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P2Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        P3Bar = factory.addPoint(BarBottomLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)

        PointTags_bars += [P0Bar, P1Bar, P2Bar, P3Bar]

    if BarTotalLength > Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P1Bar = factory.addPoint(BarTopLength - Constants.BarThinLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P2Bar = factory.addPoint(BarTopLength - Constants.BarThinLength - StepWidth, InnerGripperHeight - (BarPosition - Constants.BarHeightThick / 2), 0)
        P3Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition - Constants.BarHeightThick / 2), 0)
        P4Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition + Constants.BarHeightThick / 2), 0)
        P5Bar = factory.addPoint(BarBottomLength - Constants.BarThinLength - StepWidth, InnerGripperHeight - (BarPosition + Constants.BarHeightThick / 2), 0)
        P6Bar = factory.addPoint(BarBottomLength - Constants.BarThinLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        P7Bar = factory.addPoint(BarBottomLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)

        PointTags_bars += [P0Bar, P1Bar, P2Bar, P3Bar, P4Bar, P5Bar, P6Bar, P7Bar]

# Crear líneas para las barras internas
LineTags_bars = addLines(PointTags_bars)

# Crear wire y superficie para las barras internas
WireTag_bars = factory.addWire(LineTags_bars)
SurfaceTag_bars = factory.addPlaneSurface([WireTag_bars])

# ---------------------------
# Extrusión de Superficies
# ---------------------------

# Extruir la pared interna (Depth = Constants.Depth)
Extrude_inner = factory.extrude([(2, SurfaceTag_inner)], 0, 0, Constants.Depth)
Vol_inner = Extrude_inner[1][1]

# Extruir la pared externa (DepthOuter = Constants.DepthOuter)
Extrude_outer = factory.extrude([(2, SurfaceTag_outer)], 0, 0, Constants.DepthOuter)
Vol_outer = Extrude_outer[1][1]

# Extruir las barras internas (Depth = Constants.Depth)
Extrude_bars = factory.extrude([(2, SurfaceTag_bars)], 0, 0, Constants.Depth)
Vol_bars = Extrude_bars[1][1]

# Alinear la pared externa con la interna en el eje Z
DepthDifference = Constants.DepthOuter - Constants.Depth
factory.translate([(3, Vol_outer)], 0, 0, -DepthDifference)

# Fusionar la pared interna con las barras internas
factory.synchronize()
Solid_inner = factory.fuse([(3, Vol_inner)], [(3, Vol_bars)], removeObject=True, removeTool=True)[0]

# Fusionar el sólido interno con la pared externa
factory.synchronize()
Solid_combined = factory.fuse(Solid_inner, [(3, Vol_outer)], removeObject=True, removeTool=True)[0]

# Copiar y reflejar el sólido combinado para crear la garra completa
CopyDimTags = factory.copy(Solid_combined)
factory.symmetrize(CopyDimTags, 1, 0, 0, 0)  # Reflejar en el plano YZ

factory.synchronize()

# Fusionar las dos mitades para obtener la garra completa
result = factory.fuse(Solid_combined, CopyDimTags, removeObject=True, removeTool=True)
FullGripper = result[0]

factory.synchronize()

# Obtener todos los volúmenes de la garra completa
FullGripperVolumes = FullGripper

# ---------------------------
# Duplicar y Posicionar la Garra Completa
# ---------------------------

# Hacer una copia de la garra completa incluyendo todas las entidades
DuplicatedGripper = factory.copy(FullGripperVolumes)

# Rotar la garra duplicada 180 grados alrededor del eje Y
factory.rotate(DuplicatedGripper, 0, 0, 0, 0, 1, 0, np.pi)

# Desplazar la copia en el eje Z para dejar un espacio entre las garras
SpaceBetweenGrippers_Z = -3  # Ajusta este valor según el espacio deseado
factory.translate(DuplicatedGripper, 0, 0, SpaceBetweenGrippers_Z)

factory.synchronize()

# Fusionar ambas garras
TotalGripper = factory.fuse(FullGripperVolumes, DuplicatedGripper, removeObject=True, removeTool=True)[0]

factory.synchronize()

# Añadir la garra como un grupo físico
gmsh.model.addPhysicalGroup(3, [vol[1] for vol in TotalGripper], tag=1, name="Gripper")

# ---------------------------
# Función para Crear una Ranura Inclinada
# ---------------------------

def create_inclined_slot(slot_width, slot_height, slot_depth, inclination_angle, position):
    # Crear el prisma de la ranura en el origen
    slot = factory.addBox(
        0,
        0,
        0,
        slot_width,
        slot_height,
        slot_depth
    )
    slot_volume = [(3, slot)]

    factory.synchronize()

    # Rotar la ranura alrededor del eje Z
    factory.rotate(slot_volume, 0, 0, 0, 0, 0, 1, -0.30)

    # Trasladar la ranura a la posición deseada
    factory.translate(slot_volume, *position)

    factory.synchronize()

    return slot_volume

def create_inclined_slot2(slot_width, slot_height, slot_depth, inclination_angle, position):
    # Crear el prisma de la ranura en el origen
    slot = factory.addBox(
        0,
        0,
        0,
        1,
        0.5,
        20
    )
    slot_volume2 = [(3, slot)]

    factory.synchronize()

    # Rotar la ranura alrededor del eje Z
    factory.rotate(slot_volume2, 0, 0, 0, 0, 0, 1, -0.30)

    # Trasladar la ranura a la posición deseada
    factory.translate(slot_volume2, *position)

    factory.synchronize()

    return slot_volume2

# ---------------------------
# Creación de la Ranura Inclinada
# ---------------------------

# Definir las dimensiones y posición de la ranura desde Constants.py
SlotWidth = Constants.SlotWidth
SlotHeight = Constants.SlotHeight
SlotDepth = Constants.SlotDepth
InclinationAngle = 0  # Ángulo de inclinación de las paredes
SlotPosition = (Constants.SlotX, Constants.SlotY, Constants.SlotZ)
SlotPosition2 = (Constants.SlotX, Constants.SlotY, 0)
SlotPosition3 = (Constants.SlotX, Constants.SlotY, -3)
SlotPosition4 = (Constants.SlotX, Constants.SlotY, -6)

verticalpos = (-26, 25, -10)
verticalpos2 = (-22, 38, -10)
verticalpos3 = (-18, 51, -10)
verticalpos4 = (-13.9695768086, 64, -10)
verticalpos5 = (-9.9555257087, 77, -10)
verticalpos6 = (-5.9414746088, 90, -10)

# Crear las ranuras inclinadas y verticales
SlotVolume = create_inclined_slot(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, SlotPosition)
SlotVolume2 = create_inclined_slot(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, SlotPosition2)
SlotVolume3 = create_inclined_slot(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, SlotPosition3)
SlotVolume4 = create_inclined_slot(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, SlotPosition4)

vertical = create_inclined_slot2(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, verticalpos)
vertical2 = create_inclined_slot2(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, verticalpos2)
vertical3 = create_inclined_slot2(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, verticalpos3)
vertical4 = create_inclined_slot2(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, verticalpos4)
vertical5 = create_inclined_slot2(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, verticalpos5)
vertical6 = create_inclined_slot2(SlotWidth, SlotHeight, SlotDepth, InclinationAngle, verticalpos6)

# Añadir las ranuras como grupos físicos para visualizar
gmsh.model.addPhysicalGroup(3, [SlotVolume[0][1]], tag=2, name="SlotPrism")
gmsh.model.addPhysicalGroup(3, [SlotVolume2[0][1]], tag=3, name="SlotPrism2")
gmsh.model.addPhysicalGroup(3, [SlotVolume3[0][1]], tag=4, name="SlotPrism3")
gmsh.model.addPhysicalGroup(3, [SlotVolume4[0][1]], tag=5, name="SlotPrism4")
gmsh.model.addPhysicalGroup(3, [vertical[0][1]], tag=6, name="vertical")
gmsh.model.addPhysicalGroup(3, [vertical2[0][1]], tag=7, name="vertical2")
gmsh.model.addPhysicalGroup(3, [vertical3[0][1]], tag=8, name="vertical3")
gmsh.model.addPhysicalGroup(3, [vertical4[0][1]], tag=9, name="vertical4")
gmsh.model.addPhysicalGroup(3, [vertical5[0][1]], tag=10, name="vertical5")
gmsh.model.addPhysicalGroup(3, [vertical6[0][1]], tag=11, name="vertical6")

# ---------------------------
# Realizar la Operación de Corte
# ---------------------------

# Realizar la operación de corte
GripperWithSlot = factory.cut(TotalGripper, SlotVolume, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, SlotVolume2, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, SlotVolume3, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, SlotVolume4, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, vertical, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, vertical2, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, vertical3, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, vertical4, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, vertical5, removeObject=True, removeTool=True)[0]
GripperWithSlot = factory.cut(GripperWithSlot, vertical6, removeObject=True, removeTool=True)[0]

factory.synchronize()

# ---------------------------
# Agregar una Base a la Garra
# ---------------------------

# Definir las dimensiones de la base
BaseWidth = 80    # Ancho de la base en mm
BaseDepth = 5    # Profundidad de la base en mm
BaseHeight = 30    # Altura de la base en mm

# Posición de la base (colocada debajo de la garra)
BaseX = -BaseWidth / 2   # Centramos la base en X
BaseY = -BaseDepth / 2   # Centramos la base en Y
BaseZ = -BaseHeight      # Colocamos la base justo debajo de la garra

# Crear la base
BaseTag = factory.addBox(BaseX, BaseY, BaseZ, BaseWidth, BaseDepth, BaseHeight)
BaseVolume = [(3, BaseTag)]

# Rotar solo la base 45 grados alrededor del eje Z
factory.rotate(BaseVolume, 0, 0, 0, 0, 0, 1, 0)

factory.synchronize()

# Fusionar la base rotada con la garra
GripperWithBase = factory.fuse(GripperWithSlot, BaseVolume, removeObject=True, removeTool=True)[0]

factory.synchronize()

# Añadir el modelo final como un grupo físico
gmsh.model.addPhysicalGroup(3, [vol[1] for vol in GripperWithBase], tag=100, name="GripperWithBase")

# ---------------------------
# Generación de la Malla y Exportación
# ---------------------------

# Generar la malla 3D
gmsh.model.mesh.generate(3)

# Exportar a VTK y STL
gmsh.write("FinRayWithBaseRotated.vtk")
gmsh.write("FinRayWithBaseRotated.stl")

# Lanzar la interfaz gráfica para visualizar la geometría
launchGUI()

# Finalizar Gmsh
gmsh.finalize()
