import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import itk
import vtk
from Types import ItkTypes
from .data_source import DataSource

class DicomSeries():
  
  def __init__(self, fileNames):
    self.fileNames = fileNames
    self.type = ItkTypes.IUC3
    self.image = DataSource().loadDicomSeries(fileNames)
    self.generatePipeline(fileNames)

  def generatePipeline(self, fileNames):
    # RescaleIntensityImageFilter -> CastImageFilter -> itk.ImageToVTKImageFilter -> vtkImageViewer2
    rescaler = itk.RescaleIntensityImageFilter[ItkTypes.IF3, ItkTypes.IF3].New()
    rescaler.SetInput(self.image.GetOutput())
    rescaler.SetOutputMaximum(255)
    rescaler.SetOutputMinimum(0)
    self.caster = itk.CastImageFilter[ItkTypes.IF3, ItkTypes.IUC3].New()
    self.caster.SetInput(rescaler.GetOutput())
    self.caster.Update()

  def GetOutput(self):
    return self.caster.GetOutput()