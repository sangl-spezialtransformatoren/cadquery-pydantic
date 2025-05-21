from cadquery_pydantic import patch_cadquery
from pydantic import TypeAdapter
import cadquery as cq


def test_shape_serialization():
    patch_cadquery()

    # Create a test box
    box = cq.Workplane("XY").box(1, 1, 1).val()
    box.label = "test_box"

    # Serialize to JSON
    json_data = TypeAdapter(cq.Shape).dump_json(box)

    # Deserialize back to Shape
    box_again = TypeAdapter(cq.Shape).validate_json(json_data)

    # Compare the shapes
    # Check label
    assert box.label == box_again.label

    # Check volume (as a proxy for shape equality)
    assert abs(box.Volume() - box_again.Volume()) < 1e-10

    # Test with a different shape
    cylinder = cq.Workplane("XY").cylinder(1, 1).val()
    cylinder.label = "test_cylinder"

    # Serialize to JSON
    json_data = TypeAdapter(cq.Shape).dump_json(cylinder)

    # Deserialize back to Shape
    cylinder_again = TypeAdapter(cq.Shape).validate_json(json_data)

    # Compare the shapes
    # Check label
    assert cylinder.label == cylinder_again.label

    # Check volume (as a proxy for shape equality)
    assert abs(cylinder.Volume() - cylinder_again.Volume()) < 1e-10
