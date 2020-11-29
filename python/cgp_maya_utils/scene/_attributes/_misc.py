"""
miscellaneous attribute object library
"""


# imports python
import ast

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.api
import cgp_maya_utils.constants
from . import _generic


# MISC OBJECTS #


class BoolAttribute(_generic.Attribute):
    """attribute object that manipulates a ``boolean`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.BOOLEAN

    # COMMANDS #

    def setValue(self, value):
        """set the value on the attribute

        :param value: value to set on the boolean attribute
        :type value: bool or int
        """

        # init
        value = 0 if not value else 1

        # execute
        maya.cmds.setAttr(self.fullName(), value)


class EnumAttribute(_generic.Attribute):
    """attribute object that manipulates a ``enum`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.ENUM

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, node, name, items=None, value=None, connections=None, **__):
        """create an enum attribute

        :param node: node on which to create the attribute
        :type node: str

        :param name: name of the attribute to create
        :type name: str

        :param items: items used to create the attribute
        :type items: list[str]

        :param value: value to set on the attribute
        :type value: int or str

        :param connections: connection to build on the attribute -
                            ``{'source': node.attribute, 'destinations': [node.attribute ...]}``
        :type connections: dict

        :return: the created attribute
        :rtype: :class:`cgp_maya_utils.scene.EnumAttribute`
        """

        # execute
        maya.cmds.addAttr(node, longName=name, attributeType=cls._attributeType, enumName=':'.join(items or []))

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

    def data(self, skipConversionNodes=True):
        """data necessary to store the enum attribute on disk and/or recreate it from scratch

        :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the data of the enum attribute
        :rtype: dict
        """

        # init
        data = super(EnumAttribute, self).data(skipConversionNodes=skipConversionNodes)

        # update data
        data['items'] = self.items()

        # return
        return data

    def items(self):
        """get the items of the enum attribute

        :return: the items of the enum attribute
        :rtype: list[str]
        """

        # return
        return maya.cmds.attributeQuery(self.name(), node=self.node().name(), listEnum=True)[0].split(':')

    def setValue(self, value):
        """set the value on the enum attribute

        :param value: value to set on the enum attribute
        :type value: float or str
        """

        # data is int
        if isinstance(value, int):
            maya.cmds.setAttr(self.fullName(), value)

        # data is str
        elif isinstance(value, basestring):
            enumValues = maya.cmds.attributeQuery(self.name(), node=self.node().name(), listEnum=True)
            enumValues = enumValues[0].split(':')
            maya.cmds.setAttr(self.fullName(), enumValues.index(value))

        # errors
        else:
            raise ValueError('{0} {1} is not a valid data - expecting --> str or int'.format(value, type(value)))

    def value(self, asString=True):
        """the value of the enum attribute

        :param asString: ``True`` : value is returned as a string - ``False`` : value is returned as an integer
        :type asString: bool

        :return: the value of the enum attribute
        :rtype: int or str
        """

        # return
        return maya.cmds.getAttr(self.fullName(), asString=asString)


class MatrixAttribute(_generic.Attribute):
    """attribute object that manipulates a ``matrix`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.MATRIX

    # COMMANDS #

    def setValue(self, value):
        """set the value on the matrix attribute

        :param value: value to set on the matrix attribute
        :type value: list[int, float]
        """

        # execute
        if value and isinstance(value, basestring):
            self.connect(source=value)
        elif value:
            maya.cmds.setAttr(self.fullName(), type=self.attributeType(), *value)
        else:
            self.disconnect(source=True, destinations=False)

    def transformationMatrix(self, rotateOrder=None):
        """the transformationMatrix related to the MMatrix stored in the matrix attribute

        :param rotateOrder: rotateOrder of the transformationMatrix to get - use transform one if nothing specified
        :type rotateOrder: str

        :return: the transformationMatrix
        :rtype: :class:`cgp_maya_utils.api.TransformationMatrix`
        """

        # return
        return cgp_maya_utils.api.TransformationMatrix.fromAttribute(self, rotateOrder=rotateOrder)


class MessageAttribute(_generic.Attribute):
    """attribute object that manipulates a ``message`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.MESSAGE

    # COMMANDS #

    def setValue(self, value):
        """set the value on the message attribute

        :param value: value to set on the message attribute
        :type value: str or :class:`cgp_maya_utils.scene.Attribute`
        """

        # execute
        if value:
            self.connect(source=value)
        else:
            self.disconnect(source=True, destinations=False)

    def value(self):
        """the value of the message attribute

        :return: the value of the message attribute
        :rtype: str
        """

        # get connection
        connections = maya.cmds.listConnections(self.fullName(), source=True, destination=True, plugs=True)

        # return
        return connections[0] if connections else None


class StringAttribute(_generic.Attribute):
    """attribute object that manipulates a ``string`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.STRING

    # COMMANDS #

    def eval(self):
        """eval the content of the string attribute

        :return: the eval content
        :rtype: literal
        """

        # return
        return ast.literal_eval(self.value())

    def setValue(self, value):
        """set the value on the attribute

        :param value: value used to set the attribute
        :type value: str
        """

        # execute
        maya.cmds.setAttr(self.fullName(), value or '', type=self.attributeType())
