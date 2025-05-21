import pytest
from pydantic import TypeAdapter
import cadquery as cq
from cadquery.cq import CQContext
from cadquery_pydantic import patch_cadquery


def test_cqcontext_serialization():
    """Test serialization of CQContext."""
    patch_cadquery()
    
    # Create a context with some data
    ctx = CQContext()
    ctx.pendingWires = []
    ctx.pendingEdges = []
    ctx.tolerance = 0.001
    ctx.tags = {}
    ctx.firstPoint = None  # firstPoint is required but can be None
    
    # Test serialization
    json_data = TypeAdapter(CQContext).dump_json(ctx)
    assert isinstance(json_data, bytes)
    
    # Test deserialization
    new_ctx = TypeAdapter(CQContext).validate_json(json_data)
    assert isinstance(new_ctx, CQContext)
    assert new_ctx.pendingWires == []
    assert new_ctx.pendingEdges == []
    assert new_ctx.tolerance == 0.001
    assert new_ctx.tags == {}
    assert new_ctx.firstPoint is None


def test_cqcontext_with_wires_and_edges():
    """Test CQContext with wires and edges."""
    patch_cadquery()
    
    # Create a context with some shapes
    ctx = CQContext()
    wire = cq.Workplane("XY").rect(1, 1).val()
    edge = cq.Workplane("XY").lineTo(1, 1).val()
    ctx.pendingWires = [wire]
    ctx.pendingEdges = [edge]
    ctx.tolerance = 0.001
    ctx.tags = {}
    ctx.firstPoint = None  # firstPoint is required but can be None
    
    # Test serialization
    json_data = TypeAdapter(CQContext).dump_json(ctx)
    assert isinstance(json_data, bytes)
    
    # Test deserialization
    new_ctx = TypeAdapter(CQContext).validate_json(json_data)
    assert isinstance(new_ctx, CQContext)
    assert len(new_ctx.pendingWires) == 1
    assert len(new_ctx.pendingEdges) == 1
    assert new_ctx.tolerance == 0.001
    assert new_ctx.tags == {}
    assert new_ctx.firstPoint is None


def test_cqcontext_with_first_point():
    """Test CQContext with firstPoint."""
    patch_cadquery()
    
    # Create a context with firstPoint
    ctx = CQContext()
    ctx.pendingWires = []
    ctx.pendingEdges = []
    ctx.firstPoint = cq.Vector(1, 2, 3)
    ctx.tolerance = 0.001
    ctx.tags = {}
    
    # Test serialization
    json_data = TypeAdapter(CQContext).dump_json(ctx)
    assert isinstance(json_data, bytes)
    
    # Test deserialization
    new_ctx = TypeAdapter(CQContext).validate_json(json_data)
    assert isinstance(new_ctx, CQContext)
    assert new_ctx.firstPoint == cq.Vector(1, 2, 3)
    assert new_ctx.tolerance == 0.001
    assert new_ctx.tags == {}


def test_cqcontext_validation():
    """Test CQContext validation."""
    patch_cadquery()
    
    # Test missing required fields
    with pytest.raises(ValueError):
        TypeAdapter(CQContext).validate_json('{"pendingWires": [], "pendingEdges": [], "firstPoint": null}')
    
    # Test invalid tolerance type
    with pytest.raises(ValueError):
        TypeAdapter(CQContext).validate_json('{"pendingWires": [], "pendingEdges": [], "tolerance": "invalid", "tags": {}, "firstPoint": null}')
    
    # Test invalid firstPoint type
    with pytest.raises(ValueError):
        TypeAdapter(CQContext).validate_json('{"pendingWires": [], "pendingEdges": [], "tolerance": 0.001, "tags": {}, "firstPoint": "invalid"}')


def test_cqcontext_roundtrip():
    """Test roundtrip serialization of CQContext."""
    patch_cadquery()
    
    # Create a context with all fields
    ctx = CQContext()
    wire = cq.Workplane("XY").rect(1, 1).val()
    edge = cq.Workplane("XY").lineTo(1, 1).val()
    ctx.pendingWires = [wire]
    ctx.pendingEdges = [edge]
    ctx.firstPoint = cq.Vector(1, 2, 3)
    ctx.tolerance = 0.001
    ctx.tags = {}
    
    # Test roundtrip
    json_data = TypeAdapter(CQContext).dump_json(ctx)
    new_ctx = TypeAdapter(CQContext).validate_json(json_data)
    
    # Compare the objects directly
    assert len(new_ctx.pendingWires) == len(ctx.pendingWires)
    assert len(new_ctx.pendingEdges) == len(ctx.pendingEdges)
    assert new_ctx.tolerance == ctx.tolerance
    assert new_ctx.tags == ctx.tags
    assert new_ctx.firstPoint == ctx.firstPoint
