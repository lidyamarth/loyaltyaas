from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from .domain import Membership, TransaksiDTO, AturanDTO, HadiahDTO

app = FastAPI(title="Loyalty Core API")
membership_db = {}

class CreateMembershipRequest(BaseModel):
    pelangganId: str
    merchantId: str

class EarnPointsRequest(BaseModel):
    transaksi: TransaksiDTO
    aturan: AturanDTO

@app.post("/memberships/", status_code=201)
def create_membership(request: CreateMembershipRequest):
    new_id = str(uuid.uuid4())
    membership = Membership(membershipId=new_id, pelangganId=request.pelangganId, merchantId=request.merchantId)
    membership_db[new_id] = membership
    return {"message": "Membership created", "membershipId":new_id}

@app.get("/memberships/{membership_id}")
def get_membership(membership_id: str):
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
def earn_points(membership_id: str, request: EarnPointsRequest):
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
def redeem_points(membership_id: str, hadiah: HadiahDTO):
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