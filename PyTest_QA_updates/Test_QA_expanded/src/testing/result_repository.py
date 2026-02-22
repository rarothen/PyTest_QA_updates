from datetime import datetime
import json
import os
import threading

from config.logger_config import logger

file_lock = threading.Lock()
class ResultRepository:
    def __init__(self, uuid: str, ammeter_type: str, sampling_config: dict, results: dict):
        self.uuid = uuid
        self.timestamp = datetime.now()
        self.ammeter_type = ammeter_type
        self.sampling_config = sampling_config
        self.results = results

    def file_exist(self, directory, search_string):
        for filename in os.listdir(directory):
            if search_string in filename:
                return filename
        return False

    def save_results(self)-> dict:
        """
        Saves the results to a JSON file in the "results" directory. The filename is generated using the timestamp and ammeter type.        
        :return: The data that was saved to the file
        :rtype: dict
        """
        try:
            results_dir = "results"
            os.makedirs(results_dir, exist_ok=True)

            result_data = {
                "ammeter_type": self.ammeter_type,
                "uuid": self.uuid,
                "timestamp": self.timestamp.isoformat(),
                "sampling_config": self.sampling_config,
                "results": self.results
            }
            file_name = self.file_exist(results_dir, self.uuid)
            if file_name:
                file_path = f"{results_dir}/{file_name}"
            else: 
                ts_str = str(self.timestamp).replace(':', '-').replace(' ', '_')
                file_path = os.path.join(results_dir, f"{self.uuid}_{ts_str}.json")
            
            with file_lock:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    data.append(result_data)
                else:
                    data = [result_data]
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                    file.flush()
                    os.fsync(file.fileno())

            return result_data
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise Exception(f"Error saving results: {e}")