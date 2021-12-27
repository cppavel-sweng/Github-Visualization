from github import Github
import re
from datetime import timezone
from programming_languages import EXTENSION_TO_LANG
import statistics
import os

class GithubData:

    def __init__(self):
        self.message = "Idling"
        self.g = Github(os.environ["GITHUB_TOKEN"])


    def convert_to_histogram(self, list, bins, percentile_to_keep):
        negative_errors = []

        sorted_list = sorted(list)

        if len(sorted_list) == 0:
            return [[1],["No data"]]

        sorted_list = sorted_list[0: int(percentile_to_keep*len(sorted_list))]

        if len(sorted_list) == 0:
            return [[1],["No data"]]

        max_value = sorted_list[-1]

        step = max_value/bins

        histogram = [0]*(bins)

        for element in sorted_list:
            bin = int(element/step)
            if bin >= bins:
                bin = bins - 1

            if bin < 0:
                negative_errors.append(element)
                continue

            histogram[bin] = histogram[bin] + 1

        labels = [""]*(bins)
        for index in range(0, bins):
            labels[index] = f"[{round(step*index,1)};{round(step*(index+1),1)}]"

        print(f"Negative errors: {negative_errors}")
        return [histogram, labels]


    def extract_repo_name(self, commit_url):
        pattern = re.compile("https://api.github.com/repos/(.*)/git/")
        match = pattern.search(commit_url).group(1)
        return match 


    def search_issues(self, user_name):

        issue_author_paginated = self.g.search_issues(f"author:{user_name} is:issue", sort='created', order='desc')
        issue_assignee_paginated = self.g.search_issues(f"assignee:{user_name} is:issue", sort='created', order='desc')
        pr_author_paginated = self.g.search_issues(f"author:{user_name} is:pr", sort='created', order='desc')
        pr_assignee_paginated = self.g.search_issues(f"assignee:{user_name} is:pr", sort='created', order='desc')

        issue_author = []

        for issue in issue_author_paginated:
            issue_author.append(issue)

        issue_assignee = []

        for issue in issue_assignee_paginated:
            issue_assignee.append(issue)

        pr_author = []

        for pr in pr_author_paginated:
            pr_author.append(pr)

        pr_assignee = []

        for pr in pr_assignee_paginated:
            pr_assignee.append(pr)
        

        number_of_issues_created = len(issue_author)
        number_of_issues_assigned = len(issue_assignee)
        number_of_pr_created = len(pr_author)
        number_of_pr_assigned = len(pr_assignee)

        self.message = "Issues data received"

        time_between_issues_created = []

        for index in range(0, len(issue_author) - 1):
            first_ts = issue_author[index].created_at.replace(tzinfo=timezone.utc).timestamp()
            second_ts = issue_author[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
            difference = - (second_ts - first_ts)/3600 
            time_between_issues_created.append(difference)
            self.message = f"Done with {index + 1}/{len(issue_author) - 1} times between issues created"

        time_between_issues_assigned = []

        for index in range(0, len(issue_assignee) - 1):
            first_ts = issue_assignee[index].created_at.replace(tzinfo=timezone.utc).timestamp()
            second_ts = issue_assignee[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
            difference = - (second_ts - first_ts)/3600 
            time_between_issues_assigned.append(difference)
            self.message = f"Done with {index + 1}/{len(issue_assignee) - 1} times between issues assigned"

        time_between_pr_created = []

        for index in range(0, len(pr_author) - 1):
            first_ts = pr_author[index].created_at.replace(tzinfo=timezone.utc).timestamp()
            second_ts = pr_author[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
            difference = - (second_ts - first_ts)/3600 
            time_between_pr_created.append(difference)
            self.message = f"Done with {index + 1}/{len(pr_author) - 1} times between pr created"

        time_between_pr_assigned = []

        for index in range(0, len(pr_assignee) - 1):
            first_ts = pr_assignee[index].created_at.replace(tzinfo=timezone.utc).timestamp()
            second_ts = pr_assignee[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
            difference = - (second_ts - first_ts)/3600 
            time_between_pr_assigned.append(difference)
            self.message = f"Done with {index + 1}/{len(pr_assignee) - 1} times between pr assigned"


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

        self.message = "Done with averages and other summary measures for issues data"

        return {
            "issues_created": number_of_issues_created,
            "issues_assigned": number_of_issues_assigned,
            "pr_created": number_of_pr_created,
            "pr_assigned": number_of_pr_assigned,
            "time_between_i_c": self.convert_to_histogram(time_between_issues_created, 10, 1),
            "time_between_i_a": self.convert_to_histogram(time_between_issues_assigned, 10, 1),
            "time_between_pr_c": self.convert_to_histogram(time_between_pr_created, 10, 1),
            "time_between_pr_a": self.convert_to_histogram(time_between_pr_assigned, 10, 1),
            "issues_assigned_closed": issues_assinged_closed,
            "pr_assigned_closed": pr_assigned_closed,
            "avg_number_of_comments_in_created": average_number_of_comments_in_issues_created or "N/A",
            "avg_time_to_close_issue": average_time_to_close_issue or "N/A",
            "avg_time_to_review_pr": average_time_to_review_pr or "N/A"

        }

    def get_detailed_data(self, user_name):
        commits = self.g.search_commits(f"author:{user_name}", sort='committer-date', order='desc')

        commits_list = []

        for commit in commits:
            commits_list.append(commit)

        self.message = "Received commits"

        repos = []
        languages = {}

        changes = []
        average_change_size = 0

        index = 0

        for commit in commits_list:
            if self.extract_repo_name(commit.commit.url) not in repos:
                repos.append(self.extract_repo_name(commit.commit.url))

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
            
            index = index + 1
            self.message = f"Done with {index}/{len(commits_list)} commits"

        sorted_tuples = [list(x) for x in sorted(languages.items(),key=lambda x: x[1], reverse=True)]

        if len(repos) > 10:
            repos = repos[:10]

        differences = [] 
        average_time_between_commits = 0

        for index in range(0, len(commits_list)-1):
            differences.append(
                (
                    (commits_list[index].commit.committer.date-
                        commits_list[index+1].commit.committer.date).total_seconds()/3600)
            )
            average_time_between_commits = average_time_between_commits + differences[-1]
            self.message = f"Done with {index + 1}/{len(commits_list) - 1} differences"


        if len(differences) == 0:
            median_time_between_commits = - 1
            average_time_between_commits = -1
        else:
            median_time_between_commits = statistics.median(differences)
            average_time_between_commits = average_time_between_commits/len(differences)
        
        if len(changes) == 0:
            median_diffbase = -1
            average_change_size = -1
        else:
            median_diffbase = statistics.median(changes)
            average_change_size = average_change_size/len(changes)
            
        commit_count = len(commits_list)

        return {
            "average_time_between_commits": round(average_time_between_commits,1),
            "average_change_size": round(average_change_size,1),
            "median_time_between_commits": round(median_time_between_commits, 1),
            "median_diffbase_per_commit": round(median_diffbase, 1),
            "commit_count": commit_count,
            "repos": repos,
            "time_between_commits": self.convert_to_histogram(differences, 15, 0.9),
            "diffbase_per_commit": self.convert_to_histogram(changes, 15, 0.9),
            "languages": sorted_tuples
        }


    def get_basic_account_info(self, user_name):
        user = self.g.get_user(user_name)

        self.message = "Done with basic info"

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
    gd = GithubData()
    test_dd = gd.get_detailed_data("cppavel-sweng")
    test_di = gd.search_issues("cppavel-sweng")
    test_bi = gd.get_basic_account_info("cppavel-sweng")
    print("\n\n\n\n\n\n\n\n")
    print(test_bi)
    print(test_dd)
    print(test_di)
