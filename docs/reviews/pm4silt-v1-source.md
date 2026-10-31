# PM4Silt Version1 (2018): bounded source acquisition dossier

Verified 2026-10-31. Candidate `pm4silt`; no executable admission, transcription-complete status or scientific review granted. Repository unchanged. No DLL, driver or author source execution.

## Exact retained identity and acquisition

Boulanger, R.W. and Ziotopoulou, K. (2018), *PM4Silt (Version1): A Silt Plasticity Model for Earthquake Engineering Applications*, UCD/CGM-18/01, UC Davis Center for Geotechnical Modeling. The acquired109-page PDF cover and edition leaf identify January2018/first edition. It is not a claim to contain a later July2018 revision, nor a latest-release claim. No DOI is assigned in this dossier.

The [author files page](https://pm4silt.engr.ucdavis.edu/pm4silt-files), Version1 section, links the [manual](https://ucdavis.box.com/s/3b0vysopws6tsl96akj8y1mcdr05sqz1), [DLL ZIP](https://ucdavis.box.com/s/q355r76ncqwnn6c1qht6hw5m9lyt6sm0) and [driver ZIP](https://ucdavis.box.com/s/y4eqo72m3g5w2y1bwewhqe4qf4o6m12a). These three payloads are pinned privately, with receipts in the source-audit JSON. The manual bytes match the [Itasca-hosted original](https://itasca-software.s3.amazonaws.com/udm-library/Boulanger_Ziotopoulou_PM4Silt_Model_CGM-18-01_2018.pdf). The DLL archive contains exactly one compiled DLL, not C++ source. Driver archive contains four FISH/project pairs. Reading archive members did not execute them. Downloads filename inventory (`silt|pm4|boulanger|zior`, case-insensitive) found no matching local copy; this is not a full content search.

The author page labels the V1 DLL as compiled January17,2018 for FLAC8 dynamic analysis with VC++2015. Its separate later-release note identifies initialization and elastic stress-ratio changes and says calibrations should be checked when changing releases. That note is a version-separation receipt, not an acquired versioned changelog file. Direct author HTML retrieval returned403; web-reader access succeeded. Box landing HTML was acquired privately; static payload downloads succeeded. NSF mirror attempt timed out. No license or source-code grant was inferred from download availability.

## Dimensional and convention gate

Manual printedpp11–12, Eqs1–8 (PDFpp16–17): effective stress uses an in-plane2x2 tensor, p=(sigma_xx+sigma_yy)/2 and s=sigma-pI. This is a plane strain implementation; a six-Mandel3D rate with p=trace(sigma)/3 would change the formulation. Shear entries in those Cartesian matrices are tensor shear; engineering shear and Mandel conversion require explicit adapters. Eq6 subtracts epsilon_v/3 even though displayed in-plane stress decomposition uses p/2; preserve the source convention and resolve the implied out-of-plane strain component before defining storage. Table3.2 uses FLAC tension-positive signs; its negative p must be converted deliberately if Atlas uses compression-positive inputs. No unrestricted3D model is justified.

The minimal independent fixture here checks only Eqs1–4 in compression-positive SI project coordinates: [sigma_xx,sigma_yy,sigma_xy]=[100000,50000,30000]Pa gives p75000Pa, s=[25000,-25000,30000]Pa, r=[1/3,-1/3,2/5], and r:r=122/225. It distinguishes the source mean from an arbitrary3D embedding with sigma_zz40000Pa (mean63333.33Pa). It checks90-degree in-plane rotation, scale invariance and zero deviator without inventing a unit direction. This is algebra, not initialization or a stress update.

## Source/operation inventory

| Source locator (printed page; PDF page = printed+5 for main text) | Inventory and implementation implication |
|---|---|
|Abstract p i; pp1–10|Low-plasticity saturated silts/clays; no cap. Does not model consolidation settlement or strength evolution from consolidation history. Do not supply MCC-style OCR evolution by analogy.|
|pp12–15, Eqs9–21|Linear critical state relation in e-ln(p), state parameter; separate wet/dry bounding laws, dilatancy and critical surfaces; small translated yield cone, image back-stress ratios. Requires branch and domain inventory before transcription.|
|pp15–17, §2.5|Current, true/apparent initial and previous back-stress history; reversal logic cannot be reconstructed from current stress alone.|
|pp17–24, §§2.6–2.7|Stress-dependent elasticity; loading index with nonnegative plastic multiplier, hardening, dilatancy and reversal-related factors. Not a simple yield/return pair.|
|pp24–32, §2.8|Fabric tensor/history, accumulated and peak fabric and pressure-fabric terms, including reversal-dependent terms. Full history checkpoint is required.|
|pp32–34, two §§2.9|Post-shaking strength reduction and reconsolidation controls; named external operations, not automatic physical time or creep.|
|pp34–42, Table2.1|Constitutive equation summary; complete visual equation audit still pending.|
|pp52–55, §3.1–3.3|Explicit FLAC update, four-subzone area averaging, consistency/bounding corrections; D and Kp lag one zone step. Parallel nominal shear resistance controls hourglass modes. No constitutive substepping in this implementation; caller/global step sensitivity remains necessary.|
|pp56–57, Table3.1|Subzone elastic trial/yield/penalties followed by zone averaging, reversal, D/Kp, fabric, surfaces, moduli and history commit. Ordered phases and data locality are part of the algorithm.|
|pp58–59, Table3.2|Initialization/reset includes tensile/low-p handling, CSL placement, bounding correction, back-stress/history and fabric setup. FirstCall resets history; it is not ordinary continuation.|
|pp64–68, Tables4.1–4.2|Primary inputs, default material parameters, flags, unit pressure and calibration conventions.|
|p69, Table4.3|Tracking names aid a state inventory but do not constitute a complete independent-state layout.|
|pp70–95, §§4.2–4.3|Default and soil-specific calibration examples; calibrate strength, G_o then h_po after other settings. Separate numerical model match from experimental validation.|

Visual inspection used Poppler rendering for PDFpp16–17,61–64,70,72. Text extraction located additional sections; rows not in this visual subset remain inventory pointers, not equation verification.

## Inputs, state, initialization and domain proposal

Primary soil inputs: critical-state undrained strength **or** strength ratio, G_o, h_po; optional F_su. Operational inputs: FirstCall, PostShake and atmospheric pressure/unit system. Table4.1 says explicit strength takes precedence when both strength and ratio are supplied; ratio uses consolidation vertical effective stress at initialization. An Atlas API should expose this precedence and distinguish reset from continuation.

Twenty secondary entries in Table4.2: n_G,h_o,e_o,lambda,phi_cv,n_bwet,n_bdry,n_d,A_do,ru_max,z_max,c_z,c_e,C_GD,C_kaf,nu_o,c_rhg,c_hg,PostShake,C_GC. Resolve FLAC spellings/units and internal constants separately. Secondary zero-as-default is source input syntax; a canonical explicit-parameter schema should record whether defaulted or supplied rather than silently making physical zero impossible. No universal admissible range is established by a calibration default.

State inventory must cover in-plane effective stress and void ratio; alpha and true/apparent/previous/reversal bounds; fabric z,z_in,z_d,z_cum,z_peak; pressure-fabric history; strain accumulators; committed D,Kp,G,K; and operational stage flags/strength-line position. This is a candidate inventory, not a claim all tracked quantities are independent state or a final count. Subzone versus zone storage and lagged values must be explicit. Archive driver FISHs reset First_Call before loading; projects declare axisym false and dynamic true.

Source restrictions include positive compressive pressure for logarithms/stress ratio, finite elastic/yield denominators and parameter factors, and explicit low-pressure/bounding corrections. The algorithm itself contains corrections; an independent Atlas domain policy must not silently replace these with rejection or generic clamping. Critical-state pressure floors and tensile initialization require exact source/sign review. Initial stress checks and corrections in Table3.2 modify committed stress; distinguish a prepared state from raw user input. No source law for arbitrary OCR preparation is acquired.

Two unresolved transcription cautions are retained: (1) Table3.2 p59 initializes G using a square-root pressure factor, whereas Tables4.1–4.2 p65–66 give generalized exponent n_G with default.75. Startup versus ordinary evolution may intentionally differ; do not select one by analogy. (2) Table3.2 low-p lines mix signed FLAC p with p_min notation; Table4.2 p67 and §3.1 p53 give different prose forms requiring reconciliation against exact code/author clarification. Equality branches, zero-distance yield normal and reversal ties also need explicit treatment. The simplified pseudocode is not sufficient to infer all these branches.

## Licensing and next bounded packet

Manual/ZIPs/HTML/rendered pages/extracted text stay private and are excluded from the public whitelist. No standalone license/readme is present in either archive; no license/permission notice was found by a bounded search of four FISHs. This does not prove absence of applicable terms elsewhere. Public availability of a compiled DLL is not an open-source license. No C++ constitutive source or independent versioned changelog was acquired. No permission to redistribute the original payloads is claimed.

Next meaningful packet: source-located2D initialization and phase/state dependency table, resolving the two cautions above and identifying what a homogeneous single-material-point reduction preserves versus changes relative to four-subzone FLAC. Obtain author C++ source/license if offered; otherwise preserve manual-only branch gaps. Then independently test elastic/no-direction, yield onset, reversal, wet/dry state crossing, low-p correction, reset versus continuation and post-shaking transitions. Any implementation reduction needs a distinct variant identifier, convergence tests and explicit scope. No native target or webpage execution promotion is justified by acquisition alone.

Reproduce only the independent algebra fixture from a repo overlay:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/atlas-pm4silt-v1-source-20261031-v1:/Users/bmar5496/code/constitutive-atlas python3 -m unittest discover -s /private/tmp/atlas-pm4silt-v1-source-20261031-v1/tests -p test_pm4silt_v1_inplane_fixture.py

Four groups passed. The fixture has no dependency on Atlas, DLLs or author drivers. Public files and private source receipts are pinned in the manifest/audit JSON.
