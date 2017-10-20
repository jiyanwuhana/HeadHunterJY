import itk
import vtk

IF3         = itk.Image[itk.F, 3]
IUC3        = itk.Image[itk.UC, 3]
IRGBUC3     = itk.Image[itk.RGBPixel[itk.UC], 3]
LMLOUL3     = itk.LabelMap[itk.StatisticsLabelObject[itk.UL, 3]]

class DicomSeries():
  
  def __init__(self, fileNames):
    self.fileNames = fileNames
    self.type = IUC3
    self.generatePipeline(fileNames)

  def generatePipeline(self, fileNames):
    # itk.ImageFileReader -> itk.ImageSeriesReader -> 
    # RescaleIntensityImageFilter -> CastImageFilter -> 
    # itk.ImageToVTKImageFilter -> vtkImageViewer2
    imageSeriesReader = itk.ImageSeriesReader[IF3].New()
    imageSeriesReader.SetFileNames(fileNames)
    imageSeriesReader.UpdateLargestPossibleRegion()
    rescaler = itk.RescaleIntensityImageFilter[IF3, IF3].New()
    rescaler.SetInput(imageSeriesReader.GetOutput())
    rescaler.SetOutputMaximum(255)
    rescaler.SetOutputMinimum(0)
    self.caster = itk.CastImageFilter[IF3, IUC3].New()
    self.caster.SetInput(rescaler.GetOutput())
    self.caster.UpdateLargestPossibleRegion()

  def GetOutput(self):
    return self.caster.GetOutput()