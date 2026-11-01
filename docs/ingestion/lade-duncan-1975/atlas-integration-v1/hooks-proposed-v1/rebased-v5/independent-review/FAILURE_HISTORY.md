# Retained findings and harness failures

- Actual v5 controller/app witness: old ordinary dropdown survives; hash route starts a second run. Exact observed JSON retained; v6 fixes it.
- Old J2 routing source gate fails hard-coded four-controller startup marker against v6. Corrected proposed marker/import check retains all other assertions and passes158checks. Old source and proposed test are preserved in context.
- Witness harness initially used one extra parent segment for its pure router import, then lacked a noop scrollIntoView mock. Corrected these fixture errors; actual source methods were unchanged.
- Relocated proposed J2 test initially omitted its supported explicit router-path argument; adding web/laboratory-controller-router.mjs resolves the module location without editing test source.
