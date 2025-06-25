from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='')

@dashboard_bp.route('/')
@jwt_required()  # Ensure the user is logged in to access the dashboard
def dashboard():
    # Render the dashboard template
    return render_template('dashboard.html')
