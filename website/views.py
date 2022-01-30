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


@views.route('/hire-me/<int:record_id>', methods=['GET', 'POST'])
@login_required
def hire_me(record_id):
    try:
        from .models import Plumbers, HiredUser, Note
        import datetime
        now = datetime.datetime.now()
        hired_plumber = Plumbers.query.get(record_id)

        name = hired_plumber.name
        telephone = hired_plumber.telephone
        work = hired_plumber.work
        status = 'On The Way'
        plumber_id = hired_plumber.id
        user_id = current_user.id
        already_hired = HiredUser.user_id
        data = name + ' is hired, he will be on the way.'

        from .models import HiredUser, User
        h_user = HiredUser.query.filter_by(name=name).first()
        user = HiredUser.query.filter_by(user_id=user_id).first()
        if h_user:
            flash(name + ' is already on hire.', category='error')
        elif user:
            flash('A plumber has already been hired by you. Once the current hire is completed, you can hire more.',
                  category='error')
        else:
            from . import db
            new_hired_plumber = HiredUser(name=name, telephone=telephone, work=work, status=status, user_id=user_id, plumber_id=plumber_id)
            db.session.add(new_hired_plumber)
            db.session.commit()
            notifications = Note(data=data, date=now, user_id=user_id)
            db.session.add(notifications)
            db.session.commit()
            flash(name+' is hired successfully, check Current Hiring for more details.', category='success')
    except Exception as e:
        print(e)

    return render_template("selected_plumber.html", user=current_user, plumber=hired_plumber)
