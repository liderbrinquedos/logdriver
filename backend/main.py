from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import os
import csv
from io import StringIO, BytesIO
import openpyxl

from database import engine, get_db
from models import Base, Delivery, User
from schemas import (
    DeliveryResponse,
    DeliveryStatusUpdate,
    DeliveryStats,
    UserCreate,
    UserResponse,
    Token,
    LoginRequest,
)
from auth_utils import verify_password, get_password_hash, create_access_token, decode_token

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_token(token)
    if user_id is None:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return user

def require_admin_or_monitor(user: User = Depends(get_current_user)):
    if user.role not in ["admin", "monitor"]:
        raise HTTPException(status_code=403, detail="Acesso restrito")
    return user

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

# Configurar diretório de uploads
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="LiderLog API",
    description="API para controle de entregas - Motorista",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos (uploads)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Diretório do frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))

def save_upload_file(file: UploadFile, nf_number: str, suffix: str) -> str:
    timestamp = int(datetime.utcnow().timestamp())
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{timestamp}_NF{nf_number}_{suffix}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())
    return f"/uploads/{filename}"

def get_canhoto_url(path: Optional[str]) -> Optional[str]:
    if not path: return None
    if path.startswith("http"): return path
    return path


def format_delivery_response(d: Delivery) -> dict:
    return {
        "id": int(d.id) if d.id else 0,
        "nrunico": int(d.nrunico) if d.nrunico else 0,
        "nf_number": str(int(float(d.nf_number))) if d.nf_number else "",
        "client": d.client,
        "address": d.address,
        "city": d.city,
        "phone": d.phone,
        "value": d.value,
        "driver": d.driver,
        "company": d.company,
        "observations": d.observations,
        "canhoto_url": get_canhoto_url(d.canhoto_path),
        "status": d.status,
        "delivery_canhoto_url": get_canhoto_url(d.delivery_canhoto_path),
        "delivery_observations": d.delivery_observations,
        "delivered_at": d.delivered_at,
        "created_at": d.created_at,
        "user_id": d.user_id,
        "user_name": d.owner.username if d.owner else "Sistema",
    }


# ==================== AUTENTICAÇÃO ====================

@app.post("/api/auth/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username já está em uso")
    
    hashed = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed,
        role=user_data.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/auth/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(User).all()


@app.get("/api/drivers", response_model=List[UserResponse])
def list_drivers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Retorna apenas usuários com cargo 'motorista'
    return db.query(User).filter(User.role == "motorista").all()


@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    
    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# --- Estatísticas ---
@app.get("/api/stats", response_model=DeliveryStats)
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Delivery)
    if current_user.role not in ["admin", "monitor"]:
        name_filter = current_user.full_name if current_user.full_name else current_user.username
        query = query.filter(
            (Delivery.user_id == current_user.id) | 
            (Delivery.driver.ilike(f"%{current_user.username}%")) |
            (Delivery.driver.ilike(f"%{name_filter}%"))
        )
    total = query.count()
    entregues = query.filter(Delivery.status == "entregue").count()
    pendentes = query.filter(Delivery.status == "pendente").count()
    cancelados = query.filter(Delivery.status == "cancelado").count()
    return DeliveryStats(
        total=total, entregues=entregues, pendentes=pendentes, cancelados=cancelados
    )

# --- Listar entregas ---
@app.get("/api/deliveries", response_model=List[DeliveryResponse])
def list_deliveries(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query("pendente"),
    period: Optional[str] = Query("today"),
    order: Optional[str] = Query("desc"),
    driver: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Delivery)
    if current_user.role not in ["admin", "monitor"]:
        name_filter = current_user.full_name if current_user.full_name else current_user.username
        query = query.filter(
            (Delivery.user_id == current_user.id) | 
            (Delivery.driver.ilike(f"%{current_user.username}%")) |
            (Delivery.driver.ilike(f"%{name_filter}%"))
        )
    
    # Filtro por período
    if period == "today":
        today = datetime.utcnow().date()
        query = query.filter(func.date(Delivery.created_at) == today)
    elif period == "yesterday":
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        query = query.filter(func.date(Delivery.created_at) == yesterday)
    elif period == "week":
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(Delivery.created_at >= week_ago)
    
    # Filtros
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (Delivery.client.ilike(search_lower))
            | (Delivery.nf_number.ilike(search_lower))
            | (Delivery.address.ilike(search_lower))
        )
    if status and status != "all":
        query = query.filter(Delivery.status == status)
    if driver:
        query = query.filter(Delivery.driver.ilike(f"%{driver}%"))
    if company and company != "all":
        query = query.filter(Delivery.company == company)
    
    # Ordenação
    if order == "asc":
        query = query.order_by(Delivery.created_at.asc())
    elif order == "value_desc":
        query = query.order_by(Delivery.value.desc())
    elif order == "value_asc":
        query = query.order_by(Delivery.value.asc())
    else:
        query = query.order_by(Delivery.created_at.desc())
    
    deliveries = query.offset(skip).limit(limit).all()
    return [{
        "id": int(d.id) if d.id else 0,
        "nrunico": int(d.nrunico) if d.nrunico else 0,
        "nf_number": str(d.nf_number).split('.')[0] if d.nf_number else "",
        "client": d.client,
        "address": d.address,
        "city": d.city,
        "phone": d.phone,
        "value": d.value,
        "driver": d.driver,
        "company": d.company,
        "observations": d.observations,
        "canhoto_url": get_canhoto_url(d.canhoto_path),
        "status": d.status,
        "delivery_canhoto_url": get_canhoto_url(d.delivery_canhoto_path),
        "delivery_observations": d.delivery_observations,
        "delivered_at": d.delivered_at,
        "created_at": d.created_at,
        "user_id": d.user_id,
        "user_name": d.owner.username if d.owner else "Sistema",
    } for d in deliveries]

# --- Importar Excel ---
@app.post("/api/deliveries/import")
async def import_deliveries(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Use Excel (.xlsx)")

    try:
        contents = await file.read()
        wb = openpyxl.load_workbook(BytesIO(contents))
        sheet = wb.active
        
        deliveries_imported = 0
        
        def safe_int(v):
            if v is None: return 0
            try: return int(float(str(v)))
            except: return 0
        
        def safe_float(v):
            if v is None: return 0.0
            try: return float(str(v).replace(',', '.'))
            except: return 0.0
        
        def safe_phone(v):
            if v is None: return None
            p = str(v).strip().strip("'").replace(' ', '')
            return p if p and p != '0' else None
        
        # Pular cabeçalho
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[0]: continue 
            
            nrunico, nf, client, addr, city, phone, val, driver, comp, obs = row[:10]
            
            target_user_id = None
            if driver:
                d_clean = str(driver).strip().lower()
                d_user = db.query(User).filter(
                    (User.full_name.ilike(d_clean)) | (User.username.ilike(d_clean))
                ).first()
                if d_user: target_user_id = d_user.id

            # ADR-001: validar duplicata por nrunico (unico global)
            if nrunico:
                existing = db.query(Delivery).filter(
                    Delivery.nrunico == safe_int(nrunico)
                ).first()
                if existing:
                    print(f"Skipping NF {nf} - nrunico {nrunico} ja existe")
                    continue
            
            # Fallback: validar duplicata por NF + Empresa
            existing = db.query(Delivery).filter(
                Delivery.nf_number == str(safe_int(nf)),
                Delivery.company == (str(comp) if comp else "LDR")
            ).first()
            if existing:
                print(f"Skipping NF {nf} - ja existe para empresa {comp or 'LDR'}")
                continue

            db_delivery = Delivery(
                nrunico=safe_int(row[0]),
                nf_number=str(safe_int(nf)),
                client=str(client),
                address=str(addr),
                city=str(city) if city else None,
                phone=safe_phone(phone),
                value=safe_float(val),
                driver=str(driver) if driver else None,
                company=str(comp) if comp else "LDR",
                observations=str(obs) if obs else None,
                created_at=datetime.utcnow(),
                user_id=target_user_id,
            )
            db.add(db_delivery)
            deliveries_imported += 1
        
        db.commit()
        return {"detail": f"{deliveries_imported} entregas importadas com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

# --- Exportar CSV ---
@app.get("/api/deliveries/export")
def export_deliveries(
    current_user: User = Depends(require_admin_or_monitor),
    db: Session = Depends(get_db)
):
    query = db.query(Delivery)
    if current_user.role not in ["admin", "monitor"]:
        query = query.filter(Delivery.user_id == current_user.id)
    
    deliveries = query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "NF", "Cliente", "Endereco", "Status", "Motorista", "Valor", "Data Criacao", "Data Entrega"])
    
    for d in deliveries:
        writer.writerow([
            d.id, d.nf_number, d.client, d.address, d.status, 
            d.driver, d.value, d.created_at, d.delivered_at
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=entregas_liderlog.csv"}
    )

# --- Criar entrega ---
@app.post("/api/deliveries", response_model=DeliveryResponse, status_code=201)
async def create_delivery(
    nf_number: str = Form(...),
    client: str = Form(...),
    address: str = Form(...),
    city: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    value: Optional[float] = Form(None),
    driver: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    nrunico: Optional[int] = Form(None),
    observations: Optional[str] = Form(None),
    canhoto: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # ADR-001: validar duplicata por nrunico (unico global)
    if nrunico:
        existing = db.query(Delivery).filter(Delivery.nrunico == nrunico).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"nrunico {nrunico} ja existe")
    
    # Validar duplicata por NF + Empresa
    existing = db.query(Delivery).filter(
        Delivery.nf_number == nf_number,
        Delivery.company == company
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"NF {nf_number} ja existe para empresa {company}")
    
    canhoto_path = None
    if canhoto:
        canhoto_path = save_upload_file(canhoto, nf_number, "original")

    target_user_id = None 
    if driver:
        driver_clean = driver.strip().lower()
        driver_user = db.query(User).filter(
            (User.full_name.ilike(driver_clean)) | (User.username.ilike(driver_clean))
        ).first()
        if driver_user:
            target_user_id = driver_user.id

    db_delivery = Delivery(
        nf_number=nf_number,
        nrunico=nrunico,
        client=client,
        address=address,
        city=city,
        phone=phone,
        value=value,
        driver=driver,
        company=company,
        observations=observations,
        canhoto_path=canhoto_path,
        created_at=datetime.utcnow(),
        user_id=target_user_id,
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return format_delivery_response(db_delivery)

# --- Buscar entrega por ID ---
@app.get("/api/deliveries/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    if current_user.role != "admin" and delivery.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado a esta entrega")
    return format_delivery_response(delivery)

# --- Atualizar status ---
@app.patch("/api/deliveries/{delivery_id}/status", response_model=DeliveryResponse)
def update_status(
    delivery_id: int, status_update: DeliveryStatusUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    if current_user.role != "admin" and delivery.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado a esta entrega")

    if status_update.status == "pendente" and delivery.status == "entregue":
        delivery.delivery_canhoto_path = None
        delivery.delivery_observations = None
        delivery.delivered_at = None

    delivery.status = status_update.status
    db.commit()
    db.refresh(delivery)
    return format_delivery_response(delivery)

# --- Confirmar entrega ---
@app.patch("/api/deliveries/{delivery_id}/confirm", response_model=DeliveryResponse)
async def confirm_delivery(
    delivery_id: int,
    delivery_observations: Optional[str] = Form(None),
    delivery_canhoto: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    if current_user.role != "admin" and delivery.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado a esta entrega")

    delivery_canhoto_path = None
    if delivery_canhoto:
        delivery_canhoto_path = save_upload_file(
            delivery_canhoto, delivery.nf_number, "entrega"
        )
        delivery.delivery_canhoto_path = delivery_canhoto_path

    delivery.status = "entregue"
    delivery.delivery_observations = delivery_observations
    delivery.delivered_at = datetime.utcnow()

    db.commit()
    db.refresh(delivery)
    return format_delivery_response(delivery)

# --- Deletar entrega ---
@app.delete("/api/deliveries/{delivery_id}", status_code=204)
def delete_delivery(delivery_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    db.delete(delivery)
    db.commit()
    return None

# --- Health check ---
@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# === ROTA CATCH-ALL PARA FRONTEND (DEVE SER A ÚLTIMA) ===
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Se a rota começar com api/ e chegou aqui, é porque a rota não existe
    if full_path.startswith("api"):
        return JSONResponse(status_code=404, content={"detail": f"Rota de API '{full_path}' não encontrada"})
        
    if full_path == "" or full_path == "/":
        return FileResponse(os.path.join(FRONTEND_DIR, "LiderLog.html"))
    
    file_path = os.path.join(FRONTEND_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
        
    return FileResponse(os.path.join(FRONTEND_DIR, "LiderLog.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
