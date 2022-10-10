from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskapp.auth import login_required
from flaskapp.db import get_db

bp = Blueprint('inbox', __name__)

def get_message(id):
    message = get_db().execute(
        'SELECT m.id, m.title, m.body, m.created, m.author_id, u.username, m.to_id'
        ' FROM message m JOIN user u ON m.author_id = u.id'
        ' WHERE m.id = ?',
        (id,)
    ).fetchone()
    if message is None:
        abort(404, f"Message with ID {id} does not exist.")
    if g.user['id'] != message['author_id'] and g.user['id'] != message['to_id']:
        # the user is neither the author or the recipient of the message.
        abort(403)
    return message

@bp.route('/')
@login_required
def index():
    userId = g.user['id']
    db = get_db()
    messages = db.execute(
        'SELECT m.id, title, body, created, author_id, u.username'
        ' FROM message m JOIN user u ON m.author_id = u.id'
        ' WHERE m.to_id = ?'
        ' ORDER BY m.created DESC',
        (userId,)
    ).fetchall()
    return render_template('inbox/index.html', messages=messages)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        recipient = request.form['to']
        error = None

        if not title:
            error = 'Title is required.'
        if not body:
            error = 'Body is required.'
        if not recipient:
            error = 'Recipient is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO message (author_id, title, body, to_id) VALUES (?, ?, ?, ?)',
                (g.user['id'], title, body, recipient))
            db.commit()
            return redirect(url_for('inbox.index'))
    return render_template('inbox/create.html')

@bp.route('/<int:id>/details', methods=('GET',))
@login_required
def details(id):
    message = get_message(id)
    return render_template('inbox/details.html', message=message)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM message WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('inbox.index'))
