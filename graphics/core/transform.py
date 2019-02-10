# -*- coding: utf-8 -*-
"""OpenGL-equivalent transformation class.

This module provide basic 4x4 homogeneous transformations equivalent to
the commonly used but deprecated OpenGL matrix functions.

The transforms are represented as row-major matrices, in contrast to
OpenGL column-major layouts, in order to be consistent with Numpy

Transformations can be chained where the sequence order is left-to-right,
i.e. the opposite of matrix multiplication.

Transformations can also be multiplied where the sequence order is right-
to-left, i.e. the same as matrix multiplication.

Transforms can be post-multiplied with 3- or 4-element sequences, assumed
to represent points. The returned values are numpy arrays with same 
length.  3-element sequences are promoted to homogeneous points and 
divided by the resulting homogeneous coordinate. The function homogenize 
can be used to generate homogenous points or vectors by specifying the
homogeneous coordinate, see below.

Transforms can also be post-multiplied with 3- or 4-row matrices, assumed
to represent a set of points where each point is a column vector, i.e.
T[:,3] would be the third point if T is a 4xN matrix. This can be used to
apply transformations to existing 4x4 numpy matrices as well but only by 
pre-multiplying the numpy matrix with a transform.

Implemented functions::

    glTranslate    -> Transform.translate
    glRotate       -> Transform.rotate
    glScale        -> Transform.scale

    glFrustum      -> Transform.frustum
    glOrtho        -> Transform.ortho
    
    gluLookat      -> Transform.lookat
    gluPerspective -> Transform.perspective

Example::

    from transform import Transform

    # scale by (2,3,4) then translate by (1,2,3) then rotate 45 degrees about y-axis
    T = Transform().scale(2,3,4).translate(1,2,3).rotate( 45.0, 0.0, 1.0, 0.0 )

    # get the inverse
    iT = T.inverse()

    # retrieve the matrix, transpose for OpenGL column-major layout
    t = T.matrix().transpose()

"""

import numpy
import collections

def homogenize( A, hom=1.0 ):
    """Homogenize an input point or set of points

    Args:
        A (3 or 4 element/row resp. sequence/matrix): Input point or
            set of points. Multiple points are stored as columns in A

        hom (float): homogeneous coordinate to set in the case of 3
            element/row inputs A. Use 1.0 for 3D points and 0.0 for
            3D vectors.

    Return: 4-element/-row ndarray with specified homogeneous 
        coordinate in case of 3-element/-row inputs

    Raises:
        ValueError when input is neither a sequence nor ndarray

    """
    if len(A) == 3:
        if isinstance(A,collections.Sequence):
            return numpy.array([A[0],A[1],A[2],hom],dtype=numpy.float32)
        elif isinstance(A,numpy.ndarray):
            return numpy.row_stack( (A,hom*numpy.ones_like(A[0])) )
    elif len(A) == 4:
        if isinstance(A,collections.Sequence):
            return numpy.array( A, dtype=numpy.float32 )
        elif isinstance(A,numpy.ndarray):
            return A
    else:
        raise ValueError('Expected a 3 or 4 element sequence or a 3 or 4 row/element ndarray')



class Transform:
    def __init__( self, T=None ):
        """Initialize a Transform as identity or specified matrix"""
        if T is not None:
            if isinstance(T,Transform):
                self.M = T.M.copy()
            elif isinstance(T,numpy.ndarray):
                self.M = T.copy()
            else:
                raise ValueError('Expected a transform or 4x4 numpy.ndarray')
        else:
            self.M = numpy.eye( 4, dtype=numpy.float32 )

    def matrix( self ):
        """Return the transformation matric"""
        return self.M.copy()

    def inverse( self ):
        """Return the inverse of the transform"""
        return Transform( numpy.linalg.inv(self.M) )

    def __mul__( self, T ):
        """Post-multiply by another Transformation or (set of) point(s)"""
        if isinstance(T, Transform):
            return Transform( numpy.dot(self.M, T.M) )
        else:
            R = numpy.dot( self.M, homogenize(T) )
            if len(T) == 3:
                R[0] /= R[3]
                R[1] /= R[3]
                R[2] /= R[3]
                return R[0:3]
            else:
                return R

    def perspective( self, fovy, aspect, near, far ):
        """Implementation of gluPerspective"""
        f = 1.0/numpy.tan(numpy.deg2rad(fovy)/2)
        T = numpy.array([
            [f/aspect, 0.0, 0.0, 0.0],
            [     0.0,   f, 0.0, 0.0],
            [     0.0, 0.0, (far+near)/(near-far), 2*far*near/(near-far) ],
            [ 0.0, 0.0, -1.0, 0.0]
        ], dtype=numpy.float32)
        return Transform( numpy.dot( T, self.M ) )

    def frustum( self, left, right, bottom, top, near, far ):
        """Implementation of gluFrustum"""
        A = (right+left)/(right-left)
        B = (top+bottom)/(top-bottom)
        C = -(far+near)/(far-near)
        D = -2*far*near/(far-near)
        T = numpy.array([
            [ 2.0*near/(right-left),                 0.0,    A, 0.0 ],
            [ 0.0,                   2*near/(top-bottom),    B, 0.0 ],
            [ 0.0,                                   0.0,    C,   D ],
            [ 0.0,                                   0.0, -1.0, 0.0 ]
        ], dtype=numpy.float32 )
        return Transform( numpy.dot( T, self.M ) )

    def ortho( self, left, right, bottom, top, near, far ):
        """Implementation of glOrtho"""
        T = numpy.array([
            [2.0/(right-left),              0.0,             0.0, -(right+left)/(right-left)],
            [             0.0, 2.0/(top-bottom),             0.0, -(top+bottom)/(top-bottom)],
            [             0.0,              0.0, -2.0/(far-near), -(far+near)/(far-near) ],
            [ 0.0, 0.0, 0.0, 1.0 ]
        ], dtype=numpy.float32 )
        return Transform( numpy.dot( T, self.M ) ) 

    def lookat( self, ex, ey, ez, cx, cy, cz, ux, uy, uz ):
        """Implementation of gluLookat"""
        f = numpy.array([cx-ex,cy-ey,cz-ez],dtype=numpy.float32)
        f /= numpy.linalg.norm(f)
        u = numpy.array([ux,uy,uz],dtype=numpy.float32)
        r = numpy.cross(f,u)
        r /= numpy.linalg.norm(r)
        u = numpy.cross( r, f )
        e = numpy.array([ex,ey,ez],dtype=numpy.float32)
        T = numpy.array([
            [ r[0],  r[1],  r[2], -numpy.dot(r,e)],
            [ u[0],  u[1],  u[2], -numpy.dot(u,e)],
            [-f[0], -f[1], -f[2],  numpy.dot(f,e)],
            [ 0.0,  0.0,  0.0, 1.0]
        ], dtype=numpy.float32)
        return Transform( numpy.dot( T, self.M ) )

    def translate( self, x, y, z ):
        """Implementation of glTranslatef"""
        T = numpy.array([
            [1.0, 0.0, 0.0,   x],
            [0.0, 1.0, 0.0,   y],
            [0.0, 0.0, 1.0,   z],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=numpy.float32 )
        return Transform( numpy.dot( T, self.M ) )

    def scale( self, x, y, z ):
        """Implementation of glScalef"""
        S = numpy.array([
            [  x, 0.0, 0.0, 0.0],
            [0.0,   y, 0.0, 0.0],
            [0.0, 0.0,   z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=numpy.float32 )
        return Transform( numpy.dot( S, self.M ) )

    def rotate( self, deg, ax, ay, az ):
        """Implementation of glRotatef"""
        L = numpy.sqrt(ax**2+ay**2+az**2)
        x = ax/L
        y = ay/L
        z = az/L

        rad = numpy.deg2rad( deg )
        c = numpy.cos(rad)
        s = numpy.sin(rad)
        C = 1.0-c

        R = numpy.array([
            [x*x*C + c,   x*y*C - z*s, x*z*C + y*s, 0.0],
            [y*x*C + z*s, y*y*C + c,   y*z*C - x*s, 0.0],
            [z*x*C - y*s, z*y*C + x*s, z*z*C + c,   0.0],
            [0.0, 0.0, 0.0, 1.0]            
        ], dtype=numpy.float32 )
        return Transform( numpy.dot( R, self.M ) )