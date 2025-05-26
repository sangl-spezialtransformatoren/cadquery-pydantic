from cadquery import Assembly, Color
from cadquery.occ_impl.solver import ConstraintSpec
from pydantic_core import core_schema
from .shapes import shape_core_schema
from .workplane import workplane_core_schema
from .geom import location_core_schema


def get_assembly_id(assembly: Assembly | None) -> str | None:
    """Get a consistent string ID for an assembly instance."""
    if assembly is None:
        return None
    return str(id(assembly))


def extract_id_from_ref(ref: str | None) -> str | None:
    """Extract assembly ID from a reference."""
    if ref is None:
        return None
    return ref.split("/")[-1]


# Constraint kinds
CONSTRAINT_KINDS = [
    "Plane",
    "Point",
    "Axis",
    "PointInPlane",
    "Fixed",
    "FixedPoint",
    "FixedAxis",
    "PointOnLine",
    "FixedRotation",
]


# Schema for constraint specification
constraint_spec_schema = core_schema.typed_dict_schema(
    {
        "objects": core_schema.typed_dict_field(
            core_schema.tuple_schema(
                [core_schema.str_schema()],
                variadic_item_index=0,
            )
        ),
        "args": core_schema.typed_dict_field(
            core_schema.tuple_schema(
                [shape_core_schema],
                variadic_item_index=0,
            )
        ),
        "sublocs": core_schema.typed_dict_field(
            core_schema.tuple_schema(
                [location_core_schema],
                variadic_item_index=0,
            )
        ),
        "kind": core_schema.typed_dict_field(
            core_schema.literal_schema(CONSTRAINT_KINDS)
        ),
        "param": core_schema.typed_dict_field(core_schema.any_schema()),
    }
)


def validate_constraint_spec(value: dict) -> ConstraintSpec:
    """Validate and construct a ConstraintSpec from a dictionary."""
    return ConstraintSpec(
        objects=tuple(value["objects"]),
        args=tuple(value["args"]),
        sublocs=tuple(value["sublocs"]),
        kind=value["kind"],
        param=value["param"],
    )


def serialize_constraint_spec(spec: ConstraintSpec) -> dict:
    """Serialize a ConstraintSpec to a dictionary."""
    return {
        "objects": spec.objects,
        "args": spec.args,
        "sublocs": spec.sublocs,
        "kind": spec.kind,
        "param": spec.param,
    }


constraint_spec_from_json_schema = core_schema.chain_schema(
    [
        constraint_spec_schema,
        core_schema.no_info_plain_validator_function(validate_constraint_spec),
    ]
)


constraint_spec_core_schema = core_schema.json_or_python_schema(
    json_schema=constraint_spec_from_json_schema,
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(ConstraintSpec),
            constraint_spec_from_json_schema,
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_constraint_spec,
        return_schema=constraint_spec_schema,
    ),
)


# Color schema
color_schema = core_schema.typed_dict_schema(
    {
        "r": core_schema.typed_dict_field(core_schema.float_schema()),
        "g": core_schema.typed_dict_field(core_schema.float_schema()),
        "b": core_schema.typed_dict_field(core_schema.float_schema()),
        "a": core_schema.typed_dict_field(core_schema.float_schema()),
    }
)


def validate_color(value: dict) -> Color:
    return Color(value["r"], value["g"], value["b"], value["a"])


def serialize_color(color: Color) -> dict:
    r, g, b, a = color.toTuple()
    return {"r": r, "g": g, "b": b, "a": a}


color_from_json_schema = core_schema.chain_schema(
    [
        color_schema,
        core_schema.no_info_plain_validator_function(validate_color),
    ]
)

color_core_schema = core_schema.json_or_python_schema(
    json_schema=color_from_json_schema,
    python_schema=core_schema.union_schema(
        [core_schema.is_instance_schema(Color), color_from_json_schema]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_color,
        return_schema=color_schema,
    ),
)


# Schema for assembly objects (Shape, Workplane, or None)
assembly_object_schema = core_schema.union_schema(
    [
        core_schema.none_schema(),
        shape_core_schema,
        workplane_core_schema,
    ]
)


# Base schema for a single assembly
assembly_schema = core_schema.typed_dict_schema(
    {
        "loc": core_schema.typed_dict_field(location_core_schema),
        "name": core_schema.typed_dict_field(core_schema.str_schema()),
        "color": core_schema.typed_dict_field(
            core_schema.union_schema([core_schema.none_schema(), color_core_schema])
        ),
        "obj": core_schema.typed_dict_field(assembly_object_schema),
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
    }
)


# Schema for the complete assembly model
assembly_model_schema = core_schema.typed_dict_schema(
    {
        "root": core_schema.typed_dict_field(
            core_schema.typed_dict_schema(
                {"$ref": core_schema.typed_dict_field(core_schema.str_schema())}
            )
        ),
        "assemblies": core_schema.typed_dict_field(
            core_schema.dict_schema(
                core_schema.str_schema(),
                assembly_schema,
            )
        ),
        "constraints": core_schema.typed_dict_field(
            core_schema.list_schema(constraint_spec_core_schema)
        ),
    }
)


def collect_related_assemblies(
    assembly: Assembly, collected: set[Assembly] | None = None
) -> set[Assembly]:
    """Recursively collect all related assemblies through parent and children relationships."""
    if collected is None:
        collected = set()

    if assembly in collected:
        return collected

    collected.add(assembly)

    # Add parent if it exists
    if assembly.parent is not None:
        collect_related_assemblies(assembly.parent, collected)

    # Add all children
    for child in assembly.children:
        collect_related_assemblies(child, collected)

    return collected


def validate_assembly(value: dict) -> Assembly:
    """Validate and construct an Assembly from a dictionary."""
    assemblies = {}

    # First pass: Create all assembly instances
    for assembly_id, assembly_data in value["assemblies"].items():
        assembly = object.__new__(Assembly)
        assembly.loc = assembly_data["loc"]
        assembly.name = assembly_data["name"]
        assembly.color = assembly_data["color"]
        assembly.obj = assembly_data["obj"]
        assembly.parent = None  # Will be set in second pass
        assembly.children = []  # Will be populated in second pass
        assembly.constraints = []  # Will be populated later
        assembly.objects = {}  # Will be populated in second pass

        assemblies[assembly_id] = assembly

    # Second pass: Set up relationships
    for assembly_id, assembly_data in value["assemblies"].items():
        assembly = assemblies[assembly_id]

        # Set up parent relationship
        if assembly_data["parent"] is not None:
            parent_id = extract_id_from_ref(assembly_data["parent"]["$ref"])
            assembly.parent = assemblies[parent_id]
            assembly.parent.children.append(assembly)
            assembly.parent.objects[assembly.name] = assembly

    # Get the root assembly
    root_id = extract_id_from_ref(value["root"]["$ref"])
    root = assemblies[root_id]

    # Set up constraints
    root.constraints = value["constraints"]

    return root


def serialize_assembly(assembly: Assembly) -> dict:
    """Serialize an Assembly to a dictionary."""
    # Collect all related assemblies
    all_assemblies = collect_related_assemblies(assembly)

    # Serialize each assembly
    assemblies = {}
    for a in all_assemblies:
        assemblies[get_assembly_id(a)] = {
            "loc": a.loc,
            "name": a.name,
            "color": a.color,
            "obj": a.obj,
            "parent": {"$ref": f"2/{get_assembly_id(a.parent)}"}
            if a.parent is not None
            else None,
        }

    return {
        "root": {"$ref": f"0/assemblies/{get_assembly_id(assembly)}"},
        "assemblies": assemblies,
        "constraints": assembly.constraints,
    }


assembly_from_json_schema = core_schema.chain_schema(
    [
        assembly_model_schema,
        core_schema.no_info_plain_validator_function(validate_assembly),
    ]
)


# Root schema containing all assemblies
assembly_core_schema = core_schema.json_or_python_schema(
    json_schema=assembly_from_json_schema,
    python_schema=core_schema.union_schema(
        [core_schema.is_instance_schema(Assembly), assembly_from_json_schema]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_assembly,
        return_schema=assembly_model_schema,
    ),
)
