from cadquery_pydantic import patch_cadquery
import cadquery as cq

patch_cadquery()


def test_shape_serialization(check_serialization):
    def check_equality(s1: cq.Shape, s2: cq.Shape) -> bool:
        # Check label
        assert s1.label == s2.label
        # Check volume (as a proxy for shape equality)
        assert abs(s1.Volume() - s2.Volume()) < 1e-10
        return True

    # Test with a box
    box = cq.Workplane("XY").box(1, 1, 1).val()
    box.label = "test_box"
    check_serialization(box, cq.Shape, check_equality)

    # Test with a cylinder
    cylinder = cq.Workplane("XY").cylinder(1, 1).val()
    cylinder.label = "test_cylinder"
    check_serialization(cylinder, cq.Shape, check_equality)
