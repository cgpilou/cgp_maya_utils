"""
generic object library
"""

# imports python
import re

# imports third-parties
import maya.cmds
import maya.api.OpenMaya

# imports local
import cgp_maya_utils.api
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api


# GENERIC OBJECTS #


class Node(object):
    """node object that manipulates any kind of node
    """

    # ATTRIBUTES #
    
    _MFN = maya.api.OpenMaya.MFnDependencyNode()
    _TYPE = cgp_maya_utils.constants.NodeType.BASE_NODE

    # INIT #

    def __init__(self, name):
        """Node class initialization

        :param name: name of the node
        :type name: str
        """

        # init
        self._mObject = cgp_maya_utils.api.MayaObject(name)

    def __eq__(self, node):
        """check if the node is identical to the other node

        :param node: node to compare the node to
        :type node: str or :class:`cgp_maya_utils.scene.Node`

        :return: ``True`` : nodes are identical - ``False`` : nodes are different
        :rtype: bool
        """

        # return
        return self.name() == str(node)

    def __ne__(self, node):
        """check if the node is different to the other node

        :param node: node to compare the node to
        :type node: str or :class:`cgp_maya_utils.scene.Node`

        :return: ``True`` : nodes are different - ``False`` : nodes are identical
        :rtype: bool
        """

        # return
        return self.name() != str(node)

    def __repr__(self):
        """get the representation of the node

        :return: the representation of the node
        :rtype: str
        """

        # return
        return '{0}({1!r})'.format(self.__class__.__name__, self.name())

    def __str__(self):
        """get the string representation of the node

        :return: the string representation of the node
        :rtype: str
        """

        # return
        return self.name()

    # STATIC COMMANDS #

    @staticmethod
    def create(nodeType, connections=None, attributeValues=None, name=None, **__):
        """create a node

        :param nodeType: type of node to create
        :type nodeType: :class:`cgp_maya_utils.constants.NodeType`

        :param connections: connections to set on the created node
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the created node
        :type attributeValues: dict

        :param name: name of the created node
        :type name: str

        :return: the node object
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
        return nodeObject

    # COMMANDS #

    def addAttribute(self,
                     attributeType,
                     name,
                     value=None,
                     connectionSource=None,
                     connectionDestinations=None,
                     **extraData):
        """create an attribute on the node

        :param attributeType: the type of the attribute to create
        :type attributeType: :class:`cgp_maya_utils.constants.AttributeType`

        :param name: name of the attribute to create
        :type name: str

        :param value: value to set on the attribute
        :type value: any

        :param connectionSource: attribute that will be connected as source - `node.attribute`
        :type connectionSource: str or :class:`cgp_maya_utils.scene.Attribute`

        :param connectionDestinations: attributes that will be connected as destination -
                                       eg: `[node1.attribute1, node2.attribute2 ...]`
        :type connectionDestinations: list[str] or list[:class:`cgp_maya_utils.scene.Attribute`]

        :return: the created attribute
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # validate parameters
        if self.hasAttribute(name):
            raise ValueError('The node \'{}\' already has an attribute named \'{}\''.format(self, name))

        # prepare attribute's data
        data = {'attributeType': attributeType,
                'node': self,
                'name': name,
                'value': value,
                'connectionSource': connectionSource,
                'connectionDestinations': connectionDestinations}

        # create and return the new attribute
        return cgp_maya_utils.scene._api.createAttribute(data, **extraData)

    def attribute(self, attribute):
        """get an attribute of the node

        :param attribute: the name of the attribute to get
        :type attribute: str

        :return: the attribute of the node
        :rtype: Attribute
        """

        # return
        return cgp_maya_utils.scene._api.attribute('{0}.{1}'.format(self.name(), attribute))

    def attributes(self, namePattern=None, attributeTypes=None, attributeTypesIncluded=True):
        """get the attributes of the node

        :param namePattern: the name pattern the attributes have to match
        :type namePattern: str

        :param attributeTypes: types of attributes to get - All if nothing is specified
        :type attributeTypes: list[str or :class:`cgp_maya_utils.constants.AttributeType`]

        :param attributeTypesIncluded: ``True`` : given types are included - ``False`` : given types are excluded
        :type attributeTypesIncluded: bool

        :return: the attributes of the node
        :rtype: list[Attribute]
        """

        # init
        attrTypes = []
        nodeName = self.name()

        # errors
        if attributeTypes:
            for attrType in attributeTypes:
                if attrType not in cgp_maya_utils.constants.AttributeType.ALL:
                    raise ValueError('{0} is not a valid type - {1}'
                                     .format(attrType, cgp_maya_utils.constants.AttributeType.ALL))

        # return an empty list if no attribute types are valid
        if not attributeTypes and not attributeTypesIncluded:
            return []

        # list attribute names
        allAttributes = (maya.cmds.listAttr(nodeName, hasData=True, string=namePattern)
                         if namePattern
                         else maya.cmds.listAttr(nodeName)) or []

        # prune bad results
        validNames = []
        validAttributes = []
        internalAttributes = maya.cmds.attributeInfo(self.name(), internal=True) or []
        for name in allAttributes:

            # keep the first parent attribute (prune components of TdataCompound attributes)
            name = name.split(".", 1)[0]

            # ignore internal attributes
            if name in internalAttributes:
                continue

            # generate full name
            attributeFullName = "{}.{}".format(nodeName, name)

            # ignore doubles
            if attributeFullName in validNames:
                continue

            # store only strings to speed up the above doubles searching
            validNames.append(attributeFullName)

            # add the attribute to the valid list
            validAttributes.append(cgp_maya_utils.scene._api.attribute(attributeFullName))

        # if there is no need to check types, just return data as it is
        if not attributeTypes and attributeTypesIncluded:
            return validAttributes

        # get types to keep
        elif attributeTypes and attributeTypesIncluded:
            attrTypes = attributeTypes
        elif attributeTypes and not attributeTypesIncluded:
            attrTypes = list(set(cgp_maya_utils.constants.AttributeType.ALL) - set(attributeTypes))

        # return data matching types
        return [attribute for attribute in validAttributes if attribute.attributeType() in attrTypes]

    def attributeValues(self):
        """get the attribute values of the node

        :return: the attribute values
        :rtype: dict
        """

        # return gettable attributes
        return {attribute.name(): attribute.value()
                for attribute in self.attributes()
                if attribute.isGettable()}

    def connections(self,
                    attributes=None,
                    sources=True,
                    destinations=True,
                    nodeTypes=None,
                    nodeTypesIncluded=True,
                    skipConversionNodes=False):
        """get the source and destination connections of the node

        :param attributes: list of attributes to get the connections from - all if nothing specified
        :type attributes: list[str]

        :param sources: ``True`` : the command gets the source connections -
                        ``False`` : the command does not get the source connections
        :type sources: bool

        :param destinations: ``True`` : the command gets the destination connections -
                             ``False`` : the command does not get the destination connections
        :type destinations: bool

        :param nodeTypes: types of nodes used to get the connections - all if nothing is specified
        :type nodeTypes: list[str]

        :param nodeTypesIncluded: ``True`` : include specified node types -
                                  ``False`` : exclude specified node types
        :type nodeTypesIncluded: bool

        :param skipConversionNodes: ``True`` : conversion nodes are skipped -
                                    ``False`` : conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the connections
        :rtype: list[:class:`cgp_maya_utils.scene.Connection`]
        """

        # return
        return cgp_maya_utils.scene._api.getConnections(self.name(),
                                                        attributes=attributes,
                                                        sources=sources,
                                                        destinations=destinations,
                                                        nodeTypes=nodeTypes,
                                                        nodeTypesIncluded=nodeTypesIncluded,
                                                        skipConversionNodes=skipConversionNodes)

    def data(self):
        """get data necessary to store the node on disk and/or recreate it from scratch

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
        maya.cmds.delete(self.fullName())

    def duplicate(self):
        """duplicate the node

        :return: the duplicated node
        :rtype: Node
        """

        # return
        return self.__class__(maya.cmds.duplicate(self.fullName())[0])

    def fullName(self):
        """get the full name of the node

        :return: the full name of the node
        :rtype: str
        """

        # return
        return self.name()

    def hasAttribute(self, attribute):
        """check if the node has the attribute

        :param attribute: the name of the attribute to check
        :type attribute: str

        :return: ``True`` : the node has the attribute - ``False`` : the node does not have the attribute
        :rtype: bool
        """

        # get TDataCompound child existence
        if '[' in attribute or '.' in attribute:
            fullName = '{}.{}'.format(self.fullName(), attribute)
            try:
                maya.cmds.getAttr(fullName, type=True)
                return True
            except ValueError:
                return False

        # get generic attribute existence
        return self.MFn().hasAttribute(attribute)

    def isAttributeValid(self, attributes):
        """check if the node has the attributes

        :param attributes: attributes to check on the node
        :type attributes: list[str]

        :return: ``True`` : the node has the attributes ``False`` : the node does not have the attributes
        :rtype: bool
        """

        # init
        attrs = maya.cmds.listAttr(self.fullName())
        specifiedAttributes = set(attrs) & set(attributes)

        # return
        return sorted(specifiedAttributes) == sorted(attributes)

    def isDeleted(self):
        """check if the node has been deleted

        :return: ``True`` : the node has been deleted ``False`` : the node exists in the scene
        :rtype: bool
        """

        # return
        return not maya.cmds.objExists(self.fullName())

    def isLocked(self):
        """check if the node is locked

        :return: ``True`` : the node is locked - ``False`` : the node is not locked
        :rtype: bool
        """

        # return
        return maya.cmds.lockNode(self.fullName(), query=True)[0]

    def isReferenced(self):
        """check if the node is referenced

        :return: ``True`` : the node is referenced - ``False`` : the node is not referenced
        :rtype: bool
        """

        # return
        return maya.cmds.referenceQuery(self.fullName(), isNodeReferenced=True)

    def MFn(self):
        """get the function set of the node

        :return: the function set of the node
        :rtype: :class:`maya.api.OpenMaya.MFn`
        """

        # return
        return self._MFN.setObject(self.MObject())

    def MObject(self):
        """get the MObject of the node

        :return: the MObject of the node
        :rtype: :class:`cgp_maya_utils.api.MayaObject`
        """

        # return
        return self._mObject

    def name(self, withNamespace=True):
        """get the name of the node

        :param withNamespace: ``True`` : The name is returned with its namespace if there is any
                              ``False`` : The name is return without its namespace if there is any
        :type withNamespace: bool

        :return: the name of the node
        :rtype: str
        """

        # get name with namespace
        name = self.MFn().name()

        # return
        return name if withNamespace else maya.api.OpenMaya.MNamespace.stripNamespaceFromName(name)

    def namespace(self):
        """get the namespace of the node

        :return: the namespace of the node
        :rtype: :class:`cgp_maya_utils.scene.Namespace`
        """

        # get namespace
        namespace = maya.api.OpenMaya.MNamespace.getNamespaceFromName(self.name()) or ':'

        # return
        return cgp_maya_utils.scene._api.namespace(namespace)

    def nodeType(self):
        """get the type of the node

        :return: the type of the node
        :rtype: str
        """

        # return
        return maya.cmds.nodeType(self.fullName())

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
        self._MFN = newNode.MFn()

    def reference(self):
        """get the reference of the node if existing

        :return: the reference object
        :rtype: :class:`cgp_maya_utils.scene.Reference`
        """

        # init
        fullName = self.fullName()

        # execute
        if maya.cmds.referenceQuery(fullName, isNodeReferenced=True):
            refNode = maya.cmds.referenceQuery(fullName, referenceNode=True)
            return Reference(refNode)

        # return
        return None

    def select(self, isSelected=True):
        """select the node

        :param isSelected: define if the the Node has to be selected or not - default is True
        :type isSelected: bool
        """

        # execute
        if isSelected:
            maya.cmds.select(self.fullName(), replace=True)
        else:
            maya.cmds.select(self.fullName(), deselect=True)

    def setConnections(self, connections):
        """set the connections

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
        maya.cmds.lockNode(self.fullName(), lock=isLocked)

    def setName(self, name):
        """set the name of the node

        :param name: new name of the node
        :type name: str
        """

        # execute
        maya.cmds.rename(self.fullName(), name)

    def setNamespace(self, namespace):
        """set the namespace of the node

        :param namespace: new namespace of the node
        :type namespace: str
        """

        # init
        mfn = self.MFn()

        # prepare new name
        name = mfn.name()
        newName = '{}:{}'.format(namespace, maya.api.OpenMaya.MNamespace.stripNamespaceFromName(name))

        # rename
        if newName != name:
            mfn.setName(newName)

    def setAttributeValues(self, attributeValues):
        """set the values of the attributes to the node

        :param attributeValues: values to set to the attributes of the node - ``{attr1: value1, attr2: value2 ...}``
        :type attributeValues: dict
        """

        # init
        failedCommands = []

        # execute
        for attributeName, attributeValue in attributeValues.items():

            # bypass non-existing attributes
            if not self.hasAttribute(attributeName):
                continue

            # get the attribute
            attribute = self.attribute(attributeName)

            # bypass if value is already correct
            if attributeValue == attribute.value():
                continue

            # bypass non settable attributes
            if not attribute.isSettable():
                continue

            # set the attribute value (store the one who raised errors)
            try:
                attribute.setValue(attributeValue)
            except RuntimeError:
                failedCommands.append(attribute.fullName())
                continue

        # warn user that some attributes have not been set
        if failedCommands:
            maya.cmds.warning("Some attributes have not been updated because of a maya command error: "
                              "{}".format(", ".join(failedCommands)))

    def upstream(self, depth=0, nodeTypes=None, nodeTypesIncluded=True):
        """get the upstream nodes of the Node

        :param depth: the desired upstream depth - default is 0, meaning all upstreams will be parsed
        :type depth: int

        :param nodeTypes: types of nodes to get - default is all node types
        :type nodeTypes: list[str or :class:`cgp_maya_utils.constants.NodeType`]

        :param nodeTypesIncluded: ``True`` : given types are included - ``False`` : given types are excluded
        :type nodeTypesIncluded: bool

        :return: the upstream nodes of the Node
        :rtype: list[:class:`cgp_maya_utils.scene.Node`]
        """

        # return an empty list if no attribute types are valid
        if not nodeTypes and not nodeTypesIncluded:
            return []

        # get upstream nodes - prune the first element which is the current node
        history = maya.cmds.listHistory(self.fullName(), breadthFirst=True, levels=depth)
        nodes = [cgp_maya_utils.scene._api.node(node) for node in history[1:]] if history else []

        # return nodes whatever their types
        if not nodeTypes and nodeTypesIncluded:
            return nodes

        # return nodes matching types
        return [node
                for node in nodes
                if (nodeTypesIncluded and node.nodeType() in nodeTypes)
                or (not nodeTypesIncluded and node.nodeType() not in nodeTypes)]

    # PROTECTED COMMANDS #

    def _attributesValuesIgnoredAttributes(self):
        """get the name of the attributes that have to me ignored by the `attributeValues` public command

        :return: the name of the attributes that have to me ignored by the `attributeValues` public command
        :rtype: list[str]
        """

        # return
        return ['publishedNodeInfo']


class DagNode(Node):
    """node object that manipulates any kind of dag node
    """

    # ATTRIBUTES #

    _MFN = maya.api.OpenMaya.MFnDagNode()
    _TYPE = cgp_maya_utils.constants.NodeType.DAG_NODE

    # COMMANDS #

    def child(self, name):
        """get a child of the DagNode

        :param name: the name of the child - can reach deeper descendant with names like ``child|grandChild|...``
        :type name: str

        :return: the child of the DagNode
        :return: :class:`cgp_maya_utils.scene.DagNode`
        """

        # init
        fullName = '{}|{}'.format(self.fullName(), name)

        # return
        return cgp_maya_utils.scene._api.node(fullName)

    def children(self, namePattern=None, nodeTypes=None, asExactNodeTypes=False, recursive=False):
        """get children nodes of the node

        :param namePattern: the pattern the child name has to match - ex: '*pelvis*'
        :type namePattern: str

        :param nodeTypes: the node types the child has to match
        :type nodeTypes: list[str]

        :param asExactNodeTypes: ``True`` : list only exact node types - ``False`` : all types inheriting node types
        :type asExactNodeTypes: bool

        :param recursive: ``True`` : get children recursively - ``False`` : get only direct children
        :type recursive: bool

        :return: the children nodes
        :rtype: list[DagNode]
        """

        # init
        parentName = self.fullName()

        # query relatives
        if nodeTypes:
            nodes = [relative for nodeType in nodeTypes for relative
                     in maya.cmds.listRelatives(parentName,
                                                allDescendents=recursive,
                                                fullPath=True,
                                                type=nodeType) or []]
        else:
            nodes = maya.cmds.listRelatives(parentName, allDescendents=recursive, fullPath=True) or []

        # filter with regex
        if namePattern:
            nameRegex = '^' + namePattern.replace('*', '.*') + '$'
            nodes = [node for node in nodes if re.match(nameRegex, node.split('|')[-1])]

        # apply exact type option
        if asExactNodeTypes and nodeTypes:
            nodes = [node for node in nodes if maya.cmds.nodeType(node) in nodeTypes]

        # return
        return [cgp_maya_utils.scene._api.node(item) for item in nodes]

    def fullName(self):
        """get the full name of the node

        :return: the full name of the node
        :rtype: str
        """

        # return
        return self.MFn().fullPathName()

    def hasChild(self, name):
        """check a child exists under the DagNode

        :param name: the name of the child - can reach deeper descendant with names like ``child|grandChild|...``
        :type name: str

        :return: ``True`` : the child exists - ``False`` : the child does not exist
        :return: bool
        """

        # init
        fullName = '{}|{}'.format(self.fullName(), name)

        # return
        return maya.cmds.objExists(fullName)

    def name(self, withNamespace=True):
        """get the name of the DagNode

        :param withNamespace: ``True`` : The name is returned with its namespace if there is any
                              ``False`` : The name is return without its namespace if there is any
        :type withNamespace: bool

        :return: the name of the node
        :rtype: str
        """

        # this command should be removed in the future as the partial name and the name are two separated concepts
        # for now we have side effects in published structure when we remove this command
        # we need to be more specific on what we want to be returned in the `.data()`
        partialName = self.partialName()

        # return
        return partialName if '|' in partialName else super(DagNode, self).name(withNamespace=withNamespace)

    def objectSets(self):
        """get the object sets containing the node

        :return: the object sets containing the node
        :rtype: :class:`cgp_maya_utils.scene.ObjectSet`
        """

        # init
        name = self.fullName()

        # return
        return [cgp_maya_utils.scene._api.node(objectSet)
                for objectSet in maya.cmds.ls(type=cgp_maya_utils.constants.NodeType.OBJECT_SET, long=True)
                if maya.cmds.sets(name, isMember=objectSet)]

    def parent(self):
        """get the parent of the DagNode

        :return: the parent of the DagNode
        :rtype: DagNode
        """

        # execute
        parents = maya.cmds.listRelatives(self.fullName(), parent=True, fullPath=True)

        # return
        return cgp_maya_utils.scene._api.node(parents[0]) if parents else None

    def partialName(self):
        """get the shortest unique name (aka partial name) of the node

        :return: the shortest unique name of the node
        :rtype: str
        """

        # return
        return self.MFn().partialPathName()

    def setParentingIndex(self, value, relative=False):
        """set the node parenting index - parenting index is the position of the node under its parent in the outliner

        :param value: value to set on the parenting index
        :type value: int

        :param relative: ``True`` : index is updated relative to the current position of the node -
                         ``False`` : index is set as absolute position of the node
        :type relative: bool
        """

        # in case of absolute index
        if not relative:

            # get siblings
            siblings = self.parent().children(recursive=False)

            # check if the index is in range
            if (value > 0 and abs(value) > len(siblings) - 1) or (value < 0 and abs(value) > len(siblings)):
                raise IndexError("Sibling absolute index out of range. "
                                 "Current index limits are: [{}, {}]".format(-len(siblings), len(siblings) - 1))

            # maya does not supply an absolute reordering
            # so we need to move the node to the top and then move it in relative mode
            maya.cmds.reorder(self.fullName(), front=True)

            # modulo to accept both positive and negative indexes (python lists like)
            value = value % len(siblings)

        # move up/down node in siblings
        if value:
            maya.cmds.reorder(self.fullName(), relative=value)

    def setParent(self, parent=None, maintainOffset=True):
        """set the parent of the DagNode

        :param parent: DagNode used to parent the DagNode to - If None, parent to scene root
        :type parent: str or :class:`cgp_maya_utils.scene.DagNode`

        :param maintainOffset: ``True`` : dagNode current position is maintained
                               ``False`` : dagNode current position is not maintained
        :type maintainOffset: bool
        """

        # init
        fullName = self.fullName()

        # parent to world
        if parent is None and maya.cmds.listRelatives(fullName, parent=True):
            maya.cmds.parent(fullName, world=True)
            return

        # update parent
        parent = str(parent)

        # return
        if not maya.cmds.objExists(parent) or str(parent) == self.parent():
            return

        # execute
        if maintainOffset:
            maya.cmds.parent(fullName, parent)
        else:
            maya.cmds.parent(fullName, parent, relative=True)

    def parentingIndex(self):
        """get the node parenting index - parenting index is the position of the node under its parent in the outliner

        :return: the parenting index
        :rtype: int
        """

        # return
        return self.parent().children(recursive=False).index(self)


class ObjectSet(Node):
    """node object that manipulates an ``objectSet`` node
    """

    # ATTRIBUTES

    _TYPE = cgp_maya_utils.constants.NodeType.OBJECT_SET

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, members=None, connections=None, attributeValues=None, name=None, **__):
        """create an objectSet

        :param members: nodes to add as members to the objectSet
        :type members: list[str or :class`cgp_maya_utils.scene.Node`]

        :param connections: connections to set on the created objectSet
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the created objectSet
        :type attributeValues: dict

        :param name: name of the created objectSet
        :type name: str

        :return: the node object
        :rtype: :class:`cgp_maya_utils.scene.ObjectSet`
        """

        # init
        objectSet = super(ObjectSet, cls).create(cls._TYPE,
                                                 connections=connections,
                                                 attributeValues=attributeValues,
                                                 name=name)

        # set members
        if members:
            objectSet.setMembers(members)

        # return
        return objectSet

    # COMMANDS #

    def addMembers(self, nodes):
        """add nodes to the existing members of the objectSet

        :param nodes: nodes to add as members
        :type nodes: list[str or :class:`cgp_maya_utils.scene.Node`]
        """

        # execute
        maya.cmds.sets(nodes, edit=True, addElement=self.fullName())

    def clear(self):
        """clear the objectSet of all members
        """

        # execute
        maya.cmds.sets(edit=True, clear=self.fullName())

    def data(self):
        """get the data necessary to store the objectSet node on disk and/or recreate it from scratch

        :return: the data of the objectSet node
        :rtype: dict
        """

        # init
        data = super(ObjectSet, self).data()

        # update data
        data['members'] = [member.name() for member in self.members()]

        # return
        return data

    def delete(self):
        """delete the objectSet
        """

        # disconnect connections to avoid auto deletion of empty set members
        for connection in self.connections():
            connection.disconnect()

        # delete
        super(ObjectSet, self).delete()

    def hasMember(self, node):
        """check if the node is a member of the objectSet

        :param node: node to check
        :type node: str or :class:`cgp_maya_utils.scene.Node`

        :return: ``True`` : node is a member of the objectSet - ``False`` : the node is not a member of the objectSet
        :rtype: bool
        """

        # return
        return maya.cmds.sets(node, isMember=self.fullName())

    def members(self):
        """get the members of the objectSet

        :return: the nodes contained in the objectSet
        :rtype: list[Node]
        """

        # return
        return [cgp_maya_utils.scene._api.node(node)
                for node in maya.cmds.sets(self.fullName(), query=True) or []]

    def removeMembers(self, nodes):
        """remove the nodes from the objectSet

        :param nodes: nodes to remove from the objectSet
        :type nodes: list[str or :class:`cgp_maya_utils.scene.Node`]
        """

        # execute
        maya.cmds.sets(nodes, remove=self.fullName())

    def setMembers(self, nodes):
        """set the members of the objectSet

        :param nodes: nodes to set as members of the objectSet
        :type nodes: list[str or :class`cgp_maya_utils.scene.Node`]
        """

        # clear set
        self.clear()

        # add members
        self.addMembers(nodes)


class Reference(Node):
    """node object that manipulates a ``reference`` node
    """

    # ATTRIBUTES

    _TYPE = cgp_maya_utils.constants.NodeType.REFERENCE

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, file_, namespace=None, name=None, parent=None, **kwargs):
        """create a reference

        :param file_: path of the file to reference
        :type file_: str

        :param namespace: namespace of the created reference - default is root namespace ``:``
        :type namespace: str

        :param parent: the dag node which will contain the referenced dag nodes - default is scene root
        :type parent: str or :class:`cgp_maya_utils.scene.DagNode`

        :return: the created reference
        :rtype: :class:`cgp_maya_utils.scene.Reference`
        """

        # init
        instance = None
        namespace = namespace or ':'

        # execute
        file_ = maya.cmds.file(file_, reference=True, namespace=namespace)

        # find the newly created reference node
        for referenceNode in maya.cmds.ls(exactType='reference'):

            # get reference file name
            try:
                currentFileName = maya.cmds.referenceQuery(referenceNode, filename=True)

            # an error could be raised if the reference is not associated to a file - eg: 'sharedReferenceNode'
            except RuntimeError:
                continue

            # return
            if currentFileName == file_:
                instance = cls(referenceNode)

        # error
        if not instance:
            raise RuntimeError('No reference node associated to file: {}'.format(file_))

        # set name
        if name:
            instance.setLock(False)
            instance.setName(name)
            instance.setLock(True)

        # set the parent of the referenced nodes
        if parent:
            for node in instance.nodes():
                if node.fullName().count('|') == 1:
                    node.setParent(parent)

        # return
        return instance

    # COMMANDS #

    def data(self):
        """get the data necessary to store the reference node on disk and/or recreate it from scratch

        :return: the data of the reference
        :rtype: dict
        """

        # init
        data = super(Reference, self).data()

        # update data
        data['file_'] = self.file_()
        data['namespace'] = self.namespace().fullName(asAbsolute=False)

        # return
        return data

    def delete(self):
        """delete the reference
        """

        # init
        file_ = self.file_()

        # remove reference if there is an associated file
        if file_:
            maya.cmds.file(file_, removeReference=True)
            return

        # delete node if there is no associated file
        fullName = self.fullName()
        maya.cmds.lockNode(fullName, lock=False)
        maya.cmds.delete(fullName)

    def file_(self):
        """get the file associated with the reference node

        :return: the file of the reference node
        :rtype: str
        """

        # execute
        try:
            return maya.cmds.referenceQuery(self.fullName(), filename=True)
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
        namespace = self.namespace().name()

        # import objects
        copyFile = maya.cmds.referenceQuery(self.fullName(), filename=True, withoutCopyNumber=False)
        maya.cmds.file(copyFile, importReference=True)

        # clean namespace
        if namespaceSubstitute is not None:

            # rename content
            for obj in maya.cmds.namespaceInfo(namespace, listNamespace=True, recurse=True):
                if maya.cmds.objExists(obj):
                    maya.cmds.rename(obj, obj.replace(':', namespaceSubstitute))

            # remove namespace
            maya.cmds.namespace(removeNamespace=namespace)

    def isLoaded(self):
        """check if the reference is loaded

        :return: ``True`` : the reference is loaded - ``False`` : the reference is unloaded
        :rtype: bool
        """

        # return
        return maya.cmds.referenceQuery(self.fullName(), isLoaded=True)

    def load(self):
        """load the reference
        """

        # execute
        maya.cmds.file(self.file_(), loadReferenceDepth='asPrefs', loadReference=self.fullName())

    def namespace(self):
        """get the namespace of the reference

        :return: the namespace of the reference
        :rtype: :class:`cgp_maya_utils.scene.Namespace`
        """

        # get namespace
        copyFile = maya.cmds.referenceQuery(self.fullName(), filename=True, withoutCopyNumber=False)
        namespace = maya.cmds.file(copyFile, query=True, namespace=True)

        # return
        return cgp_maya_utils.scene._api.namespace(namespace) if self.file_() else None

    def nodes(self):
        """get the nodes referenced by the reference

        :return: the nodes referenced by the reference
        :rtype: list[:class:`cgp_maya_utils.scene.Node`]
        """

        # return
        return [cgp_maya_utils.scene._api.node(name)
                for name in maya.cmds.referenceQuery(self.fullName(), nodes=True, dagPath=True)]

    def setNamespace(self, namespace, renameNode=True):
        """set the namespace of the reference

        :param namespace: namespace to set on the reference
        :type namespace: str

        :param renameNode: ``True`` : the reference node is renamed - ``False`` : the reference node is not renamed
        :type renameNode: bool
        """

        # errors
        if self.namespace == namespace:
            maya.cmds.warning('reference already has {0} namespace'.format(namespace))
            return

        if not self.file_():
            maya.cmds.warning('can\'t set namespace on reference that doesn\'t have a file path set')
            return

        if maya.cmds.namespace(exists=namespace):
            maya.cmds.warning('{0} is already existing'.format(namespace))
            return

        # get info
        isLocked = self.isLocked()

        # set namespace
        maya.cmds.file(self.file_(), edit=True, namespace=namespace)

        # rename node
        if renameNode:
            self.setLock(False)
            self.setName('{0}RN'.format(namespace))
            self.setLock(isLocked)

    def unload(self):
        """unload the reference
        """

        # execute
        maya.cmds.file(self.file_(), unloadReference=self.fullName())
