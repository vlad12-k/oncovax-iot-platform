import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('worker_contracts', ROOT / 'services/worker/worker.py')
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


def validator(name):
    schema = json.loads((ROOT / 'schemas' / f'{name}.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


@pytest.fixture
def alert(monkeypatch):
    monkeypatch.setattr(worker, 'CONSECUTIVE_BREACH_REQUIRED', 2)
    monkeypatch.setattr(worker, 'TEMP_THRESHOLD', 8.0)
    worker.breach_state.clear()
    record = dict(device_id='contract-probe', asset_type='coldstorage',
                  ts='2026-08-10T10:00:00Z', metric='temperature', value=9.0, unit='C')
    validator('telemetry').validate(record)
    assert worker.evaluate_excursion(record) is None
    result = worker.evaluate_excursion(record)
    validator('alert').validate(result)
    assert worker.evaluate_excursion({**record, 'value': 4.0}) is None
    assert not worker.breach_state
    return result


def test_worker_output_and_api_acknowledgement_satisfy_contract(alert):
    from services.api.models import AcknowledgeRequest
    from services.api.routes.alerts import acknowledge_alert

    class Collection:
        def insert_one(self, document):
            self.document = copy.deepcopy(document)
        def update_one(self, query, update):
            assert query == {'alert_id': self.document['alert_id']}
            self.document.update(update['$set'])
            return SimpleNamespace(matched_count=1)
        def find_one(self, query, projection):
            return dict(self.document)

    collection = Collection()
    worker.write_audit_record(collection, alert)
    validator('audit_event').validate(collection.document)
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(collection=collection)))
    result = acknowledge_alert(collection.document['alert_id'],
                               AcknowledgeRequest(acknowledged_by=' Operator ', incident_note='Reviewed'), request)
    validator('audit_event').validate(result['item'])
    assert result['item']['acknowledged_by'] == 'Operator'
    assert result['item']['incident_note'] == 'Reviewed'


@pytest.mark.parametrize('field,value', [('value', 'hot'), ('ts', 'yesterday'),
                                        ('status', 'unknown'), ('consecutive_breach_count', 0)])
def test_alert_contract_rejects_invalid_output(alert, field, value):
    with pytest.raises(ValidationError):
        validator('alert').validate({**alert, field: value})


def test_incomplete_acknowledgement_is_invalid(alert):
    captured = []
    worker.write_audit_record(SimpleNamespace(insert_one=captured.append), alert)
    with pytest.raises(ValidationError):
        validator('audit_event').validate({**captured[0], 'acknowledged': True})


def test_simulator_normalization_matches_telemetry_contract():
    records = worker.to_canonical_records(dict(timestamp='2026-08-10T10:00:00Z',
        device_id='fridge-1', asset_type='vaccine fridge', temperature=4.5, humidity=50))
    assert {r['metric'] for r in records} == {'temperature', 'humidity'}
    for record in records:
        validator('telemetry').validate(record)
        assert record['asset_type'] == 'coldstorage'
