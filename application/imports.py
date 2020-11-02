from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory, jsonify
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
import random
import json
import math
import os
import re

def apology(message, code, route="error"):
    #return render_template("error.html", message=message, code=code, route=route)
    print(message, code, route)
    return render_template(route + ".html", alert=message)