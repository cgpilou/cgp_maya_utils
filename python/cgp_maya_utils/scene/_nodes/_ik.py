"""
ik object library
"""

# imports third-parties
import maya.cmds

# imports local
import cgp_maya_utils.constants
from . import _transform


# IK OBJECTS #


class IkEffector(_transform.Transform):
    """node object that manipulates an ``ikEffector`` node
    """

    # ATTRIBUTES #

    _nodeType = 'ikEffector'


class IkHandle(_transform.Transform):
    """node object that manipulates an ``ikHandle`` node
    """

    # ATTRIBUTES #

    _nodeType = 'ikHandle'

    # OBJECT COMMANDS #

    @classmethod
    def create(cls, startJoint, endJoint, solverType=None, connections=None,
               attributeValues=None, name=None, **__):
        """create an ik handle

        :param startJoint: start joint of the ik handle
        :type startJoint: str or :class:`cgp_maya_utils.scene.Joint`

        :param endJoint: end joint of the ik handle
        :type endJoint: str or :class:`cgp_maya_utils.scene.Joint`

        :param solverType: type of solver of the ik handle - default is ``cgp_maya_utils.constants.Solver.IK_RP_SOLVER``
        :type solverType: str

        :param connections: connections to set on the ikHandle
        :type connections: list[tuple[str]]

        :param attributeValues: attribute values to set on the ikHandle node
        :type attributeValues: dict

        :param name: name of the node
        :type name: str

        :return: the created ik handle
        :rtype: :class:`cgp_maya_utils.scene.IkHandle`
        """

        # init
        name = name or cls._nodeType
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
        """data necessary to store the ik handle node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : ikHandle transforms are in worldSpace - ``False`` : ikHandle transforms in local
        :type worldSpace: bool

        :return: the data of the ik handle
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
        """the effector of the ik handle

        :return: the effector of the ik handle
        :rtype: :class:`cgp_maya_utils.scene.IkEffector`
        """

        # get the ikEffector
        ikEffector = maya.cmds.ikHandle(self.name(), query=True, endEffector=True)

        # return
        return IkEffector(ikEffector)

    def endJoint(self):
        """the end joint of the ik handle

        :return: the end joint of the ik handle
        :rtype: :class:`cgp_maya_utils.scene.Joint`
        """

        # init
        translateX = self.effector().attribute(cgp_maya_utils.constants.Transform.TRANSLATE_X)
        effectorConnections = translateX.connections(source=True, destinations=False)

        # return
        return effectorConnections[0].source().node()

    def setSolver(self, solverType):
        """set the solver of the ik handle

        :param solverType: type of solver to set
        :type solverType: str
        """

        # execute
        maya.cmds.ikHandle(self.name(), edit=True, solver=solverType)

    def startJoint(self):
        """the start joint of the ik handle

        :return: the start joint
        :rtype: :class:`cgp_maya_utils.scene.Joint`
        """

        # get the startJoint
        startJoint = maya.cmds.ikHandle(self.name(), query=True, startJoint=True)

        # return
        return cgp_maya_utils.scene._nodes._transform.Joint(startJoint)
