from flask import Blueprint, render_template 
from app.models.userbase import user
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request


# Create a blueprint for user account management
user_account_bp = Blueprint('user_account_bp', __name__, 
                            url_prefix='/account', 
                            template_folder="templates", 
                            static_folder="static")

# Route for user account settings
@jwt_required()
@user_account_bp.route('/settings', methods=['GET', 'POST'])
def account_settings():
    verify_jwt_in_request()  # Ensure the JWT is valid
    # Get the current user's identity
    current_user_id = get_jwt_identity()
    # Here you would typically fetch the user's data from the database
    User = user.query.filter_by(id=current_user_id).first()
    # Render the account settings template
    return render_template('account_settings.html', title='Account Settings', username= User.username, email=User.email)