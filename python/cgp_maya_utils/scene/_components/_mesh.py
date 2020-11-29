"""
mesh component object library
"""

# imports local
import cgp_maya_utils.constants
from . import _generic


class Edge(_generic.TransformComponent):
    """component object that manipulates an ``edge`` component
    """

    # ATTRIBUTES #

    _componentType = cgp_maya_utils.constants.ComponentType.EDGE


class Face(_generic.TransformComponent):
    """component object that manipulates an ``face`` component
    """

    # ATTRIBUTES #

    _componentType = cgp_maya_utils.constants.ComponentType.FACE


class Vertex(_generic.TransformComponent):
    """component object that manipulates an ``vertex`` component
    """

    # ATTRIBUTES #

    _componentType = cgp_maya_utils.constants.ComponentType.VERTEX
