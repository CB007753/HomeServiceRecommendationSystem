from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
import json

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/notification', methods=['GET', 'POST'])
@login_required
def notification():
    return render_template("notification.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    from .models import Note
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            from . import db
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
