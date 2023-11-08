"""
connection object library
"""

# imports third-parties
import maya.cmds

# import local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api


# CONNECTION OBJECT #


class Connection(object):
    """connection object that manipulates live or virtual connection between two attributes
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.MiscType.CONNECTION

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
                        if isinstance(source, cgp_maya_utils.scene.Attribute)
                        else cgp_maya_utils.scene._api.attribute(source))

        self._destination = (destination
                             if isinstance(destination, cgp_maya_utils.scene.Attribute)
                             else cgp_maya_utils.scene._api.attribute(destination))

    def __repr__(self):
        """get the representation of the connection

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

    # COMMANDS #

    def connect(self):
        """connect the connection
        """

        # execute
        if not self.isConnected():
            maya.cmds.connectAttr(self.source(), self.destination(), force=True)

    def data(self):
        """get the data necessary to store the compound attribute on disk and/or recreate it from scratch

        :return: the data of the connection
        :rtype: tuple
        """

        # return
        return self.source().fullName(), self.destination().fullName()

    def destination(self):
        """get the destination attribute of the connection

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

        # get info
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

        # get info
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
        """get the source attribute of the connection

        :return: the source attribute
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # return
        return self._source