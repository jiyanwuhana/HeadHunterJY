class Pane():
    
  scene = {}
  
  def __init__(self, uid, renderer, viewPort, viewer):
    self.uid = uid
    self.renderer = renderer
    self.viewer = viewer
    self.viewPort = viewPort
    # set viewport
    renderer.SetViewport(viewPort)
    # add to viewer render window
    viewer.renderWindow.AddRenderer(renderer)
  
  def isPointInPane(self, x, y):
    (w, h) = self.viewer.renderWindow.GetSize()
    x = x / w
    y = y / h
    return x > self.viewPort[0] and x < self.viewPort[2] and y > self.viewPort[1] and y < self.viewPort[3]
      
  def onInteractorEvent(self, event, eventData):
    print(self.uid, event, eventData)