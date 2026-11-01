Initial reviewer script treated every manifest as a flat filename/hash map.
The historical native-v5-review manifest is structured with identity, inputs and
files fields, so it attempted to read a file named identity and stopped before
any checkers. Corrected reviewer manifest reader only. No author files, saved
evidence, gates, builds or compiled calls changed.

The next run stopped on KeyError(files); the actual historical field name is
review_files. Corrected that reviewer field lookup before checker execution.
