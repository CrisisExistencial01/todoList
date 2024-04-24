from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "tu_clave_secreta"
jwt = JWTManager(app)

# Reemplaza la cadena de conexión con la dirección de tu instancia MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["task_database"]
users_collection = db["users"]
tasks_collection = db["tasks"]

@app.route("/")
def home():
    return "Bienvenido al sistema de listas de tareas"

# Registrar un nuevo usuario
@app.route("/users", methods=["POST"])
def register_user():
    user = {
        "username": request.json["username"],
        "password": request.json["password"],
    }
    result = users_collection.insert_one(user)
    return {"message": "Usuario creado exitosamente", "user_id": str(result.inserted_id)}, 201

# Iniciar sesión y obtener un token JWT
@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        access_token = create_access_token(identity=str(user["_id"]))
        return jsonify(access_token=access_token), 200
    else:
        return {"message": "Credenciales inválidas"}, 401

# Crear una nueva tarea (CREATE)
@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    task = {
        "user_id": ObjectId(user_id),
        "title": request.json["title"],
        "description": request.json["description"],
        "completed": False,
    }
    result = tasks_collection.insert_one(task)
    return {"message": "Tarea creada exitosamente", "task_id": str(result.inserted_id)}, 201

# Obtener todas las tareas de un usuario (READ)
@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = []
    for task in tasks_collection.find({"user_id": ObjectId(user_id)}):
        task["_id"] = str(task["_id"])
        tasks.append(task)
    return jsonify(tasks)

# Actualizar una tarea (UPDATE)
@app.route("/tasks/<string:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    updated_task = {
        "title": request.json["title"],
        "description": request.json["description"],
        "completed": request.json["completed"],
    }
    tasks_collection.update_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)}, {"$set": updated_task})
    return {"message": "Tarea actualizada exitosamente"}

# Buscar una tarea por su ID (READ)
@app.route("/tasks/<string:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = tasks_collection.find_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)})
    if task:
        task["_id"] = str(task["_id"])
        return jsonify(task)
    else:
        return {"message": "Tarea no encontrada"}, 404

# Eliminar una tarea (DELETE)
@app.route("/tasks/<string:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    tasks_collection.delete_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)})
    return {"message": "Tarea eliminada exitosamente"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)

