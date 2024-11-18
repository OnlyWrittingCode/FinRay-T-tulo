import Sofa

import os
path = os.path.dirname(os.path.abspath(__file__))+'/mesh/'

def createScene(rootNode):

                rootNode.addObject('RequiredPlugin', pluginName='SoftRobots SofaOpenglVisual SofaSparseSolver SofaPreconditioner')
                rootNode.addObject('VisualStyle', displayFlags='showVisualModels hideBehaviorModels showCollisionModels hideBoundingCollisionModels showForceFields showInteractionForceFields hideWireframe')

                rootNode.addObject('FreeMotionAnimationLoop')
                rootNode.addObject('GenericConstraintSolver', maxIterations=100, tolerance = 0.0000001)

		#model
                model = rootNode.addChild('model')
                model.addObject('EulerImplicitSolver', name='odesolver')
                # model.addObject('ShewchukPCGLinearSolver', iterations=15, name='linearsolver', tolerance=1e-5, preconditioners='preconditioner', use_precond=True, update_step=1)

                model.addObject('MeshVTKLoader', name='loader', filename='Geometries/FinRay.vtk')
                model.addObject('TetrahedronSetTopologyContainer', src='@loader', name='container')
                model.addObject('TetrahedronSetTopologyModifier')

                model.addObject('MechanicalObject', name='tetras', template='Vec3', showIndices=False)
                model.addObject('UniformMass', totalMass=0.5)
                model.addObject('TetrahedronFEMForceField', template='Vec3', name='FEM', method='large', poissonRatio=0.3,  youngModulus=18000)

                model.addObject('BoxROI', name='boxROI', box=[-50, -5, -30,  50, 2, 30], drawBoxes=True, position="@tetras.rest_position", tetrahedra="@container.tetrahedra")
                model.addObject('RestShapeSpringsForceField', points='@boxROI.indices', stiffness=1e12)

                model.addObject('SparseLDLSolver', name='preconditioner')
                model.addObject('LinearSolverConstraintCorrection', linearSolver='@preconditioner')
                #model.addObject('UncoupledConstraintCorrection')

                ##########################################
                # Visualization                          #
                ##########################################

                modelVisu = model.addChild('visu')
                modelVisu.addObject('MeshSTLLoader', filename="Geometries/FinRay.stl", name="loader", rotation=[0,0,0])
                modelVisu.addObject('OglModel', src="@loader", scale3d=[1, 1, 1])
                modelVisu.addObject('BarycentricMapping')




                return rootNode
