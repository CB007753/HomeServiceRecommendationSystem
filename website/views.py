from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
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
    try:
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
    except Exception as e:
        flash("Something went wrong !", category="error")
        print(e)


@views.route('/plumbers', methods=['GET', 'POST'])
@login_required
def plumbers():
    try:
        from .models import Plumbers
        plumbers = Plumbers.query.all()
        return render_template("plumbers_page.html", user=current_user, plumbers=plumbers)
    except Exception as e:
        flash("Something went wrong !", category="error")
        print(e)


@views.route('/view-profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    return render_template("profile_page.html", user=current_user)


@views.route('/edit-profile-page', methods=['GET', 'POST'])
@login_required
def edit_profile_page():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            fullname = request.form.get('name')
            city = request.form.get('city')
            address = request.form.get('address')
            user_id = current_user.id
            current_user_email = current_user.email

            from .models import User
            user = User.query.filter_by(email=email).first()
            if user and current_user_email != email:
                flash('Email is already taken, try another email.', category='error')
            elif len(fullname) < 3:
                flash('Full name must be greater than 2 characters.', category='error')
            elif len(email) < 4:
                flash('Email must be greater than 3 characters.', category='error')
            elif len(address) < 10:
                flash('Address is too short.', category='error')
            else:
                from .models import User
                edit_user = User.query.get(user_id)

                from . import db

                edit_user.fullname = fullname
                edit_user.email = email
                edit_user.address = address
                edit_user.city = city

                db.session.commit()
                flash('Profile Updated Successfully.', category='success')
                return redirect(url_for('views.view_profile'))
    except Exception as e:
        print(e)
        flash('Something went wrong.', category='error')
    return render_template("edit_profile_page.html", user=current_user)


@views.route('/view-plumber-details/<int:record_id>', methods=['GET', 'POST'])
@login_required
def view_plumber_details(record_id):
    try:
        from .models import Plumbers, WorkEngine, HiredUser
        selected_plumber = Plumbers.query.get(record_id)
        name = selected_plumber.name
        plumber_work = selected_plumber.work
        loaded_engine = WorkEngine.recommendations
        h_user = HiredUser.query.filter_by(name=name).first()
        if h_user:
            status = 'On A Hire'
        else:
            status = 'Available'

        id_1 = loaded_engine(plumber_work)[0][0]
        id_2 = loaded_engine(plumber_work)[0][1]
        id_3 = loaded_engine(plumber_work)[0][2]
        id_4 = loaded_engine(plumber_work)[0][3]
        id_5 = loaded_engine(plumber_work)[0][4]
        id_6 = loaded_engine(plumber_work)[0][5]

        recommended_plumber_1 = Plumbers.query.get(id_1)
        recommended_plumber_2 = Plumbers.query.get(id_2)
        recommended_plumber_3 = Plumbers.query.get(id_3)
        recommended_plumber_4 = Plumbers.query.get(id_4)
        recommended_plumber_5 = Plumbers.query.get(id_5)
        recommended_plumber_6 = Plumbers.query.get(id_6)

        return render_template("selected_plumber.html", user=current_user, plumber=selected_plumber,
                               rec_plumber_1=recommended_plumber_1, rec_plumber_2=recommended_plumber_2,
                               rec_plumber_3=recommended_plumber_3, rec_plumber_4=recommended_plumber_4,
                               rec_plumber_5=recommended_plumber_5, rec_plumber_6=recommended_plumber_6, status=status)
    except Exception as e:
        flash("Something went wrong !", category="error")
        print(e)


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
        user_city = current_user.city
        plumber_city = hired_plumber.city_of_work
        if h_user:
            flash(name + ' is already on hire.', category='error')
            return redirect(url_for("views.plumbers"))
        elif user:
            flash('A plumber has already been hired by you. Once the current hire is completed, you can hire more.',
                  category='error')
            return redirect(url_for("views.current_hiring"))
        elif user_city != plumber_city:
            flash(name + ' is currently working in ' + plumber_city + ', you can only hire plumbers from ' + user_city +
                  '.',
                  category='error')
            return redirect(url_for("views.plumbers"))
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
            return redirect(url_for("views.current_hiring"))
    except Exception as e:
        print(e)
        flash("Something went wrong !", category="error")
        return redirect(url_for("views.current_hiring"))


@views.route('/current-hiring', methods=['GET', 'POST'])
@login_required
def current_hiring():
    try:
        from .models import HiredUser
        current_hired_user = HiredUser.query.all()
        return render_template("current_hiring.html", user=current_user, hired=current_hired_user)

    except Exception as e:
        flash("Something went wrong !", category="error")
        print(e)


@views.route('/details-of-hired-plumber/<int:record_id>', methods=['GET', 'POST'])
@login_required
def view_hired_plumber_details(record_id):
    try:
        from .models import Plumbers, HiredUser

        status_of_hired_plumber = HiredUser.query.get(record_id)
        plumber_id = status_of_hired_plumber.plumber_id

        details_of_hired_plumber = Plumbers.query.get(plumber_id)
        return render_template("view_details_hired_plumber.html", user=current_user, plumber=details_of_hired_plumber,
                               hired_plumber=status_of_hired_plumber)
    except Exception as e:
        flash("Something went wrong !", category="error")
        print(e)


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
        from .models import HiredUser, HiredHistory, Note, UserInterest
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

            # Adding user interest
            new_interest = UserInterest(user_id=user_id, interest=work)
            db.session.add(new_interest)
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
    try:
        from .models import HiredHistory
        hired_plumber_history = HiredHistory.query.all()
        return render_template("completed_hiring.html", user=current_user, hired=hired_plumber_history)

    except Exception as e:
        flash("Something went wrong !", category="error")
        print(e)


@views.route('/details-of-hired-plumber-history/<int:record_id>', methods=['GET', 'POST'])
@login_required
def view_hired_plumber_history_details(record_id):
    from .models import Plumbers, HiredHistory, Review
    import datetime

    now = datetime.datetime.now()
    status_of_hired_plumber = HiredHistory.query.get(record_id)
    plumber_id = status_of_hired_plumber.plumber_id
    user_id = current_user.id
    hired_date = status_of_hired_plumber.date

    user_exist = Review.query.filter_by(user_id=user_id, plumber_id=plumber_id, hired_date=hired_date).first()

    if user_exist:
        existence = 'true'
    else:
        existence = 'false'

    details_of_hired_plumber = Plumbers.query.get(plumber_id)
    try:
        if request.method == 'POST':
            message = request.form.get('message')

            user_name = current_user.fullname
            formatted_date = now.strftime("%B %d, %Y")

            from . import db
            new_review = Review(name=user_name, message=message, date=formatted_date,
                                user_id=user_id, plumber_id=plumber_id, hired_date=hired_date)
            db.session.add(new_review)
            db.session.commit()
            flash("Review Added !", category="success")
            return redirect(url_for('views.view_hired_plumber_history_details', record_id=record_id))

    except Exception as e:
        flash("Something went wrong !", category="error")
        print(e)
    return render_template("view_details_hired_plumber_history.html", user=current_user,
                           plumber=details_of_hired_plumber, hired_plumber=status_of_hired_plumber, existence=existence)


@views.route('/recommend-based-on-city', methods=['GET', 'POST'])
@login_required
def recommend_based_on_city():
    try:
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
    except Exception as e:
        print(e)
        flash("Something went wrong", category="error")


@views.route('/recommend-based-on-interest', methods=['GET', 'POST'])
@login_required
def recommend_based_on_interest():
    try:
        import sqlite3
        from .models import Plumbers,UserInterest

        con = sqlite3.connect("E:\Final_Year_Project\Assignment\website\database.db")
        print("Database opened successfully")

        my_cursor = con.execute(
            'SELECT interest , COUNT(interest) AS MOST_FREQUENT FROM user_interest WHERE user_id={}'
            ' GROUP BY interest ORDER BY COUNT(interest)DESC'.format(current_user.id))

        user_exist = UserInterest.query.filter_by(user_id=current_user.id).first()

        if user_exist:
            for row in my_cursor:
                # this prints the most occurring value and the number of occurrence
                print(row)
                from .models import WorkEngine
                loaded_engine = WorkEngine.recommendations
                work = row[0]
                id_1 = loaded_engine(work)[0][0]
                id_2 = loaded_engine(work)[0][1]
                id_3 = loaded_engine(work)[0][2]
                id_4 = loaded_engine(work)[0][3]
                id_5 = loaded_engine(work)[0][4]
                id_6 = loaded_engine(work)[0][5]
                id_7 = loaded_engine(work)[0][6]
                id_8 = loaded_engine(work)[0][7]
                id_9 = loaded_engine(work)[0][8]
                id_10 = loaded_engine(work)[0][9]
                id_11 = loaded_engine(work)[0][10]
                id_12 = loaded_engine(work)[0][11]

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
                recommended_plumber_11 = Plumbers.query.get(id_11)
                recommended_plumber_12 = Plumbers.query.get(id_12)

                return render_template("recommendation_based_on_interest.html", user=current_user,
                                       plumber_1=recommended_plumber_1, plumber_2=recommended_plumber_2,
                                       plumber_3=recommended_plumber_3, plumber_4=recommended_plumber_4,
                                       plumber_5=recommended_plumber_5, plumber_6=recommended_plumber_6,
                                       plumber_7=recommended_plumber_7, plumber_8=recommended_plumber_8,
                                       plumber_9=recommended_plumber_9, plumber_10=recommended_plumber_10,
                                       plumber_11=recommended_plumber_11, plumber_12=recommended_plumber_12)
        else:
            flash("You haven\'t hired any plumber yet, start hiring more plumbers to find your interest",
                  category="error")
            return redirect(url_for("views.plumbers"))
    except Exception as e:
        print(e)
        flash("Something went wrong", category="error")
        return redirect(url_for("views.plumbers"))
