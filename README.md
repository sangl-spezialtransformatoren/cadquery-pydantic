# CadQuery Pydantic

Monkey-patch for CadQuery to add Pydantic support.

## Installation

```bash
pip install cadquery-pydantic
```

## Usage


```python
from cadquery_pydantic import patch_cadquery

patch_cadquery()

import cadquery as cq

box = cq.Workplane("XY").box(1, 1, 1)

json_result = TypeAdapter(cq.Workplane).dump_json(box)
```

