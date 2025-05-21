from cadquery import BoundBox, Location, Matrix, Plane, Shape, Sketch, Vector, Workplane
from cadquery.sketch import Constraint as SketchConstraint
from cadquery.cq import CQContext

from cadquery_pydantic.sketch import get_constraint_schema, get_sketch_schema
from cadquery_pydantic.workplane import get_cqcontext_schema
from .geom import (
    get_boundbox_schema,
    get_location_schema,
    get_matrix_schema,
    get_plane_schema,
    get_vector_schema,
)
from .shapes import get_shape_schema
from .workplane import get_workplane_schema


def patch_cadquery():
    # Patch geometry classes
    Vector.__get_pydantic_core_schema__ = classmethod(get_vector_schema)
    Matrix.__get_pydantic_core_schema__ = classmethod(get_matrix_schema)
    Plane.__get_pydantic_core_schema__ = classmethod(get_plane_schema)
    BoundBox.__get_pydantic_core_schema__ = classmethod(get_boundbox_schema)
    Location.__get_pydantic_core_schema__ = classmethod(get_location_schema)

    # Patch shape
    Shape.__get_pydantic_core_schema__ = classmethod(get_shape_schema)

    # Patch context
    CQContext.__get_pydantic_core_schema__ = classmethod(get_cqcontext_schema)

    # Patch workplane
    Workplane.__get_pydantic_core_schema__ = classmethod(get_workplane_schema)

    # Patch sketch
    SketchConstraint.__get_pydantic_core_schema__ = classmethod(get_constraint_schema)
    Sketch.__get_pydantic_core_schema__ = classmethod(get_sketch_schema)
