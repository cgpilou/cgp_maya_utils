"""
miscellaneous object library
"""

# imports third-parties
import maya.api.OpenMaya
import maya.api.OpenMayaAnim
import maya.cmds
import maya.mel
import PySide2.QtCore
import PySide2.QtWidgets

# imports rodeo
import cgp_generic_utils.files
import cgp_generic_utils.constants

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api


# MISC OBJECTS #


class Namespace(object):
    """namespace object that manipulates a namespace
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.MiscType.NAMESPACE

    # INIT #

    def __init__(self, namespace):
        """Namespace class initialization

        :param namespace: name of the namespace - if namespace is not absolute, it will search in the current namespace
        :type namespace: str
        """

        # init
        currentNamespace = cgp_maya_utils.scene._api.currentNamespace(asAbsolute=True)

        # errors
        if not maya.cmds.namespace(exists=namespace):
            if namespace.startswith(':'):
                raise ValueError('\'{0}\' is not an existing namespace in the root namespace'
                                 .format(namespace, currentNamespace))

            else:
                raise ValueError('\'{0}\' is not an existing namespace in the current namespace \'{1}\''
                                 .format(namespace, currentNamespace))

        # set attribute
        self._fullName = (namespace
                          if namespace.startswith(':')
                          else '{0}:{1}'.format(currentNamespace, namespace))

    def __eq__(self, namespace):
        """check if the Namespace is identical to the other namespace

        :param namespace: namespace to compare to the namespace to
        :type namespace: str or :class:`cgp_maya_utils.scene.Namespace`

        :return: ``True`` : the namespaces are identical - ``False`` : the namespaces are different
        :rtype: bool
        """

        # return
        return self.fullName() == str(namespace)

    def __ne__(self, namespace):
        """check if the Namespace is different to the other namespace

        :param namespace: namespace to compare to the namespace to
        :type namespace: str or :class:`cgp_maya_utils.scene.Namespace`

        :return: ``True`` : the namespaces are different - ``False`` : the namespaces are identical
        :rtype: bool
        """

        # return
        return self.fullName() != str(namespace)

    def __repr__(self):
        """get the representation of the namespace

        :return: the representation of the namespace
        :rtype: str
        """

        # return
        return 'Namespace({0!r})'.format(self.fullName())

    def __str__(self):
        """get the string representation of the namespace

        :return: the string representation of the namespace
        :rtype: str
        """

        # return
        return self.fullName()

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, name):
        """create a namespace

        :param name: name of the namespace to create
        :type name: str

        :return: the created namespace
        :rtype: :class:`cgp_maya_utils.scene.Namespace`
        """

        # create the namespace in the current
        namespace = maya.cmds.namespace(add=name)

        # return
        return cls(namespace)

    # COMMANDS #

    def fullName(self, asAbsolute=True):
        """get the full name of the namespace

        :param asAbsolute: ``True`` : full name is returned asAbsolute - ``False`` full name is returned as relative
        :type asAbsolute: bool

        :return: the full name of the namespace
        :rtype: str
        """

        # return
        return maya.cmds.namespaceInfo(self._fullName, absoluteName=asAbsolute)

    def isCurrent(self):
        """check is the namespace is the current namespace
        """

        # execute
        return self.fullName(asAbsolute=True) == cgp_maya_utils.scene._api.currentNamespace(asAbsolute=True)

    def name(self):
        """get the name of the namespace

        :return: the name of the namespace
        :rtype: str
        """

        # return
        return maya.cmds.namespaceInfo(self._fullName, shortName=True)

    def parent(self):
        """get the parent of the namespace
        """

        # get parent namespace
        namespace = maya.cmds.namespaceInfo(self.fullName(), parent=True, absoluteName=True)

        # return
        return cgp_maya_utils.scene._api.namespace(namespace)

    def setAsCurrent(self):
        """set the namespace as current namespace
        """

        # execute
        maya.cmds.namespace(setNamespace=self.fullName())


class Plugin(object):
    """plugin object that manipulates a maya plugin
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.MiscType.PLUGIN

    # INIT #

    def __init__(self, name):
        """Plugin class initialization

        :param name: name of the plugin
        :type name: str
        """

        # init
        self._name = name

    def __repr__(self):
        """override plugin representation

        :return: the representation of the plugin
        :rtype: str
        """

        # return
        return '{0}({1!r})'.format(self.__class__.__name__, self.name())

    # COMMANDS #

    def file_(self):
        """get the file of the plugin

        :return: the file of the plugin
        :rtype: :class:`cgp_generic_utils.file.File`
        """

        # return
        return cgp_generic_utils.files.entity(str(self.path()))

    def isAutoLoaded(self):
        """check if the plugin is autoLoaded

        :return: ``True`` : the plugin is autoLoaded  - ``False`` : the plugin is not autoLoaded
        :rtype: bool
        """

        # return
        return maya.cmds.pluginInfo(self.name(), query=True, autoload=True)

    def isLoaded(self):
        """check if the plugin is loaded

        :return: ``True`` : the plugin is loaded  - ``False`` : the plugin is not loaded
        :rtype: bool
        """

        # return
        return maya.cmds.pluginInfo(self.name(), query=True, loaded=True)

    def load(self):
        """load the plugin
        """

        # execute
        try:
            if not maya.cmds.pluginInfo(self.name(), query=True, loaded=True):
                maya.cmds.loadPlugin(self.name())

        # error
        except RuntimeError:
            maya.cmds.warning('{0} is not a registered plugin'.format(self.name()))

    def name(self):
        """get the name of the plugin

        :return: the name of the plugin
        :rtype: str
        """

        # return
        return self._name

    def path(self):
        """get the path of the plugin

        :return: the path of the plugin
        :rtype: :class:`cgp_generic_utils.file.Path`
        """

        # get plugin path
        path = maya.cmds.pluginInfo(self.name(), query=True, path=True)

        # return
        return cgp_generic_utils.files.Path(path)

    def unload(self, deleteNodes=False):
        """unload the plugin

        :param deleteNodes: `True`` : plugin nodes are deleted before unload - ``False`` nodes are not deleted
        :type deleteNodes: bool
        """

        # flush undo to avoid ctrl+Z clashes
        maya.cmds.flushUndo()

        # unload plugin
        unloadedPlugin = maya.cmds.unloadPlugin(self.name())

        # delete node if specified
        if deleteNodes and unloadedPlugin:
            maya.cmds.delete(maya.cmds.ls(type=self.name()))

    def version(self):
        """get the version of the plugin

        :return: the version of the plugin
        :rtype: str
        """

        return maya.cmds.pluginInfo(self.name(), query=True, version=True)


class Scene(object):
    """scene object that manipulates a live scene
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.MiscType.SCENE

    # INIT #

    def __repr__(self):
        """get the representation of the scene

        :return: the representation of the scene
        :rtype: str
        """

        # return
        return '{0}()'.format(self.__class__.__name__)

    # STATIC COMMANDS #

    @staticmethod
    def animationStart():
        """get the start of the animation

        :return: the start of the animation
        :rtype: float
        """

        # return
        return maya.cmds.playbackOptions(query=True, animationStartTime=True)

    @staticmethod
    def animationEnd():
        """get the end of the animation

        :return: the end of the animation
        :rtype: float
        """

        # return
        return maya.cmds.playbackOptions(query=True, animationEndTime=True)

    @staticmethod
    def currentTime():
        """get the current time of the animation

        :return: the current time of the animation
        :rtype: float
        """

        # return with OpenMaya (faster than maya.cmds)
        return maya.api.OpenMayaAnim.MAnimControl.currentTime().value

    @staticmethod
    def file_():
        """get the file of the scene

        :return: the current scene file
        :rtype: :class:`cgp_maya_utils.files.MayaFile`
        """

        # get file path
        filePath = maya.cmds.file(query=True, sceneName=True)

        # return
        return cgp_generic_utils.files.entity(filePath) if filePath else None

    @staticmethod
    def mainWindow():
        """get the maya main window

        :return: the main window
        :rtype: :class:`PySide2.QtWidgets.QMainWindow`
        """

        # deprecation warning
        maya.cmds.warning('mainWindow() command from cgp_maya_utils.scene._misc._misc.Scene is deprecated '
                          'use cgp_maya_utils.qt.application().mainWindow() instead.')

        # get maya application
        mayaApplication = PySide2.QtWidgets.QApplication.instance()

        # parse top level widgets until we find the maya main window
        for widget in mayaApplication.topLevelWidgets():

            # QApplication.topLevelWidgets() also lists non QObject objects such as QListWidgetItem
            if not isinstance(widget, PySide2.QtCore.QObject):
                continue

            # if the object name match, we found the correct widget
            if widget.objectName() == cgp_maya_utils.constants.Interface.MAYA_WINDOW:
                return widget

    @staticmethod
    def maximumTime():
        """get the maximum time of the animation

        :return: the maximum time of the animation
        :rtype: float
        """

        # return
        return maya.cmds.playbackOptions(query=True, maxTime=True)

    @staticmethod
    def minimumTime():
        """get the minimum time of the animation

        :return: the minimum time of the animation
        :rtype: float
        """

        # return
        return maya.cmds.playbackOptions(query=True, minTime=True)

    @staticmethod
    def new(force=False):
        """open a new scene

        :param force: ``True`` : new scene opening will be forced - ``False`` : save prompt will show before opening
        :type force: bool
        """

        # execute
        maya.cmds.file(newFile=True, force=force)

    @staticmethod
    def setAnimationStart(value):
        """set the start of the animation

        :param value: value to set as start of animation
        :type value: float or int
        """

        # execute
        maya.cmds.playbackOptions(animationStartTime=value)

    @staticmethod
    def setAnimationEnd(value):
        """set the end of the animation

        :param value: value to set as end of animation
        :type value: float or int
        """

        # execute
        maya.cmds.playbackOptions(animationEndTime=value)

    @staticmethod
    def setCurrentTime(value):
        """set the current time of the animation

        :param value: value used to set the current time
        :type value: float or int
        """

        # we may have faster results using maya.api.OpenMayaAnim.MAnimControl.setCurrentTime
        # but since the cache playback option has been implemented in Maya, this command makes Maya freeze
        # we may disable the cache playback option in a decorator
        # but in order to keep the code simple, we prefer slower but more reliable maya.cmds command
        maya.cmds.currentTime(value)

    @staticmethod
    def setMaximumTime(value):
        """set the maximum time of the animation

        :param value: value used to set the maximum time
        :type value: float or int
        """

        # execute
        maya.cmds.playbackOptions(maxTime=value)

    @staticmethod
    def setMinimumTime(value):
        """set the minimum time of the animation

        :param value: value used to set the minimum time
        :type value: float or int
        """

        # execute
        maya.cmds.playbackOptions(minTime=value)

    @staticmethod
    def timeIncrement():
        """get the time increment of the animation

        :return: the time increment of the animation
        :rtype: float
        """

        # return
        return maya.cmds.playbackOptions(query=True, by=True)

    @staticmethod
    def timeline():
        """get the QWidget of Maya's timeline

        :return: QWidget of Maya's timeline
        :rtype: :class:`PySide2.QtWidgets.QWidget`
        """

        # deprecation warning
        maya.cmds.warning('timeline() command from cgp_maya_utils.scene._misc._misc.Scene is deprecated '
                          'use cgp_maya_utils.qt.application().timeline() instead.')

        # get timeline name
        timelineName = maya.mel.eval('$tmpVar=$gPlayBackSlider').rsplit('|')[-1]

        # get widgets
        widgets = {widget.objectName(): widget for widget in PySide2.QtWidgets.QApplication.allWidgets()}

        # return
        return widgets.get(timelineName)

    @staticmethod
    def viewport():
        """get the viewport of the scene

        :return: the viewport of the scene
        :rtype: str
        """

        # deprecation warning
        maya.cmds.warning('viewport() command from cgp_maya_utils.scene._misc._misc.Scene is deprecated '
                          'use cgp_maya_utils.qt.application().mainViewport().objectName() instead.')

        # return
        return str(maya.mel.eval('global string $gMainPane; $temp = $gMainPane;'))

    # COMMANDS #

    def reopen(self, force=False):
        """reopen the scene file

        :param force: ``True`` : scene reopening will be forced - ``False`` : save prompt will show before reopening
        :type force: bool
        """

        # execute
        maya.cmds.file(self.file_().path(), open=True, force=force)
