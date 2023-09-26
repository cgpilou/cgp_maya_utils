"""
constraint object library
"""

# imports third-parties
import maya.cmds
import maya.api.OpenMaya

# imports rodeo
import cgp_generic_utils.python
import cgp_generic_utils.constants

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api
from . import _generic


# BASE OBJECT #


class Constraint(_generic.DagNode):
    """node object that manipulates any kind of constraint node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.CONSTRAINT

    # PROPERTIES #

    @property
    def inputs(self):
        """get the input attributes of the constraint that are connected to the drivers of the constraint
        Those attributes ares scanned to get the driver nodes through connection

        :return: the input attributes connected to the driver transforms
        :rtype: list[str]
        """

        # execute
        return []

    @property
    def outputs(self):
        """get the output attributes of the constraint that are connected to the driven of the constraint
        Those attributes ares scanned to get the driven nodes through connection

        :return: the output attributes connected to the driven transform
        :rtype: list[str]
        """

        # execute
        return []

    # COMMANDS #

    def data(self):
        """get data necessary to store the constraint node on disk and/or recreate it from scratch

        :return: the data of the constraint
        :rtype: dict
        """

        # init
        data = super(Constraint, self).data()
        driven = self.driven()

        # update data
        data['drivers'] = [xform.fullName() for xform in self.drivers()]
        data['driven'] = driven.fullName() if driven else None
        data['drivenAttributes'] = [attr.name() for attr in self.drivenAttributes()]

        # return
        return data

    def driven(self):
        """get the transform that is driven by the constraint

        :return: the driven transform of the constraint
        :rtype: :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`
        """

        # init
        data = []

        #  execute
        for output in self.outputs:
            connectedNodes = maya.cmds.listConnections('{0}.{1}'.format(self.fullName(), output),
                                                       source=False,
                                                       destination=True) or []
            data.extend(connectedNodes)

        # return
        return cgp_maya_utils.scene._api.node(data[0]) if data else None

    def drivenAttributes(self):
        """get the attributes of the driven transform that are driven by the constraint

        :return: the driven attributes of the driven transform
        :rtype: list[Attribute]
        """

        # init
        data = []

        # get driven data
        for output in self.outputs:

            # get connections
            connections = maya.cmds.listConnections('{0}.{1}'.format(self.fullName(), output),
                                                    source=False,
                                                    destination=True,
                                                    plugs=True) or []

            # update data
            for con in connections:
                if con not in data:
                    data.append(con)

        # return
        return [cgp_maya_utils.scene._api.attribute(con) for con in data]

    def drivers(self):
        """get the transforms that drive the constraint

        :return: the driver transforms of the constraint
        :rtype: list[:class:`cgp_maya_utils.scene.Transform`, :class:`cgp_maya_utils.scene.Joint`]
        """

        # init
        data = []

        #  execute
        for inp in self.inputs:

            # get full attribute
            fullAttribute = '{0}.{1}'.format(self.fullName(), inp)

            # update
            try:
                # get connected nodes
                connectedNodes = maya.cmds.listConnections(fullAttribute, source=True, destination=False) or []

                if '*' in fullAttribute:
                    for index in range(len(connectedNodes)):
                        connections = maya.cmds.listConnections(fullAttribute.replace('*', str(index)),
                                                                source=True,
                                                                destination=False) or []
                        connections = [item for item in connections if item not in data]
                        data.extend(connections)
                else:
                    connections = [connectedNode for connectedNode in connectedNodes if connectedNode not in data]
                    data.extend(connections)

            # errors
            except ValueError:
                maya.cmds.warning('can\'t get connections from {0}'.format(fullAttribute))

        # return
        return [cgp_maya_utils.scene._api.node(item) for item in data]

    def isValid(self):
        """check is the constraint is valid by verifying if it has driver and driven transforms connected

        :return: ``True`` : the constraint is valid - ``False`` : the constraint is invalid
        :rtype: bool
        """

        # return
        return self.drivers() and self.driven()

    # PRIVATE COMMANDS #

    @staticmethod
    def _formatDrivenAttributes(driven, drivenAttributes=None):
        """format the driven attributes

        :param driven: name of the object that will be driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Node`

        :param drivenAttributes: the driven attributes to format
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :return: the formated drivenAttributes
        :rtype: list[str]
        """

        # init
        data = []
        drivenAttributes = drivenAttributes or cgp_maya_utils.constants.Transform.ALL

        # errors
        for attr in drivenAttributes:
            if attr not in cgp_maya_utils.constants.Transform.ALL:
                maya.cmds.warning('{0} is not a valid driven attribute - {1}'
                                  .format(attr, cgp_maya_utils.constants.Transform.ALL))

        # execute
        for attr in drivenAttributes:
            if attr in cgp_maya_utils.constants.Transform.GENERAL:
                for axe in cgp_generic_utils.constants.Axe.ALL:
                    data.append('{0}{1}'.format(attr[0].lower(), axe))
            else:
                data.append('{0}{1}'.format(attr[0].lower(), attr[-1].lower()))

        # return
        return [attr for attr in set(data) if not maya.cmds.getAttr('{0}.{1}'.format(driven, attr), lock=True)]


# CONSTRAINT OBJECTS #


class AimConstraint(Constraint):
    """node object that manipulates an ``aim`` constraint node
    """

    # ATTRIBUTES #

    _SUB_TYPE = cgp_generic_utils.constants.RigSubType.AIM
    _TYPE = cgp_maya_utils.constants.NodeType.AIM_CONSTRAINT

    # PROPERTIES #

    @property
    def inputs(self):
        """get the input attributes of the constraint that are connected to the drivers of the constraint
        Those attributes ares scanned to get the driver nodes through connection

        :return: the input attributes connected to the driver transforms
        :rtype: list[str]
        """

        # return
        return ['target[*].targetParentMatrix']

    @property
    def outputs(self):
        """the output attributes of the constraint that are connected to the driven of the constraint
        Those attributes ares scanned to get the driven nodes through connection

        :return: the output attributes connected to the driven transform
        :rtype: list[str]
        """

        # return
        return ['constraintRotate', 'constraintRotateX', 'constraintRotateY', 'constraintRotateZ']

    # COMMANDS #

    @classmethod
    def create(cls,
               drivers,
               driven,
               drivenAttributes=None,
               aimVector=None,
               upVector=None,
               worldUpType=None,
               worldUpVector=None,
               worldUpObject=None,
               maintainOffset=False,
               attributeValues=None,
               name=None,
               **__):
        """create an aimConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str, :class:`cgp_maya_utils.scene.Node`, :class:`cgp_maya_utils.scene.Joint`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Node` or :class:`cgp_maya_utils.scene.Joint`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param aimVector: aim vector of the constraint
        :type aimVector: list[float]

        :param upVector: up vector of the constraint
        :type upVector: list[float]

        :param worldUpType: world up type of the constraint
        :type worldUpType: :class:`cgp_maya_utils.constants.WorldUpType`

        :param worldUpVector: world up vector of the constraint
        :type worldUpVector: list[float]

        :param worldUpObject: world up object of the constraint - If specified, worldUp vector will be ignored
        :type worldUpObject: str or :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`

        :param maintainOffset: ``True`` : the constraint is created with offset -
                               ``False`` : the constraint is created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the created constraint
        :type attributeValues: dict

        :param name: name of the created constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.AimConstraint`
        """

        # errors
        if not drivers or not driven:
            maya.cmds.warning('no drivers and/or driven specified - drivers : {0} - driven : {1}'
                              .format(drivers, driven))
            return

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be aimConstraint'.format(driven))

        # get name
        name = name or 'aimConstraint'

        # get skip attributes
        skip = []

        for axe in cgp_generic_utils.constants.Axe.ALL:
            if 'r{0}'.format(axe) not in drivenAttributes:
                skip.append(axe)

        # get info
        data = {'aimVector': aimVector or [1, 0, 0],
                'upVector': upVector or [0, 1, 0],
                'worldUpType': worldUpType or cgp_maya_utils.constants.WorldUpType.VECTOR}

        if worldUpObject:
            data['worldUpObject'] = str(worldUpObject)
        else:
            data['worldUpVector'] = worldUpVector or [0, 1, 0]

        # execute
        node = maya.cmds.aimConstraint(drivers,
                                       driven,
                                       name=name,
                                       maintainOffset=maintainOffset,
                                       skip=skip,
                                       **data)[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject

    def data(self):
        """get the data necessary to store the aimConstraint node on disk and/or recreate it from scratch

        :return: the data of the constraint
        :rtype: dict
        """

        # init
        data = super(AimConstraint, self).data()

        # update data
        data['aimVector'] = self.attribute('aimVector').value()
        data['upVector'] = self.attribute('upVector').value()
        data['worldUpVector'] = self.attribute('worldUpVector').value()
        data['worldUpObject'] = self.worldUpObject().fullName()

        worldUpType = self.attribute('worldUpType').value(asString=False)
        data['worldUpType'] = cgp_maya_utils.constants.WorldUpType.ALL[worldUpType]

        # return
        return data

    def worldUpObject(self):
        """get the worldUp object of the constraint

        :return: the worldUp object
        :rtype: :class:`cgp_maya_utils.scene.Transform`
        """

        # get connections
        connections = self.attribute('worldUpMatrix').connections(source=True, destinations=False)

        # return
        return connections[0].source().node() if connections else None


class OrientConstraint(Constraint):
    """node object that manipulates an ``orient`` constraint node
    """

    # ATTRIBUTES #

    _SUB_TYPE = cgp_generic_utils.constants.RigSubType.ORIENT
    _TYPE = cgp_maya_utils.constants.NodeType.ORIENT_CONSTRAINT

    # PROPERTIES #

    @property
    def inputs(self):
        """get the input attributes of the constraint that are connected to the drivers of the constraint
        Those attributes ares scanned to get the driver nodes through connection

        :return: the input attributes connected to the driver transforms
        :rtype: list[str]
        """

        # return
        return ['target[*].targetRotate']

    @property
    def outputs(self):
        """the output attributes of the constraint that are connected to the driven of the constraint
        Those attributes ares scanned to get the driven nodes through connection

        :return: the output attributes connected to the driven transform
        :rtype: list[str]
        """

        # return
        return ['constraintRotate', 'constraintRotateX', 'constraintRotateY', 'constraintRotateZ']

    # COMMANDS #

    @classmethod
    def create(cls,
               drivers,
               driven,
               drivenAttributes=None,
               maintainOffset=False,
               attributeValues=None,
               name=None,
               **__):
        """create an orientConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str] or list[:class:`cgp_maya_utils.scene.Transform`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Transform`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint created with offset - ``False`` : constraint created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the created constraint
        :type attributeValues: dict

        :param name: name of the created constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.OrientConstraint`
        """

        # errors
        if not drivers or not driven:
            maya.cmds.warning('no drivers and/or driven specified - drivers : {0} - driven : {1}'
                              .format(drivers, driven))
            return

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be orientConstraint'.format(driven))

        # get name
        name = name or 'orientConstraint'

        # get skip attributes
        skip = []

        for axe in ['x', 'y', 'z']:
            if 'r{0}'.format(axe) not in drivenAttributes:
                skip.append(axe)

        # execute
        node = maya.cmds.orientConstraint(drivers,
                                          driven,
                                          name=name,
                                          maintainOffset=maintainOffset,
                                          skip=skip)[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject


class ParentConstraint(Constraint):
    """node object that manipulates a ``parent`` constraint node
    """

    # ATTRIBUTES #

    _SUB_TYPE = cgp_generic_utils.constants.RigSubType.PARENT
    _TYPE = cgp_maya_utils.constants.NodeType.PARENT_CONSTRAINT

    # PROPERTIES #

    @property
    def inputs(self):
        """get the input attributes of the constraint that are connected to the drivers of the constraint
        Those attributes ares scanned to get the driver nodes through connection

        :return: the input attributes connected to the driver transforms
        :rtype: list[str]
        """

        # return
        return ['target[*].targetParentMatrix']

    @property
    def outputs(self):
        """the output attributes of the constraint that are connected to the driven of the constraint
        Those attributes ares scanned to get the driven nodes through connection

        :return: the output attributes connected to the driven transform
        :rtype: list[str]
        """

        # return
        return ['constraintTranslate', 'constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ',
                'constraintRotate', 'constraintRotateX', 'constraintRotateY', 'constraintRotateZ']

    # COMMANDS #

    @classmethod
    def create(cls,
               drivers,
               driven,
               drivenAttributes=None,
               maintainOffset=False,
               attributeValues=None,
               name=None,
               **__):
        """create a parentConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str or :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint is created with offset -
                               ``False`` : constraint is created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the created constraint
        :type attributeValues: dict

        :param name: name of the created constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.ParentConstraint`
        """

        # errors
        if not drivers or not driven:
            maya.cmds.warning('no drivers and/or driven specified - drivers : {0} - driven : {1}'
                              .format(drivers, driven))
            return

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be parentConstraint'.format(driven))

        # get name
        name = name or 'parentConstraint'

        # get skip attributes
        skip = {'t': [], 'r': []}

        for key in skip:
            for axe in ['x', 'y', 'z']:
                if '{0}{1}'.format(key, axe) not in drivenAttributes:
                    skip[key].append(axe)

        # execute
        node = maya.cmds.parentConstraint(drivers,
                                          driven,
                                          name=name,
                                          maintainOffset=maintainOffset,
                                          skipTranslate=skip['t'],
                                          skipRotate=skip['r'])[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject


class PointConstraint(Constraint):
    """node object that manipulates a ``point`` constraint node
    """

    # ATTRIBUTES #

    _SUB_TYPE = cgp_generic_utils.constants.RigSubType.POINT
    _TYPE = cgp_maya_utils.constants.NodeType.POINT_CONSTRAINT

    # PROPERTIES #

    @property
    def inputs(self):
        """get the input attributes of the constraint that are connected to the drivers of the constraint
        Those attributes ares scanned to get the driver nodes through connection

        :return: the input attributes connected to the driver transforms
        :rtype: list[str]
        """

        # return
        return ['target[*].targetTranslate']

    @property
    def outputs(self):
        """get the output attributes of the constraint that are connected to the driven of the constraint
        Those attributes ares scanned to get the driven nodes through connection

        :return: the output attributes connected to the driven transform
        :rtype: list[str]
        """

        # return
        return ['constraintTranslate', 'constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ']

    # COMMANDS #

    @classmethod
    def create(cls,
               drivers,
               driven,
               drivenAttributes=None,
               maintainOffset=False,
               attributeValues=None,
               name=None,
               **__):
        """create a pointConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str or :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint is created with offset -
                               ``False`` : constraint is created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the created constraint
        :type attributeValues: dict

        :param name: name of the created constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.PointConstraint`
        """

        # errors
        if not drivers or not driven:
            maya.cmds.warning('no drivers and/or driven specified - drivers : {0} - driven : {1}'
                              .format(drivers, driven))
            return

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be aimConstraint'.format(driven))

        # get name
        name = name or 'aimConstraint'

        # get skip attributes
        skip = []

        for axe in ['x', 'y', 'z']:
            if 't{0}'.format(axe) not in drivenAttributes:
                skip.append(axe)

        # execute
        node = maya.cmds.pointConstraint(drivers,
                                         driven,
                                         name=name,
                                         maintainOffset=maintainOffset,
                                         skip=skip)[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject


class ScaleConstraint(Constraint):
    """node object that manipulates a ``scale`` constraint node
    """

    # ATTRIBUTES #

    _SUB_TYPE = cgp_generic_utils.constants.RigSubType.SCALE
    _TYPE = cgp_maya_utils.constants.NodeType.SCALE_CONSTRAINT

    # PROPERTIES #

    @property
    def inputs(self):
        """get the input attributes of the constraint that are connected to the drivers of the constraint
        Those attributes ares scanned to get the driver nodes through connection

        :return: the input attributes connected to the driver transforms
        :rtype: list[str]
        """

        # return
        return ['target[*].targetScale']

    @property
    def outputs(self):
        """get the output attributes of the constraint that are connected to the driven of the constraint
        Those attributes ares scanned to get the driven nodes through connection

        :return: the output attributes connected to the driven transform
        :rtype: list[str]
        """

        # return
        return ['constraintScale', 'constraintScaleX', 'constraintScaleY', 'constraintScaleZ']

    # COMMANDS #

    @classmethod
    def create(cls,
               drivers,
               driven,
               drivenAttributes=None,
               maintainOffset=False,
               attributeValues=None,
               name=None,
               **__):
        """create a scaleConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str or :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint is created with offset -
                               ``False`` : constraint is created without offset
        :type maintainOffset: bool
        :param attributeValues: attribute values to set on the created constraint
        :type attributeValues: dict

        :param name: name of the created constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.ScaleConstraint`
        """

        # errors
        if not drivers or not driven:
            maya.cmds.warning('no drivers and/or driven specified - drivers : {0} - driven : {1}'
                              .format(drivers, driven))
            return

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be scaleConstraint'.format(driven))

        # get name
        name = name or 'scaleConstraint'

        # get skip attributes
        skip = []

        for axe in ['x', 'y', 'z']:
            if 's{0}'.format(axe) not in drivenAttributes:
                skip.append(axe)

        # execute
        node = maya.cmds.scaleConstraint(drivers,
                                         driven,
                                         name=name,
                                         maintainOffset=maintainOffset,
                                         skip=skip)[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject
