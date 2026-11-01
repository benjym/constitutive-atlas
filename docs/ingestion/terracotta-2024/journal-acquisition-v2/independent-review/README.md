# Independent Terra Cotta acquisition metadata review

Accepted the bounded metadata/access conclusions in [receipt.json](receipt.json). Exact saved publisher XML and Crossref records support CC BY4 metadata for the journal version of record; the separate Crossref TDM licences and SSRN predecessor remain distinct. This does not establish third-party measurement rights or close source acquisition.

All nine raw files match their recorded hashes. The2001-byte publisher response contains metadata only; the saved FULL/PDF routes record401/403/406. OpenAlex has only journal/SSRN locations and null direct PDF URLs; the nontruncated pinned author tree has no PDF/TeX filename. Independent Downloads verification counted20 immediate PDF filenames without reading their content. No network, PDF parsing, author code, builds or compiled artifacts were run.

Reproduce saved checks from repository root: `python3 -B docs/ingestion/terracotta-2024/journal-acquisition-v2/independent-review/check_saved.py`. [checks.log](checks.log) records the pass. Scientific equations, domain, parameters, complete E1 source closure and model approval remain open.
