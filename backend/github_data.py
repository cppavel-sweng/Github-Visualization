from github import Github
import re
from datetime import timezone
from programming_languages import EXTENSION_TO_LANG
import statistics
import os

class GithubData:

    def __init__(self, task_id):
        self.message = f"{task_id}: Idling"
        self.task_id = task_id
        self.g = Github(os.environ["GITHUB_TOKEN"])

    def convert_to_histogram(self, list, bins, percentile_to_keep):
        """
            Converts an array into histogram with labels.

            Args:
                list: the array
                bins: number of columns desired
                percentile_to_keep: percentile at which the distribution is cut 
        """

        negative_errors = []
        sorted_list = sorted(list)

        if len(sorted_list) == 0:
            return [[0],["No data"]]

        sorted_list = sorted_list[0: int(percentile_to_keep*len(sorted_list))]

        if len(sorted_list) == 0:
            return [[0],["No data"]]

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
        """Simple regex to extract repo name out of the link."""
        pattern = re.compile("https://api.github.com/repos/(.*)/git/")
        match = pattern.search(commit_url).group(1)
        return match 

    def convert_paginated_list_into_regular_list(self, paginated_list):
        """
            Converts paginated lists returned by pygithub into regular lists to
            be able to assume that the length of the list is going to be constant.
        """

        result = []
        for item in paginated_list:
            result.append(item)

        return result

    def compute_time_between_consequtive_issues(self, issues, label_for_output, user_name):
        """
            Assumes issues are sorted in reverse chronological order, returns list of times
            between consequtive issues (created or assigned).

            Args:
                issues: regular list of issues
                label_for_output: information for updating the progress message
                user_name: required to make progress messsage more specific
        """
        time_between_issues = []

        for index in range(0, len(issues) - 1):
            first_ts = issues[index].created_at.replace(tzinfo=timezone.utc).timestamp()
            second_ts = issues[index + 1].created_at.replace(tzinfo=timezone.utc).timestamp()
            difference = (first_ts - second_ts)/3600 
            time_between_issues.append(difference)
            self.message = (f"{self.task_id}: Done with {index + 1}/{len(issues) - 1} {label_for_output} "
                            f"({user_name})")
        
        return time_between_issues

    def find_number_of_closed_assigned_issues(self, issues, user_name):
        """
            Finds how many issues assigned to the user were closed by them.

            Args:
                issues: regular list of issues or prs
                user_name: GitHub user name

            Returns a tuple (number of closed assigned issues, average time to close issue)
        """

        count_closed = 0
        average_time_to_close_issue = 0

        for issue in issues:
            
            if issue.closed_by:
                if user_name == issue.closed_by.login:
                    count_closed = count_closed + 1

                average_time_to_close_issue = (average_time_to_close_issue + 
                    issue.closed_at.replace(tzinfo=timezone.utc).timestamp() - 
                    issue.created_at.replace(tzinfo=timezone.utc).timestamp())

        if count_closed > 0:
            average_time_to_close_issue = average_time_to_close_issue/(count_closed * 3600)
            average_time_to_close_issue = round(average_time_to_close_issue, 1)
        else:
            average_time_to_close_issue = None

        return (count_closed, average_time_to_close_issue)


    def find_average_number_of_comments_in_issues_created(self, issues, prs):
        """
            Finds average number of comments in issues and prs the user created.
            The idea of the metric is showing how user's contributions provoke 
            discussions, which are an important part of development cycle.
        """

        average_comments = 0

        for issue in issues:
            average_comments = average_comments + issue.comments
        
        for pr in prs:
            average_comments = average_comments + pr.comments

        if len(issues) + len(prs) > 0:
            average_number_of_comments_in_issues_created = average_comments/(len(issues) + len(prs))
            average_number_of_comments_in_issues_created = round(average_number_of_comments_in_issues_created,1)    
        else:
            average_number_of_comments_in_issues_created = None

        return average_number_of_comments_in_issues_created


    def search_issues(self, user_name):

        issue_author = self.convert_paginated_list_into_regular_list(
            self.g.search_issues(f"author:{user_name} is:issue", sort='created', order='desc'))
        issue_assignee = self.convert_paginated_list_into_regular_list(
            self.g.search_issues(f"assignee:{user_name} is:issue", sort='created', order='desc'))
        pr_author = self.convert_paginated_list_into_regular_list(
            self.g.search_issues(f"author:{user_name} is:pr", sort='created', order='desc'))
        pr_assignee = self.convert_paginated_list_into_regular_list(
            self.g.search_issues(f"assignee:{user_name} is:pr", sort='created', order='desc'))

        number_of_issues_created = len(issue_author)
        number_of_issues_assigned = len(issue_assignee)
        number_of_pr_created = len(pr_author)
        number_of_pr_assigned = len(pr_assignee)

        self.message = f"{self.task_id}: Issues data received ({user_name})"

        time_between_issues_created = self.compute_time_between_consequtive_issues(
            issue_author,"times between issues created", user_name)
        time_between_issues_assigned = self.compute_time_between_consequtive_issues(
            issue_assignee,"times between issues assigned", user_name)
        time_between_pr_created = self.compute_time_between_consequtive_issues(
            pr_author,"times between pr created", user_name)
        time_between_pr_assigned = self.compute_time_between_consequtive_issues(
            pr_assignee,"times between pr assigned", user_name)

        
        issues_assigned_closed, average_time_to_close_issue = self.find_number_of_closed_assigned_issues(
            issue_assignee, user_name)
        pr_assigned_closed, average_time_to_review_pr = self.find_number_of_closed_assigned_issues(pr_assignee, user_name)

        average_number_of_comments_in_issues_created = self.find_average_number_of_comments_in_issues_created(
            issue_author, pr_author)

        self.message = (f"{self.task_id}: Done with averages and other summary measures "
                        f"for issues data ({user_name})")

        return {
            "issues_created": number_of_issues_created,
            "issues_assigned": number_of_issues_assigned,
            "pr_created": number_of_pr_created,
            "pr_assigned": number_of_pr_assigned,
            "time_between_i_c": self.convert_to_histogram(time_between_issues_created, 10, 1),
            "time_between_i_a": self.convert_to_histogram(time_between_issues_assigned, 10, 1),
            "time_between_pr_c": self.convert_to_histogram(time_between_pr_created, 10, 1),
            "time_between_pr_a": self.convert_to_histogram(time_between_pr_assigned, 10, 1),
            "issues_assigned_closed": issues_assigned_closed,
            "pr_assigned_closed": pr_assigned_closed,
            "avg_number_of_comments_in_created": average_number_of_comments_in_issues_created or "N/A",
            "avg_time_to_close_issue": average_time_to_close_issue or "N/A",
            "avg_time_to_review_pr": average_time_to_review_pr or "N/A"
        }

    def get_detailed_data(self, user_name):
        """
            Gets detailed data about the user contributions by looking at the most recent commits.
        """

        commits_list = self.convert_paginated_list_into_regular_list(self.g.search_commits(
            f"author:{user_name}", sort='committer-date', order='desc'))

        self.message = f"{self.task_id}: Received commits ({user_name})"

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
            self.message = f"{self.task_id}: Done with {index}/{len(commits_list)} commits ({user_name})"

        lang_labels = [x[0] for x in sorted(languages.items(),key=lambda x: x[1], reverse=True)]
        lang_values = [x[1] for x in sorted(languages.items(),key=lambda x: x[1], reverse=True)]

        if len(lang_values) > 64:
            lang_values = lang_values[:64]

        if len(lang_labels) > 64:
            lang_labels = lang_labels[:64]

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
            self.message = (f"{self.task_id}: Done with {index + 1}/{len(commits_list) - 1} "
                            f"differences ({user_name})")


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
            "lang_labels": lang_labels,
            "lang_values": lang_values
        }


    def get_basic_account_info(self, user_name):
        user = self.g.get_user(user_name)

        self.message =f"{self.task_id}: Done with basic info ({user_name})"

        return {
            "bio": user.bio or "Not specified",
            "company": user.company or "Not specified",
            "created_at": str(user.created_at.date()),
            "email": user.email or "Not Specified",
            "followers": user.followers or "Hidden",
            "following": user.following or "Hidden",
            "hireable": user.hireable or "Not specified",
            "location": user.location or "Not specified",
            "name": user.name or "Not specified",
            "login": user.login,
            "updated_at": str(user.updated_at.date()) or "Hidden",
            "url": user.url,
            "avatar_url": user.avatar_url
        }