import itk
import vtk
from rx.subjects import Subject

class Pane(Subject):

  def __init__(self, uid, renderer):
    super().__init__()
    self.uid = uid
    self.renderer = renderer
    self.scene = {}

  def setViewer(self, viewer):
  	self.viewer = viewer
  	viewer.AddRenderer(self.renderer)

  def setViewport(self, viewPort):
    if self.viewer and self.renderer:
      self.renderer.SetViewport(viewPort)