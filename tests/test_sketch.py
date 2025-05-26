from cadquery_pydantic import patch_cadquery
from pydantic import TypeAdapter
import cadquery as cq
from cadquery.sketch import Constraint
import pytest

patch_cadquery()


def test_constraint_serialization(check_serialization):
    """Test constraint serialization for different types."""
    # Create test shapes
    line1 = cq.Workplane("XY").lineTo(1, 1).val()
    line2 = cq.Workplane("XY").moveTo(5, 0).lineTo(6, 1).val()

    def check_equality(c1: Constraint, c2: Constraint) -> bool:
        assert c1.tags == c2.tags
        assert len(c1.args) == len(c2.args)
        assert c1.kind == c2.kind

        # Compare params with appropriate precision
        if c1.kind in ("Angle", "ArcAngle"):
            assert abs(c1.param - c2.param) < 1e-10
        else:
            assert c1.param == c2.param
        return True

    # Test different constraint types
    c0 = Constraint(tags=("line1",), args=(line1,), kind="Fixed", param=None)
    check_serialization(c0, Constraint, check_equality)

    c1 = Constraint(
        tags=("line1", "line2"),
        args=(line1, line2),
        kind="Distance",
        param=(None, None, 5.0),
    )
    check_serialization(c1, Constraint, check_equality)

    c2 = Constraint(
        tags=("line1",), args=(line1,), kind="Orientation", param=(1.0, 1.0)
    )
    check_serialization(c2, Constraint, check_equality)


def test_constraint_validation():
    """Test constraint validation."""
    with pytest.raises(ValueError):
        TypeAdapter(Constraint).validate_json(
            '{"tags": ["line1"], "args": [], "kind": "InvalidKind", "param": null}'
        )

    with pytest.raises(ValueError):
        TypeAdapter(Constraint).validate_json(
            '{"tags": ["line1"], "args": [], "kind": "Angle", "param": "invalid"}'
        )


def test_sketch_serialization(check_serialization):
    """Test sketch serialization."""
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

    def check_equality(s1: cq.Sketch, s2: cq.Sketch) -> bool:
        assert len(s1._edges) == len(s2._edges)
        assert len(s1._constraints) == len(s2._constraints)
        assert len(s1._tags) == len(s2._tags)

        # Compare constraints
        for c1, c2 in zip(s1._constraints, s2._constraints):
            assert c1.tags == c2.tags
            assert len(c1.args) == len(c2.args)
            assert c1.kind == c2.kind
            assert c1.param == c2.param
        return True

    check_serialization(sketch, cq.Sketch, check_equality)
