"""
miscellaneous attribute object library
"""

# imports python
import re
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

    _TYPE = cgp_maya_utils.constants.AttributeType.BOOLEAN

    # COMMANDS #

    def setValue(self, value):
        """set the value on the attribute

        :param value: value to set on the attribute
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

    _TYPE = cgp_maya_utils.constants.AttributeType.ENUM

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, node, name, items=None, value=None, connectionSource=None, connectionDestinations=None, **__):
        """create an enum attribute

        :param node: node on which to create the attribute
        :type node: str

        :param name: name of the attribute to create
        :type name: str

        :param items: items used to create the attribute
        :type items: list[str]

        :param value: value to set on the attribute
        :type value: int or str

        :param connectionSource: attribute to connect as source - ``node.attribute``
        :type connectionSource: str or :class:`cgp_maya_utils.scene.Attribute`

        :param connectionDestinations: attributes to connect as destination - ``[node1.attrib1, node2.attrib2 ...]``
        :type connectionDestinations: list[str] or list[:class:`cgp_maya_utils.scene.Attribute`]

        :return: the created attribute
        :rtype: :class:`cgp_maya_utils.scene.EnumAttribute`
        """

        # execute
        maya.cmds.addAttr(node, longName=name, attributeType=cls._TYPE, enumName=':'.join(items or []))

        # get attribute object
        attrObject = cls('{0}.{1}'.format(node, name))

        # set if value specified
        if value:
            attrObject.setValue(value)

        # connect attribute
        attrObject.connect(source=connectionSource, destinations=connectionDestinations)

        # return
        return attrObject

    # COMMANDS #

    def data(self, skipConversionNodes=True):
        """get the data necessary to store the enum attribute on disk and/or recreate it from scratch

        :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the data of the attribute
        :rtype: dict
        """

        # init
        data = super(EnumAttribute, self).data(skipConversionNodes=skipConversionNodes)

        # update data
        data['items'] = self.items()

        # return
        return data

    def items(self):
        """get the items of the attribute

        :return: the items of the attribute
        :rtype: list[str]
        """

        # get the string formatted item list
        itemsAsString = maya.cmds.attributeQuery(self.uniqueName(),
                                                 node=self._nodeNameFromFullName(self.fullName()),
                                                 listEnum=True)

        # use a regex to ensure item names containing ':' won't be interpreted as separated items
        # ':' is the matches delimiter except if it is followed by a space
        regex = r"( ?: |[^:])+"

        # return
        return [match.group() for match in re.finditer(regex, itemsAsString[0])] if itemsAsString else []

    def itemIndex(self, value):
        """get the item index from the given value

        Note: By default the enum use default 0 based indices. But Maya allow to override an index.
              In this case the item string will look like `myValue=7` where `7` is the index.
              But the `maya.cmds.getAttr(self.fullName(), asString=True)` will only return `myValue`

        :param value: the value of the enum item to get the index from
        :type value: str

        :return: the index of the item holding the value
        :rtype: int
        """

        # init
        index = 0

        # get the index
        for item in self.items():

            # get item value and new index
            itemValue, newIndex = item.split("=") if item.count("=") == 1 else (item, index)

            # get index
            index = int(newIndex) if isinstance(newIndex, basestring) and newIndex.isdigit() else index

            # return
            if value == itemValue:
                return index

            # increment index
            index += 1

        # raise an error if the given value is not in the enum items
        raise ValueError("Value '{}' not in {}".format(value, repr(self.fullName())))

    def setAnimKey(self,
                   frame=None,
                   animLayer=None,
                   value=None,
                   inAngle=None,
                   inTangentType=None,
                   inWeight=None,
                   outAngle=None,
                   outTangentType=None,
                   outWeight=None):
        """set an animKey on the attribute

        :param frame: frame of the animKey - default is current frame
        :type frame: float

        :param animLayer: the animation layer to create the animKey on - default is current animation layer
        :type animLayer: :class:`cgp_maya_utils.scene.AnimLayer`

        :param value: value of the animKey - key is inserted if nothing is specified
        :type value: float

        :param inAngle: the in tangent angle
        :type inAngle: float

        :param inTangentType: type of the inTangent of the animKey
        :type inTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param inWeight: the in tangent weight of the animKey
        :type inWeight: float

        :param outAngle: the out tangent angle of the animKey
        :type outAngle: float

        :param outTangentType: type of the outTangent of the animKey
        :type outTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param outWeight: the out tangent weight of the animKey
        :param outWeight: float

        :return: the created animKey
        :rtype: :class:`cgp_maya_utils.scene.AnimKey`
        """

        # get value
        if value is None:
            value = self.value(asString=False)

        elif isinstance(value, basestring):
            value = self.items().index(value)

        # return
        return super(EnumAttribute, self).setAnimKey(frame=frame,
                                                     animLayer=animLayer,
                                                     value=value,
                                                     inAngle=inAngle,
                                                     inTangentType=inTangentType,
                                                     inWeight=inWeight,
                                                     outAngle=outAngle,
                                                     outTangentType=outTangentType,
                                                     outWeight=outWeight)

    def setValue(self, value):
        """set the value on the attribute

        :param value: value to set on the attribute
        :type value: int or float or str
        """

        # data is int - warning: float is accepted but will be truncated
        if isinstance(value, (int, float)):
            maya.cmds.setAttr(self.fullName(), value)

        # data is str - warning: first match will be selected for enum containing multiple items using the same str
        elif isinstance(value, basestring):
            maya.cmds.setAttr(self.fullName(), self.itemIndex(value))

        # errors
        else:
            raise ValueError('{0} {1} is not a valid data - expecting --> str or int '.format(value, type(value)))

    def value(self, asString=True):
        """get the value of the attribute

        :param asString: ``True`` : value is returned as a string - ``False`` : value is returned as an integer
        :type asString: bool

        :return: the value of the attribute
        :rtype: int or str
        """

        # return
        return maya.cmds.getAttr(self.fullName(), asString=asString)


class MatrixAttribute(_generic.Attribute):
    """attribute object that manipulates a ``matrix`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.MATRIX

    # COMMANDS #

    def setValue(self, value):
        """set the value on the attribute

        :param value: value to set on the attribute
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
        """get the transformationMatrix related to the MMatrix stored in the matrix attribute

        :param rotateOrder: rotateOrder of the transformationMatrix to get - use transform one if nothing specified
        :type rotateOrder: :class:`cgp_maya_utils.constants.RotateOrder`

        :return: the transformationMatrix
        :rtype: :class:`cgp_maya_utils.api.TransformationMatrix`
        """

        # return
        return cgp_maya_utils.api.TransformationMatrix.fromAttribute(self, rotateOrder=rotateOrder)


class MessageAttribute(_generic.Attribute):
    """attribute object that manipulates a ``message`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.MESSAGE

    # COMMANDS #

    def setValue(self, value):
        """set the value on the attribute

        :param value: value to set on the attribute
        :type value: str or :class:`cgp_maya_utils.scene.Attribute`
        """

        # execute
        if value:
            self.connect(source=value)
        else:
            self.disconnect(source=True, destinations=False)

    def value(self):
        """get the value of the attribute

        :return: the value of the attribute
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

    _TYPE = cgp_maya_utils.constants.AttributeType.STRING

    # COMMANDS #

    def eval(self):
        """eval the content of the string attribute

        :return: the evaluated content
        :rtype: literal
        """

        # return
        return ast.literal_eval(self.value())

    def setValue(self, value):
        """set the value on the attribute

        :param value: value to set on the attribute
        :type value: str
        """

        # execute
        maya.cmds.setAttr(self.fullName(), value or '', type=self.attributeType())
