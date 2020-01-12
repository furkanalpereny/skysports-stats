from flask import Flask, request, jsonify, render_template, current_app, send_from_directory, send_file
from app import app, get_data
import os
import time
import json


@app.route('/')
def main():
    paths = get_data.get_paths()
    return render_template("index.html", paths=paths)


@app.route('/json/<path:filename>', methods=['GET', 'POST'])
def download_json(filename):
    uploads = os.path.join(current_app.root_path, "data")
    return send_from_directory(directory=uploads, filename=filename)


@app.route('/xlsx/<path:filename>', methods=['GET', 'POST'])
def download_xlsx(filename):
    uploads = os.path.join(current_app.root_path, "data")
    path = uploads+"/"+filename
    path = get_data.json_to_xlsx(path)
    return send_file(path, as_attachment=True)


@app.route('/csv/<path:filename>', methods=['GET', 'POST'])
def download_csv(filename):
    uploads = os.path.join(current_app.root_path, "data")
    path = uploads+"/"+filename
    path = get_data.json_to_csv(path)
    return send_file(path, as_attachment=True)

@app.route('/favicon.ico', methods=['GET', 'POST'])
def favicon():
    return  "favicon.ico"
