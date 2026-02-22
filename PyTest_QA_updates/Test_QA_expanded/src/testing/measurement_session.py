import time

from config.logger_config import logger


class MeasurementSession:
    def __init__(self, ammeter, measurements_count: int, total_duration_seconds: float):
        if measurements_count <= 0:
            raise ValueError("measurements_count must be greater than 0")
        if total_duration_seconds <= 0:
            raise ValueError("total_duration_seconds must be greater than 0")
        
        self.ammeter = ammeter
        self.measurements_count = measurements_count
        self.total_duration_seconds = total_duration_seconds
        self.sampling_interval = total_duration_seconds / measurements_count

    def run(self) -> list[float]:
        """
        Executes the measurement session by taking the specified number of measurements
        :return: Array of current measurements taken during the session
        :rtype: list[float]
        """
        measurement: list[float] = []

        start_time = time.perf_counter()
        next_sample_time = start_time

        for _ in range(self.measurements_count):
            try: 
                value, current = self.ammeter.measure_current()
                measurement.append(value)
            except Exception as e:
                logger.warning(f"Error during measurement: {e}")
                continue
            next_sample_time += self.sampling_interval
            sleep_time = next_sample_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
        return measurement, current