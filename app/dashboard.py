from app import app, db, login
from app.models import User, Search
from app.custom import require_role
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('/dashboard/dashboard.html')

@app.route('/dashboard/profile_settings')
@login_required
def profile_settings():
    return render_template('/dashboard/profile_settings.html')

@app.route('/dashboard/constants')
@login_required
@require_role(roles=['Admin'])
def constants():
    return render_template('/dashboard/constants.html')

@app.route('/dashboard/rbac')
@login_required
def rbac():
    return render_template('/dashboard/rbac.html')