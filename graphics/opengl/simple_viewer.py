import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtOpenGL

class SimpleViewer(QtOpenGL.QGLWidget):

    initialize_cb    = QtCore.pyqtSignal()
    resize_cb        = QtCore.pyqtSignal(int,int)
    idle_cb          = QtCore.pyqtSignal()
    render_cb        = QtCore.pyqtSignal()

    mouse_move_cb    = QtCore.pyqtSignal( QtGui.QMouseEvent )
    mouse_press_cb   = QtCore.pyqtSignal( QtGui.QMouseEvent )
    mouse_release_cb = QtCore.pyqtSignal( QtGui.QMouseEvent )
    mouse_wheel_cb   = QtCore.pyqtSignal( QtGui.QWheelEvent )

    key_press_cb     = QtCore.pyqtSignal( QtGui.QKeyEvent )
    key_release_cb   = QtCore.pyqtSignal( QtGui.QKeyEvent )

    @staticmethod
    def application():
        return QtWidgets.QApplication(sys.argv)

    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.setMouseTracking(True)


    def idle( self ):
        self.idle_cb.emit()
        self.updateGL()

    def mouseMoveEvent( self, evt ):
        self.mouse_move_cb.emit( evt )

    def mousePressEvent( self, evt ):
        self.mouse_press_cb.emit( evt )

    def mouseReleaseEvent( self, evt ):
        self.mouse_release_cb.emit( evt )

    def keyPressEvent( self, evt ):
        self.key_press_cb.emit(evt)

    def keyReleaseEvent( self, evt ):
        self.key_release_cb.emit(evt)

    def initializeGL(self):
        self.initialize_cb.emit()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot( False )
        self.timer.setInterval( 0.016 )
        self.timer.timeout.connect( self.idle )
        self.timer.start()

    def resizeGL(self, width, height):
        if height == 0: height = 1
        self.resize_cb.emit(width,height)

    def paintGL(self):
        self.render_cb.emit()

