import itk
import vtk

#################################################################################################
## Constants
#################################################################################################

IF3         = itk.Image[itk.F, 3]
IUC3        = itk.Image[itk.UC, 3]
IRGBUC3     = itk.Image[itk.RGBPixel[itk.UC], 3]
LMLOUL3     = itk.LabelMap[itk.StatisticsLabelObject[itk.UL, 3]]

class LabelMap():
  
  def __init__(self, niiPath=None, numpyLabelMap=None):
    self.niiPath = niiPath
    self.numpyLabelMap = numpyLabelMap
    if niiPath:
      self.generatePipeline(niiPath=niiPath)
    elif numpyLabelMap:
      self.generatePipeline(numpyLabelMap=numpyLabelMap)

  def generatePipeline(self, niiPath=None, numpyLabelMap=None):
    if niiPath:
      # itk.ResampleImageFilter -> itk.LabelImageToLabelMapFilter -> itk.LabelMapOverlayImageFilter
      niiReader = itk.ImageFileReader[IUC3].New()
      niiReader.SetFileName(niiPath)
      resampleImageFilter = itk.ResampleImageFilter[IUC3, IUC3].New()
      resampleImageFilter.SetInput(niiReader.GetOutput())
      resampleImageFilter.SetTransform(itk.IdentityTransform[itk.D, 3].New())
      resampleImageFilter.SetInterpolator(itk.NearestNeighborInterpolateImageFunction[IUC3, itk.D].New())
      resampleImageFilter.UseReferenceImageOn()
      resampleImageFilter.SetReferenceImage(imageSeriesReader.GetOutput())
      self.labelImageToLabelMapFilter = itk.LabelImageToLabelMapFilter[IUC3, LMLOUL3].New()
      self.labelImageToLabelMapFilter.SetInput(resampleImageFilter.GetOutput())

    elif numpyLabelMap:
      # Itk.changeInformationImageFilter -> itk.ResampleImageFilter -> itk.LabelImageToLabelMapFilter -> itk.LabelMapOverlayImageFilter
      changeInformationImageFilter = itk.ChangeInformationImageFilter[IUC3].New()
      changeInformationImageFilter.SetInput(numpyLabelMap)
      changeInformationImageFilter.UseReferenceImageOn()
      changeInformationImageFilter.ChangeDirectionOn()
      changeInformationImageFilter.ChangeSpacingOn()
      changeInformationImageFilter.ChangeOriginOn()
      changeInformationImageFilter.SetReferenceImage(caster.GetOutput())
      resampleImageFilter = itk.ResampleImageFilter[IUC3, IUC3].New()
      resampleImageFilter.SetInput(changeInformationImageFilter.GetOutput())
      resampleImageFilter.SetTransform(itk.IdentityTransform[itk.D, 3].New())
      resampleImageFilter.SetInterpolator(itk.NearestNeighborInterpolateImageFunction[IUC3, itk.D].New())
      resampleImageFilter.UseReferenceImageOn()
      resampleImageFilter.SetReferenceImage(imageSeriesReader.GetOutput())
      self.labelImageToLabelMapFilter = itk.LabelImageToLabelMapFilter[IUC3, LMLOUL3].New()
      self.labelImageToLabelMapFilter.SetInput(resampleImageFilter.GetOutput())
    
    # Merge pipelines
    self.labelMapOverlayImageFilter = itk.LabelMapOverlayImageFilter[LMLOUL3, IUC3, IRGBUC3].New()
    self.labelMapOverlayImageFilter.SetInput(labelImageToLabelMapFilter.GetOutput())
    self.labelMapOverlayImageFilter.SetFeatureImage(caster.GetOutput())
    self.labelMapOverlayImageFilter.SetOpacity(self.maskOpacity)

  def GetOutput():
    self.labelMapOverlayImageFilter.GetOutput()