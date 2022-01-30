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
            flash('Notification Deleted', category='success')
        else:
            flash('Notification couldn\'t be deleted', category='error')

    return jsonify({})


@views.route('/plumbers', methods=['GET', 'POST'])
@login_required
def plumbers():
    from .models import Plumbers
    plumbers = Plumbers.query.all()
    return render_template("plumbers_page.html", user=current_user, plumbers=plumbers)


@views.route('/view-profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    return render_template("profile_page.html", user=current_user)


@views.route('/view-plumber-details/<int:record_id>', methods=['GET', 'POST'])
@login_required
def view_plumber_details(record_id):
    from .models import Plumbers
    selected_plumber = Plumbers.query.get(record_id)
    return render_template("selected_plumber.html", user=current_user, plumber=selected_plumber)
