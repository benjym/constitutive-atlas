# Exact stored-step lattice refinement

Before this additional arithmetic study, preserve lattice-results.json unchanged. Its ideal decimal h lattice differs minutely from native binary64 h. A separate ieee-lattice.py will use Decimal.from_float for the exact stored double h and quantify final division rounding by one ulp of the nearest quotient. Compare the same original budget, without tuning or altering the source derivative. This strengthens step-representation bookkeeping; it does not supersede or hide the initial result.
