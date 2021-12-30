from parameterized import parameterized, parameterized_class
from github_data import GithubData
from test_expected_results import SEARCH_ISSUES_RESULT_TEST, GET_DETAILED_DATA_RESULT_TEST, GET_BASIC_INFO_RESULT_TEST
import github_mock
import unittest
import pprint


class GithubDataTest(unittest.TestCase):

    def setUp(self):
        self.github_data = GithubData(1, github_mock.get_github_mock())
        self.maxDiff = None

    @parameterized.expand([
        ("empty", [], 100, 1, [[0], ["No data"]]),
        ("empty after cutting percentile", [1, 2], 100, 0.1, [[0], ["No data"]]),
        ("non-empty full percentile", 
            [1, 2, 3, 4, 5], 
            5, 1, [[0,1,1,1,2], ["[0.0;1.0]", "[1.0;2.0]", "[2.0;3.0]", "[3.0;4.0]", "[4.0;5.0]"]]),
        ("non-empty full percentile, negative errors do not affect", 
            [-100, 1, 2, 3, 4, 5], 
            5, 1, [[0,1,1,1,2], ["[0.0;1.0]", "[1.0;2.0]", "[2.0;3.0]", "[3.0;4.0]", "[4.0;5.0]"]]),
    ])
    def test_convert_to_histogram(self, name, list, bins, percentile, expected):
        actual= self.github_data.convert_to_histogram(list, bins, percentile)
        self.assertEqual(actual, expected)

    @parameterized.expand([
        ("valid", "https://api.github.com/repos/test-repo/git/", "test-repo"),
        ("invalid", "https://api.githu_error_b.com/repos/test-repo/git/", None)
    ])
    def test_extract_repo_name(self, name, url, expected):
        actual= self.github_data.extract_repo_name(url)
        self.assertEqual(actual, expected)

    # Assuming here that the list passed in is actually paginated, just checking that the logic is
    # right
    @parameterized.expand([
        ("valid", [1,2,3,4,5], [1,2,3,4,5]),
        ("empty", [], []),
    ])
    def test_convert_paginated_list_to_list(self, name, paginated_list, expected):
        actual= self.github_data.convert_paginated_list_into_regular_list(paginated_list)
        self.assertListEqual(actual, expected)

    @parameterized.expand([
        ("valid", github_mock.mock_issues(), "test_label", "test_user", [1, 1, 1, 1]),
        ("empty", [], "test_label", "test_user", []),
    ])
    def test_time_between_consequtive_issues(self, name, issues, label_for_output, user_name, expected):
        actual = self.github_data.compute_time_between_consequtive_issues(
            issues, label_for_output, user_name)
        self.assertListEqual(actual, expected)

    @parameterized.expand([
        ("valid1", github_mock.mock_issues(), "cppavel", (2, 1.0)),
        ("valid2", github_mock.mock_issues(), "cppavel_sweng", (1, 2.0)),
        ("valid3", github_mock.mock_issues(), "pavel", (0, None)),
        ("empty", [], "cppavel_sweng", (0, None))
    ])
    def test_find_number_of_closed_assigned_issues(self, name, issues, user_name, expected):
        actual = self.github_data.find_number_of_closed_assigned_issues(issues, user_name)
        self.assertTupleEqual(actual, expected)

    @parameterized.expand([
        ("valid1", github_mock.mock_issues(), github_mock.mock_prs(), 3.0),
        ("valid2", [], github_mock.mock_prs(), 4.0),
        ("valid1", github_mock.mock_issues(), [], 2.0),
        ("empty", [], [], None)
    ])
    def test_find_average_number_of_comments_in_issues_created(self, name, issues, prs, expected):
        actual = self.github_data.find_average_number_of_comments_in_issues_created(issues, prs)
        self.assertEqual(actual, expected)

    @parameterized.expand([
        ("valid1", "cppavel", SEARCH_ISSUES_RESULT_TEST),
    ])
    def test_search_issues(self, name, user_name, expected):
        actual = self.github_data.search_issues(user_name)
        self.assertDictEqual(actual, expected)

    @parameterized.expand([
        ("valid1", "cppavel", GET_DETAILED_DATA_RESULT_TEST),
    ])
    def test_get_detailed_data(self, name, user_name, expected):
        actual = self.github_data.get_detailed_data(user_name)
        self.assertDictEqual(actual, expected)

    @parameterized.expand([
        ("valid1", "cppavel", GET_BASIC_INFO_RESULT_TEST),
    ])
    def test_get_basic_account_info(self, name, user_name, expected):
        actual = self.github_data.get_basic_account_info(user_name)
        pprint.pprint(actual)
        self.assertDictEqual(actual, expected)

if __name__ == "__main__":
    unittest.main(verbosity=2)
