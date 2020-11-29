"""
nurbsSurface component object library
"""

# imports local
import cgp_maya_utils.constants
from . import _generic


class IsoparmU(_generic.Component):
    """component object that manipulates an ``isoparmU`` component
    """

    # ATTRIBUTES #

    _componentType = cgp_maya_utils.constants.ComponentType.ISOPARM_U


class IsoparmV(_generic.Component):
    """component object that manipulates an ``isoparmV`` component
    """

    # ATTRIBUTES #

    _componentType = cgp_maya_utils.constants.ComponentType.ISOPARM_V


class SurfacePatch(_generic.Component):
    """component object that manipulates an ``surfacePatch`` component
    """

    # ATTRIBUTES #

    _componentType = cgp_maya_utils.constants.ComponentType.SURFACE_PATCH


class SurfacePoint(_generic.TransformComponent):
    """component object that manipulates an ``surfacePoint`` component
    """

    # ATTRIBUTES #

    _componentType = cgp_maya_utils.constants.ComponentType.SURFACE_POINT
