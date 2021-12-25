from github import Github
import re
from datetime import timezone
from programming_languages import EXTENSION_TO_LANG
import os

g = Github(os.environ["GITHUB_TOKEN"])

def convert_to_histogram(list, bins):
    sorted_list = sorted(list)

    max_value = sorted_list[-1]

    print(f"Max value is {max_value}")

    step = max_value/bins

    print(f"Step is {step}")

    histogram = [0]*(bins)
    starting_value = 0
    for index in range(0, len(sorted_list)):
        if step*starting_value <= sorted_list[index] and step*(starting_value + 1) >= sorted_list[index]:
            histogram[starting_value] = histogram[starting_value] + 1
        else:
            starting_value = starting_value + 1
            histogram[starting_value] = 1

    labels = [""]*(bins)
    for index in range(0, bins):
        labels[index] = f"[{round(step*index,1)};{round(step*(index+1),1)}]"

    return (histogram, labels) 


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

def get_detailed_data(user_name):
    commits = g.search_commits(f"author:{user_name}", sort='author-date', order='desc')
    commit_count = commits.totalCount
    print("Received commits")

    repos = []
    languages = {}
    for commit in commits:
        if extract_repo_name(commit.commit.url) not in repos:
            repos.append(extract_repo_name(commit.commit.url))

        for file in commit.files:
            name, extension = os.path.splitext(file.filename)

            if extension in EXTENSION_TO_LANG:
                language = EXTENSION_TO_LANG[extension]

                if language in languages:
                    languages[language]["changes"] = languages[language]["changes"] + file.additions + file.deletions
                else:
                    languages[language] = {"changes": file.additions + file.deletions}

    print("Computed number of repos")
    
    differences = [] 
    average_time_between_commits = 0
    for index in range(0, commits.totalCount - 1):
        first_ts = commits[index].commit.author.date.replace(tzinfo=timezone.utc).timestamp()
        second_ts = commits[index + 1].commit.author.date.replace(tzinfo=timezone.utc).timestamp()
        difference = - (second_ts - first_ts)/3600 
        differences.append(difference)
        average_time_between_commits = average_time_between_commits + difference
    
    if commit_count > 0:
        average_time_between_commits = average_time_between_commits/commit_count
    else:
        average_time_between_commits = None
        

    print("Done with differences")

    average_change_size = 0

    changes = [0]*commit_count

    for index in range(0, commit_count):
        changes[index] = commits[index].stats.total
        average_change_size = average_change_size + commits[index].stats.total

    if commit_count > 0:
        average_change_size = average_change_size/commit_count
    else:
        average_change_size = None


    return {
        "average_time_between_commits": round(average_time_between_commits,1),
        "average_change_size": round(average_change_size,1),
        "commit_count": commit_count,
        "repos": repos,
        "time_between_commits": convert_to_histogram(differences,15),
        "diffbase_per_commit": convert_to_histogram(changes, 15),
        "languages": languages
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
