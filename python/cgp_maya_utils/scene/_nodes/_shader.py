"""
misc object library
"""

# imports third parties
import maya.cmds

# imports local
import cgp_maya_utils.constants
from . import _generic


# SHADING OBJECTS #


class ShadingDependNode(_generic.Node):
    """node object that manipulates a ``shadingDependNode`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.SHADING_DEPEND_NODE

    # OBJECT COMMANDS #

    @staticmethod
    def create(nodeType,
               connections=None,
               attributeValues=None,
               name=None,
               shadingEngines=None,
               shadedNodes=None,
               **__):
        """create a ShadingDependNode

        :param nodeType: the type of ShadingDependNode to create
        :type nodeType: :class:`cgp_maya_utils.constants.NodeType`

        :param connections: connections to set on the created ShadingDependNode
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the created ShadingDependNode
        :type attributeValues: dict

        :param name: name of the created ShadingDependNode
        :type name: str

        :param shadingEngines: the shading engines associated to the shader - default is new shading engine
        :type shadingEngines: list[:class:`cgp_maya_utils.scene.ShadingEngine`, str]

        :param shadedNodes: the nodes to assign the ShadingDependNode on
        :type shadedNodes: list[:class:`cgp_maya_utils.scene.Mesh`, str]

        :return: the created ShadingDependNode
        :rtype: :class:`cgp_maya_utils.scene.ShadingDependNode`
        """

        # init
        shadedNodes = shadedNodes or []

        # create shader
        shader = (maya.cmds.shadingNode(nodeType, name=name, asShader=True)
                  if name
                  else maya.cmds.shadingNode(nodeType, asShader=True))
        shaderObject = cgp_maya_utils.scene._api.node(shader)

        # set attributeValues
        if attributeValues:
            shaderObject.setAttributeValues(attributeValues)

        # set connections
        if connections:
            shaderObject.setConnections(connections)

        # get or create the shading engines
        shadingEngines = shadingEngines or [maya.cmds.sets(name='{}SG'.format(shader),
                                                           empty=True,
                                                           renderable=True,
                                                           noSurfaceShader=True)]

        # connect each shading engines
        for shadingEngine in shadingEngines:

            # assign the shader to the shading engine
            shadingEngine = shadingEngine if isinstance(shadingEngine, str) else shadingEngine.fullName()
            maya.cmds.connectAttr('{}.outColor'.format(shader), '{}.surfaceShader'.format(shadingEngine))

            # assign the shading engine to the node
            for shadedNode in shadedNodes:
                maya.cmds.sets(shadedNode, edit=True, forceElement=shadingEngine)

        # return
        return shaderObject

    # COMMANDS #

    def setShadingEngines(self, shadingEngines):
        """set the shading engines of the ShadingDependNode

        :param shadingEngines: the shading engines of the ShadingDependNode
        :type shadingEngines: list[:class:`cgp_maya_utils.scene.ShadingEngine`, str]
        """

        # init
        attribute = self.attribute('outColor')

        # disconnect
        for connection in attribute.connections(source=False, destinations=True):
            connection.disconnect()

        # connect
        for shadingEngine in shadingEngines:
            shadingEngine = shadingEngine if isinstance(shadingEngine, str) else shadingEngine.fullName()
            attribute.connect(destinations=['{}.surfaceShader'.format(shadingEngine)])

    def setShapes(self, nodes):
        """assign shapes to the ShadingDependNode

        :param nodes: the shapes or a parent of the shapes that will be rendered with the ShadingDependNode
        :param nodes: list[:class:`cgp_maya_utils.scene.DagNode`, str]
        """

        # execute
        for engine in self.shadingEngines():
            engine.setMembers(nodes)

    def shadingEngines(self):
        """get the shading engines of the ShadingDependNode

        :return: the shading engines of the ShadingDependNode
        :rtype: list[:class:`cgp_maya_utils.scene.ShadingEngine`]
        """

        # init
        shadingEngines = []

        # collect shading engines
        for connection in self.attribute('outColor').connections(source=False, destinations=True):
            node = connection.destination().node()
            if isinstance(node, cgp_maya_utils.scene.ShadingEngine):
                shadingEngines.append(node)

        # return
        return shadingEngines

    def shapes(self):
        """get the shapes assigned to the ShadingDependNode

        :return: the shapes that will be rendered with the ShadingDependNode
        :rtype: list[:class:`cgp_maya_utils.scene.Shape`]
        """

        # return
        return [node for engine in self.shadingEngines() for node in engine.members()]


class Lambert(ShadingDependNode):
    """node object that manipulates a ``lambert`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.LAMBERT
