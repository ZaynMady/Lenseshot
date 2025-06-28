def test_register_page(client):
    """Test that the register page loads correctly."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_user(client):
    """Test user registration."""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Should redirect to login page

def test_login_user(client, test_user):
    """Test user login."""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data  # Should redirect to dashboard

def test_invalid_login(client, test_user):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword',
        'remember': False
    })
    assert b'Invalid email or password' in response.data

def test_logout(client, test_user):
    """Test user logout."""
    # First login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': False
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Should redirect to login page