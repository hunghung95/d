from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

username = "admin"
password = "adminpassword"

# Kiểm tra xem người dùng admin đã tồn tại chưa
admin_user = User.query.filter_by(username=username).first()

if not admin_user:
    # Tạo tài khoản admin mới
    admin_user = User(username=username, is_admin=True)
    admin_user.set_password(password)
    db.session.add(admin_user)
    db.session.commit()
    print(f"Tài khoản admin '{username}' đã được tạo.")
else:
    # Cập nhật tài khoản admin hiện tại
    admin_user.is_admin = True
    admin_user.set_password(password)
    db.session.commit()
    print(f"Tài khoản admin '{username}' đã được cập nhật.")