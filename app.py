import streamlit as st
import requests
from flask import Flask, request, jsonify
import pandas as pd
import threading

app = Flask(__name__)

# In-memory "database"
items = [
  {
    "id": 1,
    "name": "Inception",
    "description": "7.5/10"
  },
  {
    "id": 2,
    "name": " The god father",
    "description": "10/10"
  },
  {
    "id": 3,
    "name": "Forrest Gump",
    "description": "8/10"
  }
]


@app.route('/items', methods=['POST'])
def create_item():
    global items
    data = request.get_json()
    item_id = len(items) + 1
    new_item = {'id': item_id, 'name': data['name'], 'description': data['description']}
    items.append(new_item)
    return jsonify(new_item), 201

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        return jsonify(item)
    else:
        return jsonify({'error': 'Item not found'}), 404

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    global items
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    data = request.get_json()
    old_description = item['description']
    item['description'] = data.get('description', item['description'])
    return jsonify({'old_description': old_description, 'new_description': item['description']}), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    items = [item for item in items if item['id'] != item_id]
    return jsonify({}), 204

def run_api():
    app.run(threaded=True)

if st.button("Start API Server"):
    threading.Thread(target=run_api, daemon=True).start()

st.title('Item Manager')

if st.button('Refresh Items'):
    response = requests.get('http://localhost:5000/items')
    items = response.json()
    df = pd.DataFrame(items)
    st.dataframe(df)

name = st.text_input("Name")
description = st.text_input("Description")

if st.button('Add Item'):
    response = requests.post('http://localhost:5000/items', json={'name': name, 'description': description})
    if response.status_code == 201:
        st.success("Item added successfully!")
    else:
        st.error("Failed to add item")

selected_id = st.text_input("ID to Operate On", "")

new_description = st.text_input("New Description")

if st.button('Update Description'):
    response = requests.put(f'http://localhost:5000/items/{selected_id}', json={'description': new_description})
    if response.status_code == 200:
        result = response.json()
        st.success("Description updated successfully!")
        st.write(f"Old Description: {result['old_description']}")
        st.write(f"New Description: {result['new_description']}")
    else:
        st.error("Failed to update description")

selected_id = st.text_input("ID to Delete")

if st.button('Delete Item'):
    response = requests.delete(f'http://localhost:5000/items/{selected_id}')
    if response.status_code == 204:
        st.success("Item deleted successfully!")
    else:
        st.error("Failed to delete item")
