"""
maya decorators - also usable as contexts
"""

# imports third-parties
import maya.cmds
import maya.mel

# imports rodeo
import cgp_generic_utils.decorators
import cgp_generic_utils.qt

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.qt


class DisableAutokey(cgp_generic_utils.decorators.Decorator):
    """decorator that disable animation automatic keying and set it back to its original state
    """

    def __init__(self):
        """DisableAutokey class initialization
        """

        # init
        self._autokeyStatus = None

    def __enter__(self):
        """enter DisableAutokey decorator
        """

        # execute
        self._autokeyStatus = maya.cmds.autoKeyframe(query=True, state=True)
        maya.cmds.autoKeyframe(state=False)

    def __exit__(self, *_, **__):
        """exit DisableAutokey decorator
        """

        # execute
        maya.cmds.autoKeyframe(state=self._autokeyStatus)


class DisableIntermediateStatus(cgp_generic_utils.decorators.Decorator):
    """decorator that disable intermediate status of shapes and reactivate it
    """

    # ATTRIBUTES #

    _ATTRIBUTE_NAME_TEMPLATE = "{}.intermediateObject"

    # COMMANDS #

    def __init__(self, shapes=None):
        """DisableIntermediateStatus class initialization

        :param shapes: the node to disable status on - default is all the existing shapes
        :param shapes: list[str] or list[:class:`cgp_maya_utils.scene.Shape`]
        """

        # init
        self._shapes = shapes or maya.cmds.ls(shapes=True, long=True)
        self._intermediateShapes = []

    def __enter__(self):
        """enter DisableIntermediateStatus decorator
        """

        # parse intermediate objects
        self._intermediateShapes = [shape
                                    for shape in self._shapes
                                    if maya.cmds.getAttr(self._ATTRIBUTE_NAME_TEMPLATE.format(shape))]

        # uncheck intermediate option
        for shape in self._intermediateShapes:
            maya.cmds.setAttr(self._ATTRIBUTE_NAME_TEMPLATE.format(shape), False)

    def __exit__(self, *_, **__):
        """exit DisableIntermediateStatus decorator
        """

        # restore intermediate option
        for shape in self._intermediateShapes:
            maya.cmds.setAttr(self._ATTRIBUTE_NAME_TEMPLATE.format(shape), True)


class DisableCycleCheck(cgp_generic_utils.decorators.Decorator):
    """decorator that disable cycleCheck evaluation and set it back to it's original status
    """

    def __init__(self):
        """DisableCycleCheck class initialization
        """

        # init
        self._cycleCheckStatus = maya.cmds.cycleCheck(query=True, evaluation=True)

    def __enter__(self):
        """enter DisableCycleCheck decorator
        """

        # execute
        maya.cmds.cycleCheck(evaluation=False)

    def __exit__(self, *_, **__):
        """exit DisableCycleCheck decorator
        """

        # execute
        maya.cmds.cycleCheck(evaluation=self._cycleCheckStatus)


class DisableExpressions(cgp_generic_utils.decorators.Decorator):
    """decorator that disable expressions and set them back to their original status
    """

    def __init__(self):
        """DisableExpressions class initialization
        """

        # init
        self._data = {}

    def __enter__(self):
        """enter DisableExpressions decorator
        """

        # local import to avoid conflicts
        import cgp_maya_utils.scene._api

        # get all expression nodes
        nodes = cgp_maya_utils.scene._api.getNodes(nodeTypes=[cgp_maya_utils.constants.NodeType.EXPRESSION])

        # store expression state and disable them
        for expressionNode in nodes:
            self._data[expressionNode] = {}

            # store and check 'frozen' attribute
            attribute = expressionNode.attribute("frozen")
            self._data[expressionNode][attribute] = attribute.value()
            attribute.setValue(True)

            # store and set 'nodeState' attribute to 'HasNoEffect'
            attribute = expressionNode.attribute("nodeState")
            self._data[expressionNode][attribute] = attribute.value()
            attribute.setValue(cgp_maya_utils.constants.NodeState.HAS_NO_EFFECT)

    def __exit__(self, *_, **__):
        """exit DisableExpressions decorator
        """

        # restore expression state
        for expressionNode, attributeData in self._data.items():
            for attribute, attributeValue in attributeData.items():
                attribute.setValue(attributeValue)


class DisableViewport(cgp_generic_utils.decorators.Decorator):
    """decorator that disable viewport drawing and reactivate it
    """

    def __init__(self):
        """DisableViewport class initialization
        """

        # init
        self._viewport = str(maya.mel.eval('global string $gMainPane; $temp = $gMainPane;'))

    def __enter__(self):
        """enter DisableViewport decorator
        """

        # execute
        maya.cmds.refresh(suspend=True)
        maya.cmds.paneLayout(self._viewport, edit=True, manage=False)

    def __exit__(self, *_, **__):
        """exit DisableViewport decorator
        """

        # execute
        maya.cmds.refresh(suspend=False)
        maya.cmds.paneLayout(self._viewport, edit=True, manage=True)


class KeepCurrentAnimationLayer(cgp_generic_utils.decorators.Decorator):
    """decorator that forces to keep the currently selected animation layer
    """

    def __init__(self):
        """KeepCurrentAnimationLayer class initialization
        """

        # init
        self._activeLayer = None

    def __enter__(self):
        """enter KeepCurrentAnimationLayer decorator
        """

        # local import to avoid conflicts
        import cgp_maya_utils.scene._api

        # search for active layer and store it
        activeLayers = cgp_maya_utils.scene._api._MISC_TYPES['animLayer']._getAnimLayerNodeNames(onlyActive=True)
        if activeLayers:
            self._activeLayer = cgp_maya_utils.scene._api.animLayer(activeLayers[0])
        else:
            self._activeLayer = cgp_maya_utils.scene._api.animLayer(None)

    def __exit__(self, *_, **__):
        """exit KeepCurrentAnimationLayer decorator
        """

        # restore active layer
        if self._activeLayer and not self._activeLayer.isActive():
            self._activeLayer.setActive()


class KeepCurrentFrame(cgp_generic_utils.decorators.Decorator):
    """decorator that forces to keep the currently selected frame
    """

    def __init__(self):
        """KeepCurrentFrame class initialization
        """

        # local import to avoid conflicts
        import cgp_maya_utils.scene._api

        # init
        self._scene = cgp_maya_utils.scene._api.scene()
        self._currentFrame = None

    def __enter__(self):
        """enter KeepCurrentFrame decorator
        """

        # execute
        self._currentFrame = self._scene.currentTime()

    def __exit__(self, *_, **__):
        """exit KeepCurrentFrame decorator
        """

        # execute
        self._scene.setCurrentTime(self._currentFrame)


class KeepCurrentFrameRange(cgp_generic_utils.decorators.Decorator):
    """decorator that forces to keep the currently specified frame range
    """

    def __init__(self):
        """KeepCurrentFrameRange class initialization
        """

        # init
        self._minimumTime = None
        self._maximumTime = None
        self._animationStart = None
        self._animationEnd = None

    def __enter__(self):
        """enter KeepCurrentFrameRange decorator
        """

        # store frameRange values
        self._minimumTime = maya.cmds.playbackOptions(query=True, minTime=True)
        self._maximumTime = maya.cmds.playbackOptions(query=True, maxTime=True)
        self._animationStart = maya.cmds.playbackOptions(query=True, animationStartTime=True)
        self._animationEnd = maya.cmds.playbackOptions(query=True, animationEndTime=True)

    def __exit__(self, *_, **__):
        """exit KeepCurrentFrameRange decorator
        """

        # execute
        maya.cmds.playbackOptions(minTime=self._minimumTime)
        maya.cmds.playbackOptions(maxTime=self._maximumTime)
        maya.cmds.playbackOptions(animationStartTime=self._animationStart)
        maya.cmds.playbackOptions(animationEndTime=self._animationEnd)


class KeepOptionVars(cgp_generic_utils.decorators.Decorator):
    """decorator that forces to keep the currently specified optionVars
    """

    def __init__(self):
        """KeepCurrentOptionVars class initialization
        """

        # init
        self._options = {}

    def __enter__(self):
        """enter KeepCurrentOptionVars decorator
        """

        # local import to avoid conflicts
        import cgp_maya_utils.scene

        # backup the values
        self._options = {optionVar: optionVar.value()
                         for optionVar in cgp_maya_utils.scene.getOptionVars()
                         if type(optionVar) != cgp_maya_utils.scene.OptionVar}  # bypass read only vars

    def __exit__(self, *_, **__):
        """exit KeepCurrentOptionVars decorator
        """

        # restore the values
        for optionVar, optionValue in self._options.items():
            optionVar.setValue(optionValue)


class KeepSelection(cgp_generic_utils.decorators.Decorator):
    """decorator that forces to keep the current selection
    """

    def __init__(self):
        """KeepSelection class initialization
        """

        # init
        self._selection = None

    def __enter__(self):
        """enter KeepSelection decorator
        """

        # execute
        self._selection = maya.cmds.ls(selection=True)

    def __exit__(self, *_, **__):
        """exit KeepSelection decorator
        """

        # execute
        maya.cmds.select(self._selection, replace=True)


class LoadPlugin(cgp_generic_utils.decorators.Decorator):
    """decorator that will load the plugin and restore its initial state if specified
    """

    def __init__(self, name, restoreInitialState=False):
        """LoadPlugin class initialization

        :param name: name of the plugin
        :type name: str

        :param restoreInitialState: ``True`` : the initial state will be restored -
                                    ``False`` : the initial state won't be restored
        :type restoreInitialState: bool
        """

        # init
        import cgp_maya_utils.scene
        self._plugin = cgp_maya_utils.scene.Plugin(name)
        self._restoreInitialState = restoreInitialState
        self._isInitiallyLoaded = self._plugin.isLoaded()

    def __enter__(self):
        """enter LoadPlugin decorator
        """

        # load if not already
        if not self._isInitiallyLoaded:
            self._plugin.load()

    def __exit__(self, *_, **__):
        """exit LoadPlugin decorator
        """

        # unload the loaded plugin if needed
        if self._restoreInitialState and not self._isInitiallyLoaded:
            self._plugin.unload()


class NamespaceContext(cgp_generic_utils.decorators.Decorator):
    """decorator that force the script to be executed in the context of a namespace
    and set the current namespace back to the previous one
    """

    def __init__(self, contextNamespace=':'):
        """NamespaceContext class initialization

        :param contextNamespace: context nameSpace the decorator will go in to execute the decorated command
        :type contextNamespace: str or :class:`cgp_maya_utils.scene.Namespace`
        """

        # init
        self._contextNamespace = str(contextNamespace)
        self._originalNamespace = maya.cmds.namespaceInfo(currentNamespace=True, absoluteName=True)

    def __enter__(self):
        """enter NamespaceContext decorator
        """

        # execute
        maya.cmds.namespace(setNamespace=self._contextNamespace)

    def __exit__(self, *_, **__):
        """exit NamespaceContext decorator
        """

        # execute
        maya.cmds.namespace(setNamespace=self._originalNamespace)


class UndoChunk(cgp_generic_utils.decorators.Decorator):
    """decorator that encapsulate the script into its own undo chunk
    """

    def __init__(self, name=None, isUndoing=False, isPrompting=False, promptMessage=None):
        """UndoChunk class initialization

        :param name: name of the undoChunk
        :type name: str

        :param isUndoing: ``True`` : actions are undone if error occurred - ``False`` : actions are not undone
        :type isUndoing: bool

        :param isPrompting: ``True`` : a dialog is prompted - ``False`` : no dialog is prompted
        :type isPrompting: bool

        :param promptMessage: A custom message displayed by the dialog
        :type promptMessage: str
        """

        # init
        self._name = name
        self._isUndoing = isUndoing
        self._isPrompting = isPrompting
        self._promptMessage = promptMessage

    def __enter__(self):
        """enter UndoChunk decorator
        """

        # execute
        maya.cmds.undoInfo(openChunk=True, chunkName=self._name)

    def __exit__(self, exceptionType, *_, **__):
        """exit UndoChunk decorator

        :param exceptionType: type of exception if an exception was raised
        :type exceptionType: Exception
        """

        # close chunk
        maya.cmds.undoInfo(closeChunk=True)

        # return
        if exceptionType is None:
            return

        # prompt dialog if specified and maya is not in batch mode
        if self._isPrompting and not maya.cmds.about(batch=True):

            # get maya main window
            mayaMainWindow = cgp_maya_utils.qt.MayaApplication().mainWindow()

            # prompt undoing dialog
            if self._isUndoing:

                # create dialog
                promptMessage = self._promptMessage or 'An error has occurred. Do you want to undo the changes ?'
                dialog = cgp_generic_utils.qt.BaseDialog('Undo', promptMessage, isFrameless=True, parent=mayaMainWindow)

                # return
                if not dialog.load():
                    return

            # prompt no undoing dialog
            else:

                # create dialog
                promptMessage = self._promptMessage or 'An error has occurred. see script editor.'
                dialog = cgp_generic_utils.qt.BaseDialog('Error', promptMessage, isFrameless=True, parent=mayaMainWindow)
                dialog.setButtonDisplayed(isCancelDisplayed=False)

                # load dialog
                dialog.load()

                # return
                return

        # undo
        if self._isUndoing:

            try:
                maya.cmds.undo()
            except RuntimeError:
                pass
