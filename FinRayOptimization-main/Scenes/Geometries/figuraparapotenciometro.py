import gmsh

# Inicialización de Gmsh
gmsh.initialize()
gmsh.model.add("BaseWithProtrusions")  # Nombre del modelo

# Parámetros del modelo
length = 91    # Longitud de la base en el eje X (mm)
width = 22     # Ancho de la base en el eje Y (mm)
height = 18    # Altura de la base en el eje Z (mm)
lc = 10       # Tamaño característico de la malla (mm)
grosorlateral = -20   # Grosor lateral (valor negativo indica dirección)
grosorabajo = -5    # Grosor inferior
distancia_cilindro_superio_desde_el_centro = -10
distancia_cilindro_inferior_desde_el_centro = -14
altura_cilindros = 7 #defecto 5
radio_cilindros = 3.55  #defecto 2

# Definición de puntos para la base y estructura
# 1. Definir los puntos de la base rectangular
basep1 = gmsh.model.occ.addPoint(0, 0, 0, lc)  # Punto inferior izquierdo
basep2 = gmsh.model.occ.addPoint(length, 0, 0, lc)  # Punto inferior derecho
basep3 = gmsh.model.occ.addPoint(length, width, 0, lc)  # Punto superior derecho
basep4 = gmsh.model.occ.addPoint(0, width, 0, lc)  # Punto superior izquierdo

# 2. Definir los puntos para el rectángulo izquierdo
izqp5 = gmsh.model.occ.addPoint(0, 0, height, lc)  # Punto superior izquierdo de la estructura izquierda
izqp6 = gmsh.model.occ.addPoint(0, width, height, lc)  # Punto superior derecho de la estructura izquierda

# 3. Puntos de la extensión izquierda
izqextp8 = gmsh.model.occ.addPoint(grosorlateral, width, height, lc)
izqextp7 = gmsh.model.occ.addPoint(grosorlateral, 0, height, lc)
izqextp9 = gmsh.model.occ.addPoint(grosorlateral, 0, grosorabajo, lc)
izqextp10 = gmsh.model.occ.addPoint(grosorlateral, width, grosorabajo, lc)

# 4. Puntos para la parte inferior (debajo de la base)
p11 = gmsh.model.occ.addPoint(length, 0, grosorabajo, lc)
p12 = gmsh.model.occ.addPoint(length, width, grosorabajo, lc)
p13 = gmsh.model.occ.addPoint(0, 0, grosorabajo, lc)
p14 = gmsh.model.occ.addPoint(0, width, grosorabajo, lc)

# Conectar los puntos con líneas para formar la geometría
# 1. Líneas de la base rectangular
l1 = gmsh.model.occ.addLine(basep1, basep2)  # Línea inferior
l2 = gmsh.model.occ.addLine(basep2, basep3)  # Línea derecha
l3 = gmsh.model.occ.addLine(basep3, basep4)  # Línea superior
l4 = gmsh.model.occ.addLine(basep4, basep1)  # Línea izquierda

# 2. Líneas para la estructura izquierda
l5 = gmsh.model.occ.addLine(basep1, izqp5)  
l6 = gmsh.model.occ.addLine(izqp5, izqp6) 
l7 = gmsh.model.occ.addLine(izqp6, basep4)

# 3. Líneas para la parte inferior
l8 = gmsh.model.occ.addLine(basep2, p11) 
l9 = gmsh.model.occ.addLine(basep3, p12) 
l10 = gmsh.model.occ.addLine(p11, p12) 
l11 = gmsh.model.occ.addLine(p11, p13) 
l12 = gmsh.model.occ.addLine(p12, p14) 
l13 = gmsh.model.occ.addLine(p13, p14)
l14 = gmsh.model.occ.addLine(basep1, p13)
l15 = gmsh.model.occ.addLine(basep4, p14)

# 4. Líneas de la extensión izquierda
l16 = gmsh.model.occ.addLine(izqextp7, izqextp8)
l17 = gmsh.model.occ.addLine(izqextp7, izqextp9)
l18 = gmsh.model.occ.addLine(izqextp9, izqextp10)
l19 = gmsh.model.occ.addLine(izqextp10, izqextp8)

# Líneas internas adicionales para conectar la estructura izquierda con la extensión
l20 = gmsh.model.occ.addLine(izqp6, izqextp8)
l21 = gmsh.model.occ.addLine(izqp5, izqextp7)
l22 = gmsh.model.occ.addLine(izqextp9, p13)
l23 = gmsh.model.occ.addLine(p14, izqextp10)

# Crear los wires (bordes) para definir los contornos de las superficies
wire = gmsh.model.occ.addWire([l1, l2, l3, l4])
wire2 = gmsh.model.occ.addWire([l4, l5, l6, l7])
wire3 = gmsh.model.occ.addWire([l10, l9, l8, l2])
wire4 = gmsh.model.occ.addWire([l1, l8, l11, l14])
wire5 = gmsh.model.occ.addWire([l3, l9, l12, l15])
wire6 = gmsh.model.occ.addWire([l11, l13, l12, l10])
wire7 = gmsh.model.occ.addWire([l4, l15, l13, l14])
wire8 = gmsh.model.occ.addWire([l16, l17, l18, l19])
wire9 = gmsh.model.occ.addWire([l5, l14, l22, l17, l21])
wire10 = gmsh.model.occ.addWire([l15, l7, l20, l19, l23])
wire11 = gmsh.model.occ.addWire([l22, l18, l23, l13])
wire12 = gmsh.model.occ.addWire([l20, l16, l21, l6])

# Crear las superficies a partir de los wires
surface = gmsh.model.occ.addPlaneSurface([wire])
surface = gmsh.model.occ.addPlaneSurface([wire2])
surface = gmsh.model.occ.addPlaneSurface([wire3])
surface = gmsh.model.occ.addPlaneSurface([wire4])
surface = gmsh.model.occ.addPlaneSurface([wire5])
surface = gmsh.model.occ.addPlaneSurface([wire6])
surface = gmsh.model.occ.addPlaneSurface([wire7])
surface = gmsh.model.occ.addPlaneSurface([wire8])
surface = gmsh.model.occ.addPlaneSurface([wire9])
surface = gmsh.model.occ.addPlaneSurface([wire10])
surface = gmsh.model.occ.addPlaneSurface([wire11])
surface = gmsh.model.occ.addPlaneSurface([wire12])

# Añadir cilindros (protuberancias) en la parte superior
                                                            # X, Y, Z=height (arriba), altura de 5 mm, radio de 2 mm
cylinder1 = gmsh.model.occ.addCylinder(distancia_cilindro_inferior_desde_el_centro, 6, height, 0, 0, altura_cilindros, radio_cilindros)  # Primer cilindro
cylinder2 = gmsh.model.occ.addCylinder(distancia_cilindro_superio_desde_el_centro, width - 6, height, 0, 0, altura_cilindros, radio_cilindros)  # Segundo cilindro

# Sincronizar el modelo (necesario para que Gmsh procese todos los cambios)
gmsh.model.occ.synchronize()

# Generar la malla 2D para el modelo
gmsh.model.mesh.generate(2)

# Exportar el modelo a formato STL
gmsh.write("BasePotencio.step")
gmsh.write("BasePotencio.stl")
gmsh.write("BasePotencio.msh")

# Mostrar el modelo en la interfaz gráfica de Gmsh
gmsh.fltk.run()

# Finalizar Gmsh
gmsh.finalize()