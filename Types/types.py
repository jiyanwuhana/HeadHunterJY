import itk
from enum import Enum

class ItkTypes():
	IF3         = itk.Image[itk.F, 3]
	IUC3        = itk.Image[itk.UC, 3]
	IRGBUC3     = itk.Image[itk.RGBPixel[itk.UC], 3]
	LMLOUL3     = itk.LabelMap[itk.StatisticsLabelObject[itk.UL, 3]]

class SliceOrientation(Enum):
  Axial     = 1
  Sagittal  = 2
  Coronal   = 3

class EventType(Enum):
	SliceWillChange = 1
	SyncSliceToPane = 2