from application.imports import Flask, mkdtemp, os, HTTPException, InternalServerError, default_exceptions, apology, Session

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["SECRET_KEY"] = os.urandom(24) #make a new secret key every time the server starts

Session(app)

from application.routes import index #connect the route files, each having code for a specific range of pages

def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

