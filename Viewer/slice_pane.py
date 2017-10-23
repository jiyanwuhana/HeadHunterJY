import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import vtk
import itk
from rx.subjects import Subject
from .pane import Pane
from Types import EventType, SliceOrientation, ItkTypes

class SlicePane(Pane):
  
  def __init__(self, uid, viewer):
    self.uid = uid
    self.slice = None
    self._orientation = None
    self.imageViewer = vtk.vtkImageViewer2()
    self.imageViewer.SetRenderWindow(viewer.renderWindow) # don't use the vtkImageViewer2 render window
    super().__init__(uid, self.imageViewer.GetRenderer(), viewer)
    #################################################################
    ## Viewer Events
    #################################################################
    viewer.events.mouseWheelForward \
      .filter(lambda ev: ev[0] == self.uid) \
      .subscribe(lambda ev: self.nextSlice())
    viewer.events.mouseWheelBackward \
      .filter(lambda ev: ev[0] == self.uid) \
      .subscribe(lambda ev: self.previousSlice())

  def subscribeTo(self, observables):
    #################################################################
    ## Event Manager Events
    #################################################################
    observables \
      .filter(lambda ev: ev[0] == EventType.SyncSliceToPane and ev[2].uid != self.uid and ev[2].orientation == self.orientation) \
      .do_action(lambda ev: print(ev)) \
      .subscribe(lambda ev: self.setSlice(ev[2].slice))

  def loadModel(self, model):
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
    self.imageViewer.SetInputData(self.imageToVTKImageFilter.GetOutput())
    self.setupCamera()
    self.resetSlice()
    return self

  def setupCamera(self):
    self.renderer.GetActiveCamera().SetViewUp(0, -1, 0) # itk origin is topleft, vtk origin is bottom left
    self.renderer.ResetCamera()

  ########################################################
  ## orientation property
  ########################################################
  @property
  def orientation(self):
    return self._orientation

  @orientation.setter
  def orientation(self, sliceOrientation):
    self._orientation = sliceOrientation
    if sliceOrientation == SliceOrientation.Axial:
      self.imageViewer.SetSliceOrientationToXY()
    elif sliceOrientation == SliceOrientation.Coronal:
      self.imageViewer.SetSliceOrientationToYZ()
    elif sliceOrientation == SliceOrientation.Sagittal:
      self.imageViewer.SetSliceOrientationToXZ()

  ########################################################
  ## slice methods
  ########################################################

  def resetSlice(self):
    self.minSlice = self.imageViewer.GetSliceMin()
    self.maxSlice = self.imageViewer.GetSliceMax()
    self.slice = round((self.minSlice + self.maxSlice) / 2)
    self.imageViewer.SetSlice(self.slice)

  def setSlice(self, slice):
    self.slice = slice
    self.imageViewer.SetSlice(self.slice)
    self.renderer.Render()

  def nextSlice(self):
    if self.slice != None and self.slice < self.maxSlice:
      self.slice = self.slice + 1
      self.imageViewer.SetSlice(self.slice)
      self.renderer.Render()
      self.on_next((EventType.SliceWillChange, self, self.slice))

  def previousSlice(self):
    if self.slice != None and self.slice > self.minSlice:
      self.slice = self.slice - 1
      self.imageViewer.SetSlice(self.slice)
      self.renderer.Render()
      self.on_next((EventType.SliceWillChange, self, self.slice))
