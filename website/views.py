from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import json

from nltk.corpus import stopwords

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
            new_hired_plumber = HiredUser(name=name, telephone=telephone, work=work, status=status, user_id=user_id,
                                          plumber_id=plumber_id)
            db.session.add(new_hired_plumber)
            db.session.commit()
            notifications = Note(data=data, date=now, user_id=user_id)
            db.session.add(notifications)
            db.session.commit()
            flash(name + ' is hired successfully.', category='success')
    except Exception as e:
        print(e)

    return redirect(url_for("views.current_hiring"))


@views.route('/current-hiring', methods=['GET', 'POST'])
@login_required
def current_hiring():
    from .models import HiredUser
    current_hired_user = HiredUser.query.all()
    return render_template("current_hiring.html", user=current_user, hired=current_hired_user)


@views.route('/details-of-hired-plumber/<int:record_id>', methods=['GET', 'POST'])
@login_required
def view_hired_plumber_details(record_id):
    from .models import Plumbers, HiredUser

    status_of_hired_plumber = HiredUser.query.get(record_id)
    plumber_id = status_of_hired_plumber.plumber_id

    details_of_hired_plumber = Plumbers.query.get(plumber_id)
    return render_template("view_details_hired_plumber.html", user=current_user, plumber=details_of_hired_plumber,
                           hired_plumber=status_of_hired_plumber)


@views.route('/update-arrived/<int:record_id>', methods=['GET', 'POST'])
@login_required
def update_arrived(record_id):
    try:
        from .models import HiredUser, Note
        details_of_hired_plumber = HiredUser.query.get(record_id)
        name = details_of_hired_plumber.name
        status = 'Arrived'
        data = name + ' has arrived at your location. Make sure to click work completed once the work is done'
        import datetime
        now = datetime.datetime.now()
        user_id = current_user.id

        from . import db
        details_of_hired_plumber.status = status
        db.session.commit()

        notifications = Note(data=data, date=now, user_id=user_id)
        db.session.add(notifications)
        db.session.commit()

        flash(name + " has arrived at your location.",
              category="success")
        flash("Make sure to click work completed button once the work is done.",
              category="success")

    except Exception as e:
        flash("Something went wrong !", category="error")
        print(e)

    return redirect(url_for("views.current_hiring"))


@views.route('/work-completed/<int:record_id>', methods=['GET', 'POST'])
@login_required
def work_completed(record_id):
    try:
        from .models import HiredUser, HiredHistory, Note
        details_of_hired_plumber = HiredUser.query.get(record_id)

        name = details_of_hired_plumber.name
        telephone = details_of_hired_plumber.telephone
        work = details_of_hired_plumber.work
        status = 'Completed'
        user_id = details_of_hired_plumber.user_id
        plumber_id = details_of_hired_plumber.plumber_id

        data = name + ' has completed his service. You can make the payment now'
        import datetime
        now = datetime.datetime.now()
        user_id_2 = current_user.id

        if user_id == current_user.id:
            from . import db
            formated_date = now.strftime("%d/%m/%Y %H:%M:%S")
            # Adding hiring to completed hiring list
            new_entry = HiredHistory(name=name, telephone=telephone, work=work, status=status,
                                     user_id=user_id, plumber_id=plumber_id, date=formated_date)
            db.session.add(new_entry)
            db.session.commit()

            # Deleting the hiring from hired user table so the user can hire another service provider.
            db.session.delete(details_of_hired_plumber)
            db.session.commit()

            notifications = Note(data=data, date=now, user_id=user_id_2)
            db.session.add(notifications)
            db.session.commit()
            flash(name + ' has completed his service', category='success')
            flash('Please pay the service amount requested by the plumber',
                  category='success')

        else:
            flash('Sorry, we couldn\'t update the hiring as completed !', category='error')

    except Exception as e:
        print(e)
        flash("Something went wrong !", category="error")

    return redirect(url_for("views.hired_history"))


@views.route('/hired-history', methods=['GET', 'POST'])
@login_required
def hired_history():
    from .models import HiredHistory
    hired_plumber_history = HiredHistory.query.all()
    return render_template("completed_hiring.html", user=current_user, hired=hired_plumber_history)


@views.route('/details-of-hired-plumber-history/<int:record_id>', methods=['GET', 'POST'])
@login_required
def view_hired_plumber_history_details(record_id):
    from .models import Plumbers, HiredHistory

    status_of_hired_plumber = HiredHistory.query.get(record_id)
    plumber_id = status_of_hired_plumber.plumber_id

    details_of_hired_plumber = Plumbers.query.get(plumber_id)
    return render_template("view_details_hired_plumber_history.html", user=current_user,
                           plumber=details_of_hired_plumber, hired_plumber=status_of_hired_plumber)


@views.route('/recommend-based-on-city', methods=['GET', 'POST'])
@login_required
def recommend_based_on_city():
    from .models import CityEngine
    loaded_engine = CityEngine.recommendations
    from .models import Plumbers
    city = current_user.city
    id_1 = loaded_engine(city)[0][0]
    id_2 = loaded_engine(city)[0][1]
    id_3 = loaded_engine(city)[0][2]
    id_4 = loaded_engine(city)[0][3]
    id_5 = loaded_engine(city)[0][4]
    id_6 = loaded_engine(city)[0][5]
    id_7 = loaded_engine(city)[0][6]
    id_8 = loaded_engine(city)[0][7]
    id_9 = loaded_engine(city)[0][8]
    id_10 = loaded_engine(city)[0][9]

    recommended_plumber_1 = Plumbers.query.get(id_1)
    recommended_plumber_2 = Plumbers.query.get(id_2)
    recommended_plumber_3 = Plumbers.query.get(id_3)
    recommended_plumber_4 = Plumbers.query.get(id_4)
    recommended_plumber_5 = Plumbers.query.get(id_5)
    recommended_plumber_6 = Plumbers.query.get(id_6)
    recommended_plumber_7 = Plumbers.query.get(id_7)
    recommended_plumber_8 = Plumbers.query.get(id_8)
    recommended_plumber_9 = Plumbers.query.get(id_9)
    recommended_plumber_10 = Plumbers.query.get(id_10)

    return render_template("city_plumbers_recommendation.html", user=current_user,
                           plumber_1=recommended_plumber_1, plumber_2=recommended_plumber_2,
                           plumber_3=recommended_plumber_3, plumber_4=recommended_plumber_4,
                           plumber_5=recommended_plumber_5, plumber_6=recommended_plumber_6,
                           plumber_7=recommended_plumber_7, plumber_8=recommended_plumber_8,
                           plumber_9=recommended_plumber_9, plumber_10=recommended_plumber_10)
