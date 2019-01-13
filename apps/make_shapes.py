import graphics

mat_list = [
    {
        'name': 'bottom',
        'diffuse': (0.25,0.50,0.25),
        'ambient': (1.0,0.5,0.25),
        'specular': (0.2,1.0,0.3),
        'specular_exponent': 3.0,
        'diffuse_map': 'diffuse.png',
        'ambient_map': 'ambient.png',
        'specular_map': 'specular.png',
        'bump_map': 'bump.png'
    },{
        'name': 'top',
        'diffuse': (0.50,1.00,0.50)
    },{
        'name': 'left',
        'diffuse': (0.50,0.25,0.25)
    },{
        'name': 'right',
        'diffuse': (1.00,0.50,0.50)
    },{
        'name': 'near',
        'diffuse': (0.25,0.25,0.50)
    },{
        'name': 'far',
        'diffuse': (0.25,0.25,1.00)
    }
]
materials = [ graphics.appearance.Material(mdict=mat) for mat in mat_list ]

graphics.io.save_mtl_file( materials, '{}/cube.mtl'.format(graphics.GRAPHICS_DATA_DIR) )

mat = graphics.io.load_mtl_file( '{}/cube.mtl'.format(graphics.GRAPHICS_DATA_DIR) )

graphics.io.save_mtl_file( materials, '{}/cube2.mtl'.format(graphics.GRAPHICS_DATA_DIR) )

# c = graphics.geometry.cube()
# graphics.geometry.save_obj( c, '{}/cube.obj'.format( graphics.GRAPHICS_DATA_DIR), mat_file='cube.mtl' )

# mats = graphics.geometry.load_materials( '{}/cube.mtl'.format(graphics.GRAPHICS_DATA_DIR) )
# print( mats )