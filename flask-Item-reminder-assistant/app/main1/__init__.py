from flask import Blueprint

main = Blueprint('main', __name__)

from . import views,log,object,importdata,files,sync