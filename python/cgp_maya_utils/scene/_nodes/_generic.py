"""
generic object library
"""

# imports third-parties
import maya.cmds
import maya.api.OpenMaya
import cgp_generic_utils.files
import cgp_generic_utils.constants

# imports local
import cgp_maya_utils.api
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api


# GENERIC OBJECTS #


class Node(object):
    """node object that manipulates any kind of node
    """

    # ATTRIBUTES #

    _nodeType = 'baseNode'
    _MFn = maya.api.OpenMaya.MFnDependencyNode()

    # INIT #

    def __init__(self, name):
        """Node class initialization

        :param name: name of the node
        :type name: str
        """

        # init
        self._mObject = cgp_maya_utils.api.MayaObject(name)

    def __eq__(self, node):
        """check if the Node is identical to the other node

        :param node: node to compare to
        :type node: str or :class:`cgp_maya_utils.scene.Node`

        :return: ``True`` : nodes are identical - ``False`` : nodes are different
        :rtype: bool
        """

        # return
        return self.name() == str(node)

    def __ne__(self, node):
        """check if the Node is different to the other node

        :param node: node to compare to
        :type node: str or :class:`cgp_maya_utils.scene.Node`

        :return: ``True`` : nodes are different - ``False`` : nodes are identical
        :rtype: bool
        """

        # return
        return self.name() != str(node)

    def __repr__(self):
        """the representation of the node

        :return: the representation of the node
        :rtype: str
        """

        # return
        return '{0}(\'{1}\')'.format(self.__class__.__name__, self.name())

    def __str__(self):
        """the print of the node

        :return: the print of the node
        :rtype: str
        """

        # return
        return self.name()

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, nodeType, connections=None, attributeValues=None, name=None, **__):
        """create a node

        :param nodeType: type of node to create
        :type nodeType: str

        :param connections: connections to set on the created node
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the node
        :type attributeValues: dict

        :param name: name of the node
        :type name: str

        :return: the created node
        :rtype: :class:`cgp_maya_utils.scene.Node`
        """

        # create node
        node = maya.cmds.createNode(nodeType, name=name or nodeType)
        nodeObject = cgp_maya_utils.scene._api.node(node)

        # set attributeValues
        if attributeValues:
            nodeObject.setAttributeValues(attributeValues)

        # set connections
        if connections:
            nodeObject.setConnections(connections)

        # return
        return node

    # COMMANDS #

    def attribute(self, attribute):
        """the attribute of the node from an attribute name

        :param attribute: name of the attribute to get
        :type attribute: str

        :return: the attribute object
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # return
        return cgp_maya_utils.scene._api.attribute('{0}.{1}'.format(self.name(), attribute))

    def attributes(self, attributeTypes=None, attributeTypesIncluded=True, onlyUserDefined=False):
        """the attributes of the node from attribute types

        :param attributeTypes: types of attributes to get - All if nothing is specified
        :type attributeTypes: list[str]

        :param attributeTypesIncluded: ``True`` : attribute types are included -
                                       ``False`` : attribute types are excluded
        :type attributeTypesIncluded: bool

        :param onlyUserDefined: ``True`` : only user defined attributes - ``False`` : not only user defined attributes
        :type onlyUserDefined: bool

        :return: the attributes
        :rtype: list[:class:`cgp_maya_utils.scene.Attribute`]
        """

        # init
        returnAttributes = []
        queryAttributeTypes = []
        userDefinedAttributes = maya.cmds.listAttr(self.name(), userDefined=True)

        # errors
        if attributeTypes:
            for attributeType in attributeTypes:
                if attributeType not in cgp_maya_utils.constants.AttributeType.ALL:
                    raise ValueError('{0} is not a valid type - {1}'
                                     .format(attributeType, cgp_maya_utils.constants.AttributeType.ALL))

        # get attrTypes to query
        if not attributeTypes and attributeTypesIncluded:
            queryAttributeTypes = cgp_maya_utils.constants.AttributeType.ALL

        elif attributeTypes and attributeTypesIncluded:
            queryAttributeTypes = attributeTypes

        elif attributeTypes and not attributeTypesIncluded:
            queryAttributeTypes = set(cgp_maya_utils.constants.AttributeType.ALL) - set(attributeTypes)

        # execute
        for attribute in maya.cmds.listAttr(self.name()):

            # continue
            if onlyUserDefined and attribute not in userDefinedAttributes:
                continue

            # get full attribute
            fullAttribute = '{0}.{1}'.format(self.name(), attribute)

            # get attribute type
            # try except work around for unrecognized attributes like publishedNodeInfo.publishedNode
            try:
                attributeType = maya.cmds.getAttr(fullAttribute, type=True)
            except (ValueError, RuntimeError):
                continue

            # update
            if attributeType in queryAttributeTypes:
                returnAttributes.append(cgp_maya_utils.scene._api.attribute(fullAttribute))

        # return
        return returnAttributes

    def attributeValues(self):
        """the values of the available attributes of the node

        :return: the attribute values
        :rtype: dict
        """

        # init
        data = {}

        # get attributeValues data
        for attribute in self._availableAttributes():
            data[attribute] = self.attribute(attribute).value()

        # return
        return data

    def connections(self, attributes=None, sources=True, destinations=True, nodeTypes=None, nodeTypesIncluded=True,
                    skipConversionNodes=False):
        """the source and destination connections of the node

        :param attributes: attributes of the node to get the connections from - get all if nothing specified
        :type attributes: list[str]

        :param sources: ``True`` : get the source connections - ``False`` : does not get the source connections
        :type sources: bool

        :param destinations: ``True`` : get the destination connections -
                             ``False`` : does not get the destination connections
        :type destinations: bool

        :param nodeTypes: types of nodes to get the connections from - All if nothing is specified
        :type nodeTypes: list[str]

        :param nodeTypesIncluded: ``True`` : include specified node types - ``False`` : exclude specified node types
        :type nodeTypesIncluded: bool

        :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the connections of the node
        :rtype: list[:class:`cgp_maya_utils.scene.Connection`]
        """

        # return
        return cgp_maya_utils.scene.Connection.get(self.name(),
                                                   attributes=attributes,
                                                   sources=sources,
                                                   destinations=destinations,
                                                   nodeTypes=nodeTypes,
                                                   nodeTypesIncluded=nodeTypesIncluded,
                                                   skipConversionNodes=skipConversionNodes)

    def data(self):
        """data necessary to store the node on disk and/or recreate it from scratch

        :return: the data of the node
        :rtype: dict
        """

        # return
        return {'connections': [connection.data() for connection in self.connections(skipConversionNodes=True)],
                'name': self.name(),
                'nodeType': self.nodeType(),
                'attributeValues': self.attributeValues()}

    def delete(self):
        """delete the node
        """

        # execute
        maya.cmds.delete(self.name())

    def duplicate(self):
        """duplicate the node

        :return: the duplicated node
        :rtype: :class:`cgp_maya_utils.scene.Node`
        """

        # return
        return cgp_maya_utils.scene._api.node(maya.cmds.duplicate(self.name())[0])

    def hasAttribute(self, attribute):
        """check if the node has the attribute

        :param attribute: the attribute to check
        :type attribute: str

        :return: ``True`` : it has the attribute - ``False`` : it does not have the attribute
        :rtype: bool
        """

        # return
        return maya.cmds.attributeQuery(attribute, exists=True, node=self.name())

    def hasAttributes(self, attributes):
        """check if the node has the attributes

        :param attributes: attributes to check on the node
        :type attributes: list[str]

        :return: ``True`` : it has the attributes - ``False`` : it does not have the attributes
        :rtype: bool
        """

        # init
        attrs = maya.cmds.listAttr(self.name())
        specifiedAttributes = set(attrs) & set(attributes)

        # return
        return sorted(specifiedAttributes) == sorted(attributes)

    def isLocked(self):
        """check if the node is locked

        :return: ``True`` : it is locked - ``False`` : it is not locked
        :rtype: bool
        """

        # return
        return maya.cmds.lockNode(self.name(), query=True)[0]

    def isReferenced(self):
        """check if the node is referenced

        :return: ``True`` : it is referenced - ``False`` : it is not referenced
        :rtype: bool
        """

        # return
        return maya.cmds.referenceQuery(self.name(), isNodeReferenced=True)

    def MFn(self):
        """the function set of the node

        :return: the function set of the node
        :rtype: :class:`maya.api.OpenMaya.MFn`
        """

        # return
        return self._MFn.setObject(self.MObject())

    def MObject(self):
        """the MObject of the node

        :return: the MObject of the node
        :rtype: :class:`maya.api.OpenMaya.MObject`
        """

        # return
        return self._mObject

    def name(self):
        """the name of the node

        :return: the name of the node
        :rtype: str
        """

        # return
        return self.MFn().name()

    def namespace(self):
        """the namespace of the node

        :return: the namespace of the node
        :rtype: :class:`cgp_maya_utils.scene.Namespace`
        """

        # get namespace
        namespace = self.name().rpartition('|')[-1].rpartition(':')[0] or ':'

        # return
        return cgp_maya_utils.scene._api.namespace(namespace)

    def nodeType(self):
        """the type of the node

        :return: the type of the node
        :rtype: str
        """

        # return
        return maya.cmds.nodeType(self.name())

    def rebuild(self):
        """rebuild the node
        """

        # init
        data = self.data()

        # delete node
        self.delete()

        # rebuild skin cluster
        newNode = cgp_maya_utils.scene._api.createNode(data)

        # update node
        self._MFn = newNode.MFn()

    def reference(self):
        """the reference of the node

        :return: the reference object
        :rtype: :class:`cgp_maya_utils.scene.Reference`
        """

        # execute
        if maya.cmds.referenceQuery(self.name(), isNodeReferenced=True):
            refNode = maya.cmds.referenceQuery(self.name(), referenceNode=True)
            return Reference(refNode)

        # return
        return None

    def select(self):
        """select the node
        """

        # execute
        maya.cmds.select(self.name(), replace=True)

    def setConnections(self, connections):
        """set the connections of the node

        :param connections: connection data used to set the connections
        :type connections: list[tuple[str]]
        """

        # execute
        for source, destination in connections:

            # check if connection is settable
            if not self.name() in source or not self.name() in destination:
                continue

            if not maya.cmds.objExists(source) or not maya.cmds.objExists(destination):
                continue

            # set connection
            connection = cgp_maya_utils.scene._api.connection(source, destination)
            connection.connect()

    def setLock(self, isLocked):
        """set the lock status of the node

        :param isLocked: ``True`` : the node will be locked - ``False`` : the node will be unlocked
        :type isLocked: bool
        """

        # execute
        maya.cmds.lockNode(self.name(), lock=isLocked)

    def setName(self, name):
        """set the name of the node

        :param name: new name of the node
        :type name: str
        """

        # execute
        maya.cmds.rename(self.name(), name)

    def setAttributeValues(self, attributeValues):
        """set the values of the attributes of the node

        :param attributeValues: values to set to the attributes of the node - ``{attr1: value1, attr2: value2 ...}``
        :type attributeValues: dict
        """

        # execute
        for attribute, attributeValue in attributeValues.items():
            self.attribute(attribute).setValue(attributeValue)

    # PRIVATE COMMANDS #

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # TODO: update availableAttributes to gather all attributes used for setting - specially the userDefined ones

        # return
        return ['caching',
                'frozen',
                'nodeState']


class DagNode(Node):
    """node object that manipulates any kind of dag node
    """

    # ATTRIBUTES #

    _nodeType = 'dagNode'
    _MFn = maya.api.OpenMaya.MFnDagNode()

    # INIT #

    def __init__(self, name):
        """DagNode class initialization

        :param name: name of the dagNode
        :type name: str
        """

        # init
        super(DagNode, self).__init__(name)

    # COMMANDS #

    def fullName(self):
        """the full name of the node

        :return: the full name of the node
        :rtype: str
        """

        # return
        return self.MFn().fullPathName()

    def name(self):
        """the the shortest unique name of the node

        :return: the name of the node
        :rtype: str
        """

        # return
        return self.MFn().partialPathName()

    def parent(self):
        """the parent of the dag node

        :return: the parent of the dag node
        :rtype: :class:`cgp_maya_utils.scene.DagNode`
        """

        # execute
        parents = maya.cmds.listRelatives(self.name(), parent=True)

        # return
        return cgp_maya_utils.scene._api.node(parents[0]) if parents else None

    def setParent(self, parent=None):
        """set the parent of the dag node

        :param parent: dag node to parent the dag node to - If None, parent is the root of the scene
        :type parent: str or :class:`cgp_maya_utils.scene.DagNode`
        """

        # parent to world
        if parent is None and maya.cmds.listRelatives(self.name(), parent=True):
            maya.cmds.parent(self.name(), world=True)
            return

        # update parent
        parent = str(parent)

        # return
        if not maya.cmds.objExists(parent) or parent == self.parent():
            return

        # execute
        maya.cmds.parent(self.name(), parent)


class Reference(Node):
    """node object that manipulates a ``reference`` node
    """

    # ATTRIBUTES

    _nodeType = 'reference'

    # INIT #

    def __init__(self, name):
        """Reference class initialization

        :param name: name of the reference node
        :type name: str
        """

        # init
        super(Reference, self).__init__(name)

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, path=None, namespace=None, **__):
        """create a reference

        :param path: path of the file to reference
        :type path: str or :class:`cgp_maya_utils.files.MayaFile`

        :param namespace: namespace of the created reference
        :type namespace: str

        :return: the created reference
        :rtype: :class:`cgp_maya_utils.scene.Reference`
        """

        # errors
        if not path:
            raise ValueError('path need to be specified')

        if not namespace:
            raise ValueError('namespace need to be specified')

        # execute
        fileName = maya.cmds.file(path, reference=True, namespace=namespace)

        # return
        for referenceNode in maya.cmds.ls(exactType='reference'):
            if maya.cmds.referenceQuery(referenceNode, filename=True) == fileName:
                return cls(referenceNode)

    # COMMANDS #

    def data(self):
        """data necessary to store the reference node on disk and/or recreate it from scratch

        :return: the data of the reference
        :rtype: dict
        """

        # init
        data = super(Reference, self).data()

        # update data
        data['file'] = self.file_()
        data['namespace'] = self.namespace().fullName(asAbsolute=False)

        # return
        return data

    def delete(self):
        """delete the reference
        """

        # execute
        if self.file_():
            maya.cmds.file(self.file_(), removeReference=True)
        else:
            maya.cmds.lockNode(self.name(), lock=False)
            maya.cmds.delete(self.name())

    def file_(self):
        """the file associated to the reference node

        :return: the file of the reference node
        :rtype: :class:`cgp_maya_utils.scene.MayaFile`
        """

        # execute
        try:
            fileName = maya.cmds.referenceQuery(self.name(), filename=True)
            return cgp_generic_utils.files.entity(fileName)
        except RuntimeError:
            return None

    def import_(self, namespaceSubstitute=None):
        """import the objects from reference

        :param namespaceSubstitute: string that will replace the ``:`` of the namespace
        :type namespaceSubstitute: str
        """

        # return
        if not self.file_():
            self.delete()
            return

        # get namespace
        namespace = self.namespace()

        # import objects
        copyFile = maya.cmds.referenceQuery(self.name(), filename=True, withoutCopyNumber=False)
        maya.cmds.file(copyFile, importReference=True)

        # clean namespace
        if namespaceSubstitute is not None:

            # rename content
            for obj in maya.cmds.namespaceInfo(namespace, listNamespace=True, recurse=True):
                if maya.cmds.objExists(obj):
                    maya.cmds.rename(obj, obj.replace(':', namespaceSubstitute))

            # remove namespace
            maya.cmds.namespace(removeNamespace=namespace)

    def namespace(self):
        """the namespace of the node

        :return: the namespace of the node
        :rtype: :class:`cgp_maya_utils.scene.Namespace`
        """

        # get namespace
        copyFile = maya.cmds.referenceQuery(self.name(), filename=True, withoutCopyNumber=False)
        namespace = maya.cmds.file(copyFile, query=True, namespace=True)

        # return
        return cgp_maya_utils.scene._api.namespace(namespace) if self.file_() else None

    def setNamespace(self, namespace, renameNode=True):
        """set the namespace

        :param namespace: namespace to set
        :type namespace: str or :class:`cgp_maya_utils.scene.Namespace`

        :param renameNode: ``True`` : the reference node is renamed - ``False`` : the reference node is not renamed
        :type renameNode: bool
        """

        # init
        namespace = str(namespace)

        # errors
        if self.namespace == namespace:
            maya.cmds.warning('reference already has {0} namespace'.format(namespace))
            return

        if not self.file_():
            maya.cmds.warning("can't set namespace on reference that doesn't have a file path set")
            return

        if maya.cmds.namespace(exists=namespace):
            maya.cmds.warning('{0} is already existing'.format(namespace))
            return

        # check if the reference node is locked
        isLocked = self.isLocked()

        # set namespace
        maya.cmds.file(self.file_(), edit=True, namespace=namespace)

        # rename node
        if renameNode:
            self.setLock(False)
            self.setName('{0}RN'.format(namespace))
            self.setLock(isLocked)
