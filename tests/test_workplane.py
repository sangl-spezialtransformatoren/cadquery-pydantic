from pydantic import TypeAdapter
import cadquery as cq
from cadquery_pydantic import patch_cadquery


def test_workplane_serialization():
    """Test serialization of a Workplane."""
    patch_cadquery()
    
    # Create a simple workplane
    wp = cq.Workplane("XY")
    
    # Serialize to JSON
    adapter = TypeAdapter(cq.Workplane)
    json_data = adapter.dump_json(wp)
    
    # Deserialize from JSON
    wp2 = adapter.validate_json(json_data)
    
    # Check that the deserialized workplane has the same properties
    assert len(wp2.objects) == 0
    assert wp2.plane.origin.x == 0
    assert wp2.plane.origin.y == 0
    assert wp2.plane.origin.z == 0
    assert wp2.parent is None
    assert wp2._tag is None


def test_workplane_with_objects():
    """Test serialization of a Workplane with objects."""
    patch_cadquery()
    
    # Create a workplane with a box
    wp = cq.Workplane("XY").box(1, 1, 1)
    
    # Serialize to JSON
    adapter = TypeAdapter(cq.Workplane)
    json_data = adapter.dump_json(wp)
    
    # Deserialize from JSON
    wp2 = adapter.validate_json(json_data)
    
    # Check that the deserialized workplane has the box
    assert len(wp2.objects) == 1
    assert isinstance(wp2.objects[0], cq.Shape)


def test_workplane_with_tag():
    """Test serialization of a Workplane with a tag."""
    patch_cadquery()
    
    # Create a workplane with a tag
    wp = cq.Workplane("XY")
    wp._tag = "test_tag"
    
    # Serialize to JSON
    adapter = TypeAdapter(cq.Workplane)
    json_data = adapter.dump_json(wp)
    
    # Deserialize from JSON
    wp2 = adapter.validate_json(json_data)
    
    # Check that the tag is preserved
    assert wp2._tag == "test_tag"


def test_workplane_with_parent():
    """Test serialization of a Workplane with a parent."""
    patch_cadquery()
    
    # Create a parent workplane
    parent = cq.Workplane("XY")
    
    # Create a child workplane
    child = cq.Workplane("XZ").box(1, 1, 1)
    child.parent = parent
    
    # Serialize to JSON
    adapter = TypeAdapter(cq.Workplane)
    json_data = adapter.dump_json(child)
    
    # Deserialize from JSON
    child2 = adapter.validate_json(json_data)
    
    # Check that the parent is preserved
    assert child2.parent is not None
    assert isinstance(child2.parent, cq.Workplane) 