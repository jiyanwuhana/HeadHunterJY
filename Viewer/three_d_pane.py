from .pane import Pane

import vtk

class ThreeDPane(Pane):
    def __init__(self, uid, renderer):
        super().__init__(uid, renderer)
        self.motionFactor = 10.0  
        self.mouseWheelMotionFactor = 0.2

    #################################################################
    ## Camera Events
    #################################################################    

    def _pan(self, previousEventPosition, currentEventPosition):
        renderer = self.renderer
        camera = renderer.GetActiveCamera()
        viewFocus = camera.GetFocalPoint()
        viewPoint = camera.GetPosition()
        focalDepth = viewFocus[2]
        newPickPoint =  _computeWorldToDisplay(renderer, (currentEventPosition[0],currentEventPosition[1],focalDepth))
        oldPickPoint = _computeWorldToDisplay(renderer, (previousEventPosition[0],previousEventPosition[1],focalDepth))
        motionVector = [(pos[0]-pos[1]) for pos in slice(oldPickPoint, newPickPoint)]
        
        newFocalPoint = [(pos[0]+pos[1]) for pos in slice(motionVector, viewFocus)]
        newPosition = [(pos[0]+pos[1]) for pos in slice(motionVector, viewPoint)]
        camera.SetFocalPoint(newFocalPoint)
        camera.SetPosition(newPosition)

        renderer.UpdateLightsGeometryToFollowCamera()

    def _rotate(self, previousEventPosition, currentEventPosition):
        renderer = self.renderer
        translationVector = (currentEventPosition[0]-previousEventPosition[0], currentEventPosition[1]-previousEventPosition[1])
        size = renderer.GetRenderWindow().GetSize()
        delta_elevation = -20.0/size[1]
        delta_azimuth = -20.0/size[0]

        rxf = translationVector[0] * delta_azimuth * self.motionFactor
        ryf = translationVector[1] * delta_elevation * self.motionFactor

        camera = renderer.GetActiveCamera()
        camera.Azimuth(rxf)
        camera.Elevation(ryf)
        camera.OrthogonalizeViewUp()

        renderer.ResetCameraClippingRange()
        renderer.UpdateLightsGeometryToFollowCamera()
        self.renderer.Render()

    def _spin(self, previousEventPosition, currentEventPosition):
        renderer = self.renderer
        center = renderer.GetCenter()
        newVector = (currentEventPosition[1]-center[1], currentEventPosition[0]-center[0]) #
        oldVector = (previousEventPosition[1]-center[1], previousEventPosition[0]-center[0])
        newAngle = vtk.vtkMath.DegreesFromRadians(atan2(newVector))
        oldAngle = vtk.vtkMath.DegreesFromRadians(atan2(oldVector))

        camera = renderer.GetActiveCamera()
        camera.Roll(newAngle-oldAngle)
        camera.OrthogonalizeViewUp()

    def _dolly(self, dolly_value): #right click dolly
        renderer=self.renderer
        camera = renderer.GetActiveCamera()
        if camera.GetParallelProjection():
          camera.SetParallelScale(camera.GetParallelScale()*dolly_value)
        else:
          camera.Dolly(dolly_value)
          renderer.ResetCameraClippingRange()
          renderer.UpdateLightsGeometryToFollowCamera()
        self.renderer.Render()

    #################################################################
    ## Utility Methods
    #################################################################

    def _computeWorldToDisplay(self, value):
        coord = vtk.vtkCoordinate()
        coord.SetCoordinateSystemToWorld()
        coord.SetValue(value)
        return coord.GetComputeDisplayValue(self.renderer) 