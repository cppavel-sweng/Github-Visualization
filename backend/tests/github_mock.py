from unittest.mock import MagicMock
from datetime import datetime

def mock_issues():
    issues = []

    for index in range(5, 0, -1):
        issues.append(type('', (), {})())
        issues[-1].closed_by = None
        issues[-1].comments = index - 1
        if index%2 == 0:
            issues[-1].closed_by = type('', (), {})()
            issues[-1].closed_by.login = "cppavel"
            issues[-1].closed_at = datetime.strptime(f"Jun 1 2001  {index + 1}:33PM",
                "%b %d %Y %I:%M%p")
        issues[-1].created_at = datetime.strptime(f"Jun 1 2001  {index}:33PM", "%b %d %Y %I:%M%p")


    issues[0].closed_by = type('', (), {})()
    issues[0].closed_by.login = "cppavel_sweng"
    issues[0].closed_at = datetime.strptime(f"Jun 1 2001  7:33PM", "%b %d %Y %I:%M%p")

    return issues

def mock_prs():
    prs = []

    for index in range(5, 0, -1):
        prs.append(type('', (), {})())
        prs[-1].closed_by = None
        prs[-1].comments = index + 1
        if index%2 == 0:
            prs[-1].closed_by = type('', (), {})()
            prs[-1].closed_by.login = "cppavel"
            prs[-1].closed_at = datetime.strptime(f"Jun 1 2001  {index + 1}:33PM",
                "%b %d %Y %I:%M%p")
        prs[-1].created_at = datetime.strptime(f"Jun 1 2001  {index}:33PM", "%b %d %Y %I:%M%p")


    prs[0].closed_by = type('', (), {})()
    prs[0].closed_by.login = "cppavel_sweng"
    prs[0].closed_at = datetime.strptime(f"Jun 1 2001  7:33PM", "%b %d %Y %I:%M%p")

    return prs


def mock_commits():
    commits = []

    for index in range(0, 10):
        commits.append(type('', (), {})())
        commits[-1].commit = type('', (), {})()
        commits[-1].commit.url = f"https://api.github.com/repos/test_repo{index}/git/"
        commits[-1].stats = type('', (), {})()
        commits[-1].stats.total = index*10

        commits[-1].files = []
        commits[-1].commit.committer = type('', (), {})()
        commits[-1].commit.committer.date = datetime.strptime(f"Jun 1 2001  {10-index + 1}:33PM",
             "%b %d %Y %I:%M%p")

        for file_index in range(0, 5):
            commits[-1].files.append(type('', (), {})())
            commits[-1].files[-1].additions = (file_index + 1) * (index + 1)
            commits[-1].files[-1].deletions = (file_index + 1) * (index + 1) / 2
            if file_index < 2:
                commits[-1].files[-1].filename = f"{index}:{file_index}.cpp"
            else:
                commits[-1].files[-1].filename = f"{index}:{file_index}.java"

    return commits


def mock_user():
    user = type('', (), {})()
    user.login = "cppavel"
    user.created_at = type('', (), {})()
    user.created_at.date = MagicMock(return_value=datetime.strptime(f"Jun 1 2001  2:33PM",
        "%b %d %Y %I:%M%p"))
    user.url = "test_url"
    user.avatar_url = "test_avatar_url"
    user.followers = 10
    user.following = 25
    user.location = "Dublin"
    user.company = "TCD"
    user.bio = None
    user.email = "pavel@tcd.ie"
    user.hireable = None
    user.name = "Pavel"
    user.updated_at = type('', (), {})()
    user.updated_at.date = MagicMock(return_value=None)

    return user


def get_github_mock():
    mock = type('', (), {})()
    mock.search_issues = MagicMock(return_value=mock_issues())
    mock.search_commits = MagicMock(return_value=mock_commits())
    mock.get_user = MagicMock(return_value = mock_user())

    return mock