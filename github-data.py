from github import Github
import re
from datetime import timezone

g = Github("TOKEN")

def extract_repo_name(commit_url):
    pattern = re.compile("https://api.github.com/repos/(.*)/git/")
    match = pattern.search(commit_url).group(1)
    return match 


def get_type_of_developer_data(user_name):
    commits = g.search_commits(f"author:{user_name}", sort='author-date', order='asc')

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
        difference = (second_ts - first_ts)/3600 
        differences.append(difference)
        

    print("Done with differences")

    changes = []
    for commit in commits:
        changes.append(commit.stats.total)


    commit_count = commits.totalCount

    print(commit_count)
    print(repos)
    print(differences)
    print(changes)

    





if __name__ == "__main__":
    get_type_of_developer_data("cppavel")