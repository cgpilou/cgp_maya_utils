"""
maya file objects and management functions
"""

# import rodeo
import cgp_generic_utils.files

# imports local
from ._maya import AbcFile, GpuCacheFile, MayaFile, MaFile, MbFile, ObjFile


def registerFileTypes():
    """register maya file types to grant generic file management functions access to the maya file objects
    """

    fileTypes = {'abc': AbcFile,
                 'gpucache': GpuCacheFile,
                 'mayaFile': MayaFile,
                 'ma': MaFile,
                 'mb': MbFile,
                 'obj': ObjFile}

    # execute
    cgp_generic_utils.files.registerFileTypes(fileTypes)


__all__ = ['AbcFile', 'GpuCacheFile', 'MayaFile', 'MaFile', 'MbFile', 'ObjFile', 'registerFileTypes']
