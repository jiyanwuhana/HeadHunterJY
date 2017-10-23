import sys
import os

from PyQt5.QtCore import Qt, QUrl, pyqtSlot, pyqtProperty, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QFileDialog
from PyQt5.QtQuick import QQuickView
import vtk
import itk
from Viewer import Viewer, SlicePane
from Models import DicomSeries, LabelMap, Overlay
from Types import SliceOrientation
from EventManagers import PanesSyncEventManager

import numpy as np
import pickle
from rpc import Rpc

rpc = Rpc().get_client()

eg_to_ch_pathology = {'bpynz': '表皮样囊肿', 'tsjl':'听神经瘤',  'nml':'脑膜瘤', 'others': '其他'}

#####################################################################################################################
## CLASSES
##################################################################################################################### 

class MainWindow(QMainWindow):

  classificationChanged  = pyqtSignal()

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

    self._classification = ''

  @pyqtProperty(str, notify=classificationChanged)
  def classification(self):
    return self._classification

  @classification.setter
  def classification(self, text):
    self._classification = text
    self.classificationChanged.emit()

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
slicePaneTL = SlicePane('TL')
slicePaneTR = SlicePane('TR')
slicePaneBL = SlicePane('BL')

# add panes
viewer.addPane(slicePaneTL, (0,.5,.5,1))
viewer.addPane(slicePaneTR, (.5,.5,1,1))
viewer.addPane(slicePaneBL, (0,0,.5,.5))

# event manager
paneSyncEventManager = PanesSyncEventManager(viewer.panes, sync=True)

# subscribe to event managers
slicePaneTL.subscribeTo(paneSyncEventManager)
slicePaneTR.subscribeTo(paneSyncEventManager)
slicePaneBL.subscribeTo(paneSyncEventManager)

# # right QML widget
# component = QQuickView()
# component.rootContext().setContextProperty("MainWindow", mainWindow)
# component.setSource(QUrl('panel_eugene.qml'))
# rightWidget = QWidget.createWindowContainer(component)
# rightWidget.setMinimumSize(300,200)

def load():
  try:
    
    # get dicom path
    path  = QFileDialog().getExistingDirectory()
    # generate series
    (series, seriesUIDs) = generateSeries(path)
    # predict and get seriesUID and numpy array
    results = pickle.loads(rpc.predicting(path), encoding='latin1')
    # create argmax
    BACKGROUND = 0.4
    masks = [ mask for uid, cl, mask in results ]
    background = np.full(masks[0].shape, BACKGROUND)
    masks = [ background ] + masks
    argMax = np.argmax(masks, axis=0).astype(np.uint8)

    # create models
    (uid, classification, mask) = results[0]

    dicomModel = DicomSeries(series[uid])
    maskModel = LabelMap(dicomModel.GetOutput(), ndarr=argMax)
    overlayModel = Overlay(series[uid], numpyLabelMap=argMax)

    slicePaneTL.loadModel(dicomModel)
    slicePaneTR.loadModel(maskModel)
    # slicePaneBL.loadModel(overlayModel)

    displayClassification = '\n' + '\n'.join([f"{eg_to_ch_pathology[cl]}:\n {round(li*100)}%\n" for li, cl in classification])

    mainWindow.classification = displayClassification
    
  except Exception as e:
    print(e)
    pass

def test():
  NII_PATH = os.path.join(os.getcwd(), 'notebooks/220259.nii')
  DICOM_PATH = os.path.join(os.getcwd(), 'notebooks/220259')
  (series, seriesUIDs) = generateSeries(DICOM_PATH)
  dicomSeries = DicomSeries(series[seriesUIDs[2]])
  
  mask = LabelMap(dicomSeries.GetOutput(), niiPath=NII_PATH)
  overlay = Overlay(series[seriesUIDs[2]], niiPath=NII_PATH)
  slicePaneTL.loadModel(dicomSeries, SliceOrientation.AXIAL)
  slicePaneTR.loadModel(mask, SliceOrientation.AXIAL)
  slicePaneBL.loadModel(overlay, SliceOrientation.CORONAL)

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