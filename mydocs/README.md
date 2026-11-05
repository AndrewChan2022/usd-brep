# SMLib subsystem handbook

This handbook explains the geometry, algorithms, implementation paths, and C++
integration concerns behind SMLib. Start with the overview, then follow the
foundation chapters before studying modeling operations. The 28 subsystem
chapters supplement the existing NURBS and fitting guides.

The source baseline for the new chapters is upstream
`3fd5b9548d19aa8c12c29bc9637a96d42a06f8a5`. Source links are relative to this
checkout; recheck them after rebasing. Mathematical examples and application
design suggestions are distinguished from observed implementation behavior.

## Introduction and spline mathematics

| Guide | What it explains |
| --- | --- |
| [Project overview](overview.md) | Where SMLib fits in USD BRep |
| [Feature and architecture map](smlib.md) | Layers, capabilities, and CAD workflows |
| [B-splines and NURBS](nurbs.md) | Basis functions, rational geometry, knots, degree/order, representation editing |
| [Interpolation and approximation](fitting.md) | Parameterization, interpolation, least squares, curve and surface fitting |

## Foundations

| Guide | What it explains |
| --- | --- |
| [Topology](topology.md) | Entities, oriented uses, regions, seams, Euler-style edits, traversal |
| [Euler operations](euler.md) | Classical operators, incidence edits, edge/face splitting, loop bridging, inverse operations and validation |
| [Geometry](geometry.md) | Analytic, spline and procedural representations; domains and placements |
| [Tolerances](tolerances.md) | Scale, conditioning, error measures, effective tolerances |
| [Evaluation](evaluation.md) | Points, derivatives, normals, curvature, STEP parameter conventions |
| [Spatial indexing](spatial-indexing.md) | Bounds, parameter trees, spatial trees, pruning and caches |
| [Numerical solvers](solvers.md) | Local iteration, global subdivision, convergence and solution identity |

## Geometric analysis

| Guide | What it explains |
| --- | --- |
| [Intersections](intersections.md) | Points, curves, overlaps, tracing and trimmed-domain handling |
| [Queries and measurements](queries.md) | Closest points, boundary distance, containment, bounds, mass properties |
| [Projection and trimming](projection-trimming.md) | Directional projection, dropping, lifting, UV branches and trim regions |
| [Sections and cuts](sections.md) | Planar sections, contour ordering, holes, half-spaces and caps |

## Solid operations and display

| Guide | What it explains |
| --- | --- |
| [Booleans](booleans.md) | Intersection insertion, classification, selection, reconstruction and consumption |
| [Fillets, chamfers and blends](blend.md) | Contact geometry, sizing policies, corners, continuity and removal |
| [Tessellation](tessellation.md) | Boundary sampling, face meshing, error controls and partial-output diagnostics |
| [Silhouettes and visibility](silhouettes-visibility.md) | View-dependent curves, tracing, hidden curves and picking |

## Construction and editing

| Guide | What it explains |
| --- | --- |
| [Primitives and sweeps](primitives-sweeps.md) | Extrusion, revolution, draft, path frames, caps and solid construction |
| [Lofts and patches](lofts-patches.md) | Section correspondence, compatible splines, skins and boundary constraints |
| [Offsets and shells](offsets-shells.md) | Normal offsets, curvature limits, joins, openings and ownership |
| [Healing and stitching](healing-stitching.md) | Gap measurement, staged repair, sewing and independent validation |
| [Editing and feature removal](editing.md) | Geometry/topology changes, reconstruction, selections and application undo |
| [Local operations (LOP)](local-operations.md) | Selected support replacement, UV compatibility, edge reconstruction, face moves and radius changes |
| [Deformation](deformation.md) | Volume maps, bending, twisting, Jacobians and consistency |

## Runtime and interchange

| Guide | What it explains |
| --- | --- |
| [Runtime and ownership](runtime.md) | Contexts, lifetime, mutation, notifications, caches and concurrency |
| [Validation and diagnostics](validation-diagnostics.md) | Structural versus geometric checks, statuses and minimal reproductions |
| [Polygon BRep](polygon-brep.md) | Mesh representation, polygon booleans, signed measurements and decimation |
| [Assemblies and attributes](assemblies-attributes.md) | Instances, placements, copy behavior and topology identity |
| [Native persistence](native-io.md) | BRep/part loading, reconstruction, cleanup and round-trip checks |
| [USD interchange](usd-interchange.md) | Runtime-to-packed conversion, BrepArray, mesh output and OCCT boundaries |

## Practical reading paths

- **Build a bracket:** topology → primitives/sweeps → booleans → fillets → tessellation.
- **Import and repair a part:** native I/O or USD → tolerances → validation → healing/stitching.
- **Build a free-form cover:** NURBS → fitting → lofts/patches → projection/trimming → offsets/shells.
- **Measure clearance:** evaluation → solvers → queries; distinguish boundary distance from solid overlap.
- **Integrate into a C++ CAD application:** runtime → assemblies/attributes → editing → validation → tessellation.
- **Implement a direct face edit:** topology → projection/trimming → local operations → validation → editing.
- **Understand boundary reconstruction:** topology → Euler operations → intersections → booleans.

Qt UI, sketch constraints, parametric regeneration, persistent naming, and an
application document/undo model remain separate application architecture topics.
Kernel class names do not establish that those complete systems are provided.

## Diagrams, examples, and reproducibility

The chapters contain LaTeX mathematics and Mermaid architecture/workflow diagrams.
Seven additional SVG illustrations have PNG alternatives alongside them in
[assets/handbook](assets/handbook/). They illustrate mathematical constructions,
not captured SMLib results. Regenerate them from the repository root with:

```powershell
uv run --no-project --with numpy --with matplotlib python mydocs/assets/handbook/generate_figures.py
```

The [generator](assets/handbook/generate_figures.py) checks analytic invariants
for the plotted examples. The existing NURBS/fitting assets keep their own generators.

The [worked 3D fillet examples](blend.md#8-worked-3d-examples)
add two illustrations: a block before/after rounding one edge and three fillets
meeting at a corner patch. Their [separate generator](assets/fillets/generate_figures.py)
checks the analytic geometry; these illustrations are not kernel execution results.

```powershell
uv run --no-project --with numpy --with matplotlib python mydocs/assets/fillets/generate_figures.py
```

The [local-operation examples](local-operations.md#6-worked-3d-constructions)
add a three-panel illustration of a block, a raised top, and a tilted top.
Their [generator](assets/local-operations/generate_figures.py) checks planar
geometry and volumes; these are analytic references rather than kernel results.

```powershell
uv run --no-project --with numpy --with matplotlib python mydocs/assets/local-operations/generate_figures.py
```

The [Euler-operation guide](euler.md) adds before/after schematics for edge
subdivision, face splitting, and ring bridging. Its
[generator](assets/euler/generate_figures.py) verifies the illustrated entity
counts and the box-imprint accounting:

```powershell
uv run --no-project --with matplotlib python mydocs/assets/euler/generate_figures.py
```

Native C++ fragments in the new guides were reviewed against this checkout's
signatures; they were **not compiled or executed for this documentation change**.
Other code blocks are explicitly application pseudocode or source walkthroughs.
The existing [SM_API example](../Examples/SM_API/README.md) and
[STEP derivative example](../Examples/SMLib/README.md) provide standalone native
entry points and their own validation notes. No new kernel test run is claimed.

Check the handbook's local links, fences, display-math delimiters, source
baselines, and figure files with:

```powershell
uv run --no-project python mydocs/tools/check_docs.py
```

The [documentation plan](documentation-plan.md) records scope, review criteria,
coverage boundaries, and publication progress.

For Mermaid parsing and LaTeX rendering checks, install JavaScript dependencies
in a temporary directory, then use the additional checker:

```powershell
$docCheckDir = Join-Path $env:TEMP 'usd-brep-doc-check'
npm.cmd install --prefix $docCheckDir --no-audit --no-fund mermaid jsdom katex
node mydocs/tools/check_diagrams.mjs (Join-Path $docCheckDir 'node_modules')
```

This checks syntax with Mermaid and KaTeX; it does not replace visual review
or prove that every Markdown viewer uses the same rendering configuration.
