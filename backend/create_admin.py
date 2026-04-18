"""
Script para criar usuário admin inicial.
Execute com: python create_admin.py
"""
from database import SessionLocal, engine
from models import Base, User
from auth_utils import get_password_hash

def create_admin():
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print("Usuário admin já existe!")
            return
        
        admin = User(
            username="admin",
            full_name="Administrador",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("Usuário admin criado com sucesso!")
        print("Username: admin")
        print("Senha: admin123")
    except Exception as e:
        print(f"Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()