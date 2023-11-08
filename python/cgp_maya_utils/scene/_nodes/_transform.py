"""
transform object library
"""

# imports python
import os

# imports third-parties
import maya.cmds
import maya.api.OpenMaya
import cgp_generic_utils.constants

# imports local
import cgp_maya_utils.api
import cgp_maya_utils.constants
import cgp_maya_utils.decorators
import cgp_maya_utils.scene._api
from . import _generic


# BASE OBJECTS #


class Transform(_generic.DagNode):
    """node object that manipulates a ``transform`` node
    """

    # ATTRIBUTES #

    _MFN = maya.api.OpenMaya.MFnTransform()
    _TYPE = cgp_maya_utils.constants.NodeType.TRANSFORM

    # OBJECT COMMANDS #

    @classmethod
    def create(cls,
               translate=None,
               rotate=None,
               scale=None,
               rotateOrder=None,
               parent=None,
               worldSpace=False,
               connections=None,
               attributeValues=None,
               name=None,
               **__):
        """create a transform

        :param translate: the translation values of the transform
        :type translate: list[int, float]

        :param rotate: the rotation values of the transform
        :type rotate: list[int, float]

        :param scale: the scale values of the transform
        :type scale: list[int, float]

        :param rotateOrder: the rotateOrder of the transform -
                            default is ``cgp_maya_utils.constants.rotateOrder.XYZ``
        :type rotateOrder: :class:`cgp_maya_utils.constants.RotateOrder`

        :param parent: the parent of the transform
        :type parent: str or :class:`cgp_maya_utils.scene.DagNode`

        :param worldSpace: ``True`` : the transform values are in worldSpace -
                           ``False`` : the transform values are in local
        :type worldSpace: bool

        :param connections: the connections to set on the transform
        :type connections: list[tuple[str]]

        :param attributeValues: the attribute values to set on the transform
        :type attributeValues: dict

        :param name: the name of the transform
        :type name: str

        :return: the created transform
        :rtype: :class:`cgp_maya_utils.scene.Transform`
        """

        # errors
        if rotateOrder and rotateOrder not in cgp_maya_utils.constants.RotateOrder.ALL:
            raise ValueError('{0} is not a valid rotate order - {1}'
                             .format(rotateOrder, cgp_maya_utils.constants.RotateOrder.ALL))

        # init
        rotateOrder = rotateOrder or cgp_maya_utils.constants.RotateOrder.XYZ
        tx, ty, tz = translate or [0, 0, 0]
        rx, ry, rz = rotate or [0, 0, 0]
        sx, sy, sz = scale or [1, 1, 1]

        # create the transform
        xformObject = cls(maya.cmds.createNode(cls._TYPE))
        xformObject.setParent(parent)

        # set rotateOrder
        xformObject.attribute('rotateOrder').setValue(rotateOrder)

        # set transforms
        xformObject.translate(x=tx, y=ty, z=tz,
                              worldSpace=worldSpace,
                              mode=cgp_generic_utils.constants.TransformMode.ABSOLUTE)

        xformObject.rotate(x=rx, y=ry, z=rz,
                           worldSpace=worldSpace,
                           mode=cgp_generic_utils.constants.TransformMode.ABSOLUTE)

        xformObject.scale(x=sx, y=sy, z=sz,
                          mode=cgp_generic_utils.constants.TransformMode.ABSOLUTE)

        # set data
        if attributeValues:
            attributeValues.pop("translate", None)
            attributeValues.pop("rotate", None)
            attributeValues.pop("scale", None)
            attributeValues.pop("rotateOrder", None)
            xformObject.setAttributeValues(attributeValues)
        if connections:
            xformObject.setConnections(connections)
        if name:
            xformObject.setName(name)

        # return
        return xformObject

    # COMMANDS #

    def constraints(self, constraintTypes=None, sources=True, destinations=True, constraintTypesIncluded=True):
        """get the source constraints driving the node and the destination constraints the node drives

        :param constraintTypes: types of constraints to get -
                                default is ``cgp_maya_utils.constants.NodeType.CONSTRAINTS``
        :type constraintTypes: list[str]

        :param sources: ``True`` : the source constraints are returned  - ``False`` : the source constraints are skipped
        :type sources: bool

        :param destinations: ``True`` : destination constraints returned -
                             ``False`` : destination constraints are skipped
        :type destinations: bool

        :param constraintTypesIncluded: ``True`` : constraint types are included -
                                        ``False`` : constraint types are excluded
        :type constraintTypesIncluded: bool

        :return: the constraints
        :rtype: list[Constraint]
        """

        # init
        data = []
        cstrTypes = []

        # errors
        if constraintTypes:
            for cstrType in constraintTypes:
                if cstrType not in cgp_maya_utils.constants.NodeType.CONSTRAINTS:
                    raise ValueError('{0} is not a valid type - {1}'
                                     .format(cstrType, cgp_maya_utils.constants.NodeType.CONSTRAINTS))

        # get cstrTypes to query
        if not constraintTypes and constraintTypesIncluded:
            cstrTypes = cgp_maya_utils.constants.NodeType.CONSTRAINTS

        elif constraintTypes and constraintTypesIncluded:
            cstrTypes = constraintTypes

        elif constraintTypes and not constraintTypesIncluded:
            cstrTypes = set(cgp_maya_utils.constants.NodeType.CONSTRAINTS) - set(constraintTypes)

        # execute
        fullName = self.fullName()
        for cstrType in cstrTypes:

            # sources
            if sources:

                # get source constraints
                if not cstrType == cgp_maya_utils.constants.NodeType.FKN_SPACE_SWITCH:
                    sourceConstraints = maya.cmds.listConnections(fullName,
                                                                  source=True,
                                                                  destination=False,
                                                                  type=cstrType) or []

                else:

                    sourceConstraints = []

                    convertToLocalSpaces = maya.cmds.listConnections(fullName,
                                                                     source=True,
                                                                     destination=False,
                                                                     type='fkn_ConvertToLocalSpace') or []

                    for ctlsNode in set(convertToLocalSpaces):
                        sourceConstraints += maya.cmds.listConnections(ctlsNode,
                                                                       source=True,
                                                                       destination=False,
                                                                       type='fkn_SpaceSwitchCns') or []

                # update inputs
                for sourceConstraint in set(sourceConstraints):

                    # get object
                    cstrObject = cgp_maya_utils.scene._api.node(sourceConstraint)

                    # update
                    if cstrObject.driven() and self == cstrObject.driven():
                        data.append(cstrObject)

            # # destinations
            if destinations:

                # get destination constraints
                destinationConstraints = sorted(list(set(maya.cmds.listConnections(fullName,
                                                                                   source=False,
                                                                                   destination=True,
                                                                                   type=cstrType) or [])))

                # update inputs
                for destinationConstraint in destinationConstraints:

                    # get object
                    cstrObject = cgp_maya_utils.scene._api.node(destinationConstraint)

                    # update
                    if cstrObject.drivers() and self in cstrObject.drivers():
                        data.append(cstrObject)

        # return
        return data

    def data(self, worldSpace=False):
        """get the data necessary to store the transform node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : the transform values are queried in worldSpace -
                           ``False`` : the transform values are queried in local
        :type worldSpace: bool

        :return: the data of the transform
        :rtype: dict
        """

        # init
        data = super(Transform, self).data()

        # update data
        data['parent'] = self.parent().name() if self.parent() else None
        data['constraints'] = [constraint.data() for constraint in self.constraints()]
        data['worldSpace'] = worldSpace
        data.update(self.transformValues(worldSpace=worldSpace))

        # return
        return data

    def duplicate(self, withChildren=True):
        """duplicate the transform

        :param withChildren: ``True`` : the transform is duplicated with its children -
                             ``False`` : the transform is not duplicated with its children
        :type withChildren: bool

        :return: the duplicated transform
        :rtype: :class:`cgp_maya_utils.scene.Transform`
        """

        # return
        return self.__class__(maya.cmds.duplicate(str(self), parentOnly=not withChildren)[0])

    def freeze(self, translate=True, rotate=True, scale=True, normal=False):
        """freeze the values of the transform

        :param translate: ``True`` : the translation values are frozen -
                          ``False`` : the translation values are not frozen
        :type translate: bool

        :param rotate: ``True`` : the rotation values are frozen -
                       ``False`` : the rotation values are not frozen
        :type rotate: bool

        :param scale: ``True`` : the scale values are frozen -
                      ``False`` : the scale values are not frozen
        :type scale: bool

        :param normal: ``True`` : the normal values are frozen -
                       ``False`` : the normal values are not frozen
        :type normal: bool
        """

        # execute
        maya.cmds.makeIdentity(self.fullName(),
                               apply=True,
                               translate=translate,
                               rotate=rotate,
                               scale=scale,
                               preserveNormals=not normal,
                               normal=normal)

    def match(self, target, attributes=None, worldSpace=True):
        """match the transform to the target transform

        :param target: the transform to match to
        :type target: str or :class:`cgp_maya_utils.scene.Transform`

        :param attributes: attributes to match - default is ``cgp_maya_utils.constants.Transform.GENERAL``
        :type attributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param worldSpace: ``True`` : the match occurs in worldSpace - ``False`` : the match occurs in local
        :type worldSpace: bool
        """

        # init
        attributes = self._formatAttributes(attributes)
        target = target if isinstance(target, Transform) else Transform(target)

        # get target xforms values
        values = target.transformValues(worldSpace=worldSpace, rotateOrder=self.attribute('rotateOrder').value())

        # snap
        self._setTransformValues(values, attributes=attributes, worldSpace=worldSpace)

    def mirror(self, mirrorPlane=None, attributes=None, worldSpace=False, mode=None):
        """mirror the transform

        :param mirrorPlane: the plane of mirroring - default is ``cgp_maya_utils.constants.MirrorPlane.YZ``
        :type mirrorPlane: :class:`cgp_generic_utils.constants.MirrorPlane`

        :param attributes: the transform attributes to mirror -
                           default is ``cgp_maya_utils.constants.Transform.GENERAL``
        :type attributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param worldSpace: ``True`` : the mirror occurs in worldSpace - ``False`` : the mirror occurs in local
        :type worldSpace: bool

        :param mode: the mode of mirroring - default is ``cgp_maya_utils.constants.MirrorMode.MIRROR``
        :type mode: :class:`cgp_generic_utils.constants.MirrorMode`
        """

        # init
        mirrorPlane = mirrorPlane or cgp_generic_utils.constants.MirrorPlane.YZ
        attributes = attributes or cgp_maya_utils.constants.Transform.GENERAL
        mode = mode or cgp_generic_utils.constants.MirrorMode.MIRROR

        # errors
        if mirrorPlane not in cgp_generic_utils.constants.MirrorPlane.ALL:
            raise ValueError('{0} is not a valid mirror plane {1}'
                             .format(mirrorPlane, cgp_generic_utils.constants.MirrorPlane.ALL))

        if mode not in cgp_generic_utils.constants.MirrorMode.ALL:
            raise ValueError('{0} is not a valid mode - {1}'.format(mode, cgp_generic_utils.constants.MirrorMode.ALL))

        # get mirror values
        mirrorValues = self.mirrorTransformValues(mirrorPlane=mirrorPlane,
                                                  worldSpace=worldSpace,
                                                  rotateOrder=self.attribute('rotateOrder').value(),
                                                  mode=mode)

        # execute
        self._setTransformValues(mirrorValues, attributes=attributes, worldSpace=worldSpace)

    @cgp_maya_utils.decorators.KeepSelection()
    def mirrorTransformValues(self, mirrorPlane=None, worldSpace=False, rotateOrder=None, mode=None):
        """the mirror transform values

        :param mirrorPlane: the plane of mirroring - default is ``cgp_generic_utils.constants.MirrorPlane.YZ``
        :type mirrorPlane: :class:`cgp_generic_utils.constants.MirrorPlane`

        :param worldSpace: ``True`` : the mirror transform values are queried in worldSpace -
                           ``False`` : the mirror transform values are queried in local
        :type worldSpace: bool

        :param rotateOrder: the rotateOrder to get the mirror transform values in
        :type rotateOrder: :class:`cgp_maya_utils.constants.RotateOrder`

        :param mode: the mode of mirroring - default is ``cgp_maya_utils.constants.MirrorMode.MIRROR``
        :type mode: :class:`cgp_maya_utils.constants.MirrorMode`

        :return: the mirrored transforms
        :rtype: dict
        """

        # init
        mirrorPlane = mirrorPlane or cgp_generic_utils.constants.MirrorPlane.YZ
        mode = mode or cgp_generic_utils.constants.MirrorMode.MIRROR

        # errors
        if rotateOrder and rotateOrder not in cgp_maya_utils.constants.RotateOrder.ALL:
            raise ValueError('{0} is not a valid rotateOrder - {1}'
                             .format(rotateOrder, cgp_maya_utils.constants.RotateOrder.ALL))

        if mirrorPlane not in cgp_generic_utils.constants.MirrorPlane.ALL:
            raise ValueError('{0} is not a valid mirror plane {1}'
                             .format(mirrorPlane, cgp_generic_utils.constants.MirrorPlane.ALL))

        if mode not in cgp_generic_utils.constants.MirrorMode.ALL:
            raise ValueError('{0} is not a valid mode - {1}'.format(mode, cgp_generic_utils.constants.MirrorMode.ALL))

        # get transformation matrix
        transformationMatrix = self.transformationMatrix(worldSpace=worldSpace, rotateOrder=rotateOrder)

        # get rotation and translation
        rotation = transformationMatrix.rotation()
        translation = transformationMatrix.translation(maya.api.OpenMaya.MSpace.kWorld)

        # get MMatrix
        mMatrix = transformationMatrix.asMatrix()

        # get mirror plane index
        mirrorPlaneIndex = cgp_generic_utils.constants.Axe.ALL.index(cgp_generic_utils.constants.AxisTable.ALL[mirrorPlane])

        # mirror translation
        if mode in [cgp_generic_utils.constants.MirrorMode.NO_MIRROR, cgp_generic_utils.constants.MirrorMode.MIRROR]:

            # multiply corresponding axis by -1
            translation[mirrorPlaneIndex] *= -1

            # set translation
            transformationMatrix.setTranslation(translation, maya.api.OpenMaya.MSpace.kWorld)

            # get resulting MMatrix
            mMatrix = transformationMatrix.asMatrix()

        # mirror rotation
        if mode == cgp_generic_utils.constants.MirrorMode.MIRROR:

            # execute
            for axis in mirrorPlane:

                # get mirror plane index
                axisIndex = cgp_generic_utils.constants.Axe.ALL.index(axis)

                # multiply each corresponding axis by -1
                rotation[axisIndex] *= -1

            # set rotation
            transformationMatrix.setRotation(rotation)

            # get resulting MMatrix
            mMatrix = transformationMatrix.asMatrix()

        # neg mirror
        if mode == cgp_generic_utils.constants.MirrorMode.NEG_MIRROR:

            # init
            identityMatrix = maya.api.OpenMaya.MMatrix()

            # multiply the corresponding axis by -1
            identityMatrix[mirrorPlaneIndex * 5] *= -1

            # get resulting MMatrix
            mMatrix = mMatrix * identityMatrix

        # get transformationMatrix
        transformationMatrix = cgp_maya_utils.api.TransformationMatrix.fromMatrix(mMatrix, rotateOrder=rotateOrder)

        # return
        return transformationMatrix.transformValues()

    def reset(self, translate=True, rotate=True, scale=True, shear=True):
        """reset the values of the transform to its default values

        :param translate: ``True`` : the translation values are reset - ``False`` : the translation values are not reset
        :type translate: bool

        :param rotate: ``True`` : the rotation values are reset - ``False`` : the rotation values are not reset
        :type rotate: bool

        :param scale: ``True`` : the scale values are reset - ``False`` : the scale values are not reset
        :type scale: bool

        :param shear: ``True`` : the shear values are reset - ``False`` : the shear values are not reset
        :type shear: bool
        """

        # init
        data = {}

        # reset translate
        if translate:
            data['translation'] = [0, 0, 0]

        # reset rotate
        if rotate:
            data['rotation'] = [0, 0, 0]

        # reset scale
        if scale:
            data['scale'] = [1, 1, 1]

        # reset shear
        if shear:
            data['shear'] = [0, 0, 0]

        # errors
        if not data:
            maya.cmds.warning('nothing to reset')
            return

        # execute
        maya.cmds.xform(self.fullName(), **data)

    def rotate(self, x=None, y=None, z=None, worldSpace=False, mode=None):
        """rotate the transform

        :param x: value of rotateX to set
        :type x: float

        :param y: value of rotateY to set
        :type y: float

        :param z: value of rotateZ to set
        :type z: float

        :param worldSpace: ``True`` : the rotation occurs in worldSpace - ``False`` : the rotation occurs in local
        :type worldSpace: bool

        :param mode: ``cgp_generic_utils.constants.TransformMode.ABSOLUTE`` : value is replaced, default mode -
                     ``cgp_generic_utils.constants.TransformMode.RELATIVE`` : value is added
        :type mode: :class:`cgp_generic_utils.constants.TransformMode`
        """

        # get info
        values = self.transformationMatrix(worldSpace=worldSpace).transformValues()
        isRelative = mode == cgp_generic_utils.constants.TransformMode.RELATIVE

        # update values
        if isRelative:
            x = x if x is not None else 0
            y = y if y is not None else 0
            z = z if z is not None else 0
        else:
            x = x if x is not None else values[cgp_maya_utils.constants.Transform.ROTATE][0]
            y = y if y is not None else values[cgp_maya_utils.constants.Transform.ROTATE][1]
            z = z if z is not None else values[cgp_maya_utils.constants.Transform.ROTATE][2]

        # set values
        maya.cmds.xform(self.fullName(), worldSpace=worldSpace, relative=isRelative, rotation=[x, y, z])

    def scale(self, x=None, y=None, z=None, mode=None):
        """scale the transform

        :param x: value of scaleX to set
        :type x: float

        :param y: value of scaleY to set
        :type y: float

        :param z: value of scaleZ to set
        :type z: float

        :param mode: ``cgp_generic_utils.constants.TransformMode.ABSOLUTE`` : value is replaced, default mode -
                     ``cgp_generic_utils.constants.TransformMode.RELATIVE`` : value is added
        :type mode: :class:`cgp_generic_utils.constants.TransformMode`
        """

        # get info
        values = self.transformationMatrix().transformValues()
        isRelative = mode == cgp_generic_utils.constants.TransformMode.RELATIVE

        # update values
        if isRelative:
            x = x if x is not None else 1
            y = y if y is not None else 1
            z = z if z is not None else 1
        else:
            x = x if x is not None else values[cgp_maya_utils.constants.Transform.SCALE][0]
            y = y if y is not None else values[cgp_maya_utils.constants.Transform.SCALE][1]
            z = z if z is not None else values[cgp_maya_utils.constants.Transform.SCALE][2]

        # set values
        maya.cmds.xform(self.fullName(), relative=isRelative, scale=[x, y, z])

    def setTransformValues(self, transformValues, worldSpace=False):
        """set the transform values

        :param transformValues: the transform values to set
        :type transformValues: dict

        :param worldSpace: ``True`` : the transform values are in worldSpace -
                           ``False`` : the transform values are in local
        :type worldSpace: bool
        """

        # execute
        self._setTransformValues(transformValues, worldSpace=worldSpace)

    def shear(self, xy=None, xz=None, yz=None, mode=None):
        """shear the transform

        :param xy: value of shearXY to set
        :type xy: float

        :param xz: value of shearXZ to set
        :type xz: float

        :param yz: value of shearYZ to set
        :type yz: float

        :param mode: ``cgp_generic_utils.constants.TransformMode.ABSOLUTE`` : value is replaced, default mode -
                     ``cgp_generic_utils.constants.TransformMode.RELATIVE`` : value is added
        :type mode: :class:`cgp_generic_utils.constants.TransformMode`
        """

        # get info
        values = self.transformationMatrix().transformValues()
        isRelative = mode == cgp_generic_utils.constants.TransformMode.RELATIVE

        # update values
        if isRelative:
            xy = xy if xy is not None else 0
            xz = xz if xz is not None else 0
            yz = yz if yz is not None else 0
        else:
            xy = xy if xy is not None else values[cgp_maya_utils.constants.Transform.SHEAR][0]
            xz = xz if xz is not None else values[cgp_maya_utils.constants.Transform.SHEAR][1]
            yz = yz if yz is not None else values[cgp_maya_utils.constants.Transform.SHEAR][2]

        # set values
        maya.cmds.xform(self.fullName(), relative=isRelative, shear=[xy, xz, yz])

    def shapes(self, shapeTypes=None, shapeTypesIncluded=True, isSorted=False):
        """get the shapes from the Transform

        :param shapeTypes: types used to get the shapes - All if nothing is specified
        :type shapeTypes: list[str]

        :param shapeTypesIncluded: ``True`` : the shapeTypes are included - ``False`` : the shapeTypes are excluded
        :type shapeTypesIncluded: bool

        :param isSorted: ``True`` : shapes are sorted and returned in the upstream order -
                         ``False`` : shapes are returned in no specific order`
        :type isSorted: bool

        :return: the shapes of the transform
        :rtype: list[Shape]
        """

        # init
        shapes = []
        queryShapeTypes = []

        # errors
        if shapeTypes:
            for shapeType in shapeTypes:
                if shapeType not in cgp_maya_utils.constants.NodeType.SHAPES:
                    raise ValueError('{0} is not a valid type - {1}'
                                     .format(shapeType, cgp_maya_utils.constants.NodeType.SHAPES))

        # get shapeTypes to query
        if not shapeTypes and shapeTypesIncluded:
            queryShapeTypes = cgp_maya_utils.constants.NodeType.SHAPES

        elif shapeTypes and shapeTypesIncluded:
            queryShapeTypes = shapeTypes

        elif shapeTypes and not shapeTypesIncluded:
            queryShapeTypes = set(cgp_maya_utils.constants.NodeType.SHAPES) - set(shapeTypes)

        # collect shapes
        for shapeType in queryShapeTypes:
            shapeFullNames = maya.cmds.listRelatives(self.fullName(),
                                                     shapes=True,
                                                     type=shapeType,
                                                     fullPath=True,
                                                     noIntermediate=isSorted) or []
            for shapeFullName in shapeFullNames:
                shapes.append(cgp_maya_utils.scene.node(shapeFullName))

        # return unsorted
        if not isSorted:
            return shapes

        # sort shapes by outMesh connections
        shapes = sorted(shapes,
                        key=lambda shape_: len(shape_.attribute('outMesh').connections(source=False,
                                                                                       destinations=True)))

        # sort shapes following upstream
        sortedShapes = []
        for shape in shapes:

            # bypass if the shape has already been listed via upstreams
            if shape in sortedShapes:
                continue

            # append non intermediate shape
            sortedShapes.append(shape)

            # append upstream shapes
            for upstreamShape in shape.upstream(nodeTypes=cgp_maya_utils.constants.NodeType.SHAPES):
                if upstreamShape not in sortedShapes:
                    sortedShapes.append(upstreamShape)

        # return sorted - first is visible shape, last is original shape
        return sortedShapes

    def transformationMatrix(self, worldSpace=False, rotateOrder=None):
        """get the transformationMatrix of the transform

        :param worldSpace: ``True`` : TransformationMatrix is initialized with the worldSpace transform values -
                           ``False`` : TransformationMatrix is initialized with the local transform values
        :type worldSpace: bool

        :param rotateOrder: rotateOrder to get the transform values in -
                            default is the current rotateOrder of the transform
        :type rotateOrder: :class:`cgp_generic_utils.constants.RotateOrder`

        :return: the transformationMatrix of the transform
        :rtype: :class:`cgp_maya_utils.api.TransformationMatrix`
        """

        # init
        matrixAttr = 'worldMatrix' if worldSpace else 'matrix'
        rotateOrder = rotateOrder or self.attribute('rotateOrder').value()

        # errors
        if rotateOrder and rotateOrder not in cgp_maya_utils.constants.RotateOrder.ALL:
            raise ValueError('{0} is not a valid rotateOrder - {1}'
                             .format(rotateOrder, cgp_maya_utils.constants.RotateOrder.ALL))

        # return
        return cgp_maya_utils.api.TransformationMatrix.fromAttribute('{0}.{1}'.format(self.fullName(), matrixAttr),
                                                                     rotateOrder=rotateOrder)

    def transformValues(self, worldSpace=False, rotateOrder=None):
        """get the transform values of transform

        :param worldSpace: ``True`` : the transform values are queried in worldSpace -
                           ``False`` : the transform values are queried in local
        :type worldSpace: bool

        :param rotateOrder: the rotateOrder to get the transform values in
        :type rotateOrder: :class:`cgp_generic_utils.constants.RotateOrder`

        :return: the transform values of the transform
        :rtype: dict
        """

        # return
        return self.transformationMatrix(worldSpace=worldSpace, rotateOrder=rotateOrder).transformValues()

    def translate(self, x=None, y=None, z=None, worldSpace=False, mode=None):
        """translate the transform

        :param x: value of translateX to set
        :type x: float

        :param y: value of translateX to set
        :type y: float

        :param z: value of translateX to set
        :type z: float

        :param worldSpace: ``True`` : translation occurs in worldSpace - ``False`` : translation occurs in local
        :type worldSpace: bool

        :param mode: ``cgp_generic_utils.constants.TransformMode.ABSOLUTE`` : value is replaced, default mode -
                     ``cgp_generic_utils.constants.TransformMode.RELATIVE`` : value is added
        :type mode: :class:`cgp_generic_utils.constants.TransformMode`
        """

        # get info
        values = self.transformationMatrix(worldSpace=worldSpace).transformValues()
        isRelative = mode == cgp_generic_utils.constants.TransformMode.RELATIVE

        # update values
        if isRelative:
            x = x if x is not None else 0
            y = y if y is not None else 0
            z = z if z is not None else 0
        else:
            x = x if x is not None else values[cgp_maya_utils.constants.Transform.TRANSLATE][0]
            y = y if y is not None else values[cgp_maya_utils.constants.Transform.TRANSLATE][1]
            z = z if z is not None else values[cgp_maya_utils.constants.Transform.TRANSLATE][2]

        # set values
        maya.cmds.xform(self.fullName(), worldSpace=worldSpace, relative=isRelative, translation=[x, y, z])

    # PRIVATE COMMANDS #

    @staticmethod
    def _formatAttributes(attributes):
        """format the transform attributes into a formatted data list

        :param attributes: attributes to format
        :type attributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :return: the formatted attributes
        :rtype: list[:class:`cgp_maya_utils.constants.Transform`]
        """

        # init
        attributes = attributes or cgp_maya_utils.constants.Transform.GENERAL

        data = {cgp_maya_utils.constants.Transform.TRANSLATE: cgp_maya_utils.constants.Transform.TRANSLATES,
                cgp_maya_utils.constants.Transform.ROTATE: cgp_maya_utils.constants.Transform.ROTATES,
                cgp_maya_utils.constants.Transform.SCALE: cgp_maya_utils.constants.Transform.SCALES,
                cgp_maya_utils.constants.Transform.SHEAR: cgp_maya_utils.constants.Transform.SHEARS}

        # errors
        for attr in attributes:
            if attr not in cgp_maya_utils.constants.Transform.ALL:
                raise ValueError('{0} is not a valid attribute - {1}'
                                 .format(attr, cgp_maya_utils.constants.Transform.ALL))

        # sort attributes to set
        for attr in attributes:
            if attr in cgp_maya_utils.constants.Transform.GENERAL:
                attributes = set(attributes) | set(data[attr])

        # return
        return list(reversed(sorted(set(attributes) - set(cgp_maya_utils.constants.Transform.GENERAL))))

    @cgp_maya_utils.decorators.KeepSelection()
    def _setTransformValues(self, values, attributes=None, worldSpace=False):
        """set transform values from a dictionary of values

        :param values: the transform values to set on the transform
        :type values: dict

        :param attributes: the transform attributes to set - default is ``cgp_maya_utils.constants.Transform.GENERAL``
        :type attributes: list[:class:`cgp_maya_utils.constants.Transform`]

        :param worldSpace: ``True`` : the transform values are set on worldSpace -
                           ``False`` : the transform values are set on local
        :type worldSpace: bool
        """

        # get info
        fullName = self.fullName()
        attributes = self._formatAttributes(attributes)
        toExcludeNodeTypes = (cgp_maya_utils.constants.NodeType.ANIM_CURVES
                              + [cgp_maya_utils.constants.NodeType.ANIM_BLEND])

        # execute
        if worldSpace:

            # get targetMatrix
            targetMatrix = cgp_maya_utils.api.TransformationMatrix.fromTransforms(translate=values['translate'],
                                                                                  rotate=values['rotate'],
                                                                                  scale=values['scale'],
                                                                                  shear=values['shear'],
                                                                                  rotateOrder=values['rotateOrder'])

            targetMatrix.setRotateOrder(self.attribute('rotateOrder').value())

            # rebase targetMatrix
            if self.parent():
                # get info
                worldInvMatrixAttribute = self.parent().attribute('worldInverseMatrix')
                rotateOrder = self.attribute('rotateOrder').value()

                # get world inverse TransformationMatrix
                parentMatrix = cgp_maya_utils.api.TransformationMatrix.fromAttribute(worldInvMatrixAttribute,
                                                                                     rotateOrder=rotateOrder)

                # rebase targetMatrix
                targetMatrix = targetMatrix * parentMatrix

            # update values
            values = targetMatrix.transformValues()

        # flatten values
        flattenValues = {cgp_maya_utils.constants.Transform.TRANSLATE_X: values['translate'][0],
                         cgp_maya_utils.constants.Transform.TRANSLATE_Y: values['translate'][1],
                         cgp_maya_utils.constants.Transform.TRANSLATE_Z: values['translate'][2],
                         cgp_maya_utils.constants.Transform.ROTATE_X: values['rotate'][0],
                         cgp_maya_utils.constants.Transform.ROTATE_Y: values['rotate'][1],
                         cgp_maya_utils.constants.Transform.ROTATE_Z: values['rotate'][2],
                         cgp_maya_utils.constants.Transform.SCALE_X: values['scale'][0],
                         cgp_maya_utils.constants.Transform.SCALE_Y: values['scale'][1],
                         cgp_maya_utils.constants.Transform.SCALE_Z: values['scale'][2],
                         cgp_maya_utils.constants.Transform.SHEAR_XY: values['shear'][0],
                         cgp_maya_utils.constants.Transform.SHEAR_XZ: values['shear'][1],
                         cgp_maya_utils.constants.Transform.SHEAR_YZ: values['shear'][2]}

        # snap obj to position
        for attribute in attributes:

            # get fullAttribute
            fullAttribute = '{0}.{1}'.format(fullName, attribute)

            # get connections
            genConnections = self.connections([attribute.translate(None, 'XYZ')],
                                              nodeTypes=toExcludeNodeTypes,
                                              nodeTypesIncluded=False,
                                              sources=True,
                                              destinations=False)

            fullConnections = self.connections([attribute],
                                               nodeTypes=toExcludeNodeTypes,
                                               nodeTypesIncluded=False,
                                               sources=True,
                                               destinations=False)

            # set
            if not maya.cmds.getAttr(fullAttribute, lock=True) and not fullConnections and not genConnections:
                maya.cmds.setAttr(fullAttribute, flattenValues[attribute])


# TRANSFORM OBJECTS #


class IkEffector(Transform):
    """node object that manipulates an ``ikEffector`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.IK_EFFECTOR


class IkHandle(Transform):
    """node object that manipulates an ``ikHandle`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.IK_HANDLE

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, startJoint,
               endJoint,
               solverType=None,
               connections=None,
               attributeValues=None,
               name=None,
               **__):
        """create an ikHandle of the specified solver type

        :param startJoint: the startJoint of the ikHandle
        :type startJoint: str or :class:`cgp_maya_utils.scene.Joint`

        :param endJoint: the endJoint of the ikHandle
        :type endJoint: str or :class:`cgp_maya_utils.scene.Joint`

        :param solverType: the type of solver of the ikHandle to create - default is ``constants.Solver.IK_RP_SOLVER``
        :type solverType: :class:`cgp_maya_utils.constants.Solver`

        :param connections: the connections to set on the ikHandle
        :type connections: list[tuple[str]]

        :param attributeValues: the attribute values to set on the ikHandle
        :type attributeValues: dict

        :param name: the name of the ikHandle
        :type name: str

        :return: the ikHandle object
        :rtype: :class:`cgp_maya_utils.scene.IkHandle`
        """

        # init
        name = name or cls._TYPE
        solverType = solverType or cgp_maya_utils.constants.Solver.IK_RP_SOLVER

        # errors
        if solverType not in cgp_maya_utils.constants.Solver.IK_SOLVERS:
            raise ValueError('{0} is not a valid ik solver type - {1}'
                             .format(solverType, cgp_maya_utils.constants.Solver.IK_SOLVERS))

        # execute
        ikHandle, effector = maya.cmds.ikHandle(startJoint=str(startJoint),
                                                endEffector=str(endJoint),
                                                solver=solverType,
                                                name=name)

        # get ikHandle object
        ikHandleObject = cls(ikHandle)

        # set attributeValues
        if attributeValues:
            ikHandleObject.setAttributeValues(attributeValues)

        # set connections
        if connections:
            ikHandleObject.setConnections(connections)

        # return
        return ikHandleObject

    # COMMANDS #

    def data(self, worldSpace=False):
        """get the data necessary to store the ikHandle node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : ikHandle transforms are got in worldSpace -
                           ``False`` : ikHandle transforms are got in local
        :type worldSpace: bool

        :return: the data of the ikHandle
        :rtype: dict
        """

        # init
        data = super(IkHandle, self).data(worldSpace=worldSpace)

        # update data
        data['startJoint'] = self.startJoint()
        data['endJoint'] = self.endJoint()
        data['effector'] = self.effector()

        # return
        return data

    def effector(self):
        """get the effector of the ikHandle

        :return: the effector of the ikHandle
        :rtype: :class:`cgp_maya_utils.scene.IkEffector`
        """

        # get the ikEffector
        ikEffector = maya.cmds.ikHandle(self.fullName(), query=True, endEffector=True)

        # return
        return IkEffector(ikEffector)

    def endJoint(self):
        """get the end joint of the ikHandle

        :return: the endJoint of the ikHandle
        :rtype: :class:`cgp_maya_utils.scene.Joint`
        """

        # init
        translateX = self.effector().attribute(cgp_maya_utils.constants.Transform.TRANSLATE_X)
        effectorConnections = translateX.connections(source=True, destinations=False)

        # return
        return effectorConnections[0].source().node()

    def setSolver(self, solverType):
        """set the solver of the ikHandle

        :param solverType: type of solver to set on the ikHandle
        :type solverType: :class:`cgp_maya_utils.constants.Solver`
        """

        # execute
        maya.cmds.ikHandle(self.fullName(), edit=True, solver=solverType)

    def startJoint(self):
        """get the startJoint of the ikHandle

        :return: the startJoint of the ikHandle
        :rtype: :class:`cgp_maya_utils.scene.Joint`
        """

        # get the startJoint
        startJoint = maya.cmds.ikHandle(self.fullName(), query=True, startJoint=True)

        # return
        return cgp_maya_utils.scene._api._NODE_TYPES['joint'](startJoint)


class Joint(Transform):
    """node object that manipulates a ``joint`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.JOINT

    # OBJECT COMMANDS #

    @classmethod
    def create(cls,
               translate=None,
               rotate=None,
               scale=None,
               rotateOrder=None,
               parent=None,
               worldSpace=False,
               connections=None,
               attributeValues=None,
               name=None,
               **__):
        """create a joint

        :param translate: the translation values of the joint
        :type translate: list[int, float]

        :param rotate: the rotation values of the joint
        :type rotate: list[int, float]

        :param scale: the scale values of the joint
        :type scale: list[int, float]

        :param rotateOrder: the rotateOrder of the joint
        :type rotateOrder: :class:`cgp_maya_utils.constants.RotateOrder`

        :param parent: the parent of the joint
        :type parent: str or :class:`cgp_maya_utils.scene.DagNode`

        :param worldSpace: ``True`` : the transform values are in worldSpace -
                           ``False`` : the transform values are in local
        :type worldSpace: bool

        :param connections: the connections to set on the joint
        :type connections: list[tuple[str]]

        :param attributeValues: the attribute values to set on the joint
        :type attributeValues: dict

        :param name: the name of the joint
        :type name: str

        :return: the created joint
        :rtype: :class:`cgp_maya_utils.scene.Joint`
        """

        # init
        joint = super(Joint, cls).create(translate=translate,
                                         rotate=rotate,
                                         scale=scale,
                                         rotateOrder=rotateOrder,
                                         parent=parent,
                                         worldSpace=worldSpace,
                                         connections=connections,
                                         name=name,
                                         **__)

        # set attribute values
        if attributeValues:
            joint.setAttributeValues(attributeValues)

        # return
        return joint
