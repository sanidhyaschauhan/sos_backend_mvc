import unittest
from unittest.mock import patch
from models.emergency_model import EmergencyModel
from neurelo_client import NeureloClient

class TestEmergencyApp(unittest.TestCase):

    @patch('neurelo_client.NeureloClient.get_reports_from_location')
    def test_determine_real_report(self, mock_get_reports):
        mock_get_reports.return_value = ['report1', 'report2']
        emergency_model = EmergencyModel()
        result = emergency_model.determine_real_report('New York', 'low', {"illegal_activity": None})
        self.assertTrue(result)

    @patch('neurelo_client.NeureloClient.get_reports_from_location')
    def test_determine_real_report_no_illegal_activity(self, mock_get_reports):
        mock_get_reports.return_value = []
        emergency_model = EmergencyModel()
        result = emergency_model.determine_real_report('New York', 'low', {"illegal_activity": None})
        self.assertFalse(result)

    @patch('neurelo_client.NeureloClient.get_reports_from_location')
    def test_determine_real_report_with_illegal_activity(self, mock_get_reports):
        mock_get_reports.return_value = []
        emergency_model = EmergencyModel()
        result = emergency_model.determine_real_report('New York', 'low', {"illegal_activity": "Weapon detected"})
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
