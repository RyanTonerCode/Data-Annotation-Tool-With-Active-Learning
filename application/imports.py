from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory, jsonify, send_file, after_this_request
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect, secure_filename
from flask.helpers import url_for
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
import random
import json
import math
import time
import os
import re

def apology(message, code, route="error"):
    #return render_template("error.html", message=message, code=code, route=route)
    print(message, code, route)
    return render_template(route + ".html", alert=message)