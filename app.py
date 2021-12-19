from flask import Flask, jsonify, request
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


def get_db():
    client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")
    db = client["animal_db"]
    return db

@app.route('/')
def ping_server():
    return "Welcome to the world of animals."

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