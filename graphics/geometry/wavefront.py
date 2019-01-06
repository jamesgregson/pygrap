import os

def load_obj( filename ):
    with open( filename, 'r' ) as f:
        mesh = Mesh()
        curr_mat = -1
        for line in f:
            toks = line.split(' ')
            if len(toks) == 0:
                continue
            elif toks[0] == 'mtllib':
                mesh.material_file = toks[1]
            elif toks[0] == 'usemtl':
                curr_mat = mesh.add_material( toks[1] )
            elif toks[0] == 'v':
                mesh.add_vertex( (float(toks[1]),float(toks[2]), float(toks(3))) )
            elif toks[0] == 'vt':
                mesh.add_texcoord( (float(toks[1]), float(toks[2])) )
            elif toks[0] == 'f':
                vtx = []
                tc  = []
                for tok in toks[1:]:
                    if '/' not in tok:
                        vtx.append( int(tok)-1 )
                    else:
                        ind = tok.split('/')
                        vtx.append( int(ind[0])-1 )
                        if len(ind[1]) > 0:
                            tc.append( int(ind[1])-1 )
                mesh.add_face( vtx, tc, curr_mat )
        mesh.finalize()
        return mesh
    return None



def save_obj( mesh, filename, mat_file=None ):
    with open( filename, 'w' ) as f:
        d = os.path.splitext(filename)[0]
        mfile = '{}.mtl'.format(d)
        if mat_file is not None:
            mfile = mat_file

        f.write('# Mesh file output by mesh.py\n' )
        f.write('mtllib {}\n'.format(mfile) )

        last_mat = None

        vtx = mesh.vertices
        nor = mesh.normals
        tex = mesh.texture_coords
        for idx in range(vtx.shape[0]):
            f.write('v {} {} {}\n'.format(vtx[idx,0],vtx[idx,1],vtx[idx,2]) )
            f.write('vn {} {} {}\n'.format(nor[idx,0],nor[idx,1],nor[idx,2]) )
            f.write('vt {} {}\n'.format(tex[idx,0],tex[idx,1]) )
        for idx in range(0,vtx.shape[0],3):
            mid = mesh.mat[idx//3]
            if mid >= 0 and mid != last_mat:
                f.write( 'usemtl {}\n'.format(mesh.materials[mid]) )
                last_mat = mid
            f.write( 'f {}/{}/{} {}/{}/{} {}/{}/{}\n'.format(idx+1,idx+1,idx+1,idx+2,idx+2,idx+2,idx+3,idx+3,idx+3))
