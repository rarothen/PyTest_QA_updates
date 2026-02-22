import inspect
import pkgutil
import importlib
import socket
import pytest
from unittest.mock import patch, MagicMock

from Ammeters.base_ammeter import AmmeterEmulatorBase

# Dynamic subclass discovery (Extensible & Reusable)
def discover_ammeter_subclasses():
    import Ammeters

    subclasses = []

    for _, module_name, _ in pkgutil.iter_modules(Ammeters.__path__):
        module = importlib.import_module(f"Ammeters.{module_name}")

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, AmmeterEmulatorBase) and obj is not AmmeterEmulatorBase:
                subclasses.append(obj)

    return subclasses


AMMETER_CLASSES = discover_ammeter_subclasses()


# Shared Fixtures
@pytest.fixture
def ammeter_instance(request):
    cls = request.param
    return cls(port=12345)


# Tests get_current_command
@pytest.mark.parametrize("ammeter_instance", AMMETER_CLASSES, indirect=True)
def test_get_current_command_contract(ammeter_instance):
    cmd = ammeter_instance.get_current_command

    assert isinstance(cmd, bytes), \
        f"{ammeter_instance.__class__.__name__} must return bytes"
    assert len(cmd) > 0, \
        f"{ammeter_instance.__class__.__name__} returned empty command"

#Tests measure_current
@pytest.mark.parametrize("ammeter_instance", AMMETER_CLASSES, indirect=True)
def test_measure_current_contract(ammeter_instance):
    result = ammeter_instance.measure_current()

    assert isinstance(result, float), \
        f"{ammeter_instance.__class__.__name__} must return float"

    assert not (result is None), \
        f"{ammeter_instance.__class__.__name__} returned None"


@pytest.mark.parametrize("ammeter_instance", AMMETER_CLASSES, indirect=True)
def test_measure_current_deterministic_mock(ammeter_instance):

    module_path = ammeter_instance.__class__.__module__

    with patch(f"{module_path}.generate_random_float", return_value=1.0) as mock_random:
        result = ammeter_instance.measure_current()

        assert isinstance(result, float)
        assert result >= 0
        assert mock_random.call_count > 0

@pytest.mark.parametrize("ammeter_instance", AMMETER_CLASSES, indirect=True)
def test_measure_current_exception_handling(ammeter_instance):
    with patch.object(ammeter_instance, "measure_current", side_effect=RuntimeError):
        with pytest.raises(RuntimeError):
            ammeter_instance.measure_current()

# Test start_server
@pytest.mark.parametrize("ammeter_instance", AMMETER_CLASSES, indirect=True)
def test_start_server_single_request(ammeter_instance):
    mock_socket = MagicMock()
    mock_conn = MagicMock()

    mock_conn.recv.return_value = ammeter_instance.get_current_command
    mock_socket.accept.side_effect = [
        (mock_conn, ("127.0.0.1", 55555)),
        KeyboardInterrupt  # stop infinite loop
    ]

    with patch("socket.socket") as mock_socket_class:
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        with patch.object(ammeter_instance, "measure_current", return_value=3.14):
            try:
                ammeter_instance.start_server()
            except KeyboardInterrupt:
                pass

    mock_conn.sendall.assert_called_once_with(b"3.14")

@pytest.mark.parametrize("ammeter_instance", AMMETER_CLASSES, indirect=True)
def test_server_ignores_invalid_command(ammeter_instance):
    mock_socket = MagicMock()
    mock_conn = MagicMock()

    mock_conn.recv.return_value = b"INVALID_COMMAND"
    mock_socket.accept.side_effect = [
        (mock_conn, ("127.0.0.1", 55555)),
        KeyboardInterrupt
    ]

    with patch("socket.socket") as mock_socket_class:
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        try:
            ammeter_instance.start_server()
        except KeyboardInterrupt:
            pass

    mock_conn.sendall.assert_not_called()
