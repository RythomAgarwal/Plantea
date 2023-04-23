import functools
from urllib.parse import quote_plus, urlencode
from pymongo import MongoClient
from flask import redirect, render_template, session, url_for, request, session, abort, flash
import urllib
import datetime
import os
from flask.blueprints import Blueprint
from hashlib import md5

pages = Blueprint("Hive", __name__, template_folder="templates", static_folder="static")

client = MongoClient(
    "mongodb+srv://<YOUR_MONGO_DB_USERNAME>:" + urllib.parse.quote("<YOUR_PASSWORD>") + "@greenhive.qvwxgh4.mongodb.net/test")
pages.db = client.GreenHive
SESSION_TYPE = 'mongodb'


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        email = session.get("email")
        if not email:
            return redirect(url_for("Hive.login"))
        return route

    return route_wrapper


@pages.route('/logout')
def hello_world():  # put application's code here
    session.clear()
    return render_template("home.html", email=session.get("email"))


@pages.route('/protected')
@login_required
def protected():
    return render_template("protected.html")


@pages.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        if pages.db.account.find_one({"email": email}):
            flash("Account Already Exists!")
        else:
            dig = md5(email.lower().encode('utf-8')).hexdigest()
            image_link = 'https://www.gravatar.com/avatar/' + dig + "?d=identicon"
            pages.db.account.insert_one(
                {"email": email, "password": password, "username": username, "name": name, "pfp_link": image_link})
            return redirect(url_for("Hive.login"))
    return render_template("register.html")


@pages.route('/login', methods=["GET", "POST"])
def login():
    email = ""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_exists = pages.db.account.find_one({'email': email})
        if user_exists:
            pass_in_db = pages.db.account.find_one({"email": email})['password']
            if password == pass_in_db:
                session["email"] = email
                print("Add")
                return redirect(url_for("Hive.index"))
            else:
                flash("Wrong Email or Password")
        else:
            flash("Wrong Email or Password")
    return render_template("login.html", email=email)


@pages.route('/', methods=['POST', "GET"])
def index():
    email = session.get("email")

    if not email:
        return redirect(url_for("Hive.login"))
    else:
        user_naam = pages.db.account.find_one({"email": email})['username']
        name_pro = pages.db.account.find_one({"email": email})['name']
        pfp_pro = pages.db.account.find_one({"email": email})['pfp_link']
        if request.method == "POST":
            post_text = request.form.get("compose-tweet-body")
            format_date = datetime.datetime.today().strftime("%b %d")
            username = pages.db.account.find_one({"email": email})['username']
            name = pages.db.account.find_one({"email": email})['name']
            pfp = pages.db.account.find_one({"email": email})['pfp_link']
            n = 5
            word_list = post_text.split()
            new_words = ""

            for i, word in enumerate(word_list):
                if i % n == 0 and i > 0:
                    new_words += "\n"
                new_words += word + " "
            pages.db.tweet.insert_one(
                {"content": new_words, "date": format_date, "email": email, "username": username, "name": name,
                 "pfp_link": pfp})
    tweets = [
        (
            data["content"],
            data["date"],
            data["username"],
            data["name"],
            data["pfp_link"]
        )
        for data in pages.db.tweet.find({})
    ]
    return render_template("index.html", tweet=reversed(tweets), oneusername=user_naam, onename=name_pro,
                           onepfp=pfp_pro)


@pages.route('/event')
def event():
    email = session.get('email')
    if not email:
        return redirect(url_for("Hive.login"))
    user_naam = pages.db.account.find_one({"email": email})['username']
    name_pro = pages.db.account.find_one({"email": email})['name']
    pfp_pro = pages.db.account.find_one({"email": email})['pfp_link']
    events = [
        (data["name"],
         data["email"],
         data["phone"],
         data["dob"],
         data["gender"],
         data["level"],
         data["address1"],
         data["address2"],
         data["country"],
         data["city"],
         data["region"],
         data["postalcode"],
         data["format_date"],
         data["description"],
         data["thumbnail"],
         data['title'],
         data['start_date'],
         data['start_time'],
         data['end_date'],
         data['end_time'],
         data["date"],
         data["month"]
         )
        for data in pages.db.event.find({})
    ]
    return render_template("event.html", event=events, oneusername=user_naam, onename=name_pro, onepfp=pfp_pro)


def date_formatter(date):
    date = date.split("-")
    date.pop(0)
    month = date[0]
    date = date[1]

    if month == "01":
        month = "Jan"
    elif month == "02":
        month = "Feb"
    elif month == "03":
        month = "Mar"
    elif month == "04":
        month = "Apr"
    elif month == "05":
        month = "May"
    elif month == "06":
        month = "Jun"
    elif month == "07":
        month = "July"
    elif month == "08":
        month = "Aug"
    elif month == "09":
        month = "Sept"
    elif month == "10":
        month = "Oct"
    elif month == "11":
        month = "Nov"
    elif month == "12":
        month = "Dec"

    if "0" in date:
        date = date.replace("0", "")
    else:
        date = date

    new_date = month + " " + date
    new_date = [new_date, date, month]
    return new_date


@pages.route('/event/create', methods=["POST", "GET"])
def event_create():
    email = session.get("email")
    if not email:
        return redirect(url_for("Hive.login"))
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        level = request.form.get("level")
        address1 = request.form.get("address1")
        address2 = request.form.get("address2")
        country = request.form.get("country")
        city = request.form.get("city")
        region = request.form.get("region")
        postalcode = request.form.get("postalcode")
        format_current_date = datetime.datetime.today().strftime("%b %d")
        title = request.form.get("title")
        description = request.form.get("description")
        thumbnail = request.form.get("thumbnail")
        start_date = request.form.get("start_date")
        start_time = request.form.get("start_time")
        end_date = request.form.get("end_date")
        end_time = request.form.get("end_time")

        date_data = date_formatter(start_date)
        date = date_data[1]
        month = date_data[2]
        pages.db.event.insert_one({
            "name": name,
            "email": email,
            "phone": phone,
            "dob": dob,
            "gender": gender,
            "level": level,
            "address1": address1,
            "address2": address2,
            "country": country,
            "city": city,
            "region": region,
            "postalcode": postalcode,
            "format_date": format_current_date,
            "description": description,
            "thumbnail": thumbnail,
            "title": title,
            "start_date": start_date,
            "start_time": start_time,
            "end_date": end_date,
            "end_time": end_time,
            "date": date,
            "month": month

        })
        return redirect(url_for("Hive.event"))
    events = [
        (data["name"],
         data["email"],
         data["phone"],
         data["dob"],
         data["gender"],
         data["level"],
         data["address1"],
         data["address2"],
         data["country"],
         data["city"],
         data["region"],
         data["postalcode"],
         data["format_date"],
         data["description"],
         data["thumbnail"],
         data['title'],
         data['start_date'],
         data['start_time'],
         data['end_date'],
         data['end_time']
         )
        for data in pages.db.event.find({})
    ]
    return render_template("event_create.html")


@pages.route("/event/detail")
def detail():
    title = request.args.get("title")
    description = pages.db.event.find_one({"title": title})['description']
    level = pages.db.event.find_one({"title": title})['level']
    country = pages.db.event.find_one({"title": title})['country']
    city = pages.db.event.find_one({"title": title})['city']
    add1 = pages.db.event.find_one({"title": title})['address1']
    add2 = pages.db.event.find_one({"title": title})['address2']
    region = pages.db.event.find_one({"title": title})['region']
    postal_code = pages.db.event.find_one({"title": title})['postalcode']
    startdate = pages.db.event.find_one({"title": title})['start_date']
    starttime = pages.db.event.find_one({"title": title})['start_time']
    enddate = pages.db.event.find_one({"title": title})['end_date']
    endtime = pages.db.event.find_one({"title": title})['end_time']
    thumb = pages.db.event.find_one({"title": title})['thumbnail']

    owner = pages.db.event.find_one({"title": title})['name']
    email = pages.db.event.find_one({"title": title})['email']
    # number = pages.db.event.find_one({"title": title})['number']

    return render_template("event_detail.html", title=title, description=description, level=level, country=country,
                           city=city, add1=add1, add2=add2, region=region, postal_code=postal_code, startdate=startdate,
                           starttime=starttime, enddate=enddate, endtime=endtime, thumb=thumb, owner=owner, mail=email)


@pages.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")