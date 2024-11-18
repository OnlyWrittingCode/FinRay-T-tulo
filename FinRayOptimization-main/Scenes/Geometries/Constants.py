import numpy as np
GripperHeight = 100
Depth = 25
GripperWidth = 30
Theta = np.arctan2(GripperHeight, GripperWidth)
Phi = np.arctan2(GripperWidth, GripperHeight)
GripperHeightGift = 2

WallThickness = 3 


BarHeightThick = 2
BarHeightThin = 1
BarThinLength = 3

NBars = 9

NRowsTactile = 10
NColsTactile = 4