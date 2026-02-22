import uuid
import sys

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from src.testing.measurement_session import MeasurementSession
from src.testing.result_analyzer import ResultAnalyzer
from src.testing.result_repository import ResultRepository
from src.utils.config import load_config
from config.logger_config import logger



class AmmeterTestFramework:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.uuid = uuid.uuid4()

    
    def create_ammeter(self, ammeter_key: str):
        if ammeter_key not in self.config["ammeters"]:
            raise ValueError(f"Ammeter '{ammeter_key}' not found in config")

        ammeter_config = self.config["ammeters"][ammeter_key]
        class_name = ammeter_config["class"]
        port = ammeter_config["port"]
        ammeter_class = getattr(sys.modules[__name__], class_name, None)

        if ammeter_class is None:
            raise ValueError(f"Class '{class_name}' not found")

        return ammeter_class(port)
        
    def run_test(self, ammeter_key: str) -> dict:
        """
        Runs the test for the specified ammeter type, including measurement, analysis, and result saving.        
        :param ammeter_key: Key inside config["ammeters"]
        :type ammeter_key: str
        :return: The data that was saved to the file by the ResultRepository
        :rtype: dict
        """
        logger.info(f"Running test for ammeter: {ammeter_key}")
        ammeter = self.create_ammeter(ammeter_key)
        measurements_count = self.config["testing"]["sampling"]["measurements_count"]
        total_duration_seconds = self.config["testing"]["sampling"]["total_duration_seconds"]
        try:
            logger.info("Starting measurement session...")
            session = MeasurementSession(ammeter, measurements_count, total_duration_seconds)
            data, current = session.run()
        except Exception as e:
            logger.error(f"Error during measurement session: {e}")
            raise Exception(f"Error during measurement session: {e}")
        logger.info(f"len data {str(len(data))}")
        try:
            logger.info("Analyzing results...")
            analyzer = ResultAnalyzer(data)
            analysis_results = analyzer.analyze()
            # analyzer.visualize_data(ammeter_key, current)
        except Exception as e:
            logger.error(f"Error during result analysis: {e}")
            raise Exception(f"Error during result analysis: {e}")
        try:
            logger.info("Saving results...")
            repository = ResultRepository(str(self.uuid), ammeter.__class__.__name__, {"measurements_count": measurements_count, "total_duration_seconds": total_duration_seconds}, analysis_results)
            result_data = repository.save_results()
        except Exception as e:
            logger.error(f"Error during result saving: {e}")
            raise Exception(f"Error during result saving: {e}")
        return result_data