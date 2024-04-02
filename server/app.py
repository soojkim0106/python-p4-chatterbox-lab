from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
api = Api(app)

db.init_app(app)


@app.route("/")
def welcome():
    return "Chatterbox index"

class Messages(Resource):
    def get(self):
        try:
            serialized_messages = [
                message.to_dict()
                for message in Message.query.order_by(Message.created_at.asc())
            ]
            return serialized_messages, 200
        except Exception as e:
            return str(e), 400

    def post(self):
        try:
            data = request.json

            new_message = Message(**data)

            db.session.add(new_message)
            db.session.commit()

            message_dict = new_message.to_dict()

            return message_dict, 201

        except Exception as e:
            return str(e), 400


api.add_resource(Messages, "/messages")


class MessageByID(Resource):
    def get(self, id):
        try:
            message = db.session.get(Message, id).to_dict()
            return message, 200
        except Exception as e:
            return str(e), 400
    
    def patch(self, id):
        try:
            if not (message := db.session.get(Message, id)):
                return {"message": f"Could not find {id}"}

            for attr in request.json:
                setattr(message, attr, request.json[attr])

            db.session.commit()

            message_dict = message.to_dict()

            return message_dict, 200
        except Exception as e:
            return str(e), 400
    
    def delete(self, id):
        try:
            message = db.session.get(Message, id)
            
            db.session.delete(message)
            db.session.commit()
            
            return {}, 204
        except Exception as e:
            return str(e), 400

api.add_resource(MessageByID, "/messages/<int:id>")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
