"""
nurbsCurve component object library
"""

# imports local
import cgp_maya_utils.constants
from . import _generic


class CurvePoint(_generic.TransformComponent):
    """component object that manipulates a ``curvePoint`` component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.CURVE_POINT


class EditPoint(_generic.TransformComponent):
    """component object that manipulates an ``editPoint`` component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.EDIT_POINT
