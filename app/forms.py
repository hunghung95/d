from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import User, Group

class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember_me = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

class RegistrationForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    password2 = PasswordField(
        'Nhập lại mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.')

class FileUploadForm(FlaskForm):
    file_type = SelectField('Loại tài liệu', choices=[('Thường', 'Thường'), ('Mật', 'Mật')], validators=[DataRequired()])
    file = FileField('Chọn tệp', validators=[DataRequired()])
    urgency = SelectField('Độ khẩn', choices=[('Thường', 'Thường'), ('Hỏa tốc', 'Hỏa tốc')], default='Thường', validators=[DataRequired()])
    groups = SelectMultipleField('Chọn nhóm', coerce=int)
    additional_recipients = SelectMultipleField('Người nhận bổ sung', coerce=int)
    submit = SubmitField('Gửi tài liệu')

    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.groups.choices = [(group.id, group.name) for group in Group.query.all()]
        self.additional_recipients.choices = [(user.id, user.username) for user in User.query.all()]

class GroupForm(FlaskForm):
    name = StringField('Tên nhóm', validators=[DataRequired()])
    users = SelectMultipleField('Người dùng', coerce=int)
    submit = SubmitField('Lưu nhóm')

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.users.choices = [(user.id, user.username) for user in User.query.all()]

class AddUserForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    password2 = PasswordField(
        'Nhập lại mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Thêm người dùng')

class UploadUsersForm(FlaskForm):
    file = FileField('Chọn tệp Excel', validators=[DataRequired()])
    submit = SubmitField('Tải lên')