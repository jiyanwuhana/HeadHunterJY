import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtQuick import QQuickView
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

#####################################################################################################################
## CLASSES
##################################################################################################################### 

class QVTKRenderWindow(QVTKRenderWindowInteractor):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.renderer = vtk.vtkRenderer()
		self.renderWindow =  self.GetRenderWindow()
		self.renderWindow.AddRenderer(self.renderer)
		self.interactor = self.renderWindow.GetInteractor()
		self.interactorStyle = self.interactor.GetInteractorStyle()
		self.actors = {}

	def addActorToScene(self, actor, id):
		self.actors[id] = actor
		self.renderer.AddActor(actor)

	def startEventLoop(self):
		self.interactor.Initialize()

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		centralWidget = QWidget(self)
		gridlayout = QGridLayout(centralWidget)
		self.setCentralWidget(centralWidget)
		self.rightPanel = QVBoxLayout()
		self.leftPanel = QVBoxLayout()
		self.topPanel = QHBoxLayout()
		self.bottomPanel = QHBoxLayout()
		self.centerPanel = QHBoxLayout()
		gridlayout.addLayout(self.topPanel, 0, 0, 1, 3)
		gridlayout.addLayout(self.bottomPanel, 2, 0, 1, 3)
		gridlayout.addLayout(self.leftPanel, 1, 0, 1, 1)
		gridlayout.addLayout(self.rightPanel, 1, 2, 1, 1)
		gridlayout.addLayout(self.centerPanel, 1, 1, 1, 1)

def QMLToWidgets(sources):
	"""
	[(url, size)] -> [widget]
	"""
	widgets = []
	for source, size in sources:
		component = QQuickView()
		component.setSource(QUrl(source))
		widget = QWidget.createWindowContainer(component)
		widget.setMinimumSize(*size)
		widgets.append(widget)
	return widgets

#####################################################################################################################
## BEGIN
##################################################################################################################### 

app = QApplication([])
mainWindow = MainWindow()

# vtk component
vtkWidget = QVTKRenderWindow()
vtkWidget.setMinimumWidth(800)
vtkWidget.setMinimumHeight(600)
vtkWidget.interactorStyle.SetCurrentStyleToTrackballCamera()

# Create source
source = vtk.vtkSphereSource()
source.SetCenter(0, 0, 0)
source.SetRadius(5.0)

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(source.GetOutputPort())

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)
vtkWidget.addActorToScene(actor, 'sphere')

# load qml components
[topWidget, bottomWidget, leftWidget, rightWidget] = QMLToWidgets([
	('panel.qml', (250,50)),
	('panel.qml', (250,50)),
	('panel.qml', (50,200)),
	('panel.qml', (150,200))
])

# layout
mainWindow.show()
mainWindow.topPanel.addWidget(topWidget)
mainWindow.bottomPanel.addWidget(bottomWidget)
mainWindow.leftPanel.addWidget(leftWidget)
mainWindow.rightPanel.addWidget(rightWidget)
mainWindow.centerPanel.addWidget(vtkWidget)

vtkWidget.startEventLoop()
sys.exit(app.exec_())