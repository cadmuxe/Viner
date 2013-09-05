from flask import Flask, request, session, redirect, url_for
from flask import render_template as r_t
import pymongo, json, pickle, socket
from Item import Item as item
import dropbox
import AppKey

app = Flask(__name__)
app.secret_key = AppKey.secret_key
app_key = AppKey.app_key
app_secret = AppKey.app_secret
db = pymongo.Connection("localhost", 27017)["saver1024"]

@app.route("/", methods=['GET'])
def home():
    return r_t("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
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
            return redirect(url_for("setting"))
        else:
            return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return r_t("register.html")
    elif request.method == "POST":
        email = request.form["email"]
        passwd = request.form["pwd"]
        u = db["users"].find_one({"email":email})
        if not u:
            db["users"].save({"email":email, "passwd":passwd})
            session["email"] = email
            return redirect(url_for("setting"))
        return redirect(url_for("register"))

def get_dropbox_auth_flow(web_app_session):
    redirect_url = "http://localhost:5000/oauth"
    return dropbox.client.DropboxOAuth2Flow(app_key, app_secret,
        redirect_url, web_app_session, "dropbox-auth-csrf-token")

@app.route("/oauth", methods=["GET"])
def oauth():
    code = request.args.get("code")
    state = request.args.get("state")
    try:
        access_token, user_id, url_state = get_dropbox_auth_flow(session).finish(request.args)
        session["token"] = access_token
        user = db["users"].find_one({"email":session["email"]})
        user["token"] = access_token
        user["dropbox_id"] = user_id
        db["users"].save(user)
        return "Ok"
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
@app.route("/setting", methods=["GET"])
def setting():
    return r_t("oauth.html", href=get_dropbox_auth_flow(session).start())

@app.route("/api/saver", methods=["POST"])
def api_saver():
    if "email" not in session:
        return json.dumps({"status":"nologin"})
    else:
        info = request.form["data"]
        print info
        website = info["website"]
        title = info["title"]
        data = item(session["token"])
        for i in range(len(info["urls"])):
            data.push(("/" + website + "/" + title + "/" + str(i) + "." + info["urls"][i].split(".")[-1], \
                    info["urls"][i]))
        chunk = pickle.dumps(data)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 1024))
        s.sendall(chunk)
        s.close()
        
        return json.dumps({"status":"success"})

        


if __name__ == '__main__':
    app.run(debug=True)
