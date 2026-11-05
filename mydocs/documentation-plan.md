# SMLib subsystem documentation plan

## 1. Objective and current state

Build a source-grounded handbook for understanding and using SMLib from a C++ CAD
application. Each subsystem guide should explain the mathematics, the actual
implementation, the API contract, and a practical modeling workflow at a depth
comparable to [nurbs.md](nurbs.md) and [fitting.md](fitting.md).

The existing documents have different roles:

| Document | Role | State |
| --- | --- | --- |
| [overview.md](overview.md) | Short project introduction | Existing |
| [arch.md](arch.md) | Broad feature and architecture map | Linked to the subsystem handbook |
| [nurbs.md](nurbs.md) | Spline representation, evaluation, and representation editing | Existing |
| [fitting.md](fitting.md) | Interpolation and approximation | Existing |
| [README.md](README.md) | Handbook index and reading paths | Written |
| This plan | Scope, order, evidence requirements, and progress | Delivery record added below |

The working branch is `chen-doc`; `main` follows the upstream NVIDIA repository.
All 26 subsystem guides have now been written and source-reviewed. The roadmap
below preserves the agreed scope; the delivery record at the end states the
reviewed paths, example validation, limitations, and commits. Source review is
not a full runtime audit of every branch of every subsystem.

The later [local-operations chapter](local-operations.md) and
[Euler-operations chapter](euler.md) bring the handbook to 28 subsystem guides.
The original 26-guide roadmap and delivery ledger below retain their
historical scope.

Interpretation of the requested names: `bool` means solid BRep booleans, `iset`
means intersections, `eval` means geometric evaluation, `section` means planar
cross-sections and their relationship to cutting, and `tess` means tessellation.
Polygon booleans receive separate coverage because they use a different model.

## 2. Scope and document boundaries

Organize by engineering responsibility, rather than producing one document per
header or one enormous document containing every operation.

| Topic | Owns | Links elsewhere for |
| --- | --- | --- |
| Topology | Entities, oriented uses, incidence, regions, adjacency, Euler-style edits | Numerical surface/curve representation; full boolean algorithm |
| Evaluation | Values and derivatives at known parameters, normals, continuity, parameter conventions | Closest-point searches; fitting |
| Solvers | Iteration, subdivision, bounds, convergence and solution identity | The complete modeling operations that invoke them |
| Intersections | Common points, curves, and overlap regions of geometry | Solid selection and reconstruction in booleans |
| Queries | Closest points, distance, containment/classification, bounds, measurements | Raw derivative implementation; full intersector implementation |
| Projection and trimming | Mapping curves to/from a surface, parameter seams, constructing trimmed regions | General intersection theory; complete healing pipeline |
| Sections | Plane/body intersections, contour assembly, cuts and caps | General surface/surface intersection and arbitrary booleans |
| Booleans | Splitting, relating, classifying, selecting, and reconstructing solid topology | Repeating the foundational topology and intersection chapters |
| Fillets, chamfers, blends | Transition geometry, spine/contact construction, corners, topology replacement | Generic solver machinery and all surface construction methods |
| Tessellation | Sampling and meshing a trimmed BRep, shared boundaries, normals, mesh quality | Mesh booleans; USD persistence |

Each guide must be understandable on its own with a short prerequisite recap,
but detailed shared theory should have one home. For example, `evaluation.md`
will link to NURBS basis derivations rather than reproduce them.

## 3. Delivery order

The first three phases cover the requested core features and their prerequisites.
Later phases extend the same treatment to construction, repair, infrastructure,
and integration. Complete and review one guide before starting the next; do not
create shallow placeholder chapters merely to fill the table.

The following 19 entries are the baseline roadmap. The coverage audit in
Section 10 adds seven guides and specifies where they enter these phases,
bringing the current target to **26 new guides**, in addition to the existing
documents. Baseline numbers identify entries; the insertion schedule in Section
10 determines their revised delivery order.

### Phase 1 — foundations

| Order / file | Detailed scope | Required illustrations and examples |
| --- | --- | --- |
| 1. `topology.md` | BRep/region/shell/face/loop/edge/vertex relationships; use objects, mate/radial links and orientations; geometry attachments; manifold and non-manifold cases; seams, poles, wires and sheets; topology construction and Euler-style operations; defining versus derived data | Object/incidence diagram; edge-use orientation diagram; seam and non-manifold examples; safe C++ traversal of a simple body; worked split/join topology sketch |
| 2. `evaluation.md` | Curve/surface parameter domains; points, derivatives, tangent and normal conventions; analytic versus spline dispatch; ordinary versus STEP parameters; one-sided derivatives; curvature and regularity; boundary and pole behavior | Parameter-to-space mapping; tangent/normal and curvature illustration; derivative layout; C++ evaluation with known expected results |
| 3. `solvers.md` | Local 1D/N-dimensional solving; residuals/Jacobians; global subdivision and pruning; boundary candidates; singularity/tangency; termination and found-solution flags; duplicate solutions; caller-specific tolerances | Local iteration diagram; subdivision tree; tangent versus transverse examples; traced solver use from an actual geometric operation |

### Phase 2 — geometric analysis

| Order / file | Detailed scope | Required illustrations and examples |
| --- | --- | --- |
| 4. `intersections.md` | Curve/curve, curve/surface, surface/surface, face/face and BRep boundaries; analytic dispatch where present; candidate generation, solving/tracing, trimming and output assembly; points, curves and coincident cases | Intersection taxonomy; 3D curve and two UV traces; actual call graph; transverse, tangent, coincident and disjoint cases |
| 5. `queries.md` | Closest point and distance; constrained versus underlying geometry; local versus global candidates; classification and relationship; bounds; length, area, volume, centroid and mass properties; topology lookup | Closest-point stationary and boundary candidates; containment without boundary crossing; ordinary/tight bounds; measurable C++ examples |
| 6. `projection-trimming.md` | Directional projection versus closest-point/drop operations; lifting UV curves; 3D/UV correspondence; periodic seams; trim-loop construction and orientation; splitting and failures | 3D-to-UV mapping; seam crossing; inner/outer trim loops; projection-and-trim workflow |
| 7. `sections.md` | Plane equation and coordinate frame; section curves versus connected contours; open sheets, multiple components and holes; tangencies and coplanar faces; contour ordering; section query versus destructive cut and cap | Section through a hollow body; nested contours; touch/coplanarity cases; section query and cut compared on the same part |

### Phase 3 — solid operations and display

| Order / file | Detailed scope | Required illustrations and examples |
| --- | --- | --- |
| 8. `booleans.md` | Set and regularized-solid theory where applicable; union/intersection/difference; candidate pairs, intersection insertion, relationship/classification, selection and assembly; coincident/tangent cases; manifold/non-manifold dispatch; operand consumption and failure state | Region selection truth table; before/split/classify/after sequence; call graph; plate with cutter, containment and touching cases |
| 9. `blend.md` | Distinguish the three operations; rolling-ball/offset/contact theory where applicable; continuity and cross-section choices; constant/variable radii; spine, trimming, corners and patches; blend creation versus edge replacement; removal; feasibility and failure diagnosis | Radius/contact construction; chamfer distances; G0/G1/G2 comparison; multi-edge corner; actual executive/solver workflow; bracket example |
| 10. `tessellation.md` | Curve sampling; face-domain meshing; trim constraints; shared-edge consistency; seams/poles; chord and angular controls; triangle quality; normal handling; PolyBrep output and ownership; preview versus final display | Chord-error diagram; UV mesh mapped to a face; shared-edge crack example; quality comparison; C++ BRep-to-mesh workflow |

Milestone: all explicitly requested subject areas have detailed coverage, with
cross-links to the numerical and topology foundations.

### Phase 4 — construction and editing

| Order / file | Scope and representative CAD scenario |
| --- | --- |
| 11. `primitives-sweeps.md` | Analytic construction, extrusion, revolution, draft, path sweeps and frames; surface versus solid construction; profile orientation, self-intersection and caps; bracket, turned part and pipe |
| 12. `lofts-patches.md` | Ruled surfaces, skins/lofts and supported boundary patches; section correspondence, compatibility, knot/degree alignment and continuity; duct transition and cover |
| 13. `offsets-shells.md` | Curve/surface offsets, solid offset and shelling; normal direction, curvature singularities, self-intersections, joins and topology changes; thin-walled housing |
| 14. `healing-stitching.md` | Geometric gaps versus topology defects; stitching, orientation, tolerance decisions, seam/pole repair and validation; imported disconnected shell |
| 15. `editing.md` | Local versus global edits; transforms, representation conversion and supported direct edits; dependency updates, identity changes and invalidated views; undo-friendly application workflows |

### Phase 5 — supporting systems and integration

| Order / file | Scope and reason for a separate guide |
| --- | --- |
| 16. `runtime.md` | Context selection and lifetime, allocations, ownership, notifications, caches and concurrency contracts; supports reliable C++ integration across all operations |
| 17. `validation-diagnostics.md` | Pointer checks versus geometric validity, validator coverage, tolerance reports, status/trace interpretation, minimal reproductions and supported diagnostic tools |
| 18. `polygon-brep.md` | PolyBrep structure, adjacency, mesh queries, supported polygon booleans and limitations; separate from the exact BRep model |
| 19. `usd-interchange.md` | Runtime geometry/topology to serialized data and USD BrepArray; mesh export alternative; supported round trips and representation limits; OCCT translation as a bounded subsection or later separate guide |

Introduce context, ownership, tolerance and validity facts in every earlier guide
as needed. Their placement in Phase 5 does not justify deferring those checks.
Qt application architecture, UI implementation, CAM, meshing for analysis, and
new kernel features are outside this documentation project.

## 4. Source investigation map

These are starting points confirmed to exist in the checkout, not a claim that
every named file contains the whole operation. Follow declarations into definitions,
dispatch branches, result structures, cleanup, and the consuming callers.

| Topic | Start with |
| --- | --- |
| Topology | [canonical BRep reference](../.agents/skills/smlib-brep-model/references/brep-format.md), [SmBrep.h](../source/SMLib/inc/SmBrep.h), [SmTopology.h](../source/SMLib/inc/SmTopology.h), entity/use headers, [SmTopology.cpp](../source/SMLib/src/SmTopology.cpp) |
| Evaluation | [SmCurve.h](../source/SMLib/inc/SmCurve.h), [SmSurface.h](../source/SMLib/inc/SmSurface.h), actual analytic and B-spline overrides, existing NURBS guide |
| Solvers | [SmGlobalSolver.cpp](../source/SMLib/src/SmGlobalSolver.cpp), [SmLocalSolve1d.cpp](../source/SMLib/src/SmLocalSolve1d.cpp), [SmLocalSolveNd.cpp](../source/SMLib/src/SmLocalSolveNd.cpp), [SmTopologySolver.cpp](../source/SMLib/src/SmTopologySolver.cpp) |
| Intersections | [operation guide](../.agents/operations/intersectors.md), [SmApiIntersectors.h](../source/SM_API/inc/SmApiIntersectors.h), [SmSurfaceIntersector.cpp](../source/SMLib/src/SmSurfaceIntersector.cpp), [SmAdvSurfaceIntersector.cpp](../source/SMLib/src/SmAdvSurfaceIntersector.cpp) |
| Queries | [operation guide](../.agents/operations/queries.md), [SmApiQueries.h](../source/SM_API/inc/SmApiQueries.h), wrappers and the particular geometry/topology solver they invoke |
| Projection and sections | [cut/project/trim guide](../.agents/operations/cut_project_trim.md), [SmApiTrimmedSurfaces.h](../source/SM_API/inc/SmApiTrimmedSurfaces.h), [SmBrepCutting.cpp](../source/SMLib/src/SmBrepCutting.cpp), plane intersection wrappers |
| Booleans | [operation guide](../.agents/operations/booleans.md), [SmApiBrep.h](../source/SM_API/inc/SmApiBrep.h), [SmTopologyIntersector.cpp](../source/SMLib/src/SmTopologyIntersector.cpp), actual BRep dispatch |
| Fillets/chamfers/blends | [operation guide](../.agents/operations/fillets.md), [SmApiFillets.h](../source/SM_API/inc/SmApiFillets.h), [SmFilletExecutive.cpp](../source/SMLib/src/SmFilletExecutive.cpp), associated solver/corner/removal classes, [SmBlendSurface.cpp](../source/SMLib/src/SmBlendSurface.cpp) |
| Tessellation | [operation guide](../.agents/operations/tessellation.md), [SmTess.cpp](../source/SMLib/src/SmTess.cpp), BRep conversion and PolyBrep output paths |
| Construction and repair | [sweeps](../.agents/operations/sweeps.md), [surfaces](../.agents/operations/surfaces.md), [offset](../.agents/operations/offset.md), [stitching](../.agents/operations/stitching.md), [healing](../.agents/operations/heal_import.md), corresponding executives and geometry constructors |
| Runtime/validation | [concurrency guide](../.agents/operations/concurrency.md), [SmContext.h](../source/SMLib/inc/SmContext.h), object ownership/notifications, entity validators, [error reference](../.agents/docs/errors.md) |
| Integration | [polygon guide](../.agents/operations/polybrep.md), [USD guide](../.agents/operations/usd_import_export.md), the relevant USD and OCCT layer when its chapter is reached |

Use the relevant repository skill when its scope applies. In particular, topology
claims follow the BRep model skill's distinction between model invariants,
constructor conventions, validator enforcement, and translation policy. Debugging
skills become relevant when an example exposes an actual subsystem failure.

Existing operation guides route investigation and provide usage context. They
are not sufficient evidence for a detailed algorithm claim. Resolve conflicts
against the current implementation and document remaining uncertainty.

## 5. Standard structure of each guide

1. **Purpose and boundaries:** what problem it solves, outputs, prerequisites,
   and nearby operations that are easily confused with it.
2. **Theory:** notation, geometric principles, LaTeX equations, assumptions,
   and exact versus tolerance-based behavior.
3. **Algorithm:** stages, alternatives, stopping criteria, degeneracies, and
   correctness conditions. Separate textbook possibilities from the implemented path.
4. **SMLib architecture:** public entry points, object model, numerical helpers,
   result data, and a source-linked call graph.
5. **Code walkthrough:** trace a real operation from input validation through
   dispatch, core work, result assembly, ownership transfer, and errors.
6. **C++ use:** a minimal example with correct status and lifetime handling;
   one realistic CAD workflow with meaningful expected results.
7. **Failure and robustness:** units, scale, tolerances, seams, singularities,
   unsupported combinations, and diagnostic evidence specific to the topic.
8. **Verification and reading order:** what was checked, example execution status,
   source revision, related guides, and how to reproduce the figures.

Aim for the existing guides' explanatory depth, not a fixed word count. A short
API list does not count as a finished subsystem document. Conversely, a chapter
should not grow by duplicating NURBS theory or generic ownership advice.

## 6. Evidence and accuracy rules

- Mark mathematical theory, verified implementation, and application suggestions
  distinctly. Do not attribute a named algorithm merely because the result resembles it.
- Record the upstream source revision examined for each completed guide. Link to
  repository-relative files and stable symbol names; line numbers alone drift.
- Trace at least one complete path per major feature. For grouped topics such as
  fillet/chamfer/blend, verify which paths are shared and which are different.
- Verify mutates/consumes/produces semantics on success **and failure**. A wrapper
  name is insufficient to infer ownership.
- Identify the actual tolerance and error metric. Distinguish parameter residual,
  world-space distance, angular tolerance, and topological consistency.
- Avoid guarantees not established by code or mathematics. In particular, sampled
  error is not automatically a global bound; a success status does not always mean
  a solution was found; a manifold predicate is not a complete validity proof.
- Include cases that defeat simple explanations: a solid contained entirely in
  another has no boundary intersection; a seam can reuse an edge on one face;
  tangency and coplanarity need not produce ordinary transverse intersection curves.
- For topology, treat optional derived UV trims separately from defining 3D
  edge geometry, intervals, face supports, and incidence relationships.
- Use primary references for external mathematical claims requiring verification.
  Source citations must support the nearby claim rather than merely name a library.
- Do not silently repair kernel code while writing a guide. Record a discovered
  defect or limitation separately and keep the documentation change scoped.

## 7. Figures and examples

Keep Markdown beside the existing guides and assets under
`mydocs/assets/<topic>/`. Add a small generator when a plot needs numerical
construction. Use Mermaid for class relationships, call graphs and workflow;
use reproducible SVG plots for geometry and PNG copies when useful for preview.

Each substantial guide should normally include:

- A geometric concept illustration.
- An architecture or data-relationship diagram.
- A call-flow or algorithm-stage diagram.
- A worked CAD example, plus a limiting/degenerate case where informative.

Figures must identify whether they are conceptual constructions or actual SMLib
results. A Python plot of a mathematical fillet must not be presented as output
of the SMLib fillet executive. Inspect rendered figures, not just their scripts.

C++ is the main application language. Use the repository's brace/indent style,
`SM_SUCCESS`, explicit ownership, and source-verified signatures. State whether
each example is compiled and run, signature-reviewed only, or pseudocode.
Runnable standalone examples may live under `mydocs/examples/<topic>/` with
their build/run instructions; avoid expanding the main build simply to host prose.

Prefer simple cases with independent expected results: analytic dimensions,
volume, distance, endpoint positions, contour closure, or angular/chord error.
Do not make exact face/edge counts a universal correctness criterion when valid
operations can partition the same geometry differently.

## 8. Work cycle and completion criteria

For each guide:

1. Inventory interfaces and choose a representative operation and edge cases.
2. Read the operation guide and applicable skill/reference, then inspect source.
3. Make a brief evidence map: claims, symbols, dispatch paths, unresolved questions.
4. Draft theory and source walkthrough together, so diagrams reflect the real code.
5. Construct and inspect illustrations; prepare the C++ example.
6. Check math notation, relative links, Markdown structure, source symbols,
   whitespace and figure reproducibility. Run executable examples where supported;
   record any unavailable build/runtime dependency precisely.
7. Review API ownership, failure behavior, tolerance claims and degeneracies again.
8. Link the completed guide from `arch.md` and the planned `mydocs/README.md` index.
9. Update this progress record and publish a focused commit to `chen-doc` after
   the guide passes review. Do not batch the entire handbook into one final commit.

Documentation-only changes require documentation checks, not a full kernel test
run. An executable example requires validation appropriate to that example; a
failed example should be investigated before claiming the document is complete.
Respect repository search exclusions and avoid broad scans of build artifacts or
test fixtures. No kernel or GUI changes are part of the baseline deliverables.

A guide is complete when its scope is covered, major claims have source evidence,
the diagrams are readable, examples have an explicit validation status, links
work, and no unresolved question is disguised as established behavior.

## 9. Checkpoints and branch maintenance

Maintain a short progress entry per guide: status, source revision, example
validation, unresolved findings, and commit. Useful states are `planned`,
`researching`, `draft`, `validated`, and `published`. Do not call a researched
outline a completed guide.

| Checkpoint | Deliverable | Current state |
| --- | --- | --- |
| Planning | This scope, ordering and completion standard | Written |
| Foundation | Topology, geometry, tolerances, evaluation, spatial indexing, solvers | Written and reviewed: 6 guides |
| Analysis | Intersections, queries, projection/trimming, sections | Written and reviewed: 4 guides |
| Core modeling/display | Booleans, fillets/chamfers/blends, tessellation, silhouettes | Written and reviewed: 4 guides |
| Construction/repair | Primitives/sweeps, lofts/patches, offsets/shells, healing/stitching, editing, deformation | Written and reviewed: 6 guides |
| Infrastructure/integration | Runtime, validation, polygon BRep, assemblies/attributes, native I/O, USD | Written and reviewed: 6 guides |

Keep documentation commits on `chen-doc` and upstream synchronization on `main`.
Perform rebases between completed guide checkpoints, with a clean worktree.
Inspect changes to referenced source after each upstream update; a clean Git
rebase does not prove the documentation still describes the code correctly.
If another contributor changes the remote documentation branch, integrate that
work before pushing. Use a guarded force push only when publishing rebased commits.

The topology foundation establishes region/shell ownership, oriented uses,
seams, non-manifold incidence, and defining geometry versus optional UV trims.
The boolean, fillet, and translation chapters link back to those distinctions.

## 10. Coverage audit: additions and explicit subtopics

Comparing the baseline against the SMLib headers, corresponding implementation
files, and SM_API declarations revealed gaps beyond the originally requested
operations. Some are shared foundations; others are less prominent kernel
features. A declaration and implementation file establish a research target,
not complete support, robustness, or availability through the stable API.

### 10.1 Seven additional guides

All seven additions are included in the delivered handbook; their original
scope and placement are retained here for future coverage reviews.

| Added guide | Missing coverage | Delivery placement and source starting points |
| --- | --- | --- |
| `geometry.md` | Analytic curves and surfaces; coordinate systems and placements; bounded/unbounded geometry; composite, projected, on-surface and isoparametric curves; procedural surface representations; conversion to NURBS and its consequences | Phase 1, after topology and before evaluation. Start with [SmCurve.h](../source/SMLib/inc/SmCurve.h), [SmSurface.h](../source/SMLib/inc/SmSurface.h), [SmAxis2Placement.h](../source/SMLib/inc/SmAxis2Placement.h), [SmCompositeCurve.h](../source/SMLib/inc/SmCompositeCurve.h), [SmCrvOnSurf.h](../source/SMLib/inc/SmCrvOnSurf.h), and analytic subclasses |
| `tolerances.md` | Floating-point scale and conditioning; geometric versus parameter tolerances; effective object tolerances; comparison predicates; propagation through operations and conversion; small features and degenerate geometry | Phase 1, after geometry and before solvers. Start with [SmTol.h](../source/SMLib/inc/SmTol.h), [SmTol.cpp](../source/SMLib/src/SmTol.cpp), [SmMath.h](../source/SMLib/inc/SmMath.h), and actual caller policies. Verify build-dependent tolerance models; do not claim universally exact predicates |
| `spatial-indexing.md` | Spatial versus parameter-domain decomposition; bounds and subdivision trees; candidate-pair pruning; object caches and invalidation; cost/accuracy tradeoffs in repeated geometric queries | Phase 1, after evaluation and before solvers/intersections. Start with [SmTree.h](../source/SMLib/inc/SmTree.h), [SmTree.cpp](../source/SMLib/src/SmTree.cpp), [SmCurveCache.h](../source/SMLib/inc/SmCurveCache.h), [SmSurfaceCache.h](../source/SMLib/inc/SmSurfaceCache.h), and [SmBrepCache.h](../source/SMLib/inc/SmBrepCache.h). Explain algorithms here and cache lifetime in runtime |
| `deformation.md` | Volumetric parameter maps, B-spline volumes, bend/twist/unbend mappings, mapped curves/surfaces, invertibility/Jacobians, approximation and topology consistency; sheet-bending workflows where supported | Phase 4, after editing. Start with [SmVolume.h](../source/SMLib/inc/SmVolume.h), [SmBSplineVolume.h](../source/SMLib/inc/SmBSplineVolume.h), [SmTwistVolume.h](../source/SMLib/inc/SmTwistVolume.h), [SmSpaceBend.h](../source/SMLib/inc/SmSpaceBend.h), and [SmSpaceUnbend.h](../source/SMLib/inc/SmSpaceUnbend.h). Distinguish a deformation volume from a BRep solid or a volume measurement |
| `silhouettes-visibility.md` | View-dependent silhouettes; surface tracing; visible versus hidden curves; ray queries and picking; relation to section curves and projected edges | Phase 3, after tessellation, using Phase 2 analysis foundations. Start with [SmSurfaceSilhouette.h](../source/SMLib/inc/SmSurfaceSilhouette.h), [SmDirectedSilhouette.h](../source/SMLib/inc/SmDirectedSilhouette.h), [SmHCR.h](../source/SMLib/inc/SmHCR.h), [SmRayTracer.h](../source/SMLib/inc/SmRayTracer.h), and `SmApiCreateSilhouetteCurves`. Trace the supported entry points; internal rendering classes do not establish a complete application renderer |
| `assemblies-attributes.md` | Hierarchical assemblies, reusable instances and placements; object attributes; copy and operation propagation; identity and topology-change maps; implications for application selections | Phase 5, after runtime. Start with [SmAssembly.h](../source/SMLib/inc/SmAssembly.h), [SmAssemblyInstance.h](../source/SMLib/inc/SmAssemblyInstance.h), [SmAttribute.h](../source/SMLib/inc/SmAttribute.h), [SmTrackTopologyChanges.h](../source/SMLib/inc/SmTrackTopologyChanges.h), and [SmCopyBrepMap.h](../source/SMLib/inc/SmCopyBrepMap.h). Do not assume assembly constraints or persistent naming across arbitrary edits |
| `native-io.md` | Native SMLib BRep and part-container persistence; ASCII/binary paths; allocated-output ownership; post-load derived geometry; serialization validation and reproducibility; distinction from USD/OCCT translation | Phase 5, before USD interchange. Start with [SmApiImportExport.h](../source/SM_API/inc/SmApiImportExport.h), [SmDatabaseIO.h](../source/SMLib/inc/SmDatabaseIO.h), and [SmBrepData.h](../source/SMLib/inc/SmBrepData.h). Verify the role of each serialization path rather than assuming every format uses the same intermediate structure |

The revised foundation sequence is: **topology → geometry → tolerances →
evaluation → spatial indexing → solvers**. Other baseline phases keep their
relative order, with the additions inserted as specified above.

### 10.2 Expand existing chapters rather than add more files

| Existing planned chapter | Make this coverage explicit |
| --- | --- |
| `topology.md` | Euler-style split/join operations and their preconditions; region material/void relationships; traversal and topology-change tracking. Do not reduce Euler theory to an unrestricted V−E+F rule |
| `solvers.md` | Supporting linear algebra, polynomial root solving, Jacobians and conditioning; trace the helpers used by real callers rather than suggesting one universal solver |
| `queries.md` | Numerical quadrature, signed/oriented integration, centroids and inertia tensors; mass-property assumptions; distinguish integration accuracy from model validity. Start with [SmIntegrator.h](../source/SMLib/inc/SmIntegrator.h) and [SmGauss.h](../source/SMLib/inc/SmGauss.h) alongside the query paths |
| `editing.md` | Feature partition/removal and reconstruction, not only transforms. Investigate [SmFeatureExecutive.h](../source/SMLib/inc/SmFeatureExecutive.h) and its callers; do not equate this class with a full parametric feature-history system |
| `polygon-brep.md` | Mesh decimation/simplification and its geometric/topological constraints, in addition to queries and polygon booleans. Investigate [SmPolyDecimate.h](../source/SMLib/inc/SmPolyDecimate.h) and its implementation |
| `lofts-patches.md` | Compatibility and reparameterization, boundary continuity, corner conditions, fairness diagnostics and supported shape-editing paths; distinguish existing fitting facilities from any unsupported general fairing optimizer |
| `runtime.md` | Cancellation/progress hooks where present, object-level cache behavior, process/thread assumptions, and repeat-operation performance; verify which mechanisms are active in the shipped configuration |
| `usd-interchange.md` | Separate native I/O, OCCT conversion, USD BRep persistence and polygon mesh export; document preservation/loss of units, orientation, tolerances, attributes and instancing only where verified |

### 10.3 Application-level topics remain a separate scope

For a complete CAD application, additional design work would cover a sketch
constraint solver, parametric feature history and regeneration, persistent
selection/naming, undo/redo transactions, assembly constraints, Qt interaction,
and a document model. These are application requirements to assess separately.
The names `SmFeatureExecutive`, `SmAssembly`, or `SmAttribute` do not by themselves
establish that SMLib supplies all of those systems.

This audit covers the visible kernel/API families, not every utility class or
all repository integration tools. Each completed guide should maintain a short
coverage table marking interfaces as explained, deliberately deferred, or
unavailable at the chosen API layer. Revisit the inventory at phase checkpoints
to catch components discovered while tracing real operations.

## 11. Delivery record

All 26 guide commits below are published to `origin/chen-doc`. Each uses source
baseline `3fd5b9548d19aa8c12c29bc9637a96d42a06f8a5`. The [handbook index](README.md)
provides navigation and scenario-based reading paths. Shared illustrations were
published in commit `871b86e`.

| Guide | Reviewed coverage | Example form | Guide commit |
| --- | --- | --- | --- |
| [topology.md](topology.md) | Entity/use graph; shell/region semantics; Euler-style split; query traversal | C++ fragment | `727e3fa` |
| [geometry.md](geometry.md) | Dynamic-type hierarchy; frames; composed geometry and conversion policy | Source workflow | `347ebfa` |
| [tolerances.md](tolerances.md) | Typed tolerance vocabulary; scale/parameter error; caller-policy tracing | Mathematical workflow | `f6b4e4a` |
| [evaluation.md](evaluation.md) | Spline dispatch; STEP derivative units/layout; finite-difference checks | C++ fragment + existing example | `7e7497d` |
| [spatial-indexing.md](spatial-indexing.md) | Parameter versus object trees; bounds; cache consumers and pruning | Source workflow | `405c906` |
| [solvers.md](solvers.md) | Local/global hooks; solution identity; closest-point caller publication | C++ fragment | `5e39fe5` |
| [intersections.md](intersections.md) | Curve/surface/face dispatch; empty-result and output ownership behavior | C++ fragment | `19a9d7a` |
| [queries.md](queries.md) | Boundary distance/relationship; bounds; mass-property integration and moment conventions | C++ fragment | `c73d27d` |
| [projection-trimming.md](projection-trimming.md) | Drop/trim/lift temporary outputs; UV seams and trim-region construction | Source workflow | `05a0f0f` |
| [sections.md](sections.md) | Plane section append policy; cut half-space; contour nesting and caps | Source workflow | `ce80ff5` |
| [booleans.md](booleans.md) | Manifold dispatch; provisional intersection/resolve/imprint/relate stages; consumption | Existing native example + workflow | `9fadde4` |
| [blend.md](blend.md) | Chamfer/circular/selected-edge paths; blend insertion; removal fallback and partial mutation | Source workflows | `6bc3881` |
| [tessellation.md](tessellation.md) | Parameter struct; BRep conversion; shared edges; partial-result diagnostics | C++ fragment | `788efba` |
| [silhouettes-visibility.md](silhouettes-visibility.md) | HCR wrapper; ignored plane-point input; output copying; ray/visibility concepts | Source workflow | `ec952de` |
| [primitives-sweeps.md](primitives-sweeps.md) | Linear/rotational/draft/pipe wrappers; profile copying; caps and frames | C++ fragment | `15b2b5c` |
| [lofts-patches.md](lofts-patches.md) | Skin/ruled wrappers; Coons and N-sided kernel dispatch; boundary/correspondence constraints | Source workflows | `fc48343` |
| [offsets-shells.md](offsets-shells.md) | Offset dispatch; shell selection validation, copy mapping and ownership transfer | Source workflow | `81d0592` |
| [healing-stitching.md](healing-stitching.md) | Measure/fix/cache stages; unfinished repairs; stitch diagnostics and validation | Diagnostic workflow | `75e4456` |
| [editing.md](editing.md) | Transforms; dependent-state updates; feature reconstruction and selection lifetime | Application + source workflow | `4dec66b` |
| [deformation.md](deformation.md) | Four-space maps; Evaluate versus Map; derivative composition; bend/twist facilities | Kernel workflow + mathematical figure | `cc51902` |
| [runtime.md](runtime.md) | Default context; ownership/cache lifetime; serialized API work; cancellation boundary | Application workflow | `f7f225c` |
| [validation-diagnostics.md](validation-diagnostics.md) | Pointer/deep validity stages; status flags; independent geometry checks and reproductions | Diagnostic workflow | `888a5cb` |
| [polygon-brep.md](polygon-brep.md) | Polygon boolean dispatch; measured/quadric decimation paths; winding and volume | Source workflows | `b1c0512` |
| [assemblies-attributes.md](assemblies-attributes.md) | Occurrence constructor/destructor behavior; unfinished graphics path; attributes and identity | Kernel + application workflow | `ac39ee5` |
| [native-io.md](native-io.md) | Single/part read cleanup and publication; native persistence and round-trip observables | C++ fragment | `173dc52` |
| [usd-interchange.md](usd-interchange.md) | Packed schema/runtime separation; import/export policies; native/OCCT/mesh boundaries | Source workflow | `38250a6` |

### Validation performed

- Checked local Markdown target paths, code fences, display-math delimiters,
  source-baseline declarations, index coverage, SVG XML, PNG signatures, and
  Python syntax with [check_docs.py](tools/check_docs.py).
- Parsed all 56 Mermaid diagrams across `mydocs` and rendered the LaTeX
  expressions with [check_diagrams.mjs](tools/check_diagrams.mjs). Rendered the
  Mermaid diagrams in headless Chrome; visually inspected representative complex
  topology, solver, runtime, boolean, loft and interchange diagrams.
- Generated and visually inspected all seven supplemental mathematical figures.
  Their numerical invariants passed; rerunning the generator reproduced all 14
  SVG/PNG artifacts byte-for-byte in the validation environment.
- Reviewed native fragments against declarations and ownership paths. Checked
  staged changes with `git diff --cached --check`; no kernel code was changed.

The illustration run used NumPy 2.5.4 and Matplotlib 3.11.2. Diagram/math checks
used Mermaid 12.3.0, KaTeX 0.19.1, and jsdom 30.1.3; the browser render used
puppeteer-core 25.16.0 with installed Chrome. These versions describe the check
environment, not kernel dependencies or requirements for reading the Markdown.

### Example status and scope boundaries

The new native C++ fragments are **signature-reviewed, not compiled or executed**.
Existing executable examples are linked with their own validation notes and
were not rerun. No kernel, USD round-trip, sanitizer, performance, or concurrency
test run is claimed. Mathematical figure assertions test the illustration
formulas rather than SMLib.

For kernel-internal topics without a suitable simple stable-wrapper example,
the delivered code treatment is an explicit source walkthrough and pseudocode.
This avoids inventing public APIs or implying that every algorithm is exposed
through `SM_API`. The chapters identify representative paths and important
variants; they do not audit every utility, overload, and compile-time branch.

Known limits are recorded where they affect use: heuristic touching/overlap
classification, unfinished healer stages, non-atomic removal/replacement paths,
patch input restrictions, incomplete assembly graphics, unverified general
cancellation, and interchange normalization/metadata boundaries. They are not
silently promoted into supported guarantees. Full application history, sketch
constraints, assembly constraints, persistent naming, Qt UI, CAM and analysis
meshing remain outside the agreed scope.

After rebasing, review changes to the cited symbols before updating the source
baseline. A clean merge and passing documentation checks cannot establish that
a changed kernel still follows these workflows.

### Follow-up: worked 3D fillets

The fillet chapter now includes a dimensioned single-edge block example, a native
C++ selection/fillet/validation helper, an exact rational quarter-cylinder
construction, and an ideal three-edge spherical corner. Two additional analytic
3D figures were generated and visually inspected; radius/contact checks passed.
The native helper remains source-reviewed rather than compiled or executed.
The documentation checker now also covers these SVG/PNG files and their generator.

The 3D figure export was subsequently corrected after browser rendering exposed
polygon-boundary patterns in the SVGs. Filled 3D collections now use 300-dpi
raster layers; text and explicit line annotations remain vector. Before/after
Chrome renders at 480, 960, and 1440 pixels confirmed removal of the dense seam
pattern. The checker rejects fillet SVGs that reintroduce individual 3D face paths.

### Follow-up: explicit local operations (LOP)

Added [local-operations.md](local-operations.md) as the 27th subsystem guide and
linked it from the handbook, editing, and offset chapters. It traces
`SmBrep::LocalOperation`, `SmLocalOperationGeometryCreation`, and the extended
offset executive through face construction, UV/edge correspondence, support
extension, intersection, stitching, and whole-face-set replacement.

The chapter distinguishes mathematical local editing from this implementation's
limits: raw surface adoption/mutation, parameter compatibility, suppressed edge
repair failures, stitching versus full merge, and application validation.
Worked constructions cover raising a block top, tilting its top, and enlarging
a through-hole. A new three-panel 3D figure shows the first two edits against
the original body, with independent plane/corner/volume assertions.

Validation: documentation structure and assets passed for all 27 guides;
58 Mermaid diagrams parsed and 451 LaTeX expressions rendered without errors.
Both new Mermaid diagrams and the new SVG were rendered in Chrome and visually
inspected. The 3D SVG was reviewed at 960 pixels, with a second 1440-pixel render;
filled surfaces use raster layers and contain no individual 3D polygon paths.
The checker now includes the new SVG/PNG pair and generator. Native call fragments
remain source-reviewed, not compiled or executed; the figure is not evidence of
a successful SMLib local-operation run. No kernel code was changed.

### Follow-up: Euler operations

Added [euler.md](euler.md) as the 28th subsystem guide. It covers Euler
characteristic with explicit loop/boundary counting conventions, classical
make/kill pairs, their relationship to the SMLib radial-use representation,
and the actual kernel methods. Source walkthroughs cover wire construction,
edge subdivision, face insertion, loop bridging, compatible face joining,
and removal of intermediate vertices. A box-face imprint gives expected
entity counts, areas, and unchanged volume.

The new SVG/PNG schematic compares three edits before and after, including
the two opposite uses of a ring bridge. The generator checks its count
arithmetic and the imprint sequence; these checks are not kernel executions.
The guide records endpoint-error outputs, partial-mutation/ownership limits,
periodic-seam exceptions, and the need for independent validation. Native
fragments remain source-reviewed rather than compiled or executed.

Validation for this follow-up: documentation checks passed for 28 guides;
60 Mermaid diagrams parsed and 513 LaTeX expressions rendered without errors.
The two new Mermaid diagrams and the Euler SVG were rendered in Chrome and
visually inspected. The new schematic's count assertions passed. No native
kernel tests or topology edits were executed as part of this documentation work.
