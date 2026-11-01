"""Validate reviewed count conventions without equating storage with physics."""
from .common import ROOT, digest, read_json


def validate_model_annotations(annotations):
    if annotations['paper_annotation_version'] != 2:
        raise ValueError('scope-aware annotation version 2 required')
    records=annotations['models']
    ids=[m['model_id'] for m in records]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate model annotation ID')
    for model in records:
        path=ROOT/model['definition_path']
        if digest(path)!=model['definition_sha256_at_annotation']:
            raise ValueError(f"{model['model_id']}: source changed; review annotation before reuse")
        definition=read_json(path)
        for name, expected in model.get('source_reconciliation', {}).get('inputs_sha256', {}).items():
            if digest(ROOT/name) != expected:
                raise ValueError('source reconciliation input changed; review annotation before reuse')
        for evidence in model.get('numerical_evidence', []):
            if (evidence['definition_sha256'] != model['definition_sha256_at_annotation'] or
                    digest(ROOT/evidence['path']) != evidence['sha256']):
                raise ValueError('numerical evidence snapshot differs from annotated source')
        if set(model['parent_model_ids'])-set(ids):
            raise ValueError('unknown parent in annotation snapshot')
        material=[name for group in model['material_parameter_groups'].values() for name in group]
        nonmaterial=set(model['nonmaterial_parameters'])
        if len(material)!=len(set(material)) or set(material)&nonmaterial:
            raise ValueError('overlapping parameter classifications')
        if set(material)|nonmaterial != set(definition['parameters']):
            raise ValueError('role classifications must cover declared parameters exactly')
        counts=model['counts']
        if counts['material_constants']!=len(material) or counts['declared_parameters']!=len(definition['parameters']):
            raise ValueError('annotation role count disagrees with classifications')
        if not model['source_locators'] or any(not s.get('url') or not s.get('locator') for s in model['source_locators']):
            raise ValueError('missing source evidence locator')
        scope=model['component_count_scope']
        state={field['name']:field for field in definition['state']}
        transient=[name for name,field in state.items() if field.get('transient')]
        categories={'stored_stress_components':scope['stored_stress_fields'],
                    'persistent_internal_components':model['persistent_internal_fields'],
                    'bookkeeping_components':model['bookkeeping_fields'],
                    'transient_multiplier_components':transient}
        classified=[name for names in categories.values() for name in names]
        if len(classified)!=len(set(classified)) or set(classified)!=set(state):
            raise ValueError('state-role classifications must partition stored fields')
        for role,names in categories.items():
            actual=sum({'scalar':1,'sym':6}[state[name]['shape']] for name in names)
            if scope[role]!=actual:
                raise ValueError('supported-scope component count disagrees with stored fields')
        if scope['kinematics']=='axisymmetric_x_small_strain':
            if any(counts[key] is not None for key in ('stress_components_3d','persistent_internal_components_3d','bookkeeping_components_3d')):
                raise ValueError('unsupported 3D counts must remain null')
            if definition.get('formulation',{}).get('kinematics')!='axisymmetric_x':
                raise ValueError('axisymmetric annotation disagrees with declared model scope')
        dimension=model['independent_material_dimension']
        if dimension['value'] is not None and not dimension.get('review_evidence'):
            raise ValueError('independent material dimension requires specific review evidence')
    return records
