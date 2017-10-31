import itk
from enum import Enum

class ItkTypes():
	IF3         = itk.Image[itk.F, 3]
	IUC3        = itk.Image[itk.UC, 3]
	IRGBUC3     = itk.Image[itk.RGBPixel[itk.UC], 3]
	LMLOUL3     = itk.LabelMap[itk.StatisticsLabelObject[itk.UL, 3]]

class SliceOrientation(Enum):
  AXIAL     = 1
  SAGITTAL  = 2
  CORONAL   = 3

class EventType(Enum):

	# Mouse Move
	MouseMove 							= 0

	# Left mouse events
	LeftButtonPress 				= 1
	LeftButtonMove 					= 2		
	LeftButtonRelease 			= 3
	LeftButtonDrag 					= 4
	LeftButtonDoublePress 	= 5

	# Right mouse events
	RightButtonPress 				= 6
	RightButtonMove 				= 7
	RightButtonRelease 			= 8
	RightButtonDrag 				= 9
	RightButtonDoublePress 	= 10

	# Middle button/mouse wheel events
	MouseWheelDown 					= 11
	MouseWheelUp 						= 12

	# Custom events
	SliceWillChange 				= 13
	SyncSliceToPane 				= 14