from app import app, db, login
from app.forms import ProfileSettingsForm, ProfilePictureForm
from app.models import User, Search
from app.custom import require_role
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('/dashboard/dashboard.html')

@app.route('/dashboard/profile_settings', methods=['GET'])
@login_required
def profile_settings():
    psform = ProfileSettingsForm()
    ppform = ProfilePictureForm()
    return render_template('/dashboard/profile_settings.html', psform=psform, ppform=ppform)

@app.route('/dashboard/profile_settings/submit', methods=['POST'])
@login_required
def profile_settings_submit():
    form = ProfileSettingsForm()
    if form.validate_on_submit():
        data = {
            'show_email' : form.show_email.data or None,
            'profile_picture_file' : request.files
        }
        return jsonify(data=data)
    return '{}'

@app.route('/dashboard/constants')
@login_required
@require_role(roles=['Admin'])
def constants():
    return render_template('/dashboard/constants.html')

@app.route('/dashboard/rbac')
@login_required
def rbac():
    return render_template('/dashboard/rbac.html')