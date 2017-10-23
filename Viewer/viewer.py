import vtk
import rx
from rx import Observable
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
    self.hoveredPane = None
    self.selectedPane = None
    self.renderWindow = self.GetRenderWindow()
    self.interactor = self.renderWindow.GetInteractor()
    self.events = ViewerInteractorStyle(self)
    self.interactor.SetInteractorStyle(self.events)
    
    ########################
    ## viewer level events
    ########################
    # self.events.doubleLeftButtonPress = self.leftButtonPress \
    #   .buffer(self.leftButtonPress.debounce(300)) \
    #   .map(lambda l: len(l)) \
    #   .filter(lambda c: c == 2) \
    #   .subscribe(lambda s: print('double clicked', s))
    # self.events.leftButtonDrag = self.leftButtonPress \
    #   .flat_map(lambda ev: self.mouseMove.take_until(self.leftButtonRelease)) \
    #   .subscribe(lambda s: print('mouse drag', s))
    self.events.mouseMove \
      .subscribe(lambda ev: self.setHoveredPane(ev[0]))
    self.events.leftButtonPress \
      .subscribe(lambda ev: self.setSelectedPane(ev[0]))
      
  def addPane(self, pane, viewPort):
    self.panes[pane.uid] = (pane, viewPort)
    pane.renderer.SetViewport(viewPort)

  def setHoveredPane(self, uid):
    self.hoveredPane = uid

  def setSelectedPane(self, uid):
    self.selectedPane = uid
  
  def startEventLoop(self):
    self.interactor.Initialize()

#################################################################################################
## ViewerInteractorStyle 
#################################################################################################

class ViewerInteractorStyle(vtk.vtkInteractorStyleUser):
    
  def __init__(self, viewer):
    self.viewer = viewer
    # subjects
    leftButtonPress = rx.subjects.Subject()
    leftButtonRelease = rx.subjects.Subject()
    mouseWheelForward = rx.subjects.Subject()
    mouseWheelBackward = rx.subjects.Subject()
    mouseMove = rx.subjects.Subject()
    # forward events
    self.AddObserver(vtkCommand.LeftButtonPressEvent, lambda obj, event: leftButtonPress.on_next(event))
    self.AddObserver(vtkCommand.LeftButtonReleaseEvent, lambda obj, event: leftButtonRelease.on_next(event))
    self.AddObserver(vtkCommand.MouseWheelForwardEvent, lambda obj, event: mouseWheelForward.on_next(event))
    self.AddObserver(vtkCommand.MouseWheelBackwardEvent, lambda obj, event: mouseWheelBackward.on_next(event))
    self.AddObserver(vtk.vtkCommand.MouseMoveEvent, lambda obj, event: mouseMove.on_next(event))
    # events object
    self.leftButtonPress = leftButtonPress \
      .map(lambda ev: self.eventPosition()) \
      .filter(lambda ev: ev != None)
    self.leftButtonRelease = leftButtonRelease \
      .map(lambda ev: self.eventPosition()) \
      .filter(lambda ev: ev != None)
    self.mouseWheelForward = mouseWheelForward \
      .map(lambda ev: self.eventPosition()) \
      .filter(lambda ev: ev != None)
    self.mouseWheelBackward = mouseWheelBackward \
      .map(lambda ev: self.eventPosition()) \
      .filter(lambda ev: ev != None)
    self.mouseMove = mouseMove \
      .map(lambda ev: self.eventPosition()) \
      .filter(lambda ev: ev != None)

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
