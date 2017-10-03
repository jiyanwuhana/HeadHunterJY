import vtk
from vtk import vtkCommand
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from .pane import Pane

class Viewer(QVTKRenderWindowInteractor):
    
  panes = {}
  
  def __init__(self, parent=None):
    super().__init__(parent)
    self.renderWindow =  self.GetRenderWindow()
    self.interactor = self.renderWindow.GetInteractor()
    self.interactor.SetInteractorStyle(ViewerInteractorStyle(self))
  
  def addPane(self, uid, renderer, viewPort):
    self.panes[uid] = Pane(uid, renderer, viewPort, self)
  
  def startEventLoop(self):
    self.interactor.Initialize()


class ViewerInteractorStyle(vtk.vtkInteractorStyleUser):
    
  def __init__(self, viewer):
    self.viewer = viewer        
    self.AddObserver(vtkCommand.LeftButtonPressEvent, self.leftButtonPressEvent)

  def leftButtonPressEvent(self, obj, event):    
    (x, y) = obj.GetInteractor().GetEventPosition()
    ratio = self.viewer.devicePixelRatio() # VTK BUG for Retina Display
    x = x*ratio
    y = y*ratio
    
    # forward events to the right panes
    for uid, pane in self.viewer.panes.items():    
        if pane.isPointInPane(x, y):
            pane.onInteractorEvent(event, (x, y))