"""
compound attribute object library
"""

# imports third-parties
import maya.cmds
import cgp_generic_utils.constants

# imports local
import cgp_maya_utils.constants
from . import _generic


# BASE OBJECT #


class CompoundAttribute(_generic.Attribute):
    """attribute object that manipulates any kind of compound attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.COMPOUND
    _attributeSubType = NotImplemented

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, node, name, components=None, value=None, connections=None, **__):
        """create a compound attribute

        :param node: node on which to create the attribute
        :type node: str

        :param name: name of the attribute to create
        :type name: str

        :param components: components used to create the attribute - default is Axis.ALL
        :type components: any

        :param value: value to set on the attribute
        :type value: list[any]

        :param connections: connection to build on the attribute - {'source': obj.attr, 'destinations': [obj.attr ...]}
        :type connections: dict

        :return: the created attribute
        :rtype: :class:`cgp_maya_utils.scene.CompoundAttribute`
        """

        # init
        components = components or cgp_generic_utils.constants.Axis.ALL

        # execute
        maya.cmds.addAttr(node, longName=name, attributeType=cls._attributeType)

        for component in components:
            maya.cmds.addAttr(node, longName=component, attributeType=cls._attributeSubType, parent=name)

        # get attribute object
        attrObject = cls('{0}.{1}'.format(node, name))

        # set if value specified
        if value:
            attrObject.setValue(value)

        # connect attribute if specified
        if connections:
            attrObject.connect(source=connections['source'], destinations=connections['destinations'])

        # return
        return attrObject

    # COMMANDS #

    def components(self):
        """the components of the compound attribute

        :return: the components of the compound attribute
        :rtype: list[:class:`cgp_maya_utils.sceneAttribute`]
        """

        # get components
        components = maya.cmds.attributeQuery(self.name(), node=self.node().name(), listChildren=True)

        # return
        return [self.node().attribute(component) for component in components]

    def data(self, skipConversionNodes=True):
        """data necessary to store the compound attribute on disk and/or recreate it from scratch

        :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the data of the compound attribute
        :rtype: dict
        """

        # init
        data = super(CompoundAttribute, self).data(skipConversionNodes=skipConversionNodes)

        # update data
        data['components'] = [component.name() for component in self.components()]

        # return
        return data

    def setValue(self, value):
        """set the value of the compound attribute

        :param value: value to set on the compound attribute
        :type value: list[any]
        """

        # execute
        maya.cmds.setAttr(self.fullName(), type=self.attributeType(), *value)

    def subType(self):
        """the subType of the compound attribute

        :return: the subType of the compound attribute
        :rtype: str
        """

        # return
        return self._attributeSubType

    def value(self):
        """the value of the compound attribute

        :return: the value of the compound attribute
        :rtype: any
        """

        # return
        return maya.cmds.getAttr(self.fullName())[0]


# COMPOUND ATTRIBUTES #


class Double3Attribute(CompoundAttribute):
    """attribute object that manipulates ``double3`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.DOUBLE3
    _attributeSubType = cgp_maya_utils.constants.AttributeType.DOUBLE


class Float3Attribute(CompoundAttribute):
    """attribute object that manipulates ``float3`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.FLOAT3
    _attributeSubType = cgp_maya_utils.constants.AttributeType.FLOAT


class TDataCompoundAttribute(CompoundAttribute):
    """attribute object that manipulates ``TDataCompound`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.TDATACOMPOUND
    _attributeSubType = None

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, *_, **__):
        """create a TDataCompound attribute
        """

        # errors
        raise UserWarning('{0} attribute can\'t be created by API'.format(cls._attributeType))

    # COMMANDS #

    def setValue(self, value):
        """set the value of the TDataCompound attribute

        :param value: value to set to the TDataCompound attribute
        :type value: dict
        """

        # execute
        for attribute, attributeValue in value.items():
            self.node().attribute(attribute).setValue(attributeValue)

    def value(self):
        """the value of the TDataCompound attribute

        :return: the value of the TDataCompound attribute
        :rtype: dict
        """

        # init
        value = {}

        # execute
        for component in self.components():
            value[component.name()] = component.value()

        # return
        return value
