"""
array attribute object library
"""

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants
from . import _generic


# BASE OBJECT #


class ArrayAttribute(_generic.Attribute):
    """attribute object that manipulates any kind of array attribute
    """

    # COMMANDS #

    def setValue(self, value):
        """set the value on the attribute

        :param value: value used to set the attribute
        :type value: list
        """

        maya.cmds.setAttr(self.fullName(), len(value), *value, type=self.attributeType())

    def size(self):
        """get the size of the attribute (number of elements)

        :return: the size
        :rtype: int
        """

        # return
        return maya.cmds.getAttr(self.fullName(), size=True)

    def value(self):
        """get the value of the attribute

        :return: the value of the attribute
        :rtype: list
        """

        return super(ArrayAttribute, self).value() or []


# ARRAY OBJECTS #


class DoubleArrayAttribute(ArrayAttribute):
    """attribute object that manipulates a ``doubleArray`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.DOUBLE_ARRAY

    # COMMANDS #

    def setValue(self, value):
        """set the value on the attribute

        :param value: value used to set the attribute
        :type value: list
        """

        # execute
        value.insert(0, len(value))
        maya.cmds.setAttr(self.fullName(), value, type=self.attributeType())


class FloatArrayAttribute(ArrayAttribute):
    """attribute object that manipulates a ``floatArray`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.FLOAT_ARRAY

    # COMMANDS #

    def setValue(self, value):
        """set the value on the attribute

        :param value: value used to set the attribute
        :type value: list
        """

        # contrary to other array attributes, floatArray attribute doesn't need now the value length
        maya.cmds.setAttr(self.fullName(), value, type=self.attributeType())

    def size(self):
        """get the size of the attribute (number of elements)

        :return: the size of the attribute
        :rtype: int
        """

        # floatArray attribute size query always return 1 so we need a workaround to find its actual size
        return len(self.value())


class Int32ArrayAttribute(ArrayAttribute):
    """attribute object that manipulates a ``int32Array`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.INT_32_ARRAY

    # COMMANDS #

    def setValue(self, value):
        """set the value on the attribute

        :param value: value used to set the attribute
        :type value: list
        """

        # execute
        value.insert(0, len(value))
        maya.cmds.setAttr(self.fullName(), value, type=self.attributeType())


class PointArrayAttribute(ArrayAttribute):
    """attribute object that manipulates a ``pointArray`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.POINT_ARRAY


class StringArrayAttribute(ArrayAttribute):
    """attribute object that manipulates a ``stringArray`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.STRING_ARRAY


class VectorArrayAttribute(ArrayAttribute):
    """attribute object that manipulates a ``vectorArray`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.VECTOR_ARRAY
