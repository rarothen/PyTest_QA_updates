import pytest
import time
from unittest.mock import Mock, patch

from src.testing.measurement_session import MeasurementSession

# INIT TESTS
def test_invalid_measurements_count():
    with pytest.raises(ValueError):
        MeasurementSession(Mock(), 0, 10)

def test_invalid_total_duration_seconds():
    with pytest.raises(ValueError):
        MeasurementSession(Mock(), 10, 0)

def test_sampling_interval_calculation():
    session = MeasurementSession(Mock(), 10, 100)
    assert session.sampling_interval == 10

# RUN TESTS
@patch('src.testing.measurement_session.time.sleep', return_value=None)
def test_run_measurement_session(mock_sleep):
    mock_ammeter = Mock()
    mock_ammeter.measure_current.side_effect = [1.0, 2.0, 3.0]
    
    session = MeasurementSession(mock_ammeter, 3, 6)
    results = session.run()
    
    assert len(results) == 3
    assert results == [1.0, 2.0, 3.0]
    assert mock_ammeter.measure_current.call_count == 3

@patch('src.testing.measurement_session.time.sleep', return_value=None)
def test_run_return_floats(mock_sleep):
    mock_ammeter = Mock()
    mock_ammeter.measure_current.side_effect = [1.5, 2.5, 3.5]

    session = MeasurementSession(mock_ammeter, 3, 6)
    result = session.run()

    assert all(isinstance(value, float) for value in result)

@patch('src.testing.measurement_session.time.sleep', return_value=None)
def test_run_handles_measurement_errors(mock_sleep):
    mock_ammeter = Mock()
    mock_ammeter.measure_current.side_effect = [1.0, Exception("Measurement error"), 3.0]

    session = MeasurementSession(mock_ammeter, 3, 6)
    results = session.run()

    assert len(results) == 2
    assert results == [1.0, 3.0]

@patch("src.testing.measurement_session.time.sleep", return_value=None)
def test_run_supports_any_object_with_measure_current(mock_sleep):
    class CustomAmmeter:
        def measure_current(self):
            return 1.0

    session = MeasurementSession(CustomAmmeter(), 2, 1)
    result = session.run()

    assert result == [1.0, 1.0]

@patch("src.testing.measurement_session.time.sleep", return_value=None)
def test_run_executes_fast_when_sleep_patched(mock_sleep):
    mock_ammeter = Mock()
    mock_ammeter.measure_current.return_value = 1.0

    session = MeasurementSession(mock_ammeter, 5, 1)

    start = time.perf_counter()
    session.run()
    duration = time.perf_counter() - start

    assert duration < 0.1