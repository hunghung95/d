from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
import pandas as pd
from app import db
from app.models import User, Group
from app.forms import GroupForm, AddUserForm, UploadUsersForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('routes.file_list'))
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/groups')
@login_required
def list_groups():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('routes.file_list'))
    groups = Group.query.all()
    return render_template('admin/list_groups.html', groups=groups)

@admin_bp.route('/admin/groups/add', methods=['GET', 'POST'])
@login_required
def add_group():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('routes.file_list'))
    form = GroupForm()
    form.users.choices = [(user.id, user.username) for user in User.query.all()]
    if form.validate_on_submit():
        group = Group(name=form.name.data)
        db.session.add(group)
        db.session.commit()
        for user_id in form.users.data:
            user = User.query.get(user_id)
            group.users.append(user)
        db.session.commit()
        flash('Nhóm đã được thêm thành công.')
        return redirect(url_for('admin.list_groups'))
    return render_template('admin/add_group.html', form=form)

@admin_bp.route('/admin/groups/edit/<int:group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('routes.file_list'))
    group = Group.query.get_or_404(group_id)
    form = GroupForm(obj=group)
    form.users.choices = [(user.id, user.username) for user in User.query.all()]
    if form.validate_on_submit():
        group.name = form.name.data
        group.users = []
        for user_id in form.users.data:
            user = User.query.get(user_id)
            group.users.append(user)
        db.session.commit()
        flash('Nhóm đã được cập nhật thành công.')
        return redirect(url_for('admin.list_groups'))
    return render_template('admin/edit_group.html', form=form)

@admin_bp.route('/admin/groups/delete/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('routes.file_list'))
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash('Nhóm đã được xóa thành công.')
    return redirect(url_for('admin.list_groups'))

@admin_bp.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('routes.file_list'))
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Người dùng đã được thêm thành công.')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_user.html', form=form)

@admin_bp.route('/admin/upload_users', methods=['GET', 'POST'])
@login_required
def upload_users():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('routes.file_list'))
    form = UploadUsersForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Đọc file Excel và thêm người dùng
        df = pd.read_excel(filepath)
        for index, row in df.iterrows():
            user = User(username=row['username'])
            user.set_password(row['password'])
            db.session.add(user)
        db.session.commit()
        flash('Người dùng đã được tải lên thành công.')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/upload_users.html', form=form)