import itk
import vtk

class Pane():

  def __init__(self, uid, renderer, viewer):
    self.uid = uid
    self.renderer = renderer
    self.viewer = viewer
    self.scene = {}