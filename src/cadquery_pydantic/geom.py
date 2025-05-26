from cadquery.occ_impl.geom import Vector, Matrix, Plane, BoundBox, Location
from pydantic_core import core_schema
from OCP.Bnd import Bnd_Box
from OCP.gp import gp_Pnt

# Vector schema
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


vector_from_json_schema = core_schema.chain_schema(
    [
        vector_schema,
        core_schema.no_info_plain_validator_function(validate_vector),
    ]
)

vector_core_schema = core_schema.json_or_python_schema(
    json_schema=vector_from_json_schema,
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(Vector),
            vector_from_json_schema,
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_vector,
        return_schema=vector_schema,
    ),
)

# Matrix schema
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


matrix_from_json_schema = core_schema.chain_schema(
    [
        matrix_schema,
        core_schema.no_info_plain_validator_function(validate_matrix),
    ]
)

matrix_core_schema = core_schema.json_or_python_schema(
    json_schema=matrix_from_json_schema,
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(Matrix),
            matrix_from_json_schema,
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_matrix,
        return_schema=matrix_schema,
    ),
)


# Plane schema
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


plane_schema = core_schema.typed_dict_schema(
    {
        "origin": core_schema.model_field(vector_core_schema),
        "xDir": core_schema.model_field(vector_core_schema),
        "normal": core_schema.model_field(vector_core_schema),
    }
)

plane_from_json_schema = core_schema.chain_schema(
    [
        plane_schema,
        core_schema.no_info_plain_validator_function(validate_plane),
    ]
)

plane_core_schema = core_schema.json_or_python_schema(
    json_schema=plane_from_json_schema,
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(Plane),
            plane_from_json_schema,
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_plane,
        return_schema=plane_schema,
    ),
)

# BoundBox schema
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


boundbox_from_json_schema = core_schema.chain_schema(
    [
        boundbox_schema,
        core_schema.no_info_plain_validator_function(validate_boundbox),
    ]
)

boundbox_core_schema = core_schema.json_or_python_schema(
    json_schema=boundbox_from_json_schema,
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(BoundBox),
            boundbox_from_json_schema,
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_boundbox,
        return_schema=boundbox_schema,
    ),
)

# Location schema
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
    trans, rot = location.toTuple()
    return {
        "x": trans[0],
        "y": trans[1],
        "z": trans[2],
        "rx": rot[0],
        "ry": rot[1],
        "rz": rot[2],
    }


location_from_json_schema = core_schema.chain_schema(
    [
        location_schema,
        core_schema.no_info_plain_validator_function(validate_location),
    ]
)

location_core_schema = core_schema.json_or_python_schema(
    json_schema=location_from_json_schema,
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(Location),
            location_from_json_schema,
        ]
    ),
    serialization=core_schema.plain_serializer_function_ser_schema(
        serialize_location,
        return_schema=location_schema,
    ),
)
