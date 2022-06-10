"""
geometryFilter object library
"""

# imports third-parties
import maya.cmds
import maya.api.OpenMaya

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.scene._api
from . import _generic


# BASE OBJECT #


class GeometryFilter(_generic.Node):
    """node object that manipulates any kind of geometry filter node
    """

    # ATTRIBUTES #

    _nodeType = 'geometryFilter'

    # STATIC COMMANDS #

    @classmethod
    def create(cls, geometry, connections=None, attributeValues=None, name=None, **kwargs):
        """create a geometry filter

        :param geometry: geometry to bind the created geometry filter to
        :type geometry: str

        :param connections: connections to set on the created geometry filter
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the created geometry filter
        :type attributeValues: dict

        :param name: name of the created geometry filter
        :type name: str

        :return: the created geometry filter object
        :rtype: :class:`cgp_maya_utils.scene.GeometryFilter`
        """

        # errors
        if cls._nodeType == 'geometryFilter':
            raise RuntimeError('GeometryFilter.create is not callable for untyped geometry filters')

        # create node
        deformerNode = maya.cmds.deformer(geometry, type=cls._nodeType, name=name or cls._nodeType)[0]
        deformerObject = cls(deformerNode)

        # set attributeValues
        if attributeValues:
            deformerObject.setAttributeValues(attributeValues)

        # set connections
        if connections:
            deformerObject.setConnections(connections)

        # return
        return deformerObject

    # COMMANDS #

    def bind(self, shape):
        """bind the geometry filter to the specified shape

        :param shape: shape the geometry filter node will be bound to - can be the shape or its transform
        :type shape: str or :class:`cgp_maya_utils.scene.Shape` or :class:`cgp_maya_utils.scene.Transform`
        """

        # execute
        maya.cmds.deformer(self.name(), edit=True, geometry=str(shape))

    def copy(self, shape, byProximity=True):
        """copy the geometry filter node to the shape

        :param shape: shape on which to copy the geometry filter node
        :type shape: str or :class:`cgp_maya_utils.scene.Shape`

        :param byProximity: ``True`` : weights are copied by proximity - ``False`` : weights are injected on points
        :type byProximity: bool
        """

        # execute
        raise NotImplementedError('copy needs to be implemented')

    def data(self):
        """data necessary to store the geometry filter node on disk and/or recreate it from scratch

        :return: the data of the geometry filter node
        :rtype: dict
        """

        # init
        data = super(GeometryFilter, self).data()

        # update data
        data['shapes'] = [sh.name() for sh in self.shapes()]
        data['weights'] = self.weights()

        # return
        return data

    def reset(self):
        """reset the geometry filter node
        """

        # execute
        raise NotImplementedError('{0}.reset() needs to be implemented'.format(self.__class__.__name__))

    def shapes(self):
        """the shapes deformed by the geometry filter node

        :return: the deformed shapes
        :rtype: list[:class:`cgp_maya_utils.scene.Shape`]
        """

        # get shapes
        shapes = maya.cmds.deformer(self.name(), query=True, geometry=True)

        # return
        return [cgp_maya_utils.scene._api.node(sh) for sh in shapes]

    def weights(self):
        """the weights of the geometry filter node - same weights that are accessible through painting

        :return: the weights of the geometry filter node
        :rtype: any
        """

        # execute
        raise NotImplementedError('{0}.weights() needs to be implemented'.format(self.__class__.__name__))

    # PRIVATE COMMANDS #

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(GeometryFilter, self)._availableAttributes()

        # update settingAttributes
        availableAttributes.extend(['envelope'])

        # return
        return availableAttributes


# GEOMETRY FILTER OBJECTS #


class BlendShape(GeometryFilter):

    # ATTRIBUTES #

    _nodeType = 'blendShape'

    # PROPERTIES #

    @property
    def _availableAttributes(self):
        """get the setting attributes

        :return: the setting attributes
        :rtype: dict
        """

        # init
        settingAttributes = super(GeometryFilter, self)._availableAttributes

        # update settingAttributes
        settingAttributes.extend(['supportNegativeWeights'])

        # return
        return settingAttributes

    # OBJECT COMMANDS #

    def setTarget(self, name, positions, indexes):
        """set a target to the blendShape - if target name is already exists, target will be updated. Otherwise,
        a new target will be created at the bottom of the target list

        :param name: name of the target to set
        :type name: str

        :param positions: positions of the vertices of the target - [[x1, y1, z1], [x2, y2, z2], ...]
        :type positions: list[list[float]] or array[array[float]]

        :param indexes: indexes of the vertices of the target - [index1, index2 ...]
        :type indexes: list[int] or array[int]
        """

        # errors
        if not len(positions) == len(indexes):
            raise ValueError('positions and indexes lists don\'t have the same dimension - '
                             'positions : {0} - indexes : {1}'.format(len(positions), len(indexes)))

        # get blendShape targets
        targets = self.targets()

        # get target plugs
        inputTargetPlug = self.mFn().findPlug('inputTarget', True)
        inputTargetGrpPlug = inputTargetPlug.elementByLogicalIndex(0).child(0)

        shapeIndex = targets.index(name) if name in targets else inputTargetGrpPlug.numElements()
        inputTargetItemPlug = inputTargetGrpPlug.elementByLogicalIndex(shapeIndex).child(0).elementByLogicalIndex(6000)

        inputPointsTargetPlug = inputTargetItemPlug.child(3)
        inputComponentTargetPlug = inputTargetItemPlug.child(4)

        # set pointArray attribute - deltas
        pointArray = maya.api.OpenMaya.MPointArray(positions)
        pointArrayData = maya.api.OpenMaya.MFnPointArrayData()
        pointArrayObject = pointArrayData.create(pointArray)

        inputPointsTargetPlug.setMObject(pointArrayObject)

        # set componentList attribute - indexes
        singleIndexedComponent = maya.api.OpenMaya.MFnSingleIndexedComponent()
        singleIndexedComponent.create(maya.api.OpenMaya.MFn.kMeshVertComponent)
        singleIndexedComponent.addElements(indexes)
        componentListData = maya.api.OpenMaya.MFnComponentListData()
        componentListData.create()
        componentListData.add(singleIndexedComponent.object())

        inputComponentTargetPlug.setMObject(componentListData.object())

        # set weight value and alias
        maya.cmds.setAttr('{0}.weight[{1}]'.format(self.name(), shapeIndex), 0.0, keyable=True)
        maya.cmds.aliasAttr(name, '{0}.weight[{1}]'.format(self.name(), shapeIndex))

    def targets(self):
        """get the list of targets of the blendShape

        :return: targets of the blendShape
        :rtype: list[str]
        """

        # return
        return maya.cmds.listAttr(self.name(), multi=True, string='weight') or []


class SkinCluster(GeometryFilter):
    """node object that manipulates a ``skinCluster`` node
    """

    # ATTRIBUTES #

    _nodeType = 'skinCluster'

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, shapes, influences, weights=None, bindPreMatrixes=None, attributeValues=None, name=None, **__):
        """create a skinCluster

        :param shapes: shapes that will be deformed by the skinCluster
        :type shapes: list[str] or list[:class:`cgp_maya_utils.scene.Shape`]

        :param influences: influences that will drive the skinCluster
        :type influences: list[str] or list[:class:`cgp_maya_utils.scene.Joint`, :class:`cgp_maya_utils.scene.Shape`]

        :param weights: weights of the skin cluster - ``{influence1: [], influence2: [] ...}``
        :type weights: dict[str: list[int, float]]

        :param bindPreMatrixes: bindPreMatrixes of the skinCluster -
                                ``{influence1: matrixAttribute1, influence2: matrixAttribute2 ...}``
        :type bindPreMatrixes: dict

        :param attributeValues: attribute values to set on the skinCluster node
        :type attributeValues: dict

        :param name: name of the skinCluster node
        :type name: str

        :return: the created skinCluster
        :rtype: :class:`cgp_maya_utils.scene.SkinCluster`
        """

        # init
        shapes = [str(shape) for shape in shapes]
        influences = [str(influence) for influence in influences]
        name = name or cls._nodeType
        tempJt = None
        obj = cgp_maya_utils.scene._api.node(shapes[0])
        buildObj = obj

        # build duplicate geometry if skinCluster already existing
        if obj.geometryFilters(geometryFilterTypes=['skinCluster']):
            buildObj = obj.duplicate()

        # get joints and geometric Deformers list
        geos = [influence
                for influence in influences
                if not maya.cmds.nodeType(str(influence)) == cgp_maya_utils.constants.NodeType.JOINT]

        joints = [influence
                  for influence in influences
                  if maya.cmds.nodeType(str(influence)) == cgp_maya_utils.constants.NodeType.JOINT]

        # create temp joint if no joints specified
        if not joints:
            tempJt = cgp_maya_utils.scene._api._NODE_TYPES['joint'].create()
            joints = [tempJt]

        # build skinCluster
        skinCluster = cls(maya.cmds.skinCluster(joints, buildObj,
                                                toSelectedBones=True,
                                                normalizeWeights=1,
                                                name=name)[0])

        # add geo to skinCluster
        for geo in geos:
            skinCluster.addInfluence(geo)

        # remove tempJt from skin if existing and delete
        if tempJt:
            skinCluster.removeInfluence(tempJt)
            maya.cmds.delete(tempJt)

        # transfer skin from buildObj to obj if necessary
        if not buildObj == obj:
            skinCluster.bind(obj)
            buildObj.delete()

        # set weights
        if weights:
            skinCluster.setWeights(weights)

        # build bindPreMatrixes
        if bindPreMatrixes:
            skinCluster.connectBindPreMatrixes(bindPreMatrixes=bindPreMatrixes)

        # set attributeValues
        if attributeValues:
            skinCluster.setAttributeValues(attributeValues)

        # add other shapes
        if len(shapes) > 1:
            for shape in shapes[1:]:
                skinCluster.bind(shape)

        # return
        return skinCluster

    # COMMANDS #

    def addInfluence(self, influence):
        """add influence to the skinCluster

        :param influence: influence to add to the skinCluster
        :type influence: str
        """

        # init
        influence = str(influence)

        # add joint
        if maya.cmds.nodeType(influence) == cgp_maya_utils.constants.NodeType.JOINT:
            maya.cmds.skinCluster(self.name(),
                                  edit=True,
                                  addInfluence=str(influence),
                                  toSelectedBones=True,
                                  lockWeights=True,
                                  weight=0)

        # add anything else
        else:
            maya.cmds.skinCluster(self.name(),
                                  edit=True,
                                  addInfluence=influence,
                                  useGeometry=True,
                                  toSelectedBones=True)

            self.attribute('useComponents').setValue(1)

        # set lockInfluenceWeight
        maya.cmds.setAttr('{0}.liw'.format(influence), 0)

    def bindPreMatrixes(self):
        """get the bindPreMatrixes of the skinCluster

        :return: bindPreMatrixes dictionary - ``{influence1: matrixAttribute1, influence2: matrixAttribute2 ...}``
        :rtype: dict[str: str]
        """

        # init
        data = {}

        # get matrix connections
        matrixConnections = self.connections(attributes=['matrix'], sources=True, destinations=False)

        # execute
        for matrixConnection in matrixConnections:

            # get bindPreMatrix connections
            bpmAttribute = matrixConnection.destination().name().replace('matrix', 'bindPreMatrix')
            connections = self.connections(attributes=[bpmAttribute], sources=True, destinations=False)

            # update
            matrixAttribute = matrixConnection.source().node().name()
            data[matrixAttribute] = None

            if connections:
                data[matrixAttribute] = connections[0].source().fullName()

        # return
        return data

    def connectBindPreMatrixes(self, bindPreMatrixes=None):
        """connect the bindPreMatrixes of the skinCluster

        :param bindPreMatrixes: bindPreMatrixes of the skinCluster -
                                ``{influence1: matrixAttribute1, influence2: matrixAttribute2 ...}``
        :type bindPreMatrixes: dict
        """

        # remove existing bpm connections
        connections = self.connections(attributes=['bindPreMatrix'], sources=True, destinations=False)

        for connection in connections:
            connection.disconnect()

        # build bpm
        if bindPreMatrixes:

            # get matrix connections
            matrixConnections = self.connections(attributes=['matrix'], sources=True, destinations=True)

            # execute
            for matrixConnection in matrixConnections:

                # get bpm connections
                influence = matrixConnection.source().node().name()
                bpmAttr = matrixConnection.destination().fullName().replace('.matrix', '.bindPreMatrix')

                # build bpm connection
                if bindPreMatrixes[influence]:
                    maya.cmds.connectAttr(bindPreMatrixes[influence], bpmAttr, force=True)

    def copy(self, shape, byProximity=True):
        """copy the skinCluster to the shape

        :param shape: shape on which to copy the skinCluster
        :type shape: str or :class:`cgp_maya_utils.scene.Shape`

        :param byProximity: ``True`` : weights are copied by proximity - ``False`` : weights are injected on points
        :type byProximity: bool

        :return: the created copied SkinCluster
        :rtype: :class:`cgp_maya_utils.scene.SkinCluster`
        """

        # errors
        if not self.shapes():
            raise RuntimeError('{0} has no shapes to copy from'.format(self.name()))

        # build target skinCluster
        targetSkin = self.create([shape],
                                 influences=self.influences(),
                                 bpm=self.bindPreMatrixes(),
                                 attributeValues=self.attributeValues())

        # update target skinCluster influences
        if byProximity:
            maya.cmds.copySkinWeights(sourceSkin=self.name(),
                                      destinationSkin=targetSkin.name(),
                                      noMirror=True,
                                      surfaceAssociation=cgp_maya_utils.constants.SurfaceAssociation.CLOSEST_POINT,
                                      influenceAssociation=(cgp_maya_utils.constants.InfluenceAssociation.CLOSEST_JOINT,
                                                            cgp_maya_utils.constants.InfluenceAssociation.ONE_TO_ONE,
                                                            cgp_maya_utils.constants.InfluenceAssociation.ONE_TO_ONE))

        else:
            targetSkin.setWeights(self.weights())

        # return
        return targetSkin

    def data(self):
        """data necessary to store the skinCluster node on disk and/or recreate it from scratch

        :return: the data of the skinCluster node
        :rtype: dict
        """

        # init
        data = super(SkinCluster, self).data()

        # update data
        data['bindPreMatrixes'] = self.bindPreMatrixes()
        data['influences'] = [influence.name() for influence in self.influences()]
        data['weights'] = self.weights()

        # return
        return data

    def influences(self):
        """the influences of the skinCluster

        :return: the influences of the skinCluster
        :rtype: list[:class:`cgp_maya_utils.scene.Joint`, :class:`cgp_maya_utils.scene.Shape`]
        """

        # get influences
        influences = maya.cmds.skinCluster(self.name(), query=True, influence=True) or []

        # return
        return [cgp_maya_utils.scene._api.node(influence) for influence in influences]

    def removeInfluence(self, influence):
        """remove an influence from the skinCluster

        :param influence: the influence to remove from the skinCluster
        :type influence: str or :class:`cgp_maya_utils.scene.Joint` or :class:`cgp_maya_utils.scene.Shape`
        """

        # execute
        maya.cmds.skinCluster(self.name(), edit=True, removeInfluence=str(influence))

    def recacheBindMatrices(self):
        """recache the bind matrixes of the skinCluster
        """

        # execute
        maya.cmds.skinCluster(self.name(), edit=True, recacheBindMatrices=True)

    def reset(self):
        """reset the skinCluster
        """

        # get matrix connections
        matrixConnections = self.connections(attributes=['matrix'], sources=True, destinations=True)

        # execute
        for matrixConnection in matrixConnections:

            # get bindPreMatrix attribute
            bpmAttribute = cgp_maya_utils.scene._api.attribute(matrixConnection.destination().fullName()
                                                               .replace('matrix', 'bindPreMatrix'))

            # get matrix values
            matrixValues = matrixConnection.source().node().attribute('worldInverseMatrix').value()

            # update bpm attribute
            if not bpmAttribute.connections(source=True, destinations=False):
                bpmAttribute.setValue(matrixValues)

        # recache bindMatrices
        self.recacheBindMatrices()

    def setWeights(self, weights):
        """set the weights of the skinCluster

        :param weights: weights to set on the skinCluster - ``{influence1: [], influence2: [] ...}``
        :type weights: dict
        """

        # init
        influences = self.influences()
        pttAttribute = self.attribute('ptt')
        ptwAttribute = self.attribute('ptw')

        # unlock and deselect all joints in the skin tool
        for influence in influences:
            influence.attribute('liw').setValue(0)

        # flood to 1 on first joint
        maya.cmds.skinPercent(self.name(), self.shapes()[0], transformValue=(str(influences[0]), 1))
        pttAttribute.connect(source='{0}.message'.format(influences[0]))

        # apply influences
        for influence in influences[1:]:

            # warning
            if influence.name() not in weights:
                maya.cmds.warning('{0} doesn\'t have stored weights ! skipped !'.format(influence))

            # apply
            else:

                # connect joint to paint attribute
                pttAttribute.connect(source='{0}.message'.format(influence))

                # set paint attribute and lock joint
                ptwAttribute.setValue(weights[influence.name()])
                influence.attribute('liw').setValue(1)

                # refresh the view
                maya.cmds.refresh()

    def swapInfluences(self, oldFlag, newFlag, reset=True):
        """swap current influences by new influences using the flags

        :param oldFlag: flag that will be replaced by the new flag
        :type oldFlag: str

        :param newFlag: flag that will replace the old flag
        :type newFlag: str

        :param reset: ``True`` : skinCluster will be reset after the swap - ``False`` : skinCluster will not be reset
        :type reset: bool
        """

        # get skinCluster connections
        connections = self.connections(attributes=['matrix', 'bindPreMatrix'],
                                       sources=True,
                                       destinations=False)

        # reconnect
        for connection in connections:

            # get new influence
            newInfluenceAttr = connection.source().fullName().replace(oldFlag, newFlag)

            # errors
            if not maya.cmds.objExists(newInfluenceAttr):
                maya.cmds.warning('{0} is not an existing influence - skipped'.format(newInfluenceAttr.split('.')[0]))
                continue

            # update targetAttr connection
            connection.destination().connect(source=newInfluenceAttr)

        # reset skinCluster if specified
        if reset:
            self.reset()

    def unusedInfluences(self):
        """the unused influences of the skinCluster

        :return: the unused influences
        :rtype: list[:class:`cgp_maya_utils.scene.Joint`, Shape]
        """

        # get weightedInfluences
        weightedInfluences = maya.cmds.skinCluster(self.name(), query=True, weightedInfluence=True) or []

        # return
        return [influence for influence in self.influences() if influence not in weightedInfluences]

    def weights(self):
        """the weights of the geometry filter node - same weights that are accessible through painting

        :return: the weights of the skinCluster - ``{joint1: [], joint2: [] ...}``
        :rtype: dict
        """

        # init
        data = {}
        pttAttribute = self.attribute('ptt')
        ptwAttribute = self.attribute('ptw')

        # save Skin Weights
        for influence in self.influences():

            # connect paint attribute
            pttAttribute.connect('{0}.message'.format(influence))

            # update data
            data[str(influence)] = ptwAttribute.value()

        # return
        return data

    # PRIVATE COMMANDS #

    def _availableAttributes(self):
        """the attributes that are listed by the ``Node.attributes`` function

        :return: the available attributes
        :rtype: list[str]
        """

        # init
        availableAttributes = super(SkinCluster, self)._availableAttributes()

        # return
        availableAttributes.extend(['deformUserNormals',
                                    'dqsScale',
                                    'dqsSupportNonRigid',
                                    'normalizeWeights',
                                    'skinningMethod',
                                    'useComponents',
                                    'weightDistribution'])

        # return
        return availableAttributes
