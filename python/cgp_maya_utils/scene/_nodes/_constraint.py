"""
constraint object library
"""

# imports third-parties
import cgp_generic_utils.python
import cgp_generic_utils.constants
import maya.cmds

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api
from . import _generic


# BASE OBJECT #


class Constraint(_generic.DagNode):
    """node object that manipulates any kind of constraint node
    """

    # ATTRIBUTES #

    _nodeType = 'constraint'

    # COMMANDS #

    def data(self):
        """data necessary to store the constraint node on disk and/or recreate it from scratch

        :return: the data of the constraint
        :rtype: dict
        """

        # init
        data = super(Constraint, self).data()

        # update data
        data['drivers'] = [xform.name() for xform in self.driverTransforms()]
        data['driven'] = self.drivenTransform().name()
        data['drivenAttributes'] = [attr.name() for attr in self.drivenAttributes()]

        # return
        return data

    def drivenTransform(self):
        """the transform that is driven by the constraint

        :return: the driven transform
        :rtype: :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`
        """

        # init
        data = []

        #  execute
        for output in self._drivenOutputs():
            connectedNodes = maya.cmds.listConnections('{0}.{1}'.format(self.name(), output),
                                                       source=False,
                                                       destination=True) or []
            data.extend(connectedNodes)

        # return
        return cgp_maya_utils.scene._api.node(data[0]) if data else None

    def drivenAttributes(self):
        """the attributes of the driven transform that are driven by the constraint

        :return: the driven attributes
        :rtype: list[:class:`cgp_maya_utils.scene.Attribute`]
        """

        # init
        data = []

        # get driven data
        for output in self._drivenOutputs():

            # get connections
            connections = maya.cmds.listConnections('{0}.{1}'.format(self.name(), output),
                                                    source=False,
                                                    destination=True,
                                                    plugs=True) or []

            # update data
            for con in connections:
                if con not in data:
                    data.append(con)

        # return
        return [cgp_maya_utils.scene._api.attribute(con) for con in data]

    def driverTransforms(self):
        """the transforms that drives the constraint

        :return: the driver transforms
        :rtype: list[:class:`cgp_maya_utils.scene.Transform`, :class:`cgp_maya_utils.scene.Joint`]
        """

        # init
        data = []

        #  execute
        for inp in self._driverInputs():

            # get full attribute
            fullAttribute = '{0}.{1}'.format(self.name(), inp)

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
                print 'can\'t get connections from {0}'.format(fullAttribute)

        # return
        return [cgp_maya_utils.scene._api.node(item) for item in data] or None

    def isValid(self):
        """check is the constraint is valid by verifying if it has driver and driven transforms connected

        :return: ``True`` : the constraint is valid - ``False`` : the constraint is invalid
        :rtype: bool
        """

        # return
        return self.driverTransforms() and self.drivenTransform()

    # PRIVATE COMMANDS #

    def _driverInputs(self):
        """the input attributes of the constraint that are connected to the drivers of the constraint
        Those attributes ares scanned to get the driver nodes through connection

        :return: the input attributes connected to the drivers
        :rtype: list[str]
        """

        # execute
        return []

    def _drivenOutputs(self):
        """the output attributes of the constraint that are connected to the driven of the constraint
        Those attributes ares scanned to get the driven nodes through connection

        :return: the output attributes connected to the driven
        :rtype: list[str]
        """

        # execute
        return []

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(Constraint, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['enableRestPosition',
                                    'lockOutput'])

        # return
        return availableAttributes

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
                raise ValueError('{0} is not a valid driven attribute - {1}'
                                 .format(attr, cgp_maya_utils.constants.Transform.ALL))

        # execute
        for attr in drivenAttributes:
            if attr in cgp_maya_utils.constants.Transform.GENERAL:
                for axe in cgp_generic_utils.constants.Axis.ALL:
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

    _nodeType = 'aimConstraint'

    # COMMANDS #

    @classmethod
    def create(cls, drivers, driven, drivenAttributes=None, maintainOffset=False,
               attributeValues=None, name=None, **__):
        """create an aimConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str] or list[:class:`cgp_maya_utils.scene.Node`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Node`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint created with offset - ``False`` : constraint created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the constraint
        :type attributeValues: dict

        :param name: name of the constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.AimConstraint`
        """

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be aimConstraint'.format(driven))

        # get skip attributes
        skipAttributes = []

        for axe in cgp_generic_utils.constants.Axis.ALL:
            if 'r{0}'.format(axe) not in drivenAttributes:
                skipAttributes.append(axe)

        # get infos
        data = {'aimVector': [], 'upVector': [], 'worldUpVector': []}

        if attributeValues:

            # get vectors
            for attr in ['aimVector', 'upVector', 'worldUpVector']:
                for axe in cgp_generic_utils.constants.Axis.ALL:

                    # get value
                    value = attributeValues['{0}{1}'.format(attr, axe.upper())]
                    value = (cgp_maya_utils.scene._api.attribute(value).value()
                             if isinstance(value, basestring)
                             else value)

                    # update vectors
                    data[attr].append(value)

            # get worldUpType
            data['worldUpType'] = cgp_maya_utils.constants.WorldUpType.ALL[attributeValues['worldUpType']]

            # get worldUpObject
            if attributeValues['worldUpMatrix']:
                data.pop('worldUpVector')
                data['worldUpObject'] = (cgp_maya_utils.scene._api
                                         .attribute(attributeValues['worldUpMatrix']).node().name())

        else:
            data['aimVector'] = [1, 0, 0]
            data['upVector'] = [0, 1, 0]
            data['worldUpVector'] = [0, 1, 0]
            data['worldUpType'] = cgp_maya_utils.constants.WorldUpType.VECTOR

        # execute
        node = maya.cmds.aimConstraint(drivers,
                                       driven,
                                       name=name or '{0}_aimConstraint'.format(driven),
                                       maintainOffset=maintainOffset,
                                       skip=skipAttributes,
                                       **data)[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject

    # PRIVATE COMMANDS #

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(AimConstraint, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['worldUpMatrix',
                                    'aimVector',
                                    'restRotate',
                                    'upVector',
                                    'worldUpType',
                                    'worldUpVector'])

        # return
        return availableAttributes

    def _driverInputs(self):
        """get inputs

        :return: the inputs of the constraint related to the drivers
        :rtype: list[str]
        """

        # return
        return ['target[*].targetParentMatrix']

    def _drivenOutputs(self):
        """get the outputs of the constraint

        :return: the outputs of the constraint related to the driven
        :rtype: list[str]
        """

        # return
        return ['constraintRotate', 'constraintRotateX', 'constraintRotateY', 'constraintRotateZ']


class OrientConstraint(Constraint):
    """node object that manipulates an ``orient`` constraint node
    """

    # ATTRIBUTES #

    _nodeType = 'orientConstraint'

    # COMMANDS #

    @classmethod
    def create(cls, drivers, driven, drivenAttributes=None, maintainOffset=False,
               attributeValues=None, name=None, **__):
        """create an orientConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str] or list[:class:`cgp_maya_utils.scene.Transform`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Transform`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint created with offset - ``False`` : constraint created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the constraint
        :type attributeValues: dict

        :param name: name of the constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.OrientConstraint`
        """

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be orientConstraint'.format(driven))

        # get skip attributes
        skipAttributes = []

        for axe in ['x', 'y', 'z']:
            if 'r{0}'.format(axe) not in drivenAttributes:
                skipAttributes.append(axe)

        # execute
        node = maya.cmds.orientConstraint(drivers,
                                          driven,
                                          name=name or '{0}_orientConstraint'.format(driven),
                                          maintainOffset=maintainOffset,
                                          skip=skipAttributes)[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject

    # PRIVATE COMMANDS #

    def _driverInputs(self):
        """get inputs

        :return: the inputs of the constraint related to the drivers
        :rtype: list[str]
        """

        # return
        return ['target[*].targetRotate']

    def _drivenOutputs(self):
        """get the outputs of the constraint

        :return: the outputs of the constraint related to the driven
        :rtype: list[str]
        """

        # return
        return ['constraintRotate', 'constraintRotateX', 'constraintRotateY', 'constraintRotateZ']

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(OrientConstraint, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['interpType',
                                    'restRotateX', 'restRotateY', 'restRotateZ'])

        # return
        return availableAttributes


class ParentConstraint(Constraint):
    """node object that manipulates an ``parent`` constraint node
    """

    # ATTRIBUTES #

    _nodeType = 'parentConstraint'

    # COMMANDS #

    @classmethod
    def create(cls, drivers, driven, drivenAttributes=None, maintainOffset=False,
               attributeValues=None, name=None, **__):
        """create an parentConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str] or list[:class:`cgp_maya_utils.scene.Transform`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Transform`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint created with offset - ``False`` : constraint created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the constraint
        :type attributeValues: dict

        :param name: name of the constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_may_utils.scene.ParentConstraint`
        """

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be parentConstraint'.format(driven))

        # get skip attributes
        skipAttributes = {'t': [], 'r': []}

        for key in skipAttributes:
            for axe in ['x', 'y', 'z']:
                if '{0}{1}'.format(key, axe) not in drivenAttributes:
                    skipAttributes[key].append(axe)

        # execute
        node = maya.cmds.parentConstraint(drivers,
                                          driven,
                                          name=name or '{0}_parentConstraint'.format(driven),
                                          maintainOffset=maintainOffset,
                                          skipTranslate=skipAttributes['t'],
                                          skipRotate=skipAttributes['r'])[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject

    # PRIVATE COMMANDS #

    def _driverInputs(self):
        """get inputs

        :return: the inputs of the constraint related to the drivers
        :rtype: list[str]
        """

        # return
        return ['target[*].targetParentMatrix']

    def _drivenOutputs(self):
        """get the outputs of the constraint

        :return: the outputs of the constraint related to the driven
        :rtype: list[str]
        """

        # return
        return ['constraintTranslate', 'constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ',
                'constraintRotate', 'constraintRotateX', 'constraintRotateY', 'constraintRotateZ']

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(ParentConstraint, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['interpType',
                                    'restRotateX', 'restRotateY', 'restRotateZ',
                                    'restTranslateX', 'restTranslateY', 'restTranslateZ'])

        # return
        return availableAttributes


class PointConstraint(Constraint):
    """node object that manipulates an ``point`` constraint node
    """

    # ATTRIBUTES #

    _nodeType = 'pointConstraint'

    # COMMANDS #

    @classmethod
    def create(cls, drivers, driven, drivenAttributes=None, maintainOffset=False,
               attributeValues=None, name=None, **__):
        """create a pointConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[:class:`cgp_maya_utils.scene.Transform`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Transform`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint created with offset - ``False`` : constraint created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the constraint
        :type attributeValues: dict

        :param name: name of the constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.PointConstraint`
        """

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be aimConstraint'.format(driven))

        # get skip attributes
        skipAttributes = []

        for axe in ['x', 'y', 'z']:
            if 't{0}'.format(axe) not in drivenAttributes:
                skipAttributes.append(axe)

        # execute
        node = maya.cmds.pointConstraint(drivers,
                                         driven,
                                         name=name or '{0}_parentConstraint'.format(driven),
                                         maintainOffset=maintainOffset,
                                         skip=skipAttributes)[0]

        cstrObject = cls(node)

        # apply attributeValues
        if attributeValues:
            cstrObject.setAttributeValues(attributeValues)

        # return
        return cstrObject

    # PRIVATE COMMANDS #

    def _driverInputs(self):
        """get inputs

        :return: the inputs of the constraint related to the drivers
        :rtype: list[str]
        """

        # return
        return ['target[*].targetTranslate']

    def _drivenOutputs(self):
        """get the outputs of the constraint

        :return: the outputs of the constraint related to the driven
        :rtype: list[str]
        """

        # return
        return ['constraintTranslate', 'constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ']

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(PointConstraint, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['constraintOffsetPolarity',
                                    'restTranslateX',
                                    'restTranslateY',
                                    'restTranslateZ'])

        # return
        return availableAttributes


class ScaleConstraint(Constraint):
    """node object that manipulates an ``scale`` constraint node
    """

    # ATTRIBUTES #

    _nodeType = 'scaleConstraint'

    # COMMANDS #

    @classmethod
    def create(cls, drivers, driven, drivenAttributes=None, maintainOffset=False,
               attributeValues=None, name=None, **__):
        """create a scaleConstraint

        :param drivers: transforms driving the constraint
        :type drivers: list[str] or list[:class:`cgp_maya_utils.scene.Transform`]

        :param driven: transform driven by the constraint
        :type driven: str or :class:`cgp_maya_utils.scene.Transform`

        :param drivenAttributes: driven attributes controlled by the constraint - all attributes if nothing is specified
        :type drivenAttributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param maintainOffset: ``True`` : constraint created with offset - ``False`` : constraint created without offset
        :type maintainOffset: bool

        :param attributeValues: attribute values to set on the constraint
        :type attributeValues: dict

        :param name: name of the constraint
        :type name: str

        :return: the created constraint
        :rtype: :class:`cgp_maya_utils.scene.ScaleConstraint`
        """

        # init
        drivers = [str(driver) for driver in drivers]
        driven = str(driven)

        # get driven attributes
        drivenAttributes = cls._formatDrivenAttributes(driven, drivenAttributes=drivenAttributes)

        # errors
        if not drivenAttributes:
            raise RuntimeError('{0} can\'t be aimConstraint'.format(driven))

        # get skip attributes
        skipAttributes = []

        for axe in ['x', 'y', 'z']:
            if 's{0}'.format(axe) not in drivenAttributes:
                skipAttributes.append(axe)

        # execute
        node = maya.cmds.scaleConstraint(drivers,
                                         driven,
                                         name=name or '{0}_scaleConstraint'.format(driven),
                                         maintainOffset=maintainOffset,
                                         skip=skipAttributes)[0]

        constraintObject = cls(node)

        # apply attributeValues
        if attributeValues:
            constraintObject.setAttributeValues(attributeValues)

        # return
        return constraintObject

    # PRIVATE COMMANDS #

    def _driverInputs(self):
        """get inputs

        :return: the inputs of the constraint related to the drivers
        :rtype: list[str]
        """

        # return
        return ['target[*].targetScale']

    def _drivenOutputs(self):
        """get the outputs of the constraint

        :return: the outputs of the constraint related to the driven
        :rtype: list[str]
        """

        # return
        return ['constraintScale', 'constraintScaleX', 'constraintScaleY', 'constraintScaleZ']

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # return
        return ['enableRestPosition', 'lockOutput']
