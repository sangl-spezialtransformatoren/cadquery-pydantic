from cadquery import (
    Assembly,
    BoundBox,
    Location,
    Matrix,
    Plane,
    Shape,
    Sketch,
    Vector,
    Workplane,
    Color,
)
from cadquery.sketch import Constraint as SketchConstraint
from cadquery.assembly import Constraint as AssemblyConstraint

from .geom import (
    vector_core_schema,
    matrix_core_schema,
    plane_core_schema,
    boundbox_core_schema,
    location_core_schema,
)
from .shapes import shape_core_schema
from .sketch import constraint_core_schema, sketch_core_schema
from .workplane import workplane_core_schema
from .assembly import (
    assembly_core_schema,
    color_core_schema,
    constraint_spec_core_schema,
)


def patch_cadquery():
    # Patch geometry classes
    Vector.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: vector_core_schema
    )
    Matrix.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: matrix_core_schema
    )
    Plane.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: plane_core_schema
    )
    BoundBox.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: boundbox_core_schema
    )
    Location.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: location_core_schema
    )

    # Patch shape
    Shape.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: shape_core_schema
    )

    # Patch workplane
    Workplane.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: workplane_core_schema
    )

    # Patch sketch
    SketchConstraint.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: constraint_core_schema
    )
    Sketch.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: sketch_core_schema
    )

    # Patch assembly
    Assembly.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: assembly_core_schema
    )
    Color.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: color_core_schema
    )
    AssemblyConstraint.__get_pydantic_core_schema__ = classmethod(
        lambda cls, _source, _info: constraint_spec_core_schema
    )
