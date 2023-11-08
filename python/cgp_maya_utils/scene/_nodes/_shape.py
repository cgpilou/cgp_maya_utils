"""
shape object library
"""

# imports python
import os

# imports third-parties
import maya.api.OpenMaya
import maya.cmds
import maya.mel

# imports rodeo
import cgp_generic_utils.constants
import cgp_generic_utils.decorators
import cgp_generic_utils.files

# imports local
import cgp_maya_utils.decorators
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api
from . import _generic
from . import _transform


# BASE OBJECT #


class Shape(_generic.DagNode):
    """node object that manipulates a ``shape`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.SHAPE

    # COMMANDS #

    def duplicate(self, newTransform=False):
        """duplicate the shape

        :param newTransform: ``True`` : duplicated shape has a new transform -
                             ``False`` duplicate shape has the same transform
        :type newTransform: bool

        :return: the duplicated shape
        :rtype: :class:`cgp_maya_utils.scene.Shape`
        """

        # duplicate the shape (it will create a new transform)
        transform = cgp_maya_utils.scene._api.node(maya.cmds.duplicate(self)[0])
        shape = transform.shapes()[0]

        # return
        if newTransform:
            return shape

        # move shape under original transform
        shape.setParent(self.parent(), maintainOffset=False)
        transform.delete()

        # return
        return shape

    def original(self):
        """get the original shape (usually aka shapeOrig) of the Shape

        :return: the original shape of the Shape
        :rtype: :class:`cgp_maya_utils.scene.Shape`
        """

        # get shapes in upstream
        upstreamShapes = self.upstream(nodeTypes=cgp_maya_utils.constants.NodeType.SHAPES)

        # if no shape in upstream, the current shape is original
        if not upstreamShapes:
            return self

        # parse sibling shapes
        shapeIndexes = {}
        for availableShape in self.parent().shapes():
            if availableShape == self:
                continue

            # ignore shape which is not in upstream
            if availableShape not in upstreamShapes:
                continue

            # store the shape upstream index
            upstreamIndex = upstreamShapes.index(availableShape)
            shapeIndexes[upstreamIndex] = availableShape

        # return the most far upstream shape
        return shapeIndexes[max(shapeIndexes.keys())] if shapeIndexes else self

    def setParent(self, parent=None, maintainOffset=True):
        """set the parent of the DagNode

        :param parent: DagNode used to parent the DagNode to - If None, parent to scene root
        :type parent: str or :class:`cgp_maya_utils.scene.DagNode`

        :param maintainOffset: ``True`` : dagNode current position is maintained
                               ``False`` : dagNode current position is not maintained
        :type maintainOffset: bool
        """

        # error
        if not parent:
            raise ValueError('Unable to parent a shape to the root of the scene.')

        # relative
        if not maintainOffset:
            maya.cmds.parent(self.fullName(), parent, shape=True, relative=True)

        # absolute
        else:

            # create temp locator
            # TODO: locator creation / delete are killing perf
            #       we need to replace the creation of the locator by a pure mathematical approach
            tempLoc = _transform.Transform(maya.cmds.spaceLocator()[0])

            # snap locator to position
            tempLoc.match(self.parent())

            # parent shape to locator
            maya.cmds.parent(self.fullName(), tempLoc.name(), shape=True, relative=True)

            # parent locator to target - freeze transform
            tempLoc.setParent(parent)
            tempLoc.freeze()

            # parent shape to target
            maya.cmds.parent(self.fullName(), parent, shape=True, relative=True)

            # delete temp locator
            tempLoc.delete()


class GeometryShape(Shape):
    """node object that manipulates a ``geometryShape`` node
    """

    # ATTRIBUTES #

    _COMPONENT_TYPES = cgp_maya_utils.constants.ComponentType.ALL
    _INPUT_GEOMETRY = None
    _LIBRARY = None
    _OUTPUT_GEOMETRY = None
    _TYPE = cgp_maya_utils.constants.NodeType.GEOMETRY_SHAPE

    # PROPERTIES #

    @property
    def pointComponents(self):
        """get the pointComponents of the shape

        :return: the pointComponents of the shape
        :rtype: list[Component]
        """

        # execute
        return []

    # OBJECT COMMANDS #

    @classmethod
    def import_(cls, style, parent=None, name=None):
        """import a shape

        :param style: style of the shape to import - ``ex : cube, circle ...``
        :type style: str

        :param parent: transform to which the shape will be parented - new transform if nothing specified
        :type parent: str or :class:`cgp_maya_utils.scene.Transform`

        :param name: name of the imported shape
        :type name: str

        :return: the imported shape
        :rtype: Shape
        """

        # get the file path
        filePath = os.path.join(cls._LIBRARY, '{0}.json'.format(style))

        # errors
        if not os.path.isfile(filePath):
            raise RuntimeError('{0} is not an existing {1} in the library'.format(style, cls._TYPE))

        if cls._TYPE == cgp_maya_utils.constants.NodeType.SHAPE:
            raise NotImplementedError('generic shape can\'t be imported')

        # get data
        fileObject = cgp_generic_utils.files.entity(filePath)
        data = fileObject.read()

        # update data
        data['transform'] = parent
        data['name'] = name

        # create shape
        shapeObject = cls.create(worldSpace=False, **data)

        # return
        return shapeObject

    # COMMANDS #

    def count(self):
        """get the point count of the shape

        :return: the point count of the shape
        :rtype: int
        """

        # execute
        return 0

    def component(self, name):
        """get the component of the shape

        :param name: the name of the component to get - ``eg : 'vtx[0]'``
        :type name: str

        :return: the component of the shape
        :rtype: Component
        """

        # validate name
        if not self.hasComponent(name):
            raise ValueError('Shape {0!r} has no component named {1!r}'.format(self, name))

        # return
        return cgp_maya_utils.scene._api.component('{}.{}'.format(self.name(), name))

    def components(self, componentTypes=None):
        """get the components of the shape

        :param componentTypes: the types of the component to get - all if nothing is specified
        :type componentTypes: list[:class:`cgp_maya_utils.constants.ComponentType`]

        :return: the components of the shape
        :rtype: list[Component]
        """

        # init
        componentTypes = componentTypes or self._COMPONENT_TYPES

        # list component names
        components = ['{}.{}'.format(self, name.split('.', 1)[-1])  # replace the transform name by the shape name
                      for componentType in componentTypes
                      for name in maya.cmds.ls('{}.{}[*]'.format(self, componentType), flatten=True)]

        # return component objects
        return [cgp_maya_utils.scene._api.component(name) for name in components]

    def data(self, worldSpace=False):
        """get the data necessary to store the shape node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : shape position is in worldSpace - ``False`` : shape position is in local
        :type worldSpace: bool

        :return: the data of the shape
        :rtype: dict
        """

        # init
        data = super(Shape, self).data()

        # update data
        data['color'] = self.attribute('overrideColor').value()
        data['count'] = self.count()
        data['points'] = self.points()
        data['positions'] = self.positions(worldSpace=worldSpace)
        data['transform'] = self.parent().name()

        # return
        return data

    def export(self, name):
        """export the shape in the library

        :param name: name of the shape in the library
        :type name: str

        :return: the exported file
        :rtype: :class:`cgp_generic_utils.files.JsonFile`
        """

        # get the file path
        filePath = os.path.join(self._LIBRARY, '{0}.json'.format(name))

        # errors
        if os.path.isfile(filePath):
            raise RuntimeError('{0} already exists in the library'.format(name))

        if self._TYPE == cgp_maya_utils.constants.NodeType.SHAPE:
            raise NotImplementedError('generic shape can\'t be exported')

        # execute
        return cgp_generic_utils.files.createFile(filePath, self.data())

    def geometryFilters(self, geometryFilterTypes=None, geometryFilterTypesIncluded=True):
        """get the geometryFilters bounded to the shape

        :param geometryFilterTypes: types of geometryFilters to get - all if nothing is specified
        :type geometryFilterTypes: list[str]

        :param geometryFilterTypesIncluded: ``True`` : geometryFilter types are included -
                                            ``False`` : geometryFilter types are excluded
        :type geometryFilterTypesIncluded: bool

        :return: the geometryFilters bound to the shape
        :rtype: list[GeometryFilter]
        """

        # init
        validDeformers = []

        # get all deformers
        allDeformers = maya.cmds.findDeformers(self.fullName()) or []

        # get deformerTypes to query
        if not geometryFilterTypes and geometryFilterTypesIncluded:
            validDeformers = allDeformers

        elif geometryFilterTypes and geometryFilterTypesIncluded:
            validDeformers = [deformer
                              for deformer in allDeformers
                              if maya.cmds.nodeType(deformer) in geometryFilterTypes]

        elif geometryFilterTypes and not geometryFilterTypesIncluded:
            validDeformers = [deformer
                              for deformer in allDeformers
                              if maya.cmds.nodeType(deformer) not in geometryFilterTypes]

        # return
        return [cgp_maya_utils.scene._api.node(deformer) for deformer in validDeformers]

    def hasComponent(self, name):
        """check if the given component exists on the shape

        :param name: the name of the component to get - eg: 'vtx[0]'
        :type name: str
        """

        # validate name
        componentType = name.split("[")[0]
        if componentType not in self._COMPONENT_TYPES:
            raise ValueError("'{}' is not a valid component type. "
                             "Valid component types are: {}".format(componentType, ", ".join(self._COMPONENT_TYPES)))

        # maya.cmds.ls('shape.vtx[500]') will return 'shape.vtx[488]' if there is only 488 vertices on the shape
        # so we can get the closest existing component name
        closestComponents = maya.cmds.ls("{}.{}".format(self, name))
        closestName = closestComponents[0].split(".", 1)[-1] if closestComponents else None

        # return
        return closestName == name

    def isDeformable(self):
        """check if the shape is deformable

        :return: ``True`` : the shape is deformable - ``False`` : the shape is not deformable
        :rtype: bool
        """

        # return
        return (not self.isReferenced()
                and bool(self.fullName() in maya.cmds.ls(self.fullName(), type='deformableShape', long=True)))

    def isDeformed(self):
        """check if the shape is deformed

        :return: ``True`` : the shape is deformed - ``False`` : the shape is not deformed
        :rtype: bool
        """

        # return
        return bool(maya.cmds.findDeformers(self.fullName()))

    def isIntermediate(self):
        """check if the shape is intermediate

        :return: ``True`` : the shape is intermediate - ``False`` : the shape is not intermediate
        :rtype: bool
        """

        # return
        return self.attribute('intermediateObject').value()

    def match(self, shape, worldSpace=False):
        """match the shape to the specified shape

        :param shape: shape to match the current shape to
        :type shape: str or :class:`cgp_maya_utils.scene.Shape`

        :param worldSpace: ``True`` : match is in worldSpace - ``False`` : match is in local
        :type worldSpace: bool
        """

        # get shape
        shape = cgp_maya_utils.scene._api.node(str(shape))

        # errors
        if not shape.nodeType() == self.nodeType():
            raise RuntimeError('{0} has not the same type -  expected : {2}'
                               .format(shape.name(), shape.nodeType(), self.nodeType()))

        # execute
        self.setPositions(shape.positions(worldSpace=worldSpace), worldSpace=worldSpace)

    def mirror(self, mirrorPlane=None, worldSpace=False):
        """mirror the shape

        :param mirrorPlane: the plane used to perform the mirror - default is ``cgp_generic_utils.constants.MirrorPlane.YZ``
        :type mirrorPlane: :class:`cgp_generic_utils.constants.MirrorPlane`

        :param worldSpace: ``True`` : mirror is in worldSpace - ``False`` : mirror is in local
        :type worldSpace: bool
        """

        # init
        mirrorPlane = mirrorPlane or cgp_generic_utils.constants.MirrorPlane.YZ

        # errors
        if mirrorPlane not in cgp_generic_utils.constants.MirrorPlane.ALL:
            raise ValueError('{0} is not a valid mirror plane {1}'
                             .format(mirrorPlane, cgp_generic_utils.constants.MirrorPlane.ALL))

        # execute
        self.setPositions(self.mirroredPositions(mirrorPlane=mirrorPlane, worldSpace=worldSpace), worldSpace=worldSpace)

    def mirroredPositions(self, mirrorPlane=None, worldSpace=False):
        """get the mirror positions of the points of the shape

        :param mirrorPlane: the plane used to perform the mirror - default is ``cgp_generic_utils.constants.MirrorPlane.YZ``
        :type mirrorPlane: str

        :param worldSpace: ``True`` : positions are worldSpace - ``False`` : positions are local
        :type worldSpace: bool

        :return: the mirrored positions of the points
        :rtype: list[list[int, float]]
        """

        # init
        data = []
        mirrorPlane = mirrorPlane or cgp_generic_utils.constants.MirrorPlane.YZ

        # errors
        if mirrorPlane not in cgp_generic_utils.constants.MirrorPlane.ALL:
            raise ValueError('{0} is not a valid mirror plane {1}'
                             .format(mirrorPlane, cgp_generic_utils.constants.MirrorPlane.ALL))

        # execute
        for position in self.positions(worldSpace=worldSpace):

            if mirrorPlane == cgp_generic_utils.constants.MirrorPlane.XY:
                data.append([position[0], position[1], -1 * position[2]])

            elif mirrorPlane == cgp_generic_utils.constants.MirrorPlane.YZ:
                data.append([-1 * position[0], position[1], position[2]])

            else:
                data.append([position[0], -1 * position[1], position[2]])

        # return
        return data

    def points(self):
        """get the points of the shape

        :return: the points of the shape
        :rtype: list[]
        """

        # execute
        return []

    def positions(self, worldSpace=False):
        """get the point positions of the shape

        :param worldSpace: ``True`` : positions are worldSpace - ``False`` : positions are local
        :type worldSpace: bool

        :return: the point positions of the shape
        :rtype: list[list[float]]
        """

        # get shape points
        points = self.points()

        # return
        return (zip(*[iter(maya.cmds.xform(points, query=True, worldSpace=worldSpace, translation=True))] * 3)
                if points else [])

    def rotate(self, values, worldSpace=False, aroundBoundingBoxCenter=False):
        """rotate the shape using the specified values

        :param values: the values used to rotate the shape
        :type values: list[int, float]

        :param worldSpace: ``True`` : rotation is in worldSpace -
                           ``False`` : rotation is in local
        :type worldSpace: bool

        :param aroundBoundingBoxCenter: ``True`` : rotation around bounding box center -
                                        ``False`` : rotation around objet pivot
        :type aroundBoundingBoxCenter: bool
        """

        # execute
        maya.cmds.rotate(values[0], values[1], values[2],
                         self.points(),
                         worldSpace=worldSpace,
                         centerPivot=aroundBoundingBoxCenter)

    def scale(self, values, aroundBoundingBoxCenter=False):
        """scale the shape using the specified values

        :param values: the values used to scale the shape
        :type values: list[int, float]

        :param aroundBoundingBoxCenter: ``True`` : rotation around bounding box center -
                                        ``False`` : rotation around objet pivot
        :type aroundBoundingBoxCenter: bool
        """

        # execute
        if not aroundBoundingBoxCenter:
            maya.cmds.scale(values[0], values[1], values[2], self.points())
        else:
            boundingBoxCenter = maya.cmds.objectCenter(self.fullName(), gl=True)
            maya.cmds.scale(values[0], values[1], values[2], self.points(), pivot=boundingBoxCenter)

    def setColor(self, color=None):
        """set the color of the shape

        :param color: the color channel values to set to the shape - ``indexValue`` or ``[r, g, b]``
        :type color: int or list[int]
        """

        # enable if specified
        enabled = 1 if color is not None else 0
        self.attribute('overrideEnabled').setValue(enabled)

        # set color
        if color:
            self.attribute('overrideColor').setValue(color)

    def setIntermediate(self, isIntermediate):
        """set the intermediate status of the shape

        :param isIntermediate: ``True`` : the status is set to intermediate -
                               ``False`` : the status is set to not intermediate
        :type isIntermediate: bool
        """

        # return
        return self.attribute('intermediateObject').setValue(isIntermediate)

    def setPositions(self, positions, worldSpace=False):
        """set the point positions of the shape

        :param positions: the positions to set on the points of the shape -
                          ``[[x1, y1, z1], [x2, y2, z2], ...]`` - len(positions) = self.count()
        :type positions: list[list[int, float]]

        :param worldSpace: ``True`` : positions are set in worldSpace - ``False`` : positions are set in local
        :type worldSpace: bool
        """

        # errors
        if not len(positions) == self.count():
            raise RuntimeError('data is invalid - data count : {0} - expected : {1}'
                               .format(len(positions), self.count()))

        # execute
        for index, position in enumerate(positions):
            maya.cmds.xform(self.points()[index], ws=worldSpace, t=position)

    def translate(self, values, worldSpace=False):
        """translate the shape using the specified values

        :param values: the values used to translate the shape
        :type values: list[int, float]

        :param worldSpace: ``True`` : translation is in worldSpace - ``False`` : translation is in local
        :type worldSpace: bool
        """

        # get current values
        currentValues = self.positions(worldSpace=worldSpace)

        # execute
        for index, point in enumerate(self.points()):
            maya.cmds.xform(point, worldSpace=worldSpace, translation=[currentValues[index][0] + values[0],
                                                                       currentValues[index][1] + values[1],
                                                                       currentValues[index][2] + values[2]])


# SHAPES OBJECTS #


class Camera(Shape):
    """node object that manipulates a ``camera`` node
    """

    # ATTRIBUTES #

    _MFN = maya.api.OpenMaya.MFnCamera()
    _TYPE = cgp_maya_utils.constants.NodeType.CAMERA


class Follicle(Shape):
    """node object that manipulates a ``follicle`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.FOLLICLE


# GEOMETRY SHAPES OBJECTS #


class NurbsCurve(GeometryShape):
    """node object that manipulates a ``nurbsCurve`` node
    """

    # ATTRIBUTES #

    _COMPONENT_TYPES = cgp_maya_utils.constants.ComponentType.NURBS_CURVE
    _LIBRARY = cgp_maya_utils.constants.Environment.NURBS_CURVE_LIBRARY
    _INPUT_GEOMETRY = 'create'
    _OUTPUT_GEOMETRY = 'local'
    _TYPE = cgp_maya_utils.constants.NodeType.NURBS_CURVE

    # PROPERTIES

    @property
    def pointComponents(self):
        """get the components of a point of the shape

        :return: the components
        :rtype: list[str]
        """

        # return
        return ['xValue', 'yValue', 'zValue']

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, positions, transform=None, form=None, degree=None, color=None,
               worldSpace=False, attributeValues=None, connections=None, name=None, **__):
        """create a nurbsCurve

        :param positions: the positions of the points of the nurbsCurve
        :type positions: list[list[int, float]]

        :param transform: the transform under which the shape will be parented
        :type transform: str or :class:`cgp_maya_utils.scene.Transform`

        :param form: the form of the nurbsCurve - default is ``cgp_maya_utils.constants.GeometryData.OPEN``
        :type form: :class:`cgp_maya_utils.constants.ShapeFormType`

        :param degree: the degree of the nurbsCurve - default is ``cgp_maya_utils.constants.GeometryDegree.CUBIC``
        :type degree: :class:`cgp_maya_utils.constants.GeometryDegree`

        :param color: the color of the nurbsCurve
        :type color: list[int, float]

        :param worldSpace: ``True`` : the nurbsCurve is created in worldSpace -
                           ``False`` : the nurbsCurve is created in local
        :type worldSpace: bool

        :param attributeValues: the attribute values to set on the created nurbsCurve
        :type attributeValues: dict

        :param connections: the connections to set on the created nurbsCurve
        :type connections: list[tuple[str]]

        :param name: the name of the created nurbsCurve
        :type name: str

        :return: the created nurbsCurve
        :rtype: :class:`cgp_maya_utils.scene.NurbsCurve`
        """

        # init
        form = form or cgp_maya_utils.constants.GeometryData.OPEN
        degree = degree or cgp_maya_utils.constants.GeometryData.CUBIC

        # errors
        if form not in cgp_maya_utils.constants.GeometryData.FORMS:
            raise ValueError('{0} is not a valid shape form type'.format(form))

        if degree not in cgp_maya_utils.constants.GeometryData.DEGREES:
            raise ValueError('{0} is not a valid geometry degree'.format(degree))

        # TODO: refactor this part so all curves can be built directly with maya.cmds.curve
        #       would be nice eventually to implement knot support
        # create closed curve
        if not (form == cgp_maya_utils.constants.GeometryData.OPEN):

            # create curve
            curve = maya.cmds.circle(degree=degree,
                                     useTolerance=False,
                                     sections=len(positions),
                                     constructionHistory=False)[0]

            # close curve if shape is linear - maya only create linear circle as open curve ...
            if degree == cgp_maya_utils.constants.GeometryData.LINEAR:
                maya.cmds.closeCurve(curve,
                                     preserveShape=2,
                                     constructionHistory=False,
                                     replaceOriginal=True)

        # create opened curve
        else:
            curve = maya.cmds.curve(worldSpace=True, degree=degree, point=positions)

        # get shapeObject
        shapeObject = cls(maya.cmds.listRelatives(curve, shapes=True)[0])

        # set positions
        shapeObject.setPositions(positions, worldSpace=worldSpace)

        # set transform
        if transform:
            tempTransform = shapeObject.parent()
            shapeObject.setParent(transform, maintainOffset=worldSpace)
            tempTransform.delete()

        # set name
        if name:
            shapeObject.setName(name)

        # set color
        if color:
            shapeObject.setColor(color)

        # set attribute values
        if attributeValues:
            shapeObject.setAttributeValues(attributeValues)

        # set connections
        if connections:
            shapeObject.setConnections(connections)

        # return
        return shapeObject

    # COMMANDS #

    def count(self):
        """get the count of cv points

        :return: the count of cv points
        :rtype: int
        """

        # open
        if self.attribute('form').value() == cgp_maya_utils.constants.GeometryData.OPEN:
            return self.attribute('spans').value() + self.attribute('degree').value()

        # periodic
        elif self.attribute('form').value() == cgp_maya_utils.constants.GeometryData.PERIODIC:
            return self.attribute('spans').value()

        # closed
        else:
            return self.attribute('spans').value() + self.attribute('degree').value() - 1

    def data(self, worldSpace=False):
        """get the data necessary to store the nurbsCurve node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : the point positions are queried is in worldSpace -
                           ``False`` : the point positions are queried is in local
        :type worldSpace: bool

        :return: the data of the nurbsCurve
        :rtype: dict
        """

        # init
        data = super(NurbsCurve, self).data(worldSpace=worldSpace)

        # update data
        data['degree'] = self.attribute('degree').value()
        data['form'] = self.attribute('form').value()
        data['spans'] = self.attribute('spans').value()

        # return
        return data

    def isOpened(self):
        """check if the curve is opened or closed

        :return: ``True`` : shape is opened - ``False`` : shape is closed
        :rtype: bool
        """

        # return
        return self.attribute('form').value() == cgp_maya_utils.constants.GeometryData.OPEN

    def points(self):
        """get the cv points of the nurbsCurve

        :return: the cv points of the nurbsCurve
        :rtype: list[str]
        """

        # return
        return ['{0}.cv[{1}]'.format(self.name(), index) for index in range(self.count())]


class NurbsSurface(GeometryShape):
    """node object that manipulates a ``nurbsSurface`` node
    """

    # ATTRIBUTES #

    _COMPONENT_TYPES = cgp_maya_utils.constants.ComponentType.NURBS_SURFACE
    _INPUT_GEOMETRY = 'create'
    _LIBRARY = cgp_maya_utils.constants.Environment.NURBS_SURFACE_LIBRARY
    _OUTPUT_GEOMETRY = 'local'
    _TYPE = cgp_maya_utils.constants.NodeType.NURBS_SURFACE

    # PROPERTIES #

    @property
    def pointComponents(self):
        """get the components of a point of the shape

        :return: the components
        :rtype: list[str]
        """

        # return
        return ['xValue', 'yValue', 'zValue']

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, positions, transform=None, formU=None, formV=None, degreeU=None, degreeV=None, knotsU=None,
               knotsV=None, color=None, worldSpace=False, attributeValues=None, connections=None, name=None, **__):
        """create a nurbsSurface

        :param positions: the positions of the points of the nurbsSurface
        :type positions: list[list[int, float]]

        :param transform: the transform under which the shape will be parented
        :type transform: str or :class:`cgp_maya_utils.scene.Transform`

        :param formU: the formU of the nurbsSurface - default is ``cgp_maya_utils.constants.GeometryData.OPEN``
        :type formU: :class:`cgp_maya_utils.constants.GeometryData`

        :param formV: the formU of the nurbsSurface - default is ``cgp_maya_utils.constants.GeometryData.OPEN``
        :type formV: :class:`cgp_maya_utils.constants.GeometryData`

        :param degreeU: the degreeU of the nurbsSurface - default is ``cgp_maya_utils.constants.GeometryData.CUBIC``
        :type degreeU: :class:`cgp_maya_utils.constants.GeometryData`

        :param degreeV: the degreeU of the nurbsSurface - default is ``cgp_maya_utils.constants.GeometryData.CUBIC``
        :type degreeV: :class:`cgp_maya_utils.constants.GeometryData`

        :param knotsU: the knotU of the nurbsSurface
        :type knotsU: list[int]

        :param knotsV: the knotV of the nurbsSurface
        :type knotsV: list[int]

        :param color: the color of the nurbsSurface
        :type color: list[int, float]

        :param worldSpace: ``True`` : the nurbsSurface is created is in worldSpace -
                           ``False`` : the nurbsSurface is created is in local
        :type worldSpace: bool

        :param attributeValues: the attribute values to set on the created nurbsSurface
        :type attributeValues: dict

        :param connections: the connections to set on the created nurbsSurface
        :type connections: list[tuple[str]]

        :param name: the name of the created nurbsSurface
        :type name: str

        :return: the created nurbsSurface
        :rtype: :class:`cgp_maya_utils.scene.NurbsSurface`
        """

        # init
        formU = formU or cgp_maya_utils.constants.GeometryData.OPEN
        formV = formV or cgp_maya_utils.constants.GeometryData.OPEN
        degreeU = degreeU or cgp_maya_utils.constants.GeometryData.CUBIC
        degreeV = degreeV or cgp_maya_utils.constants.GeometryData.CUBIC

        # TODO: set automatic the knotU and knotV vector if none specified

        # errors
        for form in [formU, formV]:
            if form not in cgp_maya_utils.constants.GeometryData.FORMS:
                raise ValueError('{0} is not a valid shape form type'.format(form))

        for degree in [degreeU, degreeV]:
            if degree not in cgp_maya_utils.constants.GeometryData.DEGREES:
                raise ValueError('{0} is not a valid geometry degree'.format(form))

        if not knotsU:
            raise ValueError('knotU need to be specified')

        if not knotsV:
            raise ValueError('knotV need to be specified')

        # execute
        shape = maya.cmds.surface(degreeU=degreeU,
                                  degreeV=degreeV,
                                  formU=formU,
                                  formV=formV,
                                  knotU=knotsU,
                                  knotV=knotsV,
                                  point=positions)

        # get shapeObject
        shapeObject = cls(shape)

        # set data
        shapeObject.setPositions(positions, worldSpace=worldSpace)

        # set transform
        if transform:
            tempTransform = shapeObject.parent()
            shapeObject.setParent(transform, maintainOffset=worldSpace)
            tempTransform.delete()

        # set color
        if color:
            shapeObject.setColor(color)

        # set name
        if name:
            shapeObject.setName(name)

        # set attribute values
        if attributeValues:
            shapeObject.setAttributeValues(attributeValues)

        # set connections
        if connections:
            shapeObject.setConnections(connections)

        # return
        return shapeObject

    # COMMANDS #

    def count(self):
        """get the count of cv points

        :return: the count of cv points
        :rtype: int
        """

        # return
        return self.countU() * self.countV()

    def countU(self):
        """get the countU of cv points

        :return: the countU of cv points
        :rtype: int
        """

        # return
        return self.attribute('spansU').value() + self.attribute('degreeU').value()

    def countV(self):
        """get the countV of cv points

        :return: the countV of cv points
        :rtype: int
        """

        # return
        return self.attribute('spansV').value() + self.attribute('degreeV').value()

    def data(self, worldSpace=False):
        """get the data necessary to store the nurbsSurface node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : the point positions are queried in worldSpace -
                           ``False`` : the point positions are queried in local
        :type worldSpace: bool

        :return: the data of the nurbsSurface
        :rtype: dict
        """

        # init
        data = super(NurbsSurface, self).data(worldSpace=worldSpace)

        # update data
        data['countU'] = self.countU()
        data['countV'] = self.countV()
        data['degreeU'] = self.attribute('degreeU').value()
        data['degreeV'] = self.attribute('degreeV').value()
        data['formU'] = self.formU()
        data['formV'] = self.formV()
        data['knotsU'] = self.knotsU()
        data['knotsV'] = self.knotsV()
        data['spansU'] = self.attribute('spansU').value()
        data['spansV'] = self.attribute('spansV').value()

        # return data
        return data

    def formU(self):
        """get the formU of the nurbsSurface

        :return: the formU of the nurbsSurface
        :rtype: int
        """

        # return
        return cgp_maya_utils.constants.GeometryData.FORMS[maya.cmds.getAttr('{0}.formU'.format(self.fullName()))]

    def formV(self):
        """get the formV of the nurbsSurface

        :return: the formV of the nurbsSurface
        :rtype: int
        """

        # return
        return cgp_maya_utils.constants.GeometryData.FORMS[maya.cmds.getAttr('{0}.formV'.format(self.fullName()))]

    def knotsU(self):
        """get the knotU of the nurbsSurface

        :return: the knotU of the nurbsSurface
        :rtype: list[int]
        """

        # create surfaceInfo node
        surfaceInfo = maya.cmds.createNode('surfaceInfo')
        maya.cmds.connectAttr('{0}.worldSpace[0]'.format(self.fullName()),
                              '{0}.inputSurface'.format(surfaceInfo),
                              force=True)

        # get data
        data = maya.cmds.getAttr('{0}.knotsU'.format(surfaceInfo))[0]

        # delete surfaceInfo
        maya.cmds.delete(surfaceInfo)

        # return
        return data

    def knotsV(self):
        """get the knotV of the nurbsSurface

        :return: the knotV of the nurbsSurface
        :rtype: list[int]
        """

        # create surfaceInfo node
        surfaceInfo = maya.cmds.createNode('surfaceInfo')
        maya.cmds.connectAttr('{0}.worldSpace[0]'.format(self.fullName()),
                              '{0}.inputSurface'.format(surfaceInfo),
                              force=True)

        # get data
        data = maya.cmds.getAttr('{0}.knotsV'.format(surfaceInfo))[0]

        # delete surfaceInfo
        maya.cmds.delete(surfaceInfo)

        # return
        return data

    def points(self):
        """get the cv points of the nurbsSurface

        :return: the points
        :rtype: list[str]
        """

        # init
        data = []

        # execute
        for u in range(self.countU()):
            for v in range(self.countV()):
                data.append('{0}.cv[{1}][{2}]'.format(self.name(), u, v))

        # return
        return data


class Mesh(GeometryShape):
    """node object that manipulates a ``mesh`` node
    """

    # ATTRIBUTES #

    _COMPONENT_TYPES = cgp_maya_utils.constants.ComponentType.MESH
    _INPUT_GEOMETRY = 'inMesh'
    _LIBRARY = cgp_maya_utils.constants.Environment.MESH_LIBRARY
    _OUTPUT_GEOMETRY = 'outMesh'
    _TYPE = cgp_maya_utils.constants.NodeType.MESH

    # PROPERTIES #

    @property
    def pointComponents(self):
        """get the components of a point of the shape

        :return: the components
        :rtype: list[str]
        """

        # return
        return ['pntx', 'pnty', 'pntz']

    # OBJECT COMMANDS #

    @classmethod
    def import_(cls, style, parent=None, name=None):
        """import a mesh

        :param style: the style of the mesh to import that exists in the shape library - ex : ``cube`` - ``circle``
        :type style: str

        :param parent: the transform to which the mesh will be parented - new transform if nothing specified
        :type parent: str

        :param name: the name of the imported mesh
        :type name: str

        :return: the imported mesh
        :rtype: :class:`cgp_maya_utils.scene.Mesh`
        """

        # get the file path
        filePath = os.path.join(cls._LIBRARY, '{0}.obj'.format(style))

        # errors
        if not os.path.isfile(filePath):
            raise ValueError('{0} is not an existing {1} in the library'.format(style, cls._TYPE))

        # get data
        fileObject = cgp_generic_utils.files.entity(filePath)
        importedGeo = fileObject.import_(style)

        # get shapeObject
        shapeObject = cls(maya.cmds.listRelatives(importedGeo, shapes=True)[0])

        # parent shape
        if parent:
            tempTransform = shapeObject.parent()
            shapeObject.setParent(parent, maintainOffset=False)
            tempTransform.delete()

        # rename shape
        if name:
            shapeObject.setName(name)

        # return
        return shapeObject

    # COMMANDS #

    def closestFace(self, positionX, positionY, positionZ):
        """get the closest face from the given world coordinates

        :param positionX: the X value of position
        :type positionX: float

        :param positionY: the Y value of position
        :type positionY: float

        :param positionZ: the Z value of position
        :type positionZ: float

        :return: the closest face of the mesh
        :rtype: :class:`cgp_maya_utils.scene.Face`
        """

        # init
        point = maya.api.OpenMaya.MPoint(positionX, positionY, positionZ)
        mesh = maya.api.OpenMaya.MFnMesh(self.MFn().getPath())

        # get the closest face name
        faceIndex = mesh.getClosestPoint(point, space=maya.api.OpenMaya.MSpace.kWorld)[1]
        faceName = '{}.f[{}]'.format(self.name(), faceIndex)

        # return the attribute object
        return cgp_maya_utils.scene.Face(faceName)

    def closestUV(self, position, worldSpace=False):
        """get the closest UV coordinates from the given position

        :param position: the position to get the closest UV from - ``[x, y, z]``
        :type position: list[float]

        :param worldSpace: ``True`` : the position is in worldSpace - ``False`` : the position is in local
        :type worldSpace: bool

        :return: the closest uv coordinates
        :rtype: tuple[float]
        """

        # init
        point = maya.api.OpenMaya.MPoint(*position)
        mesh = maya.api.OpenMaya.MFnMesh(self.MFn().getPath())
        space = maya.api.OpenMaya.MSpace.kWorld if worldSpace else maya.api.OpenMaya.MSpace.kObject

        # get uv
        u, v, _ = mesh.getUVAtPoint(point, space=space)

        # return
        return u, v

    def closestVertex(self, positionX, positionY, positionZ):
        """get the closest vertex from the given world coordinates

        :param positionX: the X value of position
        :type positionX: float

        :param positionY: the Y value of position
        :type positionY: float

        :param positionZ: the Z value of position
        :type positionZ: float

        :return: the closest vertex
        :rtype: :class:`cgp_maya_utils.scene.Vertex`
        """

        # init
        point = maya.api.OpenMaya.MPoint(positionX, positionY, positionZ)
        mesh = maya.api.OpenMaya.MFnMesh(self.MFn().getPath())

        # get face index
        faceIndex = mesh.getClosestPoint(point, space=maya.api.OpenMaya.MSpace.kWorld)[1]

        # get the closest vertex name
        vertexDistances = {mesh.getPoint(vertexIndex, maya.api.OpenMaya.MSpace.kWorld).distanceTo(point): vertexIndex
                           for vertexIndex in mesh.getPolygonVertices(faceIndex)}
        vertexName = "{}.vtx[{}]".format(self.name(), vertexDistances[min(vertexDistances.keys())])

        # return the attribute object
        return cgp_maya_utils.scene.Vertex(vertexName)

    def count(self):
        """get the count of vertices of the mesh

        :return: the count of vertices of the mesh
        :rtype: int
        """

        # return
        return maya.cmds.polyEvaluate(self.fullName(), vertex=True)

    @cgp_maya_utils.decorators.KeepSelection()
    def export(self, name):
        """export the mesh in the library

        :param name: name of the mesh in the library
        :type name: str

        :return: the exported file
        :rtype: :class:`cgp_maya_utils.files.ObjFile`
        """

        # get the file path
        filePath = os.path.join(cgp_maya_utils.constants.Environment.MESH_LIBRARY, '{0}.obj'.format(name))

        # errors
        if os.path.isfile(filePath):
            raise ValueError('{0} already exists in the library'.format(name))

        # execute
        return cgp_generic_utils.files.createFile(filePath, content=[self.name()])

    def faceFromUV(self, uCoordinate, vCoordinate):
        """get the face matching the given uv coordinates

        :param uCoordinate: the U coordinate
        :type uCoordinate: float

        :param vCoordinate: the V coordinate
        :type vCoordinate: float

        :return: the face
        :rtype: :class:`cgp_maya_utils.scene.Attribute`
        """

        # init
        mesh = maya.api.OpenMaya.MFnMesh(self.MFn().getPath())

        # parse faces until we found the one matching with uv
        for faceIndex in range(mesh.numPolygons):
            try:
                mesh.getPointAtUV(faceIndex, uCoordinate, vCoordinate, space=maya.api.OpenMaya.MSpace.kWorld)
            except RuntimeError:
                continue

            # return the face
            faceName = "{}.f[{}]".format(self.name(), faceIndex)
            return cgp_maya_utils.scene._api.attribute(faceName)

        # return None if no face found
        return None

    def pointFromUV(self, uCoordinate, vCoordinate, face=None):
        """get the point matching the given uv coordinates

        :param uCoordinate: the U coordinate
        :type uCoordinate: float

        :param vCoordinate: the V coordinate
        :type vCoordinate: float

        :param face: the face
        :type face: str ot :class:`cgp_maya_utils.scene.Face`

        :return: the point world coordinates
        :rtype: tuple(float, float, float)
        """

        # init
        mesh = maya.api.OpenMaya.MFnMesh(self.MFn().getPath())

        # get face to parse
        index = cgp_maya_utils.scene.Face(str(face)).indexes()[0] if face else None
        faceIndices = range(mesh.numPolygons) if index is None else [index]

        # parse faces until we found the one matching with uv
        for faceIndex in faceIndices:
            try:
                mPoint = mesh.getPointAtUV(faceIndex, uCoordinate, vCoordinate, space=maya.api.OpenMaya.MSpace.kWorld)
            except RuntimeError:
                continue

            # return the point coordinates
            return mPoint.x, mPoint.y, mPoint.z

        # return None if no point found
        return None, None, None

    def points(self):
        """get the points of the mesh

        :return: the points of the mesh
        :rtype: list[str]
        """

        # return
        return ['{0}.vtx[{1}]'.format(self.name(), index) for index in range(self.count())]

    def positions(self, worldSpace=False):
        """get the point positions of the shape

        :param worldSpace: ``True`` : positions are worldSpace - ``False`` : positions are local
        :type worldSpace: bool

        :return: the point positions of the shape
        :rtype: list[list[float]]
        """

        # init
        mesh = maya.api.OpenMaya.MFnMesh(self.MFn().getPath())
        space = maya.api.OpenMaya.MSpace.kWorld if worldSpace else maya.api.OpenMaya.MSpace.kObject

        # return
        return [(point.x, point.y, point.z) for point in mesh.getFloatPoints(space=space)]

    def uvBorders(self, componentType=None):
        """get the border components of the uv mapping

        :param componentType: the type of the components to get - default is ``cgp_maya_utils.constants.ComponentType.VERTEX``
        :type componentType: :class:`cgp_maya_utils.constants.ComponentType`

        :return: the border components of the uv mapping
        :rtype: list[:class:`cgp_maya_utils.scene.Components`]
        """

        # init
        componentType = componentType or cgp_maya_utils.constants.ComponentType.VERTEX

        # return components on border
        return [component
                for component in self.components(componentTypes=[componentType])
                if component.isUvShellBorder()]

    # PROTECTED COMMANDS #

    def _attributesValuesIgnoredAttributes(self):
        """get the name of the attributes that have to me ignored by the `attributeValues` public command

        :return: the name of the attributes that have to me ignored by the `attributeValues` public command
        :rtype: list[str]
        """

        # return
        return super(Mesh, self)._attributesValuesIgnoredAttributes() + ['edge', 'face', 'uvSet', 'vrts']
