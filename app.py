from asyncio import tasks
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
Bootstrap(app)

# database setup.
basedir = os.path.dirname(__file__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'todo.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# application models.

class Task(db.Model):
    """model to store a task data"""

    id = db.Column(db.Integer, primary_key=True)
    """:type : int"""

    description = db.Column(db.String(200), nullable=False)
    """:type : str"""

    situation = db.Column(db.String(200), nullable=False)
    """:type : str"""

    spend_hours = db.Column(db.Integer, nullable=False)
    """:type : str"""

    category = db.Column(db.String(200), nullable=False)
    """:type : str"""

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    """:type : datetime"""

    user_id = db.Column(db.Integer, nullable=False)
    """:type : str"""
 
    def __repr__(self):
        """override __repr__ method"""
        return f"Task: #{self.id}, content: {self.description, self.situation, self.spend_hours, self.category, self.user_id}"

class User(db.Model):
    """model to store a user data"""

    id = db.Column(db.Integer, primary_key=True)
    """:type : int"""

    login = db.Column(db.String(200), nullable=False)
    """:type : str"""

    password = db.Column(db.String(200), nullable=False)
    """:type : str"""

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    """:type : datetime"""
 
    def __repr__(self):
        """override __repr__ method"""
        return f"Task: #{self.id}, content: {self.login, self.password}"

# routes and handlers.


# user1 = User(login="Lucas", password="123123")
# user2 = User(login="Victor", password="coxinha123")
# try:
#     db.session.add(user1)
#     db.session.add(user2)
#     db.session.commit()
    
# except:
#     print("Erro ao cadastrar usuários")

@app.route('/', methods=['GET', 'POST'])
def index():
    """root route"""
    if request.method == 'POST':
        taskCreate = Task(description=request.form['description'], situation=request.form['situation'], spend_hours=request.form['spend_hours'], category=request.form['category'], user_id=int(request.form['user_id']))
        try:
            db.session.add(taskCreate)
            db.session.commit()
            tasks = Task.query.order_by(Task.date_created).all()
            categories = []
            for task in tasks:
                if task.user_id == int(request.form['user_id']):
                    addCategory = True
                    for category in categories:
                        if(category['name'] == task.category):
                            category['hours'] += task.spend_hours
                            addCategory = False
                    if(addCategory):
                        categories.append({
                            'name': task.category,
                            'hours': task.spend_hours
                        })
            return render_template('index.html', tasks=tasks, categories=categories, login=int(request.form['user_id']))
        except:
            return "Houve um erro, ao inserir a tarefa"
    else:
        return render_template('index.html', tasks=[], categories=[], login=0)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """root route"""
    if request.method == 'POST':
        users = User.query.order_by(User.date_created).all()
        findUserId = 0
        for user in users:
            if(user.login == request.form['login'] and user.password == request.form['password']):
                findUserId = user.id
            
        if findUserId != 0:
            tasks = Task.query.order_by(Task.date_created).all()
            categories = []
            for task in tasks:
                if task.user_id == findUserId:
                    addCategory = True
                    for category in categories:
                        if(category['name'] == task.category):
                            category['hours'] += task.spend_hours
                            addCategory = False
                    if(addCategory):
                        categories.append({
                            'name': task.category,
                            'hours': task.spend_hours
                        })
            return render_template('index.html', tasks=tasks, categories=categories, login=findUserId)
        else:
            return render_template('login.html', error="login_error")
    else:
        return render_template('login.html', error="no_error")

@app.route('/delete/<int:id>/<int:user_id>')
def delete(id, user_id):
    """delete a task"""
    task = Task.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        tasks = Task.query.order_by(Task.date_created).all()
        categories = []
        for task in tasks:
            if task.user_id == int(user_id):
                addCategory = True
                for category in categories:
                    if(category['name'] == task.category):
                        category['hours'] += task.spend_hours
                        addCategory = False
                if(addCategory):
                    categories.append({
                        'name': task.category,
                        'hours': task.spend_hours
                    })
        return render_template('index.html', tasks=tasks, categories=categories, login=int(user_id))
    except:
        return "Houve um erro, ao inserir a tarefa"


@app.route('/update/<int:id>/<int:user_id>', methods=['GET', 'POST'])
def update(id, user_id):
    """update route"""
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.description = request.form['description']
        task.situation = request.form['situation']
        task.spend_hours = request.form['spend_hours']
        task.category = request.form['category']
        try:
            db.session.commit()
            tasks = Task.query.order_by(Task.date_created).all()
            categories = []
            for task in tasks:
                if task.user_id == int(user_id):
                    addCategory = True
                    for category in categories:
                        if(category['name'] == task.category):
                            category['hours'] += task.spend_hours
                            addCategory = False
                    if(addCategory):
                        categories.append({
                            'name': task.category,
                            'hours': task.spend_hours
                        })
            return render_template('index.html', tasks=tasks, categories=categories, login=int(user_id))
        except:
            return "Houve um erro, ao atualizar a tarefa"
    else:
        return render_template('update.html', task=task, login=user_id)