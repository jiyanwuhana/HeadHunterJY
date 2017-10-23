import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import itk
import vtk
from Types import ItkTypes
from rx.subjects import Subject

class DataSource():

  def loadDicomSeries(self, fileNames):
    imageSeriesReader = itk.ImageSeriesReader[ItkTypes.IF3].New()
    imageSeriesReader.SetFileNames(fileNames)
    imageSeriesReader.Update()
    return imageSeriesReader

  def loadNii(self, file):
    niiReader = itk.ImageFileReader[ItkTypes.IUC3].New()
    niiReader.SetFileName(file)
    niiReader.Update()
    return niiReader

  def loadNumpy(self, ndarr, reference):
    image = itk.GetImageFromArray(ndarr)
    changeInformationImageFilter = itk.ChangeInformationImageFilter[ItkTypes.IUC3].New()
    changeInformationImageFilter.SetInput(image)
    changeInformationImageFilter.UseReferenceImageOn()
    changeInformationImageFilter.ChangeDirectionOn()
    changeInformationImageFilter.ChangeSpacingOn()
    changeInformationImageFilter.ChangeOriginOn()
    changeInformationImageFilter.SetReferenceImage(reference)
    changeInformationImageFilter.Update()
    return changeInformationImageFilter