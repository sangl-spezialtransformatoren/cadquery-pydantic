from cadquery import BoundBox, Location, Matrix, Plane, Shape, Sketch, Vector, Workplane
from cadquery.sketch import Constraint as SketchConstraint
from cadquery.cq import CQContext

from .geom import (
    vector_core_schema,
    matrix_core_schema,
    plane_core_schema,
    boundbox_core_schema,
    location_core_schema,
)
from .shapes import shape_core_schema
from .sketch import constraint_core_schema, sketch_core_schema
from .workplane import cqcontext_core_schema, workplane_core_schema


def patch_cadquery():
    # Patch geometry classes
    Vector.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: vector_core_schema)
    Matrix.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: matrix_core_schema)
    Plane.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: plane_core_schema)
    BoundBox.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: boundbox_core_schema)
    Location.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: location_core_schema)

    # Patch shape
    Shape.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: shape_core_schema)

    # Patch context
    CQContext.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: cqcontext_core_schema)

    # Patch workplane
    Workplane.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: workplane_core_schema)

    # Patch sketch
    SketchConstraint.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: constraint_core_schema)
    Sketch.__get_pydantic_core_schema__ = classmethod(lambda cls, _source, _info: sketch_core_schema)
