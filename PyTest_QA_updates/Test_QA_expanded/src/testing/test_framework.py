import uuid

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from src.testing.measurement_session import MeasurementSession
from src.testing.result_analyzer import ResultAnalyzer
from src.testing.result_repository import ResultRepository
from src.utils.config import load_config


class AmmeterTestFramework:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.uuid = uuid.uuid4()

    
    def create_ammeter(self, ammeter_type: str):
        """
        Creates an instance of the specified ammeter type using the configuration.        
        :param ammeter_type: The type of ammeter to create (e.g., "GreenleeAmmeter", "EntesAmmeter", "CircutorAmmeter")
        :type ammeter_type: str
        :return: An instance of the specified ammeter
        :rtype: CircutorAmmeter | EntesAmmeter | GreenleeAmmeter
        :raises ValueError: If an unknown ammeter type is specified
        """
        ammeter_map = {
            "GreenleeAmmeter": ("greenlee", GreenleeAmmeter),
            "EntesAmmeter": ("entes", EntesAmmeter),
            "CircutorAmmeter": ("circutor", CircutorAmmeter),
        }

        if ammeter_type not in ammeter_map:
            raise ValueError(f"Unknown ammeter type: {ammeter_type}")

        config_key, ammeter_class = ammeter_map[ammeter_type]
        port = self.config["ammeters"][config_key]["port"]

        return ammeter_class(port)
        
    def run_test(self, ammeter_type: str) -> dict:
        """
        Runs the test for the specified ammeter type, including measurement, analysis, and result saving.        
        :param ammeter_type: The type of ammeter to test (e.g., "GreenleeAmmeter", "EntesAmmeter", "CircutorAmmeter")
        :type ammeter_type: str
        :return: The data that was saved to the file by the ResultRepository
        :rtype: dict
        """
        ammeter = self.create_ammeter(ammeter_type)
        measurements_count = self.config["testing"]["sampling"]["measurements_count"]
        total_duration_seconds = self.config["testing"]["sampling"]["total_duration_seconds"]
        try:
            session = MeasurementSession(ammeter, measurements_count, total_duration_seconds)
            data = session.run()
        except Exception as e:
            raise(f"Error during measurement session: {e}")
        print(len(data))
        print(data)
        try:
            analyzer = ResultAnalyzer(data)
            analysis_results = analyzer.analyze()
            # analyzer.visualize_data()
        except Exception as e:
            raise(f"Error during result analysis: {e}")
        print(analysis_results)
        try:
            repository = ResultRepository(str(self.uuid), ammeter.__class__.__name__, {"measurements_count": measurements_count, "total_duration_seconds": total_duration_seconds}, analysis_results)
            result_data = repository.save_results()
        except Exception as e:
            raise(f"Error during result saving: {e}")
        return result_data

