from cadquery_pydantic import patch_cadquery
from pydantic import TypeAdapter
import cadquery as cq


def test_vector_serialization():
    patch_cadquery()

    # Create a test vector
    vector = cq.Vector(1, 2, 3)

    # Serialize to JSON
    json_data = TypeAdapter(cq.Vector).dump_json(vector)

    # Deserialize back to Vector
    vector_again = TypeAdapter(cq.Vector).validate_json(json_data)

    # Compare the vectors
    assert abs(vector.x - vector_again.x) < 1e-10
    assert abs(vector.y - vector_again.y) < 1e-10
    assert abs(vector.z - vector_again.z) < 1e-10


def test_matrix_serialization():
    patch_cadquery()

    # Create a test matrix (identity matrix)
    matrix = cq.Matrix()

    # Serialize to JSON
    json_data = TypeAdapter(cq.Matrix).dump_json(matrix)

    # Deserialize back to Matrix
    matrix_again = TypeAdapter(cq.Matrix).validate_json(json_data)

    # Compare the matrices using transposed_list
    original_data = matrix.transposed_list()
    deserialized_data = matrix_again.transposed_list()

    # Compare each element
    assert len(original_data) == len(deserialized_data) == 16
    for orig, deser in zip(original_data, deserialized_data):
        assert abs(orig - deser) < 1e-10  # Use small epsilon for float comparison


def test_plane_serialization():
    patch_cadquery()

    # Create a test plane (XY plane at origin)
    plane = cq.Plane.XY()

    # Serialize to JSON
    json_data = TypeAdapter(cq.Plane).dump_json(plane)

    # Deserialize back to Plane
    plane_again = TypeAdapter(cq.Plane).validate_json(json_data)

    # Compare the planes
    # Check origin
    assert abs(plane.origin.x - plane_again.origin.x) < 1e-10
    assert abs(plane.origin.y - plane_again.origin.y) < 1e-10
    assert abs(plane.origin.z - plane_again.origin.z) < 1e-10

    # Check x-direction
    assert abs(plane.xDir.x - plane_again.xDir.x) < 1e-10
    assert abs(plane.xDir.y - plane_again.xDir.y) < 1e-10
    assert abs(plane.xDir.z - plane_again.xDir.z) < 1e-10

    # Check normal (z-direction)
    assert abs(plane.zDir.x - plane_again.zDir.x) < 1e-10
    assert abs(plane.zDir.y - plane_again.zDir.y) < 1e-10
    assert abs(plane.zDir.z - plane_again.zDir.z) < 1e-10

    # Test with a custom plane
    custom_plane = cq.Plane(
        origin=(1, 2, 3),
        xDir=(1, 1, 0),
        normal=(0, 0, 1)
    )

    # Serialize to JSON
    json_data = TypeAdapter(cq.Plane).dump_json(custom_plane)

    # Deserialize back to Plane
    plane_again = TypeAdapter(cq.Plane).validate_json(json_data)

    # Compare the planes
    # Check origin
    assert abs(custom_plane.origin.x - plane_again.origin.x) < 1e-10
    assert abs(custom_plane.origin.y - plane_again.origin.y) < 1e-10
    assert abs(custom_plane.origin.z - plane_again.origin.z) < 1e-10

    # Check x-direction
    assert abs(custom_plane.xDir.x - plane_again.xDir.x) < 1e-10
    assert abs(custom_plane.xDir.y - plane_again.xDir.y) < 1e-10
    assert abs(custom_plane.xDir.z - plane_again.xDir.z) < 1e-10

    # Check normal (z-direction)
    assert abs(custom_plane.zDir.x - plane_again.zDir.x) < 1e-10
    assert abs(custom_plane.zDir.y - plane_again.zDir.y) < 1e-10
    assert abs(custom_plane.zDir.z - plane_again.zDir.z) < 1e-10


def test_boundbox_serialization():
    patch_cadquery()

    # Create a test box and get its bounding box
    box = cq.Workplane("XY").box(1, 1, 1).val().BoundingBox()

    # Serialize to JSON
    json_data = TypeAdapter(cq.BoundBox).dump_json(box)

    # Deserialize back to BoundBox
    box_again = TypeAdapter(cq.BoundBox).validate_json(json_data)

    # Compare the bounding boxes
    # Check min/max coordinates
    assert abs(box.xmin - box_again.xmin) < 1e-10
    assert abs(box.xmax - box_again.xmax) < 1e-10
    assert abs(box.ymin - box_again.ymin) < 1e-10
    assert abs(box.ymax - box_again.ymax) < 1e-10
    assert abs(box.zmin - box_again.zmin) < 1e-10
    assert abs(box.zmax - box_again.zmax) < 1e-10

    # Check derived properties
    assert abs(box.xlen - box_again.xlen) < 1e-10
    assert abs(box.ylen - box_again.ylen) < 1e-10
    assert abs(box.zlen - box_again.zlen) < 1e-10
    assert abs(box.DiagonalLength - box_again.DiagonalLength) < 1e-10

    # Test with a custom bounding box
    custom_box = cq.Workplane("XY").box(2, 3, 4).val().BoundingBox()

    # Serialize to JSON
    json_data = TypeAdapter(cq.BoundBox).dump_json(custom_box)

    # Deserialize back to BoundBox
    box_again = TypeAdapter(cq.BoundBox).validate_json(json_data)

    # Compare the bounding boxes
    # Check min/max coordinates
    assert abs(custom_box.xmin - box_again.xmin) < 1e-10
    assert abs(custom_box.xmax - box_again.xmax) < 1e-10
    assert abs(custom_box.ymin - box_again.ymin) < 1e-10
    assert abs(custom_box.ymax - box_again.ymax) < 1e-10
    assert abs(custom_box.zmin - box_again.zmin) < 1e-10
    assert abs(custom_box.zmax - box_again.zmax) < 1e-10

    # Check derived properties
    assert abs(custom_box.xlen - box_again.xlen) < 1e-10
    assert abs(custom_box.ylen - box_again.ylen) < 1e-10
    assert abs(custom_box.zlen - box_again.zlen) < 1e-10
    assert abs(custom_box.DiagonalLength - box_again.DiagonalLength) < 1e-10


def test_location_serialization():
    patch_cadquery()

    # Create a test location (translation + rotation)
    location = cq.Location(x=1, y=2, z=3, rx=45, ry=0, rz=0)

    # Serialize to JSON
    json_data = TypeAdapter(cq.Location).dump_json(location)

    # Deserialize back to Location
    location_again = TypeAdapter(cq.Location).validate_json(json_data)

    # Compare the locations
    # Get transformation components
    orig_trans, orig_rot = location.toTuple()
    new_trans, new_rot = location_again.toTuple()

    # Compare translation
    assert abs(orig_trans[0] - new_trans[0]) < 1e-10
    assert abs(orig_trans[1] - new_trans[1]) < 1e-10
    assert abs(orig_trans[2] - new_trans[2]) < 1e-10

    # Compare rotation (in radians)
    assert abs(orig_rot[0] - new_rot[0]) < 1e-10
    assert abs(orig_rot[1] - new_rot[1]) < 1e-10
    assert abs(orig_rot[2] - new_rot[2]) < 1e-10

    # Test with a different location
    custom_location = cq.Location(x=2, y=3, z=4, rx=90, ry=0, rz=0)

    # Serialize to JSON
    json_data = TypeAdapter(cq.Location).dump_json(custom_location)

    # Deserialize back to Location
    location_again = TypeAdapter(cq.Location).validate_json(json_data)

    # Compare the locations
    # Get transformation components
    orig_trans, orig_rot = custom_location.toTuple()
    new_trans, new_rot = location_again.toTuple()

    # Compare translation
    assert abs(orig_trans[0] - new_trans[0]) < 1e-10
    assert abs(orig_trans[1] - new_trans[1]) < 1e-10
    assert abs(orig_trans[2] - new_trans[2]) < 1e-10

    # Compare rotation (in radians)
    assert abs(orig_rot[0] - new_rot[0]) < 1e-10
    assert abs(orig_rot[1] - new_rot[1]) < 1e-10
    assert abs(orig_rot[2] - new_rot[2]) < 1e-10

