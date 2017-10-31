import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import itk
import vtk
import numpy as np
from rx import Observable
from Types import ItkTypes, EventType
from .data_source import DataSource
from .label_map import LabelMap
from rx.subjects import Subject

class ThresholdLabelMap(Subject):

  def __init__(self, referenceImage, itkImage=None, niiPath=None, ndarr=np.array([])):
    self.niiPath        = niiPath
    self.ndarr          = ndarr
    self.type           = ItkTypes.LMLOUL3
    self.referenceImage = referenceImage
    if itkImage:
      self.image = itkImage
    elif niiPath:
      self.image = DataSource().loadNii(niiPath)
    elif ndarr.any():
      self.image = DataSource().loadNumpy(ndarr, referenceImage)
    self.generatePipeline(referenceImage)

  def subscribeTo(self, observables):
    Observable.merge(observables) \
      .filter(lambda ev: ev[0] == EventType.SetThreshold) \
      .subscribe(lambda ev: self._setThreshold(ev[2]))

  def generatePipeline(self, referenceImage):
    rescaler = itk.RescaleIntensityImageFilter[ItkTypes.IUC3, ItkTypes.IUC3].New()
    rescaler.SetInput(self.image.GetOutput())
    rescaler.SetOutputMaximum(255)
    rescaler.SetOutputMinimum(0)
    self.thresholdFilter = itk.BinaryThresholdImageFilter[ItkTypes.IUC3, ItkTypes.IUC3].New()
    self.thresholdFilter.SetInput(rescaler.GetOutput())
    self.thresholdFilter.SetLowerThreshold(50)
    self.thresholdFilter.SetUpperThreshold(255)
    self.thresholdFilter.SetOutsideValue(0)
    self.thresholdFilter.SetInsideValue(1)
    self.labelMapFilter = LabelMap(referenceImage, itkImage=self.thresholdFilter)
    self.labelMapFilter.Update()

  def GetOutput(self):
    return self.labelMapFilter.GetOutput()

  def _setThreshold(self, lower):
    self.thresholdFilter.SetLowerThreshold(lower)
    self.thresholdFilter.Update()