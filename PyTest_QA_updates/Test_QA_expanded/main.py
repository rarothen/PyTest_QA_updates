import threading
import time

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.client import request_current_from_ammeter
from src.testing.test_framework import AmmeterTestFramework
from src.testing.result_repository import ResultRepository
from src.testing.result_analyzer import ResultAnalyzer
from src.testing.measurement_session import MeasurementSession
from src.utils.config import load_config

def run_greenlee_emulator():
    greenlee = GreenleeAmmeter(5001)
    greenlee.start_server()

def run_entes_emulator():
    entes = EntesAmmeter(5002)
    entes.start_server()

def run_circutor_emulator():
    circutor = CircutorAmmeter(5003)
    circutor.start_server()

if __name__ == "__main__":
    # Start each ammeter in a separate thread

    threading.Thread(target=run_greenlee_emulator, daemon=True).start()
    threading.Thread(target=run_entes_emulator, daemon=True).start()
    threading.Thread(target=run_circutor_emulator, daemon=True).start()

    # This section is commented out because it shouldn't work.
    # Read the README.md file as well as the source code if you need, and fix the problem.

    # Wait for the servers to start, if you have problem restarting the servers between runs try increasing sleep time.
    time.sleep(5)
    try:
        request_current_from_ammeter(5001, b'MEASURE_GREENLEE -get_measurement')  # Request from Greenlee Ammeter
    except Exception as e:
        print(f"Error requesting from Greenlee Ammeter: {e}")
    try:
        request_current_from_ammeter(5002, b'MEASURE_ENTES -get_data')  # Request from ENTES Ammeter
    except Exception as e:
        print(f"Error requesting from Entes Ammeter: {e}")
    try:
        request_current_from_ammeter(5003, b'MEASURE_CIRCUTOR -get_measurement -current')  # Request from CIRCUTOR Ammeter
    except Exception as e:
        print(f"Error requesting from Circutor Ammeter: {e}")
    
    test = AmmeterTestFramework()
    threads = []

    for ammeter_key in test.config["ammeters"]:
        t = threading.Thread(target=test.run_test, args=(ammeter_key,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    analyze = ResultAnalyzer()
    analyze.visualize_run(str(test.uuid))