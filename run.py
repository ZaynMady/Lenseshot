from app import create_app

#create the app instance
app = create_app()
if __name__ == "__main__": 
    app.run(host="0.0.0.0",debug=True)