from flask import Flask, g, request,jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = 'admin'
api_password = 'admin'

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        return jsonify({'message': 'Authorization failed!'}), 403
    return decorated

@app.teardown_appcontext
def db_close(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()
    query = db.execute('SELECT * FROM members')
    members = query.fetchall()

    return_values = []

    for member in members:
        member_dict = {}
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']

        return_values.append(member_dict)
        
    return jsonify({'members': return_values})

@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    query = db.execute('SELECT * FROM members WHERE id = ?', [member_id])
    member = query.fetchone()

    return jsonify({ 'member': { 'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})

@app.route('/member', methods=['POST'])
@protected
def add_member():
    data = request.get_json()
    name = data['name']
    email = data['email']
    level = data['level']

    db = get_db()
    db.execute('INSERT INTO members (name, email, level) VALUES (?, ?, ?)', [name, email, level])
    db.commit()

    query = db.execute('SELECT id, name, email, level FROM members WHERE name = ?', [name])
    result = query.fetchone()

    return jsonify({'member': { 'id': result['id'], 'name': result['name'], 'email': result['email'], 'level': result['level'] }})

@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):
    data = request.get_json()

    name = data['name']
    email = data['email']
    level = data['level']

    db = get_db()
    db.execute('UPDATE members SET name = ?, email =  ?, level = ? WHERE id = ?', [name, email, level, member_id])
    db.commit()

    query = db.execute('SELECT * FROM members WHERE id = ?', [member_id])
    member = query.fetchone()


    return jsonify({ 'member': { 'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})

@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()
    db.execute('DELETE FROM members WHERE id = ?', [member_id])
    db.commit()

    return jsonify({'message': 'The member has been deleted!'})

if __name__ == '__main__':
    app.run()