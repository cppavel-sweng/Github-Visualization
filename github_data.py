from github import Github
import re
from datetime import timezone
from programming_languages import EXTENSION_TO_LANG
import os
import pytz

g = Github(os.environ["GITHUB_TOKEN"])

def convert_to_histogram(list, bins, percentile_to_keep):
    sorted_list = sorted(list)

    if len(sorted_list) == 0:
        return [[1],["No data"]]

    sorted_list = sorted_list[0: int(percentile_to_keep*len(sorted_list))]

    if len(sorted_list) == 0:
        return [[1],["No data"]]

    max_value = sorted_list[-1]

    print(f"Max value is {max_value}")

    step = max_value/bins

    print(f"Step is {step}")

    histogram = [0]*(bins)

    print(sorted_list)

    for element in sorted_list:
        bin = int(element/step)
        if bin >= bins:
            bin = bins - 1

        histogram[bin] = histogram[bin] + 1

    labels = [""]*(bins)
    for index in range(0, bins):
        labels[index] = f"[{round(step*index,1)};{round(step*(index+1),1)}]"

    return [histogram, labels]


def extract_repo_name(commit_url):
    pattern = re.compile("https://api.github.com/repos/(.*)/git/")
    match = pattern.search(commit_url).group(1)
    return match 


def search_issues(user_name):

    issue_author = g.search_issues(f"author:{user_name} is:issue", sort='created', order='desc')
    issue_assignee = g.search_issues(f"assignee:{user_name} is:issue", sort='created', order='desc')
    pr_author = g.search_issues(f"author:{user_name} is:pr", sort='created', order='desc')
    pr_assignee = g.search_issues(f"assignee:{user_name} is:pr", sort='created', order='desc')


    number_of_issues_created = issue_author.totalCount
    number_of_issues_assigned = issue_assignee.totalCount
    number_of_pr_created = pr_author.totalCount
    number_of_pr_assigned = pr_assignee.totalCount

    time_between_issues_created = []

    for index in range(0, issue_author.totalCount - 1):
        first_ts = issue_author[index].created_at.replace(tzinfo=timezone.utc).timestamp()
        second_ts = issue_author[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
        difference = - (second_ts - first_ts)/3600 
        time_between_issues_created.append(difference)

    time_between_issues_assigned = []

    for index in range(0, issue_assignee.totalCount - 1):
        first_ts = issue_assignee[index].created_at.replace(tzinfo=timezone.utc).timestamp()
        second_ts = issue_assignee[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
        difference = - (second_ts - first_ts)/3600 
        time_between_issues_assigned.append(difference )

    time_between_pr_created = []

    for index in range(0, pr_author.totalCount - 1):
        first_ts = pr_author[index].created_at.replace(tzinfo=timezone.utc).timestamp()
        second_ts = pr_author[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
        difference = - (second_ts - first_ts)/3600 
        time_between_pr_created.append(difference)

    time_between_pr_assigned = []

    for index in range(0, pr_assignee.totalCount - 1):
        first_ts = pr_assignee[index].created_at.replace(tzinfo=timezone.utc).timestamp()
        second_ts = pr_assignee[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
        difference = - (second_ts - first_ts)/3600 
        time_between_pr_assigned.append(difference)


    #how many issues assigned to the person were closed by them

    count_closed = 0
    average_time_to_close_issue = 0

    for issue in issue_assignee:
        
        if issue.closed_by:
            if user_name == issue.closed_by.login:
                count_closed = count_closed + 1

            average_time_to_close_issue = (average_time_to_close_issue + 
                issue.closed_at.replace(tzinfo=timezone.utc).timestamp() - 
                issue.created_at.replace(tzinfo=timezone.utc).timestamp())


    if count_closed > 0:
        average_time_to_close_issue = average_time_to_close_issue/(count_closed * 3600)
    else:
        average_time_to_close_issue = None

    issues_assinged_closed = count_closed

    count_closed = 0
    average_time_to_review_pr = 0 

    for pr in pr_assignee:
        if pr.closed_by:
            if user_name == pr.closed_by.login:
                count_closed = count_closed + 1

            average_time_to_review_pr = (average_time_to_review_pr + 
                pr.closed_at.replace(tzinfo=timezone.utc).timestamp() - 
                pr.created_at.replace(tzinfo=timezone.utc).timestamp())

    pr_assigned_closed = count_closed

    if count_closed > 0:
        average_time_to_review_pr = average_time_to_review_pr/(count_closed * 3600)
    else:
        average_time_to_review_pr = None

    #how many comments did issues created by the user had on average (how impactful they were)
    #as discussions are the most important part


    average_comments = 0

    for issue in issue_author:
        average_comments = average_comments + issue.comments
    
    for pr in pr_author:
        average_comments = average_comments + pr.comments

    if number_of_issues_created + number_of_pr_created > 0:
        average_number_of_comments_in_issues_created = average_comments/(number_of_issues_created + number_of_pr_created)
    else:
        average_number_of_comments_in_issues_created = None

    return {
        "issues_created": number_of_issues_created,
        "issues_assigned": number_of_issues_assigned,
        "pr_created": number_of_pr_created,
        "pr_assigned": number_of_pr_assigned,
        "time_between_i_c": convert_to_histogram(time_between_issues_created, int(number_of_issues_created/2) + 1, 1),
        "time_between_i_a": convert_to_histogram(time_between_issues_assigned, int(number_of_issues_assigned/2) + 1, 1),
        "time_between_pr_c": convert_to_histogram(time_between_pr_created, int(number_of_pr_created/2) + 1, 1),
        "time_between_pr_a": convert_to_histogram(time_between_pr_assigned, int(number_of_pr_assigned/2) + 1, 1),
        "issues_assigned_closed": issues_assinged_closed,
        "pr_assigned_closed": pr_assigned_closed,
        "avg_number_of_comments_in_created": average_number_of_comments_in_issues_created or "N/A",
        "avg_time_to_close_issue": average_time_to_close_issue or "N/A",
        "avg_time_to_review_pr": average_time_to_review_pr or "N/A"

    }

def get_detailed_data(user_name):
    commits = g.search_commits(f"author:{user_name}", sort='committer-date', order='desc')

    commits_list = []

    for commit in commits:
        commits_list.append(commit)

    print("Received commits")

    repos = []
    languages = {}

    changes = []
    average_change_size = 0

    for commit in commits_list:
        if extract_repo_name(commit.commit.url) not in repos:
            repos.append(extract_repo_name(commit.commit.url))

        changes.append(commit.stats.total)
        average_change_size = average_change_size + commit.stats.total

        for file in commit.files:
            name, extension = os.path.splitext(file.filename)

            if extension in EXTENSION_TO_LANG:
                language = EXTENSION_TO_LANG[extension]

                if language in languages:
                    languages[language] = languages[language] + file.additions + file.deletions
                else:
                    languages[language] = file.additions + file.deletions

    sorted_tuples = [list(x) for x in sorted(languages.items(),key=lambda x: x[1], reverse=True)]

    differences = [] 
    average_time_between_commits = 0

    for index in range(0, len(commits_list)-1):
        differences.append(
            (
                (commits_list[index].commit.committer.date-
                    commits_list[index+1].commit.committer.date).total_seconds()/3600)
        )
        average_time_between_commits = average_time_between_commits + differences[-1]


    if len(differences) == 0:
        average_time_between_commits = -1
    else:
        average_time_between_commits = average_time_between_commits/len(differences)
    
    if len(changes) == 0:
        average_change_size = -1
    else:
        average_change_size = average_change_size/len(changes)
        
    commit_count = commits.totalCount

    return {
        "average_time_between_commits": round(average_time_between_commits,1),
        "average_change_size": round(average_change_size,1),
        "commit_count": commit_count,
        "repos": repos,
        "time_between_commits": convert_to_histogram(differences,int(commit_count/2) + 1, 0.8),
        "diffbase_per_commit": convert_to_histogram(changes, int(commit_count/2) + 1, 0.8),
        "languages": sorted_tuples
    }


def get_basic_account_info(user_name):
    user = g.get_user(user_name)

    return {
        "bio": user.bio or "Bio not specified",
        "company": user.company or "Company not specified",
        "created_at": user.created_at,
        "email": user.email or "Email Not Specified",
        "followers": user.followers or "Hidden",
        "following": user.following or "Hidden",
        "hireable": user.hireable or "Hiring status not specified",
        "location": user.location or "Location not specified",
        "name": user.name or "Name not specified",
        "login": user.login,
        "private_repos_owned": user.owned_private_repos or "Hidden",
        "updated_at": user.updated_at or "Hidden",
        "url": user.url,
        "team_count": user.team_count or "Hidden",
        "avatar_url": user.avatar_url
    }


    
if __name__ == "__main__":
    test = get_detailed_data("cppavel-sweng")
    print(test)
    #print(search_issues("cppavel-sweng"))
    #print(get_basic_account_info("cppavel-sweng"))
