import itk
import vtk
from vtk import vtkCommand

#################################################################################################
## Pane 
#################################################################################################

class Pane():
     
  def __init__(self, uid, renderer, viewer):
    self.uid = uid
    self.renderer = renderer
    self.viewer = viewer
    self.scene = {}
    
  def onInteractorEvent(self, event, eventData):
    print(self.uid, event, eventData)

#################################################################################################
## SlicePane
#################################################################################################

class SlicePane(Pane):

  outputImageType = itk.Image[itk.UC, 3]
  inputImageType  = itk.Image[itk.F, 3]
  
  def __init__(self, uid, viewer):
    self.reader = itk.ImageSeriesReader[self.inputImageType].New()
    self.imageViewer = vtk.vtkImageViewer2()
    self.imageViewer.SetRenderWindow(viewer.renderWindow) # don't use the vtkImageViewer2 render window
    super().__init__(uid, self.imageViewer.GetRenderer(), viewer)

  def setupCamera(self):
    # itk origin is topleft, vtk origin is bottom left
    self.renderer.GetActiveCamera().SetViewUp(0,-1,0)
    self.renderer.ResetCamera()

  def setupPipeline(self):
    # itk.ImageSeriesReader -> RescaleIntensityImageFilter -> CastImageFilter -> itk.ImageToVTKImageFilter -> vtkImageViewer2
    rescaler = itk.RescaleIntensityImageFilter[self.inputImageType, self.inputImageType].New()
    rescaler.SetInput(self.reader.GetOutput())
    rescaler.SetOutputMaximum(255)
    rescaler.SetOutputMinimum(0)
    caster = itk.CastImageFilter[self.inputImageType, self.outputImageType].New()
    caster.SetInput(rescaler.GetOutput())
    itkToVtkConverter = itk.ImageToVTKImageFilter[self.outputImageType].New()
    itkToVtkConverter.SetInput(caster.GetOutput())
    itkToVtkConverter.Update() # update
    self.imageViewer.SetInputData(itkToVtkConverter.GetOutput())
    
  def loadDicom(self, fileNames):
    self.reader.SetFileNames(fileNames)
    self.setupPipeline()
    self.setupCamera()
    # set slice
    self.minSlice = self.imageViewer.GetSliceMin()
    self.maxSlice = self.imageViewer.GetSliceMax()
    self.slice = round((self.minSlice + self.maxSlice) / 2)
    self.imageViewer.SetSlice(self.slice)

  def onInteractorEvent(self, event, eventData):
    if event == 'MouseWheelBackwardEvent':
      self.previousSlice()
    elif event == 'MouseWheelForwardEvent':
      self.nextSlice()

  def nextSlice(self):
    if self.slice != None and self.slice < self.maxSlice:
      self.slice = self.slice + 1
      self.imageViewer.SetSlice(self.slice)

  def previousSlice(self):
    if self.slice != None and self.slice > self.minSlice:
      self.slice = self.slice - 1
      self.imageViewer.SetSlice(self.slice)
