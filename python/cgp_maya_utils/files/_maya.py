"""
maya file object library
"""

# imports python
import os
import re

# imports third-parties
import maya.cmds

# imports rodeo
import cgp_generic_utils.constants
import cgp_generic_utils.files

# imports local
import cgp_maya_utils.decorators


# MAYA FILE OBJECTS #


class GpuCacheFile(cgp_generic_utils.files.File):
    """file object that manipulates a ``.gpucache`` file on the file system
    """

    # ATTRIBUTES #

    _extension = 'gpucache'

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, path, startFrame=None, endFrame=None, content=None, **__):
        """create a gpu cache file

        :param path: path of the gpu cache file to create
        :type path: str

        :param startFrame: startFrame of the gpu cache
        :type startFrame: int

        :param endFrame: endFrame of the gpu cache
        :type endFrame: int

        :param content: group node containing the geometries to export as gpuCache
        :type content: str or :class:`cgp_maya_utils.scene.Node`

        :return: the created file
        :rtype: :class:`cgp_maya_utils.files.GpuCacheFile`
        """

        # errors
        if not content:
            raise RuntimeError("no content specified")

        if not maya.cmds.objExists(content):
            raise RuntimeError("content not existing in the scene : {}".format(content))

        # get start and end frames
        startFrame = startFrame or maya.cmds.playbackOptions(query=True, animationStartTime=True)
        endFrame = endFrame or maya.cmds.playbackOptions(query=True, animationEndTime=True)

        # In case endFrame is inferior startFrame
        if endFrame < startFrame:
            raise maya.cmds.error('endFrame is lower than startFrame : {0} < {1}'.format(endFrame, startFrame))

        # Get the file name from the path and removing the extension
        fileName = path.split(os.sep)[-1].split('.')[0]
        cacheFileName = '{}_cache'.format(fileName)
        directory = path.split('.')[0].replace(fileName, '')

        # Caching the asset
        path = maya.cmds.gpuCache(content,
                                  startTime=startFrame,
                                  endTime=endFrame,
                                  directory=directory,
                                  fileName=cacheFileName)[0]

        gpuCachePath = "{}{}.{}".format(directory, cacheFileName, cls._extension)
        os.rename(path, gpuCachePath)

        # return
        return cls(gpuCachePath)


class MayaFile(cgp_generic_utils.files.File):
    """file object that manipulates any kind of maya file on the file system
    """

    # ATTRIBUTES #

    _dataType = NotImplemented

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, path, content=None, **__):
        """create the file

        :param path: path of the file to create
        :type path: str

        :param content: content to set into the created file
        :type content: any

        :return: the created file
        :rtype: :class:`cgp_maya_utils.file.MayaFile`
        """

        # return
        raise NotImplementedError('{0}File.create is not implemented yet'.format(cls._extension.title()))

    # COMMANDS #

    def import_(self, asReference=False, namespace=None):
        """import the maya file in the scene

        :param asReference: ``True`` : maya file is referenced - ``False`` maya file is imported without reference
        :type asReference: bool

        :param namespace: namespace of the file to import
        :type namespace: str
        """

        # reference
        if asReference:
            fileArgs = {'namespace': namespace} if namespace else {'namespace': ':', 'options': 'v=0;'}
            maya.cmds.file(self.path(), reference=asReference, prompt=False, **fileArgs)

        # classic import
        else:
            fileArgs = {'namespace': namespace} if namespace else {'options': 'v=0;'}
            maya.cmds.file(self.path(), i=True, **fileArgs)

    # COMMANDS #

    def mayaVersion(self):
        """get the version of the Maya that generated the file

        :return: the maya version
        :rtype: int
        """

        # should be re implemented in each sub types of maya files
        raise NotImplementedError

    def open_(self, force=False):
        """open the maya file

        :param force: ``True`` : opening will be forced - ``False`` : prompt will show before opening
        :type force: bool
        """

        # execute
        maya.cmds.file(self.path(), open=True, force=force)


class AbcFile(MayaFile):
    """file object that manipulates an ``.abc`` file on the file system
    """

    # ATTRIBUTES #

    _extension = 'abc'

    # OBJECT COMMANDS #

    def import_(self, parent=None):
        """Import the Alembic file

        :param parent: node under which the content of the alembic will be parented to
        :type parent: str or :class: `cgp_maya_utils.scene.Transform`

        :return: the nodes imported from the alembic file
        :rtype: list[str]
        """

        # catch the current content of the scene
        sceneBefore = maya.cmds.ls()

        # import alembic file in the scene
        if parent:
            maya.cmds.AbcImport(self.path(), mode='import', reparent=parent)
        else:
            maya.cmds.AbcImport(self.path(), mode='import')

        # catch content of the scene after the import
        sceneNow = maya.cmds.ls()

        # return
        return list(set(sceneNow) - set(sceneBefore))


class MaFile(MayaFile):
    """file object that manipulates a ``.ma`` file on the file system
    """

    # ATTRIBUTES #

    _extension = 'ma'
    _dataType = 'mayaAscii'

    # COMMANDS #

    def mayaVersion(self):
        """get the version of the Maya that generated the file

        :return: the maya version
        :rtype: int
        """

        # init
        regex = r'fileInfo \"product\" \"Maya ([0-9]{4})\";'

        # read file line by line until we find the 'fileInfo "version" "xxxx";' line
        with open(self.path(), 'r') as parsedFile:
            for line in parsedFile:
                match = re.match(regex, line)
                if match:
                    return int(match.group(1))

        # raise error if no version found
        raise RuntimeError("Unable to find maya version in file: {}".format(self.path()))


class MbFile(MayaFile):
    """file object that manipulates a ``.mb`` file on the file system
    """

    # ATTRIBUTES #

    _extension = 'mb'
    _dataType = 'mayaBinary'

    # COMMANDS #

    def mayaVersion(self):
        """get the version of the Maya that generated the file

        :return: the maya version
        :rtype: int
        """

        # init
        regex = r'.*FINFproductMaya ([0-9]{4}).*'

        # get strings from mb file and remove carriage returns
        mbStrings = os.popen('strings "{}"'.format(self.path())).read().replace('\n', '')

        # find the maya version in these strings
        match = re.match(regex, mbStrings)
        if match:
            return int(match.group(1))

        # raise error if no version found
        raise RuntimeError("Unable to find maya version in file: {}".format(self.path()))


class ObjFile(cgp_generic_utils.files.File):
    """file object that manipulates a ``.obj`` file on the file system
    """

    # ATTRIBUTES #

    _extension = 'obj'

    # OBJECT COMMANDS #

    @classmethod
    @cgp_maya_utils.decorators.KeepSelection()
    def create(cls, path, content=None, **__):
        """create an obj file

        :param path: path of the obj file to create
        :type path: str

        :param content: nodes from the scene to add to the content of the file - use selection if nothing is specified
        :type content: list[str, :class:`cgp_maya_utils.scene.Node`]

        :return: the created obj file
        :rtype: :class:`cgp_maya_utils.files.ObjFile`
        """

        # init
        content = [str(node) for node in content]

        # errors
        if not cgp_generic_utils.files.getExtension(path) == cls._extension:
            raise ValueError('{0} is not a ObjFile path'.format(path))

        # get content
        if content:
            maya.cmds.select(content)

        elif not maya.cmds.ls(selection=True):
            raise RuntimeError('no content to write in {0}'.format(path))

        # execute
        maya.cmds.file(path,
                       force=True,
                       options='groups=0;ptgroups=0;materials=0;smoothing=0;normals=0',
                       exportSelected=True,
                       type='OBJexport')

        # return
        return cls(path)

    # COMMANDS #

    def import_(self, name):
        """imports the obj file

        :param name: name of the imported object
        :type name: str

        :return: the imported obj
        :rtype: str
        """

        # load shape form directory
        objPrefix = 'importer_obj_{0}'.format(self.baseName(withExtension=False))
        objTransform = '{0}_Mesh'.format(objPrefix)

        # load geometry
        maya.cmds.file(self.path(), i=True, type='OBJ', renameAll=True, renamingPrefix=objPrefix)

        # rename transform
        return maya.cmds.rename(objTransform, name)
