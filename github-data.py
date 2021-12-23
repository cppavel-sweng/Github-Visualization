from github import Github
import re
from datetime import timezone
import os

g = Github(os.environ["GITHUB_TOKEN"])

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

    average_number_of_comments_in_issues_created = average_comments/(number_of_issues_created + number_of_pr_created)


    return {
        "issues_created": number_of_issues_created,
        "issues_assigned": number_of_issues_assigned,
        "pr_created": number_of_pr_created,
        "pr_assigned": number_of_pr_assigned,
        "time_between_i_c": time_between_issues_created,
        "time_between_i_a": time_between_issues_assigned,
        "time_between_pr_c": time_between_pr_created,
        "time_between_pr_a": time_between_pr_assigned,
        "issues_assinged_closed": issues_assinged_closed,
        "pr_assigned_closed": pr_assigned_closed,
        "avg_number_of_comments_in_created": average_number_of_comments_in_issues_created,
        "avg_time_to_close_issue": average_time_to_close_issue,
        "avg_time_to_review_pr": average_time_to_review_pr

    }

def get_type_of_developer_data(user_name):
    commits = g.search_commits(f"author:{user_name}", sort='author-date', order='desc')
    commit_count = commits.totalCount
    print("Received commits")

    repos = []
    for commit in commits:
        if extract_repo_name(commit.commit.url) not in repos:
            repos.append(extract_repo_name(commit.commit.url))

    print("Computed number of repos")
    
    differences = [] 
    for index in range(0, commits.totalCount - 1):
        first_ts = commits[index].commit.author.date.replace(tzinfo=timezone.utc).timestamp()
        second_ts = commits[index + 1].commit.author.date.replace(tzinfo=timezone.utc).timestamp()
        difference = - (second_ts - first_ts)/3600 
        differences.append(difference)
        

    print("Done with differences")

    changes = [0]*commit_count

    for index in range(0, commit_count):
        print(f"{index}: {commits[index].stats.total}")
        changes[index] = commits[index].stats.total


    return {
        "commit_count": commit_count,
        "repos": repos,
        "avg_time_between_commits": differences,
        "diffbase_per_commit": changes
    }


def get_basic_account_info(user_name):
    user = g.get_user(user_name)

    return {
        "bio": user.bio,
        "company": user.company,
        "created_at": user.created_at,
        "email": user.email,
        "followers": user.followers,
        "following": user.following,
        "hireable": user.hireable,
        "location": user.location,
        "name": user.name,
        "login": user.login,
        "private_repos_owned": user.owned_private_repos,
        "updated_at": user.updated_at,
        "url": user.url,
        "team_count": user.team_count
    }


    
if __name__ == "__main__":
    print(get_type_of_developer_data("cppavel"))
    print(search_issues("cppavel"))
    print(get_basic_account_info("cppavel"))
