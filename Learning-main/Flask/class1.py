from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

gull = Flask(__name__)
gull.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///john.db'
db = SQLAlchemy(gull)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    contact = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)

with gull.app_context():
    db.create_all()

@gull.route('/')
def home():
    return render_template('index.html')

@gull.route('/register' , methods=['GET','POST'])
def register():
    if request.method=='POST':
        #Get data from form
        username=request.form['username']
        password=request.form['password']
        contact=request.form['contact']
        role=request.form['role']

        user_exists=User.query.filter_by(username=username).first()
        if user_exists:
            print("User Name already Exist")
            return redirect(url_for('register'))
        
        new_user=User(username=username, password=password, contact=contact, role=role)
        db.session.add(new_user)
        db.session.commit()
        print("Data inserted successfully")
        return redirect(url_for("home"))

    return render_template('register.html')

if __name__ == '__main__':
    gull.run(debug=True)
