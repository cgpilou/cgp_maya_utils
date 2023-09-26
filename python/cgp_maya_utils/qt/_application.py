"""
maya application object library
"""

# imports third-parties
import maya.mel
import maya.cmds
import PySide2.QtWidgets

# imports rodeo
import cgp_generic_utils.constants
import cgp_generic_utils.python
import cgp_generic_utils.qt

# imports local
import cgp_maya_utils.constants


# MAYA APPLICATION OBJECT #


class MayaApplication(cgp_generic_utils.qt.Application):
    """application object that manipulates a ``maya`` application
    """

    # STATIC COMMANDS #

    @staticmethod
    def createInViewMessage(logType, message, position=None):
        """display the inView message in the maya viewport

        :param logType: type of the inView message - ``[info - warning - error]``
        :type logType: :class:`cgp_generic_utils.constants.LogType`

        :param message: content of the inView message
        :type message: str

        :param position: position of the inView message in the viewport -
                        default is ``cgp_maya_utils.constants.ViewportPosition.BOTTOM_CENTER``
        :type position: :class:`cgp_maya_utils.constants.ViewportPosition`
        """

        # init
        position = position or cgp_maya_utils.constants.ViewportPosition.BOTTOM_CENTER

        # get colors
        colors = {cgp_generic_utils.constants.LogType.INFO:
                  cgp_generic_utils.python.Color(*cgp_generic_utils.constants.StatusColor.VALID).hex(),
                  cgp_generic_utils.constants.LogType.WARNING:
                  cgp_generic_utils.python.Color(*cgp_generic_utils.constants.StatusColor.WARNING).hex(),
                  cgp_generic_utils.constants.LogType.ERROR:
                  cgp_generic_utils.python.Color(*cgp_generic_utils.constants.StatusColor.ERROR).hex()}

        # errors
        if logType not in cgp_generic_utils.constants.LogType.ALL:
            raise ValueError('{0} is not a type ! Specify one : {1}'.format(position,
                                                                            cgp_generic_utils.constants.LogType.ALL))
        if position not in cgp_maya_utils.constants.ViewportPosition.ALL:
            raise ValueError('{0} is not a viewport position ! Specify one : {1}'
                             .format(position, cgp_maya_utils.constants.ViewportPosition.ALL))

        # display inView message
        maya.cmds.inViewMessage(message='  <span style=\"color:{0};\">{1}</span> - {2}  '
                                .format(colors[logType], logType.upper(), message),
                                position=position,
                                dragKill=True)

    # COMMANDS #

    def mainViewport(self):
        """get the main viewport of the maya application

        :return: the main viewport of the maya application
        :rtype: :class:`PySide2.QtWidgets.QWidget`
        """

        # init
        widgetName = maya.mel.eval('global string $gMainPane; $temp = $gMainPane;')

        # return
        return self.widget(widgetName)

    def mainWindow(self):
        """get the main window of the maya application

        :return: the main window of the maya application
        :rtype: :class:`PySide2.QtWidgets.QMainWindow`
        """

        # init
        widgetName = maya.mel.eval('global string $gMainWindow; $temp = $gMainWindow;')

        # return
        return self.widget(widgetName)

    def name(self):
        """get the name of the application

        :return: the name of the application
        :rtype: str
        """

        # return
        return maya.cmds.about(application=True)

    def version(self, asTuple=False):
        """get the version of the maya application

        :param asTuple: ``True`` : the version is queried as a tuple - ``False`` : the version is queried as a string
        :type asTuple: bool

        :return: the version of the application
        :rtype: tuple[int] or str
        """

        # init
        apiVersion = str(maya.cmds.about(apiVersion=True))
        major, minor, patch = int(apiVersion[:4]), int(apiVersion[4:6]), int(apiVersion[6:])

        # return
        return (major, minor, patch) if asTuple else '{}.{}.{}'.format(major, minor, patch)

    def timeline(self):
        """get the timeline of the maya application

        :return: the timeline of the maya application
        :rtype: :class:`PySide2.QtWidgets.QWidget`
        """

        # init
        widgetName = maya.mel.eval("$tmpVar=$gPlayBackSlider").rsplit('|')[-1]

        # return
        return self.widget(widgetName)
