from cadquery_pydantic import patch_cadquery
from pydantic import TypeAdapter
import cadquery as cq
from cadquery.sketch import Constraint
import pytest


def test_constraint_serialization():
    """Test constraint serialization for different types."""
    patch_cadquery()

    # Create test shapes
    line1 = cq.Workplane("XY").lineTo(1, 1).val()
    line2 = cq.Workplane("XY").moveTo(5, 0).lineTo(6, 1).val()

    # Test different constraint types
    c0 = Constraint(tags=("line1",), args=(line1,), kind="Fixed", param=None)
    c1 = Constraint(
        tags=("line1", "line2"),
        args=(line1, line2),
        kind="Distance",
        param=(None, None, 5.0),
    )
    c2 = Constraint(
        tags=("line1",), args=(line1,), kind="Orientation", param=(1.0, 1.0)
    )
    constraints = [c0, c1, c2]

    for constraint in constraints:
        # Test roundtrip
        json_data = TypeAdapter(Constraint).dump_json(constraint)
        new_constraint = TypeAdapter(Constraint).validate_json(json_data)

        # Compare objects
        assert new_constraint.tags == constraint.tags
        assert len(new_constraint.args) == len(constraint.args)
        assert new_constraint.kind == constraint.kind

        # Compare params with appropriate precision
        if constraint.kind in ("Angle", "ArcAngle"):
            assert abs(new_constraint.param - constraint.param) < 1e-10
        else:
            assert new_constraint.param == constraint.param


def test_constraint_validation():
    """Test constraint validation."""
    patch_cadquery()

    # Test invalid cases
    with pytest.raises(ValueError):
        TypeAdapter(Constraint).validate_json(
            '{"tags": ["line1"], "args": [], "kind": "InvalidKind", "param": null}'
        )

    with pytest.raises(ValueError):
        TypeAdapter(Constraint).validate_json(
            '{"tags": ["line1"], "args": [], "kind": "Angle", "param": "invalid"}'
        )


def test_sketch_serialization():
    """Test sketch serialization."""
    patch_cadquery()

    # Create a sketch with various components
    sketch = cq.Sketch()

    # Add some edges
    line = cq.Workplane("XY").lineTo(1, 1).val()
    circle_edge = cq.Workplane("XY").circle(1).val().Edges()[0]
    sketch._edges = [line, circle_edge]

    # Add some constraints
    sketch._constraints = [
        Constraint(tags=("line1",), args=(line,), kind="Fixed", param=None),
        Constraint(tags=("circle1",), args=(circle_edge,), kind="Radius", param=1.0),
    ]

    # Add some tags
    sketch._tags = {
        "line": [(line, cq.Location())],
        "circle": [(circle_edge, cq.Location())],
    }

    # Test serialization
    json_data = TypeAdapter(cq.Sketch).dump_json(sketch)
    new_sketch = TypeAdapter(cq.Sketch).validate_json(json_data)

    # Compare objects
    assert len(new_sketch._edges) == len(sketch._edges)
    assert len(new_sketch._constraints) == len(sketch._constraints)
    assert len(new_sketch._tags) == len(sketch._tags)

    # Compare constraints
    for c1, c2 in zip(new_sketch._constraints, sketch._constraints):
        assert c1.tags == c2.tags
        assert len(c1.args) == len(c2.args)
        assert c1.kind == c2.kind
        assert c1.param == c2.param
