"""
subclassed Qt objects for UI development
"""

# imports rodeo
import cgp_generic_utils.qt

# imports local
from ._application import MayaApplication


# API #


cgp_generic_utils.qt.registerApplicationType(MayaApplication)


# ALL #


__all__ = ['MayaApplication']
