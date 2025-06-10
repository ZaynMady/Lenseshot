from Services.core_api.app.app import create_app


app = create_app(__name__)

if __name__ == "__main__": 
    app.run(debug=True)