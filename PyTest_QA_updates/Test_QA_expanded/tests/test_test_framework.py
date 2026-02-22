import pytest
from unittest.mock import Mock, patch

from src.testing.test_framework import AmmeterTestFramework

# INIT TESTS

@patch("src.testing.test_framework.load_config")
def test_init_loads_config(mock_load_config):
    mock_load_config.return_value = {"testing": {"sampling": {}}}

    framework = AmmeterTestFramework("dummy_path.yaml")

    mock_load_config.assert_called_once_with("dummy_path.yaml")
    assert framework.config is not None
    assert framework.uuid is not None

# AMMETER CREATION TESTS
@patch("src.testing.test_framework.CircutorAmmeter")
@patch("src.testing.test_framework.load_config")
def test_create_some_ammeter(mock_load_config, mock_circutor_class):

    mock_load_config.return_value = {
        "ammeters": {
            "circutor": {"port": 8000}
        }
    }

    framework = AmmeterTestFramework("dummy.yaml")

    framework.create_ammeter("CircutorAmmeter")

    mock_circutor_class.assert_called_once_with(8000)

def test_create_unknown_ammeter():
    framework = AmmeterTestFramework.__new__(AmmeterTestFramework)
    framework.config = {}

    with pytest.raises(ValueError):
        framework.create_ammeter("UnknownType")

# RUN TESTS

@patch("src.testing.test_framework.ResultRepository")
@patch("src.testing.test_framework.ResultAnalyzer")
@patch("src.testing.test_framework.MeasurementSession")
@patch("src.testing.test_framework.AmmeterTestFramework.create_ammeter")
@patch("src.testing.test_framework.load_config")
def test_run_test_success(
    mock_load_config,
    mock_create_ammeter,
    mock_session_class,
    mock_analyzer_class,
    mock_repository_class,
):

    # Mock config
    mock_load_config.return_value = {
        "testing": {
            "sampling": {
                "measurements_count": 3,
                "total_duration_seconds": 1
            }
        }
    }

    mock_ammeter = Mock()
    mock_ammeter.__class__.__name__ = "MockAmmeter"
    mock_create_ammeter.return_value = mock_ammeter

    mock_session = Mock()
    mock_session.run.return_value = [1.0, 2.0, 3.0]
    mock_session_class.return_value = mock_session

    mock_analyzer = Mock()
    mock_analyzer.analyze.return_value = {"mean": 2.0}
    mock_analyzer.visualize_data.return_value = None
    mock_analyzer_class.return_value = mock_analyzer

    mock_repository = Mock()
    mock_repository.save_results.return_value = {"saved": True}
    mock_repository_class.return_value = mock_repository

    framework = AmmeterTestFramework("dummy.yaml")
    result = framework.run_test("SomeType")

    assert result == {"saved": True}

    mock_create_ammeter.assert_called_once()
    mock_session.run.assert_called_once()
    mock_analyzer.analyze.assert_called_once()
    mock_repository.save_results.assert_called_once()


@patch("src.testing.test_framework.load_config")
@patch("src.testing.test_framework.AmmeterTestFramework.create_ammeter")
@patch("src.testing.test_framework.MeasurementSession")
def test_run_test_session_error(
    mock_session_class,
    mock_create_ammeter,
    mock_load_config
):
    mock_load_config.return_value = {
        "testing": {
            "sampling": {
                "measurements_count": 1,
                "total_duration_seconds": 1
            }
        }
    }

    mock_create_ammeter.return_value = Mock()

    mock_session = Mock()
    mock_session.run.side_effect = Exception("Session failure")
    mock_session_class.return_value = mock_session

    framework = AmmeterTestFramework("dummy.yaml")

    with pytest.raises(Exception):
        framework.run_test("AnyType")


@patch("src.testing.test_framework.ResultAnalyzer")
@patch("src.testing.test_framework.MeasurementSession")
@patch("src.testing.test_framework.AmmeterTestFramework.create_ammeter")
@patch("src.testing.test_framework.load_config")
def test_run_test_analysis_error(
    mock_load_config,
    mock_create_ammeter,
    mock_session_class,
    mock_analyzer_class,
):
    mock_load_config.return_value = {
        "testing": {
            "sampling": {
                "measurements_count": 1,
                "total_duration_seconds": 1
            }
        }
    }

    mock_create_ammeter.return_value = Mock()

    mock_session = Mock()
    mock_session.run.return_value = [1.0]
    mock_session_class.return_value = mock_session

    mock_analyzer = Mock()
    mock_analyzer.analyze.side_effect = Exception("Analysis failure")
    mock_analyzer_class.return_value = mock_analyzer

    framework = AmmeterTestFramework("dummy.yaml")

    with pytest.raises(Exception):
        framework.run_test("AnyType")
