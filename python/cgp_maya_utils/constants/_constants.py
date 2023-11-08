"""
constants used to manipulate maya data
"""

# imports python
import os

# import rodeo
import cgp_generic_utils.constants


class AttributeType(object):
    ALIAS = 'attributeAlias'
    ATTRIBUTE = 'attribute'
    BOOLEAN = 'bool'
    BYTE = 'byte'
    CHAR = 'char'
    COMPOUND = 'compound'
    DATA_REFERENCE_EDITS = 'dataReferenceEdits'
    DOUBLE = 'double'
    DOUBLE2 = 'double2'
    DOUBLE3 = 'double3'
    DOUBLE4 = 'double4'
    DOUBLE_ANGLE = 'doubleAngle'
    DOUBLE_ARRAY = 'doubleArray'
    DOUBLE_LINEAR = 'doubleLinear'
    ENUM = 'enum'
    FLOAT = 'float'
    FLOAT2 = 'float2'
    FLOAT3 = 'float3'
    FLOAT4 = 'float4'
    FLOAT_ARRAY = 'floatArray'
    FLOAT_MATRIX = 'fltMatrix'
    FUNCTION = 'function'
    INT_32_ARRAY = 'Int32Array'
    LATTICE = 'lattice'
    LONG = 'long'
    LONG2 = 'long2'
    LONG3 = 'long3'
    LONG4 = 'long4'
    MATRIX = 'matrix'
    MESH = 'mesh'
    MESSAGE = 'message'
    NUMERIC = 'numeric'
    NURBSCURVE = 'nurbsCurve'
    NURBSCURVE_HEADER = 'nurbsCurveHeader'
    NURBSSURFACE = 'nurbsSurface'
    POINT_ARRAY = 'pointArray'
    POLY_FACES = 'polyFaces'
    REFLECTANCE = 'reflectance'
    REFLECTANCE_RGB = 'reflectanceRGB'
    SHORT = 'short'
    SHORT2 = 'short2'
    SHORT3 = 'short3'
    SHORT4 = 'short4'
    SPECTRUM = 'spectrum'
    SPECTRUM_RGB = 'spectrumRGB'
    STRING = 'string'
    STRING_ARRAY = 'stringArray'
    TDATACOMPOUND = 'TdataCompound'
    TIME = 'time'
    VECTOR_ARRAY = 'vectorArray'
    VOID = 'void'
    ARRAYS = [DOUBLE_ARRAY, FLOAT_ARRAY, INT_32_ARRAY, FLOAT_ARRAY, POINT_ARRAY, STRING_ARRAY, VECTOR_ARRAY]
    COMPOUNDS = [COMPOUND, DOUBLE2, DOUBLE3, DOUBLE4, FLOAT2, FLOAT3, FLOAT4, LONG2, LONG3, LONG4, REFLECTANCE,
                 SHORT2, SHORT3, SHORT4, SPECTRUM, TDATACOMPOUND]
    DISCRETE = [BOOLEAN, BYTE, ENUM, LONG, LONG2, LONG3, LONG4, SHORT, SHORT2, SHORT3, SHORT4]
    MATRICES = [MATRIX, FLOAT_MATRIX]
    NON_SETTABLES = [DATA_REFERENCE_EDITS, FUNCTION, MESH, MESSAGE, NURBSCURVE, NURBSCURVE_HEADER, NURBSSURFACE,
                     TDATACOMPOUND, TIME, VOID]
    NUMERICS = [NUMERIC, BYTE, DOUBLE, DOUBLE_ANGLE, DOUBLE_LINEAR, FLOAT, LONG, SHORT, TIME]
    DISPLAYABLES = NUMERICS + COMPOUNDS + ARRAYS + MATRICES + [BOOLEAN, ENUM, MESSAGE, STRING]
    ALL = [ALIAS, BOOLEAN, BYTE, CHAR, COMPOUND, DATA_REFERENCE_EDITS, DOUBLE, DOUBLE2, DOUBLE3, DOUBLE4, DOUBLE_ANGLE,
           DOUBLE_ARRAY, DOUBLE_LINEAR, ENUM, FLOAT, FLOAT2, FLOAT3, FLOAT4, FLOAT_ARRAY, FLOAT_MATRIX, FUNCTION,
           INT_32_ARRAY, LATTICE, LONG, LONG2, LONG3, LONG4, MATRIX, MESH, MESSAGE, NUMERIC, NURBSCURVE,
           NURBSCURVE_HEADER, NURBSSURFACE, POINT_ARRAY, POLY_FACES, REFLECTANCE_RGB, SHORT, SHORT2, SHORT3, SHORT4,
           SPECTRUM, SPECTRUM_RGB, STRING, STRING_ARRAY, TDATACOMPOUND, TIME, VECTOR_ARRAY, VOID]


class ComponentType(object):

    COMPONENT = 'component'
    MESH_COMPONENT = 'meshComponent'
    TRANSFORM_COMPONENT = 'transformComponent'

    EDGE = 'e'
    FACE = 'f'
    UV_MAP = 'map'
    VERTEX = 'vtx'

    CURVE_POINT = 'cv'
    EDIT_POINT = 'ep'

    ISOPARM_U = 'u'
    ISOPARM_V = 'v'
    SURFACE_PATCH = 'sf'
    SURFACE_POINT = 'cv'

    MESH = [EDGE, FACE, UV_MAP, VERTEX]
    NURBS_CURVE = [CURVE_POINT, EDIT_POINT]
    NURBS_SURFACE = [ISOPARM_U, ISOPARM_V, SURFACE_PATCH, SURFACE_POINT]
    ALL = MESH + NURBS_CURVE + NURBS_SURFACE


class Environment(cgp_generic_utils.constants.Environment):

    # shape libraries
    SHAPE_LIBRARY = os.path.join(os.sep.join(os.path.dirname(__file__).split(os.sep)[:-3]), 'shapes')
    NURBS_CURVE_LIBRARY = os.path.join(SHAPE_LIBRARY, 'nurbsCurve')
    NURBS_SURFACE_LIBRARY = os.path.join(SHAPE_LIBRARY, 'nurbsSurface')
    MESH_LIBRARY = os.path.join(SHAPE_LIBRARY, 'mesh')


class Font(object):
    FREE_SERIF = 'FreeSerif'
    LIBERATION_MONO = 'Liberation Mono'
    LIBERATION_SANS = 'Liberation Sans'
    ALL = [FREE_SERIF, LIBERATION_MONO, LIBERATION_SANS]


class FontStyle(object):
    BOLD = 'Bold'
    BOLD_ITALIC = 'Bold Italic'
    ITALIC = 'Italic'
    REGULAR = 'Regular'
    ALL = [BOLD, BOLD_ITALIC, ITALIC, REGULAR]


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


class Interface(object):
    MAYA_WINDOW = 'MayaWindow'


class MiscType(object):
    ANIM_KEY = 'animKey'
    ANIM_LAYER = 'animLayer'
    CONNECTION = 'connection'
    NAMESPACE = 'namespace'
    PLUGIN = 'plugin'
    SCENE = 'scene'


class NodeType(object):
    ANIM_BLEND = 'animBlendNodeBase'
    ANIM_CURVE = 'animCurve'
    ANIM_CURVE_TA = 'animCurveTA'
    ANIM_CURVE_TL = 'animCurveTL'
    ANIM_CURVE_TU = 'animCurveTU'
    ANIM_LAYER = 'animLayer'
    AIM_CONSTRAINT = 'aimConstraint'
    BASE_NODE = 'baseNode'
    BLEND_DEFORMER = 'blendDeformer'
    BLEND_SHAPE = 'blendShape'
    CAMERA = 'camera'
    CLUSTER = 'cluster'
    CONSTRAINT = 'constraint'
    COMPOSE_MATRIX = 'composeMatrix'
    DAG_NODE = 'dagNode'
    DECOMPOSE_MATRIX = 'decomposeMatrix'
    DISPLAY_LAYER = 'displayLayer'
    EXPRESSION = 'expression'
    GEOMETRY_FILTER = 'geometryFilter'
    GEOMETRY_SHAPE = 'geometryShape'
    GPUCACHE = 'gpuCache'
    IK_EFFECTOR = 'ikEffector'
    IK_HANDLE = 'ikHandle'
    JOINT = 'joint'
    LAMBERT = 'lambert'
    MESH = 'mesh'
    NURBS_CURVE = 'nurbsCurve'
    NURBS_SURFACE = 'nurbsSurface'
    ORIENT_CONSTRAINT = 'orientConstraint'
    PAIR_BLEND = 'pairBlend'
    PARENT_CONSTRAINT = 'parentConstraint'
    POINT_CONSTRAINT = 'pointConstraint'
    SCALE_CONSTRAINT = 'scaleConstraint'
    FOLLICLE = 'follicle'
    FKN_SRT_CONSTRAINT = 'fkn_SRT_Constraint'
    FKN_SPACE_SWITCH = 'fkn_SpaceSwitchCns'
    REFERENCE = 'reference'
    RDO_MODEL_NODE = 'rdoModelNode'
    SHADING_DEPEND_NODE = 'shadingDependNode'
    SHADING_ENGINE = 'shadingEngine'
    SHAPE = 'shape'
    SKINCLUSTER = 'skinCluster'
    SOFT_MOD = 'softMod'
    SOFT_MOD_HANDLE = 'softModHandle'
    TRANSFORM = 'transform'
    TWEAK = 'tweak'
    OBJECT_SET = 'objectSet'
    API_ERRORED_TYPES = [SOFT_MOD]
    ANIM_CURVES = [ANIM_CURVE_TA, ANIM_CURVE_TL, ANIM_CURVE_TU]
    CONSTRAINTS = [AIM_CONSTRAINT, ORIENT_CONSTRAINT, PARENT_CONSTRAINT, POINT_CONSTRAINT, SCALE_CONSTRAINT,
                   FKN_SRT_CONSTRAINT, FKN_SPACE_SWITCH]
    GEOMETRY_FILTERS = [CLUSTER, SKINCLUSTER, TWEAK, BLEND_DEFORMER, SOFT_MOD, GEOMETRY_FILTER]
    SHAPES = [NURBS_CURVE, NURBS_SURFACE, MESH]
    TRANSFORMS = [TRANSFORM, JOINT]


class NodeState(object):
    BLOCKING = 'Blocking'
    HAS_NO_EFFECT = 'HasNoEffect'
    NORMAL = 'Normal'
    WAITING_BLOCKING = 'Waiting-Blocking'
    WAITING_HAS_NO_EFFECT = 'Waiting-HasNoEffect'
    WAITING_NORMAL = 'Waiting-Normal'
    ALL = [BLOCKING, HAS_NO_EFFECT, NORMAL, WAITING_BLOCKING, WAITING_HAS_NO_EFFECT, WAITING_NORMAL]


class OptionVarType(object):
    ARRAY = 'array'
    FLOAT = 'float'
    FLOAT_ARRAY = 'floatArray'
    GENERIC = 'generic'
    INT = 'int'
    INT_ARRAY = 'intArray'
    STRING = 'str'
    STRING_ARRAY = 'strArray'


class Plugin(object):
    TYPE = 'Type'
    ALL = [TYPE]


class RotateOrder(object):

    # do not shuffle this order. this is the order it is stored by maya
    XYZ = 'xyz'
    YZX = 'yzx'
    ZXY = 'zxy'
    XZY = 'xzy'
    YXZ = 'yxz'
    ZYX = 'zyx'
    ALL = [XYZ, YZX, ZXY, XZY, YXZ, ZYX]


class Scene(object):
    SUBSTEP = 0.01


class Solver(object):
    IK_SC_SOLVER = 'ikSCsolver'
    IK_RP_SOLVER = 'ikRPsolver'
    IK_SPLINE_SOLVER = 'splineSolver'
    IK_SOLVERS = [IK_SC_SOLVER, IK_RP_SOLVER, IK_SPLINE_SOLVER]


class SurfaceAssociation(object):
    CLOSEST_COMPONENT = 'closestComponent'
    CLOSEST_POINT = 'closestPoint'
    RAYCAST = 'rayCast'
    ALL = [CLOSEST_COMPONENT, CLOSEST_POINT, RAYCAST]


class TangentType(object):
    AUTO = 'auto'
    CLAMPED = 'clamped'
    FAST = 'fast'
    FIXED = 'fixed'
    FLAT = 'flat'
    LINEAR = 'linear'
    PLATEAU = 'plateau'
    SLOW = 'slow'
    SPLINE = 'spline'
    STEP = 'step'
    STEPNEXT = 'stepnext'
    ALL = [AUTO, CLAMPED, FAST, FIXED, FLAT, LINEAR, PLATEAU, SLOW, SPLINE, STEP, STEPNEXT]
    STEPS = [STEP, STEPNEXT]


class TextAlignment(object):
    CENTER = 'Centre'
    LEFT = 'Left'
    RIGHT = 'Right'
    ALL = [CENTER, LEFT, RIGHT]


class ToolContext(object):

    ARTISAN_SELECT = 'artSelectContext'
    LASSO_SELECT = 'lassoSelectContext'
    SUPER_MOVE = 'moveSuperContext'
    SUPER_ROTATE = 'RotateSuperContext'
    SUPER_SCALE = 'scaleSuperContext'
    SUPER_SELECT = 'selectSuperContext'

    ALL = [ARTISAN_SELECT, LASSO_SELECT, SUPER_MOVE, SUPER_ROTATE, SUPER_SCALE, SUPER_SELECT]
    SUPER = [ARTISAN_SELECT, LASSO_SELECT, SUPER_MOVE, SUPER_ROTATE, SUPER_SCALE, SUPER_SELECT]


class Transform(object):
    TRANSLATE = 'translate'
    ROTATE = 'rotate'
    SCALE = 'scale'
    SHEAR = 'shear'
    TRANSLATE_X = 'translateX'
    TRANSLATE_Y = 'translateY'
    TRANSLATE_Z = 'translateZ'
    ROTATE_ORDER = 'rotateOrder'
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


class TypeGeneratorMode(object):
    OFF = 'Off'
    PYTHON = 'Python'
    ALL = [OFF, PYTHON]


class ViewportPosition(object):
    TOP_LEFT = 'topLeft'
    TOP_CENTER = 'topCenter'
    TOP_RIGHT = 'topRight'
    MIDDLE_LEFT = 'midLeft'
    MIDDLE_CENTER = 'midCenter'
    MIDDLE_CENTER_TOP = 'midCenterTop'
    MIDDLE_CENTER_BOTTOM = 'midCenterBot'
    MIDDLE_RIGHT = 'midRight'
    BOTTOM_LEFT = 'botLeft'
    BOTTOM_CENTER = 'botCenter'
    BOTTOM_RIGHT = 'botRight'
    ALL = [TOP_LEFT, TOP_CENTER, TOP_RIGHT,
           MIDDLE_LEFT, MIDDLE_CENTER, MIDDLE_CENTER_TOP, MIDDLE_CENTER_BOTTOM, MIDDLE_RIGHT,
           BOTTOM_LEFT, BOTTOM_CENTER, BOTTOM_RIGHT]


class WorldUpType(object):
    SCENE = 'scene'
    OBJECT = 'object'
    OBJECT_ROTATION = 'objectrotation'
    VECTOR = 'vector'
    NONE = 'none'
    ALL = [SCENE, OBJECT, OBJECT_ROTATION, VECTOR, NONE]
