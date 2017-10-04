import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtQuick import QQuickView
import vtk
import itk
from Viewer import Viewer, Pane, SlicePane

#####################################################################################################################
## CLASSES
##################################################################################################################### 

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

# generate dicom series file names
DICOM_PATH = "/Users/benjaminhon/Developer/data/bpynz/M489106/001321140"
generator = itk.GDCMSeriesFileNames.New()
generator.SetDirectory(DICOM_PATH)
seriesUIDs = generator.GetSeriesUIDs()
series = { uid: generator.GetFileNames(uid) for uid in generator.GetSeriesUIDs() }

app = QApplication([])
mainWindow = MainWindow()

viewer = Viewer()
viewer.setMinimumWidth(800)
viewer.setMinimumHeight(600)

# Slice Pane
slicePane = SlicePane('TL', viewer)
slicePane.loadDicom(series[seriesUIDs[3]])
slicePane2 = SlicePane('TR', viewer)
slicePane2.loadDicom(series[seriesUIDs[3]])

# Add panes
viewer.addPane(slicePane, (0,.5,.5,1))
viewer.addPane(slicePane2, (.5,.5,1,1))

# Load qml components
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
mainWindow.centerPanel.addWidget(viewer)

viewer.startEventLoop()
sys.exit(app.exec_())