from cadquery.occ_impl.geom import Vector, Matrix, Plane, BoundBox, Location
from pydantic_core import core_schema, CoreSchema
from OCP.Bnd import Bnd_Box
from OCP.gp import gp_Pnt


def get_vector_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for Vector serialization.

    Example:
        >>> from pydantic import TypeAdapter
        >>> import cadquery as cq
        >>> vec = cq.Vector(1, 2, 3)
        >>> TypeAdapter(cq.Vector).dump_json(vec)
        '{"x": 1.0, "y": 2.0, "z": 3.0}'
    """
    vector_schema = core_schema.typed_dict_schema(
        {
            "x": core_schema.typed_dict_field(core_schema.float_schema()),
            "y": core_schema.typed_dict_field(core_schema.float_schema()),
            "z": core_schema.typed_dict_field(core_schema.float_schema()),
        }
    )

    def validate_vector(value: dict) -> Vector:
        required_keys = {"x", "y", "z"}
        if not all(key in value for key in required_keys):
            raise ValueError("Vector must contain x, y, z coordinates")
        return Vector(value["x"], value["y"], value["z"])

    def serialize_vector(vector: Vector) -> dict:
        return {"x": vector.x, "y": vector.y, "z": vector.z}

    return core_schema.json_or_python_schema(
        json_schema=core_schema.chain_schema(
            [
                vector_schema,
                core_schema.no_info_after_validator_function(validate_vector, vector_schema),
            ]
        ),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(Vector),
                core_schema.chain_schema(
                    [
                        vector_schema,
                        core_schema.no_info_after_validator_function(validate_vector, vector_schema),
                    ]
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_vector,
            return_schema=vector_schema,
            when_used="json",
        ),
    )


def get_matrix_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for Matrix serialization.

    Example:
        >>> from pydantic import TypeAdapter
        >>> import cadquery as cq
        >>> matrix = cq.Matrix()  # Identity matrix
        >>> TypeAdapter(cq.Matrix).dump_json(matrix)
        '[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]'
    """
    matrix_schema = core_schema.list_schema(
        core_schema.list_schema(core_schema.float_schema(), min_length=4, max_length=4),
        min_length=4,
        max_length=4,
    )

    def validate_matrix(value: list) -> Matrix:
        if not isinstance(value, list) or len(value) != 4:
            raise ValueError("Matrix must be a list of 4 rows")
        for row in value:
            if not isinstance(row, list) or len(row) != 4:
                raise ValueError("Each row must be a list of 4 elements")
        return Matrix(value)

    def serialize_matrix(matrix: Matrix) -> list:
        data = matrix.transposed_list()
        return [data[0:4], data[4:8], data[8:12], data[12:16]]

    return core_schema.json_or_python_schema(
        json_schema=core_schema.chain_schema(
            [
                matrix_schema,
                core_schema.no_info_after_validator_function(validate_matrix, matrix_schema),
            ]
        ),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(Matrix),
                core_schema.chain_schema(
                    [
                        matrix_schema,
                        core_schema.no_info_after_validator_function(validate_matrix, matrix_schema),
                    ]
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_matrix,
            return_schema=matrix_schema,
            when_used="json",
        ),
    )


def get_plane_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for Plane serialization.

    Example:
        >>> from pydantic import TypeAdapter
        >>> import cadquery as cq
        >>> plane = cq.Plane.XY()
        >>> TypeAdapter(cq.Plane).dump_json(plane)
        '{"origin": {"x": 0.0, "y": 0.0, "z": 0.0}, "xDir": {"x": 1.0, "y": 0.0, "z": 0.0}, "normal": {"x": 0.0, "y": 0.0, "z": 1.0}}'
    """
    vector_schema = get_vector_schema(Vector, None, None)
    model_schema = core_schema.typed_dict_schema(
        {
            "origin": core_schema.model_field(vector_schema),
            "xDir": core_schema.model_field(vector_schema),
            "normal": core_schema.model_field(vector_schema),
        }
    )

    def validate_plane(value: dict) -> Plane:
        required_keys = {"origin", "xDir", "normal"}
        if not all(key in value for key in required_keys):
            raise ValueError("Plane must contain origin, xDir, and normal vectors")
        return Plane(value["origin"], value["xDir"], value["normal"])

    def serialize_plane(plane: Plane) -> dict:
        return {
            "origin": plane.origin,
            "xDir": plane.xDir,
            "normal": plane.zDir,
        }

    return core_schema.json_or_python_schema(
        json_schema=core_schema.no_info_after_validator_function(validate_plane, model_schema),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(Plane),
                core_schema.chain_schema(
                    [
                        model_schema,
                        core_schema.no_info_after_validator_function(validate_plane, model_schema),
                    ]
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_plane,
            return_schema=model_schema,
            when_used="json",
        ),
    )


def get_boundbox_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for BoundBox serialization.
    
    Example:
        >>> from pydantic import TypeAdapter
        >>> import cadquery as cq
        >>> box = cq.Workplane("XY").box(1, 1, 1).val().BoundingBox()
        >>> TypeAdapter(cq.BoundBox).dump_json(box)
        '{"xmin": -0.5, "xmax": 0.5, "ymin": -0.5, "ymax": 0.5, "zmin": -0.5, "zmax": 0.5}'
    """
    boundbox_schema = core_schema.typed_dict_schema(
        {
            "xmin": core_schema.typed_dict_field(core_schema.float_schema()),
            "xmax": core_schema.typed_dict_field(core_schema.float_schema()),
            "ymin": core_schema.typed_dict_field(core_schema.float_schema()),
            "ymax": core_schema.typed_dict_field(core_schema.float_schema()),
            "zmin": core_schema.typed_dict_field(core_schema.float_schema()),
            "zmax": core_schema.typed_dict_field(core_schema.float_schema()),
        }
    )

    def validate_boundbox(value: dict) -> BoundBox:
        required_keys = {"xmin", "xmax", "ymin", "ymax", "zmin", "zmax"}
        if not all(key in value for key in required_keys):
            raise ValueError("BoundBox must contain xmin, xmax, ymin, ymax, zmin, zmax")
        
        bb = Bnd_Box()
        bb.Add(gp_Pnt(value["xmin"], value["ymin"], value["zmin"]))
        bb.Add(gp_Pnt(value["xmax"], value["ymax"], value["zmax"]))
        return BoundBox(bb)

    def serialize_boundbox(boundbox: BoundBox) -> dict:
        return {
            "xmin": boundbox.xmin,
            "xmax": boundbox.xmax,
            "ymin": boundbox.ymin,
            "ymax": boundbox.ymax,
            "zmin": boundbox.zmin,
            "zmax": boundbox.zmax,
        }

    return core_schema.json_or_python_schema(
        json_schema=core_schema.chain_schema(
            [
                boundbox_schema,
                core_schema.no_info_after_validator_function(validate_boundbox, boundbox_schema),
            ]
        ),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(BoundBox),
                core_schema.chain_schema(
                    [
                        boundbox_schema,
                        core_schema.no_info_after_validator_function(validate_boundbox, boundbox_schema),
                    ]
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_boundbox,
            return_schema=boundbox_schema,
            when_used="json",
        ),
    )


def get_location_schema(cls, _source, _info) -> CoreSchema:
    """Get Pydantic schema for Location serialization.
    
    Example:
        >>> from pydantic import TypeAdapter
        >>> import cadquery as cq
        >>> loc = cq.Location(x=1, y=2, z=3, rx=45, ry=0, rz=0)
        >>> TypeAdapter(cq.Location).dump_json(loc)
        '{"x": 1.0, "y": 2.0, "z": 3.0, "rx": 45.0, "ry": 0.0, "rz": 0.0}'
    """
    location_schema = core_schema.typed_dict_schema(
        {
            "x": core_schema.typed_dict_field(core_schema.float_schema()),
            "y": core_schema.typed_dict_field(core_schema.float_schema()),
            "z": core_schema.typed_dict_field(core_schema.float_schema()),
            "rx": core_schema.typed_dict_field(core_schema.float_schema()),
            "ry": core_schema.typed_dict_field(core_schema.float_schema()),
            "rz": core_schema.typed_dict_field(core_schema.float_schema()),
        }
    )

    def validate_location(value: dict) -> Location:
        required_keys = {"x", "y", "z", "rx", "ry", "rz"}
        if not all(key in value for key in required_keys):
            raise ValueError("Location must contain x, y, z, rx, ry, rz")
        
        return Location(
            x=value["x"],
            y=value["y"],
            z=value["z"],
            rx=value["rx"],
            ry=value["ry"],
            rz=value["rz"],
        )

    def serialize_location(location: Location) -> dict:
        translation, rotation = location.toTuple()
        return {
            "x": translation[0],
            "y": translation[1],
            "z": translation[2],
            "rx": rotation[0],
            "ry": rotation[1],
            "rz": rotation[2],
        }

    return core_schema.json_or_python_schema(
        json_schema=core_schema.chain_schema(
            [
                location_schema,
                core_schema.no_info_after_validator_function(validate_location, location_schema),
            ]
        ),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(Location),
                core_schema.chain_schema(
                    [
                        location_schema,
                        core_schema.no_info_after_validator_function(validate_location, location_schema),
                    ]
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_location,
            return_schema=location_schema,
            when_used="json",
        ),
    )
