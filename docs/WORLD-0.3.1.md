# Bytecraft World 0.3.1

Continues the isolated `bytecraft-world-mvp` edition, Android package
`com.pazzia.bytecraftworld`. Main and Career are separate products.

## Visual update
- Bundled offline illustrated atlas: island IT city, mountain expedition,
  Bug Lord arena, Kai portrait.
- City labels use saved building levels. Tapping a building opens its real
  upgrade action; existing coin costs and persistence remain in the controller.
- Hub and city use a square map to preserve the art composition.
- Arena HP and expedition progress remain native Flutter UI, not painted text.
- Widget checks cover narrow-phone city taps and asset/layout failures.

Art generated using the built-in image tool. Prompt: four equal square
quadrants without gutters, UI or text; richly detailed 3D mobile adventure
art in navy, purple, turquoise and gold. Top left: five-building island IT
city; top right: mountain path with five stone platforms and treasure chest;
bottom left: purple robot Bug Lord with orange core; bottom right: friendly
anime programmer Kai in violet hoodie. File: assets/world/world-atlas.png.
Flutter clips quadrants at render time; no external image URLs are needed.

## Existing MVP limits
This is a visual milestone, not a production multiplayer release. Ghost PvP
and guild participants remain local simulations; Kai is scripted, not a live
LLM. The World challenge buttons still use the existing MVP progression;
full code-validated World challenges are a subsequent implementation task.
