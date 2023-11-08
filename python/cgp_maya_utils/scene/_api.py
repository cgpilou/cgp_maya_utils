"""
maya scene management functions
"""

# imports python
import re

# imports third-parties
import maya.api.OpenMaya
import maya.cmds

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.api


_ATTRIBUTE_TYPES = {}
_COMPONENT_TYPES = {}
_MISC_TYPES = {}
_NODE_TYPES = {}
_OPTIONVAR_TYPES = {}


# ANIM KEY COMMANDS #


def animKey(attr, frame, layer=None):
    """get the animKey object from an attribute and a frame

    :param attr: attribute associated to the animKey
    :type attr: str or :class:`cgp_maya_utils.scene.Attribute`

    :param frame: frame of the animKey
    :type frame: float

    :param layer: the animLayer containing the animKey
    :type layer: str or :class:`cgp_maya_utils.scene.AnimLayer`

    :return: the animKey object
    :rtype: :class:`cgp_maya_utils.scene.AnimKey`
    """

    # cast params in expected types
    attr = attribute(attr) if isinstance(attr, str) else attr
    layer = animLayer(layer) if isinstance(layer, str) else layer

    # return
    return _MISC_TYPES[cgp_maya_utils.constants.MiscType.ANIM_KEY](attr, frame, layer)


def getAnimKeys(attributes=None,
                frames=None,
                animLayers=None,
                attributesIncluded=True,
                framesIncluded=True,
                animLayersIncluded=True):
    """get the existing animKeys in the scene

    :param attributes: attributes used to get the animKeys - All if nothing is specified
    :type attributes: list[str, :class:`cgp_maya_utils.scene.Attribute`]

    :param frames: frames used to get the animKeys - All if nothing is specified
    :type frames: list[float]

    :param animLayers: animLayers used to get the animKeys - All if nothing is specified
    :type animLayers: list[str or :class:`cgp_maya_utils.scene.AnimLayer`]

    :param attributesIncluded: ``True`` : the attributes will be included - ``False`` : the attributes will be excluded
    :type attributesIncluded: bool

    :param framesIncluded: ``True`` : the frames will be included - ``False`` : the frames will be excluded
    :type framesIncluded: bool

    :param animLayersIncluded: ``True`` : the animLayers will be included - ``False`` :  the animLayers will be excluded
    :type animLayersIncluded: bool

    :return: the animKeys
    :rtype: list[:class:`cgp_maya_utils.scene.AnimKey`]
    """

    # cast param in expected types
    attributes = ([attribute(attr) if isinstance(attr, str) else attr for attr in attributes]
                  if attributes else [])

    # getting keys from Attribute is faster than from AnimLayer so we prioritise this way
    if attributes and attributesIncluded:
        keys = [key
                for attr in attributes
                for key in attr.animKeys(animLayers=animLayers, animLayersIncluded=animLayersIncluded)]

    # get keys from the animation layers
    else:

        # cast param in expected types
        animLayers = ([animLayer(layer) if isinstance(layer, str) else layer for layer in animLayers]
                      if animLayers else getAnimLayers())

        # return keys
        keys = [key
                for layer in animLayers
                for key in layer.animKeys(attributes=attributes or None, attributesIncluded=attributesIncluded)]

    # return all keys
    if not frames:
        return keys

    # return keys inside the given frames
    if framesIncluded:
        return [key for key in keys if key.frame() in frames]

    # return keys outside the given frames
    return [key for key in keys if key.frame() not in frames]


# ANIM LAYER COMMANDS #


def animLayer(layer):
    """get the animLayer object from a layer's name

    :param layer: the name of the animLayer
    :type layer: None or str or :class:`cgp_maya_utils.scene.AnimLayer`

    :return: the animLayer object
    :rtype: :class:`cgp_maya_utils.scene.AnimLayer`
    """

    # cast params in expected types
    layerNode = None if layer is None else node(layer) if isinstance(layer, str) else layer.node()

    # return
    return _MISC_TYPES[cgp_maya_utils.constants.MiscType.ANIM_LAYER](layerNode)


def getAnimLayers(noneLayerIncluded=True, baseLayerIncluded=True, onlyActive=False, onlyInactive=False):
    """get the existing animLayers in the scene

    :param noneLayerIncluded: ``True`` : the None layer is included - ``False`` : the None layer is excluded
    :type noneLayerIncluded: bool

    :param baseLayerIncluded: ``True`` : the Base layer is included - ``False`` : the Base layer is excluded
    :type noneLayerIncluded: bool

    :param onlyActive: ``True`` : only active layers are returned - ``False`` : not only active layers are returned
    :type onlyActive: bool

    :param onlyInactive: ``True`` : only inactive layers are returned - ``False`` : not only inactive layers are returned
    :type onlyInactive: bool

    :return: the existing animLayers
    :rtype: list[:class:`cgp_maya_utils.scene.AnimLayer`]
    """

    # init
    genericType = cgp_maya_utils.constants.MiscType.ANIM_LAYER

    # check params
    if onlyActive and onlyInactive:
        raise ValueError('unable to get only active and only inactive layers at the same time')

    # get layers
    activeLayers = _MISC_TYPES[genericType]._getAnimLayerNodeNames(onlyActive=True)
    baseLayer = maya.cmds.animLayer(query=True, root=True)
    allLayers = activeLayers if onlyActive else _MISC_TYPES[genericType]._getAnimLayerNodeNames()

    # remove base layer if asked to
    if not baseLayerIncluded and baseLayer:
        allLayers = [layer for layer in allLayers if layer != baseLayer]

    # remove inactive layers if asked to
    if onlyInactive:
        allLayers = [layer for layer in allLayers if layer not in activeLayers]

    # add the None layer if asked to
    if noneLayerIncluded:

        # check if none layer is active
        noneIsActive = not activeLayers

        # update allLayers
        if ((not onlyActive and not onlyInactive)
                or (onlyActive and noneIsActive)
                or (onlyInactive and not noneIsActive)):
            allLayers.insert(0, None)

    # return
    return [animLayer(name) for name in allLayers]


# ATTRIBUTE COMMANDS #


def attribute(attribute_):
    """get the attribute object from an attribute full name

    :param attribute_: the MPlug of the attribute or its full name - ``node.attribute``
    :type attribute_: str or :class:`maya.api.OpenMaya.MPlug`

    :return: the attribute object
    :rtype: Attribute
    """

    # init
    genericClass = _ATTRIBUTE_TYPES[cgp_maya_utils.constants.AttributeType.ATTRIBUTE]

    # get plug
    attributePlug = (attribute_
                     if isinstance(attribute_, maya.api.OpenMaya.MPlug)
                     else genericClass._plugFromFullName(attribute_))

    # get type
    attributeType = genericClass._typeFromPlug(attributePlug)

    # return the class associated to the exact type
    attributeClass = _ATTRIBUTE_TYPES.get(attributeType)
    if attributeClass:
        return attributeClass(attributePlug)

    # fallback on generic compound attribute
    if attributeType in cgp_maya_utils.constants.AttributeType.COMPOUNDS:
        return _ATTRIBUTE_TYPES[cgp_maya_utils.constants.AttributeType.COMPOUND](attributePlug)

    # fallback on generic attribute
    return genericClass(attributePlug)


def connection(source, destination):
    """get the connection object representing a connection, live or virtual, between the source and the destination

    :param source: the source of the connection
    :type source: str or :class:`cgp_maya_utils.scene.Attribute`

    :param destination: the destination of the connection
    :type destination: str or :class:`cgp_maya_utils.scene.Attribute`

    :return: the connection object
    :rtype: :class:`cgp_maya_utils.scene.Connection`
    """

    # return
    return _MISC_TYPES[cgp_maya_utils.constants.MiscType.CONNECTION](source, destination)


def getConnections(node_,
                   attributes=None,
                   sources=True,
                   destinations=True,
                   nodeTypes=None,
                   nodeTypesIncluded=True,
                   skipConversionNodes=False):
    """get the connections from the specified node

    :param node_: node to get the connections from
    :type node_: str

    :param attributes: list of attributes to get the connections from - get all if nothing specified
    :type attributes: list[str]

    :param sources: ``True`` : get the source connections - ``False`` : does not get source connections
    :type sources: bool

    :param destinations: ``True`` : get the destination connections - ``False`` : does not get destination connections
    :type destinations: bool

    :param nodeTypes: types of nodes used to get the connections - All if nothing is specified
    :type nodeTypes: list[str]

    :param nodeTypesIncluded: ``True`` : include specified node types - ``False`` : exclude specified node types
    :type nodeTypesIncluded: bool

    :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` : conversion nodes are not skipped
    :type skipConversionNodes: bool

    :return: the connections
    :rtype: list[:class:`cgp_maya_utils.scene.Connection`]
    """

    # init
    toQueries = ['{0}.{1}'.format(node_, attr) for attr in attributes] if attributes else [node_]
    nodeTypes = nodeTypes or []
    data = []

    # get source connections
    sourceConnections = maya.cmds.listConnections(toQueries,
                                                  source=True,
                                                  destination=False,
                                                  plugs=True,
                                                  skipConversionNodes=skipConversionNodes,
                                                  connections=True) or [] if sources else []

    # get destination connections
    destinationConnections = maya.cmds.listConnections(toQueries,
                                                       source=False,
                                                       destination=True,
                                                       plugs=True,
                                                       skipConversionNodes=skipConversionNodes,
                                                       connections=True) or [] if destinations else []

    # sort connections
    sourceConnections = reversed(zip(*[iter(reversed(sourceConnections))] * 2))
    destinationConnections = reversed(zip(*[iter(destinationConnections)] * 2))

    # execute
    for index, connections in enumerate([sourceConnections, destinationConnections]):
        for connection_ in connections:

            # check if not is a connectedType
            isValid = bool(set(maya.cmds.nodeType(connection_[index], inherited=True)) & set(nodeTypes))

            # update
            if (not nodeTypes and nodeTypesIncluded
                    or nodeTypes and nodeTypesIncluded and isValid
                    or nodeTypes and not nodeTypesIncluded and not isValid):
                data.append(connection(*connection_))

    # return
    return data


def createAttribute(data, **extraData):
    """create an attribute using an attribute data dictionary

    :param data: data used to create the attribute
    :type data: dict

    :param extraData: extraData used to update the data before creating the attribute
    :type extraData: any

    :return: the created attribute
    :rtype: Attribute
    """

    # update data
    data.update(extraData)

    # init attribute object
    attributeObject = _ATTRIBUTE_TYPES.get(data['attributeType'], None)

    # errors
    if not attributeObject:
        raise ValueError('{0} Attribute is not implemented'.format(data['attributeType']))

    # return
    return attributeObject.create(**data)


def getAttributes(name, attributeTypes=None):
    """get existing attributes in the scene

    :param name: name of the attributes to get in the scene
    :type name: str

    :param attributeTypes: types of attributes to get in the scene
    :type attributeTypes: list[:class:`cgp_maya_utils.constants.AttributeType`]

    :return: the listed Attributes
    :rtype: list[Attribute]
    """

    # init
    attributes = []

    # list all
    if not attributeTypes:
        attributes = maya.cmds.ls('*.{0}'.format(name), recursive=True)

    # list by types
    else:
        for attributeType in attributeTypes:

            # get listed attributes
            listedAttributes = maya.cmds.ls('*.{0}'.format(name), recursive=True, type=attributeType)

            # extend attributes
            attributes.extend(listedAttributes)

    # return
    return [attribute(item) for item in attributes]


def getNodesFromAttributes(attributes):
    """get the nodes which have the specified attributes

    :param attributes: attributes required on the node for it to be part of the return
    :type attributes: list[str]

    :return: the nodes having the attributes
    :rtype: list[Node]
    """

    # init
    data = []
    toQuery = []
    attributes = sorted(set(attributes))

    # init
    for attr in attributes:
        toQuery.extend(maya.cmds.ls('*.{0}'.format(attr), recursive=True, objectsOnly=True) or [])
        toQuery = list(set(toQuery))

    for nod in toQuery:

        # get all the existing tags on the node
        attrs = maya.cmds.listAttr(nod)

        # get specified attributes on the node
        specifiedAttributes = sorted(set(attributes).intersection(set(attrs)))

        # update data
        if attributes == specifiedAttributes:
            data.append(nod)

    # return
    return data


# COMPONENT COMMANDS #


def component(fullName):
    """get the component object from a component full name

    :param fullName: the full name of the component - ``shape.component[]`` or ``shape.component[][]``
    :type fullName: str

    :return: the component object
    :rtype: Component
    """

    # errors
    if (not re.match(r'.+\.[a-zA-Z]+\[[0-9]+]$', fullName) and
            not re.match(r'.+\.[a-zA-Z]+\[[0-9]+]\[[0-9]+]$', fullName)):
        raise ValueError('{0} is not a valid component'.format(fullName))

    # init
    genericType = cgp_maya_utils.constants.ComponentType.COMPONENT
    shape, component_ = fullName.split('.')

    # errors
    if maya.cmds.nodeType(shape) not in cgp_maya_utils.constants.NodeType.SHAPES:
        raise ValueError('{0} is not a shape component'.format(fullName))

    # get info
    componentType = component_.split('[', 1)[0]

    # return
    return _COMPONENT_TYPES.get(componentType, _COMPONENT_TYPES[genericType])(fullName)


# MISC COMMANDS #


def currentNamespace(asAbsolute=True):
    """get the current namespace of the maya scene

    :param asAbsolute: ``True`` : command returns an absolute namespace -
                       ``False`` : command returns a relative namespace
    :type asAbsolute: bool

    :return: the current namespace object
    :rtype: :class:`cgp_maya_utils.scene.Namespace`
    """

    # return
    return maya.cmds.namespaceInfo(currentNamespace=True, absoluteName=asAbsolute)


def namespace(name):
    """get the namespace object from a namespace's name

    :param name: name of the namespace to get the namespace object from
    :type name: str

    :return: the namespace object
    :rtype: :class:`cgp_maya_utils.scene.Namespace`
    """

    # return
    return _MISC_TYPES[cgp_maya_utils.constants.MiscType.NAMESPACE](name)


def getNamespaces(parent=None, isRecursive=True):
    """get the namespace objects available in scene

    :param parent: name of the parent namespace for look under - default is root namespace `:`
    :type parent: str or :class:`cgp_maya_utils.scene.Namespace`

    :param isRecursive: ``True`` : get all namespaces recursively under the parent -
                        ``False`` : get only direct children under the parent
    :type isRecursive: bool

    :return: the namespace objects
    :rtype: list[:class:`cgp_maya_utils.scene.Namespace`]
    """

    # init
    parent = parent or ':'

    # return
    return [namespace(name) for name in maya.cmds.namespaceInfo(parent, listOnlyNamespaces=True, recurse=isRecursive)]


def optionVar(name):
    """get the optionVar object of the given OptionVar name

    :param name: the name of the optionVar to get the optionVar object from
    :type name: str

    :return: the optionVar object
    :rtype: OptionVar
    """

    # init
    genericType = cgp_maya_utils.constants.OptionVarType.GENERIC

    # check existence
    if not maya.cmds.optionVar(exists=name):
        raise ValueError('No OptionVar named: {0!r}'.format(name))

    # query value in order to find its type
    value = maya.cmds.optionVar(query=name)

    # get type name from value
    if isinstance(value, list):
        typeName = '{0}Array'.format(type(value[0]).__name__) if value else genericType  # avoid crash with unknown type
    else:
        typeName = type(value).__name__

    # return the correct OptionVar instance
    if typeName in _OPTIONVAR_TYPES:
        return _OPTIONVAR_TYPES[typeName](name)

    # if no OptionVar class accept this kind of data, return a read-only instance
    return _OPTIONVAR_TYPES[genericType](name)


def getOptionVars():
    """get all the OptionVars from the current scene

    :return: all the optionVars
    :rtype: list[OptionVar]
    """

    # return
    return [optionVar(name) for name in maya.cmds.optionVar(list=True)]


def plugin(name):
    """get the plugin object from a plugin's name

    :param name: name of the plugin to get
    :type name: str

    :return: the plugin object
    :rtype: Plugin
    """

    # return
    return _MISC_TYPES[cgp_maya_utils.constants.MiscType.PLUGIN](name)


def scene():
    """get the scene object from the live maya scene

    :return: the scene object
    :rtype: :class:`cgp_maya_utils.scene.Scene`
    """

    # return
    return _MISC_TYPES[cgp_maya_utils.constants.MiscType.SCENE]()


# NODE COMMANDS #


def createNode(data, **extraData):
    """create a node using a node data dictionary

    :param data: data used to create the node
    :type data: dict

    :param extraData: extraData used to update the data before creating the node
    :type extraData: any

    :return: the created node
    :rtype: Node
    """

    # update data
    data.update(extraData)

    # init attribute object
    nodeObject = _NODE_TYPES.get(data['nodeType'], None)

    # errors
    if not nodeObject:
        raise ValueError('{0} is not implemented'.format(data['nodeType']))

    # return
    return nodeObject.create(**data)


def getNodes(namePattern=None, nodeTypes=None, asExactNodeTypes=False):
    """get existing nodes in the scene

    :param namePattern: name pattern of the nodes to get - ex : '*_suffix'
    :type namePattern: str

    :param nodeTypes: types of nodes to get
    :type nodeTypes: list[str]

    :param asExactNodeTypes: ``True`` : list only exact node types - ``False`` : all types inheriting node types
    :type asExactNodeTypes: bool

    :return: the listed Nodes
    :rtype: tuple[Node]
    """

    # init
    nodes = []

    # list all
    if not nodeTypes:
        nodes = (maya.cmds.ls(namePattern, recursive=True)
                 if namePattern
                 else maya.cmds.ls(recursive=True))

    # list by types
    else:
        for nodeType in nodeTypes:

            # get typeArg
            typeArg = {'exactType': nodeType} if asExactNodeTypes else {'type': nodeType}

            # get listedNodes
            listedNodes = (maya.cmds.ls(namePattern, recursive=True, **typeArg)
                           if namePattern
                           else maya.cmds.ls(recursive=True, **typeArg))

            # extend nodes
            nodes.extend(listedNodes)

    # return
    return tuple([node(item) for item in nodes])


def node(name):
    """get the node object from a node's name

    :param name: name of the node to get the node object from
    :type name: str

    :return: the node object
    :rtype: Node
    """

    # query the node type via the open maya api (fastest but does not work with every node types)
    nodeType = cgp_maya_utils.api.MayaObject(name).apiTypeStr
    nodeType = nodeType[1].lower() + nodeType[2:]  # we remove the 'k' and we lower the first char
    if nodeType not in cgp_maya_utils.constants.NodeType.API_ERRORED_TYPES and nodeType in _NODE_TYPES:
        return _NODE_TYPES[nodeType](name)

    # query the exact type from maya.cmds (slower but works only with node types we already wrapped)
    nodeType = maya.cmds.nodeType(name)
    if nodeType in _NODE_TYPES:
        return _NODE_TYPES[nodeType](name)

    # return object based on inherited node type (slowest but fallback on inherited node types)
    for nodeType in reversed(maya.cmds.nodeType(name, inherited=True)):
        if nodeType in _NODE_TYPES:
            return _NODE_TYPES[nodeType](name)

    # ultra generic fallback
    return _NODE_TYPES[cgp_maya_utils.constants.NodeType.BASE_NODE](name)


# MISC COMMANDS


def _registerAttributeTypes(attributeTypes):
    """register attribute types

    :param attributeTypes: attribute types to register
    :type attributeTypes: dict
    """

    # execute
    _ATTRIBUTE_TYPES.update(attributeTypes)


def _registerComponentTypes(componentTypes):
    """register component types

    :param componentTypes: component types to register
    :type componentTypes: dict
    """

    # execute
    _COMPONENT_TYPES.update(componentTypes)


def _registerMiscTypes(miscTypes):
    """register node types

    :param miscTypes: misc types to register
    :type miscTypes: dict
    """

    # execute
    _MISC_TYPES.update(miscTypes)


def _registerNodeTypes(nodeTypes):
    """register node types

    :param nodeTypes: node types to register
    :type nodeTypes: dict
    """

    # execute
    _NODE_TYPES.update(nodeTypes)


def _registerOptionVarTypes(optionVarTypes):
    """register node types

    :param optionVarTypes: optionVar types to register
    :type optionVarTypes: dict
    """

    # execute
    _OPTIONVAR_TYPES.update(optionVarTypes)
