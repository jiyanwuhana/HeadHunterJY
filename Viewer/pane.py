import itk
import vtk
from vtk import vtkCommand

#################################################################################################
## Constants
#################################################################################################

IF3     = itk.Image[itk.F, 3]
IUC3    = itk.Image[itk.UC, 3]
IRGBUC3 = itk.Image[itk.RGBPixel[itk.UC], 3]
LMLOUL3 = itk.LabelMap[itk.StatisticsLabelObject[itk.UL, 3]]

#################################################################################################
## Pane 
#################################################################################################

class Pane():
     
  def __init__(self, uid, renderer, viewer):
    self.uid = uid
    self.renderer = renderer
    self.viewer = viewer
    self.scene = {}

#################################################################################################
## SlicePane
#################################################################################################

class SlicePane(Pane):
  
  def __init__(self, uid, viewer, imageMax=255, maskOpacity=0.5):
    self.imageMax = imageMax
    self.maskOpacity = maskOpacity
    self.uid = uid
    self.imageViewer = vtk.vtkImageViewer2()
    self.imageViewer.SetRenderWindow(viewer.renderWindow) # don't use the vtkImageViewer2 render window
    super().__init__(uid, self.imageViewer.GetRenderer(), viewer)
    # subscribe to viewer events
    viewer.events.mouseWheelForward \
      .filter(lambda ev: ev[0] == self.uid) \
      .subscribe(lambda ev: self.nextSlice())
    viewer.events.mouseWheelBackward \
      .filter(lambda ev: ev[0] == self.uid) \
      .subscribe(lambda ev: self.previousSlice())

  def setupCamera(self):
    # itk origin is topleft, vtk origin is bottom left
    self.renderer.GetActiveCamera().SetViewUp(0, -1, 0)
    self.renderer.ResetCamera()

  def loadDicomNii(self, fileNames, niiPath=None):
    self.setupPipeline(fileNames, niiPath)
    self.setupCamera()
    # set slice
    self.minSlice = self.imageViewer.GetSliceMin()
    self.maxSlice = self.imageViewer.GetSliceMax()
    self.slice = round((self.minSlice + self.maxSlice) / 2)
    self.imageViewer.SetSlice(self.slice)

  def setupPipeline(self, fileNames, niiPath):
    # DICOM pipeline
    # itk.ImageFileReader -> itk.ImageSeriesReader -> RescaleIntensityImageFilter -> CastImageFilter -> itk.ImageToVTKImageFilter -> vtkImageViewer2
    imageSeriesReader = itk.ImageSeriesReader[IF3].New()
    imageSeriesReader.SetFileNames(fileNames)
    rescaler = itk.RescaleIntensityImageFilter[IF3, IF3].New()
    rescaler.SetInput(imageSeriesReader.GetOutput())
    rescaler.SetOutputMaximum(self.imageMax)
    rescaler.SetOutputMinimum(0)
    caster = itk.CastImageFilter[IF3, IUC3].New()
    caster.SetInput(rescaler.GetOutput())

    if niiPath:
      # NII pipeline
      # itk.ResampleImageFilter -> itk.LabelImageToLabelMapFilter -> itk.LabelMapOverlayImageFilter
      niiReader = itk.ImageFileReader[IUC3].New()
      niiReader.SetFileName(niiPath)
      resampleImageFilter = itk.ResampleImageFilter[IUC3, IUC3].New()
      resampleImageFilter.SetInput(niiReader.GetOutput())
      resampleImageFilter.SetTransform(itk.IdentityTransform[itk.D, 3].New())
      resampleImageFilter.SetInterpolator(itk.NearestNeighborInterpolateImageFunction[IUC3, itk.D].New())
      resampleImageFilter.UseReferenceImageOn()
      resampleImageFilter.SetReferenceImage(imageSeriesReader.GetOutput())
      labelImageToLabelMapFilter = itk.LabelImageToLabelMapFilter[IUC3, LMLOUL3].New()
      labelImageToLabelMapFilter.SetInput(resampleImageFilter.GetOutput())

      # Merge pipelines
      labelMapOverlayImageFilter = itk.LabelMapOverlayImageFilter[LMLOUL3, IUC3, IRGBUC3].New()
      labelMapOverlayImageFilter.SetInput(labelImageToLabelMapFilter.GetOutput())
      labelMapOverlayImageFilter.SetFeatureImage(caster.GetOutput())
      labelMapOverlayImageFilter.SetOpacity(self.maskOpacity);

    # Itk to Vtk
    if niiPath:
      self.imageToVTKImageFilter = itk.ImageToVTKImageFilter[IRGBUC3].New()
      self.imageToVTKImageFilter.SetInput(labelMapOverlayImageFilter.GetOutput())
    else:
      self.imageToVTKImageFilter = itk.ImageToVTKImageFilter[IUC3].New()
      self.imageToVTKImageFilter.SetInput(caster.GetOutput())
    
    self.imageToVTKImageFilter.Update()
    self.imageViewer.SetInputData(self.imageToVTKImageFilter.GetOutput())

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
