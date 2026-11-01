# Preserve the published fifteen-model fixtures

Before any new MD fixture was compiled, CI-context comparison found that the original 582-file baseline preceded the published Ramberg–Osgood rotation fixture. This revision inserts that exact six-line source-compliance preparation block from commit `37d70660e3561c342bb114716c233a3d06651bcb` into a new isolated copy of accepted fixture v2.

The full published source snapshot, exact insertion and source freeze are retained. Removing the one published block recovers v2 byte-for-byte. Every MD numerical instruction, tolerance, probe, selector condition and corrected label is unchanged. All previous trees and reviews remain immutable. The added block restores the current published fifteen-model fixture baseline; it does not change any material definition or relax a gate.

Run `python3 -B verify.py` for source identity checks. No build or compiled call has occurred. Independent prospective review is required before the actual numerical test. The separately prepared CI dispatch implementation remains an additional integration prerequisite. Later published changes require another bounded drift check before shared integration.
