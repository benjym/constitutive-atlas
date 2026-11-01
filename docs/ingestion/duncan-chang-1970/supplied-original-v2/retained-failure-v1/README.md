# Retained initial algebra-check failure

The initial source checker doubled Mandel shear compliance and failed its independent six-component Hooke inverse: recovered8 versus expected4. Eq15 uses engineering gamma, whereas Mandel strain is gamma/sqrt(2) and Mandel stress is sqrt(2)*tau. Thus Mandel compliance is (1+nu)/E, not2(1+nu)/E. The failed checker is retained here; the corrected checker and packet use the independently confirmed factor. No compiled/model observations occurred and no acceptance gate was changed.

Command: python3 -B docs/ingestion/duncan-chang-1970/supplied-original-v2/retained-failure-v1/check_algebra.py
Expected retained result: AssertionError (Fraction(8,1), Fraction(4,1)).
