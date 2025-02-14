from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

username = "admin"

# Kiểm tra xem người dùng admin có tồn tại không
admin_user = User.query.filter_by(username=username).first()

if admin_user:
    db.session.delete(admin_user)
    db.session.commit()
    print(f"Tài khoản admin '{username}' đã được xóa.")
else:
    print(f"Tài khoản admin '{username}' không tồn tại.")