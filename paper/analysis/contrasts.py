"""Paired within-model calibration-design contrasts; no independent-sample inference."""
import math


def root_error(predictions, identifiers, stress_weight):
    """Require every scheduled test and both channels before an aggregate."""
    if not math.isfinite(stress_weight) or not 0 <= stress_weight <= 1:
        raise ValueError('stress weight must lie between zero and one')
    index = {p['experiment_id']: p for p in predictions}
    if len(index) != len(predictions):
        raise ValueError('duplicate contrast prediction')
    values = []
    for identifier in identifiers:
        prediction = index.get(identifier)
        if prediction is None or prediction['status'] != 'success' or not prediction.get('metrics'):
            return None
        metrics = prediction['metrics']
        for channel in ('q', 'volumetric_strain'):
            item = metrics[channel]
            if (not all(math.isfinite(item[k]) for k in ('rmse', 'scale', 'scaled_mse')) or
                    item['rmse'] < 0 or item['scale'] <= 0 or item['scaled_mse'] < 0 or
                    not math.isclose(item['scaled_mse'], (item['rmse']/item['scale'])**2, rel_tol=1e-9, abs_tol=1e-14)):
                raise ValueError('inconsistent or nonfinite contrast metric')
        values.append(stress_weight*metrics['q']['scaled_mse']+(1-stress_weight)*metrics['volumetric_strain']['scaled_mse'])
    if not values:
        raise ValueError('empty contrast group')
    return math.sqrt(sum(values)/len(values))


def design_contrasts(report):
    config = report['config']
    design = config['calibration_design_contrast']
    reference, alternative = design['reference_package'], design['alternative_package']
    groups = {'all_evaluation_tests': config['evaluation_ids'], **design['evaluation_groups']}
    summaries, per_test, starts = [], [], []
    for model in config['models']:
        mid = model['id']
        selected = {package: [p for p in report['predictions'] if p['model'] == mid and
                    p['package'] == package and p.get('selected')] for package in (reference, alternative)}
        for group, identifiers in groups.items():
            for weight in design['evaluation_stress_weight_sensitivity']:
                errors = {p: root_error(selected[p], identifiers, weight) for p in selected}
                complete = all(v is not None for v in errors.values())
                summaries.append({'model_id': mid, 'group': group, 'test_ids': identifiers,
                    'stress_weight': weight, 'complete': complete,
                    'reference_root_error': errors[reference], 'alternative_root_error': errors[alternative],
                    'root_error_change': errors[alternative]-errors[reference] if complete else None})
        by_package = {package: {p['experiment_id']: p for p in predictions} for package,predictions in selected.items()}
        for identifier in config['evaluation_ids']:
            pair = [by_package[p].get(identifier) for p in (reference,alternative)]
            complete = all(p and p['status'] == 'success' and p.get('metrics') for p in pair)
            item = {'model_id': mid, 'experiment_id': identifier, 'complete': complete,
                    'statuses': {package: prediction['status'] if prediction else 'missing_prediction'
                                 for package,prediction in zip((reference,alternative),pair)}}
            if complete:
                for channel in config['objective']['channels']:
                    a,b = [p['metrics'][channel] for p in pair]
                    if a['scale'] != b['scale']:
                        raise ValueError('paired tests must use identical physical scales')
                    item[channel] = {'reference_rmse': a['rmse'], 'alternative_rmse': b['rmse'],
                                     'rmse_change': b['rmse']-a['rmse']}
            per_test.append(item)
        for seed in config['optimizer']['seeds']:
            errors = {}
            for package in (reference,alternative):
                predictions = [p for p in report['predictions'] if p['model'] == mid and p['package'] == package and p.get('seed') == seed]
                errors[package] = root_error(predictions, config['evaluation_ids'], design['primary_stress_weight'])
            complete = all(v is not None for v in errors.values())
            starts.append({'model_id': mid, 'seed': seed, 'complete': complete,
                'reference_root_error': errors[reference], 'alternative_root_error': errors[alternative],
                'root_error_change': errors[alternative]-errors[reference] if complete else None})
    return {'summaries': summaries, 'per_test': per_test, 'same_seed_search_sensitivity': starts}
