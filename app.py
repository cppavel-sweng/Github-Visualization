from flask import Flask, jsonify, request, render_template
import pymongo
from threading import Thread
from pymongo import MongoClient
from github_data import GithubData

app = Flask(__name__)

task_id = 0
g_table = {}

client = MongoClient(host='test_mongodb',
                        port=27017, 
                        username='root', 
                        password='pass',
                    authSource="admin")

def github_gathering(developer_handle):
    global task_id 
    global client

    db = client["developer_db"]
    developer_data = db.developer_data.find_one({"handle": developer_handle})
    g = GithubData()
    g_table[task_id] = g
    
    if not developer_data:
        developer_basic_details = g.get_basic_account_info(developer_handle)
        developer_detailed_data = g.get_detailed_data(developer_handle)
        developer_issues_data = g.search_issues(developer_handle)

        mydb = client["developer_db"]
        collection = mydb["developer_data"]

        developer_data =  {
            "handle": developer_handle,
            "bd": developer_basic_details,
            "dd": developer_detailed_data,
            "di": developer_issues_data

        }

        collection.insert_one(developer_data)

        g.message = "Completed"

        print(developer_basic_details)
        print(developer_detailed_data)
        print(developer_issues_data)

    else:
        g.message = "Completed"

@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/progress/<task_id>')
def progress(task_id):
    global g_table
    return f"{g_table[task_id].message}"


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
        return f"<h1>Sorry, no data found for such developer: {handle}</h1>"

@app.route('/top-developers-for-a-repo')
def top_developers_for_a_repo():
    return render_template('top_developers_for_a_repo.html')

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)