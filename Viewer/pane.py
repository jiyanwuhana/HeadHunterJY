import itk
import vtk
from rx.subjects import Subject

class Pane(Subject):

  def __init__(self, uid, renderer, viewer):
    super().__init__()
    self.uid = uid
    self.renderer = renderer
    self.viewer = viewer
    self.scene = {}