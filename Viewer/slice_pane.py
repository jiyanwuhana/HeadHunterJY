import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import vtk
import itk
from rx.subjects import Subject
from .pane import Pane
from Types import EventType, SliceOrientation, ItkTypes

class SlicePane(Pane):
  
  def __init__(self, uid):
    self.uid = uid
    self.slice = None
    self.sliceRange = None
    self._orientation = None
    self.imageViewer = vtk.vtkImageViewer2()
     # don't use the vtkImageViewer2 render window
    self.imageViewer.GetRenderWindow().OffScreenRenderingOn()
    super().__init__(uid, self.imageViewer.GetRenderer())

  def setViewer(self, viewer):
    self.viewer = viewer
    self.imageViewer.SetRenderWindow(viewer.renderWindow)
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
      .subscribe(lambda ev: self._syncSlice(ev[2].slice, ev[2].sliceRange))

  def loadModel(self, model, orientation=SliceOrientation.AXIAL):
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
    # self.setupCamera()
    self.orientation=orientation
    self.sliceRange=(self.imageViewer.GetSliceMin(), self.imageViewer.GetSliceMax())
    return self

  # def setupCamera(self):
  #   self.renderer.GetActiveCamera().SetViewUp(0, -1, 0) # itk origin is topleft, vtk origin is bottom left
  #   self.renderer.ResetCamera()

  ########################################################
  ## orientation property
  ########################################################
  @property
  def orientation(self):
    return self._orientation

  @orientation.setter
  def orientation(self, sliceOrientation):
    self._orientation = sliceOrientation
    if sliceOrientation == SliceOrientation.AXIAL:
      self.imageViewer.SetSliceOrientationToXY()
    elif sliceOrientation == SliceOrientation.CORONAL:
      self.imageViewer.SetSliceOrientationToYZ()
    elif sliceOrientation == SliceOrientation.SAGITTAL:
      self.imageViewer.SetSliceOrientationToXZ()
    else:
      raise ValueError("Unknown Orientation specified")

    self.renderer.ResetCamera()
    self.resetSlice()

  ########################################################
  ## slice methods
  ########################################################

  def resetSlice(self):
    self.minSlice = self.imageViewer.GetSliceMin()
    self.maxSlice = self.imageViewer.GetSliceMax()
    self.slice = round((self.minSlice + self.maxSlice) / 2)
    self.imageViewer.SetSlice(self.slice)

  def _syncSlice(self, sliceNumber, sliceRange):
    self.setSlice(self._normalizeValue(sliceRange[0], sliceRange[1], self.sliceRange[0], self.sliceRange[1], sliceNumber))

  def _normalizeValue(self, currMin, currMax, newMin, newMax, value):
    normalizedValue = round((float(value)/(currMax-currMin))*(newMax-newMin)+newMin)
    normalizedValue = max([normalizedValue, newMin])
    normalizedValue = min([normalizedValue, newMax])
    return normalizedValue

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
