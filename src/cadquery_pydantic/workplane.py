from typing import cast
from cadquery import Workplane
from cadquery.cq import CQContext
from pydantic_core import core_schema
from .geom import vector_core_schema, location_core_schema, plane_core_schema
from .shapes import shape_core_schema
from .sketch import sketch_core_schema


def get_workplane_id(wp: Workplane | None) -> str | None:
    """Get a consistent string ID for a workplane instance."""
    if wp is None:
        return None
    return str(id(wp))


def extract_id_from_ref(ref: str | None) -> str | None:
    """Extract workplane ID from a reference."""
    if ref is None:
        return None
    return ref.split("/")[-1]


# CQObject schema - Union of all possible object types in a workplane
cqobject_core_schema = core_schema.union_schema(
    [
        vector_core_schema,
        location_core_schema,
        shape_core_schema,
        sketch_core_schema,
    ]
)


def collect_related_workplanes(
    wp: Workplane, collected: set[Workplane] | None = None
) -> set[Workplane]:
    """Recursively collect all related workplanes through parent links and context tags."""
    if collected is None:
        collected = set()

    if wp in collected:
        return collected

    collected.add(wp)

    # Add parent if it exists
    if wp.parent is not None and isinstance(wp.parent, Workplane):
        parent = cast(Workplane, wp.parent)
        collect_related_workplanes(parent, collected)

    # Add all tagged workplanes
    for tagged_wp in wp.ctx.tags.values():
        if isinstance(tagged_wp, Workplane):
            collect_related_workplanes(tagged_wp, collected)

    return collected


# Schema for a workplane's context
workplane_ctx_schema = core_schema.typed_dict_schema(
    {
        "pendingWires": core_schema.typed_dict_field(
            core_schema.list_schema(shape_core_schema)
        ),
        "pendingEdges": core_schema.typed_dict_field(
            core_schema.list_schema(shape_core_schema)
        ),
        "firstPoint": core_schema.typed_dict_field(
            core_schema.union_schema([core_schema.none_schema(), vector_core_schema])
        ),
        "tolerance": core_schema.typed_dict_field(core_schema.float_schema()),
        "tags": core_schema.typed_dict_field(
            core_schema.dict_schema(
                core_schema.str_schema(),
                core_schema.union_schema(
                    [
                        core_schema.none_schema(),
                        core_schema.typed_dict_schema(
                            {
                                "$ref": core_schema.typed_dict_field(
                                    core_schema.str_schema()
                                )
                            }
                        ),
                    ]
                ),
            )
        ),
    }
)


# Base schema for a single workplane
workplane_schema = core_schema.typed_dict_schema(
    {
        "plane": core_schema.typed_dict_field(plane_core_schema),
        "objects": core_schema.typed_dict_field(
            core_schema.list_schema(cqobject_core_schema)
        ),
        "parent": core_schema.typed_dict_field(
            core_schema.union_schema(
                [
                    core_schema.none_schema(),
                    core_schema.typed_dict_schema(
                        {"$ref": core_schema.typed_dict_field(core_schema.str_schema())}
                    ),
                ]
            )
        ),
        "_tag": core_schema.typed_dict_field(
            core_schema.union_schema(
                [core_schema.none_schema(), core_schema.str_schema()]
            )
        ),
    }
)


# Schema for the complete workplane model
workplane_model_schema = core_schema.typed_dict_schema(
    {
        "root": core_schema.typed_dict_field(
            core_schema.typed_dict_schema(
                {"$ref": core_schema.typed_dict_field(core_schema.str_schema())}
            )
        ),
        "workplanes": core_schema.typed_dict_field(
            core_schema.dict_schema(
                core_schema.str_schema(),
                workplane_schema,
            )
        ),
        "ctx": core_schema.typed_dict_field(workplane_ctx_schema),
    }
)


def validate_workplane(value: dict) -> Workplane:
    """Validate and construct a Workplane from a dictionary."""
    workplanes = {}

    # Create shared context
    ctx = object.__new__(CQContext)
    ctx.pendingWires = value["ctx"]["pendingWires"]
    ctx.pendingEdges = value["ctx"]["pendingEdges"]
    ctx.firstPoint = value["ctx"]["firstPoint"]
    ctx.tolerance = value["ctx"]["tolerance"]
    ctx.tags = {}  # Will be populated in second pass

    # First pass: Create all workplane instances
    for wp_id, wp_data in value["workplanes"].items():
        wp = object.__new__(Workplane)
        wp.plane = wp_data["plane"]
        wp.objects = wp_data["objects"]
        wp.parent = None  # Will be set in second pass
        wp._tag = wp_data["_tag"]
        wp.ctx = ctx  # Share the same context

        workplanes[wp_id] = wp

    # Second pass: Set up relationships
    for wp_id, wp_data in value["workplanes"].items():
        wp = workplanes[wp_id]

        # Set up parent relationship
        if wp_data["parent"] is not None:
            parent_id = extract_id_from_ref(wp_data["parent"]["$ref"])
            wp.parent = workplanes[parent_id]

    # Set up tags in the shared context
    for tag, ref in value["ctx"]["tags"].items():
        if ref is not None:
            tagged_wp_id = extract_id_from_ref(ref["$ref"])
            ctx.tags[tag] = workplanes[tagged_wp_id]

    # Get the root workplane
    root_id = extract_id_from_ref(value["root"]["$ref"])
    return workplanes[root_id]


def serialize_workplane(wp: Workplane) -> dict:
    """Serialize a Workplane to a dictionary."""
    # Collect all related workplanes
    all_workplanes = collect_related_workplanes(wp)

    # Get the shared context from the root workplane
    ctx = {
        "pendingWires": wp.ctx.pendingWires if wp.ctx.pendingWires is not None else [],
        "pendingEdges": wp.ctx.pendingEdges if wp.ctx.pendingEdges is not None else [],
        "firstPoint": wp.ctx.firstPoint,
        "tolerance": wp.ctx.tolerance,
        "tags": {
            tag: {"$ref": f"3/{get_workplane_id(tagged_wp)}"}
            if tagged_wp is not None
            else None
            for tag, tagged_wp in wp.ctx.tags.items()
        },
    }

    # Serialize each workplane
    workplanes = {}
    for workplane in all_workplanes:
        workplanes[get_workplane_id(workplane)] = {
            "plane": workplane.plane,
            "objects": workplane.objects,
            "parent": {"$ref": f"2/{get_workplane_id(workplane.parent)}"}
            if workplane.parent is not None
            else None,
            "_tag": workplane._tag,
        }

    return {
        "root": {"$ref": f"0/workplanes/{get_workplane_id(wp)}"},
        "workplanes": workplanes,
        "ctx": ctx,
    }


workplane_from_json_schema = core_schema.chain_schema(
    [
        workplane_model_schema,
        core_schema.no_info_plain_validator_function(validate_workplane),
    ]
)


# Root schema containing all workplanes
workplane_core_schema = core_schema.json_or_python_schema(
    json_schema=workplane_from_json_schema,
    python_schema=core_schema.union_schema(
        [core_schema.is_instance_schema(Workplane), workplane_from_json_schema]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_workplane, return_schema=workplane_model_schema
    ),
)
