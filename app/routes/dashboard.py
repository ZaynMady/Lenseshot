from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required

from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='')

@dashboard_bp.route('/')
@login_required  # Ensure the user is logged in to access the dashboard
def dashboard():
    # Render the dashboard template
    return render_template('dashboard.html')
