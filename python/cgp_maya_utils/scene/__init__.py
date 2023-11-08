"""
python objects and management functions to manipulate a variety of entities in a maya scene
such as nodes, attributes, components, namespaces, plugins ...
"""


# IMPORTS #


from ._api import (_registerAttributeTypes,
                   _registerComponentTypes,
                   _registerMiscTypes,
                   _registerNodeTypes,
                   _registerOptionVarTypes,
                   animKey,
                   animLayer,
                   attribute,
                   createAttribute,
                   createNode,
                   component,
                   connection,
                   currentNamespace,
                   getAnimKeys,
                   getAnimLayers,
                   getAttributes,
                   getConnections,
                   getNamespaces,
                   getNodes,
                   getNodesFromAttributes,
                   getOptionVars,
                   namespace,
                   node,
                   optionVar,
                   plugin,
                   scene)

# attribute imports

from ._attributes._generic import Attribute

from ._attributes._array import (DoubleArrayAttribute,
                                 FloatArrayAttribute,
                                 Int32ArrayAttribute,
                                 PointArrayAttribute,
                                 StringArrayAttribute,
                                 VectorArrayAttribute)

from ._attributes._compound import (CompoundAttribute,
                                    Double2Attribute,
                                    Double3Attribute,
                                    Double4Attribute,
                                    Float2Attribute,
                                    Float3Attribute,
                                    Float4Attribute,
                                    Long2Attribute,
                                    Long3Attribute,
                                    Long4Attribute,
                                    Short2Attribute,
                                    Short3Attribute,
                                    Short4Attribute,
                                    TdataCompoundAttribute)

from ._attributes._misc import (BoolAttribute,
                                EnumAttribute,
                                MatrixAttribute,
                                MessageAttribute,
                                StringAttribute)

from ._attributes._numeric import (NumericAttribute,
                                   ByteAttribute,
                                   DoubleAngleAttribute,
                                   DoubleAttribute,
                                   DoubleLinearAttribute,
                                   FloatAttribute,
                                   LongAttribute,
                                   ShortAttribute,
                                   TimeAttribute)

# component imports

from ._components._generic import (Component,
                                   TransformComponent)

from ._components._mesh import (MeshComponent,
                                Edge,
                                Face,
                                UvMap,
                                Vertex)

from ._components._nurbCurve import (CurvePoint,
                                     EditPoint)

from ._components._nurbsSurface import (IsoparmU,
                                        IsoparmV,
                                        SurfacePatch,
                                        SurfacePoint)

# misc imports

from ._misc._animKey import AnimKey

from ._misc._animLayer import AnimLayer

from ._misc._connection import Connection

from ._misc._misc import (Namespace,
                          Plugin,
                          Scene)

from ._misc._optionVar import (OptionVar,
                               FloatArrayOptionVar,
                               FloatOptionVar,
                               IntArrayOptionVar,
                               IntOptionVar,
                               StringArrayOptionVar,
                               StringOptionVar)

# node imports

from ._nodes._animCurve import (AnimCurve,
                                AnimCurveTA,
                                AnimCurveTL,
                                AnimCurveTU)

from ._nodes._constraint import (Constraint,
                                 AimConstraint,
                                 OrientConstraint,
                                 ParentConstraint,
                                 PointConstraint,
                                 ScaleConstraint)

from ._nodes._generic import (Node,
                              DagNode,
                              ObjectSet,
                              Reference)

from ._nodes._geometryFilter import (GeometryFilter,
                                     BlendShape,
                                     SoftMod,
                                     SkinCluster)

from ._nodes._misc import (ComposeMatrix,
                           DecomposeMatrix,
                           DisplayLayer,
                           GpuCache,
                           ShadingEngine)

from ._nodes._shader import (ShadingDependNode,
                             Lambert)

from ._nodes._shape import (Shape,
                            GeometryShape,
                            Camera,
                            Follicle,
                            Mesh,
                            NurbsCurve,
                            NurbsSurface)

from ._nodes._transform import (Transform,
                                IkEffector,
                                IkHandle,
                                Joint)


# COLLECT TYPES #


__attributeTypes = {cls._TYPE: cls
                    for cls in (Attribute,
                                DoubleArrayAttribute,
                                FloatArrayAttribute,
                                Int32ArrayAttribute,
                                PointArrayAttribute,
                                StringArrayAttribute,
                                VectorArrayAttribute,
                                CompoundAttribute,
                                Double2Attribute,
                                Double3Attribute,
                                Double4Attribute,
                                Float2Attribute,
                                Float3Attribute,
                                Float4Attribute,
                                Long2Attribute,
                                Long3Attribute,
                                Long4Attribute,
                                Short2Attribute,
                                Short3Attribute,
                                Short4Attribute,
                                TdataCompoundAttribute,
                                BoolAttribute,
                                EnumAttribute,
                                MatrixAttribute,
                                MessageAttribute,
                                StringAttribute,
                                NumericAttribute,
                                ByteAttribute,
                                DoubleAttribute,
                                DoubleAngleAttribute,
                                DoubleLinearAttribute,
                                FloatAttribute,
                                LongAttribute,
                                ShortAttribute,
                                TimeAttribute)}

__componentTypes = {cls._TYPE: cls
                    for cls in (Component,
                                TransformComponent,
                                Edge,
                                Face,
                                UvMap,
                                Vertex,
                                CurvePoint,
                                EditPoint,
                                SurfacePoint,
                                IsoparmU,
                                IsoparmV,
                                SurfacePatch)}

__miscTypes = {cls._TYPE: cls
               for cls in (AnimKey,
                           AnimLayer,
                           Connection,
                           Namespace,
                           Plugin,
                           Scene)}

__nodeTypes = {cls._TYPE: cls
               for cls in (AnimCurve,
                           AnimCurveTA,
                           AnimCurveTL,
                           AnimCurveTU,
                           Constraint,
                           AimConstraint,
                           OrientConstraint,
                           ParentConstraint,
                           PointConstraint,
                           ScaleConstraint,
                           Node,
                           DagNode,
                           ObjectSet,
                           Reference,
                           GeometryFilter,
                           BlendShape,
                           SoftMod,
                           SkinCluster,
                           IkEffector,
                           IkHandle,
                           ComposeMatrix,
                           DecomposeMatrix,
                           DisplayLayer,
                           GpuCache,
                           ShadingEngine,
                           ShadingDependNode,
                           Lambert,
                           Shape,
                           GeometryShape,
                           Camera,
                           Follicle,
                           NurbsCurve,
                           NurbsSurface,
                           Mesh,
                           Transform,
                           Joint)}

__optionVarTypes = {cls._TYPE: cls
                    for cls in (OptionVar,
                                IntOptionVar,
                                FloatOptionVar,
                                StringOptionVar,
                                IntArrayOptionVar,
                                FloatArrayOptionVar,
                                StringArrayOptionVar)}


# REGISTER TYPES #


_registerAttributeTypes(__attributeTypes)
_registerComponentTypes(__componentTypes)
_registerMiscTypes(__miscTypes)
_registerNodeTypes(__nodeTypes)
_registerOptionVarTypes(__optionVarTypes)


# DEFINE ALL #


__all__ = ['animKey',  # api
           'animLayer',
           'attribute',
           'createAttribute',
           'createNode',
           'component',
           'connection',
           'currentNamespace',
           'getAnimKeys',
           'getAnimLayers',
           'getAttributes',
           'getConnections',
           'getNamespaces',
           'getNodes',
           'getNodesFromAttributes',
           'getOptionVars',
           'namespace',
           'node',
           'optionVar',
           'plugin',
           'scene',

           # attributes
           'Attribute',
           'BoolAttribute',
           'ByteAttribute',
           'NumericAttribute',
           'CompoundAttribute',
           'Connection',
           'Double2Attribute',
           'Double3Attribute',
           'Double4Attribute',
           'DoubleAngleAttribute',
           'DoubleArrayAttribute',
           'DoubleAttribute',
           'DoubleLinearAttribute',
           'EnumAttribute',
           'Float2Attribute',
           'Float3Attribute',
           'Float4Attribute',
           'FloatAttribute',
           'FloatArrayAttribute',
           'Int32ArrayAttribute',
           'Long2Attribute',
           'Long3Attribute',
           'Long4Attribute',
           'LongAttribute',
           'MatrixAttribute',
           'MessageAttribute',
           'PointArrayAttribute',
           'Short2Attribute',
           'Short3Attribute',
           'Short4Attribute',
           'ShortAttribute',
           'StringArrayAttribute',
           'StringAttribute',
           'TdataCompoundAttribute',
           'TimeAttribute',
           'VectorArrayAttribute',

           # components
           'Component',
           'CurvePoint',
           'Edge',
           'EditPoint',
           'Face',
           'IsoparmU',
           'IsoparmV',
           'MeshComponent',
           'SurfacePatch',
           'SurfacePoint',
           'TransformComponent',
           'UvMap',
           'Vertex',

           # nodes
           'AimConstraint',
           'AnimCurve',
           'AnimCurveTA',
           'AnimCurveTL',
           'AnimCurveTU',
           'BlendShape',
           'Camera',
           'ComposeMatrix',
           'Constraint',
           'DagNode',
           'DecomposeMatrix',
           'DisplayLayer',
           'Follicle',
           'GeometryFilter',
           'GeometryShape',
           'GpuCache',
           'ShadingEngine',
           'ShadingDependNode',
           'Lambert',
           'IkEffector',
           'IkHandle',
           'Joint',
           'Mesh',
           'Node',
           'NurbsCurve',
           'NurbsSurface',
           'ObjectSet',
           'OrientConstraint',
           'ParentConstraint',
           'PointConstraint',
           'Reference',
           'ScaleConstraint',
           'Shape',
           'SoftMod',
           'SkinCluster',
           'Transform',

           # optionVars
           'FloatArrayOptionVar',
           'FloatOptionVar',
           'IntArrayOptionVar',
           'IntOptionVar',
           'OptionVar',
           'StringArrayOptionVar',
           'StringOptionVar']
