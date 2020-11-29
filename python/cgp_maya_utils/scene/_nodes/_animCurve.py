"""
animation curve object library
"""

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.api
from . import _generic


# BASE OBJECTS #


class AnimCurve(_generic.Node):
    """node object that manipulates any kind of animation curve node
    """

    # ATTRIBUTES #

    _nodeType = 'animCurve'

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, keys=None, drivenAttributes=None, attributeValues=None, name=None, connections=None, **__):
        """create an animation curve node

        :param keys: keys defining the profile of the animation curve - ``[AnimKey1.data(), AnimKey2.data() ...]``
        :type keys: list[dict]

        :param drivenAttributes: attributes driven by the animation curve node
        :type drivenAttributes: list[str]

        :param attributeValues: attribute values to set on the animation curve node
        :type attributeValues: dict

        :param name: name of the animation curve node
        :type name: str

        :param connections: connections to set on the animation curve node
        :type connections: list[tuple]

        :return: the animation curve object
        :rtype: :class:`cgp_maya_utils.scene.AnimCurve`
        """

        # init
        keys = keys or []
        drivenAttributes = drivenAttributes or []
        name = name or '{0}_{1}'.format(*drivenAttributes[0].split('.')) if drivenAttributes else cls._nodeType

        # create node
        node = maya.cmds.createNode(cls._nodeType, name=name)

        # get animCurve object
        animCurveObject = cls(node)

        # create keys
        for key in keys:
            animCurveObject.addAnimKey(**key)

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

    def data(self):
        """data necessary to store the animation curve node on disk and/or recreate it from scratch

        :return: the data of the animation curve
        :rtype: dict
        """

        # init
        data = super(AnimCurve, self).data()

        # update data
        data['drivenAttributes'] = [attribute.fullName() for attribute in self.drivenAttributes()]
        data['keys'] = [key.data() for key in self.keys()]

        # return
        return data

    def drivenAttributes(self):
        """the attributes driven by the anim curve node

        :return: the driven attributes
        :rtype: list[:class:`cgp_maya_utils.scene.Attribute`]
        """

        # get connections
        connections = self.attribute('output').connections(source=False, destinations=True, skipConversionNodes=True)

        # return
        return [connection.destination() for connection in connections]

    def keys(self):
        """the animation keys of the animation curve node

        :return: the animation keys
        :rtype: list[:class:`cgp_maya_utils.api.AnimKey`]
        """

        # init
        animKeys = []

        # get infos
        keyFrames = maya.cmds.keyframe(self.name(), query=True, timeChange=True)
        keyValues = maya.cmds.keyframe(self.name(), query=True, valueChange=True)

        for keyFrame, keyValue in zip(keyFrames, keyValues):
            animKeys.append(cgp_maya_utils.api.AnimKey(self.name(), keyFrame, keyValue))

        # return
        return animKeys

    def addAnimKey(self, frame=None, value=None, inTangentType=None, outTangentType=None, **__):
        """add an animation key on the animation curve

        :param frame: frame of the animation key - current frame if None is specified
        :type frame: float

        :param value: value of the animation key - key will be inserted if None is specified
        :type value: float

        :param inTangentType: type of the inTangent of the animation key - default is ``cgp_maya_utils.constants.TangentType.AUTO``
        :type inTangentType: str

        :param outTangentType: type of the outTangent of the animation key - - default is ``cgp_maya_utils.constants.TangentType.AUTO``
        :type outTangentType: str

        :return: the added animation key
        :rtype: :class:`cgp_maya_utils.api.AnimKey`
        """

        # return
        return cgp_maya_utils.api.AnimKey.create(self.name(),
                                                 frame=frame,
                                                 value=value,
                                                 inTangentType=inTangentType,
                                                 outTangentType=outTangentType)

    # PRIVATE COMMANDS #

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(AnimCurve, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['input',
                                    'preInfinity',
                                    'postInfinity',
                                    'useCurveColor'])

        # return
        return availableAttributes


# ANIMCURVE OBJECTS #


class AnimCurveTA(AnimCurve):
    """node object that manipulates an ``animCurveTA`` animation curve node
    """

    # ATTRIBUTES #

    _nodeType = 'animCurveTA'


class AnimCurveTL(AnimCurve):
    """node object that manipulates an ``animCurveTL`` animation curve node
    """

    # ATTRIBUTES #

    _nodeType = 'animCurveTL'


class AnimCurveTU(AnimCurve):
    """node object that manipulates an ``animCurveTU`` animation curve node
    """

    # ATTRIBUTES #

    _nodeType = 'animCurveTU'
