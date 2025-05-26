import cadquery as cq
from cadquery_pydantic import patch_cadquery

patch_cadquery()


def test_workplane_serialization(check_serialization):
    """Test serialization of a Workplane."""
    # Create a simple workplane
    wp = cq.Workplane("XY")

    def check_equality(w1: cq.Workplane, w2: cq.Workplane) -> bool:
        assert len(w2.objects) == 0
        assert w2.plane.origin.x == 0
        assert w2.plane.origin.y == 0
        assert w2.plane.origin.z == 0
        assert w2.parent is None
        assert w2._tag is None
        return True

    check_serialization(wp, cq.Workplane, check_equality)


def test_workplane_with_objects(check_serialization):
    """Test serialization of a Workplane with objects."""
    # Create a workplane with a box
    wp = cq.Workplane("XY").box(1, 1, 1)

    def check_equality(w1: cq.Workplane, w2: cq.Workplane) -> bool:
        assert len(w2.objects) == 1
        assert isinstance(w2.objects[0], cq.Shape)
        return True

    check_serialization(wp, cq.Workplane, check_equality)


def test_workplane_with_tag(check_serialization):
    """Test serialization of a Workplane with a tag."""
    # Create a workplane with a tag
    wp = cq.Workplane("XY")
    wp._tag = "test_tag"

    def check_equality(w1: cq.Workplane, w2: cq.Workplane) -> bool:
        assert w2._tag == "test_tag"
        return True

    check_serialization(wp, cq.Workplane, check_equality)


def test_workplane_with_parent(check_serialization):
    """Test serialization of a Workplane with a parent."""
    # Create a parent workplane
    parent = cq.Workplane("XY")

    # Create a child workplane
    child = cq.Workplane("XZ").box(1, 1, 1)
    child.parent = parent

    def check_equality(w1: cq.Workplane, w2: cq.Workplane) -> bool:
        assert w2.parent is not None
        assert isinstance(w2.parent, cq.Workplane)
        return True

    check_serialization(child, cq.Workplane, check_equality)
