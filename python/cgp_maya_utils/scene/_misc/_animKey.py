"""
animKey object library
"""

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.decorators
import cgp_maya_utils.scene._api


# ANIM KEY OBJECT #


class AnimKey(object):
    """animKey object that manipulates an animKey
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.MiscType.ANIM_KEY

    # INIT #

    def __init__(self, attribute, frame, animLayer=None):
        """AnimKey class initialization

        :param attribute: attribute associated to the animKey
        :type attribute: :class:`cgp_maya_utils.scene.Attribute`

        :param frame: frame of the animKey
        :type frame: float

        :param animLayer: the animation layer containing the key
        :type animLayer: :class:`cgp_maya_utils.scene.AnimLayer`
        """

        # init
        self._attribute = attribute
        self._frame = frame
        self._animLayer = animLayer or cgp_maya_utils.scene._api.animLayer(animLayer)
        self._identifier = self._getAnimKeyIdentifier(self._attribute, self._animLayer)

    def __repr__(self):
        """get the representation of the animKey

        :return: the representation of the animKey
        :rtype: str
        """

        # return
        return "{0}('{1}', '{2}', '{3}')".format(self.__class__.__name__,
                                                 self._attribute,
                                                 self._frame,
                                                 self._animLayer.name())

    # OBJECT COMMANDS #

    @classmethod
    def create(cls,
               attribute,
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
        """create  an animKey

        :param attribute: attribute associated to the animKey
        :type attribute: :class:`cgp_maya_utils.scene.Attribute`

        :param frame: frame of the animKey - default is current frame
        :type frame: float

        :param animLayer: the animation layer to create the animKey on - default is current animation layer
        :type animLayer: :class:`cgp_maya_utils.scene.AnimLayer`

        :param value: value of the animKey - key is inserted if nothing is specified
        :type value: float

        :param inAngle: the in tangent angle of the animKey
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

        # init
        frame = frame or cgp_maya_utils.scene._api.scene().currentTime()
        animLayer = animLayer or cgp_maya_utils.scene._api.animLayer(None)
        flags = {'time': frame, 'insert': True} if value is None else {'time': frame, 'value': value}

        # validate the given anim layer
        if animLayer not in attribute.animLayers():
            if not animLayer.isBaseLayer():
                raise ValueError("Unable to create key at frame {} "
                                 "because {} is not a member of {}".format(frame, attribute, animLayer))
            # for BaseAnimation, we can fallback on None layer
            animLayer = cgp_maya_utils.scene._api.animLayer(None)

        # add the anim layer to the maya command flags
        if not animLayer.isNoneLayer():
            flags['animLayer'] = animLayer.name()

        # create the key in Maya
        maya.cmds.setKeyframe(str(attribute), **flags)

        # create the AnimKey instance
        instance = cls(attribute, frame, animLayer=animLayer)

        # set tangent values
        instance.setTangentValues(inAngle=inAngle,
                                  inTangentType=inTangentType,
                                  inWeight=inWeight,
                                  outAngle=outAngle,
                                  outTangentType=outTangentType,
                                  outWeight=outWeight)

        # return
        return instance

    # COMMANDS #

    def attribute(self):
        """get the attribute associated with the animKey

        :return: the attribute associated to the animKey
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # return
        return self._attribute

    def animLayer(self):
        """get the animation layer associated with the animKey

        :return: the animation layer associated to the animKey
        :rtype: :class:`cgp_maya_utils.scene.AnimLayer`
        """

        # return
        return self._animLayer

    def data(self):
        """get the data necessary to store the animKey on disk and/or recreate it from scratch

        :return: the data of the animKey
        :rtype: dict
        """

        # get base data
        data = {'attribute': self.attribute(),
                'frame': self.frame(),
                'animLayer': self.animLayer(),
                'value': self.value()}

        # get tangent data
        data.update(self.tangentValues())

        # return
        return data

    def delete(self):
        """delete the animKey
        """

        # delete the key
        maya.cmds.cutKey(self._identifier,
                         time=(self.frame(), self.frame()),
                         clear=True)

        # force dependency graph evaluation to avoid maya crashes
        maya.cmds.dgeval(self.attribute())

    def inAngle(self):
        """get the inTangent angle of the animKey

        :return: the inTangent angle of the animKey
        :rtype: float
        """

        # query the inTangent angle
        result = maya.cmds.keyTangent(self._identifier,
                                      time=(self.frame(), self.frame()),
                                      query=True,
                                      inAngle=True)

        # return
        return result[0] if result else None

    def inTangentType(self):
        """get the inTangent type of the animKey

        :return: the inTangent type of the animKey
        :rtype: :class:`cgp_maya_utils.constants.TangentType`
        """

        # query the inTangent type
        result = maya.cmds.keyTangent(self._identifier,
                                      time=(self.frame(), self.frame()),
                                      query=True,
                                      inTangentType=True)

        # return
        return result[0] if result else None

    def inWeight(self):
        """get the inTangent weight of the animKey

        :return: the inTangent weight of the animKey
        :rtype: float
        """

        # query the inTangent weight
        result = maya.cmds.keyTangent(self._identifier,
                                      time=(self.frame(), self.frame()),
                                      query=True,
                                      inWeight=True)

        # return
        return result[0] if result else None

    def frame(self):
        """get the frame of the animKey

        :return: the frame of the animKey
        :rtype: float
        """

        # return
        return self._frame

    def outAngle(self):
        """get the outTangent angle of the animKey

        :return: the outTangent angle of the animKey
        :rtype: float
        """

        # query the outTangent angle
        result = maya.cmds.keyTangent(self._identifier,
                                      time=(self.frame(), self.frame()),
                                      query=True,
                                      outAngle=True)

        # return
        return result[0] if result else None

    def outTangentType(self):
        """get the outTangent type of the animKey

        :return: the outTangent type of the animKey
        :rtype: :class:`cgp_maya_utils.constants.TangentType`
        """

        # query the outTangent type
        result = maya.cmds.keyTangent(self._identifier,
                                      time=(self.frame(), self.frame()),
                                      query=True,
                                      outTangentType=True)

        # return
        return result[0] if result else None

    def outWeight(self):
        """get the outTangent weight of the animKey

        :return: the outTangent weight of the animKey
        :rtype: float
        """

        # query the outTangent weight
        result = maya.cmds.keyTangent(self._identifier,
                                      time=(self.frame(), self.frame()),
                                      query=True,
                                      outWeight=True)

        # return
        return result[0] if result else None

    def setFrame(self, frame):
        """set the frame of the animKey

        :param frame: the frame to set on the animKey
        :type frame: float
        """

        # move the AnimKey
        maya.cmds.keyframe(self._identifier,
                           time=(self.frame(), self.frame()),
                           edit=True,
                           option="move",
                           absolute=True,
                           timeChange=frame)

        # store the new frame number
        self._frame = frame

    def setInAngle(self, angle):
        """set the inTangent angle of the animKey

        :param angle: the inTangent angle to set on the animKey
        :type: float
        """

        # update the inTangent angle
        maya.cmds.keyTangent(self._identifier,
                             time=(self.frame(), self.frame()),
                             edit=True,
                             inAngle=angle)

    def setInTangentType(self, tangentType):
        """set the inTangent type of the animKey

        :param tangentType: The inTangent type to set on the animKey
        :type tangentType: class:`cgp_maya_utils.constants.TangentType`
        """

        # validate the given value
        if tangentType not in cgp_maya_utils.constants.TangentType.ALL:
            raise ValueError('{0} is not a valid tangent type - {1}'
                             .format(tangentType, cgp_maya_utils.constants.TangentType.ALL))

        # update the inTangent type
        maya.cmds.keyTangent(self._identifier,
                             time=(self.frame(), self.frame()),
                             edit=True,
                             inTangentType=tangentType)

    def setInWeight(self, weight):
        """set the inTangent weight of the animKey

        :param weight: the inTangent weight to set on the animKey
        :type: float
        """

        # update the inTangent weight
        maya.cmds.keyTangent(self._identifier,
                             time=(self.frame(), self.frame()),
                             edit=True,
                             inWeight=weight)

    def setOutAngle(self, angle):
        """set the outTangent angle of the animKey

        :param angle: the outTangent angle to set on the animKey
        :type: float
        """

        # update the outTangent angle
        maya.cmds.keyTangent(self._identifier,
                             time=(self.frame(), self.frame()),
                             edit=True,
                             outAngle=angle)

    def setOutTangentType(self, tangentType):
        """set the outTangent type of the animKey

        :param tangentType: The outTangent type to set on the animKey
        :type tangentType: class:`cgp_maya_utils.constants.TangentType`
        """

        # validate the given value
        if tangentType not in cgp_maya_utils.constants.TangentType.ALL:
            raise ValueError('{0} is not a valid tangent type - {1}'
                             .format(tangentType, cgp_maya_utils.constants.TangentType.ALL))

        # update the outTangent type
        maya.cmds.keyTangent(self._identifier,
                             time=(self.frame(), self.frame()),
                             edit=True,
                             outTangentType=tangentType)

    def setOutWeight(self, weight):
        """set the outTangent weight of the animKey

        :param weight: the outTangent weight to set on the animKey
        :type: float
        """

        # update the outTangent weight
        maya.cmds.keyTangent(self._identifier,
                             time=(self.frame(), self.frame()),
                             edit=True,
                             outWeight=weight)

    def setTangentValues(self,
                         inAngle=None,
                         inTangentType=None,
                         inWeight=None,
                         outAngle=None,
                         outTangentType=None,
                         outWeight=None):
        """set the tangent values of the AnimKeys

        ::param inAngle: the angle of the inTangent
        :type inAngle: float

        :param inTangentType: type of the inTangent of the animKey
        :type inTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param inWeight: the weight of the inTangent
        :type inWeight: float

        :param outAngle: the angle of the outTangent
        :type outAngle: float

        :param outTangentType: type of the outTangent of the animKey
        :type outTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param outWeight: the weight of the outTangent
        :param outWeight: float
        """

        # set tangent types
        if inTangentType is not None:
            self.setInTangentType(inTangentType)

        if outTangentType is not None:
            self.setOutTangentType(outTangentType)

        # init flags
        flags = {}

        # set in angle/weight (except for step tangents)
        if self.inTangentType() not in cgp_maya_utils.constants.TangentType.STEPS:
            if inAngle is not None:
                flags["inAngle"] = inAngle
            if inWeight is not None:
                flags["inWeight"] = inWeight

        # set out angle/weight (except for step tangents)
        if self.outTangentType() not in cgp_maya_utils.constants.TangentType.STEPS:
            if outAngle is not None:
                flags["outAngle"] = outAngle
            if outWeight is not None:
                flags["outWeight"] = outWeight

        # set all the values at once to speed up the process
        if flags:
            maya.cmds.keyTangent(self._identifier,
                                 time=(self.frame(), self.frame()),
                                 edit=True,
                                 **flags)

    def setValue(self, value):
        """set the value of the animKey

        :param value: value to set on the animKey
        :type value: float
        """

        # update the animKey value
        maya.cmds.keyframe(self._identifier,
                           time=(self.frame(), self.frame()),
                           edit=True,
                           absolute=True,
                           valueChange=value)

    def tangentValues(self):
        """get the tangent values of the AnimKey

        :return: the tangent values of the animKey - {'inAngle': 1.0, 'outAngle': 1.0,
                                                      'inWeight': 1.0, 'outWeight': 1.0,
                                                      'inTangentType': 'spline', 'outTangentType': 'spline'}
        :rtype: dict
        """

        # query all values at the same time to speed up the process
        values = maya.cmds.keyTangent(self._identifier,
                                      time=(self.frame(), self.frame()),
                                      query=True,
                                      inAngle=True,
                                      inTangentType=True,
                                      inWeight=True,
                                      outAngle=True,
                                      outTangentType=True,
                                      outWeight=True)

        # return
        return {"inAngle": values[0],
                "outAngle": values[1],
                "inWeight": values[2],
                "outWeight": values[3],
                "inTangentType": values[4],
                "outTangentType": values[5]}

    def value(self):
        """get the value of the animKey

        :return: the value of the animKey
        :rtype: float
        """

        # query the animKey value
        value = maya.cmds.keyframe(self._identifier,
                                   time=(self.frame(), self.frame()),
                                   query=True,
                                   valueChange=True)

        # return
        return None if value is None else value[0]

    # PRIVATE COMMANDS #

    @staticmethod
    def _getAnimKeyIdentifier(attribute, animLayer):
        """get the animation key identifier for the given attribute and animation layer

        Note: Maya allows us to identify an anim key using its animation curve name, or using its attribute name.
              An 'animCurve/animLayer' couple is unique whereas an attribute can be keyed on multiple layers.
              We obviously prefer the 'animCurve/animLayer' couple option. And for base/generic layers we can easily
              get this couple. But the `maya.cmds.animLayer` does not support the None layer.
              For this specific case we can identify the anim key using its attribute name.
              Because an attribute member of the None layer can't be member of another layer.

        :param attribute: attribute associated to the animKey
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`

        :param animLayer: the animation layer containing the animKey
        :type animLayer: :class:`cgp_maya_utils.scene.AnimLayer`

        :return: the identifier
        :rtype: str
        """

        # None layer case
        if animLayer.isNoneLayer():
            return str(attribute)

        # Base/generic layers case
        curves = maya.cmds.animLayer(animLayer.name(), query=True, findCurveForPlug=attribute)

        if not curves:
            raise RuntimeError("Unable to identify animation. The attribute '{}' is not keyed on {}."
                               .format(attribute, animLayer))

        # return the curve
        return curves[0]
