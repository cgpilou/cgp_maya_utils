"""
miscellaneous object library
"""

# imports third-parties
import maya.cmds
import maya.mel
import PySide2.QtWidgets
import cgp_generic_utils.files
import cgp_generic_utils.constants

# imports local
import cgp_maya_utils.scene._api
import cgp_maya_utils.decorators


# MISC OBJECTS #


class Namespace(object):
    """namespace object that manipulates a namespace
    """

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
        """check if the Namespace has the same name as the other namespace

        :param namespace: namespace to check the name with
        :type namespace: Namespace / str

        :return: True if the names are identical, False otherwise
        :rtype: bool
        """

        # return
        return self.fullName() == str(namespace)

    def __ne__(self, namespace):
        """check if the Namespace has not the same name as the other namespace

        :param namespace: namespace to check the name with
        :type namespace: Namespace / str

        :return: True if the names are different, False otherwise
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
        return 'Namespace(\'{0}\')'.format(self.fullName())

    def __str__(self):
        """get the print of the namespace

        :return: the print of the namespace
        :rtype: str
        """

        # return
        return self.fullName(asAbsolute=True)

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
        """the full name of the namespace

        :param asAbsolute: ``True`` : full name is returned asAbsolute - ``False`` full name is returned as relative
        :type asAbsolute: bool

        :return: the full name of the namespace
        :rtype: str
        """

        # return
        return (maya.cmds.namespaceInfo(self._fullName, absoluteName=True)
                if asAbsolute
                else maya.cmds.namespaceInfo(self._fullName, fullName=True))

    def isCurrent(self):
        """check is the namespace is the current namespace
        """

        # execute
        return self.fullName(asAbsolute=True) == cgp_maya_utils.scene._api.currentNamespace(asAbsolute=True)

    def name(self):
        """the name of the namespace

        :return: the name of the namespace
        :rtype: str
        """

        # return
        return maya.cmds.namespaceInfo(self._fullName, shortName=True)

    def parent(self):
        """the parent namespace of the namespace
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
        return '{0}(\'{1}\')'.format(self.__class__.__name__, self.name())

    # COMMANDS #

    def file_(self):
        """the plugin file

        :return: the plugin file
        :rtype: :class:`cgp_generic_utils.files.File`
        """

        # get plugin path
        path = maya.cmds.pluginInfo(self.name(), query=True, path=True)

        # return
        return cgp_generic_utils.files.entity(path)

    def isAutoLoaded(self):
        """check if the plugin is autoLoaded

        :return: ``True`` : it is autoLoaded  - ``False`` : it is not autoLoaded
        :rtype: bool
        """

        # return
        return maya.cmds.pluginInfo(self.name(), query=True, autoload=True)

    def isLoaded(self):
        """check if the plugin is loaded

        :return: ``True`` : it is loaded  - ``False`` : it is not loaded
        :rtype: bool
        """

        # return
        return maya.cmds.pluginInfo(self.name(), query=True, loaded=True)

    def load(self):
        """load the plugin if it is not already loaded
        """

        # execute
        try:
            if not maya.cmds.pluginInfo(self.name(), query=True, loaded=True):
                maya.cmds.loadPlugin(self.name())
        except RuntimeError:
            maya.cmds.warning('{0} is not a registered plugin'.format(self.name()))

    def name(self):
        """the name of the plugin

        :return: the name of the plugin
        :rtype: str
        """

        # return
        return self._name

    def unload(self, deleteNodes=False):
        """unload the plugin

        :param deleteNodes: ``True`` : plugin nodes are deleted before unload - ``False`` nodes are not deleted
        :type deleteNodes: bool
        """

        # flush undo to avoid ctrl+Z clashes
        maya.cmds.flushUndo()

        # unload plugin
        unloadedPlugin = maya.cmds.unloadPlugin(self.name)

        # delete node if specified
        if deleteNodes and unloadedPlugin:
            maya.cmds.delete(maya.cmds.ls(type=self.name))


class Scene(object):
    """scene object that manipulates a live scene
    """

    # INIT #

    def __repr__(self):
        """the representation of the scene object

        :return: the representation of the scene object
        :rtype: str
        """

        # return
        return '{0}()'.format(self.__class__.__name__)

    # STATIC COMMANDS #

    @staticmethod
    def animationStart():
        """the start of the animation

        :return: the start of the animation
        :rtype: float
        """

        # return
        return maya.cmds.playbackOptions(query=True, animationStartTime=True)

    @staticmethod
    def animationEnd():
        """the end of the animation

        :return: the end of the animation
        :rtype: float
        """

        # return
        return maya.cmds.playbackOptions(query=True, animationEndTime=True)

    @staticmethod
    def currentTime():
        """the current time of the animation

        :return: the current time of the animation
        :rtype: float
        """

        # return
        return maya.cmds.currentTime(query=True)

    @staticmethod
    def file_():
        """get the file of the scene

        :return: the file of the scene
        :rtype: :class:`cgp_generic_utils.files.File`
        """

        # get the path
        path = maya.cmds.file(query=True, sceneName=True) or None

        # return
        return cgp_generic_utils.files.entity(path) if path else None

    @staticmethod
    def mainWindow():
        """get the maya main window

        :return: the main window
        :rtype: :class:`PySide2.QtWidgets.QMainWindow`
        """

        # get maya application
        mayaApplication = PySide2.QtWidgets.QApplication.instance()

        # return
        for widget in mayaApplication.topLevelWidgets():
            if widget.objectName() == 'MayaWindow':
                return widget

    @staticmethod
    def maximumTime():
        """the maximum time of the animation

        :return: the maximum time of the animation
        :rtype: float
        """

        # return
        return maya.cmds.playbackOptions(query=True, maxTime=True)

    @staticmethod
    def minimumTime():
        """the minimum time of the animation

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

        :param value: value used to set the animationStart
        :type value: float or int
        """

        # execute
        maya.cmds.playbackOptions(animationStartTime=value)

    @staticmethod
    def setAnimationEnd(value):
        """set the end of the animation

        :param value: value used to set the animationEnd
        :type value: float or int
        """

        # execute
        maya.cmds.playbackOptions(animationEndTime=value)

    @staticmethod
    def setCurrentTime(value):
        """set the currentTime of the animation

        :param value: value used to set the currentTime
        :type value: float or int
        """

        # execute
        maya.cmds.currentTime(value)

    @staticmethod
    def setMaximumTime(value):
        """set the maximumTime of the animation

        :param value: value used to set the maximumTime
        :type value: float or int
        """

        # execute
        maya.cmds.playbackOptions(maxTime=value)

    @staticmethod
    def setMinimumTime(value):
        """set the minimumTime of the animation

        :param value: value used to set the minimumTime
        :type value: float or int
        """

        # execute
        maya.cmds.playbackOptions(minTime=value)

    @staticmethod
    def viewport():
        """the viewport of the scene

        :return: the viewport of the scene
        :rtype: str
        """

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
