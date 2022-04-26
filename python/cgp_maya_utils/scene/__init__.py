"""
python objects and management functions to manipulate a variety of entities in a maya scene
such as nodes, attributes, components, namespaces, plugins ...
"""

# imports local
from ._api import (attribute, connection, createAttribute, getAttributes, getNodesFromAttributes,
                   currentNamespace, namespace, plugin, scene,
                   component,
                   createNode, getNodes, node,
                   _registerAttributeTypes, _registerComponentTypes, _registerMiscTypes, _registerNodeTypes)

from ._misc._misc import Namespace, Plugin, Scene

from ._attributes._generic import Attribute, Connection
from ._attributes._compound import CompoundAttribute, Double3Attribute, Float3Attribute, TDataCompoundAttribute
from ._attributes._misc import (BoolAttribute, EnumAttribute, MatrixAttribute, MessageAttribute, StringAttribute)
from ._attributes._numeric import (NumericAttribute, ByteAttribute, DoubleAngleAttribute, DoubleAttribute,
                                   DoubleLinearAttribute, FloatAttribute, LongAttribute, ShortAttribute, TimeAttribute)

from ._components._generic import Component, TransformComponent
from ._components._mesh import Edge, Face, Vertex
from ._components._nurbCurve import EditPoint, CurvePoint
from ._components._nurbsSurface import IsoparmU, IsoparmV, SurfacePatch, SurfacePoint

from ._nodes._animCurve import AnimCurve, AnimCurveTA, AnimCurveTL, AnimCurveTU
from ._nodes._constraint import (Constraint, AimConstraint, OrientConstraint, ParentConstraint,
                                 PointConstraint, ScaleConstraint)
from ._nodes._generic import Node, DagNode, ObjectSet, Reference
from ._nodes._geometryFilter import GeometryFilter, BlendShape, SkinCluster
from ._nodes._ik import IkEffector, IkHandle
from ._nodes._shape import Shape, NurbsCurve, NurbsSurface, Mesh
from ._nodes._transform import Transform, Joint


# register attributes / misc / node / component types
__attributeTypes = {'compound': CompoundAttribute,
                    'double3': Double3Attribute,
                    'float3': Float3Attribute,
                    'TdataCompound': TDataCompoundAttribute,
                    'connection': Connection,
                    'attribute': Attribute,
                    'bool': BoolAttribute,
                    'enum': EnumAttribute,
                    'matrix': MatrixAttribute,
                    'message': MessageAttribute,
                    'string': StringAttribute,
                    'numeric': NumericAttribute,
                    'byte': ByteAttribute,
                    'double': DoubleAttribute,
                    'doubleAngle': DoubleAngleAttribute,
                    'doubleLinear': DoubleLinearAttribute,
                    'float': FloatAttribute,
                    'long': LongAttribute,
                    'short': ShortAttribute,
                    'time': TimeAttribute}

__miscTypes = {'namespace': Namespace,
               'plugin': Plugin,
               'scene': Scene}

__nodeTypes = {'node': Node,
               'dagNode': DagNode,
               'objectSet': ObjectSet,
               'reference': Reference,
               'animCurve': AnimCurve,
               'animCurveTA': AnimCurveTA,
               'animCurveTL': AnimCurveTL,
               'animCurveTU': AnimCurveTU,
               'constraint': Constraint,
               'aimConstraint': AimConstraint,
               'orientConstraint': OrientConstraint,
               'parentConstraint': ParentConstraint,
               'pointConstraint': PointConstraint,
               'scaleConstraint': ScaleConstraint,
               'geometryFilter': GeometryFilter,
               'blendShape': BlendShape,
               'skinCluster': SkinCluster,
               'ikEffector': IkEffector,
               'ikHandle': IkHandle,
               'shape': Shape,
               'nurbsCurve': NurbsCurve,
               'nurbsSurface': NurbsSurface,
               'mesh': Mesh,
               'transform': Transform,
               'joint': Joint}

__componentTypes = {'component': Component,
                    'transformComponent': TransformComponent,
                    'e[]': Edge,
                    'f[]': Face,
                    'vtx[]': Vertex,
                    'cv[]': CurvePoint,
                    'ep[]': EditPoint,
                    'cv[][]': SurfacePoint,
                    'u[]': IsoparmU,
                    'v[]': IsoparmV,
                    'sf[][]': SurfacePatch}

_registerAttributeTypes(__attributeTypes)
_registerMiscTypes(__miscTypes)
_registerNodeTypes(__nodeTypes)
_registerComponentTypes(__componentTypes)


__all__ = ['attribute', 'connection', 'createAttribute', 'getAttributes', 'getNodesFromAttributes',
           'createNode', 'getNodes', 'node',
           'currentNamespace', 'namespace', 'plugin', 'scene',
           'Namespace', 'Plugin', 'Scene',
           'Attribute', 'Connection',
           'Double3Attribute', 'Float3Attribute',
           'BoolAttribute', 'EnumAttribute', 'MatrixAttribute', 'MessageAttribute', 'StringAttribute',
           'ByteAttribute', 'DoubleAngleAttribute', 'DoubleAttribute', 'DoubleLinearAttribute',
           'NumericAttribute', 'FloatAttribute', 'LongAttribute', 'ShortAttribute', 'TimeAttribute',
           'CompoundAttribute', 'Double3Attribute', 'Float3Attribute', 'TDataCompoundAttribute',
           'component',
           'Component', 'TransformComponent',
           'Edge', 'Face', 'Vertex',
           'EditPoint', 'CurvePoint',
           'IsoparmU', 'IsoparmV', 'SurfacePatch', 'SurfacePoint',
           'AnimCurve', 'AnimCurveTA', 'AnimCurveTL', 'AnimCurveTU',
           'Constraint', 'AimConstraint', 'OrientConstraint', 'ParentConstraint',
           'PointConstraint', 'ScaleConstraint',
           'Node', 'DagNode', 'Reference',
           'GeometryFilter', 'BlendShape', 'SkinCluster',
           'IkEffector', 'IkHandle',
           'Shape', 'NurbsCurve', 'NurbsSurface', 'Mesh',
           'Transform', 'Joint']
