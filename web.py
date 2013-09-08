from flask import Flask, request, session, redirect, url_for, send_file, make_response
from flask import render_template as r_t
import pymongo, json, pickle, socket
from StringIO import StringIO
from Item import Item as item
import dropbox
import AppKey

app = Flask(__name__)
app.secret_key = AppKey.secret_key
app_key = AppKey.app_key
app_secret = AppKey.app_secret
db = pymongo.Connection("localhost", 27017)["saver1024"]
f = open("static/jquery-json.js","rb")
js_0 = f.read()
f.close()
f=open("static/saver.js","rb")
js_2 = f.read()
f.close()

@app.route("/", methods=['GET'])
def home():
    if "email" in session:
        return redirect(url_for("settings"))
    return r_t("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "email" in session:
        return redirect(url_for("settings"))
    if request.method == "GET":
        return r_t("login.html")
    elif request.method == "POST":
        email = request.form["email"]
        passwd = request.form["pwd"]
        u = db["users"].find_one({"email":email, "passwd":passwd})
        if u:
            session["email"] = email
            if u.has_key("token"):
                session["token"] = u["token"]
            return redirect(url_for("do_auth"))
        else:
            return redirect(url_for("login"))
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if "email" in session:
        return redirect(url_for("settings"))
    if request.method == "GET":
        return r_t("register.html")
    elif request.method == "POST":
        email = request.form["email"]
        passwd = request.form["pwd"]
        u = db["users"].find_one({"email":email})
        if not u:
            db["users"].save({"email":email, "passwd":passwd})
            session["email"] = email
            return redirect(url_for("do_auth"))
        return redirect(url_for("register"))

def get_dropbox_auth_flow(web_app_session):
    redirect_url = "http://localhost:5000/oauth"
    return dropbox.client.DropboxOAuth2Flow(app_key, app_secret,
        redirect_url, web_app_session, "dropbox-auth-csrf-token")

@app.route("/oauth", methods=["GET"])
def oauth():
    if "email" not in session:
        return redirect(url_for("login"))
    code = request.args.get("code")
    state = request.args.get("state")
    try:
        access_token, user_id, url_state = get_dropbox_auth_flow(session).finish(request.args)
        session["token"] = access_token
        user = db["users"].find_one({"email":session["email"]})
        user["token"] = access_token
        user["dropbox_id"] = user_id
        db["users"].save(user)
        return redirect(url_for("howto"))
    except dropbox.client.DropboxOAuth2Flow.BadRequestException, e:
        pass
        #http_status(400)
    except dropbox.client.DropboxOAuth2Flow.BadStateException, e:
        # Start the auth flow again.
        #redirect_to("/dropbox-auth-start")
        pass
    except dropbox.client.DropboxOAuth2Flow.CsrfException, e:
        pass
        #http_status(403)
    except dropbox.client.DropboxOAuth2Flow.NotApprovedException, e:
        pass
        #flash('Not approved?  Why not, bro?')
        #return redirect_to("/home")
    except dropbox.client.DropboxOAuth2Flow.ProviderException, e:
        #logger.log("Auth error: %s" % (e,))
        #http_status(403)
        pass
    return "No"
@app.route("/dropbox", methods=["GET"])
def do_auth():
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        u = db["users"].find_one({"email":session["email"]})
        if not u:
            return redirect(url_for("login"))
        if u.has_key("tolen"):
            session["token"] = u["token"]
            return redirect(url_for("howto"))
        return r_t("dropbox.html",  href=get_dropbox_auth_flow(session).start())

@app.route("/howto", methods=["GET"])
def howto():
    if "email" not in session:
        return redirect(url_for("login"))
    if "token" not in session:
        return redirect(url_for("do_auth"))
    return r_t("howto.html", 
        uid=str(db["users"].find_one({"email":session["email"]})["_id"]))

@app.route("/api/saver", methods=["POST"])
def api_saver():
    if "email" not in session:
        return json.dumps({"status":"nologin"})
    else:
        info = json.loads(request.form["data"])
        print info
        website = info["website"]
        title = info["title"]
        data = item(session["email"], session["token"])
        for i in range(len(info["urls"])):
            data.push(("/" + website + "/" + title + "/" + str(i) + "." + info["urls"][i].split(".")[-1], \
                    info["urls"][i]))
        chunk = pickle.dumps(data)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 1024))
        s.sendall(chunk)
        s.close()
        
        return json.dumps({"status":"success"})

@app.route("/settings", methods=["GET"])
def settings():
    if "email" not in session:
        return redirect(url_for("login"))
    if "token" not in session:
        return redirect(url_for("do_auth"))
    return r_t("settings.html")

def get_js_selector(uid, url):
    """
    get the js selector, now just for 1024
    """
    return db["settings"].find_one({"selector":"default"})["func"].encode("utf8")

@app.route("/j/<uid>", methods=["GET"])
def js_get(uid):
    if "email" not in session:
        response = make_response(r"document.location ='http://localhost:5000/login'")
        response.headers['content-type'] = "application/javascript"
        return response
    else:
        if "token" not in session:
            user = db["users"].find_one({"email":session["email"]})
            if user.has_key("token"):
                session["token"] = user["token"]
            else:
                response = make_response(r"document.location ='http://localhost:5000/dropbox'")
                response.headers['content-type'] = "application/javascript"
                return response

    url = request.args.get("u")
    timestamp = request.args.get("t")
    print "uid:%s, url:%s, time:%s" % (uid, url, timestamp)
    js_2t = js_2 % (timestamp,timestamp,timestamp)
    jsf = StringIO(js_0 + get_js_selector(uid, url) + js_2t.encode("utf8") )
    return send_file(jsf, "application/javascript")


if __name__ == '__main__':
    app.run(debug=True)
