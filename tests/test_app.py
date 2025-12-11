import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.domain import Membership, TransaksiDTO, AturanDTO, TipeAturan, HadiahDTO

client = TestClient(app)

def test_domain_membership_logic():
    member = Membership("123", "CUST-1", "MERCH-1")
    
    # 1. Test Inisialisasi
    assert member.poinTersedia == 0
    assert member.currentTier.nama == "Bronze"

    # 2. Test Tambah Poin (PER_RUPIAH)
    trx = TransaksiDTO(transaksiId="T1", totalBelanja=50000)
    rule = AturanDTO(tipeAturan=TipeAturan.PER_RUPIAH, nilaiKelipatan=10000, poinDiberikan=10)
    member.tambah_poin(trx, rule)
    assert member.poinTersedia == 50 # 5 * 10
    
    # 3. Test Tambah Poin (PER_KUNJUNGAN)
    rule_kunjungan = AturanDTO(tipeAturan=TipeAturan.PER_KUNJUNGAN, poinDiberikan=5)
    member.tambah_poin(trx, rule_kunjungan)
    assert member.poinTersedia == 55 # 50 + 5

    # 4. Test Tukar Poin (Berhasil)
    hadiah = HadiahDTO(hadiahId="H1", hargaPoin=20)
    member.tukar_poin(hadiah)
    assert member.poinTersedia == 35 # 55 - 20

    # 5. Test Tukar Poin (gagal - saldo kurang)
    hadiah_mahal = HadiahDTO(hadiahId="H2", hargaPoin=1000)
    with pytest.raises(ValueError):
        member.tukar_poin(hadiah_mahal)

    # 6. Test Tier Upgrade (Edge Case)
    # Tambah poin biar sampe 500 (Silver)
    trx_big = TransaksiDTO(transaksiId="T2", totalBelanja=5000000) # 5jt / 10rb * 10 = 5000 poin
    member.tambah_poin(trx_big, rule)
    assert member.currentTier.nama == "Gold" 

# helper: login dan dapatkan token
def get_auth_headers():
    response = client.post(
        "/token",
        data={"username": "admin", "password": "rahasia123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_api_flow_complete():
    headers = get_auth_headers()
    
    payload_create = {"pelangganId": "JOUTIER-01", "merchantId": "KOPI-A"}
    res = client.post("/memberships/", json=payload_create, headers=headers)
    assert res.status_code == 201
    membership_id = res.json()["membershipId"]
    
    payload_earn = {
        "transaksi": {"transaksiId": "TRX-1", "totalBelanja": 20000},
        "aturan": {"tipeAturan": "PER_RUPIAH", "nilaiKelipatan": 10000, "poinDiberikan": 5}
    }
    res = client.post(f"/memberships/{membership_id}/earn", json=payload_earn, headers=headers)
    assert res.status_code == 200
    assert res.json()["totalPoinSekarang"] == 10 # 2 * 5
    
    res = client.get(f"/memberships/{membership_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["poinTersedia"] == 10
    
    payload_redeem = {"hadiahId": "GIFT-1", "hargaPoin": 5}
    res = client.post(f"/memberships/{membership_id}/redeem", json=payload_redeem, headers=headers)
    assert res.status_code == 200
    assert res.json()["sisaPoin"] == 5

    payload_redeem_fail = {"hadiahId": "GIFT-MAHAL", "hargaPoin": 100}
    res = client.post(f"/memberships/{membership_id}/redeem", json=payload_redeem_fail, headers=headers)
    assert res.status_code == 400
    assert res.json()["detail"] == "Point tidak mencukupi."

def test_login_failed():
    res = client.post("/token", data={"username": "admin", "password": "salah"})
    assert res.status_code == 401

def test_access_without_token():
    res = client.post("/memberships/", json={"pelangganId": "A", "merchantId": "B"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"

def test_not_found():
    headers = get_auth_headers()
    
    res = client.get("/memberships/ngawur-id", headers=headers)
    assert res.status_code == 404
    
    payload_dummy_earn = {
        "transaksi": {"transaksiId": "DUMMY", "totalBelanja": 0},
        "aturan": {"tipeAturan": "PER_RUPIAH", "nilaiKelipatan": 1, "poinDiberikan": 1}
    }
    res = client.post("/memberships/ngawur-id/earn", json=payload_dummy_earn, headers=headers)
    assert res.status_code == 404 

    payload_dummy_redeem = {"hadiahId": "A", "hargaPoin": 1}
    res = client.post("/memberships/ngawur-id/redeem", json=payload_dummy_redeem, headers=headers)
    assert res.status_code == 404