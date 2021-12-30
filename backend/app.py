from flask import Flask, jsonify, request, render_template
import os
import pymongo
from threading import Thread
from pymongo import MongoClient
from github_data import GithubData
from github import Github


app = Flask(__name__)


task_id = 0
g_table = {}


client = MongoClient(host='test_mongodb',
                        port=27017, 
                        username='root', 
                        password='pass',
                    authSource="admin")


def github_gathering(developer_handle):
    """Gather basic information, commits, changes, issues, PRs and associated metrics."""
    
    global task_id 
    global client

    db = client["developer_db"]
    developer_data = db.developer_data.find_one({"handle": developer_handle})
    g = GithubData(task_id, Github(os.environ["GITHUB_TOKEN"]))
    g_table[task_id] = g
    
    if not developer_data:

        try:
            developer_detailed_data = g.get_detailed_data(developer_handle)
            developer_issues_data = g.search_issues(developer_handle)
            developer_basic_details = g.get_basic_account_info(developer_handle)
        except Exception as e:
            print(e)
            user_limits = g_table[task_id].g.get_rate_limit()
            g.message = (f"Failed: (task_id:{g.task_id}, handle: {developer_handle}).<br/> "
                        f"Error: {e}. .<br/> Your API limits, for core: "
                        f"{user_limits.core.remaining}/{user_limits.core.limit} requests left, "
                        f"which will be reset at {user_limits.core.reset}, for search: "
                        f"{user_limits.search.remaining}/{user_limits.search.limit} requests left, "
                        f"which will be reset at {user_limits.search.reset}.")

        mydb = client["developer_db"]
        collection = mydb["developer_data"]

        developer_data =  {
            "handle": developer_handle,
            "bd": developer_basic_details,
            "dd": developer_detailed_data,
            "di": developer_issues_data

        }

        collection.insert_one(developer_data)

        g.message = f"Completed, stored in DB (task_id:{g.task_id}, handle: {developer_handle})."

        print(developer_basic_details)
        print(developer_detailed_data)
        print(developer_issues_data)

    else:
        print("already in database")
        g.message = g.message = f"Completed, already in DB (task_id:{g.task_id}, handle: {developer_handle})"


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/drop_developer_database')
def drop_developer_db():
    global client 
    db = client["developer_db"]
    collection = db["developer_data"]
    collection.drop()

    return "<h1>Successfully dropped the database</h1>"


@app.route('/progress/<taskid>')
def progress(taskid):
    global g_table
    return f"{g_table[int(taskid)].message}"


@app.route('/compute_data/<handle>')
def compute_data(handle):
    global task_id 

    task_id = task_id + 1

    th = Thread(target=github_gathering, args=(handle,), daemon=True)

    th.start()

    return f"{task_id}"


@app.route('/type-of-developer')
def type_of_developer():
    return render_template('type_of_developer.html')


@app.route('/type-of-developer/<handle>')
def type_of_developer_result(handle):
    global client

    db = client["developer_db"]
    developer_data = db.developer_data.find_one({"handle": handle})

    if developer_data:
        developer_basic_details = developer_data["bd"]
        developer_detailed_data = developer_data["dd"]
        developer_issues_data = developer_data["di"]
        return render_template(
            'type_of_developer_result.html', 
            developer_basic_details=developer_basic_details,
            developer_detailed_data=developer_detailed_data,
            developer_issues_data=developer_issues_data
        )
    else:
        return (f"<h1>Sorry, no data found for such developer: {handle}.<br/>"
                 f"Consider starting the computation for {handle} on the previous page.<br/>"
                 f"After the computation is completed you will be able to see the "
                 f"visualization.</h1>")


@app.route('/top-developers-for-a-repo')
def top_developers_for_a_repo():
    return render_template('top_developers_for_a_repo.html')


if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)