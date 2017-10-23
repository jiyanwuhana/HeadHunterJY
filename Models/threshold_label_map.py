import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import itk
import vtk
from Types import ItkTypes
from rx.subjects import Subject

class ThresholdLabelMap(Subject):

	def __init__(self):
		super().__init__()

	