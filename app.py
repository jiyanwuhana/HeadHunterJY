import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QFileDialog
from PyQt5.QtQuick import QQuickView
import vtk
import itk
from Viewer import Viewer, Pane, SlicePane
from winson_integration import AINI

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

def generateSeries(path):
	generator = itk.GDCMSeriesFileNames.New()
	generator.SetDirectory(path)
	seriesUIDs = generator.GetSeriesUIDs()
	series = { uid: generator.GetFileNames(uid) for uid in generator.GetSeriesUIDs() }
	return (series, seriesUIDs)

#####################################################################################################################
## BEGIN
##################################################################################################################### 

app = QApplication([])
mainWindow = MainWindow()

viewer = Viewer()
viewer.setMinimumWidth(800)
viewer.setMinimumHeight(600)

# slice panes
slicePaneTL = SlicePane('TL', viewer, sync=True)
slicePaneTR = SlicePane('TR', viewer, imageMax=0, maskOpacity=1, sync=True)
slicePaneBL = SlicePane('BL', viewer, sync=True)

# add panes
viewer.addPane(slicePaneTL, (0,.5,.5,1))
viewer.addPane(slicePaneTR, (.5,.5,1,1))
viewer.addPane(slicePaneBL, (0,0,.5,.5))

# load qml components
[topWidget, bottomWidget, leftWidget, rightWidget] = QMLToWidgets([
	('panel.qml', (250,50)),
	('panel.qml', (250,50)),
	('panel.qml', (50,200)),
	('panel.qml', (150,200))
])

def load():
	# DICOM_PATH = "/Users/benjaminhon/Developer/HeadHunter/notebooks/220259"
	path  = QFileDialog().getExistingDirectory()
	# generate series
	(series, seriesUIDs) = generateSeries(path)

	# predict and get nii
	NII_PATH = "/Users/benjaminhon/Developer/HeadHunter/notebooks/220259.nii"

	# predict and get seriesUID and numpy array
	aini = AINI()
	aini.initModel()
	aini.restoreModel()
	prediction = aini.predictClassification(path)

	
	print(prediction['UID'])
	print()

	masksNumpy = [ maskInfo['mask'] for maskName, maskInfo in prediction['MASK'].items() ]


	# populate slice panes
	slicePaneTL.loadDicomNii(series[prediction['UID']])
	slicePaneTR.loadDicomNii(series[prediction['UID']], numpyMasks=masksNumpy)
	slicePaneBL.loadDicomNii(series[prediction['UID']], numpyMasks=masksNumpy)

# menu bar
fileMenu = QMenu('File')
fileMenu.addAction('Load', load)
menuBar = QMenuBar()
menuBar.addMenu(fileMenu)

# layout
mainWindow.show()
# mainWindow.topPanel.addWidget(topWidget)
# mainWindow.bottomPanel.addWidget(bottomWidget)
# mainWindow.leftPanel.addWidget(leftWidget)
mainWindow.rightPanel.addWidget(rightWidget)
mainWindow.centerPanel.addWidget(viewer)

viewer.startEventLoop()
sys.exit(app.exec_())