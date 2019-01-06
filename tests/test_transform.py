import unittest

import sys
import numpy

from PyQt5.QtWidgets import *
from OpenGL.GL import *
from OpenGL.GLU import *

from graphics.opengl import GLWidget
from graphics.core import Transform

class TestTransform(unittest.TestCase):

    def test_mul( self ):
        pos  = numpy.random.randn(3)
        deg  = numpy.random.uniform(-180,180)
        axis = numpy.random.randn(3)
        T = Transform().translate( *pos )
        R = Transform().rotate( deg, *axis )

        M1 = Transform().translate( *pos ).rotate( deg, *axis )        
        M2 = R*T
        M3 = R*T.matrix()
        self.assertTrue( numpy.allclose( M1.matrix(), M2.matrix() ) )
        self.assertTrue( numpy.allclose( M1.matrix(), M3 ) )

    def test_translate(self):
        t = [1.0, 2.0, 3.0]
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef( t[0], t[1], t[2] )
        Mgl = glGetFloatv( GL_MODELVIEW_MATRIX ).transpose()
        M   = Transform().translate(t[0],t[1],t[2]).matrix()
        self.assertTrue( numpy.allclose(M,Mgl) )

    def test_scale(self):
        s = [2.0, 3.0, 4.0]
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glScalef( s[0], s[1], s[2] )
        Mgl = glGetFloatv( GL_MODELVIEW_MATRIX ).transpose()
        M   = Transform().scale(s[0],s[1],s[2]).matrix()
        self.assertTrue( numpy.allclose(M,Mgl) )

    def test_rotate(self):
        for i in range(1000):
            deg  = (numpy.random.rand()-0.5)*360.0
            axis = numpy.random.randn(3)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glRotatef( deg, axis[0], axis[1], axis[2] )
            Mgl = glGetFloatv( GL_MODELVIEW_MATRIX ).transpose()
            M   = Transform().rotate( deg, axis[0], axis[1], axis[2] ).matrix()
            self.assertTrue( numpy.allclose(M, Mgl, rtol=1e-5, atol=1e-5) )

    def test_lookat(self):
        for i in range(1000):
            params = numpy.random.randn(9)
            glMatrixMode( GL_MODELVIEW )
            glLoadIdentity()
            gluLookAt( *params )
            Mgl = glGetFloatv( GL_MODELVIEW_MATRIX ).transpose()
            M   = Transform().lookat( *params ).matrix()
            self.assertTrue( numpy.allclose( M, Mgl, rtol=1e-5, atol=1e-5 ) )

    def test_perspective(self):
        for i in range(1000):
            fov = numpy.random.uniform( 1.0, 70.0 )
            aspect = numpy.random.uniform( 0.5, 2.0 )
            near = numpy.random.uniform()
            far = near + numpy.random.uniform()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            gluPerspective( fov, aspect, near, far )
            Mgl = glGetFloatv( GL_MODELVIEW_MATRIX ).transpose()
            M   = Transform().perspective( fov, aspect, near, far ).matrix()
            self.assertTrue( numpy.allclose(M, Mgl, rtol=1e-5, atol=1e-5 ) )

    def test_ortho(self):
        for i in range(1000):
            p = numpy.random.randn(6)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glOrtho( *p )
            Mgl = glGetFloatv( GL_MODELVIEW_MATRIX ).transpose()
            M   = Transform().ortho( *p ).matrix()
            self.assertTrue( numpy.allclose( M, Mgl ) )

    def test_frustum(self):
        for i in range(1000):
            p = numpy.random.randn(6)
            p[4] = abs(p[4])
            p[5] = abs(p[5])
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glFrustum( *p )
            Mgl = glGetFloatv( GL_MODELVIEW_MATRIX ).transpose()
            M   = Transform().frustum( *p ).matrix()
            self.assertTrue( numpy.allclose( M, Mgl ) )



if __name__ == '__main__':

    # needed to use the OpenGL functions
    app = QApplication(sys.argv)
    win = GLWidget()
    win.show()

    # what we actually want to do
    try:
        unittest.main()
    except SystemExit:
        pass