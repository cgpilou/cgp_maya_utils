"""
maya files management functions
"""

# imports third-parties
import cgp_generic_utils.files


# COMMANDS #


def registerFileTypes():
    """register maya file types to grant generic file management functions access to the maya file objects
    """

    # imports file modules
    from ._maya import MayaFile, MaFile, MbFile, ObjFile

    fileTypes = {'mayaFile': MayaFile,
                 'ma': MaFile,
                 'mb': MbFile,
                 'obj': ObjFile}

    # execute
    cgp_generic_utils.files.registerFileTypes(fileTypes)
