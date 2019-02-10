from graphics.geometry import *
from graphics.io import *

mshfile = '{}/cube.obj'.format(graphics.GRAPHICS_DATA_DIR)
matfile = 'cube.mtl'

# create a cube and save it
mesh, materials = cube()
save_obj( mesh, mshfile, matfile )
save_mtl_file( materials, '{}/{}'.format( graphics.GRAPHICS_DATA_DIR, matfile ) )

# now load it
mesh, materials = load_obj( mshfile )

print('hello')