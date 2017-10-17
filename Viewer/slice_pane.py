import vtk
import itk
from .pane import Pane

class SlicePane(Pane):
  
  def __init__(self, uid, viewer, sync=False):
    self.sync = sync
    self.uid = uid
    self.slice = None
    self.imageViewer = vtk.vtkImageViewer2()
    self.imageViewer.SetRenderWindow(viewer.renderWindow) # don't use the vtkImageViewer2 render window
    super().__init__(uid, self.imageViewer.GetRenderer(), viewer)

    # subscribe to viewer events
    viewer.events.mouseWheelForward \
      .filter(lambda ev: self.sync or ev[0] == self.uid) \
      .subscribe(lambda ev: self.nextSlice())
    viewer.events.mouseWheelBackward \
      .filter(lambda ev: self.sync or ev[0] == self.uid) \
      .subscribe(lambda ev: self.previousSlice())

  def loadModel(self, model):
    self.imageToVTKImageFilter = itk.ImageToVTKImageFilter[model.type].New()
    self.imageToVTKImageFilter.SetInput(model.GetOutput())
    self.imageToVTKImageFilter.Update()
    self.imageViewer.SetInputData(self.imageToVTKImageFilter.GetOutput())
    self.setupCamera()
    self.resetSlice()
    return self

  def setupCamera(self):
    self.renderer.GetActiveCamera().SetViewUp(0, -1, 0) # itk origin is topleft, vtk origin is bottom left
    self.renderer.ResetCamera()

  def setOrientation(orientation):
    if orientation == "AXIAL":
      self.imageViewer.SetSliceOrientationToXY()
    elif orientation == "CORONAL":
      self.imageViewer.SetSliceOrientationToYZ()
    elif orientation == "SAGITTAL":
      self.imageViewer.SetSliceOrientationToXZ()

  def resetSlice(self):
    self.minSlice = self.imageViewer.GetSliceMin()
    self.maxSlice = self.imageViewer.GetSliceMax()
    self.slice = round((self.minSlice + self.maxSlice) / 2)
    self.imageViewer.SetSlice(self.slice)

  def nextSlice(self):
    if self.slice != None and self.slice < self.maxSlice:
      self.slice = self.slice + 1
      self.imageViewer.SetSlice(self.slice)
      self.renderer.Render() # WHY MUST DO THIS, PREVIOUSLY NO NEED

  def previousSlice(self):
    if self.slice != None and self.slice > self.minSlice:
      self.slice = self.slice - 1
      self.imageViewer.SetSlice(self.slice)
      self.renderer.Render()
