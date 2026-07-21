# Portable visual assets

`THEKEY_hero_chess.png` was generated for this project with OpenAI image
generation on 2026-07-21. The user-provided premium chess UI screenshot was
used only as a composition, palette, and mood reference. The generated asset
contains no copied interface, text, logo, or watermark and is distributed only
as the portable launcher's background artwork.

`THEKEY_hero_canonical_decor.png` is a transparent exact-pixel crop of the
user-authorized canonical reference. It contains only the hero's non-interactive
king, chessboard, lighting, texture, and landscape fragments; all text, the
local-mode control, CTA, cards, and other interface controls remain native WPF.
Regenerate it with `./scripts/extract-canonical-hero-decor.ps1` after an
authorized canonical-reference update.

`THEKEY_sidebar_canonical_decor.png` applies the same rule to the sidebar's
non-interactive crown, halo, texture, and landscape. Its text and navigation
controls are transparent masks, so they remain native WPF. Regenerate it with
`./scripts/extract-canonical-sidebar-decor.ps1` after an authorized canonical
reference update.

`THEKEY_mode_king_canonical_decor.png` and
`THEKEY_mode_checkmate_canonical_decor.png` contain the modes' exact interior
textures and non-interactive emblems. Native WPF renders their cards, badges,
and text. Regenerate both with `./scripts/extract-canonical-mode-decor.ps1`.

`THEKEY_app_icon.png` was generated in the same workflow as a project-owned
taskbar/application mark. It combines a chess king and keyhole shield without
third-party text or logos and is converted into the embedded Windows icon by
the portable build script.

`THEKEY_cinematic_loop_5s.mp4` is retained as a legacy project-owned asset but
is not packaged or rendered by the canonical desktop experience.
