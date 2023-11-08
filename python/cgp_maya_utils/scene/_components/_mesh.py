"""
mesh component object library
"""


# imports python
import re

# imports 3rd parties
import maya.api.OpenMaya
import maya.cmds

# imports local
import cgp_maya_utils.constants
from . import _generic


# MESH COMPONENT OBJECTS #


class MeshComponent(_generic.TransformComponent):
    """component object that manipulates any kind of mesh component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.MESH_COMPONENT

    # COMMANDS #

    def edges(self):
        """get the edges related to the component

        :return: the edges related to the component
        :rtype: list[:class:`cgp_maya_utils.scene.Edge`]
        """

        # get names
        shapeName = self.fullName().split('.')[0]
        names = ["{}.{}".format(shapeName, name.split(".", 1)[-1])  # replace the transform name by the shape name
                 for name in maya.cmds.ls(maya.cmds.polyListComponentConversion(self, toEdge=True), flatten=True)]

        # return objects
        return [Edge(name) for name in names]

    def faces(self):
        """get the faces related to the component

        :return: the faces related to the component
        :rtype: list[:class:`cgp_maya_utils.scene.Face`]
        """

        # get names
        shapeName = self.fullName().split('.')[0]
        names = ["{}.{}".format(shapeName, name.split(".", 1)[-1])  # replace the transform name by the shape name
                 for name in maya.cmds.ls(maya.cmds.polyListComponentConversion(self, toFace=True), flatten=True)]

        # return objects
        return [Face(name) for name in names]

    def uvCoordinates(self):
        """get the UV coordinates of the component

        :return: the UV coordinates of the component
        :rtype: tuple[float]
        """

        # init
        mesh = self.shape()
        vertices = [self] if isinstance(self, Vertex) else self.vertices()
        positions = [vertex.position(worldSpace=True) for vertex in vertices]
        borderVertices = [vertex for vertex in vertices if vertex.isUvShellBorder()]

        # as the final result is the average uv coordinates of all the vertices.
        # if a vertex is on the border of an uv shell, it can point in fact to a totally different uv position.
        # to avoid bad result we slightly offset the stored positions of the border vertices
        # so we force those positions to be on the correct uv shell
        for index, vertex in enumerate(vertices):
            if vertex not in borderVertices:
                continue

            # get the average position
            averagePosition = [sum([position[0] for position in positions]) / len(positions),
                               sum([position[1] for position in positions]) / len(positions),
                               sum([position[2] for position in positions]) / len(positions)]

            # move the stored position a little bit to the average one
            positions[index] = [positions[index][0] * 0.999 + averagePosition[0] * 0.001,
                                positions[index][1] * 0.999 + averagePosition[1] * 0.001,
                                positions[index][2] * 0.999 + averagePosition[2] * 0.001]

        # get the average uv coordinates from the vertices list
        uvList = [mesh.closestUV(position, worldSpace=True) for position in positions]
        uCoordinate = sum([uv[0] for uv in uvList]) / len(uvList)
        vCoordinate = sum([uv[1] for uv in uvList]) / len(uvList)

        # return
        return uCoordinate, vCoordinate

    def uvMaps(self):
        """get the uv maps related to the component

        :return: the uv maps related to the component
        :rtype: list[:class:`cgp_maya_utils.scene.UvMap`]
        """

        # get names
        shapeName = self.fullName().split('.')[0]
        names = ["{}.{}".format(shapeName, name.split(".", 1)[-1])  # replace the transform name by the shape name
                 for name in maya.cmds.ls(maya.cmds.polyListComponentConversion(self, toUV=True), flatten=True)]

        # return objects
        return [UvMap(name) for name in names]

    def uvShells(self):
        """get the ids of the uv shells related to the component

        Note: if the uv shell is sewn on itself this command will return multiple occurrences of the same id

        :return: the uv shell ids related to the components
        :rtype: list[int]
        """

        # init
        mesh = self.shape()
        mfnMesh = maya.api.OpenMaya.MFnMesh(mesh.MFn().getPath())
        uvMapIndexes = [index for uvMap in self.uvMaps() for index in uvMap.indexes()]

        # get the uv set and the uv shell ids
        # TODO: should we handle multiple uv sets ?
        uvSet = maya.cmds.polyUVSet(mesh, query=True, allUVSets=True)[0]
        uvShellsCount, uvShellIdForMap = mfnMesh.getUvShellsIds(uvSet)

        # return shell ids related to the current component
        return [uvShellId for uvMapId, uvShellId in enumerate(uvShellIdForMap) if uvMapId in uvMapIndexes]

    def isUvShellBorder(self):
        """check if the current component in on the border or a uv shell

        :return: ``True`` : the component is on the border - ``False`` : the component is not on the border
        :rtype: bool
        """

        # init
        vertices = [self] if isinstance(self, Vertex) else self.vertices()

        # check if a vertex is related to multiple uv shells
        for vertex in vertices:
            if len(vertex.uvShells()) > 1:
                return True

        # return False by default
        return False

    def vertices(self):
        """get the vertices related to the component

        :return: the vertices related to the component
        :rtype: list[:class:`cgp_maya_utils.scene.Vertex`]
        """

        # get names
        shapeName = self.fullName().split('.')[0]
        names = ["{}.{}".format(shapeName, name.split(".", 1)[-1])  # replace the transform name by the shape name
                 for name in maya.cmds.ls(maya.cmds.polyListComponentConversion(self, toVertex=True), flatten=True)]

        # return objects
        return [Vertex(name) for name in names]


class Edge(MeshComponent):
    """component object that manipulates an ``edge`` component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.EDGE

    # COMMANDS #

    def faces(self):
        """get the faces related to the component

        :return: the faces related to the component
        :rtype: list[:class:`cgp_maya_utils.scene.Face`]
        """

        # init
        mesh = self.shape()

        # get indexes (`polyInfo` needs string parsing but avoid `polyListComponentConversion` inconsistencies)
        # note that `polyInfo` could be pretty long to respond, openMaya api seems to be the best solution here
        polyInfo = maya.cmds.polyInfo(self, edgeToFace=True)
        indexes = ([int(index) for match in re.finditer(r"([0-9]+)", polyInfo[0]) for index in match.groups()][1:]
                   if polyInfo
                   else [])

        # return
        return [Face("{}.{}[{}]".format(mesh, cgp_maya_utils.constants.ComponentType.FACE, index))
                for index in indexes]

    def vertices(self):
        """get the vertices related to the component

        :return: the vertices related to the component
        :rtype: list[:class:`cgp_maya_utils.scene.Vertex`]
        """

        # init
        mesh = self.shape()

        # get indexes (`polyInfo` needs string parsing but avoid `polyListComponentConversion` inconsistencies)
        # note that `polyInfo` could be pretty long to respond, openMaya api seems to be the best solution here
        polyInfo = maya.cmds.polyInfo(self, edgeToVertex=True)
        indexes = ([int(index) for match in re.finditer(r"([0-9]+)", polyInfo[0]) for index in match.groups()][1:]
                   if polyInfo
                   else [])

        # return
        return [Vertex("{}.{}[{}]".format(mesh, cgp_maya_utils.constants.ComponentType.VERTEX, index))
                for index in indexes]


class Face(MeshComponent):
    """component object that manipulates a ``face`` component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.FACE

    # COMMANDS #

    def edges(self):
        """get the edges related to the component

        :return: the edges related to the component
        :rtype: list[:class:`cgp_maya_utils.scene.Edge`]
        """

        # init
        mesh = self.shape()

        # get indexes (`polyInfo` needs string parsing but avoid `polyListComponentConversion` inconsistencies)
        # note that `polyInfo` could be pretty long to respond, openMaya api seems to be the best solution here
        polyInfo = maya.cmds.polyInfo(self, faceToEdge=True)
        indexes = ([int(index) for match in re.finditer(r"([0-9]+)", polyInfo[0]) for index in match.groups()][1:]
                   if polyInfo
                   else [])

        # return
        return [Edge("{}.{}[{}]".format(mesh, cgp_maya_utils.constants.ComponentType.EDGE, index))
                for index in indexes]

    def vertices(self):
        """get the vertices related to the component

        :return: the vertices related to the component
        :rtype: list[:class:`cgp_maya_utils.scene.Vertex`]
        """

        # init
        mesh = self.shape()

        # get indexes (`polyInfo` needs string parsing but avoid `polyListComponentConversion` inconsistencies)
        # note that `polyInfo` could be pretty long to respond, openMaya api seems to be the best solution here
        polyInfo = maya.cmds.polyInfo(self, faceToVertex=True)
        indexes = ([int(index) for match in re.finditer(r"([0-9]+)", polyInfo[0]) for index in match.groups()][1:]
                   if polyInfo
                   else [])

        # return
        return [Vertex("{}.{}[{}]".format(mesh, cgp_maya_utils.constants.ComponentType.VERTEX, index))
                for index in indexes]


class UvMap(MeshComponent):
    """component object that manipulates an ``uvMap`` component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.UV_MAP

    # COMMANDS #

    def position(self, worldSpace=False):
        """get the position of the uv map

        :param worldSpace: ``True`` : the position is queried in worldSpace -
                           ``False`` : the position is queried in local
        :type worldSpace: bool

        :return: the position of the uvMap
        :rtype: list[float]
        """

        # return
        return maya.cmds.pointPosition(self, world=True) if worldSpace else maya.cmds.pointPosition(self, local=True)

    def uvCoordinates(self):
        """get the UV coordinates of the component

        :return: the UV coordinates of the component
        :rtype: tuple[float]
        """

        # return
        return self.shape().closestUV(self.position(worldSpace=True), worldSpace=True)


class Vertex(MeshComponent):
    """component object that manipulates an ``vertex`` component
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.ComponentType.VERTEX

    # COMMAND #

    def edges(self):
        """get the edges related to the component

        :return: the edges
        :rtype: list[:class:`cgp_maya_utils.scene.Edge`]
        """

        # init
        mesh = self.shape()

        # get indexes (`polyInfo` needs string parsing but avoid `polyListComponentConversion` inconsistencies)
        # note that `polyInfo` could be pretty long to respond, openMaya api seems to be the best solution here
        polyInfo = maya.cmds.polyInfo(self, vertexToEdge=True)
        indexes = ([int(index) for match in re.finditer(r"([0-9]+)", polyInfo[0]) for index in match.groups()][1:]
                   if polyInfo
                   else [])

        # return
        return [Edge("{}.{}[{}]".format(mesh, cgp_maya_utils.constants.ComponentType.EDGE, index))
                for index in indexes]

    def faces(self):
        """get the faces related to the component

        :return: the faces
        :rtype: list[:class:`cgp_maya_utils.scene.Face`]
        """

        # init
        mesh = self.shape()

        # get indexes (`polyInfo` needs string parsing but avoid `polyListComponentConversion` inconsistencies)
        # note that `polyInfo` could be pretty long to respond, openMaya api seems to be the best solution here
        polyInfo = maya.cmds.polyInfo(self, vertexToFace=True)
        indexes = ([int(index) for match in re.finditer(r"([0-9]+)", polyInfo[0]) for index in match.groups()][1:]
                   if polyInfo
                   else [])

        # return
        return [Face("{}.{}[{}]".format(mesh, cgp_maya_utils.constants.ComponentType.FACE, index))
                for index in indexes]

    def position(self, worldSpace=False):
        """get the position of the vertex

        :param worldSpace: defines whether or not the values will be got in worldSpace
        :type worldSpace: bool

        :return: the position
        :rtype: list[float]
        """

        # return
        return maya.cmds.pointPosition(self, world=True) if worldSpace else maya.cmds.pointPosition(self, local=True)

    def uvCoordinates(self):
        """get the UV coordinates of the component

        :return: the UV coordinates of the component
        :rtype: tuple[float]
        """

        # return
        return self.shape().closestUV(self.position(worldSpace=True), worldSpace=True)
