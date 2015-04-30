from flask import Flask
from app.controller import root

app = Flask(__name__)
app.register_blueprint(root.app)

if __name__ == '__main__':
    app.run(debug=True)
