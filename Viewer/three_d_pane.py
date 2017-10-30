from .pane import Pane

import vtk

class ThreeDPane(Pane):
    def __init__(self, uid, renderer):
        super().__init__(uid, renderer)
        self.motionFactor = 10.0  
        self.mouseWheelMotionFactor = 0.2

    #################################################################
    ## Camera Methods
    #################################################################    

    #protected method
    def rotate(self, previousEventPosition, currentEventPosition):
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
        self._rerender()