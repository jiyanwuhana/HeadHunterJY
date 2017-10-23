import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import itk
import vtk
from vtk import vtkCommand
import numpy as np
from .dicom_series import DicomSeries
from .label_map import LabelMap
from Types import ItkTypes

class Overlay():
  
  def __init__(self, dicomFileNames, niiPath=None, ndarr=np.array([]), maskOpacity=0.5):
    self.type           = ItkTypes.IRGBUC3
    self.dicomFileNames = dicomFileNames
    self.niiPath        = niiPath
    self.ndarr          = ndarr
    self.maskOpacity    = maskOpacity
    self.dicomSeries    = DicomSeries(dicomFileNames)
    self.labelMap       = LabelMap(self.dicomSeries.GetOutput(), niiPath=niiPath, ndarr=ndarr)
    self.generatePipeline(self.dicomSeries, self.labelMap)

  def generatePipeline(self, dicomSeries, labelMap):
    # Merge pipelines
    self.labelMapOverlayImageFilter = itk.LabelMapOverlayImageFilter[ItkTypes.LMLOUL3, ItkTypes.IUC3, ItkTypes.IRGBUC3].New()
    self.labelMapOverlayImageFilter.SetInput(labelMap.GetOutput())
    self.labelMapOverlayImageFilter.SetFeatureImage(dicomSeries.GetOutput())
    self.labelMapOverlayImageFilter.SetOpacity(self.maskOpacity);
    self.labelMapOverlayImageFilter.Update()

  def GetOutput(self):
    return self.labelMapOverlayImageFilter.GetOutput()