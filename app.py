from flask import Flask,jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/testhateoas"

ma = Marshmallow(app)
db= SQLAlchemy(app)


class Student(db.Model):
    __tablename__='students'
    id= db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(50), nullable=False,unique=True)
    name= db.Column(db.String(50),nullable=False)
    mail= db.Column(db.String(50), nullable=False,unique=True)

    def __init__(self, username, name, mail):
        self.username=username
        self.name= name
        self.mail= mail

db.create_all()


class StudentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'name', 'mail','_links')
        # Smart hyperlinking
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("get_Student", values=dict(id="<id>")),
            "collection": ma.URLFor("get_Students"),
        }
    )


student_schema= StudentSchema()
students_schema= StudentSchema(many=True)

#GET de lista completa
@app.route("/students", methods=['GET'])
def get_Students():
    all_students = Student.query.all()
    return jsonify(students_schema.dump(all_students)),200


#GET en base un id
@app.route("/students/<id>")
def get_Student(id):
    student = Student.query.get(id)
    if not student is None:
        return student_schema.dump(student),200
    
    return jsonify({'message': 'students Not found'}),404


#POST
@app.route("/students", methods=['POST'])
def create_student():
    username=request.json['username']
    name=request.json['name']
    mail=request.json['mail']
    new_student= Student(username, name, mail)
    db.session.add(new_student)
    db.session.commit()
    return student_schema.jsonify(new_student),200

#PUT
@app.route("/students/<id>", methods=['PUT'])
def update_student(id):
    student= Student.query.get(id)
    if not student is None:
        student.username=request.json['username']
        student.name=request.json['name']
        student.mail=request.json['mail']
        db.session.commit()
        return student_schema.jsonify(student),200
    return jsonify({'message': 'student Not found'}),404

#DELETE
@app.route("/students/<id>", methods=['DELETE'])
def delete_student(id):
    student= Student.query.get(id)
    if not student is None:
        db.session.delete(student)
        db.session.commit()
        return student_schema.jsonify(student),200
    return jsonify({'message': 'student Not found'}),404


if __name__ == '__main__':
    app.run(debug=True, port=4000)