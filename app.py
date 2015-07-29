from flask import Flask
from app.controller import root, add_creative, copy_adset

app = Flask(__name__)
app.register_blueprint(root.app)
app.register_blueprint(add_creative.app)
app.register_blueprint(copy_adset.app)

if __name__ == '__main__':
    app.run(debug=True)
