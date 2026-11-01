"""Additional MD strict legacy/selector contracts; never accept admissible success here."""
import sys
sys.dont_write_bytecode=True
import re

NATIVE='explicit-gis20-occ-restart-duncan-v5'
NUMERICAL='md1997-source-admissible-v1'
POSITIVE_STDOUT='Source-admissible MD1997 numerical fixtures; inherited explicit-gis20-occ-restart-duncan-v5; models=16\n'
SELECTORS=('ATLAS_NATIVE_FIXTURES','ATLAS_NUMERICAL_FIXTURES')

def contracts():
    return [
        dict(id='md-legacy-explicit-v5',target='atlas_numerical_tests',native_selector=NATIVE,numerical_selector=None,returncode=1,stdout='Explicit valid-domain/GIS-depth20 fixtures; models=16\n',stderr='FD test outside domain\n'),
        dict(id='unknown-numerical',target='atlas_numerical_tests',native_selector=NATIVE,numerical_selector='unknown',returncode=1,stdout='',stderr='unknown numerical fixture profile\n'),
        dict(id='missing-native',target='atlas_numerical_tests',native_selector=None,numerical_selector=NUMERICAL,returncode=1,stdout='',stderr='MD1997 numerical fixture requires explicit-gis20-occ-restart-duncan-v5\n'),
        dict(id='incompatible-native',target='atlas_numerical_tests',native_selector='explicit-gis20-occ-restart-v4',numerical_selector=NUMERICAL,returncode=1,stdout='',stderr='MD1997 numerical fixture requires explicit-gis20-occ-restart-duncan-v5\n')]

def selector_env(base, native=None, numerical=None):
    env=dict(base)
    for key in SELECTORS:env.pop(key,None)
    if native is not None:env[SELECTORS[0]]=native
    if numerical is not None:env[SELECTORS[1]]=numerical
    return env

def require(condition, message):
    if not condition:raise ValueError(message)

def verify(row, expected):
    require(row.get('status')=='completed','MD process incomplete')
    for key in ['returncode','stdout','stderr']:
        require(type(row.get(key)) is type(expected[key]) and row[key]==expected[key], 'MD contract mismatch: '+key)
    require(row.get('effective_selectors')=={k:v for k,v in zip(SELECTORS,[expected['native_selector'],expected['numerical_selector']]) if v is not None},'MD effective selectors differ')

def verify_positive_log(text):
    # CTest hides passing stdout on its console. Its complete LastTest.log must
    # contain the exact new profile line, once, from the numerical test section.
    sections=re.split(r'(?m)(?=^\d+/\d+ Testing: )',text)
    matching=[section for section in sections if re.match(r'^\d+/\d+ Testing: atlas_numerical\n',section)]
    require(len(matching)==1,'missing/duplicate numerical CTest log section')
    section=matching[0]
    require(section.count('\nOutput:\n----------------------------------------------------------\n')==1 and section.count('<end of output>\n')==1,'missing/ambiguous numerical output region')
    output=section.split('\nOutput:\n----------------------------------------------------------\n',1)[1].split('<end of output>\n',1)[0]
    require(output.splitlines(keepends=True).count(POSITIVE_STDOUT)==1,'missing exact MD positive fixture output line')
    require(section.count(POSITIVE_STDOUT)==1 and text.count(POSITIVE_STDOUT)==1,'duplicate/metadata MD profile label')
    require('Test Passed.' in section,'numerical test did not pass')
    require('Strict original default fixtures;' not in section and 'Explicit valid-domain/GIS-depth20 fixtures;' not in section,'legacy profile used for positive numerical test')
