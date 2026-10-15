# Demo refresh

The refresh changes the presentation layer only. Keep your existing databases, environment files and database volumes when updating. No re-import or reset is needed.

## Recording flow

1. Open Overview and set search, dates and category to the records you want to present.
2. Select **Presentation view** in the top bar to hide administrative controls and use the compact page navigation. Select **Exit presentation** to restore the full workspace.
3. Open Relationship graph. Hover over an account to highlight its visible connections; select an account or edge to inspect its evidence. Zoom controls enlarge the canvas, which supports scrolling.
4. Review evidence, compare personas and export the current result set as needed.

The graph shows up to 24 accounts, prioritizing those with more connections. Identifier groups are layout aids, not confirmed identities. Reported trust remains a dashed link. Large groups may span multiple panels. Synthetic records remain labeled; records without supporting identifier links are never given invented connections.

## Validation

TypeScript checks passed for both dashboard variants. The hosted Worker build and integration checks are run before publication. Browser visual QA was unavailable in this environment; verify your recording viewport before capture.
