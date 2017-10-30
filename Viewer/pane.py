import itk
import vtk
from rx.subjects import Subject

class Pane(Subject):

  def __init__(self, uid, renderer):
    super().__init__()
    self.uid = uid
    self.renderer = renderer
    self.scene = {}

  def setViewer(self, viewer):
  	self.viewer = viewer
  	viewer.AddRenderer(self.renderer)

  def setViewport(self, viewPort):
    if self.viewer and self.renderer:
      self.renderer.SetViewport(viewPort)

  #################################################################
  ## Camera Methods
  #################################################################

  #protected method
  def pan(self, previousEventPosition, currentEventPosition):
    renderer = self.renderer
    camera = renderer.GetActiveCamera()
    viewFocus = camera.GetFocalPoint()
    viewPoint = camera.GetPosition()
    focalDepth = viewFocus[2]
    newPickPoint =  self._computeWorldToDisplay(renderer, (currentEventPosition[0],currentEventPosition[1],focalDepth))
    oldPickPoint = self._computeWorldToDisplay(renderer, (previousEventPosition[0],previousEventPosition[1],focalDepth))
    motionVector = [(pos[0]-pos[1]) for pos in slice(oldPickPoint, newPickPoint)]
    
    newFocalPoint = [(pos[0]+pos[1]) for pos in slice(motionVector, viewFocus)]
    newPosition = [(pos[0]+pos[1]) for pos in slice(motionVector, viewPoint)]
    camera.SetFocalPoint(newFocalPoint)
    camera.SetPosition(newPosition)

    renderer.UpdateLightsGeometryToFollowCamera()
    self._rerender()

  #protected method
  def dolly(self, dolly_value): 
    renderer=self.renderer
    camera = renderer.GetActiveCamera()
    if camera.GetParallelProjection():
      camera.SetParallelScale(camera.GetParallelScale()*dolly_value)
    else:
      camera.Dolly(dolly_value)
      renderer.ResetCameraClippingRange()
      renderer.UpdateLightsGeometryToFollowCamera()
    self._rerender()

  #################################################################
  ## Utility Methods
  #################################################################

  def _computeWorldToDisplay(self, value):
      coord = vtk.vtkCoordinate()
      coord.SetCoordinateSystemToWorld()
      coord.SetValue(value)
      return coord.GetComputeDisplayValue(self.renderer) 

  def _rerender(self):
    self.renderer.GetRenderWindow().GetInteractor().Render()