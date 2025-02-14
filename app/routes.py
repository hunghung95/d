from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, send_from_directory, send_file
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date
import zipfile
from io import BytesIO
from app import db
from app.models import File, FileRecipient, User, Group, user_groups
from app.forms import FileUploadForm, GroupForm

bp = Blueprint('routes', __name__)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = FileUploadForm()

    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Kiểm tra và tạo thư mục nếu chưa tồn tại
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])

        form.file.data.save(file_path)
        file = File(name=filename, file_path=filename, uploaded_by=current_user, urgency=form.urgency.data)
        db.session.add(file)
        db.session.commit()

        # Add recipients from selected groups
        selected_users = set()
        if form.groups.data:
            group_users = User.query.join(user_groups).filter(user_groups.c.group_id.in_(form.groups.data)).all()
            selected_users.update(group_users)

        # Add additional recipients
        if form.additional_recipients.data:
            additional_users = User.query.filter(User.id.in_(form.additional_recipients.data)).all()
            selected_users.update(additional_users)

        for user in selected_users:
            file_recipient = FileRecipient(file_id=file.id, recipient_id=user.id)
            db.session.add(file_recipient)

        db.session.commit()
        flash('Tài liệu đã được gửi thành công!')
        return redirect(url_for('routes.file_list'))
    return render_template('upload_file.html', form=form)

@bp.route('/group_users')
@login_required
def group_users():
    group_ids = request.args.get('group_ids')
    if group_ids:
        group_ids = [int(id) for id in group_ids.split(',')]
        users = User.query.join(user_groups).filter(user_groups.c.group_id.in_(group_ids), User.is_admin == False).all()
        users_data = [{'id': user.id, 'username': user.username} for user in users]
        return jsonify(users_data)
    return jsonify([])

@bp.route('/search_users')
@login_required
def search_users():
    query = request.args.get('query')
    if query:
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
        users_data = [{'id': user.id, 'username': user.username} for user in users]
        return jsonify(users_data)
    return jsonify([])

@bp.route('/')
@login_required
def file_list():
    files = File.query.filter_by(uploaded_by=current_user).all()
    return render_template('file_list.html', files=files)

@bp.route('/received')
@login_required
def received_files():
    files = FileRecipient.query.filter_by(recipient_id=current_user.id).join(File).order_by(File.uploaded_at.desc()).all()
    unread_files_count = FileRecipient.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    today_files = [file for file in files if file.file.uploaded_at.date() == date.today()]
    unread_files = [file for file in files if not file.is_read]
    return render_template('received_files.html', files=files, today_files=len(today_files),
                           unread_files=len(unread_files), unread_files_count=unread_files_count)

@bp.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    recipient = FileRecipient.query.filter_by(file_id=file_id, recipient_id=current_user.id).first_or_404()
    recipient.is_read = True
    recipient.read_at = datetime.utcnow()
    db.session.commit()
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], file.file_path, as_attachment=True)

@bp.route('/download_all')
@login_required
def download_all_files():
    files = FileRecipient.query.filter_by(recipient_id=current_user.id, is_read=False).all()
    for recipient in files:
        recipient.is_read = True
        recipient.read_at = datetime.utcnow()
    db.session.commit()

    # Tạo file zip với tên có định dạng Tailieu_giờ-ngày-tháng-năm
    zip_filename = datetime.now().strftime("Tailieu_%H-%d-%m-%Y.zip")
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for recipient in files:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipient.file.file_path)
            if os.path.exists(file_path):
                zf.write(file_path, os.path.basename(file_path))

    memory_file.seek(0)
    return send_file(memory_file, download_name=zip_filename, as_attachment=True)

@bp.route('/admin/groups', methods=['GET', 'POST'])
@login_required
def manage_groups():
    form = GroupForm()
    groups = Group.query.all()
    if form.validate_on_submit():
        group = Group(name=form.name.data)
        for user_id in form.users.data:
            user = User.query.get(user_id)
            if user:
                group.users.append(user)
        db.session.add(group)
        db.session.commit()
        flash('Nhóm đã được tạo thành công!')
        return redirect(url_for('routes.manage_groups'))
    return render_template('manage_groups.html', form=form, groups=groups)