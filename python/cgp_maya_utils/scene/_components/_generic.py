"""
generic component object library
"""

# imports python
import re

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api


class Component(object):
    """component object that manipulates any kind of component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.COMPONENT

    # INIT #

    def __init__(self, fullName):
        """Component class initialization

        :param fullName: full name of the component - ``shape.component[*]`` or ``shape.component[*][*]``
        :type fullName: str
        """

        # init
        self._fullName = fullName

    def __eq__(self, component):
        """check if the Component is identical to the other component

        :param component: component to compare the component to
        :type component: str or :class:`cgp_maya_utils.scene.Component`

        :return: ``True`` : components are identical - ``False`` : components are different
        :rtype: bool
        """

        # return
        return self.fullName() == str(component)

    def __ne__(self, component):
        """check if the Component is different from the other component

        :param component: component to compare the component to
        :type component: str or :class:`cgp_maya_utils.scene.Component`

        :return: ``True`` : components are different - ``False`` : components are identical
        :rtype: bool
        """

        # return
        return self.fullName() != str(component)

    def __repr__(self):
        """get the representation of the component

        :return: the representation of the component
        :rtype: str
        """

        # return
        return '{0}(\'{1}\')'.format(self.__class__.__name__, self.fullName())

    def __str__(self):
        """get the string representation of the node

        :return: the string representation of the component
        :rtype: str
        """

        # return
        return self.fullName()

    # COMMANDS #

    def componentType(self):
        """get the type of the component

        :return: the type of the component
        :rtype: str
        """

        # execute
        return self.name().split('[')[0]

    def indexes(self):
        """get the indexes of the component

        :return: the indexes of the component
        :rtype: list[int]
        """

        # return
        return ([int(self.name().split('[')[-1].split(']')[0])]
                if re.match(r'.+\.[a-zA-Z]+\[[0-9]+]$', self.fullName())
                else [int(s) for s in re.findall(r'\d+', self.name())])

    def fullName(self):
        """get the full name of the component

        :return: the full name of the component - ``node.component[*]`` or ``node.component[*][*]``
        :rtype: str
        """

        # return
        return self._fullName

    def name(self):
        """get the name of the component

        :return: the name of the component - ``component[*]`` or ``component[*][*]``
        :rtype: str
        """

        # return
        return self._fullName.split('.')[-1]

    def select(self):
        """select the component
        """

        # allow component selection
        maya.cmds.hilite(self.shape())

        # select the component
        maya.cmds.select(self)

    def shape(self):
        """get the shape of the component

        :return: the shape of the component
        :rtype: :class:`cgp_maya_utils.scene.Shape` or :class:`cgp_maya_utils.scene.Mesh`
        """

        # return
        return cgp_maya_utils.scene._api.node(self._fullName.split('.')[0])


class TransformComponent(Component):
    """component object that manipulates any kind of transform component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.TRANSFORM_COMPONENT

    # INIT #

    def __init__(self, fullName):
        """TransformComponent class initialization

        :param fullName: full name of the transform component - ``shape.component[*]`` or ``shape.component[*][*]`
        :type fullName: str
        """

        # init
        super(TransformComponent, self).__init__(fullName)

    # COMMANDS #

    def position(self, worldSpace=False):
        """get the position of the transform component

        :param worldSpace: ``True`` : position will be queried in worldSpace -
                           ``False`` : position will be queried in local
        :type worldSpace: bool

        :return: the position of the component
        :rtype: list[float]
        """

        # get position
        position = maya.cmds.xform(self.fullName(), query=True, worldSpace=worldSpace, translation=True)

        # sort position
        position = [position[x:x+3] for x in xrange(0, len(position), 3)]

        # return
        return position[0] if len(position) == 1 else position
