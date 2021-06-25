from flask import render_template, g, flash
from wuxia import app
from mysql.connector import Error as SQLError


@app.errorhandler(500)
def handle_internal_server_error(e):
    error = ''
    if isinstance(e, SQLError):
        error = 'Database error. Please try again or contact the administrator.'
    else:
        error = 'Application error. Please try again or contact the administrator.'
    
    flash(error)
    return render_template('base.html')