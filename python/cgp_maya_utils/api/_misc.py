"""
miscellaneous api objects
"""

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants


class AnimKey(object):
    """animation key object that manipulates a key of an animCurve stored in an animCurve node
    """

    # INIT #

    def __init__(self, node, frame, value):
        """AnimKey class initialization

        :param node: animCurve node where the animation key exists
        :type node: str or :class:`cgp_maya_utils.scene.Node`

        :param frame: frame of the animation key
        :type frame: float

        :param value: value of the animation key
        :type value: float
        """

        # init
        self._node = str(node)
        self._frame = frame
        self._value = value

    def __repr__(self):
        """the representation of the animation key

        :return: the representation of the animation key
        :rtype: str
        """

        # return
        return "{0}('{1}', '{2}', '{3}')".format(self.__class__.__name__, self._node, self._frame, self._value)

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, node, frame=None, value=None, inTangentType=None, outTangentType=None, **__):
        """create an animation key

        :param node: animCurve node where the animation key exists
        :type node: str or :class:`cgp_maya_utils.scene.Node`

        :param frame: frame of the animation key - currentFrame if Nothing specified
        :type frame: float

        :param value: value of the animation key - key is inserted if nothing is specified
        :type value: float

        :param inTangentType: inTangent type of the animation key -
                              default is ``cgp_maya_utils.constants.TangentType.AUTO``
        :type inTangentType: str

        :param outTangentType: outTangent type of the animation key -
                               default is ``cgp_maya_utils.constants.TangentType.AUTO``
        :type outTangentType: str

        :return: the created animation key
        :rtype: :class:`cgp_maya_utils.api.AnimKey`
        """

        # init
        frame = frame or maya.cmds.currentTime(query=True)
        inTangentType = inTangentType or cgp_maya_utils.constants.TangentType.AUTO
        outTangentType = outTangentType or cgp_maya_utils.constants.TangentType.AUTO

        # errors
        for tangentType in [inTangentType, outTangentType]:
            if tangentType not in cgp_maya_utils.constants.TangentType.ALL:
                raise ValueError('{0} is not a valid tangent type - {1}'
                                 .format(tangentType, cgp_maya_utils.constants.TangentType.ALL))

        # set key
        if value is None:
            maya.cmds.setKeyframe(str(node),
                                  time=frame,
                                  i=True)
        else:
            maya.cmds.setKeyframe(str(node),
                                  time=frame,
                                  value=value,
                                  itt=inTangentType,
                                  ott=outTangentType)

        # return
        return cls(node, frame, value)

    # COMMANDS #

    def data(self):
        """data necessary to store the animation key on disk and/or recreate it from scratch

        :return: the data of the animation key
        :rtype: dict
        """

        # return
        return {'frame': self.frame(),
                'inTangentType': self.inTangentType(),
                'node': self._node,
                'outTangentType': self.outTangentType(),
                'value': self.value()}

    def inTangentType(self):
        """the inTangent type of the animation key

        :return: the inTangent type of the animation key
        :rtype: str
        """

        # return
        return maya.cmds.keyTangent(self._node,
                                    query=True,
                                    inTangentType=True,
                                    time=(self.frame(), self.frame()))[0]

    def frame(self):
        """the frame of the animation key

        :return: the frame of the animation key
        :rtype: float
        """

        # return
        return self._frame

    def outTangentType(self):
        """the outTangent type of the animation key

        :return: the outTangent type of the animation key
        :rtype: str
        """

        # return
        return maya.cmds.keyTangent(self._node,
                                    query=True,
                                    outTangentType=True,
                                    time=(self.frame(), self.frame()))[0]

    def value(self):
        """the value of the animation key

        :return: the value of the animation key
        :rtype: float
        """

        # return
        return self._value
