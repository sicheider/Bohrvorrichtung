from PyQt4 import QtCore, QtGui, uic

parentInterface = uic.loadUiType('Interface.ui')[0]

class Interface(parentInterface, QtGui.QMainWindow):
  def __init__(self):
    QtGui.QMainWindow.__init__(self)
    self.setupUi(self)
    self.setWindowFlags(QtCore.Qt.Window)
    self.show()
