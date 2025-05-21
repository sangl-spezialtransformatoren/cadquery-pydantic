from cadquery import Location, Sketch
from cadquery.occ_impl.shapes import Compound, Edge
from pydantic_core import CoreSchema, core_schema
from cadquery.sketch import Constraint, ConstraintKind, ConstraintInvariants

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

def get_constraint_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for Constraint serialization."""
    from .shapes import get_shape_schema

    # Get schemas for nested types
    edge_schema = get_shape_schema(Edge, None, None)



    model_schema = core_schema.typed_dict_schema(
        {
            "tags": core_schema.model_field(
                core_schema.tuple_schema(
                    [core_schema.str_schema()], variadic_item_index=0
                )
            ),
            "args": core_schema.model_field(
                core_schema.tuple_schema([edge_schema], variadic_item_index=0)
            ),
            "kind": core_schema.model_field(
                core_schema.literal_schema(list(ConstraintInvariants.keys()))
            ),
            "param": core_schema.model_field(constraint_param_schema),
        }
    )

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

    return core_schema.json_or_python_schema(
        json_schema=core_schema.no_info_after_validator_function(
            validate_constraint, model_schema
        ),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(Constraint),
                core_schema.chain_schema(
                    [
                        model_schema,
                        core_schema.no_info_after_validator_function(
                            validate_constraint, model_schema
                        ),
                    ]
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_constraint,
            return_schema=model_schema,
            when_used="json",
        ),
    )


def get_sketch_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for Sketch serialization."""
    from .geom import get_location_schema
    from .shapes import get_shape_schema

    # Get schemas for nested types
    location_schema = get_location_schema(Location, None, None)
    edge_schema = get_shape_schema(Edge, None, None)
    compound_schema = get_shape_schema(Compound, None, None)
    constraint_schema = get_constraint_schema(Constraint, None, None)

    # Create schema for SketchVal (which is a tuple of (Edge, Location))
    sketchval_schema = core_schema.tuple_schema(
        [
            edge_schema,
            location_schema,
        ]
    )

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

    model_schema = core_schema.typed_dict_schema(
        {
            "locs": core_schema.model_field(core_schema.list_schema(location_schema)),
            "_faces": core_schema.model_field(
                core_schema.union_schema([core_schema.none_schema(), compound_schema])
            ),
            "_edges": core_schema.model_field(core_schema.list_schema(edge_schema)),
            "_selection": core_schema.model_field(
                core_schema.union_schema(
                    [
                        core_schema.none_schema(),
                        core_schema.list_schema(sketchval_schema),
                    ]
                )
            ),
            "_constraints": core_schema.model_field(
                core_schema.list_schema(constraint_schema)
            ),
            "_tags": core_schema.model_field(core_schema.dict_schema(core_schema.str_schema(), core_schema.list_schema(sketchval_schema))),
        }
    )

    return core_schema.json_or_python_schema(
        json_schema=core_schema.no_info_after_validator_function(
            validate_sketch, model_schema
        ),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(Sketch),
                core_schema.chain_schema(
                    [
                        model_schema,
                        core_schema.no_info_after_validator_function(
                            validate_sketch, model_schema
                        ),
                    ]
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_sketch,
            return_schema=model_schema,
            when_used="json",
        ),
    )
