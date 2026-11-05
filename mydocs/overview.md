# USD BRep overview

USD BRep is a library for creating, editing, and storing precise 3D CAD geometry
with OpenUSD. It combines the SMLib solid modeling kernel with C++ and Python APIs
and a USD schema for saving solid geometry.

BRep means **boundary representation**. A solid is described by connected faces,
edges, and vertices. Its geometry can use analytic shapes, such as planes and
cylinders, or NURBS curves and surfaces. This preserves curved geometry without
requiring a fixed triangle mesh.

You can use the library to:

- Create primitives such as boxes, spheres, cylinders, and cones.
- Combine, intersect, or subtract solids using Boolean operations.
- Add fillets and chamfers, or construct shapes with sweeps and offsets.
- Inspect topology and measure volume, area, length, and bounding boxes.
- Validate and heal BRep geometry.
- Read and write BReps in USD, and tessellate them into meshes for rendering.

The main layers are:

| Layer | Role |
| --- | --- |
| `SMLib` | Core geometry, topology, and solid modeling algorithms. |
| `SM_API` | High-level C-style C++ interface to the kernel. |
| `SM_API_USD` | Import and export between SMLib and USD `BrepArray` prims. |
| `SmPyLib` / `_omni_solid` | Python bindings used from the source checkout. |
| `usd_brep` | Packaged Python API with operation submodules. |

A typical workflow is to create or import a BRep, edit it with modeling operations,
and save it as a USD `BrepArray` to retain its geometry and topology. When a polygon
mesh is needed, tessellation produces a mesh approximation with configurable
tolerances.

Start with the [repository README](../README.md) for a quick example, the
[Python package guide](../tools/pyproject/README.md) for the packaged API, and
[BUILDING.md](../BUILDING.md) for building from source.
