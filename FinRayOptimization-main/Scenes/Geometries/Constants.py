import numpy as np

# Parámetros de la Garra
GripperHeight = 100                # Altura total de la garra en mm
GripperWidth = 33                  # Ancho de la garra en mm
WallThickness = 1.5                # Espesor de las paredes en mm
GripperHeightGift = 2              # Margen adicional en la altura de la garra en mm

# Ángulos y Cálculos Derivados
Theta = np.arctan2(GripperHeight, GripperWidth)
Phi = np.arctan2(GripperWidth, GripperHeight)

# Profundidades
Depth = 5                          # Profundidad de la pared interna y barras internas en mm
DepthOuter = 12                    # Profundidad de la pared externa en mm

# Barras Internas
BarHeightThick = 2                 # Altura de las barras gruesas en mm
BarHeightThin = 1                  # Altura de las barras delgadas en mm
BarThinLength = 3                  # Longitud de transición entre barras delgadas y gruesas en mm
NBars = 7                          # Número de conjuntos de barras internas

# Parámetros para la Ranura Manual
SlotWidth = 1.5                    # Ancho de la ranura en mm
SlotHeight = 110                   # Altura de la ranura en mm
SlotDepth = 0.5                    # Profundidad de la ranura (ligeramente mayor que la pared externa)

# Posición de la Ranura
SlotX = -34                        # Posición en X de la esquina inferior izquierda de la ranura en mm
SlotY = 0                          # Posición en Y de la esquina inferior izquierda de la ranura en mm
SlotZ = 3                          # Posición en Z de la ranura (nivel base)

# Otros Parámetros (si es necesario)
# Añade aquí cualquier otro parámetro que necesites

print(Theta)
print(Phi)
