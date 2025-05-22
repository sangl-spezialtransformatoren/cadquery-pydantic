from cadquery import Workplane
from cadquery.cq import CQContext
from pydantic_core import core_schema
from .geom import vector_core_schema, location_core_schema, plane_core_schema
from .shapes import shape_core_schema
from .sketch import sketch_core_schema

# CQObject schema
cqobject_core_schema = core_schema.union_schema(
    [
        vector_core_schema,
        location_core_schema,
        shape_core_schema,
        sketch_core_schema,
    ]
)

# CQContext schema
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

cqcontext_model_schema = core_schema.typed_dict_schema(
    {
        "pendingWires": core_schema.model_field(
            core_schema.list_schema(shape_core_schema)
        ),
        "pendingEdges": core_schema.model_field(
            core_schema.list_schema(shape_core_schema)
        ),
        "firstPoint": core_schema.model_field(
            core_schema.union_schema([core_schema.none_schema(), vector_core_schema])
        ),
        "tolerance": core_schema.model_field(core_schema.float_schema()),
    }
)

cqcontext_core_schema = core_schema.json_or_python_schema(
    json_schema=core_schema.no_info_after_validator_function(
        validate_cqcontext, cqcontext_model_schema
    ),
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(CQContext),
            core_schema.chain_schema(
                [
                    cqcontext_model_schema,
                    core_schema.no_info_after_validator_function(
                        validate_cqcontext, cqcontext_model_schema
                    ),
                ]
            ),
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_cqcontext,
        return_schema=cqcontext_model_schema,
        when_used="json",
    ),
)

# Workplane schema
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

workplane_model_schema = core_schema.typed_dict_schema(
    {
        "plane": core_schema.model_field(plane_core_schema),
        "objects": core_schema.model_field(
            core_schema.list_schema(cqobject_core_schema)
        ),
        "_tag": core_schema.model_field(
            core_schema.union_schema([core_schema.none_schema(), core_schema.str_schema()])
        ),
        "ctx": core_schema.model_field(
            core_schema.union_schema([core_schema.none_schema(), cqcontext_core_schema])
        ),
        "parent": core_schema.model_field(
            core_schema.union_schema([core_schema.none_schema(), core_schema.definition_reference_schema("Workplane")])
        ),
    }
)

workplane_core_schema = core_schema.definitions_schema(
    schema=core_schema.definition_reference_schema("Workplane"),
    definitions=[
        core_schema.json_or_python_schema(
            json_schema=core_schema.no_info_after_validator_function(
                validate_workplane, workplane_model_schema
            ),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(Workplane),
                    core_schema.chain_schema(
                        [
                            workplane_model_schema,
                            core_schema.no_info_after_validator_function(
                                validate_workplane, workplane_model_schema
                            ),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_workplane,
                return_schema=workplane_model_schema,
                when_used="json",
            ),
            ref="Workplane",
        )
    ],
)
