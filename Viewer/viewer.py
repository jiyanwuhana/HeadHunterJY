import vtk
from vtk import vtkCommand
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from .pane import Pane

#################################################################################################
## Viewer 
#################################################################################################

class Viewer(QVTKRenderWindowInteractor):
    
  def __init__(self, parent=None):
    super().__init__(parent)
    self.panes = {}
    self.renderWindow =  self.GetRenderWindow()
    self.interactor = self.renderWindow.GetInteractor()
    self.interactor.SetInteractorStyle(ViewerInteractorStyle(self))
  
  def addPane(self, pane, viewPort):
    self.panes[pane.uid] = (pane, viewPort)
    pane.renderer.SetViewport(viewPort)
  
  def startEventLoop(self):
    self.interactor.Initialize()

#################################################################################################
## ViewerInteractorStyle 
#################################################################################################

class ViewerInteractorStyle(vtk.vtkInteractorStyleUser):
    
  def __init__(self, viewer):
    self.viewer = viewer        
    self.AddObserver(vtkCommand.LeftButtonPressEvent, self.genericEvent)
    self.AddObserver(vtkCommand.MouseWheelForwardEvent, self.genericEvent)        
    self.AddObserver(vtkCommand.MouseWheelBackwardEvent, self.genericEvent)

  def eventPosition(self):
    (x, y) = self.GetInteractor().GetEventPosition()
    ratio = self.viewer.devicePixelRatio() # VTK BUG for Retina Display
    return (x * ratio, y * ratio)

  def isPointInPane(self, x, y, viewPort):
    (w, h) = self.viewer.renderWindow.GetSize()
    x = x / w
    y = y / h
    return x > viewPort[0] and x < viewPort[2] and y > viewPort[1] and y < viewPort[3]

  def genericEvent(self, obj, event):
    (x, y) = self.eventPosition()
    # forward events to the right panes
    for uid, (pane, viewPort) in self.viewer.panes.items():
      if self.isPointInPane(x, y, viewPort):
        pane.onInteractorEvent(event, (x, y))