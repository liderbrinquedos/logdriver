from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# === SCHEMAS DE AUTENTICAÇÃO ===

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: str = Field(default="motorista", pattern="^(admin|motorista)$")


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Schema para login
class LoginRequest(BaseModel):
    username: str
    password: str


# === SCHEMAS DE ENTREGA ===
class DeliveryCreate(BaseModel):
    nf_number: str = Field(..., min_length=1)
    client: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    city: Optional[str] = None
    phone: Optional[str] = None
    value: Optional[float] = None
    driver: Optional[str] = None
    company: Optional[str] = None
    observations: Optional[str] = None


# Schema para atualização de status
class DeliveryStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pendente|entregue|cancelado)$")


# Schema para confirmação de entrega
class DeliveryConfirm(BaseModel):
    delivery_observations: Optional[str] = None


# Schema de resposta
class DeliveryResponse(BaseModel):
    id: int
    nf_number: str
    client: str
    address: str
    city: Optional[str]
    phone: Optional[str]
    value: Optional[float]
    driver: Optional[str]
    company: Optional[str]
    observations: Optional[str]
    canhoto_url: Optional[str] = None
    status: str
    delivery_canhoto_url: Optional[str] = None
    delivery_observations: Optional[str]
    delivered_at: Optional[datetime]
    created_at: datetime
    user_id: Optional[int] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


# Schema para estatísticas
class DeliveryStats(BaseModel):
    total: int
    entregues: int
    pendentes: int
    cancelados: int
