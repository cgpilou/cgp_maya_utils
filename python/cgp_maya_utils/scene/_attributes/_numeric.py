"""
numeric attribute object library
"""


# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants
from . import _generic


# BASE OBJECT #


class NumericAttribute(_generic.Attribute):
    """attribute object that manipulates any kind of numeric attribute
    """

    # ATTRIBUTES #

    _attributeType = 'numeric'

    # INIT #

    def __le__(self, value):
        """override le operator

        :param value: value to compare to the numeric attribute
        :type value: numeric

        :return: ``True`` : attribute is less than or equal to the value - ``False`` attribute is greater than the value
        :rtype: bool
        """

        # return
        return self.value() <= value

    def __lt__(self, value):
        """override lt operator

        :param value:value to compare to the numeric attribute
        :type value: numeric

        :return: ``True`` : attribute is less than the value - ``False`` attribute is greater than or equal to the value
        :rtype: bool
        """

        # return
        return self.value() < value

    def __ge__(self, value):
        """override ge operator

        :param value : value to compare to the numeric attribute
        :type value: int or float

        :return: ``True`` : attribute is greater than or equal to the value - ``False`` attribute is less than the value
        :rtype: bool
        """

        # return
        return self.value() >= value

    def __gt__(self, value):
        """override gt operator

        :param value: value to compare to the numeric attribute
        :type value: int or float

        :return: ``True`` : attribute is greater than the value - ``False`` attribute is less than or equal to the value
        :rtype: bool
        """

        # return
        return self.value() > value

    # COMMANDS #

    def add(self, value):
        """add the value to the numeric attribute

        :param value: value to add to the numeric attribute
        :type value: int or float
        """

        # execute
        self.setValue(self.value() + value)

    def setValue(self, value):
        """set the value on the numeric attribute

        :param value: value to set on the numeric attribute
        :type value: int or float
        """

        # execute
        maya.cmds.setAttr(self.fullName(), value)

    def substract(self, value):
        """substract the value to the numeric attribute

        :param value: value to substract to the numeric
        :type value: int or float
        """

        # execute
        self.add(-value)

    def multiply(self, value):
        """multiply the numeric attribute by the value

        :param value: value to multiply to the numeric attribute
        :type value: int or float
        """

        # execute
        self.setValue(self.value() * value)

    def divide(self, value):
        """divide the numeric attribute by the value

        :param value: value to divide to the numeric attribute
        :type value: int or float
        """

        # execute
        self.multiply(1 / value)

    def power(self, value):
        """power the numeric attribute by the value

        :param value: value to power the numeric attribute by
        :type value: int or float
        """

        # execute
        self.setValue(pow(self.value(), value))


# NUMERIC OBJECTS #


class ByteAttribute(NumericAttribute):
    """attribute object that manipulates a ``byte`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.BYTE


class DoubleAttribute(NumericAttribute):
    """attribute object that manipulates a ``double`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.DOUBLE


class DoubleAngleAttribute(NumericAttribute):
    """attribute object that manipulates a ``doubleAngle`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.DOUBLE_ANGLE


class DoubleLinearAttribute(NumericAttribute):
    """attribute object that manipulates a ``doubleLinear`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.DOUBLE_LINEAR


class FloatAttribute(NumericAttribute):
    """attribute object that manipulates a ``float`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.FLOAT


class LongAttribute(NumericAttribute):
    """attribute object that manipulates a ``long`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.LONG


class ShortAttribute(NumericAttribute):
    """attribute object that manipulates a ``short`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.SHORT


class TimeAttribute(NumericAttribute):
    """attribute object that manipulates a ``time`` attribute
    """

    # ATTRIBUTES #

    _attributeType = cgp_maya_utils.constants.AttributeType.TIME
