from datetime import datetime
import json
import os

class ResultRepository:
    def __init__(self, uuid: str, ammeter_type: str, sampling_config: dict, results: dict):
        self.uuid = uuid
        self.timestamp = datetime.now()
        self.ammeter_type = ammeter_type
        self.sampling_config = sampling_config
        self.results = results
    
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
                "uuid": self.uuid,
                "timestamp": self.timestamp.isoformat(),
                "ammeter_type": self.ammeter_type,
                "sampling_config": self.sampling_config,
                "results": self.results
            }
            ts_str = str(self.timestamp).replace(':', '-').replace(' ', '_')
            file_path = os.path.join(results_dir, f"{ts_str}_{self.ammeter_type}.json")
            with open(file_path, 'w') as f:
                json.dump(result_data, f, indent=4)

            return result_data
        except Exception as e:
            raise Exception(f"Error saving results: {e}")