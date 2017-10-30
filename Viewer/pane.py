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

  def makeVtkImageData(self, model):
    # display label maps
    if model.type == ItkTypes.LMLOUL3:
      labelMapToRGBImageFilter = itk.LabelMapToRGBImageFilter[ItkTypes.LMLOUL3, ItkTypes.IRGBUC3].New()
      labelMapToRGBImageFilter.SetInput(model.GetOutput())
      self.imageToVTKImageFilter = itk.ImageToVTKImageFilter[ItkTypes.IRGBUC3].New()
      self.imageToVTKImageFilter.SetInput(labelMapToRGBImageFilter.GetOutput())
    # display scalar images or overlay
    else:
      self.imageToVTKImageFilter = itk.ImageToVTKImageFilter[model.type].New()
      self.imageToVTKImageFilter.SetInput(model.GetOutput())
    # vtk display
    self.imageToVTKImageFilter.Update()
    return self.imageToVTKImageFilter.GetOutput()

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

  #protected method
  def spin(self, previousEventPosition, currentEventPosition):
      renderer = self.renderer
      center = renderer.GetCenter()
      newVector = (currentEventPosition[1]-center[1], currentEventPosition[0]-center[0]) #
      oldVector = (previousEventPosition[1]-center[1], previousEventPosition[0]-center[0])
      newAngle = vtk.vtkMath.DegreesFromRadians(atan2(newVector))
      oldAngle = vtk.vtkMath.DegreesFromRadians(atan2(oldVector))

      camera = renderer.GetActiveCamera()
      camera.Roll(newAngle-oldAngle)
      camera.OrthogonalizeViewUp()
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
