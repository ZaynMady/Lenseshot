from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from os import path, makedirs

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='')

BASE_PROJECT_PATH = "app/projects/" #base path for Project files

@dashboard_bp.route('/')
@jwt_required()  # Ensure the user is logged in to access the dashboard
def dashboard():
    # Render the dashboard template
    return render_template('dashboard.html')

def create_project(project_name):
    #Function to create a new project
    path = path.join(BASE_PROJECT_PATH, project_name)
    makedirs(path, exist_ok=True)  # Create the project directory if it doesn't exist

    makedirs(path.join(path, 'scripts'), exist_ok=True)  # Create screenplays directory
    makedirs(path.join(path, 'shotlist'), exist_ok=True)  # Create shotlist directory
    makedirs(path.join(path, 'budget'), exist_ok=True)  # Create budget directory
