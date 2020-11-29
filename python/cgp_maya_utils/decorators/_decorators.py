"""
maya decorators - also usable as contexts
"""

# imports third-parties
import maya.cmds
import maya.mel
import cgp_generic_utils.decorators


class DisableAutoKey(cgp_generic_utils.decorators.Decorator):
    """decorator that disable animation automatic keying and set it back to its original state
    """

    def __init__(self):
        """DisableAutoKey class initialization
        """

        # init
        self._autoKeyStatus = None

    def __enter__(self):
        """enter DisableAutoKey decorator
        """

        # execute
        self._autoKeyStatus = maya.cmds.autoKeyframe(query=True, state=True)
        maya.cmds.autoKeyframe(state=False)

    def __exit__(self, *args, **kwargs):
        """exit DisableAutoKey decorator
        """

        # execute
        maya.cmds.autoKeyframe(state=self._autoKeyStatus)


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

    def __exit__(self, *args, **kwargs):
        """exit DisableViewport decorator
        """

        # execute
        maya.cmds.refresh(suspend=False)
        maya.cmds.paneLayout(self._viewport, edit=True, manage=True)


class KeepCurrentFrame(cgp_generic_utils.decorators.Decorator):
    """decorator that force the current frame to remain the same
    """

    def __init__(self):
        """KeepCurrentFrame class initialization
        """

        # init
        self._currentFrame = None

    def __enter__(self):
        """enter KeepCurrentFrame decorator
        """

        # execute
        self._currentFrame = maya.cmds.currentTime(query=True)

    def __exit__(self, *args, **kwargs):
        """exit KeepCurrentFrame decorator
        """

        # execute
        maya.cmds.currentTime(self._currentFrame)


class KeepCurrentFrameRange(cgp_generic_utils.decorators.Decorator):
    """decorator that force the current frame range to remain the same
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

    def __exit__(self, *args, **kwargs):
        """exit KeepCurrentFrameRange decorator
        """

        # execute
        maya.cmds.playbackOptions(minTime=self._minimumTime)
        maya.cmds.playbackOptions(maxTime=self._maximumTime)
        maya.cmds.playbackOptions(animationStartTime=self._animationStart)
        maya.cmds.playbackOptions(animationEndTime=self._animationEnd)


class KeepCurrentSelection(cgp_generic_utils.decorators.Decorator):
    """decorator that force the current selection to remain the same
    """

    def __init__(self):
        """KeepCurrentSelection class initialization
        """

        # init
        self._selection = None

    def __enter__(self):
        """enter KeepCurrentSelection decorator
        """

        # execute
        self._selection = maya.cmds.ls(selection=True)

    def __exit__(self, *args, **kwargs):
        """exit KeepCurrentSelection decorator
        """

        # execute
        maya.cmds.select(self._selection, replace=True)


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

    def __exit__(self, *args, **kwargs):
        """exit NamespaceContext decorator
        """

        # execute
        maya.cmds.namespace(setNamespace=self._originalNamespace)


class UndoChunk(cgp_generic_utils.decorators.Decorator):
    """decorator that encapsulate the script into its own undo chunk
    """

    def __init__(self, name=None):
        """UndoChunk class initialization

        :param name: name of the undoChunk
        :type name: str
        """

        # init
        self._name = name

    def __enter__(self):
        """enter UndoChunk decorator
        """

        # execute
        maya.cmds.undoInfo(openChunk=True, chunkName=self._name)

    def __exit__(self, *args, **kwargs):
        """exit UndoChunk decorator
        """

        # execute
        maya.cmds.undoInfo(closeChunk=True)
