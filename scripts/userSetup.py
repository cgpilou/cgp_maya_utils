"""
cgp_maya_utils userSetup
"""

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.files
import cgp_maya_utils.scene
import cgp_maya_utils.constants


# register files
cgp_maya_utils.files.registerFileTypes()

# get env
env = cgp_maya_utils.constants.Environment.__dict__

# rodeo plugins
for key in env:
    if key.endswith('_PLUGIN') and env.get(key.replace('_PLUGIN', '_AUTOLOAD'), False):
        maya.cmds.evalDeferred("cgp_maya_utils.scene.Plugin(\'{0}\').load()".format(env.get(key)))

# set preferences
maya.cmds.jointDisplayScale(1.0, a=True)
maya.cmds.displayPref(materialLoadingMode='immediate')
maya.cmds.help(popupMode=True)
maya.cmds.optionVar(intValue=['generateUVTilePreviewsOnSceneLoad', 1])


print 'cgp_maya_utils - userSetup.py : loaded'
