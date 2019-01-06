from graphics.geometry import Mesh

def cube():
    #   7-------6
    #  /|      /|
    # 4-+-----5 |
    # | |     | |
    # | 3-----+-2
    # |/      |/
    # 0-------1
    l = -0.5
    h =  0.5
    vtx = [
        [l,l,l],[h,l,l],[h,l,h],[l,l,h],
        [l,h,l],[h,h,l],[h,h,h],[l,h,h]
    ]
    tex = [
        [0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0]
    ]
    face = [
        [0,3,2,1],
        [4,5,6,7],
        [0,4,7,3],
        [1,2,6,5],
        [2,3,7,6],
        [0,1,5,4]
    ]
    mat = [
        'bottom', 'top', 'left', 'right', 'far', 'near'
    ]
    tc = [ 0, 1, 2, 3 ]

    m = Mesh()
    for v in vtx:
        m.add_vertex( v )
    for t in tex:
        m.add_texcoord( t )
    for side,f in zip(mat,face):
        m.add_material( side )
        m.add_face( f, tc )
    
    m.finalize()
    return m