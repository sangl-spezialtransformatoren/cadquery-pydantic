from cadquery import Sketch
from pydantic_core import core_schema
from cadquery.sketch import Constraint, ConstraintInvariants
from .shapes import shape_core_schema
from .geom import location_core_schema

# Create a union schema for all possible parameter types
constraint_param_schema = core_schema.union_schema(
    [
        core_schema.none_schema(),  # None
        core_schema.float_schema(),  # float
        core_schema.tuple_schema(
            [  # Tuple[Optional[float], Optional[float], float]
                core_schema.union_schema(
                    [core_schema.none_schema(), core_schema.float_schema()]
                ),
                core_schema.union_schema(
                    [core_schema.none_schema(), core_schema.float_schema()]
                ),
                core_schema.float_schema(),
            ]
        ),
        core_schema.tuple_schema(
            [  # Tuple[float, float]
                core_schema.float_schema(),
                core_schema.float_schema(),
            ]
        ),
    ]
)

# Constraint schema
def validate_constraint(value: dict) -> Constraint:
    return Constraint(
        tags=tuple(value["tags"]),
        args=tuple(value["args"]),
        kind=value["kind"],
        param=value["param"],
    )

def serialize_constraint(constraint: Constraint) -> dict:
    return {
        "tags": constraint.tags,
        "args": constraint.args,
        "kind": constraint.kind,
        "param": constraint.param,
    }

constraint_model_schema = core_schema.typed_dict_schema(
    {
        "tags": core_schema.model_field(
            core_schema.tuple_schema(
                [core_schema.str_schema()], variadic_item_index=0
            )
        ),
        "args": core_schema.model_field(
            core_schema.tuple_schema([shape_core_schema], variadic_item_index=0)
        ),
        "kind": core_schema.model_field(
            core_schema.literal_schema(list(ConstraintInvariants.keys()))
        ),
        "param": core_schema.model_field(constraint_param_schema),
    }
)

constraint_core_schema = core_schema.json_or_python_schema(
    json_schema=core_schema.no_info_after_validator_function(
        validate_constraint, constraint_model_schema
    ),
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(Constraint),
            core_schema.chain_schema(
                [
                    constraint_model_schema,
                    core_schema.no_info_after_validator_function(
                        validate_constraint, constraint_model_schema
                    ),
                ]
            ),
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_constraint,
        return_schema=constraint_model_schema,
        when_used="json",
    ),
)

# Sketch schema
def validate_sketch(value: dict) -> Sketch:
    # Create a new Sketch instance without calling __init__
    sketch = object.__new__(Sketch)

    # Set fields directly
    sketch._locs = value.get("_locs", [])
    sketch._faces = value.get("_faces", [])
    sketch._edges = value.get("_edges", [])
    sketch._constraints = value.get("_constraints", [])
    sketch._selection = value.get("_selection", [])
    sketch._tags = value.get("_tags", {})

    return sketch

def serialize_sketch(sketch: Sketch) -> dict:
    return {
        "locs": sketch.locs,
        "_faces": sketch._faces,
        "_edges": sketch._edges,
        "_selection": sketch._selection,
        "_constraints": sketch._constraints,
        "_tags": sketch._tags,
    }

# Create schema for SketchVal (which is a tuple of (Edge, Location))
sketchval_schema = core_schema.tuple_schema(
    [
        shape_core_schema,
        location_core_schema,
    ]
)

sketch_model_schema = core_schema.typed_dict_schema(
    {
        "locs": core_schema.model_field(core_schema.list_schema(location_core_schema)),
        "_faces": core_schema.model_field(
            core_schema.union_schema([core_schema.none_schema(), shape_core_schema])
        ),
        "_edges": core_schema.model_field(core_schema.list_schema(shape_core_schema)),
        "_selection": core_schema.model_field(
            core_schema.union_schema(
                [
                    core_schema.none_schema(),
                    core_schema.list_schema(sketchval_schema),
                ]
            )
        ),
        "_constraints": core_schema.model_field(
            core_schema.list_schema(constraint_core_schema)
        ),
        "_tags": core_schema.model_field(core_schema.dict_schema(core_schema.str_schema(), core_schema.list_schema(sketchval_schema))),
    }
)

sketch_core_schema = core_schema.json_or_python_schema(
    json_schema=core_schema.no_info_after_validator_function(
        validate_sketch, sketch_model_schema
    ),
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(Sketch),
            core_schema.chain_schema(
                [
                    sketch_model_schema,
                    core_schema.no_info_after_validator_function(
                        validate_sketch, sketch_model_schema
                    ),
                ]
            ),
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_sketch,
        return_schema=sketch_model_schema,
        when_used="json",
    ),
)
