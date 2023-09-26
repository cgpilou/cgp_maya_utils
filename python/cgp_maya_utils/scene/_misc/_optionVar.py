"""
package : cgp_maya_utils.scene._misc
file : _optionVar.py

description : optionVars library
"""

# imports third-parties
import maya.cmds

# import local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api


class OptionVar(object):
    """optionVar object that manipulates any kind of optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = NotImplemented
    _PROTECTED_OPTION_VARS = ['TrustCenterCommandsList']
    _SETTER_FLAG = NotImplemented
    _TYPE = cgp_maya_utils.constants.OptionVarType.GENERIC

    # INIT #

    def __init__(self, name):
        """OptionVar class initialization

        :param name: name of the optionVar
        :type name: str
        """

        # init
        self._name = name

    def __repr__(self):
        """get the optionVar representation

        :return: the representation of the OptionVar
        :rtype: str
        """

        # return
        return '{0}({1!r})'.format(self.__class__.__name__, self.name())

    # COMMANDS #

    def isProtected(self):
        """check if the OptionVar is protected

        :return: ``True`` : the optionVar is protected - ``False`` : the optionvar is not protected
        :rtype: bool
        """

        # return
        return self.name() in self._PROTECTED_OPTION_VARS

    def name(self):
        """get the name of the optionVar

        :return: The name of the optionVar
        :rtype: str
        """

        # return
        return self._name

    def value(self):
        """get the value of the optionVar

        :return: The value of the optionVar
        :rtype: any
        """

        # return
        return maya.cmds.optionVar(query=self._name)

    def setValue(self, value):
        """set the value of the OptionVar

        :param value: value to set on the optionVar
        :type value: any
        """

        # setting optionVars is slow to execute - speed up by skipping already correct values
        if value == self.value():
            return

        # alert user if the OptionVar is read only
        if self._DATA_TYPE == NotImplemented:
            typedClasses = [cls.__name__ for cls in cgp_maya_utils.scene._api._OPTIONVAR_TYPES.values()]
            raise TypeError('Unknown type for OptionVar "{}". '
                            'Non-typed OptionVar instances are read only. '
                            'To be able to set the value consider using typed OptionVar classes such as: '
                            '{}'.format(self._name, ', '.join(typedClasses)))

        # make sur the data to set matches the correct type to avoid Maya crashes or userPrefs.mel file corruption
        elif not isinstance(value, self._DATA_TYPE):
            expected = self._DATA_TYPE.__name__
            given = type(value).__name__
            raise TypeError('Unable to set {} value: '
                            '{} expected, {} given'.format(self.__class__.__name__, expected, given))

        # set the value
        maya.cmds.optionVar(**{self._SETTER_FLAG: (self._name, value)})


class IntOptionVar(OptionVar):
    """optionVar object that manipulates an ``int`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = int
    _SETTER_FLAG = 'intValue'
    _TYPE = cgp_maya_utils.constants.OptionVarType.INT


class LongOptionVar(IntOptionVar):
    """optionVar object that manipulates a ``long`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = long
    _TYPE = cgp_maya_utils.constants.OptionVarType.LONG


class FloatOptionVar(OptionVar):
    """optionVar object that manipulates a ``float`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = float
    _SETTER_FLAG = 'floatValue'
    _TYPE = cgp_maya_utils.constants.OptionVarType.FLOAT


class StringOptionVar(OptionVar):
    """optionVar object that manipulates a ``string`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = str
    _SETTER_FLAG = 'stringValue'
    _TYPE = cgp_maya_utils.constants.OptionVarType.STRING


class UnicodeOptionVar(StringOptionVar):
    """optionVar object that manipulates a ``unicode`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = unicode
    _TYPE = cgp_maya_utils.constants.OptionVarType.UNICODE


class ArrayOptionVar(OptionVar):
    """optionVar object that manipulates any kind of array optionVar
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.OptionVarType.ARRAY

    # COMMANDS #

    def appendValue(self, value):
        """append the value at the end of the array

        :param value: The value to append to the array
        :type value: any
        """

        # execute
        super(ArrayOptionVar, self).setValue(value)

    def clear(self):
        """clear the array of the optionVar
        """

        # execute
        maya.cmds.optionVar(clearArray=self._name)

    def setValue(self, value):
        """set the value of the optionVar

        :param value: The value to set on the optionVar
        :type value: any
        """

        # setting optionVars is slow to execute - speed up by skipping already correct values
        if value == self.value():
            return

        # make sur the data to set matches the correct type to avoid Maya crashes or userPrefs.mel file corruption
        if not isinstance(value, list) or not isinstance(value[0], self._DATA_TYPE):
            expected = 'list[{}]'.format(self._DATA_TYPE.__name__)
            given = 'list[{}]'.format(type(value[0]).__name__) if isinstance(value, list) else type(value).__name__
            raise TypeError('Unable to set {} value: '
                            '{} expected, {} given'.format(self.__class__.__name__, expected, given))

        # clear the array
        self.clear()

        # fill the array
        for subValue in value:
            self.appendValue(subValue)

    def size(self):
        """get the size of optionVar's array

        :return: the size of the optionVar's array
        :rtype: int
        """

        # return
        return maya.cmds.optionVar(arraySize=self._name)


class IntArrayOptionVar(ArrayOptionVar):
    """optionVar object that manipulates an ``intArray`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = int
    _SETTER_FLAG = 'intValueAppend'
    _TYPE = cgp_maya_utils.constants.OptionVarType.INT_ARRAY


class LongArrayOptionVar(IntArrayOptionVar):
    """optionVar object that manipulates a ``longArray`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = long
    _TYPE = cgp_maya_utils.constants.OptionVarType.LONG_ARRAY


class FloatArrayOptionVar(ArrayOptionVar):
    """optionVar object that manipulates a ``floatArray`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = float
    _SETTER_FLAG = 'floatValueAppend'
    _TYPE = cgp_maya_utils.constants.OptionVarType.FLOAT_ARRAY


class StringArrayOptionVar(ArrayOptionVar):
    """optionVar object that manipulates a ``stringArray`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = str
    _SETTER_FLAG = 'stringValueAppend'
    _TYPE = cgp_maya_utils.constants.OptionVarType.STRING_ARRAY


class UnicodeArrayOptionVar(StringArrayOptionVar):
    """optionVar object that manipulates a ``unicodeArray`` optionVar
    """

    # ATTRIBUTES #

    _DATA_TYPE = unicode
    _TYPE = cgp_maya_utils.constants.OptionVarType.UNICODE_ARRAY
