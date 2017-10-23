import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import itk
import vtk
from Types import ItkTypes

class DicomSeries():
  
  def __init__(self, fileNames):
    self.fileNames = fileNames
    self.type = ItkTypes.IUC3
    self.generatePipeline(fileNames)

  def generatePipeline(self, fileNames):
    # itk.ImageFileReader -> itk.ImageSeriesReader -> 
    # RescaleIntensityImageFilter -> CastImageFilter -> 
    # itk.ImageToVTKImageFilter -> vtkImageViewer2
    imageSeriesReader = itk.ImageSeriesReader[ItkTypes.IF3].New()
    imageSeriesReader.SetFileNames(fileNames)
    imageSeriesReader.UpdateLargestPossibleRegion()
    rescaler = itk.RescaleIntensityImageFilter[ItkTypes.IF3, ItkTypes.IF3].New()
    rescaler.SetInput(imageSeriesReader.GetOutput())
    rescaler.SetOutputMaximum(255)
    rescaler.SetOutputMinimum(0)
    self.caster = itk.CastImageFilter[ItkTypes.IF3, ItkTypes.IUC3].New()
    self.caster.SetInput(rescaler.GetOutput())
    self.caster.UpdateLargestPossibleRegion()

  def GetOutput(self):
    return self.caster.GetOutput()