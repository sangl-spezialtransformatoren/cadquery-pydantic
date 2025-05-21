from cadquery import Shape
from pydantic_core import core_schema, CoreSchema
from io import BytesIO


def get_shape_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for Shape serialization.
    
    Example:
        >>> from pydantic import TypeAdapter
        >>> import cadquery as cq
        >>> box = cq.Workplane("XY").box(1, 1, 1).val()
        >>> TypeAdapter(cq.Shape).dump_json(box)
        '{"brep": "\nCASCADE Topology V3, (c) Open Ca...", "label": "box"}'
    """
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

    shape_schema = core_schema.typed_dict_schema(
        {
            "brep": core_schema.typed_dict_field(core_schema.str_schema()),
            "label": core_schema.typed_dict_field(core_schema.str_schema(), required=False),
        }
    )

    return core_schema.json_or_python_schema(
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
