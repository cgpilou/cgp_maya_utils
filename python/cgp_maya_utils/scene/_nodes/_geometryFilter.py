"""
geometryFilter object library
"""

# imports third-parties
import maya.cmds
import maya.api.OpenMaya

# imports local
import cgp_maya_utils.constants
import cgp_maya_utils.decorators
import cgp_maya_utils.scene._api
from . import _generic


# BASE OBJECT #


class GeometryFilter(_generic.Node):
    """node object that manipulates any kind of geometryFilter node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.GEOMETRY_FILTER

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, geometry, connections=None, attributeValues=None, name=None, **__):
        """create a geometryFilter

        :param geometry: geometry to bind the created geometryFilter to
        :type geometry: str

        :param connections: connections to set on the created geometryFilter
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the created geometryFilter
        :type attributeValues: dict

        :param name: name of the created geometryFilter
        :type name: str

        :return: the created geometryFilter object
        :rtype: :class:`cgp_maya_utils.scene.GeometryFilter`
        """

        # errors
        if cls._TYPE == cgp_maya_utils.constants.NodeType.GEOMETRY_FILTER:
            raise RuntimeError('GeometryFilter.create is not callable for untyped geometryFilters')

        # create node
        deformerNode = maya.cmds.deformer(geometry, type=cls._TYPE, name=name or cls._TYPE)[0]
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
        """bind the geometryFilter to the shape

        :param shape: shape the geometryFilter will be bound to - can be the shape or its transform
        :type shape: str or :class:`cgp_maya_utils.scene.Shape` or :class:`cgp_maya_utils.Transform`
        """

        # execute
        maya.cmds.deformer(self.fullName(), edit=True, geometry=str(shape))

    def copy(self, shape, byProximity=True):
        """copy the geometryFilter to the shape

        :param shape: shape on which to copy the geometryFilter
        :type shape: str

        :param byProximity: ``True`` : weights are copied by proximity - ``False`` : weights are injected on points
        :type byProximity: bool
        """

        # execute
        raise NotImplementedError('copy needs to be implemented')

    def data(self):
        """data necessary to store the geometryFilter node on disk and/or recreate it from scratch

        :return: the data of the geometryFilter
        :rtype: dict
        """

        # init
        data = super(GeometryFilter, self).data()

        # update data
        data['shapes'] = [shape.fullName() for shape in self.shapes()]
        data['weights'] = self.weights()

        # return
        return data

    def reset(self):
        """reset the geometryFilter
        """

        # execute
        raise NotImplementedError('reset needs to be implemented')

    def setData(self, data):
        """set the data on the geometryFilter

        :param data: data used to set the geometryFilter
        :type data: dict
        """

        # execute
        raise NotImplementedError('setData needs to be implemented')

    def shapes(self):
        """get the shapes deformed by the geometryFilter

        :return: the shapes of the geometryFilter
        :rtype: list[:class:`cgp_maya_utils.scene.Shape`]
        """

        # get shapes
        shapes = maya.cmds.deformer(self.fullName(), query=True, geometry=True) or []

        # return
        return [cgp_maya_utils.scene._api.node(sh) for sh in shapes]

    def setShapes(self, shapes):
        """set the shapes deformed by the geometryFilter

        :param shapes: the shapes that will be deformed by the geometryFilter
        :type shapes: list[str] or list[:class:`cgp_maya_utils.scene.Shape`]
        """

        # init
        fullName = self.fullName()

        # get the current shapes
        currentlyDeformed = self.shapes()

        # remove unwanted shapes
        toRemove = [geometry for geometry in currentlyDeformed if geometry not in shapes]
        if toRemove:
            maya.cmds.deformer(fullName, edit=True, geometry=toRemove, remove=True)

        # add missing shapes
        maya.cmds.deformer(fullName, edit=True, geometry=shapes)

    def weights(self):
        """get the weights of the geometryFilter - same weights that are accessible through painting

        :return: the weights of the geometryFilter
        :rtype: any
        """

        # execute
        raise NotImplementedError('weights needs to be implemented')


# DEFORMER OBJECTS #


class BlendShape(GeometryFilter):
    """node object that manipulates a ``blendShape`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.BLEND_SHAPE

    # COMMANDS #

    def setTarget(self, name, positions, indexes):
        """set a target to the blendShape - if target name is already exists, target will be updated. Otherwise,
        a new target will be created at the bottom of the target list

        :param name: name of the target to set
        :type name: str

        :param positions: positions of the vertices of the target - ``[[x1, y1, z1], [x2, y2, z2], ...]``
        :type positions: list[list[float]] or array[array[float]]

        :param indexes: indexes of the vertices of the target - ``[index1, index2 ...]``
        :type indexes: list[int] or array[int]
        """

        # errors
        if not len(positions) == len(indexes):
            raise ValueError('positions and indexes lists don\'t have the same dimension - '
                             'positions : {0} - indexes : {1}'.format(len(positions), len(indexes)))

        # get blendShape targets
        targets = self.targets()

        # get target plugs
        inputTargetPlug = self.MFn().findPlug('inputTarget', True)
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
        fullName = self.fullName()
        maya.cmds.setAttr('{0}.weight[{1}]'.format(fullName, shapeIndex), 0.0, keyable=True)
        maya.cmds.aliasAttr(name, '{0}.weight[{1}]'.format(fullName, shapeIndex))

    def targets(self):
        """get the targets of the blendShape

        :return: targets of the blendShape
        :rtype: list[str]
        """

        # return
        return maya.cmds.listAttr(self.fullName(), multi=True, string='weight') or []


class SoftMod(GeometryFilter):
    """node object that manipulates a ``softMod`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.SOFT_MOD

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, shapesToDeform, name=None, weightedNode=None, connections=None, attributeValues=None, **__):
        """create a softMod

        :param shapesToDeform: shapes on which to create the softMod
        :type shapesToDeform: list[str] or list[:class:`cgp_maya_utils.Shape`]

        :param name: name of the created softMod
        :type name: str

        :param weightedNode: the node which will drive the softMod weight
        :type weightedNode: str or :class:`cgp_maya_utils3.scene.Node`

        :param connections: connections to set on the created softMod
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the created softMod
        :type attributeValues: dict

        :return: the created softMod
        :rtype: :class:`cgp_maya_utils.scene.SoftMod`
        """

        # init
        name = name or cls._TYPE

        # create the softMod
        with cgp_maya_utils.decorators.DisableIntermediateStatus(shapesToDeform):
            _, transformName = (maya.cmds.softMod(shapesToDeform,
                                                  weightedNode=(str(weightedNode), str(weightedNode)),
                                                  falloffAroundSelection=False,
                                                  falloffRadius=1)
                                if weightedNode
                                else maya.cmds.softMod(shapesToDeform,
                                                       falloffAroundSelection=False,
                                                       falloffRadius=1))

        # the maya command return the correct handle name but not the correct deformer name, so we need to find it
        deformerName = maya.cmds.listConnections(transformName,
                                                 source=False,
                                                 destination=True,
                                                 type=cgp_maya_utils.constants.NodeType.SOFT_MOD)[0]

        # generate the deformer instance
        instance = cls(deformerName)

        # match the desired name
        instance.setName(name)

        # set attributeValues
        if attributeValues:
            instance.setAttributeValues(attributeValues)

        # set connections
        if connections:
            instance.setConnections(connections)

        # return
        return instance

    def handle(self):
        """get the handle of the softMod

        :return: the handle of the softMod
        :rtype: Shape
        """

        # find the handle in the incoming connections
        attribute = self.attribute('softModXforms')
        connections = attribute.connections(source=True,
                                            destinations=False,
                                            nodeTypes=[cgp_maya_utils.constants.NodeType.SOFT_MOD_HANDLE])

        # return the handle if found
        return connections[0].source().node() if connections else None

    def shapes(self):
        """get the shapes deformed by the softMod

        :return: the shapes deformed by the softMod
        :rtype: Shape
        """

        # get all related shapes
        shapes = super(SoftMod, self).shapes()

        # disable intermediate objects to get correct shapes
        with cgp_maya_utils.decorators.DisableIntermediateStatus(shapes):
            shapes = super(SoftMod, self).shapes()

        # return
        return shapes

    def setShapes(self, shapes):
        """set the shapes deformed by the softMod

        :param shapes: the shapes to set on the softMod
        :type shapes: list[str] or list[:class:`cgp_maya_utils.scene.Shape`]
        """

        # init
        fullName = self.fullName()

        # get the geometries to remove
        toRemove = [geometry for geometry in self.shapes() if geometry not in shapes]

        # remove geometries
        if toRemove:
            with cgp_maya_utils.decorators.DisableIntermediateStatus(toRemove):
                maya.cmds.softMod(fullName, edit=True, geometry=toRemove, remove=True)

        # add missing shapes
        with cgp_maya_utils.decorators.DisableIntermediateStatus(shapes):
            maya.cmds.softMod(fullName, edit=True, geometry=shapes)

    def setWeightedNode(self, node):
        """set the weightedNode of the softMod

        :param node: the weightedNode of the softMod
        :type node: str or :class:`cgp_maya_utils.scene.Transform`
        """

        # execute
        maya.cmds.softMod(self.fullName(), edit=True, bindState=True, weightedNode=(str(node), str(node)))

    def weightedNode(self):
        """get the weightedNode of the softMod

        :return: the weightedNode of the softMod
        :rtype: Transform
        """

        # get the name of the weightedNode
        nodeName = maya.cmds.softMod(self.fullName(), query=True, weightedNode=True)

        # return
        return cgp_maya_utils.scene._api.node(nodeName) if nodeName else None


class SkinCluster(GeometryFilter):
    """node object that manipulates a ``skinCluster`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.SKINCLUSTER

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, shapes, influences, weights=None, bindPreMatrices=None, attributeValues=None, name=None, **__):
        """create a skinCluster

        :param shapes: shapes that will be deformed by the skinCluster
        :type shapes: list[str or :class:`cgp_maya_utils.scene.Shape`]

        :param influences: influences that will drive the skinCluster
        :type influences: list[str] or list[:class:`cgp_maya_utils.scene.Joint`, :class:`cgp_maya_utils.scene.Shape`]

        :param weights: weights of the skin cluster - ``{influence1: [], influence2: [] ...}``
        :type weights: dict[str: list[int, float]]

        :param bindPreMatrices: bindPreMatrices of the skinCluster -
                                ``{influence1: matrixAttribute1, influence2: matrixAttribute2 ...}``
        :type bindPreMatrices: dict

        :param attributeValues: attribute values to set on the skinCluster node
        :type attributeValues: dict

        :param name: name of the skinCluster node
        :type name: str

        :return: the created skinCluster
        :rtype: :class:`cgp_maya_utils.scene.SkinCluster`
        """

        # init
        name = name or cls._TYPE
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
        if bindPreMatrices:
            skinCluster.setBindPreMatrices(bindPreMatrices=bindPreMatrices)

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
        :type influence: str or :class:`cgp_maya_utils.scene.Joint` or :class:`cgp_maya_utils.scene.Shape`
        """

        # init
        influence = str(influence)
        fullName = self.fullName()

        # add joint
        if maya.cmds.nodeType(influence) == cgp_maya_utils.constants.NodeType.JOINT:
            maya.cmds.skinCluster(fullName,
                                  edit=True,
                                  addInfluence=str(influence),
                                  toSelectedBones=True,
                                  lockWeights=True,
                                  weight=0)

        # add anything else
        else:
            maya.cmds.skinCluster(fullName,
                                  edit=True,
                                  addInfluence=influence,
                                  useGeometry=True,
                                  toSelectedBones=True)

            self.attribute('useComponents').setValue(1)

        # set lockInfluenceWeight
        maya.cmds.setAttr('{0}.liw'.format(influence), 0)

    def bindPreMatrices(self):
        """get the bindPreMatrices of the skinCluster

        :return: bindPreMatrices dictionary - ``{influence1: matrixAttribute1, influence2: matrixAttribute2 ...}``
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
            matrixAttribute = matrixConnection.source().node().fullName()
            data[matrixAttribute] = None

            if connections:
                data[matrixAttribute] = connections[0].source().fullName()

        # return
        return data

    def copy(self, targetShape, byProximity=True):
        """copy the skinCluster to the target shape

        :param targetShape: shape on which to copy the skinCluster
        :type targetShape: str or :class:`cgp_maya_utils.Shape`

        :param byProximity: ``True`` : weights are copied by proximity - ``False`` : weights are injected on points
        :type byProximity: bool

        :return: the created copied SkinCluster
        :rtype: :class:`cgp_maya_utils.scene.SkinCluster`
        """

        # init
        shapes = self.shapes()
        fullName = self.fullName()

        # errors
        if not shapes:
            raise RuntimeError('{0} has no shapes to copy from'.format(fullName))

        # build target skinCluster
        targetSkin = self.create([str(targetShape)],
                                 influences=self.influences(),
                                 bpm=self.bindPreMatrices(),
                                 attributeValues=self.attributeValues())

        # update target skinCluster influences
        if byProximity:
            maya.cmds.copySkinWeights(sourceSkin=fullName,
                                      destinationSkin=targetSkin.fullName(),
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

        :return: the data of the skinCluster
        :rtype: dict
        """

        # init
        data = super(SkinCluster, self).data()

        # update data
        data['bindPreMatrixes'] = self.bindPreMatrices()
        data['influences'] = [influence.name() for influence in self.influences()]
        data['weights'] = self.weights()

        # return
        return data

    def influences(self):
        """get the influences of the skinCluster

        :return: the influences of the skinCluster
        :rtype: list[:class:`cgp_maya_utils.scene.Joint`, :class:`cgp_maya_utils.scene.Shape`]
        """

        # get influences
        influences = maya.cmds.skinCluster(self.fullName(), query=True, influence=True) or []

        # return
        return [cgp_maya_utils.scene._api.node(influence) for influence in influences]

    def removeInfluence(self, influence):
        """remove the influence from the skinCluster

        :param influence: the influence to remove from the skinCluster
        :type influence: str or :class:`cgp_maya_utils.scene.Joint` or :class:`cgp_maya_utils.scene.Shape`
        """

        # execute
        maya.cmds.skinCluster(self.fullName(), edit=True, removeInfluence=str(influence))

    def recacheBindMatrices(self):
        """recache the bindMatrices of the skinCluster
        """

        # execute
        maya.cmds.skinCluster(self.fullName(), edit=True, recacheBindMatrices=True)

    def reset(self):
        """reset the skinCluster
        """

        # get matrix connections
        matrixConnections = self.connections(attributes=['matrix'], sources=True, destinations=True)

        # execute
        for matrixConnection in matrixConnections:

            # get bindPreMatrix attribute
            bpmAttribute = cgp_maya_utils.scene._api.attribute(matrixConnection.destination().fullName().replace('matrix', 'bindPreMatrix'))

            # get matrix values
            matrixValues = matrixConnection.source().node().attribute('worldInverseMatrix').value()

            # update bpm attribute
            if not bpmAttribute.connections(source=True, destinations=False):
                bpmAttribute.setValue(matrixValues)

        # recache bindMatrices
        self.recacheBindMatrices()

    def setBindPreMatrices(self, bindPreMatrices=None):
        """set the bindPreMatrices of the skinCluster

        :param bindPreMatrices: the bindPreMatrices to set on the skinCluster -
                                ``{influence1: matrixAttribute1, influence2: matrixAttribute2 ...}``
        :type bindPreMatrices: dict
        """

        # remove existing bpm connections
        connections = self.connections(attributes=['bindPreMatrix'], sources=True, destinations=False)

        for connection in connections:
            connection.disconnect()

        # build bpm
        if bindPreMatrices:

            # get matrix connections
            matrixConnections = self.connections(attributes=['matrix'], sources=True, destinations=True)

            # execute
            for matrixConnection in matrixConnections:

                # get bpm connections
                influence = matrixConnection.source().node().fullName()
                bpmAttr = matrixConnection.destination().fullName().replace('.matrix', '.bindPreMatrix')

                # build bpm connection
                if bindPreMatrices[influence]:
                    maya.cmds.connectAttr(bindPreMatrices[influence], bpmAttr, force=True)

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
        maya.cmds.skinPercent(self.fullName(), self.shapes()[0], transformValue=(str(influences[0]), 1))
        pttAttribute.connect('{0}.message'.format(influences[0]))

        # apply influences
        for influence in influences[1:]:

            # warning
            if influence.name() not in weights:
                maya.cmds.warning('{0} doesn\'t have stored weights ! skipped !'.format(influence))

            # apply
            else:

                # connect joint to paint attribute
                pttAttribute.connect('{0}.message'.format(influence))

                # set paint attribute and lock joint
                ptwAttribute.setValue(weights[influence.name()])
                influence.attribute('liw').setValue(1)

                # refresh the view
                maya.cmds.refresh()

    def swapInfluences(self, oldFlag, newFlag, reset=True):
        """swap current influences by new influences using the specified flags

        :param oldFlag: flag that will be replaced in the current influences to find the influences to replace with
        :type oldFlag: str

        :param newFlag: flag that will replace the old one to find the influences to add to the skinCluster
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
        """get the unused influences of the skinCluster

        :return: the unused influences of the skinCluster
        :rtype: list[:class:`cgp_maya_utils.scene.Joint`, Shape]
        """

        # get weightedInfluences
        weightedInfluences = maya.cmds.skinCluster(self.fullName(), query=True, weightedInfluence=True) or []

        # return
        return [influence for influence in self.influences() if influence not in weightedInfluences]

    def weights(self):
        """get the weights of the skinCluster - same weights that are accessible through painting

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
