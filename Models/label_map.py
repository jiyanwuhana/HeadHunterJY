import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import itk
import vtk
import numpy as np
from Types import ItkTypes
from .data_source import DataSource

class LabelMap():
  
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

  def generatePipeline(self, referenceImage):
    # itk.ResampleImageFilter -> itk.LabelImageToLabelMapFilter
    resampleImageFilter = itk.ResampleImageFilter[ItkTypes.IUC3, ItkTypes.IUC3].New()
    resampleImageFilter.SetInput(self.image.GetOutput())
    resampleImageFilter.SetTransform(itk.IdentityTransform[itk.D, 3].New())
    resampleImageFilter.SetInterpolator(itk.NearestNeighborInterpolateImageFunction[ItkTypes.IUC3, itk.D].New())
    resampleImageFilter.UseReferenceImageOn()
    resampleImageFilter.SetReferenceImage(referenceImage)
    self.labelImageToLabelMapFilter = itk.LabelImageToLabelMapFilter[ItkTypes.IUC3, ItkTypes.LMLOUL3].New()
    self.labelImageToLabelMapFilter.SetInput(resampleImageFilter.GetOutput())
    self.labelImageToLabelMapFilter.UpdateLargestPossibleRegion()

  def GetOutput(self):
    return self.labelImageToLabelMapFilter.GetOutput()
