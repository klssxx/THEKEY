# THEKEY visual contract

Canonical source: `design/reference/THEKEY_BUILD_WEEK_CANONICAL.png` (1448 ×
1086 px, 96 DPI). It is comparison-only and is never loaded by the launcher.

## Regions

| Region | Canonical bounds (px) | Contract |
| --- | --- | --- |
| Title bar | `0,0,1448,48` | Compact gold-on-black brand at left and native window actions at right. |
| Sidebar | `0,48,270,1038` | Dark blue/black column, emblem, brand and seven navigational entries. |
| Hero | `270,48,1178,372` | Cinematic chess art to the right; serif title and bilingual copy to the left; local-mode pill. |
| Primary action | `317,302,690,112` | Gold outlined, real select-and-inspect action. |
| Operation cards | `312,432,1078,252` | Four equal dark cards: Verify, Repair, Judge demo, View results. |
| Upcoming modes | `312,723,1078,111` | THE KING and CHECKMATE; both visibly unavailable. |
| Real activity | `288,849,1132,211` | Recent real launcher activity only; a neutral empty state when none exists. |

## Tokens

- Canvas: `#030A12`; panels: `#071625` / `#0B1E31`.
- Primary gold: `#E8B33E`; muted gold border: `#8B642A`.
- Primary text: `#F4F1E8`; muted text: `#C8C2B8`; secondary: `#9BA8BA`.
- Success is reserved for a completed local action; pending uses gold; failure uses `#EF7D7A`.
- Brand headings use Georgia. Interface text uses Segoe UI. Neither is rasterized.
- Card radius: 10 px; pill radius: 22 px; standard spacing rhythm: 8, 12, 18,
  24, 42 px.

## Interaction and accessibility

All controls are native WPF controls with names, keyboard focus, hover,
pressed, disabled, and visible focus states. Icons are WPF vector geometry;
the supplied chess art is limited to non-interactive atmospheric backgrounds
and the brand mark. The layout uses native WPF measurement and the included
PerMonitorV2 manifest, not a scaled screenshot.

## Explicit exclusions

No CPU/RAM/health telemetry, synthetic percentages, fabricated activity,
invented result rows, fake security claims, or unsupported operations may be
shown. The activity table is deliberately empty until THEKEY itself has
completed an action. The reference image supplies composition only; text,
buttons, borders, cards and controls are reconstructed as real UI.

## Baseline differences to correct

The pre-existing launcher used an extra system dashboard, a short desktop
composition, Unicode icon glyphs, an expandable tools menu, and a console on
the home canvas. Those differ from the canonical composition and/or imply
uncomputed state. The Build Week implementation removes them from Home and
places real operation output in secondary views.
