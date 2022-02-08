from nltk.corpus import stopwords
import pandas as pd

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    city = db.Column(db.String(150))
    address = db.Column(db.String(300))
    notes = db.relationship('Note')
    hired_user = db.relationship('HiredUser')
    hired_history = db.relationship('HiredHistory')
    review = db.relationship('Review')
    interest = db.relationship('UserInterest')


class HiredUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    telephone = db.Column(db.String(150))
    work = db.Column(db.String(150))
    status = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))


class HiredHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    telephone = db.Column(db.String(150))
    work = db.Column(db.String(150))
    status = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))
    date = db.Column(db.String(150))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Plumbers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    nic = db.Column(db.String(150))
    address = db.Column(db.String(500))
    city_of_work = db.Column(db.String(150))
    telephone = db.Column(db.Integer)
    occupation = db.Column(db.String(150))
    work = db.Column(db.String(150))
    years_of_experience = db.Column(db.Integer)
    age_group = db.Column(db.String(150))
    nvq_level = db.Column(db.String(150))
    review = db.relationship('Review')


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    message = db.Column(db.String(500))
    date = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))
    hired_date = db.Column(db.String(150))


class UserInterest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    interest = db.Column(db.String(150))


class CityEngine:
    ds = pd.read_csv("E:\Final_Year_Project\Assignment\Recommendation_App\plumbers_dataset.csv")
    ds = ds[["ID", "Name", "Telephone", "City_of_work", "Work", "Years of Experience", "Age Group", "NVQ Level"]]
    ds = ds.rename({"ConvertedComp": "Plumbers"}, axis=1)

    x = ds.City_of_work
    y = ds['Years of Experience']

    # Function for removing NonAscii characters
    def _removeNonAscii(s):
        return "".join(i for i in s if ord(i) < 128)

    # Function for converting into lower case
    def make_lower_case(text):
        return text.lower()

    # Function for removing stop words(eg:'is','the', etc..)
    def remove_stop_words(text):
        text = text.split()
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
        text = " ".join(text)
        return text

    # Applying all the functions to city of work column and storing as a cleaned_city_of_work
    ds['cleaned_city_of_work'] = ds['City_of_work'].apply(_removeNonAscii)
    ds['cleaned_city_of_work'] = ds.cleaned_city_of_work.apply(func=make_lower_case)
    ds['cleaned_city_of_work'] = ds.cleaned_city_of_work.apply(func=remove_stop_words)

    from sklearn.feature_extraction.text import CountVectorizer
    # instantiating and generating the count matrix
    count = CountVectorizer()
    count_matrix = count.fit_transform(ds['cleaned_city_of_work'])
    indices = pd.Series(ds.City_of_work)

    from sklearn.metrics.pairwise import cosine_similarity
    # generating the cosine similarity matrix
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    # function that takes in the work of service provider as input and returns the top 5 recommended service providers
    def recommendations(City_of_work, cosine_sim=cosine_sim):
        recommended_city = []
        recommended_id = []
        recommended_name = []
        recommended_work = []
        recommended_exp = []
        recommend = []
        indices = CityEngine.indices
        ds = CityEngine.ds
        # getting the index of the service providers that matches the city
        idx = indices[indices == City_of_work].index[0]

        # creating a Series with the similarity scores in descending order
        score_series = pd.Series(cosine_sim[idx]).sort_values(ascending=False)

        # getting the indexes of the 10 most similar service providers
        top_5_indexes = list(score_series.iloc[1:11].index)

        # populating the list with the name,city,work and experience of the best 5 matching service providers
        for i in top_5_indexes:
            recommended_city.append(list(ds['City_of_work'])[i])
            recommended_name.append(list(ds['Name'])[i])
            recommended_work.append(list(ds['Work'])[i])
            recommended_exp.append(list(ds['Years of Experience'])[i])
            recommended_id.append(list(ds['ID'])[i])

            recommend = recommended_id, recommended_name, recommended_city, recommended_work, recommended_exp

        return recommend


class WorkEngine:
    ds = pd.read_csv("E:\Final_Year_Project\Assignment\Recommendation_App\plumbers_dataset.csv")
    ds = ds[["ID", "Name", "Telephone", "City_of_work", "Work", "Years of Experience", "Age Group", "NVQ Level"]]
    ds = ds.rename({"ConvertedComp": "Plumbers"}, axis=1)

    x = ds.Work
    y = ds['Years of Experience']

    # Data preprocessing
    # Function for removing NonAscii characters
    def _removeNonAscii(s):
        return "".join(i for i in s if ord(i) < 128)

    # Function for converting into lower case
    def make_lower_case(text):
        return text.lower()

    # Function for removing stop words(eg:'is','the', etc..)
    def remove_stop_words(text):
        text = text.split()
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
        text = " ".join(text)
        return text

    # Applying all the functions in description and storing as a cleaned_desc
    ds['cleaned_work'] = ds['Work'].apply(_removeNonAscii)
    ds['cleaned_work'] = ds.cleaned_work.apply(func=make_lower_case)
    ds['cleaned_work'] = ds.cleaned_work.apply(func=remove_stop_words)

    from sklearn.feature_extraction.text import CountVectorizer
    # instantiating and generating the count matrix
    count = CountVectorizer()
    count_matrix = count.fit_transform(ds['cleaned_work'])

    # creating a Series for the Service Provider Names so they are associated to an ordered numerical
    # list which I will use later to match the indexes
    indices = pd.Series(ds.Work)

    from sklearn.metrics.pairwise import cosine_similarity

    # generating the cosine similarity matrix
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    # function that takes in the work of service provider as input and returns the top 5 recommended service providers
    def recommendations(Work, cosine_sim=cosine_sim):
        recommended_city = []
        recommended_name = []
        recommended_work = []
        recommended_exp = []
        recommended_id = []
        recommend = []

        indices = WorkEngine.indices
        ds = WorkEngine.ds
        # getting the index of the service providers that matches the work
        idx = indices[indices == Work].index[0]

        # creating a Series with the similarity scores in descending order
        score_series = pd.Series(cosine_sim[idx]).sort_values(ascending=False)

        # getting the indexes of the 15 most similar service providers
        top_5_indexes = list(score_series.iloc[1:16].index)

        # populating the list with the name,city,work and experience of the best 5 matching service providers
        for i in top_5_indexes:
            recommended_city.append(list(ds['City_of_work'])[i])
            recommended_name.append(list(ds['Name'])[i])
            recommended_work.append(list(ds['Work'])[i])
            recommended_exp.append(list(ds['Years of Experience'])[i])
            recommended_id.append(list(ds['ID'])[i])

            recommend = recommended_id, recommended_name, recommended_city, recommended_work, recommended_exp

        return recommend
