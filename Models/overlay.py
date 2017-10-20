import itk
import vtk
from vtk import vtkCommand
import numpy as np
from .dicom_series import DicomSeries
from .label_map import LabelMap

IF3         = itk.Image[itk.F, 3]
IUC3        = itk.Image[itk.UC, 3]
IRGBUC3     = itk.Image[itk.RGBPixel[itk.UC], 3]
LMLOUL3     = itk.LabelMap[itk.StatisticsLabelObject[itk.UL, 3]]

class Overlay():
  
  def __init__(self, dicomFileNames, niiPath=None, numpyLabelMap=None, maskOpacity=0.5):
    self.type = IRGBUC3
    self.dicomFileNames = dicomFileNames
    self.niiPath = niiPath
    self.numpyLabelMap = numpyLabelMap
    self.maskOpacity = maskOpacity
    self.dicomSeries = DicomSeries(dicomFileNames)
    if niiPath:
      self.labelMap = LabelMap(self.dicomSeries.GetOutput(), niiPath=niiPath)
    elif numpyLabelMap.any():
      self.labelMap = LabelMap(self.dicomSeries.GetOutput(), numpyLabelMap=numpyLabelMap)
    self.generatePipeline(self.dicomSeries, self.labelMap)

  def generatePipeline(self, dicomSeries, labelMap):
    # Merge pipelines
    self.labelMapOverlayImageFilter = itk.LabelMapOverlayImageFilter[LMLOUL3, IUC3, IRGBUC3].New()
    self.labelMapOverlayImageFilter.SetInput(labelMap.GetOutput())
    self.labelMapOverlayImageFilter.SetFeatureImage(dicomSeries.GetOutput())
    self.labelMapOverlayImageFilter.SetOpacity(self.maskOpacity);
    self.labelMapOverlayImageFilter.Update()

  def GetOutput(self):
    return self.labelMapOverlayImageFilter.GetOutput()