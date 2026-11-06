# Current illustration asset handoff

## Coordinate contract

- Five animals: `cat`, `dog`, `bear`, `fox`, `rabbit`.
- New artwork: transparent RGBA PNG, **300 x 320** canvas, same scale, position,
  seated orientation and outline treatment as the approved portraits.
- Do not crop individual poses to their visible bounds. All frames must line up.
- Runtime atlas: **1200 x 1920**, four 300 x 320 columns and six rows in order:
  `typing`, `mouse`, `watching`, `gaming`, `idle`, `sleep`.
- Existing portraits are in `assets/illustrations/`. Most originals are smaller
  than the canonical canvas; `pad_portrait()` in
  `tools/generate_chibi_animations.py` centers them horizontally at y=14.
  The dog uses `assets/illustration_sources/dog_original.png` with the approved
  drooping-ear repair. Use canonical atlas cells as alignment references.

## Required shop artwork

Current computer, desk and desk-prop art is rendered as SVG scene equipment.
The approved PNG already contains the blue hoodie, chair, arms and paws.
Changing the old SVG outfit/hat arguments does not change that PNG.

Integrated: `pajamas` portraits for all five animals in
`assets/illustrations/pajamas/`, with matching four-frame/six-mode atlases in
`assets/animations/pajamas/`. The shared scene selects these when pajamas are
equipped or previewed; hoodie uses the original portraits and atlases.
The supplied canonical 300 x 320 canvases are used without padding or dog-ear
reconstruction. The existing deformation generator animates the painted poses;
these are not separately hand-drawn action frames.

Still needed to make the remaining costume purchases visibly distinct:

| Item IDs | Needed artwork |
|----------|----------------|
| `suit` | One full portrait variant per animal, preserving chair, head, paws and coordinates |
| `cat_ears`, `ribbon`, `bunny_ears` | Three transparent head-accessory layers per animal, aligned to the same full canvas |

Keep a matching editable layered source (PSD, Krita or equivalent) for every
animal. Separate body/clothes, left sleeve/paw, right sleeve/paw, head/face and
chair. Remove the original hand from the underlying layer before adding a
movable hand; never paste a second arm over a finished portrait.

An approved static costume portrait can feed the existing atlas generator.
Custom hand poses should instead be supplied as aligned frames. Animated
headwear must follow the corresponding head positions, not stay fixed in space.
Runtime loading for the remaining costume and headwear layers will be wired when
approved assets are supplied; merely adding arbitrary PNG filenames is not yet
a supported installation mechanism.

## Expression and popcorn pose request

Suggested expressions: neutral, happy, curious, sleepy, surprised and chewing.
Prefer full aligned portrait variants initially: an expression pasted over
existing eyes/mouth leaves duplicate facial features. Layer-only expressions
need a matching clean head base without those original features.

For a clearly articulated popcorn action, supply four frames:

1. Right paw at the popcorn rim; left paw resting.
2. The same right paw lifting one kernel.
3. Paw/kernel at the mouth, with a chewing expression.
4. Paw returning toward the tub.

Keep the head/body anchor steady. The kernel should stay with the paw until
the bite; do not add another hand. Current existing-paw deformation and snack
effects can be used while the separately drawn articulated poses are prepared.

## Review before integration

- First deliver one animal (cat) with the four watching poses and one outfit
  variant for alignment review, then expand to all five animals.
- Include the editable layered source, individual transparent frames and a
  contact sheet. Keep the approved original artwork intact.
- Verify at 160 x 96 shop-card size as well as 480 x 288 scene size.
- New expressions/cosmetic artwork requires approval and runtime integration;
  it is not generated or silently substituted by this guide.
