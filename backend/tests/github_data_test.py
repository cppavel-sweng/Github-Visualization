from parameterized import parameterized, parameterized_class
from github_data import GithubData
from github_mock import GithubMock
import unittest


class GithubDataTest(unittest.TestCase):

    def setUp(self):
        self.github_data = GithubData(1, GithubMock())

    @parameterized.expand([
        ("check_test_config_works_success", [], 100, 1, [[0], ["No data"]]),
    ])
    def test_convert_to_histogram(self, actual, list, bins, percentile, expected):
        actual= self.github_data.convert_to_histogram(list, bins, percentile)
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main(verbosity=2)
