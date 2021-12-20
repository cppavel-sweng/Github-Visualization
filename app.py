from flask import Flask, jsonify, request, render_template
import pymongo
from pymongo import MongoClient

app = Flask(__name__)

def drop():
    client = MongoClient(host='test_mongodb',
                            port=27017, 
                            username='root', 
                            password='pass',
                            authSource="admin")

    mydb = client["animal_db"]
    collection = mydb["animal_tb"]
    collection.drop()

def put_new_animal(animal_name, animal_type):
    client = MongoClient(host='test_mongodb',
                            port=27017, 
                            username='root', 
                            password='pass',
                            authSource="admin")

    mydb = client["animal_db"]
    collection = mydb["animal_tb"]
    dict = {"id": 100, "name": animal_name, "type": animal_type}
    x = collection.insert_one(dict)

    return x

def get_data(handle):
    return {'avg-t-c': 100,
            'n-c': 200,
            'lar-diff': 500, 
            'n-r-w': 10, 
            'n-pr-i': 10, 
            'avg-t-pr-i': 200,
            'repos-include-course-codes': False
    }

def analyze_developer(data):
    return "Open Source Fan"

def get_db():
    client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")
    db = client["animal_db"]
    return db

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/type-of-developer',  methods=['GET', 'POST'])
def type_of_developer():
    if request.method == 'POST':
        developer_handle = request.form.get('handle')
        developer_data = get_data(developer_handle)
        type_of_developer = analyze_developer(developer_data)
        data = {'chart_data': {'developer_type': type_of_developer, 'data': developer_data}}
        print(data)
        return render_template('type_of_developer_result.html', data=data)

    else:
        return render_template('type_of_developer.html')

@app.route('/top-developers-for-a-repo')
def top_developers_for_a_repo():
    return render_template('top_developers_for_a_repo.html')

@app.route('/hiring-system')
def hiring_system():
    return render_template('hiring_system.html')

@app.route('/animals')
def get_stored_animals():
    db = get_db()
    _animals = db.animal_tb.find()
    animals = [{"id": animal["id"], "name": animal["name"], "type": animal["type"]} for animal in _animals]
    return jsonify({"animals": animals})


@app.route('/drop')
def get_drop():
  drop()

@app.route('/form-example', methods=['GET', 'POST'])
def form_example():
    if request.method == 'POST':
        animal_name = request.form.get('animal_name')
        animal_type = request.form.get('animal_type')
        result = put_new_animal(animal_name, animal_type)


        return f'''Successfully added to database {animal_name}, {animal_type}: {result} </h1>'''
                  
    return '''
           <form method="POST">
               <div><label>Animal Name: <input type="text" name="animal_name"></label></div>
               <div><label>Type: <input type="text" name="animal_type"></label></div>
               <input type="submit" value="Submit">
           </form>'''

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)