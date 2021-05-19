from flask import Flask, request
import flask.scaffold
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from flask_restplus import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_mysqldb import MySQL
from datetime import date
from functools import wraps

today = date.today().strftime("%Y-%m-%d")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

#Authorization
authorizations={
    'apikey':{
        'type':'apiKey',
        'in':'header',
        'name':'User'
    }
}

#DataBase Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sun@0097'
app.config['MYSQL_DB'] = 'todolist'

mysql = MySQL(app)

api = Api(app, version='1.0', title='TodoMVC API', description='A simple TodoMVC API', authorizations=authorizations)

def readAccess(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None
        if 'User' in request.headers:
            token = request.headers['User']
        if not token:
            return {'message':'Not Yet Authorized'},401
        cur = mysql.connection.cursor()
        resval=cur.execute("SELECT * FROM users WHERE userid in (%s)",(token,))
        cur.close()
        if resval==0:
            return {'message':'User not Identified'},402
        return f(*args,**kwargs)
    return decorated

def writeAccess(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None
        if 'User' in request.headers:
            token = request.headers['User']
        if not token:
            return {'message':'Not Yet Authorized'},401
        cur = mysql.connection.cursor()
        resval=cur.execute("SELECT access FROM users WHERE userid in (%s)",(token,))
        if resval==0:
            cur.close()
            return {'message':'User not Identified'},402
        details = cur.fetchall()
        cur.close()
        for i in details:
            if i[0]!='write':
                return {'message':'Action Not Permitted'},403
        return f(*args,**kwargs)
    return decorated


ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'dueby': fields.Date(required=True,description='format: YYYY-MM-DD'),
    'status':fields.String(required=True,description = 'Status of project [Not started, In progress, Finished]')
})

class TodoDAO(object):
    def __init__(self):
        self.counter=0

    def setCounter(self):
        cur = mysql.connection.cursor()
        cnt=0
        resval = cur.execute("SELECT MAX(id) FROM todos")
        if resval>0:
            details=cur.fetchall()
            for detail in details:
                cnt=detail[0]
        cur.close()
        if cnt == None:
            cnt=0
        print(cnt)
        self.counter=cnt

    def get(self, id):
        cur = mysql.connection.cursor()
        resval = cur.execute("SELECT * FROM todos WHERE id=%s",(id,))
        if resval>0:
            details=cur.fetchall()
            cur.close()
            for detail in details:
                obj = {
                    'id':detail[0],
                    'task':detail[1],
                    'dueby':detail[2].strftime("%Y-%m-%d"),
                    'status':detail[3]
                }
                return obj
        cur.close()
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        self.setCounter()
        todo = data
        todo['id'] = self.counter = self.counter + 1
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO todos VALUES(%s,%s,%s,%s)",(todo['id'],todo['task'],todo['dueby'],todo['status']))
        mysql.connection.commit()
        cur.close()
        return todo

    def update(self, id, data):
        todo = data
        todo['id'] = id
        cur = mysql.connection.cursor()
        cur.execute("UPDATE todos SET task=%s,dueby=%s,status=%s WHERE id=%s",(todo['task'],todo['dueby'],todo['status'],todo['id']))
        mysql.connection.commit()
        cur.close()
        return todo

    def change(self, id, status):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE todos SET status=%s WHERE id=%s",(status,id))
        mysql.connection.commit()
        cur.close()

    def delete(self, id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM todos WHERE id=%s",(id,))
        mysql.connection.commit()
        cur.close()
    
    def dueTasks(self,date):
        todos=[]
        cur = mysql.connection.cursor()
        resval = cur.execute("SELECT * FROM todos WHERE status NOT IN ('Completed') AND dueby<=%s",(date,))
        if resval>0:
            details=cur.fetchall()
            for detail in details:
                obj = {
                    'id':detail[0],
                    'task':detail[1],
                    'dueby':detail[2].strftime("%Y-%m-%d"),
                    'status':detail[3]
                }
                todos.append(obj)
        cur.close()
        return todos

    def Completed(self):
        todos=[]
        cur = mysql.connection.cursor()
        resval = cur.execute("SELECT * FROM todos WHERE status IN ('Completed')")
        if resval>0:
            details=cur.fetchall()
            for detail in details:
                obj = {
                    'id':detail[0],
                    'task':detail[1],
                    'dueby':detail[2].strftime("%Y-%m-%d"),
                    'status':detail[3]
                }
                todos.append(obj)
        cur.close()
        return todos


DAO = TodoDAO()
# DAO.create({'task': 'Build an API'})
# DAO.create({'task': '?????'})
# DAO.create({'task': 'profit!'})


@ns.route('/')
@ns.response(402, 'User not identified')
@ns.response(401, 'Authorization not done')
@ns.response(403, 'Action not Permitted')
@ns.response(201, 'Insert Success')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    # @ns.marshal_list_with(todo)
    @api.doc(security='apikey')
    @readAccess
    def get(self):
        '''List all tasks'''
        todos=[]
        cur = mysql.connection.cursor()
        resval = cur.execute("SELECT * FROM todos")
        if resval>0:
            details=cur.fetchall()
            for detail in details:
                obj = {
                    'id':detail[0],
                    'task':detail[1],
                    'dueby':detail[2].strftime("%Y-%m-%d"),
                    'status':detail[3]
                }
                todos.append(obj)
        cur.close()
        return todos

    @ns.doc('create_todo')
    @ns.expect(todo)
    # @ns.marshal_with(todo, code=201)
    @api.doc(security='apikey')
    @writeAccess
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.response(402, 'User not identified')
@ns.response(401, 'Authorization not done')
@ns.response(403, 'Action not Permitted')
@ns.param('id', 'The task identifier')
@ns.response(200, 'Success')
@ns.response(204, 'Delete Success')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @api.doc(security='apikey')
    @readAccess
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    @api.doc(security='apikey')
    @writeAccess
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return  '', 204

    @ns.expect(todo)
    # @ns.marshal_with(todo)
    @api.doc(security='apikey')
    @writeAccess
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

@ns.route('/<int:id><string:status>')
@ns.response(402, 'User not identified')
@ns.response(401, 'Authorization not done')
@ns.response(403, 'Action not Permitted')
@ns.param('status', 'new Status')
@ns.param('id', 'The task identifier')
@ns.response(205, 'Update Success')
class todo(Resource):
    '''lets you modify the status'''
    @ns.doc('change_todo')
    @api.doc(security='apikey')
    @writeAccess
    def options(self, id,status):
        '''Update status given its identifier'''
        DAO.change(id,status)
        return '',205

@ns.route('/due/<date>')
@ns.response(402, 'User not identified')
@ns.response(401, 'Authorization not done')
@ns.param('date', 'YYYY-MM-DD')
@ns.response(200, 'Success')
class todoget1(Resource):
    '''Search on specific details'''
    @ns.doc('due_date_todo')
    @api.doc(security='apikey')
    @readAccess
    def get(self,date):
        '''Fetch all due tasks by Date'''
        return DAO.dueTasks(date),200

@ns.route('/overdue')
@ns.response(200, 'Success')
@ns.response(402, 'User not identified')
@ns.response(401, 'Authorization not done')
class todoget2(Resource):
    '''Search on specific details'''
    @ns.doc('due_today_todo')
    @api.doc(security='apikey')
    @readAccess
    def get(self):
        '''Fetch all due tasks'''
        return DAO.dueTasks(today),200


@ns.route('/finished')
@ns.response(200, 'Success')
@ns.response(402, 'User not identified')
@ns.response(401, 'Authorization not done')
class todoget3(Resource):
    '''Search on specific details'''
    @ns.doc('completed_todo')
    @api.doc(security='apikey')
    @readAccess
    def get(self):
        '''Fetch all Completed tasks'''
        return DAO.Completed(),200   


if __name__ == '__main__':
    app.run(debug=True)