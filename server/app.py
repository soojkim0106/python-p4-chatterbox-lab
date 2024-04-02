from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        
        message_dict = [message.to_dict() for message in messages]
        
        return message_dict, 200

    if request.method == 'POST':
        data = request.json
        new_message = Message(
            username = data.get("username"),
            body = data.get("body")
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        new_message_dict = new_message.to_dict()
        
        return new_message_dict, 201
@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = db.session.get(Message, id)
    if request.method == "GET":
        message_serialized = message.to_dict()
        return message_serialized, 200
    
    elif request.method == 'PATCH':
        data = request.json
        for attr in data:
            setattr(message, attr, data.get(attr))
        
        db.session.add(message)
        db.session.commit()
        
        message_dict = message.to_dict()
        
        return message_dict, 200

    elif request.method =='DELETE':
        db.session.delete(message)
        db.session.commit()
        
        response_body = {
            "deleted successful": True,
            "message": "Message deleted."
        }
        
        return response_body, 200
    
if __name__ == '__main__':
    app.run(port=5555)
