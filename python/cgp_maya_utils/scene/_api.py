"""
maya scene management functions
"""

# imports python
import re

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants


_ATTRIBUTE_TYPES = {}
_COMPONENT_TYPES = {}
_MISC_TYPES = {}
_NODE_TYPES = {}


# ATTRIBUTE COMMANDS #


def attribute(fullName):
    """the attribute object from an attribute full name

    :param fullName: the full name of the attribute - ``node.attribute``
    :type fullName: str

    :return: the attribute object
    :rtype: :class:`cgp_maya_utils.scene.Attribute`,
            :class:`cgp_maya_utils.scene.BoolAttribute`,
            :class:`cgp_maya_utils.scene.ByteAttribute`,
            :class:`cgp_maya_utils.scene.CompoundAttribute`,
            :class:`cgp_maya_utils.scene.Double3Attribute`,
            :class:`cgp_maya_utils.scene.DoubleAngleAttribute`,
            :class:`cgp_maya_utils.scene.DoubleAttribute`,
            :class:`cgp_maya_utils.scene.DoubleLinearAttribute`,
            :class:`cgp_maya_utils.scene.EnumAttribute`,
            :class:`cgp_maya_utils.scene.Float3Attribute`,
            :class:`cgp_maya_utils.scene.FloatAttribute`,
            :class:`cgp_maya_utils.scene.LongAttribute`,
            :class:`cgp_maya_utils.scene.MatrixAttribute`,
            :class:`cgp_maya_utils.scene.MessageAttribute`,
            :class:`cgp_maya_utils.scene.NumericAttribute`,
            :class:`cgp_maya_utils.scene.ShortAttribute`,
            :class:`cgp_maya_utils.scene.StringAttribute`,
            :class:`cgp_maya_utils.scene.TDataCompoundAttribute`,
            :class:`cgp_maya_utils.scene.TimeAttribute`
    """

    # get infos
    attributeType = maya.cmds.getAttr(fullName, type=True)

    # return
    return _ATTRIBUTE_TYPES.get(attributeType, _ATTRIBUTE_TYPES['attribute'])(fullName)


def connection(source, destination):
    """the connection object representing a connection, live or virtual, between the source and the destination

    :param source: the source of the connection
    :type source: str or :class:`cgp_maya_utils.scene.Attribute`

    :param destination: the destination of the connection
    :type destination: str or :class:`cgp_maya_utils.scene.Attribute`

    :return: the connection object
    :rtype: :class:`cgp_maya_utils.scene.Connection`
    """

    # return
    return _ATTRIBUTE_TYPES['connection'](source, destination)


def createAttribute(data, **extraData):
    """create an attribute using an attribute data dictionary

    :param data: data used to create the attribute
    :type data: dict

    :param extraData: extraData used to update the data dictionary before creating the attribute
    :type extraData: any

    :return: the created attribute
    :rtype: :class:`cgp_maya_utils.scene.Attribute`,
            :class:`cgp_maya_utils.scene.BoolAttribute`,
            :class:`cgp_maya_utils.scene.ByteAttribute`,
            :class:`cgp_maya_utils.scene.CompoundAttribute`,
            :class:`cgp_maya_utils.scene.Double3Attribute`,
            :class:`cgp_maya_utils.scene.DoubleAngleAttribute`,
            :class:`cgp_maya_utils.scene.DoubleAttribute`,
            :class:`cgp_maya_utils.scene.DoubleLinearAttribute`,
            :class:`cgp_maya_utils.scene.EnumAttribute`,
            :class:`cgp_maya_utils.scene.Float3Attribute`,
            :class:`cgp_maya_utils.scene.FloatAttribute`,
            :class:`cgp_maya_utils.scene.LongAttribute`,
            :class:`cgp_maya_utils.scene.MatrixAttribute`,
            :class:`cgp_maya_utils.scene.MessageAttribute`,
            :class:`cgp_maya_utils.scene.NumericAttribute`,
            :class:`cgp_maya_utils.scene.ShortAttribute`,
            :class:`cgp_maya_utils.scene.StringAttribute`,
            :class:`cgp_maya_utils.scene.TDataCompoundAttribute`,
            :class:`cgp_maya_utils.scene.TimeAttribute`
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
    """get the existing attributes in the scene

    :param name: name of the attributes to get in the scene
    :type name: str

    :param attributeTypes: types of attributes to get in the scene
    :type attributeTypes: list[str]

    :return: the listed Attributes
    :rtype: tuple[:class:`cgp_maya_utils.scene.Attribute`,
                  :class:`cgp_maya_utils.scene.BoolAttribute`,
                  :class:`cgp_maya_utils.scene.ByteAttribute`,
                  :class:`cgp_maya_utils.scene.CompoundAttribute`,
                  :class:`cgp_maya_utils.scene.Double3Attribute`,
                  :class:`cgp_maya_utils.scene.DoubleAngleAttribute`,
                  :class:`cgp_maya_utils.scene.DoubleAttribute`,
                  :class:`cgp_maya_utils.scene.DoubleLinearAttribute`,
                  :class:`cgp_maya_utils.scene.EnumAttribute`,
                  :class:`cgp_maya_utils.scene.Float3Attribute`,
                  :class:`cgp_maya_utils.scene.FloatAttribute`,
                  :class:`cgp_maya_utils.scene.LongAttribute`,
                  :class:`cgp_maya_utils.scene.MatrixAttribute`,
                  :class:`cgp_maya_utils.scene.MessageAttribute`,
                  :class:`cgp_maya_utils.scene.NumericAttribute`,
                  :class:`cgp_maya_utils.scene.ShortAttribute`,
                  :class:`cgp_maya_utils.scene.StringAttribute`,
                  :class:`cgp_maya_utils.scene.TDataCompoundAttribute`,
                  :class:`cgp_maya_utils.scene.TimeAttribute`]
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
    return tuple([attribute(attribute_) for attribute_ in attributes])


def getNodesFromAttributes(attributes):
    """get the nodes having the specified attributes

    :param attributes: attributes required on the node for it to be part of the return
    :type attributes: list[str]

    :return: the gathered nodes
    :rtype: tuple[:class:`cgp_maya_utils.scene.Node`,
                  :class:`cgp_maya_utils.scene.AimConstraint`,
                  :class:`cgp_maya_utils.scene.AnimCurve`,
                  :class:`cgp_maya_utils.scene.AnimCurveTA`,
                  :class:`cgp_maya_utils.scene.AnimCurveTL`,
                  :class:`cgp_maya_utils.scene.AnimCurveTU`,
                  :class:`cgp_maya_utils.scene.Constraint`,
                  :class:`cgp_maya_utils.scene.DagNode`,
                  :class:`cgp_maya_utils.scene.GeometryFilter`,
                  :class:`cgp_maya_utils.scene.IkEffector`,
                  :class:`cgp_maya_utils.scene.IkHandle`,
                  :class:`cgp_maya_utils.scene.Joint`,
                  :class:`cgp_maya_utils.scene.Mesh`,
                  :class:`cgp_maya_utils.scene.Node`,
                  :class:`cgp_maya_utils.scene.NurbsCurve`,
                  :class:`cgp_maya_utils.scene.NurbsSurface`,
                  :class:`cgp_maya_utils.scene.OrientConstraint`,
                  :class:`cgp_maya_utils.scene.ParentConstraint`,
                  :class:`cgp_maya_utils.scene.PointConstraint`,
                  :class:`cgp_maya_utils.scene.Reference`,
                  :class:`cgp_maya_utils.scene.ScaleConstraint`,
                  :class:`cgp_maya_utils.scene.Shape`,
                  :class:`cgp_maya_utils.scene.SkinCluster`,
                  :class:`cgp_maya_utils.scene.Transform`]
    """

    # init
    data = []
    toQuery = []
    attributes = set(attributes)

    # init
    for attr in sorted(attributes):
        toQuery.extend(maya.cmds.ls('*.{0}'.format(attr), recursive=True, objectsOnly=True) or [])

    # execute
    for node_ in set(toQuery):

        # get all the existing tags on the node
        attrs = maya.cmds.listAttr(node_)

        # get specified attributes on the node
        specifiedAttributes = sorted(attributes.intersection(set(attrs)))

        # update data
        if attributes == specifiedAttributes:
            data.append(node(node_))

    # return
    return tuple(data)


# COMPONENT COMMANDS #


def component(fullName):
    """the component object from a component full name

    :param fullName: the full name of the component - ``shape.component[]`` or ``shape.component[][]``
    :type fullName: str

    :return: the component object
    :rtype: :class:`cgp_maya_utils.scene.Component`,
            :class:`cgp_maya_utils.scene.CurvePoint`,
            :class:`cgp_maya_utils.scene.Edge`,
            :class:`cgp_maya_utils.scene.EditPoint`,
            :class:`cgp_maya_utils.scene.Face`,
            :class:`cgp_maya_utils.scene.IsoparmU`,
            :class:`cgp_maya_utils.scene.IsoparmV`,
            :class:`cgp_maya_utils.scene.SurfacePatch`,
            :class:`cgp_maya_utils.scene.SurfacePoint`,
            :class:`cgp_maya_utils.scene.TransformComponent`,
            :class:`cgp_maya_utils.scene.Vertex`,
    """

    # errors
    if (not re.match(r'.+\.[a-zA-Z]+\[[0-9]+]$', fullName) and
            not re.match(r'.+\.[a-zA-Z]+\[[0-9]+]\[[0-9]+]$', fullName)):
        raise ValueError('{0} is not a valid component'.format(fullName))

    # init
    shape, comp = fullName.split('.')

    # errors
    if maya.cmds.nodeType(shape) not in cgp_maya_utils.constants.NodeType.SHAPES:
        raise ValueError('{0} is not a shape node'.format(shape))

    # get infos
    componentType = ''.join([char for char in comp if not char.isdigit()])

    # return
    return _COMPONENT_TYPES.get(componentType, _COMPONENT_TYPES['component'])(fullName)


# MISC COMMANDS #


def currentNamespace(asAbsolute=True):
    """the current namespace of the maya scene

    :param asAbsolute: defines whether or not the command will return an absolute namespace
    :type asAbsolute: bool

    :return: the current namespace object
    :rtype: :class:`cgp_maya_utils.scene.Namespace`
    """

    # return
    return maya.cmds.namespaceInfo(currentNamespace=True, absoluteName=asAbsolute)


def namespace(name):
    """the namespace object from a name

    :param name: name to get the namespace object from
    :type name: str

    :return: the namespace object
    :rtype: :class:`cgp_maya_utils.scene.Namespace`
    """

    # return
    return _MISC_TYPES['namespace'](name)


def plugin(name):
    """the plugin object from a name

    :param name: name to get the plugin object from
    :type name: str

    :return: the plugin object
    :rtype: :class:`cgp_maya_utils.scene.Plugin`
    """

    # return
    return _MISC_TYPES['plugin'](name)


def scene():
    """the scene object from the live maya scene

    :return: the scene object
    :rtype: :class:`cgp_maya_utils.scene.Scene`
    """

    # return
    return _MISC_TYPES['scene']()


# NODE COMMANDS #


def createNode(data, **extraData):
    """create a node using a node data dictionary

    :param data: data used to create the node
    :type data: dict

    :param extraData: extraData used to update the data before creating the node
    :type extraData: any

    :return: the created node
    :rtype: :class:`cgp_maya_utils.scene.Node`,
            :class:`cgp_maya_utils.scene.AimConstraint`,
            :class:`cgp_maya_utils.scene.AnimCurve`,
            :class:`cgp_maya_utils.scene.AnimCurveTA`,
            :class:`cgp_maya_utils.scene.AnimCurveTL`,
            :class:`cgp_maya_utils.scene.AnimCurveTU`,
            :class:`cgp_maya_utils.scene.Constraint`,
            :class:`cgp_maya_utils.scene.DagNode`,
            :class:`cgp_maya_utils.scene.GeometryFilter`,
            :class:`cgp_maya_utils.scene.IkEffector`,
            :class:`cgp_maya_utils.scene.IkHandle`,
            :class:`cgp_maya_utils.scene.Joint`,
            :class:`cgp_maya_utils.scene.Mesh`,
            :class:`cgp_maya_utils.scene.Node`,
            :class:`cgp_maya_utils.scene.NurbsCurve`,
            :class:`cgp_maya_utils.scene.NurbsSurface`,
            :class:`cgp_maya_utils.scene.OrientConstraint`,
            :class:`cgp_maya_utils.scene.ParentConstraint`,
            :class:`cgp_maya_utils.scene.PointConstraint`,
            :class:`cgp_maya_utils.scene.Reference`,
            :class:`cgp_maya_utils.scene.ScaleConstraint`,
            :class:`cgp_maya_utils.scene.Shape`,
            :class:`cgp_maya_utils.scene.SkinCluster`,
            :class:`cgp_maya_utils.scene.Transform`
    """

    # update data
    data.update(extraData)

    # init attribute object
    nodeObject = _NODE_TYPES.get(data['nodeType'], _NODE_TYPES['node'])

    # return
    return nodeObject.create(**data)


def getNodes(namePattern=None, nodeTypes=None, asExactNodeTypes=False):
    """get the existing nodes in the scene

    :param namePattern: name pattern of the nodes to get - ex : *_suffix
    :type namePattern: str

    :param nodeTypes: types of nodes to get in the scene
    :type nodeTypes: list[str]

    :param asExactNodeTypes: defines whether or not the command will list exactType nodes
    :type asExactNodeTypes: bool

    :return: the listed Nodes
    :rtype: tuple[:class:`cgp_maya_utils.scene.Node`,
                  :class:`cgp_maya_utils.scene.AimConstraint`,
                  :class:`cgp_maya_utils.scene.AnimCurve`,
                  :class:`cgp_maya_utils.scene.AnimCurveTA`,
                  :class:`cgp_maya_utils.scene.AnimCurveTL`,
                  :class:`cgp_maya_utils.scene.AnimCurveTU`,
                  :class:`cgp_maya_utils.scene.Constraint`,
                  :class:`cgp_maya_utils.scene.DagNode`,
                  :class:`cgp_maya_utils.scene.GeometryFilter`,
                  :class:`cgp_maya_utils.scene.IkEffector`,
                  :class:`cgp_maya_utils.scene.IkHandle`,
                  :class:`cgp_maya_utils.scene.Joint`,
                  :class:`cgp_maya_utils.scene.Mesh`,
                  :class:`cgp_maya_utils.scene.Node`,
                  :class:`cgp_maya_utils.scene.NurbsCurve`,
                  :class:`cgp_maya_utils.scene.NurbsSurface`,
                  :class:`cgp_maya_utils.scene.OrientConstraint`,
                  :class:`cgp_maya_utils.scene.ParentConstraint`,
                  :class:`cgp_maya_utils.scene.PointConstraint`,
                  :class:`cgp_maya_utils.scene.Reference`,
                  :class:`cgp_maya_utils.scene.ScaleConstraint`,
                  :class:`cgp_maya_utils.scene.Shape`,
                  :class:`cgp_maya_utils.scene.SkinCluster`,
                  :class:`cgp_maya_utils.scene.Transform`]
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
    return tuple([node(node_) for node_ in nodes])


def node(name):
    """the node object from a node name

    :param name: the name of the node
    :type name: str

    :return: the node object
    :rtype: :class:`cgp_maya_utils.scene.Node`,
            :class:`cgp_maya_utils.scene.AimConstraint`,
            :class:`cgp_maya_utils.scene.AnimCurve`,
            :class:`cgp_maya_utils.scene.AnimCurveTA`,
            :class:`cgp_maya_utils.scene.AnimCurveTL`,
            :class:`cgp_maya_utils.scene.AnimCurveTU`,
            :class:`cgp_maya_utils.scene.Constraint`,
            :class:`cgp_maya_utils.scene.DagNode`,
            :class:`cgp_maya_utils.scene.GeometryFilter`,
            :class:`cgp_maya_utils.scene.IkEffector`,
            :class:`cgp_maya_utils.scene.IkHandle`,
            :class:`cgp_maya_utils.scene.Joint`,
            :class:`cgp_maya_utils.scene.Mesh`,
            :class:`cgp_maya_utils.scene.Node`,
            :class:`cgp_maya_utils.scene.NurbsCurve`,
            :class:`cgp_maya_utils.scene.NurbsSurface`,
            :class:`cgp_maya_utils.scene.OrientConstraint`,
            :class:`cgp_maya_utils.scene.ParentConstraint`,
            :class:`cgp_maya_utils.scene.PointConstraint`,
            :class:`cgp_maya_utils.scene.Reference`,
            :class:`cgp_maya_utils.scene.ScaleConstraint`,
            :class:`cgp_maya_utils.scene.Shape`,
            :class:`cgp_maya_utils.scene.SkinCluster`,
            :class:`cgp_maya_utils.scene.Transform`
    """

    # get the current object
    currentObject = _NODE_TYPES['node']

    # init node object
    for nodeType in reversed(maya.cmds.nodeType(name, inherited=True)):
        if nodeType in _NODE_TYPES:
            currentObject = _NODE_TYPES[nodeType]
            break

    # return
    return currentObject(name)


# PRIVATE COMMANDS #


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
