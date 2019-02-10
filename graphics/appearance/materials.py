import numpy

class Material:
    """Defines a basic material with ambient, diffuse, specular terms

    Attributes:
        name (string): name of material

        diffuse (3x float): diffuse RGB albedo

        ambient (3x float): ambient RGB term

        specular (3x float): specular RGB term

        specular_exponent (float): exponent for specular model

        diffuse_map (string): name of file containing diffuse
            albedo texture map

        ambient_map (string): name of file containing ambient
            texture map

        specular_map (string): name of file containing specular
            texture map

        bump_map (string): name of file containing bump
            texture map
    """

    def __init__( self, name=None, mdict=None ):
        """Constructs a material

        Dictionary keys should be the name of the corresponding properties, as string
        
        Args:
            name (string): name of material, may be overridden by mdict (see below)

            mdict (dict): dictionary containing values for the material parameters,
                overrides material name
        """
        self._name        = name
        self._diffuse     = numpy.array([1.0, 1.0, 1.0])
        self._diffuse_map = None
        self._ambient     = numpy.array([0.0, 0.0, 0.0])
        self._ambient_map = None
        self._specular    = numpy.array([0.0, 0.0, 0.0])
        self._specular_map = None
        self._specular_exponent = 1.0
        self._bump_map     = None

        if mdict is not None:
            if 'name' in mdict:
                self._name = mdict['name']
            if 'diffuse' in mdict:
                self.diffuse = mdict['diffuse']
            if 'ambient' in mdict:
                self.ambient = mdict['ambient']
            if 'specular' in mdict:
                self.specular = mdict['specular']
            if 'specular_exponent' in mdict:
                self.specular_exponent = mdict['specular_exponent']
            if 'diffuse_map' in mdict:
                self.diffuse_map = mdict['diffuse_map']
            if 'ambient_map' in mdict:
                self.ambient_map = mdict['ambient_map']
            if 'specular_map' in mdict:
                self.specular_map = mdict['specular_map']
            if 'bump_map' in mdict:
                self.bump_map = mdict['bump_map']

    def to_dict( self ):
        """Returns the material in dict form"""
        m = {
            'name': self.name.copy,
            'diffuse': self.diffuse,
            'ambient': self.ambient,
            'specular': self.specular,
            'specular_exponent': self.specular_exponent
        }
        if self.diffuse_map is not None:
            m['diffuse_map'] = self.diffuse_map
        if self.ambient_map is not None:
            m['ambient_map'] = self.ambient_map
        if self.specular_map is not None:
            m['specular_map'] = self.specular_map
        if self.bump_map is not None:
            m['bump_map'] = self.bump_map
        return m

    @property
    def name( self ):
        return self._name

    @property
    def diffuse( self ):
        return self._diffuse

    @diffuse.setter
    def diffuse( self, val ):
        if len(val) != 3:
            raise ValueError('Expected 3-element array-like')
        self._diffuse = numpy.array([v for v in val])

    @property 
    def ambient( self ):
        return self._ambient

    @ambient.setter
    def ambient( self, val ):
        if len(val) != 3:
            raise ValueError('Expected 3-element array-like')
        self._ambient = numpy.array([v for v in val])

    @property 
    def specular( self ):
        return self._specular

    @specular.setter
    def specular( self, val ):
        if len(val) != 3:
            raise ValueError('Expected 3-element array-like')
        self._specular = numpy.array([v for v in val])

    @property
    def specular_exponent( self ):
        return self._specular_exponent

    @specular_exponent.setter
    def specular_exponent( self, val ):
        if hasattr(type(val),'__iter__'):
            raise ValueError('Expected scalar for specular exponent')
        self._specular_exponent = val

    @property
    def diffuse_map( self ):
        return self._diffuse_map

    @diffuse_map.setter
    def diffuse_map( self, val ):
        self._diffuse_map = val

    @property
    def ambient_map( self ):
        return self._ambient_map

    @ambient_map.setter
    def ambient_map( self, val ):
        self._ambient_map = val

    @property
    def specular_map( self ):
        return self._specular_map

    @specular_map.setter
    def specular_map( self, val ):
        self._specular_map = val

    @property
    def bump_map( self ):
        return self._bump_map

    @bump_map.setter
    def bump_map( self, val ):
        self._bump_map = val
