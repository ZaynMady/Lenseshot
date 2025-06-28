from app.models.userbase import user

def test_user_model(app):
    """Test the User model."""
    with app.app_context():
        # Create a new user
        new_user = user(
            username='modeltest',
            email='model@test.com',
            password='hashedpassword'
        )
        
        # Add to database
        from app.models import db
        db.session.add(new_user)
        db.session.commit()
        
        # Query the user
        queried_user = user.query.filter_by(email='model@test.com').first()
        
        # Assert user was created correctly
        assert queried_user is not None
        assert queried_user.username == 'modeltest'
        assert queried_user.email == 'model@test.com'
        assert queried_user.password == 'hashedpassword'