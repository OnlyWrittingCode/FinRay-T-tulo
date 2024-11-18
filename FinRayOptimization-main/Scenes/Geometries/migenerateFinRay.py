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
    LineTags = []
    if not Close:
        EndIdx -= 1
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

# Extruir la pared interna (Depth = 10)
Extrude_inner = factory.extrude([(2, SurfaceTag_inner)], 0, 0, Constants.Depth)
Vol_inner = Extrude_inner[1][1]

# Extruir la pared externa (DepthOuter = 13)
Extrude_outer = factory.extrude([(2, SurfaceTag_outer)], 0, 0, Constants.DepthOuter)
Vol_outer = Extrude_outer[1][1]

# Extruir las barras internas (Depth = 10)
Extrude_bars = factory.extrude([(2, SurfaceTag_bars)], 0, 0, Constants.Depth)
Vol_bars = Extrude_bars[1][1]

# Alinear la pared externa con la interna en el eje Z
DepthDifference = Constants.DepthOuter - Constants.Depth
factory.translate([(3, Vol_outer)], 0, 0, -DepthDifference)

# Fusionar la pared interna con las barras internas
factory.synchronize()
Solid_inner = factory.fuse([(3, Vol_inner)], [(3, Vol_bars)])[0]

# Fusionar el sólido interno con la pared externa
factory.synchronize()
Solid_combined = factory.fuse(Solid_inner, [(3, Vol_outer)])[0]

# Copiar y reflejar el sólido combinado para crear la garra completa
CopyDimTags = factory.copy(Solid_combined)
factory.symmetrize(CopyDimTags, 1, 0, 0, 0)  # Reflejar en el plano YZ

factory.synchronize()

# Fusionar las dos mitades para obtener la garra completa
result = factory.fuse(Solid_combined, CopyDimTags)
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

# Opcional: Fusionar ambas garras en una sola entidad
# Si deseas que sean entidades separadas, puedes omitir este paso
TotalGripper = factory.fuse(FullGripperVolumes, DuplicatedGripper)[0]

factory.synchronize()

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