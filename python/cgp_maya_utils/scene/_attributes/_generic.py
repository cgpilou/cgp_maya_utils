"""
generic attribute object library
"""

# imports third-parties
import maya.cmds

# import local
import cgp_maya_utils.scene._api


# GENERIC OBJECTS #


class Connection(object):
    """connection object that manipulates live or virtual connection between two attributes
    """

    # INIT #

    def __init__(self, source, destination):
        """Connection class initialization

        :param source: attribute that drives the connection - ``node.attribute`` or ``Attribute``
        :type source: str or :class:`cgp_maya_utils.scene.Attribute`

        :param destination: attribute that is driven by the connection - ``node.attribute`` or ``Attribute``
        :type destination: str or :class:`cgp_maya_utils.scene.Attribute`
        """

        # errors
        if str(source) == str(destination):
            raise ValueError('Connection can\'t have identical source and destination')

        # set attributes
        self._source = (source
                        if isinstance(source, Attribute)
                        else cgp_maya_utils.scene._api.attribute(source))

        self._destination = (destination
                             if isinstance(destination, Attribute)
                             else cgp_maya_utils.scene._api.attribute(destination))

    def __repr__(self):
        """the representation of the connection

        :return: the representation of the connection
        :rtype: str
        """

        # return
        return '{0}(\'{1}\', \'{2}\')'.format(self.__class__.__name__,
                                              self.source().fullName(),
                                              self.destination().fullName())

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, source, destination):
        """create a connection

        :param source: attribute that drives the connection - ``node.attribute``
        :type source: str

        :param destination: attribute that is driven by the connection - ``node.attribute``
        :type destination: str

        :return: the created connection
        :rtype: :class:`cgp_maya_utils.scene.Connection`
        """

        # init
        connectionObject = cls(source, destination)
        connectionObject.connect()

        # return
        return connectionObject

    @classmethod
    def get(cls, node, attributes=None, sources=True, destinations=True, nodeTypes=None,
            nodeTypesIncluded=True, skipConversionNodes=False):
        """get the connections from the specified node

        :param node: node to get the connections from
        :type node: str or :class:`cgp_maya_utils.scene.Node`

        :param attributes: list of attributes to get the connections from - get all if nothing specified
        :type attributes: list[str]

        :param sources: ``True`` : get the source connections - ``False`` does not get source connections
        :type sources: bool

        :param destinations: ``True`` : get the destination connections - ``False`` does not get destination connections
        :type destinations: bool

        :param nodeTypes: types of nodes used to get the connections - All if nothing is specified
        :type nodeTypes: list[str]

        :param nodeTypesIncluded: ``True`` : include specified node types - ``False`` : exclude specified node types
        :type nodeTypesIncluded: bool

        :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the connections
        :rtype: list[:class:`cgp_maya_utils.scene.Connection`]
        """

        # init
        toQueries = ['{0}.{1}'.format(node, attr) for attr in attributes] if attributes else [str(node)]
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
            for connection in connections:

                # check if not is a connectedType
                isValid = bool(set(maya.cmds.nodeType(connection[index], inherited=True)) & set(nodeTypes))

                # update
                if (not nodeTypes and nodeTypesIncluded
                        or nodeTypes and nodeTypesIncluded and isValid
                        or nodeTypes and not nodeTypesIncluded and not isValid):
                    data.append(cls(*connection))

        # return
        return data

    # COMMANDS #

    def connect(self):
        """connect the connection
        """

        # execute
        if not self.isConnected():
            maya.cmds.connectAttr(self.source(), self.destination(), force=True)

    def data(self):
        """data necessary to store the compound attribute on disk and/or recreate it from scratch

        :return: the data of the connection
        :rtype: tuple
        """

        # return
        return self.source().fullName(), self.destination().fullName()

    def destination(self):
        """the destination attribute of the connection

        :return: the destination attribute
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # return
        return self._destination

    def disconnect(self):
        """disconnect the connection
        """

        # execute
        if self.isConnected():
            maya.cmds.disconnectAttr(self.source(), self.destination())

    def isConnected(self):
        """check if the connection exists or not

        :return: ``True`` : connection is live - ``False`` : connection is virtual
        :rtype: bool
        """

        # return
        return maya.cmds.isConnected(self.source(), self.destination())

    def setDestination(self, node=None, attribute=None):
        """set the destination of the connection

        :param node: the new name of the destination node - keep current if None is specified
        :type node: str

        :param attribute: the new name of the destination attribute - keep current if None is specified
        :type attribute: str
        """

        # get infos
        isConnected = self.isConnected()
        node = node or self.destination().node()
        attribute = attribute or self.destination().name()

        # disconnect connection if necessary
        if isConnected:
            self.disconnect()

        # set attribute
        self._destination = cgp_maya_utils.scene._api.attribute('{0}.{1}'.format(node, attribute))

        # connect if necessary
        if isConnected:
            self.connect()

    def setSource(self, node=None, attribute=None):
        """set the source of the connection

        :param node: the new name of the source node - keep current if None is specified
        :type node: str

        :param attribute: the new name of the source attribute - keep current if None is specified
        :type attribute: str
        """

        # get infos
        isConnected = self.isConnected()
        node = node or self.source().node()
        attribute = attribute or self.source().name()

        # disconnect connection
        self.disconnect()

        # set attribute
        self._source = cgp_maya_utils.scene._api.attribute('{0}.{1}'.format(node, attribute))

        # connect if necessary
        if isConnected:
            self.connect()

    def source(self):
        """the source attribute of the connection

        :return: the source attribute
        :rtype: :class:`cgp_maya_utis.scene.Attribute`
        """

        # return
        return self._source


class Attribute(object):
    """attribute object that manipulates any kind of attribute
    """

    # ATTRIBUTES #

    _attributeType = 'attribute'

    # INIT #

    def __init__(self, fullName):
        """Attribute class initialization

        :param fullName: full name of the attribute - ``node.attribute``
        :type fullName: str
        """

        # set fullName
        self._fullName = fullName

    def __eq__(self, attribute):
        """check if the Attribute is identical to the other attribute

        :param attribute: attribute to compare to
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`

        :return: ``True`` : attributes are identical - ``False`` : attributes are different
        :rtype: bool
        """

        # return
        return self.fullName() == str(attribute)

    def __ne__(self, attribute):
        """check if the Attribute is different to the other attribute

        :param attribute: attribute to compare to
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`

        :return: ``True`` : attributes are different - ``False`` : attributes are identical
        :rtype: bool
        """

        # return
        return self.fullName() != str(attribute)

    def __repr__(self):
        """the representation of the attribute

        :return: the representation of the attribute
        :rtype: str
        """

        # return
        return '{0}(\'{1}\')'.format(self.__class__.__name__, self.fullName())

    def __str__(self):
        """the print of the attribute

        :return: the print the attribute
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

        :param connectionDestinations: attributes to connect as destination -
                                       ``[node1.attribute1, node2.attribute2 ...]``
        :type connectionDestinations: list[str] or list[:class:`cgp_maya_utils.scene.Attribute`]

        :return: the created attribute
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # execute
        try:
            maya.cmds.addAttr(node, longName=name, attributeType=cls._attributeType)
        except RuntimeError:
            maya.cmds.addAttr(node, longName=name, dataType=cls._attributeType)

        # get attribute object
        attrObject = cls('{0}.{1}'.format(node, name))

        # set if value specified
        if value:
            attrObject.setValue(value)

        # connect attribute
        attrObject.connect(source=connectionSource, destinations=connectionDestinations)

        # return
        return attrObject

    # COMMANDS #

    def attributeType(self):
        """the type of the attribute

        :return: the type of the attribute
        :rtype: str
        """

        # execute
        return maya.cmds.getAttr(self.fullName(), type=True)

    def connect(self, source=None, destinations=None):
        """connect the attribute to the source and destinations

        :param source: source attribute to connect to the attribute - ``node.attribute`` or ``Attribute``
        :type source: str or :class:`cgp_maya_utils.scene.Attribute`

        :param destinations: destination attributes to connect to the attribute -
                             ``[node1.attribute1 ...]`` or ``[Attribute1 ...]``
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

    def connections(self, nodeTypes=None, source=True, destinations=True, nodeTypesIncluded=True,
                    skipConversionNodes=False):
        """get the connections of the attribute

        :param nodeTypes: types of nodes used to get the connections - All if nothing is specified
        :type nodeTypes: list[str]

        :param source: define whether or not the command will get the source connection
        :type source: bool

        :param destinations: define whether or not the command will get the destination connections
        :type destinations: bool

        :param nodeTypesIncluded: ``True`` : include specified node types - ``False`` : exclude specified node types
        :type nodeTypesIncluded: bool

        :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` conversion nodes are not skipped
        :type skipConversionNodes: bool

        :return: the connections of the attribute
        :rtype: list[:class:`cgp_maya_utils.scene.Connection`]
        """

        # return
        return Connection.get(self.node(),
                              attributes=[self.name()],
                              sources=source,
                              destinations=destinations,
                              nodeTypes=nodeTypes,
                              nodeTypesIncluded=nodeTypesIncluded,
                              skipConversionNodes=skipConversionNodes)

    def data(self, skipConversionNodes=True):
        """data necessary to store the attribute on disk and/or recreate it from scratch

        :param skipConversionNodes: ``True`` : conversion nodes are skipped - ``False`` conversion nodes are not skipped
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
                'connectionDestinations': [connection.source().fullName() for connection in destinationConnections],
                'name': self.name(),
                'node': self.node().name(),
                'attributeType': self.attributeType(),
                'value': self.value()}

    def delete(self):
        """delete the attribute
        """

        # execute
        maya.cmds.deleteAttr(self.fullName())

    def disconnect(self, source=True, destinations=True, destinationAttributes=None):
        """disconnect the attribute from the source and the specified destinations

        :param source: defines whether or not the source connected attribute will be disconnected
        :type source: bool

        :param destinations: defines whether or not the destination connected attribute will be disconnected
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

    def isLocked(self):
        """check if the attribute is locked

        :return: ``True`` : it is locked - ``False`` : it is not locked
        :rtype: bool
        """

        # return
        return maya.cmds.getAttr(self.fullName(), lock=True)

    def isUserDefined(self):
        """check if the attribute is user defined

        :return: ``True`` : it is user defined - ``False`` : it is not user defined
        :rtype: bool
        """

        # return
        return self.name() in maya.cmds.listAttr(self.node(), userDefined=True)

    def name(self):
        """the name of the attribute

        :return: the name of the attribute
        :rtype: str
        """

        # return
        return self.fullName().partition('.')[-1]

    def node(self):
        """the node on which the attribute lives

        :return: the node of the attribute
        :rtype: :class:`cgp_maya_utils.scene.Node`
        """

        # return
        return cgp_maya_utils.scene._api.node(self.fullName().split('.')[0])

    def setLock(self, isLocked):
        """set the lock state of the attribute

        :param isLocked: ``True`` attribute will be locked - ``False`` : attribute will be unlocked
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

        :param value: value used to set the attribute
        :type value: any
        """

        # execute
        try:
            maya.cmds.setAttr(self.fullName(), value)
        except RuntimeError:
            maya.cmds.setAttr(self.fullName(), value, type=self.attributeType())

    def value(self):
        """the value of the attribute

        :return: the value of the attribute
        :rtype: any
        """

        # return
        return maya.cmds.getAttr(self.fullName())
