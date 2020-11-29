"""
transform object library
"""

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

    _nodeType = 'transform'
    _MFn = maya.api.OpenMaya.MFnTransform()

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, translate=None, rotate=None, scale=None, rotateOrder=None, parent=None,
               worldSpace=False, connections=None, attributeValues=None, name=None, **__):
        """create a transform

        :param translate: translation values of the transform
        :type translate: list[int, float]

        :param rotate: rotation values  of the transform
        :type rotate: list[int, float]

        :param scale: scale values of the transform
        :type scale: list[int, float]

        :param rotateOrder: rotateOrder of the transform - default is ``cgp_maya_utils.constants.rotateOrder.XYZ``
        :type rotateOrder: str

        :param parent: parent of the transform
        :type parent: str or :class:`cgp_maya_utils.scene.DagNode`

        :param worldSpace: ``True`` : transform values are worldSpace - ``False`` : transform values are local
        :type worldSpace: bool

        :param connections: connections to set on the transform
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the transform
        :type attributeValues: dict

        :param name: name of the transform
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
        xformObject = cls(maya.cmds.createNode(cls._nodeType))
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
            xformObject.setAttributeValues(attributeValues)
        if connections:
            xformObject.setConnections(connections)
        if name:
            xformObject.setName(name)

        # return
        return xformObject

    # COMMANDS #

    def constraints(self, constraintTypes=None, sources=True, destinations=True, constraintTypesIncluded=True):
        """the source constraints driving the node and the destination constraints the node drives

        :param constraintTypes: types of constraints to get - All if nothing is specified
        :type constraintTypes: list[str]

        :param sources: ``True`` : source constraints are returned  - ``False`` : source constraints are skipped
        :type sources: bool

        :param destinations: ``True`` : destination constraints returned -
                             ``False`` : destination constraints are skipped
        :type destinations: bool

        :param constraintTypesIncluded: ``True`` : constraint types are included -
                                        ``False`` : constraint types are excluded
        :type constraintTypesIncluded: bool

        :return: the constraints
        :rtype: list[:class:`cgp_maya_utils.scene.Constraint`,
                     :class:`cgp_maya_utils.scene.AimConstraint`,
                     :class:`cgp_maya_utils.scene.OrientConstraint`,
                     :class:`cgp_maya_utils.scene.ParentConstraint`,
                     :class:`cgp_maya_utils.scene.PointConstraint`,
                     :class:`cgp_maya_utils.scene.ScaleConstraint`]
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
        for cstrType in cstrTypes:

            # get constraints
            constraints = set(maya.cmds.listConnections(self.name(),
                                                        source=sources,
                                                        destination=destinations,
                                                        type=cstrType) or [])

            # update data
            for constraint in constraints:

                # get constraint object
                constraintObject = cgp_maya_utils.scene._api.node(constraint)

                # update
                if (constraintObject.driven() and self == constraintObject.driven() and sources
                        or constraintObject.drivers() and self in constraintObject.drivers() and destinations):
                    data.append(constraintObject)

        # return
        return data

    def data(self, worldSpace=False):
        """data necessary to store the transform node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : transform values are worldSpace -
                           ``False`` : transform values are local
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
        """duplicate the transform node

        :param withChildren: ``True`` : transform node is duplicated with its children -
                             ``False`` : transform node is not duplicated with its children
        :type withChildren: bool

        :return: the duplicated transform
        :rtype: :class:`cgp_maya_utils.scene.Transform`
        """

        # return
        return cgp_maya_utils.scene.node(maya.cmds.duplicate(str(self), parentOnly=not withChildren)[0])

    def freeze(self, translate=True, rotate=True, scale=True, normal=False):
        """freeze the values of the transform

        :param translate: ``True`` : translation values are frozen - ``False`` : translation values are not frozen
        :type translate: bool

        :param rotate: ``True`` : rotation values are frozen - ``False`` : rotation values are not frozen
        :type rotate: bool

        :param scale: ``True`` : scale values are frozen - ``False`` : scale values are not frozen
        :type scale: bool

        :param normal: ``True`` : normal values are frozen - ``False`` : normal values are not frozen
        :type normal: bool
        """

        # execute
        maya.cmds.makeIdentity(self.name(),
                               apply=True,
                               translate=translate,
                               rotate=rotate,
                               scale=scale,
                               preserveNormals=not normal,
                               normal=normal)

    def match(self, targetTransform, attributes=None, worldSpace=True):
        """match the transform to the target transform

        :param targetTransform: transform to match to
        :type targetTransform: str or :class:`cgp_maya_utils.scene.Transform`

        :param attributes: attributes to match - default is ``cgp_maya_utils.constants.Transform.GENERAL``
        :type attributes: list[str]

        :param worldSpace: ``True`` : match occurs in worldSpace - ``False`` : match occurs in local
        :type worldSpace: bool
        """

        # init
        attributes = self._formatAttributes(attributes)
        targetTransform = targetTransform if isinstance(targetTransform, Transform) else Transform(targetTransform)

        # get target xforms values
        values = targetTransform.transformValues(worldSpace=worldSpace,
                                                 rotateOrder=self.attribute('rotateOrder').value())

        # snap
        self._setTransformValues(values, attributes=attributes, worldSpace=worldSpace)

    def mirror(self, mirrorPlane=None, attributes=None, worldSpace=False, mode=None):
        """mirror the transform

        :param mirrorPlane: plane of mirroring - default is ``cgp_generic_utils.constants.MirrorPlane.YZ``
        :type mirrorPlane: str

        :param attributes: transform attributes to mirror - default is ``cgp_maya_utils.constants.Transform.GENERAL``
        :type attributes: list

        :param worldSpace: ``True`` : mirror occurs in worldSpace - ``False`` : mirror occurs in local
        :type worldSpace: bool

        :param mode: mode of mirroring - default is ``cgp_generic_utils.constants.MirrorMode.MIRROR``
        :type mode: str
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

    @cgp_maya_utils.decorators.KeepCurrentSelection()
    def mirrorTransformValues(self, mirrorPlane=None, worldSpace=False, rotateOrder=None, mode=None):
        """the mirror transform values

        :param mirrorPlane: plane of mirroring - default is ``cgp_generic_utils.constants.MirrorPlane.YZ``
        :type mirrorPlane: str

        :param worldSpace: ``True`` : mirror transform values are worldSpace -
                           ``False`` : mirror transform values are local
        :type worldSpace: bool

        :param rotateOrder: rotateOrder to get the mirror transform values in - ! ONLY IN WORLDSPACE !
        :type rotateOrder: str

        :param mode: mode of mirroring - default is ``cgp_generic_utils.constants.MirrorMode.MIRROR``
        :type mode: str

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

        # create temporary locator
        tempOrig = maya.cmds.group(empty=True)
        tempLoc = Transform(maya.cmds.spaceLocator()[0])

        # snap tempLoc to position # TODO: make it works with matrix calculation instead of locator
        maya.cmds.parent(tempLoc.name(), tempOrig)
        maya.cmds.delete(maya.cmds.parentConstraint(self.name(), tempLoc.name()))
        maya.cmds.delete(maya.cmds.scaleConstraint(self.name(), tempLoc.name()))

        # parent locator if necessary
        if not worldSpace and self.parent():
            tempLoc.setParent(self.parent().name())

        # mirror translation
        if mode in [cgp_generic_utils.constants.MirrorMode.NO_MIRROR, cgp_generic_utils.constants.MirrorMode.MIRROR]:
            attr = '{0}.t{1}'.format(tempLoc.name(), cgp_generic_utils.constants.AxisTable.ALL[mirrorPlane])
            cgp_maya_utils.scene._api.attribute(attr).multiply(-1)

        # mirror rotation
        if mode == cgp_generic_utils.constants.MirrorMode.MIRROR:
            for axis in mirrorPlane:
                attr = '{0}.r{1}'.format(tempLoc.name(), axis)
                cgp_maya_utils.scene._api.attribute(attr).multiply(-1)

        # neg mirror
        if mode == cgp_generic_utils.constants.MirrorMode.NEG_MIRROR:
            maya.cmds.setAttr('{0}.s{1}'.format(tempOrig, cgp_generic_utils.constants.AxisTable.ALL[mirrorPlane]), -1)

        # get mirror transform values
        values = tempLoc.transformValues(worldSpace=worldSpace, rotateOrder=rotateOrder)

        # delete temporaries joints
        maya.cmds.delete([tempOrig, tempLoc.name()])

        # return
        return values

    def reset(self, translate=True, rotate=True, scale=True, shear=True):
        """reset the values of the transform to its default values

        :param translate: ``True`` : translation values are reset - ``False`` : translation values are not reset
        :type translate: bool

        :param rotate: ``True`` : rotation values are reset - ``False`` : rotation values are not reset
        :type rotate: bool

        :param scale: ``True`` : scale values are reset - ``False`` : scale values are not reset
        :type scale: bool

        :param shear: ``True`` : shear values are reset - ``False`` : shear values are not reset
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
        maya.cmds.xform(self.name(), **data)

    def rotate(self, x=None, y=None, z=None, worldSpace=False, mode=None):
        """rotate the transform

        :param x: value of rotateX to set
        :type x: float

        :param y: value of rotateY to set
        :type y: float

        :param z: value of rotateZ to set
        :type z: float

        :param worldSpace: ``True`` : rotate occurs in worldSpace - ``False`` : rotate occurs in local
        :type worldSpace: bool

        :param mode: ``cgp_generic_utils.constants.TransformMode.ABSOLUTE`` : value is replaced, default mode -
                     ``cgp_generic_utils.constants.TransformMode.RELATIVE`` : value is added
        :type mode: str
        """

        # get infos
        values = self.transformationMatrix(worldSpace=worldSpace).transformValues()
        isRelative = mode == cgp_generic_utils.constants.TransformMode.RELATIVE

        # update values
        if isRelative:
            x = x if x is not None else 0
            y = y if y is not None else 0
            z = z if z is not None else 0
        else:
            x = x if x is not None else values[cgp_maya_utils.constants.Transform.ROTATE_X]
            y = y if y is not None else values[cgp_maya_utils.constants.Transform.ROTATE_Y]
            z = z if z is not None else values[cgp_maya_utils.constants.Transform.ROTATE_Z]

        # set values
        maya.cmds.xform(self.name(), worldSpace=worldSpace, relative=isRelative, rotation=[x, y, z])

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
        :type mode: str
        """

        # get infos
        values = self.transformationMatrix().transformValues()
        isRelative = mode == cgp_generic_utils.constants.TransformMode.RELATIVE

        # update values
        if isRelative:
            x = x if x is not None else 1
            y = y if y is not None else 1
            z = z if z is not None else 1
        else:
            x = x if x is not None else values[cgp_maya_utils.constants.Transform.SCALE_X]
            y = y if y is not None else values[cgp_maya_utils.constants.Transform.SCALE_Y]
            z = z if z is not None else values[cgp_maya_utils.constants.Transform.SCALE_Z]

        # set values
        maya.cmds.xform(self.name(), relative=isRelative, scale=[x, y, z])

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
        :type mode: str
        """

        # get infos
        values = self.transformationMatrix().transformValues()
        isRelative = mode == cgp_generic_utils.constants.TransformMode.RELATIVE

        # update values
        if isRelative:
            xy = xy if xy is not None else 0
            xz = xz if xz is not None else 0
            yz = yz if yz is not None else 0
        else:
            xy = xy if xy is not None else values[cgp_maya_utils.constants.Transform.SHEAR_XY]
            xz = xz if xz is not None else values[cgp_maya_utils.constants.Transform.SHEAR_XZ]
            yz = yz if yz is not None else values[cgp_maya_utils.constants.Transform.SHEAR_YZ]

        # set values
        maya.cmds.xform(self.name(), relative=isRelative, shear=[xy, xz, yz])

    def setTransformValues(self, transformValues, worldSpace=False):
        """set transform values

        :param transformValues: transform values to set
        :type transformValues: dict

        :param worldSpace: ``True`` : values are set in worldSpace - ``False`` : values are set in local
        :type worldSpace: bool
        """

        # execute
        self._setTransformValues(transformValues, worldSpace=worldSpace)

    def shapes(self, shapeTypes=None, shapeTypesIncluded=True):
        """the shapes parented under the transform

        :param shapeTypes: types of shape to get - All if nothing is specified
        :type shapeTypes: list[str]

        :param shapeTypesIncluded: ``True`` : shape types are included - ``False`` : shape types are excluded
        :type shapeTypesIncluded: bool

        :return: the shapes of the transform
        :rtype: list[:class:`cgp_maya_utils.scene.Shape`,
                     :class:`cgp_maya_utils.scene.NurbsCurve`,
                     :class:`cgp_maya_utils.scene.NurbsSurface`,
                     :class:`cgp_maya_utils.scene.Mesh`,]
        """

        # init
        returnShapes = []
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

        # execute
        for shapeType in queryShapeTypes:
            for shape in maya.cmds.listRelatives(self.name(), shapes=True, type=shapeType) or []:
                returnShapes.append(cgp_maya_utils.scene.node(shape))

        # return
        return returnShapes

    def transformationMatrix(self, worldSpace=False, rotateOrder=None):
        """the transformationMatrix of the transform

        :param worldSpace: ``True`` : TransformationMatrix is initialized with the worldSpace transform values -
                           ``False`` : TransformationMatrix is initialized with the local transform values
        :type worldSpace: bool

        :param rotateOrder: rotateOrder to get the transform values in -
                            default is the current rotateOrder of the transform
        :type rotateOrder: str

        :return: the transformMatrix
        :rtype: :class:`cgp_generic_utils.api.TransformationMatrix`
        """

        # init
        matrixAttr = 'worldMatrix' if worldSpace else 'matrix'
        rotateOrder = rotateOrder or self.attribute('rotateOrder').value()

        # errors
        if rotateOrder and rotateOrder not in cgp_maya_utils.constants.RotateOrder.ALL:
            raise ValueError('{0} is not a valid rotateOrder - {1}'
                             .format(rotateOrder, cgp_maya_utils.constants.RotateOrder.ALL))

        # return
        return cgp_maya_utils.api.TransformationMatrix.fromAttribute('{0}.{1}'.format(self.name(), matrixAttr),
                                                                     rotateOrder=rotateOrder)

    def transformValues(self, worldSpace=False, rotateOrder=None):
        """the transform values

        :param worldSpace: ``True`` : transform values are worldSpace - ``False`` : transform values are local
        :type worldSpace: bool

        :param rotateOrder: rotateOrder to get the transform values in ! ONLY IN WORLDSPACE !
        :type rotateOrder: str

        :return: the transform values
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
        :type mode: str
        """

        # get infos
        values = self.transformationMatrix(worldSpace=worldSpace).transformValues()
        isRelative = mode == cgp_generic_utils.constants.TransformMode.RELATIVE

        # update values
        if isRelative:
            x = x if x is not None else 0
            y = y if y is not None else 0
            z = z if z is not None else 0
        else:
            x = x if x is not None else values[cgp_maya_utils.constants.Transform.TRANSLATE_X]
            y = y if y is not None else values[cgp_maya_utils.constants.Transform.TRANSLATE_Y]
            z = z if z is not None else values[cgp_maya_utils.constants.Transform.TRANSLATE_Z]

        # set values
        maya.cmds.xform(self.name(), worldSpace=worldSpace, relative=isRelative, translation=[x, y, z])

    # PRIVATE COMMANDS #

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(Transform, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['displayRotatePivot',
                                    'displayScalePivot'])

        # return
        return availableAttributes

    @staticmethod
    def _formatAttributes(attributes):
        """format the transform attributes into a formated data list

        :param attributes: attributes to format
        :type attributes: list[str]

        :return: the formated attributes
        :rtype: list[str]
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

    @cgp_maya_utils.decorators.KeepCurrentSelection()
    def _setTransformValues(self, values, attributes=None, worldSpace=False):
        """set transform values from the dictionary to the specified object

        :param values: the dictionary of the transform values to set on the specified object
        :type values: dict

        :param attributes: transform attributes to set - default is ``cgp_maya_utils.constants.Transform.GENERAL``
        :type attributes: list[str]

        :param worldSpace: ``True`` : transform values are set on worldSpace -
                           ``False`` : transform values are set on local
        :type worldSpace: bool
        """

        # init
        attributes = self._formatAttributes(attributes)

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

                # get infos
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
            fullAttribute = '{0}.{1}'.format(self.name(), attribute)

            # get connections
            genConnections = self.connections([attribute[0]],
                                              nodeTypes=cgp_maya_utils.constants.NodeType.ANIM_CURVES,
                                              nodeTypesIncluded=False,
                                              sources=True,
                                              destinations=False)

            fullConnections = self.connections([attribute],
                                               nodeTypes=cgp_maya_utils.constants.NodeType.ANIM_CURVES,
                                               nodeTypesIncluded=False,
                                               sources=True,
                                               destinations=False)

            # set
            if not maya.cmds.getAttr(fullAttribute, lock=True) and not fullConnections and not genConnections:
                maya.cmds.setAttr(fullAttribute, flattenValues[attribute])


# TRANSFORM OBJECTS #


class Joint(Transform):
    """node object that manipulates a ``joint`` node
    """

    # ATTRIBUTES #

    _nodeType = 'joint'

    # PRIVATE COMMANDS #

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(Joint, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['drawLabel',
                                    'jointOrient',
                                    'otherType',
                                    'segmentScaleCompensate',
                                    'side',
                                    'type'])

        # return
        return availableAttributes
