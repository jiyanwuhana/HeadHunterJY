import sys
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, pyqtProperty, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QFileDialog
from PyQt5.QtQuick import QQuickView
import vtk
import itk
from Viewer import Viewer, SlicePane
from Models import DicomSeries, LabelMap, Overlay

# from winson_integration import AINI
# import zerorpc
# import numpy as np

# #############################################################################
# ## RPC
# #############################################################################

# config  = {
#   "rpc": 			"tcp://0.0.0.0:3000",
#   "storage": 	"/Users/benjaminhon/Developer/Classifier/demo/storage"
# }

# rpc     = zerorpc.Client(config['rpc'], timeout=3000, heartbeat=None)

#####################################################################################################################
## CLASSES
##################################################################################################################### 

class MainWindow(QMainWindow):

	# classificationChanged  = pyqtSignal()

	def __init__(self, parent=None):
		super().__init__(parent)
		centralWidget = QWidget(self)
		gridlayout = QGridLayout(centralWidget)
		gridlayout.setContentsMargins(0,0,0,0)
		gridlayout.setHorizontalSpacing(0)

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

		# self._classification = ''

	# @pyqtProperty(str, notify=classificationChanged)
	# def classification(self):
	# 	return self._classification

	# @classification.setter
	# def classification(self, text):
	# 	self._classification = text
	# 	self.classificationChanged.emit()

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
viewer.setMinimumWidth(1000)
viewer.setMinimumHeight(800)

# slice panes
slicePaneTL = SlicePane('TL', viewer, sync=True)
slicePaneTR = SlicePane('TR', viewer, sync=True)
slicePaneBL = SlicePane('BL', viewer, sync=True)

# add panes
viewer.addPane(slicePaneTL, (0,.5,.5,1))
viewer.addPane(slicePaneTR, (.5,.5,1,1))
viewer.addPane(slicePaneBL, (0,0,.5,.5))

# # right QML widget
# component = QQuickView()
# component.rootContext().setContextProperty("MainWindow", mainWindow)
# component.setSource(QUrl('panel_eugene.qml'))
# rightWidget = QWidget.createWindowContainer(component)
# rightWidget.setMinimumSize(300,200)

def load():
	pass
	# # DICOM_PATH = "/Users/benjaminhon/Developer/HeadHunter/notebooks/220259"
	# path  = QFileDialog().getExistingDirectory()
	# # generate series
	# (series, seriesUIDs) = generateSeries(path)

	# # predict and get nii
	# NII_PATH = "/Users/benjaminhon/Developer/HeadHunter/notebooks/220259.nii"

	# # # predict and get seriesUID and numpy array
	# # aini = AINI()
	# # aini.initModel()
	# # aini.restoreModel()
	# # prediction = aini.predictClassification(filepath=path)

	# # masksArr = [ maskInfo['mask'] for maskName, maskInfo in prediction['MASK'].items() ]
	# # classifications = [ maskInfo['label'] for maskName, maskInfo in prediction['MASK'].items() ]

	# # displayClassification = ''
	# # for m in classifications:
	# # 	for k, v in m.items():
	# # 		displayClassification = displayClassification + k + ': ' + str(v) + '\n'
	# # 	displayClassification = displayClassification + '\n'

	# # # update classification
	# # mainWindow.classification = displayClassification

	# # populate slice panes
	# slicePaneTL.loadDicomNii(series[prediction['UID']])
	# slicePaneTR.loadDicomNii(series[prediction['UID']], numpyMasks=masksArr)
	# slicePaneBL.loadDicomNii(series[prediction['UID']], numpyMasks=masksArr)

def test():
	NII_PATH = "/Users/benjaminhon/Developer/HeadHunter/notebooks/220259.nii"
	DICOM_PATH = "/Users/benjaminhon/Developer/HeadHunter/notebooks/220259"

	(series, seriesUIDs) = generateSeries(DICOM_PATH)

	dicomSeries = DicomSeries(series[seriesUIDs[2]])
	mask = LabelMap(dicomSeries.GetOutput(), niiPath=NII_PATH)
	overlay = Overlay(series[seriesUIDs[2]], niiPath = NII_PATH)
	
	slicePaneTL.loadModel(dicomSeries)
	slicePaneTR.loadModel(mask)
	slicePaneBL.loadModel(overlay)

test()

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
# mainWindow.rightPanel.addWidget(rightWidget)
mainWindow.centerPanel.addWidget(viewer)

viewer.startEventLoop()
sys.exit(app.exec_())