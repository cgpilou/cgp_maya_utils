"""
compound attribute object library
"""

# imports python
import re

# imports third-parties
import maya.cmds
import cgp_generic_utils.constants

# imports rodeo
import cgp_generic_utils.decorators

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api
from . import _generic


# BASE OBJECT #


class CompoundAttribute(_generic.Attribute):
    """attribute object that manipulates any kind of compound attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = NotImplemented
    _CHILDREN_TYPE = NotImplemented
    _TYPE = cgp_maya_utils.constants.AttributeType.COMPOUND

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, node, name, components=None, value=None, connectionSource=None, connectionDestinations=None, **__):
        """create a compound attribute

        :param node: node on which to create the attribute
        :type node: str

        :param name: name of the attribute to create
        :type name: str

        :param components: components used to create the attribute - default is Axe.ALL
        :type components: list[any]

        :param value: value to set on the attribute
        :type value: list[any]

        :param connectionSource: attribute to connect as source - ``node.attribute``
        :type connectionSource: str or :class:`cgp_maya_utils.scene.Attribute`

        :param connectionDestinations: attributes to connect as destination - ``[node1.attrib1, node2.attrib2 ...]``
        :type connectionDestinations: list[str] or list[:class:`cgp_maya_utils.scene.Attribute`]

        :return: the created attribute
        :rtype: :class:`cgp_maya_utils.scene.CompoundAttribute`
        """

        # init
        components = components or [{'name': axis} for axis in cgp_generic_utils.constants.Axe.ALL]

        # execute
        try:
            maya.cmds.addAttr(node, longName=name, attributeType=cls._TYPE)
        except RuntimeError:
            maya.cmds.addAttr(node, longName=name, dataType=cls._TYPE)

        # create components
        for component in components:
            try:
                maya.cmds.addAttr(node, longName=component['name'], parent=name, attributeType=cls._CHILDREN_TYPE)
            except RuntimeError:
                maya.cmds.addAttr(node, longName=component['name'], parent=name, dataType=cls._CHILDREN_TYPE)

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

    def animKeys(self, animLayers=None, animLayersIncluded=True):
        """get the existing animKeys on the attribute

        :param animLayers: the animation layers to parse
        :type animLayers: list[:class:`cgp_maya_utils.scene.AnimLayer`]

        :param animLayersIncluded: ``True`` : the animLayers will be included -
                                   ``False`` : the animLayers will be excluded
        :type animLayersIncluded: bool

        :return: the keys
        :rtype: list[:class:`cgp_maya_utils.scene.AnimKey`]
        """

        # the compound attribute keys are located on its components
        return [key for child in self.children(isRecursive=False)
                for key in child.animKeys(animLayers=animLayers, animLayersIncluded=animLayersIncluded)]
    
    def children(self, isRecursive=False):
        """get the children of the attribute

        :param isRecursive: ``True`` : get all descendants - ``False`` : get direct children only
        :type isRecursive: bool

        :return: the children of the attribute
        :rtype: list[:class:`cgp_maya_utils.scene.Attribute`]
        """
        
        # a TDataCompound attribute can be nested so we use the default behavior
        if isinstance(self, TdataCompoundAttribute):
            return super(CompoundAttribute, self).children()
        
        # a non TDataCompound attribute can't be nested
        # so we can bypass the recursion system and get directly the components
        return [cgp_maya_utils.scene._api.attribute(self.MPlug().child(index))
                for index in range(self._CHILDREN_COUNT)]

    def data(self, skipConversionNodes=True):
        """get the data necessary to store the compound attribute on disk and/or recreate it from scratch

        :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the data of the attribute
        :rtype: dict
        """

        # init
        data = super(CompoundAttribute, self).data(skipConversionNodes=skipConversionNodes)

        # update data
        data['components'] = [child.data() for child in self.children(isRecursive=False)]

        # return
        return data

    def isAnimatable(self):
        """check if the attribute is animatable (ie keyable and displayed in the channelBox)

        :return: ``True`` : the attribute is animatable - ``False`` : the attribute is not animatable
        :rtype: bool
        """

        # parse components
        for child in self.children(isRecursive=False):

            # return
            if not child.isAnimatable():
                return False

        # return
        return True

    def isKeyed(self, animLayers=None):
        """check if the attribute is keyed/animated

        :param animLayers: the animation layers to parse
        :type animLayers: list[:class:`cgp_maya_utils.scene.AnimLayer`]

        :return: ``True`` : the attribute is keyed/animated -  ``False`` : the attribute is not keyed/animated
        :rtype: bool
        """

        # a compound attribute is keyed if one of its components is keyed
        for child in self.children(isRecursive=False):
            if child.isKeyed(animLayers=animLayers):
                return True

        # return
        return False

    def setAnimKey(self,
                   frame=None,
                   animLayer=None,
                   value=None,
                   isInserted=False,
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
        :type value: float or list

        :param isInserted: ``True`` : the animKey is inserted - ``False`` : the animKey is not inserted
        :type isInserted: bool

        :param inAngle: the in tangent angle
        :type inAngle: float

        :param inTangentType: type of the inTangent of the animKey
        :type inTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param inWeight: the in tangent weight
        :type inWeight: float

        :param outAngle: the out tangent angle
        :type outAngle: float

        :param outTangentType: type of the outTangent of the animKey
        :type outTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param outWeight: the out tangent weight
        :param outWeight: float

        :return: the created animKey
        :rtype: list[:class:`cgp_maya_utils.scene.AnimKey`]
        """

        # init
        keys = []

        # key each components
        for index, child in enumerate(self.children(isRecursive=False)):
            keys.append(child.setAnimKey(frame=frame,
                                         animLayer=animLayer,
                                         value=value[index] if isinstance(value, (list, tuple)) else value,
                                         inAngle=inAngle,
                                         inTangentType=inTangentType,
                                         inWeight=inWeight,
                                         outAngle=outAngle,
                                         outTangentType=outTangentType,
                                         outWeight=outWeight))

        # return
        return keys

    def setValue(self, value):
        """set the value on the attribute

        :param value: value to set on the attribute
        :type value: any
        """

        # validate the attribute is settable
        if not self.isSettable():

            # if the attribute type is the problem, alert the user
            type_ = self.attributeType()
            if type_ in cgp_maya_utils.constants.AttributeType.NON_SETTABLES:
                raise RuntimeError("The attributes of type '{}' are not settable: {}".format(type_, self))

            # otherwise tell the user the attribute is in a non-settable state
            raise RuntimeError("The attribute '{}' is not settable (locked, connected or not writable)".format(self))

        # try to set all the components values at once
        try:
            maya.cmds.setAttr(self.fullName(), *value, type=self.attributeType())

        # if not possible, apply values component by component
        except RuntimeError:
            for index, child in enumerate(self.children(isRecursive=False)):
                if child.isSettable():
                    child.setValue(value[index])

    def size(self):
        """get the size of the attribute (number of components)

        :return: the size of the attribute
        :rtype: int
        """

        # return
        return maya.cmds.getAttr(self.fullName(), size=True)

    def value(self):
        """get the value of the attribute

        :return: the value of the attribute
        :rtype: any
        """

        # return
        return [child.value() for child in self.children()]


# COMPOUND ATTRIBUTES #


class Double2Attribute(CompoundAttribute):
    """attribute object that manipulates ``double2`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 2
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.DOUBLE
    _TYPE = cgp_maya_utils.constants.AttributeType.DOUBLE2


class Double3Attribute(CompoundAttribute):
    """attribute object that manipulates ``double3`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 3
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.DOUBLE
    _TYPE = cgp_maya_utils.constants.AttributeType.DOUBLE3


class Double4Attribute(CompoundAttribute):
    """attribute object that manipulates ``double4`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 4
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.DOUBLE
    _TYPE = cgp_maya_utils.constants.AttributeType.DOUBLE4


class Float2Attribute(CompoundAttribute):
    """attribute object that manipulates ``float2`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 2
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.FLOAT
    _TYPE = cgp_maya_utils.constants.AttributeType.FLOAT2


class Float3Attribute(CompoundAttribute):
    """attribute object that manipulates ``float3`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 3
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.FLOAT
    _TYPE = cgp_maya_utils.constants.AttributeType.FLOAT3


class Float4Attribute(CompoundAttribute):
    """attribute object that manipulates ``float4`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 4
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.FLOAT
    _TYPE = cgp_maya_utils.constants.AttributeType.FLOAT4


class Long2Attribute(CompoundAttribute):
    """attribute object that manipulates ``long2`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 2
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.LONG
    _TYPE = cgp_maya_utils.constants.AttributeType.LONG2


class Long3Attribute(CompoundAttribute):
    """attribute object that manipulates ``long3`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 3
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.LONG
    _TYPE = cgp_maya_utils.constants.AttributeType.LONG3


class Long4Attribute(CompoundAttribute):
    """attribute object that manipulates ``long4`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 4
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.LONG
    _TYPE = cgp_maya_utils.constants.AttributeType.LONG4


class Short2Attribute(CompoundAttribute):
    """attribute object that manipulates ``short2`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 2
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.SHORT
    _TYPE = cgp_maya_utils.constants.AttributeType.SHORT2


class Short3Attribute(CompoundAttribute):
    """attribute object that manipulates ``short3`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 3
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.SHORT
    _TYPE = cgp_maya_utils.constants.AttributeType.SHORT3


class Short4Attribute(CompoundAttribute):
    """attribute object that manipulates ``short4`` attribute
    """

    # ATTRIBUTES #

    _CHILDREN_COUNT = 4
    _CHILDREN_TYPE = cgp_maya_utils.constants.AttributeType.SHORT
    _TYPE = cgp_maya_utils.constants.AttributeType.SHORT4


class TdataCompoundAttribute(CompoundAttribute):
    """attribute object that manipulates ``TDataCompound`` attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.TDATACOMPOUND

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, node, name, **__):
        """create a TdataCompound attribute

        note: nested TdataCompound can't be created via `maya.cmds.addAttr`
              the values are not settables
              the connections are not settables

        :param node: node on which to create the attribute
        :type node: str

        :param name: name of the attribute to create
        :type name: str

        :return: the created attribute
        :rtype: :class:`cgp_maya_utils.scene.CompoundAttribute`
        """

        # execute
        maya.cmds.addAttr(node, longName=name, dataType=cls._TYPE)

        # get attribute object
        attrObject = cls('{0}.{1}'.format(node, name))

        # return
        return attrObject

    # COMMANDS #

    def value(self):
        """get the value of the attribute

        :return: the value of the attribute
        :rtype: list[any]
        """

        # try the regular ways (for un-nested TDataCompounds)
        try:
            return maya.cmds.getAttr(self.fullName())

        # try to get the component values one by one (for nested TDataCompounds)
        except RuntimeError:
            return [child.value() for child in self.children(isRecursive=False)]
