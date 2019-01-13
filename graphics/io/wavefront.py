import os

import graphics

def save_mtl_file( materials, filename ):
    with open( filename, 'w' ) as f:
        
        def write_key( key, vals ):
            if vals is not None:
                if hasattr(type(vals),'__iter__') and type(vals) != str:
                    f.write( '{} {}\n'.format(key,' '.join('{}'.format(v) for v in vals)) )
                else:
                    f.write( '{} {}\n'.format(key,vals) )

        for mat in materials:
            f.write( 'newmtl {}\n'.format(mat.name) )
            write_key('Kd',mat.diffuse )
            write_key('Ka',mat.ambient )
            write_key('Ks',mat.specular )
            write_key('Ns',mat.specular_exponent )
            write_key('map_Kd',mat.diffuse_map)
            write_key('map_Ka',mat.ambient_map)
            write_key('map_Ks',mat.specular_map)
            write_key('map_bump',mat.bump_map)
            f.write('\n')

def load_mtl_file( filename ):
    with open( filename, 'r' ) as f:
        materials = []
        curr_mat = None

        def floatify( vals ):
            return [ float(v) for v in vals ]

        for line in f:
            toks = line.split()
            if len(toks) == 0:
                continue

            if toks[0] == 'newmtl':
                if curr_mat is not None:
                    materials.append( curr_mat )
                curr_mat = graphics.appearance.Material( toks[1] )
            elif curr_mat is not None:
                if toks[0] == 'Kd':
                    curr_mat.diffuse = floatify(toks[1::])
                elif toks[0] == 'Ka':
                    curr_mat.diffuse = floatify(toks[1::])
                elif toks[0] == 'Ks':
                    curr_mat.specular = floatify(toks[1::])
                elif toks[0] == 'Ns':
                    curr_mat.specular_exponent = float(toks[1])
                elif toks[0] == 'map_Ka':
                    curr_mat.diffuse_map = toks[-1]
                elif toks[0] == 'map_Kd':
                    curr_mat.ambient_map = toks[-1]
                elif toks[0] == 'map_Ks':
                    curr_mat.specular_map = toks[-1]
                elif toks[0] == 'map_bump':
                    curr_mat.bump_map = toks[-1]

        if curr_mat is not None:
            materials.append( curr_mat )
        return materials


def load_obj( filename ):
    with open( filename, 'r' ) as f:
        mesh = graphics.geometry.Mesh()
        path = os.path.dirname(filename)
        materials = None
        curr_mat = -1
        for line in f:
            toks = line.split(' ')
            if len(toks) == 0:
                continue
            elif toks[0] == 'mtllib':
                mesh.material_file = toks[1]
                materials = load_mtl_file( '{}/{}'.format(path,toks[1]) )
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
        return mesh, materials

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
