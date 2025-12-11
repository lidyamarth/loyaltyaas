from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import uuid
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from .domain import Membership, TransaksiDTO, AturanDTO, HadiahDTO

app = FastAPI(title="Loyalty Core API",
              description="API Backend untuk sistem loyalitas UMKM dengan fitur poin dinamis.",
              version="1.0.0")

SECRET_KEY = "gak_sabar_kelar_semua_tugas_ini" # buat tubes jadi di taro disini
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 40

users_db = {
    "admin": "rahasia123",
    "lidya": "joutier",  
    "kasir": "kasir123"
}

class Token(BaseModel):
    access_token: str
    token_type: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    """Membuat JWT Token dengan waktu kadaluarsa"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dipasang di endpoint untuk cek apakah user bawa token asli"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username


membership_db = {}

class CreateMembershipRequest(BaseModel):
    pelangganId: str
    merchantId: str

class EarnPointsRequest(BaseModel):
    transaksi: TransaksiDTO
    aturan: AturanDTO

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    password_di_db = users_db.get(form_data.username)
    
    if not password_di_db or password_di_db != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/memberships/", status_code=201)
def create_membership(request: CreateMembershipRequest, current_user: str = Depends(get_current_user)):
    new_id = str(uuid.uuid4())
    membership = Membership(membershipId=new_id, pelangganId=request.pelangganId, merchantId=request.merchantId)
    membership_db[new_id] = membership
    return {"message": "Membership created", "membershipId":new_id, "createdBy": current_user}

@app.get("/memberships/{membership_id}")
def get_membership(membership_id: str, current_user: str = Depends(get_current_user)):
    if membership_id not in membership_db:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    member = membership_db[membership_id]
    return {
        "membershipId": member.membershipId,
        "pelangganId": member.pelangganId,
        "poinTersedia": member.poinTersedia,
        "tier": member.currentTier,
        "riwayat": member.riwayatPoin
    }

@app.post("/memberships/{membership_id}/earn")
def earn_points(membership_id: str, request: EarnPointsRequest, current_user: str = Depends(get_current_user)):
    if membership_id not in membership_db:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    member = membership_db[membership_id]
    member.tambah_poin(request.transaksi, request.aturan)
    return{
        "message": "Poin berhasil ditambahkan",
        "totalPoinSekarang": member.poinTersedia,
        "tierSekarang": member.currentTier
    }

@app.post("/memberships/{membership_id}/redeem")
def redeem_points(membership_id: str, hadiah: HadiahDTO, current_user: str = Depends(get_current_user)):
    if membership_id not in membership_db:
        raise HTTPException(status_code=404, detail="Membership not found")

    member = membership_db[membership_id]   
    try:
        member.tukar_poin(hadiah)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "message": "Penukaran berhasil",
        "sisaPoin": member.poinTersedia
    }