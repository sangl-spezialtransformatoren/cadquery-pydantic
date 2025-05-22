from cadquery import Shape
from pydantic_core import core_schema
from io import BytesIO

# Shape schema
shape_schema = core_schema.typed_dict_schema(
    {
        "brep": core_schema.typed_dict_field(core_schema.str_schema()),
        "label": core_schema.typed_dict_field(core_schema.str_schema(), required=False),
    }
)

def validate_shape(value: dict) -> Shape:
    if "brep" not in value:
        raise ValueError("Shape must contain brep")
    
    # Create a new shape from the BREP data
    brep_stream = BytesIO(value["brep"].encode('utf-8'))
    shape = Shape.importBrep(brep_stream)
    if "label" in value:
        shape.label = value["label"]
    return shape

def serialize_shape(shape: Shape) -> dict:
    # Use BytesIO to capture the BREP output
    brep_stream = BytesIO()
    shape.exportBrep(brep_stream)
    brep_data = brep_stream.getvalue().decode('utf-8')
    brep_stream.close()
    
    result = {"brep": brep_data}
    if shape.label:
        result["label"] = shape.label
    return result

shape_core_schema = core_schema.json_or_python_schema(
    json_schema=core_schema.chain_schema(
        [
            shape_schema,
            core_schema.no_info_after_validator_function(validate_shape, shape_schema),
        ]
    ),
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(Shape),
            core_schema.chain_schema(
                [
                    shape_schema,
                    core_schema.no_info_after_validator_function(validate_shape, shape_schema),
                ]
            ),
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_shape,
        return_schema=shape_schema,
        when_used="json",
    ),
)
