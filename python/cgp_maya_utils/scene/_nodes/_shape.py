"""
shape object library
"""

# imports python
import os

# imports third-parties
import cgp_generic_utils.constants
import cgp_generic_utils.files
import maya.cmds

# imports local
import cgp_maya_utils.decorators
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api
from . import _generic
from . import _transform


# BASE OBJECT #


class Shape(_generic.DagNode):
    """node object that manipulates any kind of shape node
    """

    # ATTRIBUTES #

    _nodeType = 'shape'
    _inputGeometry = None
    _outputGeometry = None
    _library = None

    # OBJECT COMMANDS #

    @classmethod
    def import_(cls, style, parent=None, name=None):
        """import a shape

        :param style: style of the shape to import that exists in the shape library - ex : ``cube`` - ``circle``
        :type style: str

        :param parent: transform to which the shape will be parented - new transform if nothing specified
        :type parent: str or :class:`cgp_maya_utils.scene.Transform`

        :param name: name of the shape
        :type name: str

        :return: the imported shape
        :rtype: :class:`cgp_maya_utils.scene.Shape`
        """

        # get the file path
        filePath = os.path.join(cls._library, '{0}.json'.format(style))

        # errors
        if not os.path.isfile(filePath):
            raise RuntimeError('{0} is not an existing {1} in the library'.format(style, cls._nodeType))

        if cls._nodeType == 'shape':
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
        """the count of points

        :return: the count of points
        :rtype: int
        """

        raise NotImplementedError('count function needs to be implemented')

    def data(self, worldSpace=False):
        """data necessary to store the shape node on disk and/or recreate it from scratch

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
        data['transform'] = self.transform().name()

        # return
        return data

    def duplicate(self, newTransform=False):
        """duplicate the shape

        :param newTransform: ``True`` : duplicated shape has a new transform -
                             ``False`` duplicate shape has the same transform
        :type newTransform: bool

        :return: the duplicated shape
        :rtype: :class:`cgp_maya_utils.Shape`
        """

        # create new shape
        newShape = cgp_maya_utils.scene._api.node(maya.cmds.createNode(self.nodeType()))

        # copy newShape from current shape
        newShape.attribute(self._inputGeometry).connect(source=self.attribute(self._outputGeometry))
        maya.cmds.refresh()  # refresh force de create connection to take effects
        newShape.attribute(self._inputGeometry).disconnect()

        # parent shape to original transform
        if not newTransform:
            newShape.setTransform(self.transform(), worldSpace=False, deleteOriginalTransform=True)

        # return
        return newShape

    def export(self, name):
        """export the shape in the library

        :param name: name of the shape in the library
        :type name: str

        :return: the exported file
        :rtype: :class:`cgp_generic_utils.files.JsonFile`
        """

        # get the file path
        filePath = os.path.join(self._library, '{0}.json'.format(name))

        # errors
        if os.path.isfile(filePath):
            raise RuntimeError('{0} already exists in the library'.format(name))

        if self._nodeType == 'shape':
            raise NotImplementedError('generic shape can\'t be exported')

        # execute
        return cgp_generic_utils.files.createFile(filePath, self.data())

    def geometryFilters(self, geometryFilterTypes=None, geometryFilterTypesIncluded=True):
        """the geometryFilters bounded to the shape

        :param geometryFilterTypes: types of geometryFilters to get - All if nothing is specified
        :type geometryFilterTypes: list[str]

        :param geometryFilterTypesIncluded: ``True`` : geometryFilter types are included -
                                            ``False`` : geometryFilter types are excluded
        :type geometryFilterTypesIncluded: bool

        :return: the geometryFilters bound to the shape
        :rtype: list[:class:`cgp_maya_utils.scene.GeometryFilter`]
        """

        # init
        validDeformers = []

        # get all deformers
        allDeformers = maya.cmds.findDeformers(self.name())

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

    def isDeformed(self):
        """check if the shape is deformed

        :return: ``True`` : the shape is deformed - ``False`` : the shape is not deformed
        :rtype: bool
        """

        # return
        return bool(maya.cmds.findDeformers(self.name()))

    def match(self, targetShape, worldSpace=False):
        """match the shape to the target shape

        :param targetShape: shape to match the current shape to
        :type targetShape: str or :class:`cgp_maya_utils.scene.Shape`

        :param worldSpace: ``True`` : match is in worldSpace - ``False`` : match is in local
        :type worldSpace: bool
        """

        # get shape
        targetShape = cgp_maya_utils.scene._api.node(str(targetShape))

        # errors
        if not targetShape.nodeType() == self.nodeType():
            raise RuntimeError('{0} has not the same type -  expected : {2}'
                               .format(targetShape.name(), targetShape.nodeType(), self.nodeType()))

        # execute
        self.setPositions(targetShape.positions(worldSpace=worldSpace), worldSpace=worldSpace)

    def mirror(self, mirrorPlane=None, worldSpace=False):
        """mirror the shape

        :param mirrorPlane: plane used to perform the mirror - default is ``cgp_generic_utils.constants.MirrorPlane.YZ``
        :type mirrorPlane: str

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
        """the mirror positions of the points of the shape

        :param mirrorPlane: plane used to perform the mirror - default is ``cgp_generic_utils.constants.MirrorPlane.YZ``
        :type mirrorPlane: str

        :param worldSpace: ``True`` : positions are worldSpace - ``False`` : positions are local
        :type worldSpace: bool

        :return: the mirrored positions of the points
        :rtype: list[list[float]]
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
        """the points of the shape

        :return: the points of the shape
        :rtype: list[str]
        """

        # execute
        raise NotImplementedError('points function needs to be implemented')

    def positions(self, worldSpace=False):
        """the positions of the points of the shape

        :param worldSpace: ``True`` : positions are worldSpace - ``False`` : positions are local
        :type worldSpace: bool

        :return: the positions of the points
        :rtype: list[list[float]]
        """

        # return
        return zip(*[iter(maya.cmds.xform(self.points(), query=True, worldSpace=worldSpace, translation=True))] * 3)

    def rotate(self, values, worldSpace=False, aroundBoundingBoxCenter=False):
        """rotate the shape

        :param values: values used to rotate the shape
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
        """scale the shape

        :param values: values used to scale the shape
        :type values: list[int, float]

        :param aroundBoundingBoxCenter: If False shape will rotate around obj pivot. Otherwise around boundingBox center
        :type aroundBoundingBoxCenter: bool
        """

        # execute
        if not aroundBoundingBoxCenter:
            maya.cmds.scale(values[0], values[1], values[2], self.points())
        else:
            boundingBoxCenter = maya.cmds.objectCenter(self.name(), gl=True)
            maya.cmds.scale(values[0], values[1], values[2], self.points(), pivot=boundingBoxCenter)

    def setColor(self, color=None):
        """set the color of the shape

        :param color: color channel values to set to the shape - ``indexValue`` or ``[r, g, b]``
        :type color: int or list[int]
        """

        # enable if specified
        enabled = 1 if color is not None else 0
        self.attribute('overrideEnabled').setValue(enabled)

        # set color
        if color:
            self.attribute('overrideColor').setValue(color)

    def setPositions(self, positions, worldSpace=False):
        """set the positions of the points of the shape

        :param positions: positions to set - ``[[x1, y1, z1], [x2, y2, z2], ...]`` - len(positions) = self.count()
        :type positions: list[list[float]]

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

    def setTransform(self, transform, worldSpace=False, deleteOriginalTransform=False):
        """set the transform of the shape

        :param transform: transform the shape will be parented to
        :type transform: str or :class:`cgp_maya_utils.scene.Transform`

        :param worldSpace: ``True`` : parenting occurs in worldSpace -
                           ``False`` : parenting occurs in local
        :type worldSpace: bool

        :param deleteOriginalTransform: ``True`` : original transform is deleted -
                                        ``False`` : original transform remains
        :type deleteOriginalTransform: bool
        """

        # get original transform
        originalTransform = self.transform()

        # relative
        if not worldSpace:
            maya.cmds.parent(self.name(), transform, shape=True, relative=True)

        # absolute
        else:

            # get shape positions
            positions = self.positions(worldSpace=True)

            # parent shape
            maya.cmds.parent(self.name(), transform, shape=True, relative=True)

            # set worldspace positions
            self.setPositions(positions, worldSpace=True)

        # delete original transform if specified
        if deleteOriginalTransform:
            originalTransform.delete()

    def transform(self):
        """the transform of the shape

        :return: the transform of the shape
        :rtype: :class:`cgp_maya_utils.scene.Transform` or :class:`cgp_maya_utils.scene.Joint`
        """

        # get transform node
        xform = maya.cmds.listRelatives(self.name(), parent=True, fullPath=True)[0]

        # return
        return _transform.Transform(xform)

    def translate(self, values, worldSpace=False):
        """translate the shape

        :param values: values used to translate the shape
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


class NurbsCurve(Shape):
    """node object that manipulates a ``nurbsCurve`` shape node
    """

    # ATTRIBUTES #

    _nodeType = 'nurbsCurve'
    _inputGeometry = 'create'
    _outputGeometry = 'local'
    _library = cgp_maya_utils.constants.Environment.NURBS_CURVE_LIBRARY

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, positions, transform=None, form=None, degree=None, color=None,
               worldSpace=False, attributeValues=None, connections=None, name=None, **__):
        """create a nurbsCurve

        :param positions: positions of the points of the nurbsCurve
        :type positions: list[list[int, float]]

        :param transform: transform under which the shape will be parented
        :type transform: str or :class:`cgp_maya_utils.scene.Transform`

        :param form: form of the nurbsCurve - default is ``cgp_maya_utils.constants.ShapeFormType.OPEN``
        :type form: str

        :param degree: degree of the nurbsCurve - default is ``cgp_maya_utils.constants.GeometryDegree.CUBIC``
        :type degree: str

        :param color: color of the nurbsCurve
        :type color: list[int, float]

        :param worldSpace: ``True`` : creation is in worldSpace - ``False`` : creation is in local
        :type worldSpace: bool

        :param attributeValues: attribute values to set on the nurbsCurve
        :type attributeValues: dict

        :param connections: connections to set on the nurbsCurve
        :type connections: list[tuple[str]]

        :param name: name of the nurbsSurface
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

        # create closed curve
        if not form == cgp_maya_utils.constants.GeometryData.OPEN:
            curve = maya.cmds.circle(degree=degree,
                                     useTolerance=False,
                                     sections=len(positions),
                                     constructionHistory=False)[0]

        # create opened curve
        else:
            curve = maya.cmds.curve(worldSpace=True, degree=degree, point=positions)

        # get shapeObject
        shapeObject = cls(maya.cmds.listRelatives(curve, shapes=True)[0])

        # set data
        shapeObject.setPositions(positions, worldSpace=worldSpace)

        if transform:
            shapeObject.setTransform(transform, worldSpace=worldSpace, deleteOriginalTransform=True)
        if name:
            shapeObject.setName(name)
        if color:
            shapeObject.setColor(color)
        if attributeValues:
            shapeObject.setAttributeValues(attributeValues)
        if connections:
            shapeObject.setConnections(connections)

        # return
        return shapeObject

    # COMMANDS #

    def count(self):
        """the count of cv points

        :return: the count of cv points
        :rtype: int
        """

        # return
        if self.isOpened():
            return self.attribute('spans').value() + self.attribute('degree').value()
        else:
            return self.attribute('spans').value()

    def data(self, worldSpace=False):
        """data necessary to store the nurbsCurve node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : shape position is in worldSpace - ``False`` : shape position is in local
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
        """the cv points of the nurbsCurve

        :return: the cv points of the nurbsCurve
        :rtype: list[str]
        """

        # return
        return ['{0}.cv[{1}]'.format(self.name(), index) for index in range(self.count())]


class NurbsSurface(Shape):
    """node object that manipulates a ``nurbsSurface`` shape node
    """

    # ATTRIBUTES #

    _nodeType = 'nurbsSurface'
    _inputGeometry = 'create'
    _outputGeometry = 'local'
    _library = cgp_maya_utils.constants.Environment.NURBS_SURFACE_LIBRARY

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, positions, transform=None, formU=None, formV=None, degreeU=None, degreeV=None, knotsU=None,
               knotsV=None, color=None, worldSpace=False, attributeValues=None, connections=None, name=None, **__):
        """create a nurbsSurface

        :param positions: positions of the points of the nurbsSurface
        :type positions: list[list[int, float]]

        :param transform: transform under which the shape will be parented
        :type transform: str or :class:`cgp_maya_utils.scene.Transform`

        :param formU: formU of the nurbsSurface - default is ``cgp_maya_utils.constants.ShapeFormType.OPEN``
        :type formU: str

        :param formV: formU of the nurbsSurface - default is ``cgp_maya_utils.constants.ShapeFormType.OPEN``
        :type formV: str

        :param degreeU: degreeU of the nurbsSurface - default is ``cgp_maya_utils.constants.GeometryDegree.CUBIC``
        :type degreeU: str

        :param degreeV: degreeU of the nurbsSurface - default is ``cgp_maya_utils.constants.GeometryDegree.CUBIC``
        :type degreeV: str

        :param knotsU: knotU of the nurbsSurface
        :type knotsU: list[int]

        :param knotsV: knotV of the nurbsSurface
        :type knotsV: list[int]

        :param color: color of the nurbsSurface
        :type color: list[int, float]

        :param worldSpace: ``True`` : creation is in worldSpace - ``False`` : creation is in local
        :type worldSpace: bool

        :param attributeValues: attribute values to set on the nurbsSurface
        :type attributeValues: dict

        :param connections: connections to set on the nurbsSurface
        :type connections: list[tuple[str]]

        :param name: name of the nurbsSurface
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

        if transform:
            shapeObject.setTransform(transform, worldSpace=worldSpace, deleteOriginalTransform=True)
        if color:
            shapeObject.setColor(color)
        if name:
            shapeObject.setName(name)
        if attributeValues:
            shapeObject.setAttributeValues(attributeValues)
        if connections:
            shapeObject.setConnections(connections)

        # return
        return shapeObject

    # COMMANDS #

    def count(self):
        """the count of cv points

        :return: the count of cv points
        :rtype: int
        """

        # return
        return self.countU() * self.countV()

    def countU(self):
        """the countU of cv points

        :return: the countU of cv points
        :rtype: int
        """

        # return
        return self.attribute('spansU').value() + self.attribute('degreeU').value()

    def countV(self):
        """the countV of cv points

        :return: the countV of cv points
        :rtype: int
        """

        # return
        return self.attribute('spansV').value() + self.attribute('degreeV').value()

    def data(self, worldSpace=False):
        """data necessary to store the nurbsSurface node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : shape position is in worldSpace - ``False`` : shape position is in local
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
        """the formU of the nurbsSurface

        :return: the formU of the nurbsSurface
        :rtype: int
        """

        # return
        return cgp_maya_utils.constants.GeometryData.FORMS[maya.cmds.getAttr('{0}.formU'.format(self.name()))]

    def formV(self):
        """the formV of the nurbsSurface

        :return: the formV of the nurbsSurface
        :rtype: int
        """

        # return
        return cgp_maya_utils.constants.GeometryData.FORMS[maya.cmds.getAttr('{0}.formV'.format(self.name()))]

    def knotsU(self):
        """the knotU of the nurbsSurface

        :return: the knotU of the nurbsSurface
        :rtype: list[int]
        """

        # create surfaceInfo node
        surfaceInfo = maya.cmds.createNode('surfaceInfo')
        maya.cmds.connectAttr('{0}.worldSpace[0]'.format(self.name()),
                              '{0}.inputSurface'.format(surfaceInfo),
                              force=True)

        # get data
        data = maya.cmds.getAttr('{0}.knotsU'.format(surfaceInfo))[0]

        # delete surfaceInfo
        maya.cmds.delete(surfaceInfo)

        # return
        return data

    def knotsV(self):
        """the knotV of the nurbsSurface

        :return: the knotV of the nurbsSurface
        :rtype: list[int]
        """

        # create surfaceInfo node
        surfaceInfo = maya.cmds.createNode('surfaceInfo')
        maya.cmds.connectAttr('{0}.worldSpace[0]'.format(self.name()),
                              '{0}.inputSurface'.format(surfaceInfo),
                              force=True)

        # get data
        data = maya.cmds.getAttr('{0}.knotsV'.format(surfaceInfo))[0]

        # delete surfaceInfo
        maya.cmds.delete(surfaceInfo)

        # return
        return data

    def points(self):
        """the cv points of the nurbsSurface

        :return: the cv points of the nurbsSurface
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


class Mesh(Shape):
    """node object that manipulates a ``mesh`` shape node
    """

    # ATTRIBUTES #

    _nodeType = 'mesh'
    _inputGeometry = 'inMesh'
    _outputGeometry = 'outMesh'
    _library = cgp_maya_utils.constants.Environment.MESH_LIBRARY

    # OBJECT COMMANDS #

    @classmethod
    def import_(cls, style, parent=None, name=None):
        """import a mesh

        :param style: style of the mesh shape to import that exists in the shape library - ex : ``cube`` - ``circle``
        :type style: str

        :param parent: transform to which the mesh will be parented - new transform if nothing specified
        :type parent: str or :class:`cgp_maya_utils.scene.Transform`

        :param name: name of the mesh
        :type name: str

        :return: the imported mesh
        :rtype: :class:`cgp_maya_utils.scene.Mesh`
        """

        # get the file path
        filePath = os.path.join(cls._library, '{0}.obj'.format(style))

        # errors
        if not os.path.isfile(filePath):
            raise ValueError('{0} is not an existing {1} in the library'.format(style, cls._nodeType))

        # get data
        fileObject = cgp_generic_utils.files.entity(filePath)
        importedGeo = fileObject.import_(style)

        # get shapeObject
        shapeObject = cls(maya.cmds.listRelatives(importedGeo, shapes=True)[0])

        # parent shape
        if parent:
            shapeObject.setTransform(parent, worldSpace=False, deleteOriginalTransform=True)

        # rename shape
        if name:
            shapeObject.setName(name)

    # COMMANDS #

    def count(self):
        """the count of vertices of the mesh

        :return: the count of vertices of the mesh
        :rtype: int
        """

        # return
        return maya.cmds.polyEvaluate(self.name(), vertex=True)

    @cgp_maya_utils.decorators.KeepCurrentSelection()
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
            raise RuntimeError('{0} already exists in the library'.format(name))

        # execute
        return cgp_generic_utils.files.createFile(filePath, self.name())

    def points(self):
        """the vertices of the mesh

        :return: the vertices of the mesh
        :rtype: list[str]
        """

        # return
        return ['{0}.vtx[{1}]'.format(self.name(), index) for index in range(self.count())]
