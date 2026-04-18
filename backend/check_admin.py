from database import SessionLocal
from models import User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()
if user:
    print(f"Usuário encontrado: {user.username}")
    print(f"Role: {user.role}")
    print(f"Ativo: {user.is_active}")
    print(f"Hash: {user.hashed_password}")
else:
    print("Usuário 'admin' NÃO encontrado no banco de dados.")
db.close()
