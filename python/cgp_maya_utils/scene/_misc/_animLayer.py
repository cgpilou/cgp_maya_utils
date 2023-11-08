"""
animLayer library
"""

# imports third-parties
import maya.cmds
import maya.mel

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.decorators
import cgp_maya_utils.scene._api


# ANIM LAYER OBJECTS #


class AnimLayer(object):
    """animLayer object that manipulates an animLayer

    Note about the 'None' animation layer :
        This class also represent the 'None' anim layer which is not a proper Maya node but can handle most of the
        animLayer node features and can also contains anim keys for attributes not associated to any animLayer node.
        For each new implemented command we need to check if a specific behavior is needed for the None layer.

    Note about the BaseAnimation layer :
        "[The BaseAnimation] is not an animation layer, but is there to represent the non-layered animation."
            - Maya 2020 official documentation.
        More specifically it contains all attributes that are at least on one animLayer which is not None.
        So, for this case, some flags of the `maya.cmds.animLayer` command will not always work as expected.
        For each new implemented command we need to check if a specific behavior is needed for the BaseAnimation layer.

    Note about the multiple layers selection :
        Maya technically allows multiple layers to be active at the same time.
        But the None layer is active when no other layer is active.
        So we can't activate the None layer alongside base/generic layers.
        We restrict this behavior here to only have one active layer at a time.
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.MiscType.ANIM_LAYER

    # INIT #

    def __init__(self, node=None):
        """AnimLayer class initialization

        :param node: the node the AnimLayer is associated to
        :type node: :class:`cgp_maya_utils.scene.Node`
        """

        # init
        self._node = node

    def __eq__(self, other):
        """check if the animLayer is identical to the other animLayer

        :param other: animLayer to compare the animLayer to
        :type other: :class:`cgp_maya_utils.scene.AnimLayer`

        :return: ``True`` : animLayers are identical - ``False`` : animLayers are different
        :rtype: bool
        """

        # return
        return self.node() == other.node()

    def __ne__(self, other):
        """check if the animLayer is different from the other animLayer

        :param other: animLayer to compare the animLayer to
        :type other: str or :class:`cgp_maya_utils.scene.AnimLayer`

        :return: ``True`` : animLayers are different - ``False`` : animLayers are identical
        :rtype: bool
        """

        # return
        return self.node() != other.node()

    def __repr__(self):
        """get the representation of the animLayer

        :return: the representation of the animLayer
        :rtype: str
        """

        # return
        return '{0}({1!r})'.format(self.__class__.__name__, self.name())

    # COMMANDS #

    def addMember(self, attribute):
        """add the given attribute as a member to the animLayer

        :param attribute: the attribute to add as a member
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`
        """

        # None layer case: raise an error
        if self.isNoneLayer():
            raise RuntimeError("Adding member to the None animation layer is not possible. "
                               "An attribute is member of the None animation layer if it is member of no other "
                               "animation layer.")

        # Base layer case: raise an error
        if self.isBaseLayer():
            raise RuntimeError("Adding member to the BaseAnimation layer is not possible. "
                               "An attribute is member of the BaseAnimation layer if it is member "
                               "of at least one animation layer which is not BaseAnimation or None.")

        # Generic layer case
        maya.cmds.animLayer(self.name(), edit=True, attribute=str(attribute))

    def animKeys(self, attributes=None, attributesIncluded=True):
        """get the animKeys associated to the animLayer

        :param attributes: the attributes to get the animKeys from - all if nothing is specified
        :type attributes: list[:class:`cgp_maya_utils.scene.Attribute`] or list[str]

        :param attributesIncluded: ``True`` : attributes are included - ``False`` : attributes are excluded
        :type attributesIncluded: bool

        :return: the animKeys associated to the animLayer
        :rtype: list[:class:`cgp_maya_utils.scene.AnimKey`]
        """

        # apply attributes options
        if attributes is None:
            attributes = self.members(keyed=True)

        elif not attributesIncluded:
            attributes = [member for member in self.members(keyed=True) if member not in attributes]

        # return
        return [key for attribute in attributes for key in attribute.animKeys(animLayers=[self])]

    def animCurves(self):
        """get the animCurves associated to the animLayer

        :return: the animCurves associated to the animLayer
        :rtype: list[:class:`cgp_maya_utils.scene.AnimCurve`]
        """

        # None layer case
        if self.isNoneLayer():

            # list all existing curves
            allCurves = maya.cmds.ls(type=cgp_maya_utils.constants.NodeType.ANIM_CURVE)

            # list curves associated to children layers
            childrenCurves = [curve
                              for layer in self._getAnimLayerNodeNames()
                              for curve in (maya.cmds.animLayer(layer, query=True, animCurves=True) or []) +
                                           (maya.cmds.animLayer(layer, query=True, baseAnimCurves=True) or [])]

            # return curves which are not associated to any child
            return [cgp_maya_utils.scene.node(curve) for curve in allCurves if curve not in childrenCurves]

        # Base layer case: we ask every generic layer what are their baseAnimCurves
        elif self.isBaseLayer():
            layerCurves = [curve
                           for child in self.children(recursive=True)
                           for curve in maya.cmds.animLayer(child.name(), query=True, baseAnimCurves=True) or []]
            layerCurves = list(set(layerCurves))  # remove doubles

        # Generic layer case
        else:
            layerCurves = maya.cmds.animLayer(self.name(), query=True, animCurves=True) or []

        # return AnimCurve instances
        return [cgp_maya_utils.scene.node(curveName) for curveName in layerCurves]

    def children(self, recursive=False):
        """get the children animLayers of the animLayer

        :param recursive: ``True`` : children are got recursively - ``False`` : only direct children are got
        :type recursive: bool

        :return: The children animLayers
        :rtype: list[:class:`AnimLayer`]
        """

        # None layer case: the only possible direct child is the BaseAnimation
        if self.isNoneLayer():
            baseLayerName = maya.cmds.animLayer(query=True, root=True)
            if not baseLayerName:
                return []
            children = [cgp_maya_utils.scene._api.animLayer(baseLayerName)]

        # Generic/Base layer case: we can easily get animLayer direct children
        else:
            children = [cgp_maya_utils.scene._api.animLayer(name)
                        for name in maya.cmds.animLayer(self.name(), query=True, children=True) or []]

        # recurse if needed
        if recursive:
            children += [grandChild for child in children for grandChild in child.children(recursive=True)]

        # return
        return children

    def isActive(self):
        """get the activation state of the animLayer

        :return: ``True`` : the animLayer is active - ``False`` : the animLayer is inactive
        :rtype: bool
        """

        # None layer case: the None layer is active if no other anim layers are actives
        if self.isNoneLayer():
            return len(self._getAnimLayerNodeNames(onlyActive=True)) == 0

        # Generic/Base layer case: we search the current layer name in the currently active layer names
        return self.name() in self._getAnimLayerNodeNames(onlyActive=True)

    def isMember(self, member):
        """check if the item is a member of the animLayer

        :param member: the item to check the membership from - [node or attribute]
        :type member: str or :class:`cgp_maya_utils.scene.Node` or :class:`cgp_maya_utils.scene.Attribute`

        :return: ``True`` : the item is a member of the layer - ``False`` : the item is not a member of the layer
        :rtype: bool
        """

        # None layer case: an attribute is a member of the None layer if it is affected by no other layers
        if self.isNoneLayer():
            return maya.cmds.animLayer([str(member)], query=True, affectedLayers=True) is None

        # Generic/Base layer case
        return self.name() in (maya.cmds.animLayer([str(member)], query=True, affectedLayers=True) or [])

    def isBaseLayer(self):
        """check if the animLayer is the BaseAnimation layer

        :return: ``True`` : the layer is the baseAnimation layer - ``False`` : the layer is not the baseAnimation layer
        :rtype: bool
        """

        # it is base if it's not None and its name match the 'root' name
        return not self.isNoneLayer() and self.name() == maya.cmds.animLayer(query=True, root=True)

    def isNoneLayer(self):
        """check if the animLayer is the None layer

        :return: ``True`` : the layer is the None layer - ``False`` : the layer is not the None layer
        :rtype: bool
        """

        # the current layer is the None layer if it has no associated node
        return self.node() is None

    def members(self, keyed=False):
        """get the members of the animLayer

        :param keyed: ``True`` : command gets only keyed members - ``False`` : command gets all members
        :type keyed: bool

        :return: the members of the animLayer
        :rtype: list[:class:`cgp_maya_utils.scene.Attribute`]
        """

        # None layer case
        if self.isNoneLayer():

            # apply keyed option (for the None layer case it's faster to parse anim curve connections)
            if keyed:
                return [attribute for curve in self.animCurves()
                        for attribute in curve.drivenAttributes(recursive=True) if self.isMember(attribute)]

            # we list all possible member nodes
            excludedNodeTypes = [cgp_maya_utils.constants.NodeType.ANIM_BLEND,
                                 cgp_maya_utils.constants.NodeType.ANIM_LAYER,
                                 cgp_maya_utils.constants.NodeType.ANIM_CURVE]
            nodeNames = maya.cmds.ls(excludeType=excludedNodeTypes) or []

            # then we search for keyable attributes on those nodes
            memberNames = []
            for nodeName in nodeNames:

                # looping over keyable attributes
                for attributeName in maya.cmds.listAttr(nodeName, keyable=True) or []:

                    # generate attribute fullName
                    attributeName = '{}.{}'.format(nodeName, attributeName.split(".")[0])

                    # check membership and keyframe existences, then add to list
                    if attributeName not in memberNames and self.isMember(attributeName):
                        memberNames.append(attributeName)

        # Base layer case
        # maya.cmds.animLayer("BaseAnimation", query=True, attribute=True) -> None
        # but we know that if an attribute is a member of a non-base layer so it is also a member of the base layer
        # so we can list the members of all the non-base layers
        elif self.isBaseLayer():

            # get layer name - query it only once is faster
            layerName = self.name()

            # get non base layers
            nonBaseLayers = [nodeName for nodeName in self._getAnimLayerNodeNames() if nodeName != layerName]

            # get member names
            memberNames = [attributeName
                           for layerName in nonBaseLayers
                           for attributeName in maya.cmds.animLayer(layerName, query=True, attribute=True) or []]

            # remove possible doubles
            memberNames = set(memberNames)

        # Generic layer case
        else:
            memberNames = maya.cmds.animLayer(self.name(), query=True, attribute=True) or []

        # generate attribute objects
        members = [cgp_maya_utils.scene.attribute(name) for name in memberNames]

        # apply keyed option
        if keyed:
            members = [attribute for attribute in members if attribute.isKeyed(animLayers=[self])]

        # return
        return members

    def name(self):
        """get the name of the AnimLayer - the 'None' animLayer has no name

        :return: the name of the animLayer
        :rtype: str or None
        """

        # None layer name is None, the other layers names are their node name
        return None if self.isNoneLayer() else self.node().name()

    def node(self):
        """get the node associated to the animLayer - the 'None' animLayer has no node

        :return: the node associated to the animLayer
        :rtype: :class:`cgp_maya_utils.scene.Node`
        """

        # return
        return self._node

    def removeMembers(self, attributes=None):
        """remove the attributes membership from the animLayer

        NOTE: If the members have animKeys on the current layers they will be deleted.
              If the members have animKeys on the BaseAnimation layer, they will be moved to the 'None' animLayer

        :param attributes: the attributes to remove the membership from - All attributes if nothing is specified
        :type attributes: list[:class:`cgp_maya_utils.scene.Attribute`]
        """

        # None layer case: raise an error
        if self.isNoneLayer():
            raise RuntimeError('removing member from the None layer is not possible')

        # Base layer case: we need to remove membership from all the other animation layers.
        # Generic layer case, we only treat the current layer
        layerNames = self._getAnimLayerNodeNames() if self.isBaseLayer() else [self.name()]
        for layerName in layerNames:

            # if no attributes are given, we remove it all
            if attributes is None:
                maya.cmds.animLayer(layerName, edit=True, removeAllAttributes=True)

            # remove attribute per attribute
            else:
                for attribute in attributes:
                    maya.cmds.animLayer(layerName, edit=True, removeAttribute=attribute.fullName())

    def setActive(self):
        """set the animLayer as active
        """

        # disable all unwanted layers
        toActive = self.name()
        for currentName in self._getAnimLayerNodeNames():
            isActive = currentName == toActive
            maya.cmds.animLayer(currentName, edit=True, selected=isActive, preferred=isActive)

        # None layer case: we empty the mel global var
        if self.isNoneLayer():
            maya.mel.eval('global string $gSelectedAnimLayers[];$gSelectedAnimLayers = {};')

        # Generic/Base layer case: we set the current layer to be the only one stored in the mel global var
        else:
            maya.mel.eval('global string $gSelectedAnimLayers[];$gSelectedAnimLayers = {{ \"{}\" }};'.format(toActive))

    # PRIVATE COMMANDS #

    @staticmethod
    def _getAnimLayerNodeNames(onlyActive=False):
        """get the existing animLayer's names

        :param onlyActive: ``True`` : command gets only active animLayer's names -
                           ``False`` : command gets all animLayer's names
        :type onlyActive: bool

        :return: the existing animLayer's names
        :rtype: list[str]
        """

        # querying the mel global var seems to be the fastest way to kow which layers are currently actives
        if onlyActive:
            return maya.mel.eval('$tmp = $gSelectedAnimLayers')

        # recursively querying children layers from the root one seems to be the fastest way to get all animLayer nodes
        baseLayer = maya.cmds.animLayer(query=True, root=True)
        layers = [baseLayer] if baseLayer else []

        # parse non root layers
        count = 0
        while len(layers) > count:
            count = len(layers)
            for layer in layers[count - 1:]:
                layers += maya.cmds.animLayer(layer, query=True, children=True) or []

        # return
        return layers
