import itk
import vtk

IF3         = itk.Image[itk.F, 3]
IUC3        = itk.Image[itk.UC, 3]
IRGBUC3     = itk.Image[itk.RGBPixel[itk.UC], 3]
LMLOUL3     = itk.LabelMap[itk.StatisticsLabelObject[itk.UL, 3]]

class LabelMap():
  
  def __init__(self, referenceImage, niiPath=None, numpyLabelMap=None):
    self.niiPath = niiPath
    self.numpyLabelMap = numpyLabelMap
    self.type = LMLOUL3
    self.referenceImage = referenceImage
    if niiPath:
      self.generatePipeline(referenceImage, niiPath=niiPath)
    elif numpyLabelMap.any():
      self.generatePipeline(referenceImage, numpyLabelMap=numpyLabelMap)

  def generatePipeline(self, referenceImage, niiPath=None, numpyLabelMap=None):
    if niiPath:
      # itk.ResampleImageFilter -> itk.LabelImageToLabelMapFilter -> itk.LabelMapOverlayImageFilter
      niiReader = itk.ImageFileReader[IUC3].New()
      niiReader.SetFileName(niiPath)
      resampleImageFilter = itk.ResampleImageFilter[IUC3, IUC3].New()
      resampleImageFilter.SetInput(niiReader.GetOutput())
      resampleImageFilter.SetTransform(itk.IdentityTransform[itk.D, 3].New())
      resampleImageFilter.SetInterpolator(itk.NearestNeighborInterpolateImageFunction[IUC3, itk.D].New())
      resampleImageFilter.UseReferenceImageOn()
      resampleImageFilter.SetReferenceImage(referenceImage)
      self.labelImageToLabelMapFilter = itk.LabelImageToLabelMapFilter[IUC3, LMLOUL3].New()
      self.labelImageToLabelMapFilter.SetInput(resampleImageFilter.GetOutput())
      self.labelImageToLabelMapFilter.UpdateLargestPossibleRegion()

    elif numpyLabelMap.any():
      # Itk.changeInformationImageFilter -> itk.ResampleImageFilter -> itk.LabelImageToLabelMapFilter -> itk.LabelMapOverlayImageFilter
      maskImage = itk.GetImageFromArray(numpyLabelMap)
      changeInformationImageFilter = itk.ChangeInformationImageFilter[IUC3].New()
      changeInformationImageFilter.SetInput(maskImage)
      changeInformationImageFilter.UseReferenceImageOn()
      changeInformationImageFilter.ChangeDirectionOn()
      changeInformationImageFilter.ChangeSpacingOn()
      changeInformationImageFilter.ChangeOriginOn()
      changeInformationImageFilter.SetReferenceImage(referenceImage)
      resampleImageFilter = itk.ResampleImageFilter[IUC3, IUC3].New()
      resampleImageFilter.SetInput(changeInformationImageFilter.GetOutput())
      resampleImageFilter.SetTransform(itk.IdentityTransform[itk.D, 3].New())
      resampleImageFilter.SetInterpolator(itk.NearestNeighborInterpolateImageFunction[IUC3, itk.D].New())
      resampleImageFilter.UseReferenceImageOn()
      resampleImageFilter.SetReferenceImage(referenceImage)
      resampleImageFilter.Update()
      self.labelImageToLabelMapFilter = itk.LabelImageToLabelMapFilter[IUC3, LMLOUL3].New()
      self.labelImageToLabelMapFilter.SetInput(resampleImageFilter.GetOutput())
      self.labelImageToLabelMapFilter.Update()

  def GetOutput(self):
    return self.labelImageToLabelMapFilter.GetOutput()
