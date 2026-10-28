# Recovery package evidence

The production recovery kit holds only the used source windows (with short handles), not full third-party uploads, plus scripts, selected caption data, source credits, fonts, emoji and licenses. A stream-copy starts on an earlier keyframe, so the packager calibrates each planned segment against the original.

- **17 source window files**, 21 distinct edit ranges; all **21/21** tested calibration frames matched the original exactly at 160×90 grayscale (mean absolute error 0.0). This is a sampled frame check, not proof every frame is identical.
- An actual rebuild of the Jokers cannonball clip using the raw-window map completed. Six sampled decoded frames from the original-source render and the recovered render matched exactly at 160×90 grayscale. The decoded AAC audio had cross-correlation 0.843 at a best offset under 1 ms; it was not bit-identical. Different library versions and encoding passes will produce different MP4 hashes.
- The unmastered r01 draft's first recovery ZIP had SHA-256 `30db9299d4c040f02041d5b668cda207489dc61ae6c0877630d00ca39f4d1ea3` and remains in that draft as an additive checkpoint. The published r02 kit is repackaged with the mastering script and final documentation.
- Source 1 is not in the kit, because its age-restricted media could not be obtained. An authorized file must be supplied before those clips can be made.
