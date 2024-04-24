from flask import Flask, jsonify

app = Flask(__name__)
data_list = []
# data = {
#   {"item": item , "cantidad": cantidad},
# }
@app.route('/items', methods=['GET'])
def get_items():
    
    return jsonify(data_list)

@app.route('/add_item', methods=['POST'])
def add_item():

    new_data = request.get_json()

    data_list.append(new_data)

    return jsonify({'message': 'Data added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8081)

