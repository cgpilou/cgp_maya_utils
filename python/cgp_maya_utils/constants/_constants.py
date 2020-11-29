"""
constants used to manipulate maya data
"""

# imports python
import os

# imports third-parties
import cgp_generic_utils.constants


class AttributeType(object):
    BOOLEAN = 'bool'
    BYTE = 'byte'
    CHAR = 'char'
    COMPOUND = 'compound'
    DOUBLE = 'double'
    DOUBLE2 = 'double2'
    DOUBLE3 = 'double3'
    DOUBLE_ANGLE = 'doubleAngle'
    DOUBLE_ARRAY = 'doubleArray'
    DOUBLE_LINEAR = 'doubleLinear'
    ENUM = 'enum'
    FLOAT = 'float'
    FLOAT2 = 'float2'
    FLOAT3 = 'float3'
    FLOAT_ARRAY = 'floatArray'
    FLOAT_MATRIX = 'fltMatrix'
    INT_32_ARRAY = 'Int32Array'
    LATTICE = 'lattice'
    LONG = 'long'
    LONG2 = 'long2'
    LONG3 = 'long3'
    MATRIX = 'matrix'
    MESH = 'mesh'
    MESSAGE = 'message'
    NURBSCURVE = 'nurbsCurve'
    NURBSSURFACE = 'nurbsSurface'
    POINT_ARRAY = 'pointArray'
    REFLECTANCE_RGB = 'reflectanceRGB'
    SHORT = 'short'
    SHORT2 = 'short2'
    SHORT3 = 'short3'
    SPECTRUM = 'spectrum'
    SPECTRUM_RGB = 'spectrumRGB'
    STRING = 'string'
    STRING_ARRAY = 'stringArray'
    TDATACOMPOUND = 'TdataCompound'
    TIME = 'time'
    VECTOR_ARRAY = 'vectorArray'
    ALL = [BOOLEAN, BYTE, CHAR, COMPOUND, DOUBLE, DOUBLE2, DOUBLE3, DOUBLE_ANGLE, DOUBLE_ARRAY, DOUBLE_LINEAR, ENUM,
           FLOAT, FLOAT2, FLOAT3, FLOAT_ARRAY, FLOAT_MATRIX, INT_32_ARRAY, LATTICE, LONG, LONG2, LONG3, MATRIX, MESH,
           MESSAGE, NURBSCURVE, NURBSSURFACE, POINT_ARRAY, REFLECTANCE_RGB, SHORT, SHORT2, SHORT3, SPECTRUM,
           SPECTRUM_RGB, STRING, STRING_ARRAY, TDATACOMPOUND, TIME, VECTOR_ARRAY]


class ComponentType(object):

    EDGE = 'e'
    FACE = 'f'
    VERTEX = 'vtx'

    CURVE_POINT = 'cv'
    EDIT_POINT = 'ep'

    ISOPARM_U = 'u'
    ISOPARM_V = 'v'
    SURFACE_PATCH = 'sf'
    SURFACE_POINT = 'cv'

    MESH = [EDGE, FACE, VERTEX]
    NURBS_CURVE = [CURVE_POINT, EDIT_POINT]
    NURBS_SURFACE = [ISOPARM_U, ISOPARM_V, SURFACE_PATCH, SURFACE_POINT]
    ALL = MESH + NURBS_CURVE + NURBS_SURFACE


class Environment(cgp_generic_utils.constants.Environment):

    # maya utils root
    MAYA_UTILS_ROOT = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-3])

    # shape libraries
    NURBS_CURVE_LIBRARY = os.path.join(MAYA_UTILS_ROOT, 'shapes', 'nurbsCurve')
    NURBS_SURFACE_LIBRARY = os.path.join(MAYA_UTILS_ROOT, 'shapes', 'nurbsSurface')
    MESH_LIBRARY = os.path.join(MAYA_UTILS_ROOT, 'shapes', 'mesh')


class GeometryData(object):

    LINEAR = 1
    DEGREE_2 = 2
    CUBIC = 3
    DEGREE_5 = 5
    DEGREE_7 = 7
    DEGREES = [LINEAR, DEGREE_2, CUBIC, DEGREE_5, DEGREE_7]

    OPEN = 'Open'
    CLOSED = 'Closed'
    PERIODIC = 'Periodic'
    FORMS = [OPEN, CLOSED, PERIODIC]


class InfluenceAssociation(object):
    CLOSEST_BONE = 'closestBone'
    CLOSEST_JOINT = 'closestJoint'
    LABEL = 'label'
    NAME = 'name'
    ONE_TO_ONE = 'oneToOne'
    ALL = [CLOSEST_BONE, CLOSEST_JOINT, LABEL, NAME, ONE_TO_ONE]


class Solver(object):
    IK_SC_SOLVER = 'ikSCsolver'
    IK_RP_SOLVER = 'ikRPsolver'
    IK_SPLINE_SOLVER = 'splineSolver'
    IK_SOLVERS = [IK_SC_SOLVER, IK_RP_SOLVER, IK_SPLINE_SOLVER]


class NodeType(object):
    ANIM_CURVE_TA = 'animCurveTA'
    ANIM_CURVE_TL = 'animCurveTL'
    ANIM_CURVE_TU = 'animCurveTU'
    ANIM_CURVES = [ANIM_CURVE_TA, ANIM_CURVE_TL, ANIM_CURVE_TU]
    AIM_CONSTRAINT = 'aimConstraint'
    ORIENT_CONSTRAINT = 'orientConstraint'
    PARENT_CONSTRAINT = 'parentConstraint'
    POINT_CONSTRAINT = 'pointConstraint'
    SCALE_CONSTRAINT = 'scaleConstraint'
    CONSTRAINTS = [AIM_CONSTRAINT, ORIENT_CONSTRAINT, PARENT_CONSTRAINT, POINT_CONSTRAINT, SCALE_CONSTRAINT]
    CLUSTER = 'cluster'
    SKINCLUSTER = 'skinCluster'
    TWEAK = 'tweak'
    GEOMETRY_FILTERS = [CLUSTER, SKINCLUSTER, TWEAK]
    NURBS_CURVE = 'nurbsCurve'
    NURBS_SURFACE = 'nurbsSurface'
    MESH = 'mesh'
    SHAPES = [NURBS_CURVE, NURBS_SURFACE, MESH]
    TRANSFORM = 'transform'
    JOINT = 'joint'
    TRANSFORMS = [TRANSFORM, JOINT]
    REFERENCE = 'reference'


class RotateOrder(object):
    XYZ = 'xyz'
    YZX = 'yzx'
    ZXY = 'zxy'
    XZY = 'xzy'
    YXZ = 'yxz'
    ZYX = 'zyx'
    ALL = [XYZ, YZX, ZXY, XZY, YXZ, ZYX]


class SurfaceAssociation(object):
    CLOSEST_COMPONENT = 'closestComponent'
    CLOSEST_POINT = 'closestPoint'
    RAYCAST = 'rayCast'
    ALL = [CLOSEST_COMPONENT, CLOSEST_POINT, RAYCAST]


class TangentType(object):
    AUTO = 'auto'
    CLAMPED = 'clamped'
    FAST = 'fast'
    FLAT = 'flat'
    LINEAR = 'linear'
    PLATEAU = 'plateau'
    SLOW = 'slow'
    SPLINE = 'spline'
    STEP = 'step'
    STEPNEXT = 'stepnext'
    ALL = [AUTO, CLAMPED, FAST, FLAT, LINEAR, PLATEAU, SLOW, SPLINE, STEP, STEPNEXT]


class Transform(object):
    TRANSLATE = 'translate'
    ROTATE = 'rotate'
    SCALE = 'scale'
    SHEAR = 'shear'
    TRANSLATE_X = 'translateX'
    TRANSLATE_Y = 'translateY'
    TRANSLATE_Z = 'translateZ'
    ROTATE_X = 'rotateX'
    ROTATE_Y = 'rotateY'
    ROTATE_Z = 'rotateZ'
    SCALE_X = 'scaleX'
    SCALE_Y = 'scaleY'
    SCALE_Z = 'scaleZ'
    SHEAR_XY = 'shearXY'
    SHEAR_XZ = 'shearXZ'
    SHEAR_YZ = 'shearYZ'
    TRANSLATES = [TRANSLATE_X, TRANSLATE_Y, TRANSLATE_Z]
    ROTATES = [ROTATE_X, ROTATE_Y, ROTATE_Z]
    SCALES = [SCALE_X, SCALE_Y, SCALE_Z]
    SHEARS = [SHEAR_XY, SHEAR_XZ, SHEAR_YZ]
    GENERAL = [TRANSLATE, ROTATE, SCALE, SHEAR]
    ALL = GENERAL + TRANSLATES + ROTATES + SCALES + SHEARS


class WorldUpType(object):
    SCENE = 'scene'
    OBJECT = 'object'
    OBJECT_ROTATION = 'objectrotation'
    VECTOR = 'vector'
    NONE = 'none'
    ALL = [SCENE, OBJECT, OBJECT_ROTATION, VECTOR, NONE]
