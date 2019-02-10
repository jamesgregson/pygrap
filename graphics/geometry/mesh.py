import os
import numpy

class Mesh:
    def __init__( self ):
        self.init_vtx = []
        self.init_tex = []
        self.init_tri = []
        self.init_mat = -1

        self.mat_file = None
        self.materials = []
        self.mat = []

        self.vtx = None
        self.tex = None
        self.nor = None
        self.tri = None
        self.mat_tris = None

    @property
    def vertices( self ):
        if self.vtx is None:
            raise ValueError('Must load existing mesh or call finalize before accessing vertices')
        return self.vtx

    @property
    def texture_coords( self ):
        if self.tex is None:
            raise ValueError('Must load existing mesh or call finalize before accessing texture coordinates')
        return self.tex

    @property
    def normals( self ):
        if self.nor is None:
            raise ValueError('Must load existing mesh or call finalize before accessing normals')
        return self.nor

    @property
    def material_triangles( self ):
        if self.mat_tris is None:
            raise ValueError('Must load existing mesh or call finalize before accessing material triangles')
        return self.mat_tris

    @property
    def material_file( self ):
        return self.mat_file

    @material_file.setter
    def material_file( self, filename ):
        self.mat_file = filename

    def add_material( self, matname ):
        if matname not in self.materials:
            self.init_mat = len(self.materials)
            self.materials.append( matname )
        else:
            self.init_mat = self.materials.index(matname)
        return self.init_mat

    def add_vertex( self, pos ):
        self.init_vtx.append( ( pos[0], pos[1], pos[2] ) )
        return len(self.init_vtx)

    def add_texcoord( self, tx ):
        self.init_tex.append( (tx[0], tx[1]) )
        return len(self.init_tex)

    def add_face( self, vtx, tc=None, mat=-1 ):
        if tc is None or len(tc) == 0:
            tc = [ None ]*len(vtx)
        if mat < 0:
            mat = self.init_mat

        s = vtx[0]
        for i in range(1,len(vtx)-1):
            self.init_tri.append( ((s,tc[0]),(vtx[i],tc[i]),(vtx[i+1],tc[i+1])) )
            self.mat.append( mat )
        return len(self.init_tri)

    def finalize( self ):
        vtx = []
        tex = []
        fnor = []
        vnor = [ numpy.array((0,0,0),dtype=float) for a in range(len(self.init_vtx)) ]

        self.mat, self.init_tri = zip( *[ (mat,tri) for mat, tri in sorted(zip(self.mat,self.init_tri))] )

        self.num_materials = 0
        self.mat_tris = {}

        curr_mat  = 0
        mat_start = 0 

        for idx,f in enumerate(self.init_tri):
            if self.mat[idx] != curr_mat:
                self.mat_tris[self.materials[curr_mat]] = (mat_start,idx)
                curr_mat  = self.mat[idx]
                mat_start = idx

            # compute face normal
            a = numpy.array( self.init_vtx[f[0][0]] )
            b = numpy.array( self.init_vtx[f[1][0]] )
            c = numpy.array( self.init_vtx[f[2][0]] )
            n = numpy.cross( c-a, b-a )
            vnor[ f[0][0] ] += n
            vnor[ f[1][0] ] += n
            vnor[ f[2][0] ] += n

            vtx.append( a )
            if self.init_tex[f[0][1]] is not None:
                tex.append( self.init_tex[f[0][1]] )
            else:
                tex.append( (0.0, 0.0) )

            vtx.append( b )
            if self.init_tex[f[1][1]] is not None:
                tex.append( self.init_tex[f[1][1]] )
            else:
                tex.append( (0.0, 0.0) )

            vtx.append( c )
            if self.init_tex[f[2][1]] is not None:
                tex.append( self.init_tex[f[2][1]] )
            else:
                tex.append( (0.0, 0.0) )

        self.mat_tris[self.materials[curr_mat]] = (mat_start,len(self.init_tri))

        self.vtx = numpy.array( vtx, dtype=numpy.float32 )
        self.tex = numpy.array( tex, dtype=numpy.float32 )
        self.nor = numpy.zeros_like( self.vtx )
        self.tri = numpy.array( self.init_tri )

        # accumulate normals to vertices
        for idx, f in enumerate(self.init_tri):
            self.nor[idx*3+0,:] = vnor[f[0][0]]/numpy.linalg.norm(vnor[f[0][0]])
            self.nor[idx*3+1,:] = vnor[f[1][0]]/numpy.linalg.norm(vnor[f[1][0]])
            self.nor[idx*3+2,:] = vnor[f[2][0]]/numpy.linalg.norm(vnor[f[2][0]])

