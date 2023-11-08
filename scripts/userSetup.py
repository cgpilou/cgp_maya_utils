"""
cgp_maya_utils userSetup
"""

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants


# register files
cgp_maya_utils.files.registerFileTypes()

# set preferences
maya.cmds.jointDisplayScale(1.0, a=True)
maya.cmds.displayPref(materialLoadingMode='immediate')
maya.cmds.help(popupMode=True)
maya.cmds.optionVar(intValue=['generateUVTilePreviewsOnSceneLoad', 1])


print('cgp_maya_utils - userSetup.py : loaded')
