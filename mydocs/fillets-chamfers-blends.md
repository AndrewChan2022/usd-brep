# Fillets, chamfers, and blends

Source baseline: upstream `3fd5b9548d19aa8c12c29bc9637a96d42a06f8a5`.
This chapter distinguishes construction theory, actual executive roles, and
application workflows. No new native fillet example was executed here.

For a concrete solid-model example, jump to
[the worked 3D fillet and corner examples](#8-worked-3d-examples).

## 1. Three operations sharing a transition problem

A fillet commonly inserts a rounded transition with a circular cross-section.
A chamfer inserts a bevel, often with a linear cross-section. A blend is a
broader transition construction whose section and continuity can be controlled.
Replacing a solid edge includes trimming and topology reconstruction; creating
a standalone blend surface does not perform all of that work.

The user-visible “radius” or “distance” may have different meanings across these
operations. Selecting a linear cross-section in a radius-based solver is not
necessarily equivalent to selecting the dedicated constant-distance chamfer
solver.

## 2. Rolling-ball and offset interpretation

![Circular radius compared with chamfer width at a right-angle corner](assets/handbook/transitions.svg)

These idealized planar sections illustrate the dimensions independently of the
kernel; they do not depict a completed SMLib corner blend.

For a regular constant-radius contact on oriented supports, a ball center can
be written locally as

$$
\mathbf c=\mathbf S_1(u,v)+s_1r\mathbf n_1
=\mathbf S_2(a,b)+s_2r\mathbf n_2,
$$

where the signs select offset sides. Intersecting the appropriate offsets gives
a candidate center locus or spine; contact points on the original supports
define transition boundaries. This is a geometric model, not a statement that
every SMLib fillet branch explicitly constructs two complete offset surfaces.

For two perpendicular planes with a symmetric chamfer whose cross-section
width is $w$, the setback along each plane is $w/\sqrt2$. A circular fillet's
radius is a different quantity. A field labeled “radius” in a generic UI should
not conceal that difference.

```mermaid
flowchart LR
    S[Adjacent supports and edge] --> P[Choose side, size law and section]
    P --> C[Spine and contact solutions]
    C --> B[Transition surface]
    B --> T[Trim original supports]
    T --> K[Corner patches and topology replacement]
```

## 3. Continuity conditions

$G^0$ means matching position; $G^1$ requires compatible tangent planes; $G^2$
adds geometric curvature compatibility. Parametric $C^k$ requirements are
stronger in a different sense because derivatives must agree under the selected
parameterizations. Equal endpoint positions alone do not give a smooth highlight.

For curves, one way to express regular $G^1$ matching is

$$
\mathbf C_1'(1)=\lambda\mathbf C_2'(0),\qquad\lambda>0.
$$

For surfaces, the shared tangent plane and appropriate cross-boundary behavior
matter. A circular section can provide tangent continuity while curvature still
jumps across the join. Higher continuity settings must be interpreted for the
supported blend generator, not assumed to apply to every circular fillet.

## 4. SMLib architecture

Public entries are split between [SmApiFillets.h](../source/SM_API/inc/SmApiFillets.h)
and [SmApiBrep.h](../source/SM_API/inc/SmApiBrep.h). The all-edge convenience
wrappers are in [SmApiFillets.cpp](../source/SM_API/src/SmApiFillets.cpp).

| Component | Responsibility |
| --- | --- |
| `SmFilletExecutive` | Collect solvers, organize corners, coordinate modeling stages |
| `SmFilletSolver` and subclasses | Solve contact/spine problems under the chosen sizing policy |
| Surface generators | Construct linear, circular or blend sections/surfaces |
| `SmFilletCorner` | Coordinate transitions at vertices and multi-edge junctions |
| `SmFilletIntersector` / topology intersector | Resolve intersections and integrate replacement geometry |
| `SmFilletRemoval` | Separate removal/reconstruction workflow |

The principal sources are [SmFilletExecutive.cpp](../source/SMLib/src/SmFilletExecutive.cpp),
[SmFilletStandardSolver.h](../source/SMLib/inc/SmFilletStandardSolver.h),
[SmFilletGeom.h](../source/SMLib/inc/SmFilletGeom.h), and
[SmFilletCorner.cpp](../source/SMLib/src/SmFilletCorner.cpp).

## 5. A traced chamfer path

`SmApiChamferFillet` first checks the body and requested distance through
`SmFilletExecutive::IsRadiusSupported`. It creates a linear cross-section
generator, a self-intersection handler, and a fillet executive with global merge
enabled. It traverses the body's edges and uses `GetBlendEdgeuse` to select
eligible edge incidence; an edge without such an incidence is skipped.

For each eligible edge it creates `SmConstantDistanceFS`, assigns the linear
generator, and loads the solver into the executive. It then creates corners,
sets their bevel behavior, and calls `DoFilleting`.

```mermaid
flowchart TD
    API[SmApiChamferFillet] --> V[Validate body and distance]
    V --> E[Enumerate blendable edgeuses]
    E --> FS[SmConstantDistanceFS]
    FS --> G[Linear cross-section generator]
    G --> EX[Load into SmFilletExecutive]
    EX --> C[CreateFilletCorners and bevel policy]
    C --> D[DoFilleting]
```

This is more precise than “all edges always receive a bevel.” The executive's
`DoFilleting` also contains a global merge path invoking `IntersectInsertRelate`.
Fillet construction consequently depends on the same topology/intersection
foundations as booleans, not only on generating a visually smooth patch.

### Circular fillets and selected-edge blends

`SmApiCircularFillet` shares the executive and corner stages, but uses
`SmConstantRadiusFS` with `SmCircularCrossSectionFSG`. After `DoFilleting`, the
wrapper calls `StitchAndOrient`; this call's status is not propagated in the
inspected wrapper. Independent validation remains necessary even when the
earlier executive returned success.

`SmApiFilletEdges` in [SmApiBrep.cpp](../source/SM_API/src/SmApiBrep.cpp)
uses `SetFilletParameters` followed by `DoFillet`. Its section selector maps
0 to linear, 2 to blend-curve, and otherwise to circular. Crucially, it still
selects `SM_FS_CONST_RADIUS`; changing the section to linear does not switch
to the dedicated chamfer wrapper's `SmConstantDistanceFS`. Per-edge radii in
`SmApiFilletEdgesPerEdge` mean different constant radii on different edges;
that alone is not a continuously varying radius along one edge.

`SmApiCreateBlendPrimitive` in
[SmApiPrimitives.cpp](../source/SM_API/src/SmApiPrimitives.cpp) is another
distinct path. It supplies two boundary edges, their support faces, and a
same/opposite correspondence flag to `SmPrimitiveCreation::CreateBlendPrimitive`.
It inserts the resulting face into the supplied BRep. The returned face is
body-owned; the function is not a pure standalone-surface producer.

### Removal reconstructs the retained supports

`SmApiRemoveFillet` first identifies faces with tangent rail edges, then attempts
`DeleteFilletFace` on each. Successful deletions remain applied; after any
deletion, the wrapper checks the result of `StitchAndOrient`. If some fillets
remain, `sm_DefeatureFillets` works on a copy, adds qualifying rounded corners,
groups connected feature faces, and runs `SmFeatureExecutive::DoDefeature`.

The fallback checks reconstruction, removes redundant topological edges/vertices,
and validates the working body before replacing the original topology. Replacement
has a backup and best-effort restoration. This does **not** make the whole public
call atomic: earlier successful fillet deletions can already have changed the
input, and restoration itself is not guaranteed.

| Entry family | Explained path | Important boundary |
| --- | --- | --- |
| All-edge chamfer | Constant-distance solver, linear section, bevel corners | Eligible edgeuses only |
| All-edge circular fillet | Constant-radius solver, circular section, executive and stitch | Validate after post-processing |
| Selected-edge fillet/blend | Parameter setup, section selection, `DoFillet` | Section type and sizing policy are separate |
| Blend primitive | Boundary-edge correspondence and primitive insertion | Mutates supplied BRep |
| Fillet removal | Direct deletion, then grouped feature reconstruction | Partial mutation can survive failure |

## 6. Radius feasibility and variable size

A radius is feasible only if contact geometry, available face domains, corner
construction, self-intersection avoidance, and retained material all cooperate.
There is no general rule that “radius smaller than the smallest adjacent face
dimension” is sufficient. A narrow region, concavity, nearby unrelated face, or
poor parameterization can invalidate that shortcut.

For a variable-radius law $r(s)$, the meaning of $s$ matters: edge parameter,
normalized parameter and arc length are different. Endpoint values do not
fully specify every interpolation/continuity policy. Inspect the chosen solver
and API rather than assuming linear variation in physical distance.

Several selected edges meeting at a corner must be solved together. Independently
filleting each edge can produce different topology or fail after the first edit
invalidates later selections. Reacquire edges after a mutation unless the operation
explicitly processes the whole selection in one call.

## 7. Application workflow and ownership

```text
copy the body if cancellation/undo must preserve the original
select edges by geometric/topological criteria, not array position
verify all selected edges belong to the target body
choose solver semantics, section, continuity and size law
run the operation and check status plus any diagnostics
reacquire topology; inspect boundaries, corners and material validity
publish the edited body only after application acceptance checks
```

Common wrappers mutate the supplied BRep. Do not assume failure rolls back all
intermediate work. The exact selected wrapper governs its input validation and
ownership. A standalone blend or preview result has a different contract from
in-place edge replacement.

For a bracket, begin with one isolated edge at a conservative design radius,
verify tangency and material side, then add the connected corner network. This
sequence is diagnostic; the final model should still use the intended design
radius and edge set rather than silently reduced settings.

## 8. Worked 3D examples

### 8.1 Round one edge of a rectangular block

Take a block of length $L=20$, width $W=12$, and height $H=8$, with its minimum
corner at the origin. Use consistent model length units throughout. Select only
the top-front edge, from $(0,0,8)$ to $(20,0,8)$, and apply a circular fillet of
radius $r=2$.

![A 3D block before and after rounding one full-length edge](assets/fillets/single_edge_3d.svg)

Orange marks the selected sharp edge on the left and the new **surface** on the
right. These are analytic illustrations of the intended geometry, not screenshots
of an executed SMLib operation. [PNG alternative](assets/fillets/single_edge_3d.png).

The two adjacent supports are the front plane $y=0$ and top plane $z=H$.
In each YZ cross-section, replace the sharp corner with a quarter-circle centered
at $(r,H-r)=(2,6)$. Extending that section along X produces a quarter-cylinder:

$$
\mathbf S(x,\theta)=
\begin{bmatrix}
x\\r-r\cos\theta\\H-r+r\sin\theta
\end{bmatrix},\qquad
0\leq x\leq L,\quad0\leq\theta\leq\frac\pi2.
$$

The surface has two contact rails and a center spine:

| Curve | Position | Meaning |
| --- | --- | --- |
| Front contact rail | $(x,0,6)$ | Fillet meets the trimmed front face |
| Top contact rail | $(x,2,8)$ | Fillet meets the trimmed top face |
| Center spine | $(x,2,6)$ | Centers of the rolling radius-2 ball/section circles |

The spine lies inside the solid; it is construction geometry, not a new visible
boundary edge. A 2D fillet constructs the section arc. This **3D edge fillet**
constructs a surface, trims its neighboring faces, changes the two end-face
boundaries, and reconnects the solid's topology.

The outward normal on the cylindrical patch is

$$
\mathbf n=(0,-\cos\theta,\sin\theta).
$$

At $\theta=0$ it is the front-face normal $(0,-1,0)$; at $\theta=\pi/2$ it is
the top-face normal $(0,0,1)$. The joins are tangent-continuous. Curvature across
the circular section changes from zero on either plane to magnitude $1/r$ on
the cylinder, so this ordinary circular fillet is generally $G^1$, not $G^2$.

### 8.2 Its NURBS representation

This special case has an exact rational tensor-product representation. At each
of $x=0$ and $x=L$, use the three YZ control points

$$
\mathbf P_0=(0,H-r),\qquad
\mathbf P_1=(0,H),\qquad
\mathbf P_2=(r,H),
$$

with weights $(1,1/\sqrt2,1)$. Two copies of that control row, one at each X end,
give a $2\times3$ control net. The degrees are 1 along the edge and 2 across the
arc; corresponding clamped knot vectors are $(0,0,1,1)$ and $(0,0,0,1,1,1)$.

The middle control point lies at the old sharp corner, but the rational curve
does not pass through it. Also, the spline parameter across the arc is not
linear in $\theta$. This construction explains the exact geometry available in
this planar case; it does not claim that every SMLib fillet branch stores this
particular control net or retains one unsplit face.

### 8.3 Native C++ workflow for the selected edge

The following helper creates a fresh body, finds the edge passing through
$(10,0,8)$, fillets it, and checks manifold status and expected volume. Selecting
by a known interior point avoids depending on the order returned by `GetEdges`.
The point test is specific to this simple box; an arbitrary model needs a more
complete selection policy.

This is a source-reviewed C++ usage example, **not a compiled or executed result**.
Use the include/link setup in the [native example README](../Examples/SM_API/README.md).

```cpp
#include <SmApiBrep.h>
#include <SmApiGeneral.h>
#include <SmApiPrimitives.h>
#include <SmApiQueries.h>
#include <SmBrep.h>
#include <SmVector3d.h>

#include <cmath>
#include <memory>
#include <stdexcept>

void CheckFilletStatus(SmApiStatus status, const char* operation)
{
    if (status != SM_SUCCESS)
    {
        throw std::runtime_error(operation);
    }
}

std::unique_ptr<SmBrep> MakeSingleEdgeFillet()
{
    // Initialize before dispatching work; general SM_API calls are serialized.
    SmApiCreateContext();
    SmBrep* raw = nullptr;
    SmApiStatus status = SmApiCreateBox(
        SmVector3d(0.0, 0.0, 0.0), 20.0, 12.0, 8.0, raw);
    std::unique_ptr<SmBrep> body(raw);
    CheckFilletStatus(status, "CreateBox failed");

    SmTArray<SmEdge*> edges;
    SmTArray<SmEdge*> selected;
    CheckFilletStatus(SmApiGetEdges(body.get(), edges), "GetEdges failed");
    const SmPoint3d probe(10.0, 0.0, 8.0);
    for (ULONG i = 0; i < edges.GetSize(); ++i)
    {
        SmPoint3d closest;
        double parameter = 0.0;
        double distance = 0.0;
        CheckFilletStatus(SmApiEdgeClosestPoint(
            edges[i], probe, closest, parameter, distance), "Edge query failed");
        if (distance <= 1.0e-5)
        {
            selected.Add(edges[i]);
        }
    }
    if (selected.GetSize() != 1)
    {
        throw std::runtime_error("Expected exactly one top-front edge");
    }

    // Radius 2; circular section; G1 setting; default blend thumbweight.
    CheckFilletStatus(SmApiFilletEdges(
        body.get(), selected, 2.0, 1, 1, 1.0), "FilletEdges failed");
    // These are borrowed pointers; discard them after topology mutation.
    selected.ReSet();
    edges.ReSet();

    SmBoolean manifold = FALSE;
    CheckFilletStatus(SmApiBrepIsManifoldSolid(
        body.get(), manifold), "Manifold query failed");
    double volume = 0.0;
    CheckFilletStatus(SmApiBrepComputeVolume(
        body.get(), 1.0e-6, volume), "Volume query failed");
    const double pi = std::acos(-1.0);
    const double expectedVolume = 1920.0 - 20.0 * 4.0 * (1.0 - pi / 4.0);
    if (!manifold || std::abs(volume - expectedVolume) > 1.0e-3)
    {
        throw std::runtime_error("Fillet result failed the example checks");
    }
    return body;
}
```

The radius and acceptance thresholds are for this fixture, not universal
defaults. The wrapper mutates the owned body. On any thrown failure the local
owner destroys that working body; this helper never retries partially modified
geometry. On success the caller owns the returned solid and must retain its
context through destruction. There is no ownership transfer of selected edges
to the application, and old edge pointers must not be used after the fillet.

For display, pass the returned solid to `SmApiTessellate` as described in
[tessellation.md](tessellation.md). A Qt viewport draws the resulting mesh;
the fillet construction itself does not depend on Qt.

### 8.4 Independent expected results

The ideal removed YZ area is a square minus a quarter-disk. Therefore

$$
\Delta V=Lr^2\left(1-\frac\pi4\right),\qquad
V_{\rm result}=LWH-\Delta V\approx1902.831853072.
$$

The block's overall extrema remain $(0,0,0)$ and $(20,12,8)$. At $x=10$, the
new boundary should follow the quarter-circle centered at $(y,z)=(2,6)$ with
radius 2; its two contacts are $(10,0,6)$ and $(10,2,8)$.
Check these section points, face normals at the rails, closure at both ends,
and material validity. Volume plus manifold status is a useful initial check,
not a complete proof of local surface accuracy. Avoid a fixed face-count test:
equivalent geometry can be represented with different partitions.

### 8.5 Three fillets meeting at one 3D corner

When three mutually perpendicular edges are rounded with the same radius, their
cylindrical strips need a transition at the shared corner. In the ideal symmetric
convex case, a spherical octant provides that corner patch:

![Three cylindrical fillet strips joined by an ideal spherical corner patch](assets/fillets/three_edge_corner_3d.svg)

Orange shows the three edge-filleting surfaces; green shows the corner patch.
Only the transition surfaces are shown, with neighboring planar faces omitted.
Coordinates are local to the sphere center and divided by the radius.
[PNG alternative](assets/fillets/three_edge_corner_3d.png).

For sphere center $\mathbf c$, the positive-octant patch can be parameterized as

$$
\mathbf K(u,v)=\mathbf c+r
\begin{bmatrix}
\cos v\cos u\\\cos v\sin u\\\sin v
\end{bmatrix},\qquad 0\leq u,v\leq\frac\pi2.
$$

The sphere and each quarter-cylinder share positions and normals along their
common quarter-circle. Their principal curvatures differ: a cylinder has
magnitudes $(1/r,0)$, while a sphere has $(1/r,1/r)$. Thus a visually smooth
corner can still be only $G^1$ across that boundary.

For a kernel example involving all twelve box edges, create a **fresh** box,
retrieve all its edges, and pass the whole selection to one `SmApiFilletEdges`
call with radius 2. Do not run that variant on the already filleted body above,
and do not reuse its edge array. The volume formula in Section 8.4 then no longer
applies because the other edges and eight corners also remove material.

The spherical illustration is an ideal equal-radius construction, not a promise
that the kernel always builds spherical corner geometry. Unequal radii, curved
supports, concavity, and mixed continuity can require different patches. The
current `SmApiFilletEdges` declaration explicitly limits three-edge corner
boundary guarantees to $G^1$, even when the blend cross-section continuity is
set to 2 or 3. Corner treatment is a separate part of the 3D algorithm.

### 8.6 Reproduce the illustrations

The [figure generator](assets/fillets/generate_figures.py) evaluates the explicit
surfaces above and checks radii, contact positions, and spherical interface
geometry. It does not call SMLib:

```powershell
uv run --no-project --with numpy --with matplotlib python mydocs/assets/fillets/generate_figures.py
```

## 9. Verification and failure localization

Check contact positions, tangent-plane continuity, trim agreement, corner closure,
and the resulting solid. A smooth tessellated highlight can hide a small gap or
an incorrectly oriented face. Conversely, coarse tessellation can make a valid
transition appear faceted.

Classify failures by edge eligibility, spine solve, contact tracing, section
generation, self-intersection, corner construction, or global insertion/merge.
Use the first failing stage to choose the next diagnostic. Raising tolerances
or suppressing corner checks without measuring their effect changes the model's
quality contract.

Related guides: [solvers](solvers.md), [booleans](booleans.md),
[offsets/shells](offsets-shells.md), and [tessellation](tessellation.md).
