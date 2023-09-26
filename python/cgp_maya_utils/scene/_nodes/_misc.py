"""
misc object library
"""

# imports python
import os

# imports third-parties
import maya.cmds
import maya.api.OpenMaya

# imports local
import cgp_maya_utils.files
import cgp_maya_utils.decorators
import cgp_maya_utils.constants
from . import _generic


# MISC OBJECTS #


class ComposeMatrix(_generic.Node):
    """node object that manipulates a ``composeMatrix`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.COMPOSE_MATRIX


class DecomposeMatrix(_generic.Node):
    """node object that manipulates a ``decomposeMatrix`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.DECOMPOSE_MATRIX


class DisplayLayer(_generic.Node):
    """node object that manipulates a ``displayLayer`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.DISPLAY_LAYER


class GpuCache(_generic.DagNode):
    """node object that manipulates a ``gpuCache`` node
    """

    # ATTRIBUTES #

    _TYPE = cgp_maya_utils.constants.NodeType.GPUCACHE

    # COMMANDS #

    @classmethod
    def create(cls, name, connections=None, attributeValues=None, file_=None, **__):
        """create a gpuCache

        :param name: name of the gpuCache
        :type name: str

        :param connections: connections to set on the gpuCache
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the gpuCache
        :type attributeValues: dict

        :param file_: path of the file that is associated to the gpuCache
        :type file_: str

        :return: the created gpuCache
        :rtype: :class:`cgp_maya_utils.scene.GpuCache`
        """

        # create the node
        name = maya.cmds.createNode(cls._TYPE, name=name)

        # initialize GpuCache object
        node = cls(name)

        # if an associated file is provided, assigned it to the node
        if file_:
            node.setFile(file_)

        # return
        return node

    def data(self):
        """get the data necessary to store the gpuCache node on disk and/or recreate it from scratch

        :return: the data of the gpuCache
        :rtype: dict
        """

        # get data
        data = super(GpuCache, self).data()

        # update data
        if self.attribute('cacheFileName').value():
            data['file_'] = self.attribute('cacheFileName').value()

        # return
        return data

    def file_(self):
        """get the file associated to the gpuCache

        :return: the file of the gpuCache
        :rtype: :class:`cgp_maya_utils.files.GpuCacheFile`
        """

        # return
        return (cgp_maya_utils.files.GpuCacheFile(self.attribute('cacheFileName').value())
                if self.attribute('cacheFileName').value()
                else None)

    def generate(self, directory, startFrame=None, endFrame=None, asset=None):
        """generate The gpuCache

        :param directory: directory the gpuCache file will be saved in
        :type directory: str

        :param startFrame: startFrame of the caching
        :type startFrame: int

        :param endFrame: endFrame of the caching
        :type endFrame: int

        :param asset: nodes from the scene to add to the content of the file
        :type asset: str or :class:`cgp_maya_utils.scene.Node`

        :return: the generated gpuCache file
        :rtype: :class:`cgp_maya_utils.file.GpuCacheFile`
        """

        # TODO : rewrite command to have better file name management

        # get path
        path = self.file_().path() if self.file_() else '{}{}{}.gpucache'.format(directory, os.sep, asset)

        # load plugin
        if not maya.cmds.pluginInfo('gpuCache.so', query=True, loaded=True):
            maya.cmds.loadPlugin('gpuCache.so')

        # create the gpuCache file
        gpuCacheFile = cgp_maya_utils.files.GpuCacheFile.create(path,
                                                                startFrame=startFrame,
                                                                ndFrame=endFrame,
                                                                content=asset)

        # set file
        self.setFile(gpuCacheFile.path())

        # return
        return gpuCacheFile

    def setFile(self, file_):
        """set the file of the gpuCache

        :param file_: file to set to the gpuCache
        :type file_: str or :class:`cgp_maya_utils.files.GpuCacheFile`
        """

        # update
        gpuCacheFile = (file_
                        if isinstance(file_, cgp_maya_utils.files.GpuCacheFile)
                        else cgp_maya_utils.files.GpuCacheFile(file_))

        # set cacheFileName attribute
        self.attribute('cacheFileName').setValue(gpuCacheFile.path())

    def setParent(self, parent):
        """set the parent of the gpuCache

        :param parent: DagNode used to parent the gpuCache to
        :type parent: str
        """

        # TODO: this need to be removed once inheritance is back to Shape object

        # execute
        maya.cmds.parent(self.fullName(), parent)

    def delete(self):
        """delete the gpuCache and its parent
        """

        # TODO : this should be changed for next line once inheritance is back to Shape object
        # self.parent().delete()

        # execute
        maya.cmds.delete(maya.cmds.listRelatives(self.fullName(), parent=True, fullPath=True)[0])
