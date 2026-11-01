# Seams: the boundaries between graphics sections

Claude (Kiln, local), 1 Nov 2026. One row per boundary. gfx.py reads the Transition column (`flash 2`, `whip 3`, `slide 6`,
`mosaic 5`, or `hard`; the number is frames, 25 fps), so its form matters. An agent writes only its own side's cell; Kiln
settles a clash and sets the Transition. Sides: `open`, `proposed`, `built`, `Lati ok`.

| Cut | Time | Sections | Outgoing last beat | Incoming first beat | Transition | Outgoing side | Incoming side |
|---|---|---|---|---|---|---|---|
| s016 → s017 | 44.100 | A → B | "Ready?" held; drums out | the drop: [Y/n] answered, cannons fire | flash 2 | built | built (test) |
| s030 → s031 | 73.094 | B → C | "First time, every time" chant ends | "You bring me a bug at three a.m." at the desk | hard | built | built |
| s042 → s043 | 98.408 | C → B | "okay inside—" cut off | the walk, "(Ready?)" | hard | built | built |
| s053 → s054 | 123.639 | B → D | chorus 2's last "every time" | the call, half-time: "But that's exactly what I'd say" | hard | built | built |
| s059 → s060 | 149.061 | D → B | one bar of black | key change, the biggest stage | flash 2 | built | built |
| s067 → s068 | 168.948 | B → D | the last "hey" | "First time, every time", then the sustained vocal | hard | built | built |
