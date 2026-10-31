# Additive provenance correction carried into v2

The frozen v1 source packet and v1 rate packet retain a historical extraction error: they say the pinned accepted manuscript p10 Eq38 has a minus unloading bracket. The [independent audit](../rate-review-v1/README.md) verified the exact718767-byte PDF, SHA256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`, and rendered the equation at high resolution. The printed bracket is **Q + f_di*a*sqrt(3)**. It agrees with Eq40 and AppendixC. This is a correction to the Atlas extraction, not a change to the author equation.

V2 names that plus provenance explicitly. All41historical Cartesian rate records and the source-consistent DSL rate expressions remain identical; no constitutive sign was changed to implement the correction. The v1 synthetic minus-slope diagnostic remains historical evidence of its own assumption, not a source-truth test. The audit lists affected old claims and exact page/crop coordinates; no old bytes are overwritten.

The [original DOI](https://doi.org/10.1002/nag.416) and [accepted manuscript](https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf) remain the source identities. Final-publisher equation equivalence has not been established, and this correction does not claim it. Raw PDF, extracted text and page images stay private.
