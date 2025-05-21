from cadquery import Plane, Vector, Workplane, Location, Sketch
from cadquery.cq import CQObject, CQContext
from cadquery.occ_impl.shapes import Shape
from pydantic_core import core_schema, CoreSchema



def get_cqobject_schema(cls, _source, _info) -> CoreSchema:
    from .geom import get_vector_schema, get_location_schema
    from .shapes import get_shape_schema
    from .sketch import get_sketch_schema


    """Get Pydantic schema for CQObject serialization."""
    # Get schemas for each type in the union
    vector_schema = get_vector_schema(Vector, None, None)
    location_schema = get_location_schema(Location, None, None)
    shape_schema = get_shape_schema(Shape, None, None)
    sketch_schema = get_sketch_schema(Sketch, None, None)

    # Create a union schema for CQObject
    return core_schema.union_schema(
        [
            vector_schema,
            location_schema,
            shape_schema,
            sketch_schema,
        ]
    )


def get_cqcontext_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for CQContext serialization."""
    from .geom import get_vector_schema
    from .shapes import get_shape_schema

    def validate_cqcontext(value: dict) -> CQContext:
        # Create a new CQContext using __new__
        ctx = object.__new__(CQContext)
        ctx.pendingWires = value["pendingWires"]
        ctx.pendingEdges = value["pendingEdges"]
        ctx.firstPoint = value.get("firstPoint")
        ctx.tolerance = value["tolerance"]
        ctx.tags = value.get("tags", {})
        return ctx

    def serialize_cqcontext(ctx: CQContext) -> dict:
        result = {
            "pendingWires": ctx.pendingWires if ctx.pendingWires is not None else [],
            "pendingEdges": ctx.pendingEdges if ctx.pendingEdges is not None else [],
            "firstPoint": ctx.firstPoint,
            "tolerance": ctx.tolerance,
        }
        return result

    # Get schemas for nested types
    vector_schema = get_vector_schema(Vector, None, None)
    shape_schema = get_shape_schema(Shape, None, None)

    model_schema = core_schema.typed_dict_schema(
        {
            "pendingWires": core_schema.model_field(
                core_schema.list_schema(shape_schema)
            ),
            "pendingEdges": core_schema.model_field(
                core_schema.list_schema(shape_schema)
            ),
            "firstPoint": core_schema.model_field(
                core_schema.union_schema([core_schema.none_schema(), vector_schema])
            ),
            "tolerance": core_schema.model_field(core_schema.float_schema()),
        }
    )

    return core_schema.json_or_python_schema(
        json_schema=core_schema.no_info_after_validator_function(
            validate_cqcontext, model_schema
        ),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(CQContext),
                core_schema.chain_schema(
                    [
                        model_schema,
                        core_schema.no_info_after_validator_function(
                            validate_cqcontext, model_schema
                        ),
                    ]
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_cqcontext,
            return_schema=model_schema,
            when_used="json",
        ),
    )


def get_workplane_schema(cls, _source, _info) -> CoreSchema:
    from .geom import get_plane_schema

    """Get Pydantic schema for Workplane serialization.

    Example:
        >>> from pydantic import TypeAdapter
        >>> import cadquery as cq
        >>> wp = cq.Workplane("XY").box(1, 1, 1)
        >>> TypeAdapter(cq.Workplane).dump_json(wp)
        '{"plane": {...}, "objects": [...], "parent": null, "_tag": null}'
    """

    # Define the field schemas
    plane_field = core_schema.model_field(get_plane_schema(Plane, None, None))
    objects_field = core_schema.model_field(
        core_schema.list_schema(get_cqobject_schema(CQObject, None, None))
    )
    tag_field = core_schema.model_field(
        core_schema.union_schema([core_schema.none_schema(), core_schema.str_schema()])
    )

    context_schema = get_cqcontext_schema(CQContext, None, None)
    context_field = core_schema.model_field(
        core_schema.union_schema([core_schema.none_schema(), context_schema])
    )

    workplane_schema = core_schema.definition_reference_schema("Workplane")
    parent_field = core_schema.model_field(
        core_schema.union_schema([core_schema.none_schema(), workplane_schema])
    )
    # Create the model schema
    model_schema = core_schema.typed_dict_schema(
        {
            "plane": plane_field,
            "objects": objects_field,
            "_tag": tag_field,
            "ctx": context_field,
            "parent": parent_field,
        }
    )

    def validate_workplane(value: dict | Workplane) -> Workplane:
        if isinstance(value, Workplane):
            return value

        # Create a new workplane instance without calling __init__
        wp = object.__new__(Workplane)

        # Set fields directly
        wp.plane = value["plane"]
        wp.objects = value["objects"]
        wp._tag = value["_tag"]
        wp.parent = value["parent"]
        # wp.ctx = value["ctx"]
        return wp

    def serialize_workplane(wp: Workplane) -> dict:
        return {
            "plane": wp.plane,
            "objects": list(wp.objects),  # Ensure we get a list
            "_tag": wp._tag,
            "parent": wp.parent,
            "ctx": wp.ctx,
        }

    schema = core_schema.definitions_schema(
        schema=workplane_schema,
        definitions=[
            core_schema.json_or_python_schema(
                json_schema=core_schema.no_info_after_validator_function(
                    validate_workplane, model_schema
                ),
                python_schema=core_schema.union_schema(
                    [
                        core_schema.is_instance_schema(Workplane),
                        core_schema.chain_schema(
                            [
                                model_schema,
                                core_schema.no_info_after_validator_function(
                                    validate_workplane, model_schema
                                ),
                            ]
                        ),
                    ]
                ),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    serialize_workplane,
                    return_schema=model_schema,
                    when_used="json",
                ),
                ref="Workplane",
            )
        ],
    )
    return schema
