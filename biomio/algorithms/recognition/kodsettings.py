from biomio.algorithms.features import (constructSettings, BRISKDetectorType)
from biomio.algorithms.logger import logger


class KODSettings:
    """
    Keypoints Object Detector's Settings class
    """
    neighbours_distance = 1.0
    detector_type = BRISKDetectorType
    settings = None
    probability = 25.0

    def exportSettings(self):
        return {
            'Neighbours Distance': self.neighbours_distance,
            'Probability': self.probability,
            'Detector Type': self.detector_type,
            'Detector Settings': self.settings.exportSettings()
        }

    def importSettings(self, settings):
        self.neighbours_distance = settings['Neighbours Distance']
        self.probability = settings['Probability']
        self.detector_type = settings.get('Detector Type')
        self.settings = constructSettings(self.detector_type)
        self.settings.importSettings(settings.get('Detector Settings', dict()))

    def dump(self):
        logger.info('Keypoints Objects Detectors Settings')
        logger.info('Neighbours Distance: %f' % self.neighbours_distance)
        logger.info('Probability: %f' % self.probability)
        logger.info('Detector Type: %s' % self.detector_type)
        self.settings.dump()
