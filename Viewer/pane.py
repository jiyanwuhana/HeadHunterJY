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

  def _makeVtkImageData(self, model):
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
    return self.imageToVTKImageFilter.GetOutput()