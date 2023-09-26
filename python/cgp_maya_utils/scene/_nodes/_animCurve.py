"""
animation curve object library
"""

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.api
import cgp_maya_utils.scene._api
from . import _generic


# BASE OBJECTS #


class AnimCurve(_generic.Node):
    """node object that manipulates any kind of animation curve node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.ANIM_CURVE

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, keys=None, drivenAttributes=None, attributeValues=None, name=None, connections=None, **__):
        """create a animCurve node

        :param keys: keys defining the profile of the anim curve - [AnimKey1.data(), AnimKey2.data() ...]
        :type keys: list[dict]

        :param drivenAttributes: attributes driven by the animCurve node
        :type drivenAttributes: list[str]

        :param attributeValues: attribute values to set on the animCurve node
        :type attributeValues: dict

        :param name: name of the created animCurve
        :type name: str

        :param connections: connections to set on the animCurve node
        :type connections: list[tuple]

        :return: the animCurve object
        :rtype: AnimCurve
        """

        # init
        keys = keys or []
        drivenAttributes = drivenAttributes or []
        name = name or '{0}_{1}'.format(*drivenAttributes[0].split('.')) if drivenAttributes else cls._TYPE

        # create node
        node = maya.cmds.createNode(cls._TYPE, name=name)

        # get animCurve object
        animCurveObject = cls(node)

        # create keys
        for key in keys:
            animCurveObject.setAnimKey(**key)

        # connect driven attributes
        if drivenAttributes:
            animCurveObject.attribute('output').connect(destinations=drivenAttributes)

        # set attribute values
        if attributeValues:
            animCurveObject.setAttributeValues(attributeValues)

        # set connections
        if connections:
            animCurveObject.setConnections(connections)

        # return
        return animCurveObject

    # COMMANDS #

    def animLayer(self):
        """get the animLayer associated to the current animCurve

        :return: the associated animLayer
        :rtype: :class:`cgp_maya_utils.scene.AnimLayer`
        """

        # list all existing layer (except the None layer which can be slower to query)
        layers = cgp_maya_utils.scene.getAnimLayers(noneLayerIncluded=False)

        # return the first driven attribute member of one of theses layers
        for recursive in [False, True]:
            for attribute in self.drivenAttributes(recursive=recursive):
                for layer in layers:
                    if layer.isMember(attribute):
                        return layer

        # and we fallback on None layer without querying it
        return cgp_maya_utils.scene.AnimLayer(node=None)

    def data(self):
        """get the data necessary to store the animCurve node on disk and/or recreate it from scratch

        :return: the data of the animCurve
        :rtype: dict
        """

        # init
        data = super(AnimCurve, self).data()

        # update data
        data['drivenAttributes'] = [attribute.fullName() for attribute in self.drivenAttributes()]
        data['keys'] = [key.data() for key in self.animKeys()]

        # return
        return data

    def drivenAttributes(self, recursive=True):
        """get the attributes driven by the animCurve

        :param recursive: ``True`` : the command passes over nodes such as PairBlend to get the real driven attribute
                          ``False`` : the command returns the directly driven attributes
        :type recursive: bool

        :return: the driven attributes
        :rtype: list[Attribute]
        """

        # TODO: the recursive feature is not working with conversion nodes.
        #       the real use of this feature is not obvious and needs to be clarified. !!! use at your own risk !!!

        # return recursively queried driven attributes
        if recursive:
            return [cgp_maya_utils.scene._api.attribute(destination)
                    for destination in self._recursiveDrivenAttributes(self.attribute('output').fullName())]

        # return driven attribute from direct connections
        return [connection.destination()
                for connection in self.attribute('output').connections(source=False,
                                                                       destinations=True,
                                                                       skipConversionNodes=True)]

    def animKeys(self):
        """get the animKeys of the animCurve

        :return: the animKeys of the animCurve
        :rtype: list[:class:`cgp_maya_utils.scene.AnimKey`]
        """

        # init
        animLayer = self.animLayer()

        # return anim keys
        return [cgp_maya_utils.scene.AnimKey(attribute, frame, animLayer=animLayer)
                for attribute in self.drivenAttributes()
                for frame in maya.cmds.keyframe(self.fullName(), query=True, timeChange=True)]

    def setAnimKey(self,
                   frame=None,
                   animLayer=None,
                   value=None,
                   inAngle=None,
                   inTangentType=None,
                   inWeight=None,
                   outAngle=None,
                   outTangentType=None,
                   outWeight=None,
                   **__):
        """set an animKey on the animCurve

        :param frame: the frame of the animKey - default is current frame
        :type frame: float

        :param animLayer: the animLayer to create the animKey on - default is current animLayer
        :type animLayer: :class:`cgp_maya_utils.scene.AnimLayer`

        :param value: the value of the animKey - key is inserted if nothing is specified
        :type value: float

        :param inAngle: the inTangent angle of the animKey
        :type inAngle: float

        :param inTangentType: the type of the inTangent of the animKey
        :type inTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param inWeight: the inTangent weight of the animKey
        :type inWeight: float

        :param outAngle: the outTangent angle of the animKey
        :type outAngle: float

        :param outTangentType: the type of the outTangent of the animKey
        :type outTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param outWeight: the outTangent weight of the animKey
        :param outWeight: float

        :return: the created AnimKey
        :rtype: list[:class:`cgp_maya_utils.scene.AnimKey`]
        """

        # return
        return [cgp_maya_utils.scene.AnimKey.create(attribute,
                                                    frame=frame,
                                                    animLayer=animLayer,
                                                    value=value,
                                                    inAngle=inAngle,
                                                    inTangentType=inTangentType,
                                                    inWeight=inWeight,
                                                    outAngle=outAngle,
                                                    outTangentType=outTangentType,
                                                    outWeight=outWeight)
                for attribute in self.drivenAttributes()]

    # PROTECTED COMMANDS #

    def _recursiveDrivenAttributes(self, fullName):
        """recursively get the attributes driven by the animCurve

        :param fullName: the starting attribute full name for the recursion
        :type fullName: str

        :return: the driven attributes
        :rtype: list[str]
        """

        # init
        destinations = []
        nodeName, attributeName = fullName.split('.')

        # try to find an output matching with the input (eg: for pairBlend, 'inRotateX1' -> 'outRotateX')
        outputAttributes = []
        if attributeName.startswith('in'):
            outputPattern = 'out' + attributeName.split('in', 1)[-1]
            while outputPattern[-1].isdigit():
                outputPattern = outputPattern[:-1]
            outputPattern += '*'
            outputAttributes = maya.cmds.listAttr(nodeName, string=outputPattern) or []

        # fallback on regular 'output' attributes
        outputAttributes = outputAttributes or maya.cmds.listAttr(nodeName, string='output*') or []

        # for each output attributes
        for output in outputAttributes:

            destinations += maya.cmds.listConnections('{}.{}'.format(nodeName, output),
                                                      source=False,
                                                      destination=True,
                                                      plugs=True) or []

            # recurse on those new destinations
            for destination in destinations:
                destinations += self._recursiveDrivenAttributes(destination)

        # return all destination attributes
        return list(set(destinations))


# ANIMCURVE OBJECTS #


class AnimCurveTA(AnimCurve):
    """node object that manipulates an ``animCurveTA`` animCurve node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.ANIM_CURVE_TA


class AnimCurveTL(AnimCurve):
    """node object that manipulates an ``animCurveTL`` animCurve node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.ANIM_CURVE_TL


class AnimCurveTU(AnimCurve):
    """node object that manipulates an ``animCurveTU`` animCurve node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.ANIM_CURVE_TU
