"""
generic attribute object library
"""

# imports python
import re

# imports third-parties
import maya.cmds
import maya.api.OpenMaya

# import local
import cgp_maya_utils.constants
import cgp_maya_utils.api
import cgp_maya_utils.scene._api


# GENERIC OBJECTS #


class Attribute(object):
    """attribute object that manipulates any kind of attribute
    """

    # ATTRIBUTES #

    _MPLUG_VALUE_GETTER = None  # name of the MPlug getter - eg: "asFloat" for `maya.api.OpenMaya.MPlug.asFloat()`
    _TYPE = cgp_maya_utils.constants.AttributeType.ATTRIBUTE

    # INIT #

    def __init__(self, attribute):
        """Attribute class initialization

        :param attribute: the MPlug of the attribute or its full name - ``node.attribute``
        :type attribute: str or :class:`maya.api.OpenMaya.MPlug`
        """

        # init MPlug
        self._mPlug = attribute if isinstance(attribute, maya.api.OpenMaya.MPlug) else self._plugFromFullName(attribute)

        # init MFnNode
        mObject = self._mPlug.node()
        self._mfnNode = (maya.api.OpenMaya.MFnDagNode(mObject)
                         if mObject.hasFn(maya.api.OpenMaya.MFn.kDagNode)
                         else maya.api.OpenMaya.MFnDependencyNode(mObject))

    def __eq__(self, attribute):
        """check if the Attribute is identical to the other attribute

        :param attribute: attribute to compare the attribute to
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`

        :return: ``True`` : attributes are identical - ``False`` : attributes are different
        :rtype: bool
        """

        # init
        plug = attribute.MPlug() if isinstance(attribute, Attribute) else self._plugFromFullName(attribute)

        # return
        return self.MPlug() == plug

    def __ne__(self, attribute):
        """check if the Attribute is different to the other attribute

        :param attribute: attribute to compare the attribute to
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`

        :return: ``True`` : attributes are different - ``False`` : attributes are identical
        :rtype: bool
        """

        # init
        plug = attribute.MPlug() if isinstance(attribute, Attribute) else self._plugFromFullName(attribute)

        # return
        return self.MPlug() != plug

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
        return self._typeFromPlug(self.MPlug())

    def children(self, isRecursive=False):
        """get the children of the attribute

        :param isRecursive: ``True`` : get all descendants - ``False`` : get direct children only
        :type isRecursive: bool

        :return: the children of the attribute
        :rtype: list[:class:`cgp_maya_utils.scene.Attribute`]
        """

        # init
        plug = self.MPlug()

        # get children of multi attributes
        children = maya.cmds.getAttr(self.fullName(), multiIndices=True) or []
        if children:
            children = [cgp_maya_utils.scene._api.attribute(plug.elementByLogicalIndex(int(index)))
                        for index in children]

        # get children of compound attributes
        else:
            try:
                count = plug.numChildren()
            except TypeError:
                count = 0
            children = [cgp_maya_utils.scene._api.attribute(plug.child(index)) for index in range(count)]

        # get sub children if needed
        if isRecursive:
            for child in children:
                children += child.children(isRecursive=True)

        # return
        return children

    def connect(self, source=None, destinations=None):
        """connect the attribute to the source and destinations

        :param source: source attribute to connect to the attribute - ``node.attribute`` or ``Attribute``
        :type source: str or :class:`cgp_maya_utils.scene.Attribute`

        :param destinations: destination attributes to connect to the attribute - ``[node1.attribute1 ...]`` or ``[Attribute1 ...]``
        :type destinations: list[str] or list[:class:`cgp_maya_utils.scene.Attribute`]
        """

        # init
        fullName = self.fullName()

        # source
        if source:

            # check if connected
            isConnected = maya.cmds.isConnected(str(source), fullName)

            # connect attribute if necessary
            if not isConnected:
                maya.cmds.connectAttr(str(source), fullName, force=True)

        # destinations
        if destinations:
            for destination in destinations:

                # check if connected
                isConnected = maya.cmds.isConnected(fullName, str(destination))

                # connect attribute if necessary
                if not isConnected:
                    maya.cmds.connectAttr(fullName, str(destination), force=True)

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
                'node': self.node().name(),
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

        # init
        node = self._nodeName()
        attributeWithParents = self.MPlug().partialName(includeNodeName=False,
                                                        includeNonMandatoryIndices=True,
                                                        useLongNames=True)

        # return
        return '{}.{}'.format(node, attributeWithParents)

    def isInternal(self):
        """check if the attribute is internal - internal attributes may not allow some operations

        :return: ``True`` : attribute is internal - ``False`` : attribute is not internal
        :rtype: bool
        """

        # return
        return maya.cmds.attributeQuery(self.uniqueName(), node=self._nodeName(), internal=True)

    def isAnimatable(self):
        """check if the attribute is animatable (ie keyable and displayed in the channelBox)

        :return: ``True`` : the attribute is animatable - ``False`` : the attribute is not animatable
        :rtype: bool
        """

        # init
        nodeName = self._nodeName()

        # get animatable attributes
        animatableAttributes = [attribute.split('|')[-1] for attribute in maya.cmds.listAnimatable(nodeName) or []]

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

        if not self._isDisplayable():
            return False

        # check if the attribute is readable
        if not maya.cmds.attributeQuery(self.uniqueName(), node=self._nodeName(), readable=True):
            return False

        # if none of the above filters have been triggered, the attribute is gettable
        return True

    def isMulti(self):
        """check if the attribute is multi (multi attributes have index based children)

        :return: ``True`` : the attribute is a multi - ``False`` : the attribute is not a multi
        :rtype: bool
        """

        # return
        return maya.cmds.attributeQuery(self.uniqueName(), node=self._nodeName(), multi=True)

    def isProxy(self):
        """check if the attribute is a proxy or another one

        :return: ``True`` : the attribute is a proxy - ``False`` : the attribute is not a proxy
        :rtype: bool
        """

        # init
        fullName = self.fullName()

        # check if the attribute is used as a proxy
        isProxy = self.isUserDefined() and maya.cmds.addAttr(fullName, query=True, usedAsProxy=True)

        # if it is a proxy, we need to check if it is connected, otherwise the proxy is corrupted and can't be queried
        if isProxy and not maya.cmds.listConnections(fullName, source=True, destination=False):
            raise RuntimeError('Corrupted proxy attribute: {} '
                               '(a proxy attribute must be connected to a source attribute)'.format(fullName))

        # return
        return isProxy

    def isSettable(self):
        """check if the attribute value can be set - (an attribute is settable if it is not locked, not connected,
        writable and not having a non-settable type)

        :return: ``True`` the attribute is settable - ``False`` : the attribute is not settable
        :rtype: bool
        """

        # check if the attribute is locked or connected
        if not maya.cmds.getAttr(self.fullName(), settable=True):
            return False

        # check if the attribute is writable
        if not maya.cmds.attributeQuery(self.uniqueName(), node=self._nodeName(), writable=True):
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

    def isVisible(self):
        """check if the attribute is visible

        :return: ``True`` : the attribute is visible - ``False`` : the attribute is hidden
        :rtype: bool
        """

        # init
        nodeName, attributeName = self.fullName().split('.', 1)

        # return
        return attributeName not in maya.cmds.attributeInfo(nodeName, hidden=True)

    def MPlug(self):
        """get the MPlug of the attribute

        :return: the open maya api MPlug
        :rtype: :class:`maya.api.OpenMaya.MPlug`
        """

        # return
        return self._mPlug

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
        return cgp_maya_utils.scene._api.node(self._nodeName())

    def parent(self):
        """get the parent attribute of the attribute

        :return: the parent attribute
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # init
        fullName = self.fullName()
        nodeName = self._nodeName()
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

        # execute
        maya.cmds.renameAttr(self.fullName(), name)

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

        # init
        name = self.fullName().rpartition('.')[-1]

        # return
        return name.partition('[')[0] if '[' in name else name

    def value(self):
        """get the value of the attribute

        :return: the value of the attribute
        :rtype: any
        """

        # corrupted proxy attributes break the value query
        try:

            # speed up by using MPlug if possible
            if self._MPLUG_VALUE_GETTER:
                return getattr(self.MPlug(), self._MPLUG_VALUE_GETTER)()

            # return
            return maya.cmds.getAttr(self.fullName(), silent=True)

        # we check if it is a corrupted proxy
        except RuntimeError as error:
            self.isProxy()
            raise error

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

    def _nodeName(self):
        """get the name of the node containing the attribute

        :return: the name of the node containing the attribute
        :rtype: str
        """

        # return
        return (self._mfnNode.partialPathName()
                if isinstance(self._mfnNode, maya.api.OpenMaya.MFnDagNode)
                else self._mfnNode.name())

    @staticmethod
    def _plugFromFullName(fullName):
        """get the MPlug object from the given attribute full name

        :param fullName: full name of the attribute - ``node.attribute``
        :type fullName: str

        :return: the open maya api MPlug
        :rtype: :class:`maya.api.OpenMaya.MPlug`
        """

        # init
        nameParts = fullName.split('.')

        # get the mfn node
        mayaObject = cgp_maya_utils.api.MayaObject(nameParts[0])
        mfnNode = maya.api.OpenMaya.MFnDependencyNode().setObject(mayaObject)

        # find plug
        attributePlug = None
        for name in nameParts[1:]:

            # split attribute name and child index
            indexes = [int(index)
                       for match in re.finditer(r'\[(-?[0-9]+)]', name)
                       for index in match.groups()]
            if indexes:
                name = name.split('[', 1)[0]

            # find plug
            if not attributePlug:

                try:
                    attributePlug = mfnNode.findPlug(name, True)
                except RuntimeError as error:
                    if not mfnNode.hasAttribute(name):
                        raise ValueError('No attribute named "{}" on node: {}'.format(name, nameParts[0]))
                    raise error

            # find sub plug
            else:
                isSubAttributeFound = False
                for subIndex in range(attributePlug.numChildren()):
                    subPlug = attributePlug.child(subIndex)

                    # try with long name
                    subName = subPlug.partialName(includeNodeName=False, useLongNames=True).rsplit('.', 1)[-1]
                    if name == subName:
                        attributePlug = subPlug
                        isSubAttributeFound = True
                        break

                    # try with short name
                    subName = subPlug.partialName(includeNodeName=False, useLongNames=False).rsplit('.', 1)[-1]
                    if name == subName:
                        attributePlug = subPlug
                        isSubAttributeFound = True
                        break

                if not isSubAttributeFound:
                    raise ValueError('No attribute named "{}" under parent attribute: {}'.format(name, attributePlug))

            # find child from parent
            for index in indexes:
                if index == -1:
                    break
                attributePlug = attributePlug.elementByLogicalIndex(index)

        # return
        return attributePlug

    @staticmethod
    def _typeFromFullName(fullName):
        """get the type  of an attribute

        :param fullName: full name of the attribute - ``node.attribute``
        :type fullName: str

        :return: the attribute type
        :rtype: :class:`cgp_maya_utils.constants.AttributeType`
        """

        # return
        return Attribute._typeFromPlug(Attribute._plugFromFullName(fullName))

    @staticmethod
    def _typeFromPlug(attributePlug):
        """get the attribute type of an attribute plug

        note1: this command goal is to avoid using `maya.cmds.getAttr(fullName, type=True)`
               which is more precise but very slow to execute

        note2: the open maya api that does not handle correctly the TDataCompound attributes (or their children)
               so we still need few `maya.cmds.getAttr(fullName, type=True)` in specific cases

        :param attributePlug: the MPlug of the attribute
        :type attributePlug: :class:`maya.api.OpenMaya.MPlug`

        :return: the attribute type
        :rtype: :class:`cgp_maya_utils.constants.AttributeType`
        """

        # get mfn attribute
        attributeObject = attributePlug.attribute()
        mfnAttribute = maya.api.OpenMaya.MFnAttribute(attributeObject)

        # get attribute creation command
        command = mfnAttribute.getAddAttrCmd(longFlags=True)

        # get type from command
        type_ = re.search(r'-(?:attribute|data)Type \"([a-zA-Z0-9]+)\"', command).group(1)

        # unnested compound attributes are created with types like `float2`, `double3`, `long4`, `short2`
        # the `compound` type means TDataCompound
        if type_ == cgp_maya_utils.constants.AttributeType.COMPOUND:
            return cgp_maya_utils.constants.AttributeType.TDATACOMPOUND

        # a multi attribute could be a TDataCompound
        # we list here the types we are sure they are not TDataCompound
        regularMultiTypes = [cgp_maya_utils.constants.AttributeType.MATRIX,
                             cgp_maya_utils.constants.AttributeType.MESSAGE,
                             cgp_maya_utils.constants.AttributeType.MESH]

        # check for multi TDataCompound
        if '-multi ' in command and type_ not in regularMultiTypes:
            try:
                attributePlug.elementByLogicalIndex(0)
                return cgp_maya_utils.constants.AttributeType.TDATACOMPOUND
            except TypeError:
                return maya.cmds.getAttr(str(attributePlug), type=True)

        # return
        return type_
