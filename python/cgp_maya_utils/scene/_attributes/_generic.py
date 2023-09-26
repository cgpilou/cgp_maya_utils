"""
generic attribute object library
"""

# imports third-parties
import maya.cmds

# import local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api


# GENERIC OBJECTS #


class Attribute(object):
    """attribute object that manipulates any kind of attribute
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.AttributeType.ATTRIBUTE

    # INIT #

    def __init__(self, fullName):
        """Attribute class initialization

        :param fullName: full name of the attribute - ``node.attribute``
        :type fullName: str
        """

        # ensure we use long attribute names
        self._fullName = self._longNameFromFullName(fullName)

    def __eq__(self, attribute):
        """check if the Attribute is identical to the other attribute

        :param attribute: attribute to compare the attribute to
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`

        :return: ``True`` : attributes are identical - ``False`` : attributes are different
        :rtype: bool
        """

        # init
        fullName = attribute.fullName() if isinstance(attribute, Attribute) else self._longNameFromFullName(attribute)

        # return
        return self.fullName() == fullName

    def __ne__(self, attribute):
        """check if the Attribute is different to the other attribute

        :param attribute: attribute to compare the attribute to
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`

        :return: ``True`` : attributes are different - ``False`` : attributes are identical
        :rtype: bool
        """

        # init
        fullName = attribute.fullName() if isinstance(attribute, Attribute) else self._longNameFromFullName(attribute)

        # return
        return self.fullName() != fullName

    def __repr__(self):
        """get the representation of the attribute

        :return: the representation of the attribute
        :rtype: str
        """

        # return
        return '{0}(\'{1}\')'.format(self.__class__.__name__, self.fullName())

    def __str__(self):
        """get the string representation of the attribute

        :return: the string representation the attribute
        :rtype: str
        """

        # return
        return self.fullName()

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, node, name, value=None, connectionSource=None, connectionDestinations=None, **__):
        """create an attribute

        :param node: node on which to create the attribute
        :type node: str

        :param name: name of the attribute to create
        :type name: str

        :param value: value to set on the attribute
        :type value: int or bool

        :param connectionSource: attribute to connect as source - ``node.attribute``
        :type connectionSource: str or :class:`cgp_maya_utils.scene.Attribute`

        :param connectionDestinations: attributes to connect as destination - ``[node1.attrib1, node2.attrib2 ...]``
        :type connectionDestinations: list[str] or list[:class:`cgp_maya_utils.scene.Attribute`]

        :return: the created attribute
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # execute
        try:
            maya.cmds.addAttr(node, longName=name, attributeType=cls._TYPE)
        except RuntimeError:
            maya.cmds.addAttr(node, longName=name, dataType=cls._TYPE)

        # get attribute object
        attrObject = cls('{0}.{1}'.format(node, name))

        # set if value specified
        if value is not None and attrObject.isSettable():
            attrObject.setValue(value)

        # connect attribute
        attrObject.connect(source=connectionSource, destinations=connectionDestinations)

        # return
        return attrObject

    # COMMANDS #

    def animKeys(self, animLayers=None, animLayersIncluded=True):
        """get the existing animKeys on the attribute

        :param animLayers: the animLayers to get the animKeys from - all if nothing is specified
        :type animLayers: list[:class:`cgp_maya_utils.scene.AnimLayer`]

        :param animLayersIncluded: ``True`` : the anim layers will be included -
                                   ``False`` : the anim layers will be excluded
        :type animLayersIncluded: bool

        :return: the existing animKeys
        :rtype: list[:class:`cgp_maya_utils.scene.AnimKey`]
        """

        # init
        keys = []
        affectedLayers = self.animLayers()

        # apply anim layers filters
        if animLayers:
            if animLayersIncluded:
                animLayers = [layer for layer in animLayers if layer in affectedLayers]
            else:
                animLayers = [layer for layer in affectedLayers if layer not in animLayers]
        else:
            animLayers = affectedLayers

        # parse layers
        for layer in animLayers:

            # bypass non keyed layers
            if not self.isKeyed(animLayers=[layer]):
                continue

            # get the correct AnimKey identifier
            identifier = cgp_maya_utils.scene._api._MISC_TYPES['animKey']._getAnimKeyIdentifier(self, layer)

            # get animation keys on layer
            for frame in maya.cmds.keyframe(identifier, query=True, timeChange=True) or []:
                keys.append(cgp_maya_utils.scene._api.animKey(self, frame, layer))

        # return found keys
        return keys

    def animLayers(self):
        """get the animLayers associated to the current attribute

        :return: the associated animLayers
        :rtype: list [:class:`cgp_maya_utils.scene.AbstractAnimLayer`]
        """

        # query the associated anim layers
        affectedLayers = maya.cmds.animLayer([self.fullName()], query=True, affectedLayers=True) or []

        # if the attribute is not associated to any layer, it is still associated to the 'None' anim layer
        if not affectedLayers:
            return [cgp_maya_utils.scene._api.animLayer(None)]

        # return AnimLayer instances
        return [cgp_maya_utils.scene._api.animLayer(affectedLayer) for affectedLayer in affectedLayers]

    def attributeType(self):
        """get the type of the attribute

        :return: the type of the attribute
        :rtype: str
        """

        # execute
        return maya.cmds.getAttr(self.fullName(), type=True)

    def connect(self, source=None, destinations=None):
        """connect the attribute to the source and destinations

        :param source: source attribute to connect to the attribute - ``node.attribute`` or ``Attribute``
        :type source: str or :class:`cgp_maya_utils.scene.Attribute`

        :param destinations: destination attributes to connect to the attribute - ``[node1.attribute1 ...]`` or ``[Attribute1 ...]``
        :type destinations: list[str] or list[:class:`cgp_maya_utils.scene.Attribute`]
        """

        # source
        if source:

            # check if connected
            isConnected = maya.cmds.isConnected(str(source), self.fullName())

            # connect attribute if necessary
            if not isConnected:
                maya.cmds.connectAttr(str(source), self.fullName(), force=True)

        # destinations
        if destinations:
            for destination in destinations:

                # check if connected
                isConnected = maya.cmds.isConnected(self.fullName(), str(destination))

                # connect attribute if necessary
                if not isConnected:
                    maya.cmds.connectAttr(self.fullName(), str(destination), force=True)

    def connections(self,
                    nodeTypes=None,
                    source=True,
                    destinations=True,
                    nodeTypesIncluded=True,
                    skipConversionNodes=False):
        """get the connections of the attribute

        :param nodeTypes: the types of nodes used to get the connections - All if nothing is specified
        :type nodeTypes: list[str]

        :param source: ``True`` : the command will get the source connection -
                       ``False`` : the command won't get the source connection
        :type source: bool

        :param destinations: ``True`` : the command will get the destination connections -
                             ``False`` : the command won't get the destination connections
        :type destinations: bool

        :param nodeTypesIncluded: ``True`` : nodeTypes are included -
                                  ``False`` : nodeTypes are excluded
        :type nodeTypesIncluded: bool

        :param skipConversionNodes: ``True`` : conversion nodes are skipped -
                                    ``False`` : conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the connections of the attribute
        :rtype: list[:class:`cgp_maya_utils.scene.Connection`]
        """

        # return
        return cgp_maya_utils.scene._api.getConnections(str(self.node()),
                                                        attributes=[self.name()],
                                                        sources=source,
                                                        destinations=destinations,
                                                        nodeTypes=nodeTypes,
                                                        nodeTypesIncluded=nodeTypesIncluded,
                                                        skipConversionNodes=skipConversionNodes)

    def data(self, skipConversionNodes=True):
        """get the data necessary to store the compound attribute on disk and/or recreate it from scratch

        :param skipConversionNodes: ``True`` : conversion nodes are skipped -
                                    ``False`` : conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the data of the attribute
        :rtype: dict
        """

        # get connections
        sourceConnections = self.connections(source=True,
                                             destinations=False,
                                             skipConversionNodes=skipConversionNodes)

        destinationConnections = self.connections(source=False,
                                                  destinations=True,
                                                  skipConversionNodes=skipConversionNodes)

        # return
        return {'connectionSource': sourceConnections[0].source().fullName() if sourceConnections else None,
                'connectionDestinations': [connection.destination().fullName() for connection in destinationConnections],
                'name': self.name(),
                'node': self.node().fullName(),
                'attributeType': self.attributeType(),
                'value': self.value()}

    def defaultValue(self):
        """get the default value of the attribute

        :return: the default value of the attribute
        :rtype: any
        """

        # return
        return maya.cmds.addAttr(self.fullName(), query=True, defaultValue=True)

    def delete(self):
        """delete the attribute
        """

        # execute
        maya.cmds.deleteAttr(self.fullName())

    def disconnect(self, source=True, destinations=True, destinationAttributes=None):
        """disconnect the attribute from the source and the specified destinations

        :param source: ``True`` : the connected source attribute will be disconnected -
                       ``False`` : the connected source attribute won't be disconnected
        :type source: bool

        :param destinations: ``True`` : the connected destination attributes will be disconnected -
                       ``False`` : the connected destination attributes won't be disconnected
        :type destinations: bool

        :param destinationAttributes: destination attributes to disconnect from the attribute - All if None is specified
        :type destinationAttributes: list
        """

        # source connection
        if source:

            # get connections
            connections = self.connections(source=True, destinations=False)

            # disconnect connections
            for connection in connections:
                connection.disconnect()

        # destination connections
        if destinations:

            # get connections
            connections = self.connections(source=False, destinations=True)

            # filter connections
            destinationConnections = (connections
                                      if not destinationAttributes
                                      else [connection
                                            for connection in connections
                                            if connection.destination().fullName() in destinationAttributes])

            # disconnect connections
            for connection in destinationConnections:
                connection.disconnect()

    def fullName(self):
        """get the full name of the attribute

        :return: the full name of the attribute - ``node.attribute``
        :rtype: str
        """

        # return
        return self._fullName

    def isInternal(self):
        """check if the attribute is internal - internal attributes may not allow some operations

        :return: ``True`` : attribute is internal - ``False`` : attribute is not internal
        :rtype: bool
        """

        # return
        return maya.cmds.attributeQuery(self.uniqueName(),
                                        node=self._nodeNameFromFullName(self.fullName()),
                                        internal=True)

    def isAnimatable(self):
        """check if the attribute is animatable (ie keyable and displayed in the channelBox)

        :return: ``True`` : the attribute is animatable - ``False`` : the attribute is not animatable
        :rtype: bool
        """

        # get animatable attributes
        animatableAttributes = [attribute.split('|')[-1]
                                for attribute in maya.cmds.listAnimatable(self.node().fullName()) or []]

        # return
        return self.fullName() in animatableAttributes

    def isKeyed(self, animLayers=None):
        """check if the attribute is keyed

        :param animLayers: the animation layers to parse
        :type animLayers: list[:class:`cgp_maya_utils.scene.AnimLayer`]

        :return: ``True`` : the attribute is keyed - ``False`` : the attribute is not keyed
        :rtype: bool
        """

        # init
        affectedLayers = self.animLayers()
        animLayers = [layer for layer in animLayers if layer in affectedLayers] if animLayers else affectedLayers

        # for each layers
        for layer in animLayers:
            isNoneLayer = layer.isNoneLayer()

            # for the None layer, we check if the key count with the current attribute
            if isNoneLayer and maya.cmds.keyframe(self, query=True, keyframeCount=True):
                return True

            # for base/generic layers we check if a curve is associated to the current attribute
            if not isNoneLayer and maya.cmds.animLayer(layer.name(), query=True, findCurveForPlug=self):
                return True

        # return False by default
        return False

    def isLocked(self):
        """check if the attribute is locked

        :return: ``True`` : the attribute is locked - ``False`` : the attribute is not locked
        :rtype: bool
        """

        # return
        return maya.cmds.getAttr(self.fullName(), lock=True)

    def isGettable(self):
        """check if the attribute value is gettable - (an attribute is gettable if it is displayable and readable)

        :return: ``True`` : the attribute is gettable - ``False`` : the attribute is not gettable
        :rtype: bool
        """

        # init
        nodeName = self._nodeNameFromFullName(self.fullName())

        if not self._isDisplayable():
            return False

        # check if the attribute is readable
        if not maya.cmds.attributeQuery(self.uniqueName(), node=nodeName, readable=True):
            return False

        # if none of the above filters have been triggered, the attribute is gettable
        return True

    def isMulti(self):
        """check if the attribute is multi (multi attributes have index based children)

        :return: ``True`` : the attribute is a multi - ``False`` : the attribute is not a multi
        :rtype: bool
        """

        # return
        return maya.cmds.attributeQuery(self.uniqueName(), node=self._nodeNameFromFullName(self.fullName()), multi=True)

    def isSettable(self):
        """check if the attribute value can be set - (an attribute is settable if it is not locked, not connected,
        writable and not having a non-settable type)

        :return: ``True`` the attribute is settable - ``False`` : the attribute is not settable
        :rtype: bool
        """

        # init
        nodeName = self._nodeNameFromFullName(self.fullName())

        # check if the attribute is locked or connected
        if not maya.cmds.getAttr(self.fullName(), settable=True):
            return False

        # check if the attribute is writable
        if not maya.cmds.attributeQuery(self.uniqueName(), node=nodeName, writable=True):
            return False

        # check attribute type
        if self.attributeType() in [None] + cgp_maya_utils.constants.AttributeType.NON_SETTABLES:
            return False

        # if none of the above filters have been triggered, the attribute is settable
        return True

    def isUserDefined(self):
        """check if the attribute is user defined

        :return: ``True`` : it is user defined - ``False`` : it is not user defined
        :rtype: bool
        """

        # return
        return self.name() in (maya.cmds.listAttr(self.node(), userDefined=True) or [])

    def indexes(self):
        """get the multi indexes of the attribute

        :return: the indexes
        :rtype: list[int]
        """

        # non multi attribute don't have indexes
        if not self.isMulti():
            return []

        # return
        return [int(index) for index in maya.cmds.getAttr(self.fullName(), multiIndices=True) or []]

    def MPlug(self):
        """get the MPlug of the attribute

        :return: the open maya api MPlug
        :rtype: :class:`maya.api.OpenMaya.MPlug`
        """

        # return
        return self.node().MFn().findPlug(self.uniqueName(), True)

    def name(self):
        """get the name of the attribute

        :return: the name of the attribute
        :rtype: str
        """

        # return
        return self.fullName().partition('.')[-1]

    def node(self):
        """get the node of the attribute

        :return: the node on which the attribute exists
        :rtype: :class:`cgp_maya_utils.scene.Node`
        """

        # return
        return cgp_maya_utils.scene._api.node(self._nodeNameFromFullName(self.fullName()))

    def parent(self):
        """get the parent attribute of the attribute

        :return: the parent attribute
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # init
        fullName = self.fullName()
        nodeName = self._nodeNameFromFullName(fullName)
        attributeName = fullName.rsplit('.', 1)[-1]

        # get parent name
        if attributeName.count('[') > 1:
            parentName = attributeName.rsplit('[', 1)[0]
            parentFullName = '{}.{}'.format(nodeName, parentName)
        else:
            parentNames = maya.cmds.attributeQuery(self.uniqueName(), node=nodeName, listParent=True)
            parentFullName = '{}.{}'.format(nodeName, parentNames[0]) if parentNames else None

        # return
        return cgp_maya_utils.scene._api.attribute(parentFullName) if parentFullName else None

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

        :param inWeight: the in tangent weight
        :type inWeight: float

        :param outAngle: the out tangent angle
        :type outAngle: float

        :param outTangentType: type of the outTangent of the animKey
        :type outTangentType: :class:`cgp_maya_utils.constants.TangentType`

        :param outWeight: the out tangent weight
        :param outWeight: float

        :return: the created animKey
        :rtype: :class:`cgp_maya_utils.scene.AnimKey`
        """

        # init
        value = self.value() if value is None else value

        # generate the key
        return cgp_maya_utils.scene.AnimKey.create(self,
                                                   frame=frame,
                                                   animLayer=animLayer,
                                                   value=value,
                                                   inAngle=inAngle,
                                                   inTangentType=inTangentType,
                                                   inWeight=inWeight,
                                                   outAngle=outAngle,
                                                   outTangentType=outTangentType,
                                                   outWeight=outWeight)

    def setLock(self, isLocked):
        """set the lock state of the attribute

        :param isLocked: ``True`` : the attribute is locked - ``False`` : the attribute is unlocked
        :type isLocked: bool
        """

        # execute
        maya.cmds.setAttr(self.fullName(), lock=isLocked)

    def setName(self, name):
        """set the name of the attribute

        :param name: new name of the attribute
        :type name: str
        """

        # rename attribute
        newName = maya.cmds.renameAttr(self.fullName(), name)

        # update fullname
        self._fullName = '{0}.{1}'.format(self._fullName.split('.')[0], newName)

    def setValue(self, value):
        """set the value on the attribute

        :param value: value to set on the attribute
        :type value: any
        """

        # execute
        try:
            maya.cmds.setAttr(self.fullName(), value)
        except RuntimeError:
            maya.cmds.setAttr(self.fullName(), value, type=self.attributeType())

    def uniqueName(self):
        """get the unique name of the attribute

        note 1: this name is the one expected by `maya.cmds.attributeQuery` to identify the attribute
        note 2: a TdataCompound attribute may have multiple components using same unique names
                but in this case they all follow the same definition so the results of `maya.cmds.attributeQuery`
                will be consistent

        :return: the unique name of the attribute
        :rtype: str
        """

        # return
        return self._uniqueNameFromFullName(self.fullName())

    def value(self):
        """get the value of the attribute

        :return: the value of the attribute
        :rtype: any
        """

        # non displayable attributes will print this noisy non-blocking error message
        # "Error: The data is not a numeric or string value, and cannot be displayed."
        # but they will return `None` anyway so we can speed-up the process by bypassing the maya query
        return maya.cmds.getAttr(self.fullName()) if self._isDisplayable() else None

    # PROTECTED COMMANDS #

    def _isDisplayable(self):
        """check if the attribute is displayable - displayable attributes are the attributes
        that will be accepted by `maya.cmds.getAttr` to query value

        :return: ``True`` : the attribute is displayable - ``False`` : the attribute is not displayable
        :rtype: bool
        """

        # get all displayable attribute classes
        displayables = tuple([cls for name, cls in cgp_maya_utils.scene._api._ATTRIBUTE_TYPES.items()
                              if name in cgp_maya_utils.constants.AttributeType.DISPLAYABLES])

        # check if current class is in the displayable ones
        return isinstance(self, displayables)

    @staticmethod
    def _longNameFromFullName(fullName):
        """get the long full name of an attribute from its full name

        :param fullName: the full name of the attribute
        :type fullName: str

        :return: the long full name of the attribute
        :rtype: str
        """

        # init
        nameParts = fullName.split('.')

        # handle nested attributes by querying long name of each name parts
        for index, namePart in enumerate(nameParts):

            # the first part is the node name, we bypass it
            if not index:
                continue

            # get long name
            nameParts[index] = maya.cmds.attributeName('.'.join(nameParts[:index + 1]), long=True)

        # store the full name
        return '.'.join(nameParts)

    @staticmethod
    def _nodeNameFromFullName(fullName):
        """get the name of the node holding the attribute from the attribute's full name

        :param fullName: the full name of the attribute
        :type fullName: str

        :return: the name of the node holding the attribute
        :rtype: str
        """

        # return
        return fullName.split('.', 1)[0]

    @staticmethod
    def _uniqueNameFromFullName(fullName):
        """get the unique name of the attribute from its full name

        :param fullName: the full name of the attribute
        :type fullName: str

        :return: the unique name of the attribute
        :rtype: str
        """

        # keep only last name part and remove potential index
        return fullName.rsplit('.', 1)[-1].split('[', 1)[0]
