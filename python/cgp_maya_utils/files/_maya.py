"""
maya file object library
"""

# imports third-parties
import maya.cmds
import cgp_generic_utils.files
import cgp_generic_utils.constants

# imports local
import cgp_maya_utils.decorators


# MAYA FILE OBJECTS #


class MayaFile(cgp_generic_utils.files.File):
    """file object that manipulates any kind of maya file on the file system
    """

    # ATTRIBUTES #

    _dataType = NotImplemented

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, path, content=None, **__):
        """create a maya file

        :param path: path of the maya file
        :type path: str

        :param content: content of the maya file
        :type content: any

        :return: the created maya file
        :rtype: :class:`cgp_maya_utils.files.MayaFile`
        """

        # return
        raise NotImplementedError('{0}File.create is not implemented yet'.format(cls._extension.title()))

    # COMMANDS #

    def import_(self, asReference=False, namespace=None):
        """import the maya file in the scene

        :param asReference: ``True`` : maya file is referenced - ``False`` maya file is imported without reference
        :type asReference: bool

        :param namespace: namespace of the file to import
        :type namespace: str or :class:`cgp_maya_utils.scene.Namespace`
        """

        # init
        namespace = str(namespace)

        # reference
        if asReference:
            fileArgs = {'namespace': namespace} if namespace else {'namespace': ':', 'options': 'v=0;'}
            maya.cmds.file(self.path(), reference=asReference, prompt=False, **fileArgs)

        # classic import
        else:
            fileArgs = {'namespace': namespace} if namespace else {'options': 'v=0;'}
            maya.cmds.file(self.path(), i=True, type=self._dataType, **fileArgs)

    def open(self, force=False):
        """open the maya file

        :param force: ``True`` : opening will be forced - ``False`` : prompt will show before opening
        :type force: bool
        """

        # execute
        maya.cmds.file(self.path(), open=True, force=force)


class MaFile(MayaFile):
    """file object that manipulate a ``.ma`` file on the file system
    """

    # ATTRIBUTES #

    _extension = 'ma'
    _dataType = 'mayaAscii'


class MbFile(MayaFile):
    """file object that manipulates a ``.mb`` file on the file system
    """

    # ATTRIBUTES #

    _extension = 'mb'
    _dataType = 'mayaBinary'


class ObjFile(cgp_generic_utils.files.File):
    """file object that manipulates a ``.obj`` file on the file system
    """

    # ATTRIBUTES #

    _extension = 'obj'

    # OBJECT COMMANDS #

    @classmethod
    @cgp_maya_utils.decorators.KeepCurrentSelection()
    def create(cls, path, content=None, **__):
        """create an obj file

        :param path: path of the obj file
        :type path: str

        :param content: nodes from the scene to add to the content of the file - use selection if nothing is specified
        :type content: list[str, :class:`cgp_maya_utils.scene.Node`]

        :return: the created obj file
        :rtype: :class:`cgp_maya_utils.files.ObjFile`
        """

        # init
        content = [str(node) for node in content]

        # errors
        if not cgp_generic_utils.files.Path(path).extension() == cls._extension:
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

        :return: the imported object
        :rtype: str
        """

        # load shape form directory
        loadPrefix = 'importer_obj_{0}'.format(self.baseName())
        loadGeo = '{0}_Mesh'.format(loadPrefix)

        # load geometry
        maya.cmds.file(self.path(), i=True, type='OBJ', renameAll=True, renamingPrefix=loadPrefix)

        # return
        return maya.cmds.rename(loadGeo, name)
