from cadquery_pydantic import patch_cadquery
import cadquery as cq

patch_cadquery()


def test_vector_serialization(check_serialization):
    # Create a test vector
    vector = cq.Vector(1, 2, 3)

    def check_equality(v1: cq.Vector, v2: cq.Vector) -> bool:
        assert abs(v1.x - v2.x) < 1e-10
        assert abs(v1.y - v2.y) < 1e-10
        assert abs(v1.z - v2.z) < 1e-10
        return True

    check_serialization(vector, cq.Vector, check_equality)


def test_matrix_serialization(check_serialization):
    # Create a test matrix (identity matrix)
    matrix = cq.Matrix()

    def check_equality(m1: cq.Matrix, m2: cq.Matrix) -> bool:
        # Compare the matrices using transposed_list
        original_data = m1.transposed_list()
        deserialized_data = m2.transposed_list()

        # Compare each element
        assert len(original_data) == len(deserialized_data) == 16
        for orig, deser in zip(original_data, deserialized_data):
            assert abs(orig - deser) < 1e-10  # Use small epsilon for float comparison
        return True

    check_serialization(matrix, cq.Matrix, check_equality)


def test_plane_serialization(check_serialization):
    def check_equality(p1: cq.Plane, p2: cq.Plane) -> bool:
        # Check origin
        assert abs(p1.origin.x - p2.origin.x) < 1e-10
        assert abs(p1.origin.y - p2.origin.y) < 1e-10
        assert abs(p1.origin.z - p2.origin.z) < 1e-10

        # Check x-direction
        assert abs(p1.xDir.x - p2.xDir.x) < 1e-10
        assert abs(p1.xDir.y - p2.xDir.y) < 1e-10
        assert abs(p1.xDir.z - p2.xDir.z) < 1e-10

        # Check normal (z-direction)
        assert abs(p1.zDir.x - p2.zDir.x) < 1e-10
        assert abs(p1.zDir.y - p2.zDir.y) < 1e-10
        assert abs(p1.zDir.z - p2.zDir.z) < 1e-10
        return True

    # Test with XY plane
    plane = cq.Plane.XY()
    check_serialization(plane, cq.Plane, check_equality)

    # Test with a custom plane
    custom_plane = cq.Plane(origin=(1, 2, 3), xDir=(1, 1, 0), normal=(0, 0, 1))
    check_serialization(custom_plane, cq.Plane, check_equality)


def test_boundbox_serialization(check_serialization):
    def check_equality(b1: cq.BoundBox, b2: cq.BoundBox) -> bool:
        # Check min/max coordinates
        assert abs(b1.xmin - b2.xmin) < 1e-10
        assert abs(b1.xmax - b2.xmax) < 1e-10
        assert abs(b1.ymin - b2.ymin) < 1e-10
        assert abs(b1.ymax - b2.ymax) < 1e-10
        assert abs(b1.zmin - b2.zmin) < 1e-10
        assert abs(b1.zmax - b2.zmax) < 1e-10

        # Check derived properties
        assert abs(b1.xlen - b2.xlen) < 1e-10
        assert abs(b1.ylen - b2.ylen) < 1e-10
        assert abs(b1.zlen - b2.zlen) < 1e-10
        assert abs(b1.DiagonalLength - b2.DiagonalLength) < 1e-10
        return True

    # Test with a simple box
    box = cq.Workplane("XY").box(1, 1, 1).val().BoundingBox()
    check_serialization(box, cq.BoundBox, check_equality)

    # Test with a custom box
    custom_box = cq.Workplane("XY").box(2, 3, 4).val().BoundingBox()
    check_serialization(custom_box, cq.BoundBox, check_equality)


def test_location_serialization(check_serialization):
    def check_equality(l1: cq.Location, l2: cq.Location) -> bool:
        # Get transformation components
        orig_trans, orig_rot = l1.toTuple()
        new_trans, new_rot = l2.toTuple()

        # Compare translation
        assert abs(orig_trans[0] - new_trans[0]) < 1e-10
        assert abs(orig_trans[1] - new_trans[1]) < 1e-10
        assert abs(orig_trans[2] - new_trans[2]) < 1e-10

        # Compare rotation (in radians)
        assert abs(orig_rot[0] - new_rot[0]) < 1e-10
        assert abs(orig_rot[1] - new_rot[1]) < 1e-10
        assert abs(orig_rot[2] - new_rot[2]) < 1e-10
        return True

    # Test with translation + rotation
    location = cq.Location(x=1, y=2, z=3, rx=45, ry=0, rz=0)
    check_serialization(location, cq.Location, check_equality)

    # Test with a different location
    custom_location = cq.Location(x=2, y=3, z=4, rx=90, ry=0, rz=0)
    check_serialization(custom_location, cq.Location, check_equality)
