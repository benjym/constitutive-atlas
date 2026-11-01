# Maxwell measurement-unit provenance delta

The broad Maxwell source manifest still contains exactly 149 files. Its sole delta adds `kPa/h` → `Pa/s` and `Hz` → `Hz` aliases in atlas/measurement_units.py. These support measurement-data preparation. No compiler, runtime, schema, constitutive definition, scalar helper or reference changed.

The cmake/maxwell recipe lists atlas/*.py as conservative generation dependencies; atlas.compiler and its imported modules do not import measurement_units. Compare the complete before/current source manifest and trace Python imports rather than infer numerical impact from the filename. The dedicated generated models.json must still regenerate byte-for-byte through the existing bundle guard.

Proposed scope: retain the exact independently reviewed compiled engine and all original bounded gates. Change only repository provenance binding after separate review. Preserve the original qualification, review, archives, failed CI and reference policy. The strict source-manifest equality and all other bundle checks remain unchanged. No rebuild, new numerical qualification, browser verification or live delivery is claimed by this rebind.

The reviewer supplies a new actual build-review.json only if the complete delta is independently accepted. The coordinator will bind a new qualification to those exact review bytes and repoint provisioning to that new packet, while reading the original unchanged compiled archive.
