import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add parent to path
import vtk
import rx
from rx import Observable
from rx.subjects import Subject
from vtk import vtkCommand
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from Types import EventType
from .pane import Pane

#################################################################################################
## Viewer 
#################################################################################################

class Viewer(QVTKRenderWindowInteractor):
    
  def __init__(self, parent=None):
    super().__init__(parent)
    self.panes = {}
    self.hoveredPane = None
    self.selectedPane = None
    self.renderWindow = self.GetRenderWindow()
    self.interactor = self.renderWindow.GetInteractor()
    self.events =  ViewerInteractorStyle(self)
    self.interactor.SetInteractorStyle(self.events)

    # compose events
    leftButtonPress       = self.events.filter(lambda ev: ev[0] == EventType.LeftButtonPress)
    mouseMove             = self.events.filter(lambda ev: ev[0] == EventType.MouseMove)
    leftButtonRelease     = self.events.filter(lambda ev: ev[0] == EventType.LeftButtonRelease)
    leftButtonDoublePress = leftButtonPress \
                              .buffer(leftButtonPress.debounce(300)) \
                              .map(lambda xs: len(xs)) \
                              .filter(lambda x: x == 2)
    mouseDrag             = leftButtonPress \
                              .flat_map(lambda ev: mouseMove.take_until(leftButtonRelease))

    ########################################
    ## Handle events
    ########################################
    mouseMove \
      .subscribe(lambda ev: self.setHoveredPane(ev[2][0]))
    leftButtonPress \
      .subscribe(lambda ev: self.setSelectedPane(ev[2][0]))
    leftButtonDoublePress \
      .subscribe(lambda s: print('double clicked', s))
    mouseDrag \
      .subscribe(lambda s: print('mouse drag', s))
      
  def addPane(self, pane, viewPort):
    self.panes[pane.uid] = (pane, viewPort)
    pane.setViewer(self)
    pane.setViewport(viewPort)

  def setHoveredPane(self, uid):
    self.hoveredPane = uid

  def setSelectedPane(self, uid):
    self.selectedPane = uid
  
  def startEventLoop(self):
    self.interactor.Initialize()

#################################################################################################
## ViewerInteractorStyle 
#################################################################################################

class ViewerInteractorStyle(vtk.vtkInteractorStyleUser, Subject):
    
  def __init__(self, viewer):
    Subject.__init__(self)
    vtk.vtkInteractorStyleUser.__init__(self)
    self.viewer = viewer

    # events
    self.AddObserver(vtkCommand.LeftButtonPressEvent,
      lambda obj, event: self.on_next((EventType.LeftButtonPress, viewer, self.eventPosition())))
    self.AddObserver(vtkCommand.LeftButtonReleaseEvent,\
      lambda obj, event: self.on_next((EventType.LeftButtonRelease, viewer, self.eventPosition())))
    self.AddObserver(vtkCommand.MouseWheelForwardEvent,\
      lambda obj, event: self.on_next((EventType.MouseWheelUp, viewer, self.eventPosition())))
    self.AddObserver(vtkCommand.MouseWheelBackwardEvent,\
      lambda obj, event: self.on_next((EventType.MouseWheelDown, viewer, self.eventPosition())))
    self.AddObserver(vtkCommand.MouseMoveEvent,\
      lambda obj, event: self.on_next((EventType.MouseMove, viewer, self.eventPosition())))

  def eventPosition(self):
    (x, y) = self.GetInteractor().GetEventPosition()
    (xp, yp) = self.GetInteractor().GetLastEventPosition()
    ratio = self.viewer.devicePixelRatio() # VTK BUG for Retina Display
    x = x * ratio
    y = y * ratio
    xp = xp * ratio
    yp = yp * ratio
    for uid, (pane, viewPort) in self.viewer.panes.items():
      if self.isPointInPane(x, y, viewPort):
        return (uid, (x, y), (xp, yp))

  def isPointInPane(self, x, y, viewPort):
    (w, h) = self.viewer.renderWindow.GetSize()
    x = x / w
    y = y / h
    return x > viewPort[0] and x < viewPort[2] and y > viewPort[1] and y < viewPort[3]
