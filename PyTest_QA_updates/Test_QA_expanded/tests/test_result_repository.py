import pytest
import json
import os
from unittest.mock import patch, mock_open

from src.testing.result_repository import ResultRepository

# INIT TESTS
def test_init_sets_attributes():
    repo = ResultRepository(
        uuid="1234",
        ammeter_type="circutor",
        sampling_config={"count": 10},
        results={"mean": 5},
    )

    assert repo.uuid == "1234"
    assert repo.ammeter_type == "circutor"
    assert repo.sampling_config == {"count": 10}
    assert repo.results == {"mean": 5}
    assert repo.timestamp is not None


# SAVE RESULTS TESTS
@patch("src.testing.result_repository.os.makedirs")
@patch("src.testing.result_repository.open", new_callable=mock_open)
@patch("src.testing.result_repository.json.dump")
def test_save_results_success(mock_json_dump, mock_file, mock_makedirs):
    repo = ResultRepository(
        uuid="1234",
        ammeter_type="entes",
        sampling_config={"count": 5},
        results={"mean": 10}
    )

    result_data = repo.save_results()
    mock_makedirs.assert_called_once()
    mock_file.assert_called_once()
    mock_json_dump.assert_called_once()

    assert result_data["uuid"] == "1234"
    assert result_data["ammeter_type"] == "entes"
    assert result_data["sampling_config"] == {"count": 5}
    assert result_data["results"] == {"mean": 10}
    assert "timestamp" in result_data

@patch("src.testing.result_repository.os.makedirs")
def test_save_results_creates_valid_json_structure(mock_makedirs, tmp_path):
    repo = ResultRepository(
        uuid="abcd",
        ammeter_type="greenlee",
        sampling_config={"count": 3},
        results={"mean": 7}
    )

    with patch("src.testing.result_repository.os.path.join", side_effect=lambda *parts: str(tmp_path) + os.sep + parts[-1]):
        data = repo.save_results()

        files = list(tmp_path.iterdir())
        assert len(files) == 1
        with open(files[0], "r") as f:
            saved_data = json.load(f)
        assert saved_data == data


@patch("src.testing.result_repository.os.makedirs", side_effect=Exception("Disk error"))
def test_save_results_raises_exception(mock_makedirs):
    repo = ResultRepository(
        uuid="error-test",
        ammeter_type="circutor",
        sampling_config={"count": 1},
        results={"mean": 1}
    )

    with pytest.raises(Exception):
        repo.save_results()
