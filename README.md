# CadQuery Pydantic

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Warning**: The serialization format is not yet stable. Future versions will introduce breaking changes to the JSON structure. Do not rely on the current format for long-term storage.

Monkey-patch for [CadQuery](https://github.com/CadQuery/cadquery) to add [Pydantic](https://docs.pydantic.dev/latest/) support.

### Overview

This package adds Pydantic serialization support to CadQuery objects through monkey-patching. It enables:
- Direct serialization of CadQuery objects to JSON
- Integration with Pydantic models
- Seamless API usage (FastAPI, strawberry, etc.)
- Database storage and caching (for example with Redis)

The monkey-patching approach means you can use CadQuery objects exactly as before - the serialization support is added transparently.

### Table of Contents

- [Quick Start](#quick-start)
- [Examples](#examples)
- [Implementation Details](#implementation-details)
- [Development](#development)

## Quick Start

Install the package from GitHub (a PyPI package will be available soon):

```bash
pip install git+https://github.com/sangl-spezialtransformatoren/cadquery-pydantic.git
```

Then, patch CadQuery and use CadQuery objects just like a Pydantic model:

```python
import cadquery as cq
from pydantic import BaseModel
from cadquery_pydantic import patch_cadquery

patch_cadquery()

class BoxModel(BaseModel):
    box: cq.Workplane
    name: str = "my_box"

box = cq.Workplane("XY").box(1, 1, 1)
model = BoxModel(box=box)
json_result = model.model_dump_json()
loaded_model = BoxModel.model_validate_json(json_result)
```

## Examples

### Direct Serialization with TypeAdapter

You can serialize CadQuery objects directly using `TypeAdapter`:

```python
import cadquery as cq
from pydantic import TypeAdapter
from cadquery_pydantic import patch_cadquery

patch_cadquery()

# Direct serialization of a CadQuery object
box = cq.Workplane("XY").box(1, 1, 1)
json_result = TypeAdapter(cq.Workplane).dump_json(box)

# Deserialize back to a CadQuery object
loaded_box = TypeAdapter(cq.Workplane).validate_json(json_result)
```

### Usage with FastAPI

The package works seamlessly with FastAPI (or any other framework that uses Pydantic), allowing you to directly return CadQuery objects from your endpoints:

```python
from fastapi import FastAPI
import cadquery as cq
from cadquery_pydantic import patch_cadquery

patch_cadquery()

app = FastAPI()

@app.get("/box")
def get_box() -> cq.Workplane:
    box = cq.Workplane("XY").box(1, 1, 1)
    return box  # Automatically serialized to JSON

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Implementation Details

### Supported Types

The following CadQuery types are supported for serialization:
- Geometric types (`Vector`, `Matrix`, `Plane`, `BoundBox`, `Location`)
- `Shape` (and its subclasses: `Solid`, `Face`, `Edge`, `Wire`, `Vertex`, etc.)
- `Sketch`
- `Workplane`
- `Assembly`

### Pydantic Core

Built on [pydantic_core](https://docs.pydantic.dev/latest/concepts/core_schema/) for serialization and validation. Each CadQuery type (Vector, Matrix, Plane, etc.) has its own schema definition and validation/serialization functions. For example:

```python
vector_schema = core_schema.typed_dict_schema({
    "x": core_schema.typed_dict_field(core_schema.float_schema()),
    "y": core_schema.typed_dict_field(core_schema.float_schema()),
    "z": core_schema.typed_dict_field(core_schema.float_schema()),
})
```

This schema is then added to the respective class by monkey-patching the `__get_pydantic_core_schema__` method (see `patch_cadquery` in [`src/cadquery_pydantic/__init__.py`](src/cadquery_pydantic/__init__.py)).

### Nested Structure Handling

Complex nested structures like workplanes and assemblies are flattened during serialization:

- All related workplanes/assemblies are collected into a flat dictionary
- Relationships are preserved using [JSON pointer](https://datatracker.ietf.org/doc/html/rfc6901) references
- Shared contexts are properly maintained

### Shape Serialization

CadQuery shapes (solids, faces, edges, etc.) are serialized using the OpenCascade [BREP](https://dev.opencascade.org/doc/occt-6.7.0/overview/html/occt_brep_format.html) (Boundary Representation) format via cadquery's [`exportBrep`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Shape.exportBrep) method. This format is OpenCascade's native format and keeps all topological information.

## Development

Built with modern Python tooling:

- [uv](https://github.com/astral-sh/uv) for dependency management
- [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [pre-commit](https://pre-commit.com/) for automated checks

### Getting Started

```bash
uv sync  # Install dependencies
uv run pytest  # Run tests
uv run ruff check  # Check code
uv run ruff format  # Format code
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks before each commit:

```bash
pre-commit install
```

The hooks will run ruff checks and formatting on staged files.
