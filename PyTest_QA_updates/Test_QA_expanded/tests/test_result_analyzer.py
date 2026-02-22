import pytest
from unittest.mock import Mock, patch

from src.testing.result_analyzer import ResultAnalyzer

# INIT TESTS

def test_init_with_empty_list():
    with pytest.raises(ValueError):
        ResultAnalyzer([])

def test_init_with_valid_data():
    data = [1.0, 2.0, 3.0]
    analyzer = ResultAnalyzer(data)
    assert analyzer.data == data

# ANALYZE TESTS

def test_analyze_calculations():
    data = [1.0, 2.0, 3.0]
    analyzer = ResultAnalyzer(data)
    results = analyzer.analyze()
    
    assert results["mean"] == 2.0
    assert results["median"] == 2.0
    assert results["std"] == pytest.approx(1.0)
    assert results["min"] == 1.0
    assert results["max"] == 3.0

def test_analyze_with_even_number_of_values():
    data = [10, 20, 30, 40]
    analyzer = ResultAnalyzer(data)
    results = analyzer.analyze()
    
    assert results["median"] == 30

def test_analyze_with_identical_values():
    data = [2.0, 2.0, 2.0]
    analyzer = ResultAnalyzer(data)
    results = analyzer.analyze()
    
    assert results["std"] == pytest.approx(0.0)

def test_analyze_return_expected_keys():
    data = [1.0, 2.0, 3.0]
    analyzer = ResultAnalyzer(data)
    results = analyzer.analyze()
    
    expected_keys = {"mean", "median", "std", "min", "max"}
    assert set(results.keys()) == expected_keys

@patch("src.testing.result_analyzer.plt.show")
@patch("src.testing.result_analyzer.plt.hist")
def test_visualize_data_calls_matplotlib(mock_hist, mock_show):
    data = [1, 2, 3, 4]
    analyzer = ResultAnalyzer(data)

    analyzer.visualize_data()

    assert mock_hist.called
    assert mock_show.called 
