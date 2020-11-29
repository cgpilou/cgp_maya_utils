"""
subclassed OpenMaya api objects
"""

# imports python
import math

# imports third-parties
import maya.api.OpenMaya
import maya.cmds

# imports local
import cgp_maya_utils.constants


class MayaObject(maya.api.OpenMaya.MObject):
    """MObject with custom functionalities
    """

    # INIT #

    def __init__(self, node):
        """MayaObject class initialization

        :param node: node to get the MayaObject from
        :type node: str or :class:`cgp_maya_utils.scene.Node`
        """

        # init
        self._node = node

        # get selection list
        selection_list = maya.api.OpenMaya.MSelectionList()
        selection_list.add(str(node))

        # get mObject
        mObject = selection_list.getDependNode(0)

        # init
        super(MayaObject, self).__init__(mObject)

    def __repr__(self):
        """the representation of the maya object

        :return: the representation of the maya object
        :rtype: str
        """

        # return
        return 'MayaObject(\'{0}\')'.format(self._node)


class TransformationMatrix(maya.api.OpenMaya.MTransformationMatrix):
    """MTransformationMatrix with custom functionalities
    """

    # INIT #

    def __init__(self, matrix=None, translate=None, rotate=None, scale=None, shear=None, rotateOrder=None):
        """TransformationMatrix class initialization

        :param matrix: matrix used to initialize the transformationMatrix - MMatrix or matrixList[16]
        :type matrix: list[int, float] or :class:`maya.api.OpenMaya.MMatrix`

        :param translate: value of translation of the transformationMatrix - ONLY IF MATRIX NOT SPECIFIED
        :type translate: list[int, float]

        :param rotate: value of rotation of the transformationMatrix - ONLY IF MATRIX NOT SPECIFIED
        :type rotate: list[int, float]

        :param scale: value of scale of the transformationMatrix - ONLY IF MATRIX NOT SPECIFIED
        :type scale: list[int, float]

        :param shear: value of shear of the transformationMatrix - ONLY IF MATRIX NOT SPECIFIED
        :type shear: list[int, float]

        :param rotateOrder: value of rotateOrder of the transformationMatrix
        :type rotateOrder: :str

        :return: the transformation matrix
        :rtype: :class:`cgp_maya_utils.api.TransformationMatrix`
        """

        # matrix list mode
        if matrix:

            # init MMatrix if necessary
            if isinstance(matrix, list):
                matrix = maya.api.OpenMaya.MMatrix(matrix)

            # init TransformationMatrix
            super(TransformationMatrix, self).__init__(matrix)

            # set rotateOrder
            self.setRotateOrder(rotateOrder)

        # transform mode
        else:

            # init
            super(TransformationMatrix, self).__init__()
            translate = translate or [0, 0, 0]
            rotate = [math.radians(angle) for angle in rotate] if rotate else [0, 0, 0]
            scale = scale or [1, 1, 1]
            shear = shear or [0, 0, 0]
            rotateOrder = rotateOrder or cgp_maya_utils.constants.RotateOrder.XYZ

            # set rotateOrder
            self.setRotateOrder(rotateOrder)

            # set translations
            self.setTranslation(maya.api.OpenMaya.MVector(*translate), maya.api.OpenMaya.MSpace.kWorld)

            # set rotations
            eulerRotation = maya.api.OpenMaya.MEulerRotation()
            eulerRotateOrder = getattr(eulerRotation, 'k{0}'.format(rotateOrder.upper()))
            eulerRotation.setValue(maya.api.OpenMaya.MVector(*rotate), eulerRotateOrder)
            self.setRotation(eulerRotation)

            # set scale
            self.setScale(scale, maya.api.OpenMaya.MSpace.kWorld)

            # set shear
            self.setShear(shear, maya.api.OpenMaya.MSpace.kWorld)

    def __repr__(self):
        """the representation of the TransformationMatrix

        :return: the representation of the TransformationMatrix
        :rtype: str
        """

        # return
        return 'TransformationMatrix([{0}])'.format(str(self.asMatrix())[2:-2])

    # OPERATORS #

    def __mul__(self, matrix):
        """multiply the transformationMatrix by a MtransformationMatrix/MMatrix

        :param matrix: matrix to multiply to the transformationMatrix
        :type matrix: :class:`maya.api.OpenMaya.MMatrix` or :class:`maya.api.OpenMaya.MTransformationMatrix`

        :return: the multiplied transformationMatrix
        :rtype: :class:`cgp_maya_utils.api.TransformationMatrix`
        """

        # init
        matrix = matrix if isinstance(matrix, maya.api.OpenMaya.MMatrix) else matrix.asMatrix()

        # multiply
        result = self.asMatrix() * matrix

        # return
        return TransformationMatrix.fromMatrix(result, rotateOrder=self.rotateOrder())

    # OBJECT COMMANDS #

    @classmethod
    def fromAttribute(cls, attribute, rotateOrder=None):
        """get the transformationMatrix from the specified attribute

        :param attribute: attribute to get the matrix from - transform.matrix
        :type attribute: str or :class:`cgp_maya_utils.scene.Attribute`

        :param rotateOrder: rotateOrder of the transformationMatrix to get - use transform one if nothing specified
        :type rotateOrder: str

        :return: the transformationMatrix
        :rtype: :class:`cgp_maya_utils.api.TransformationMatrix`
        """

        # init
        attribute = str(attribute)
        rotateOrder = rotateOrder or maya.cmds.getAttr('{0}.rotateOrder'.format(attribute.split('.')[0]), asString=True)

        # execute
        matrix = maya.cmds.getAttr(attribute)

        # return
        return cls(matrix=matrix, rotateOrder=rotateOrder)

    @classmethod
    def fromMatrix(cls, matrix, rotateOrder=None):
        """get the transformationMatrix from the specified matrix

        :param matrix: MMatrix or 16 numbers list used to initialize the transformationMatrix
        :type matrix: list[int, float] or :class:`maya.api.OpenMaya.MMatrix`

        :param rotateOrder: rotateOrder of the transformationMatrix to get
        :type rotateOrder: str

        :return: the transformationMatrix
        :rtype: :class:`cgp_maya_utils.api.TransformationMatrix`
        """

        # init
        rotateOrder = rotateOrder or cgp_maya_utils.constants.RotateOrder.XYZ

        # return
        return cls(matrix=matrix, rotateOrder=rotateOrder)

    @classmethod
    def fromTransforms(cls, translate=None, rotate=None, scale=None, shear=None, rotateOrder=None):
        """get the transformationMatrix from the specified transforms

        :param translate: value of translation of the transformationMatrix
        :type translate: list[int, float]

        :param rotate: value of rotation of the transformationMatrix
        :type rotate: list[int, float]

        :param scale: value of scale of the transformationMatrix
        :type scale: list[int, float]

        :param shear: value of shear of the transformationMatrix
        :type shear: list[int, float]

        :param rotateOrder: rotateOrder of the transformationMatrix to get
        :type rotateOrder: str

        :return: the transformationMatrix
        :rtype: :class:`cgp_maya_utils.api.TransformationMatrix`
        """

        # return
        return cls(translate=translate, rotate=rotate, scale=scale, shear=shear, rotateOrder=rotateOrder)

    # COMMANDS #

    def rotateOrder(self):
        """the rotateOrder of the transformationMatrix

        :return: the rotateOrder
        :rtype: str
        """

        # return
        return cgp_maya_utils.constants.RotateOrder.ALL[self.rotationOrder() - 1]

    def setRotateOrder(self, rotateOrder):
        """set the rotateOrder of the transformationMatrix

        :param rotateOrder: new rotateOrder of the transformationMatrix
        :type rotateOrder: str
        """

        # errors
        if rotateOrder not in cgp_maya_utils.constants.RotateOrder.ALL:
            raise ValueError('{0} is not a valid rotateOrder - {1}'
                             .format(rotateOrder, cgp_maya_utils.constants.RotateOrder.ALL))

        # execute
        mRotateOrder = getattr(self, 'k{0}'.format(rotateOrder.upper()))
        self.reorderRotation(mRotateOrder)

    def transformValues(self):
        """the transform values stored in the transformation matrix

        :return: the transform values of the transformation matrix
        :rtype: dict
        """

        # get values
        translate = self.translation(maya.api.OpenMaya.MSpace.kWorld)
        rotate = self.rotation()
        scale = self.scale(maya.api.OpenMaya.MSpace.kObject)
        shear = self.shear(maya.api.OpenMaya.MSpace.kObject)

        # return
        return {'rotateOrder': self.rotateOrder(),
                'translate': [translate.x, translate.y, translate.z],
                'rotate': [math.degrees(angle) for angle in rotate],
                'scale': scale,
                'shear': shear}
