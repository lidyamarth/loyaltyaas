import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class TipeMutasi(str, Enum):
    EARNED = "EARNED"
    REDEEMED = "REDEEMED"
    EXPIRED = "EXPIRED"

class TipeAturan(str, Enum):
    PER_RUPIAH = "PER_RUPIAH"
    PER_PRODUK = "PER_PRODUK"
    PER_KUNJUNGAN = "PER_KUNJUNGAN"

class Poin(BaseModel):
    jumlah: int = Field(..., ge=0)

class Tier(BaseModel):
    nama: str
    level: int

class TransaksiDTO(BaseModel):
    transaksiId: str
    totalBelanja: int

class AturanDTO(BaseModel):
    tipeAturan: TipeAturan
    nilaiKelipatan: Optional[int] = None
    poinDiberikan: int
    idProduk: Optional[str] = None

class HadiahDTO(BaseModel):
    hadiahId: str
    hargaPoin: int

class RiwayatPoin(BaseModel):
    riwayatId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tipeMutasi: TipeMutasi
    jumlah: int
    tanggal: datetime = Field(default_factory=datetime.now)

class Penukaran(BaseModel):
    penukaranId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hadiahId: str
    poinDitukar: int
    tanggal: datetime = Field(default_factory=datetime.now)

class Membership:
    def __init__(self, membershipId: str, pelangganId: str, merchantId: str):
        self.membershipId = membershipId
        self.pelangganId = pelangganId
        self.merchantId = merchantId
        self.poinTersedia = 0
        self.currentTier = Tier(nama="Bronze", level = 1)
        self.riwayatPoin: List[RiwayatPoin] = []
        self.riwayatPenukaran: List[Penukaran] = []

    def tambah_poin(self, transaksi:TransaksiDTO, aturan: AturanDTO):
        poin_didapat = 0

        if aturan.tipeAturan == TipeAturan.PER_RUPIAH:
            if aturan.nilaiKelipatan and aturan.nilaiKelipatan > 0:
                poin_didapat = (transaksi.totalBelanja // aturan.nilaiKelipatan) * aturan.poinDiberikan
        elif aturan.tipeAturan == TipeAturan.PER_KUNJUNGAN:
            poin_didapat = aturan.poinDiberikan
        
        if poin_didapat > 0:
            self.poinTersedia += poin_didapat
            riwayat_baru = RiwayatPoin(tipeMutasi=TipeMutasi.EARNED, jumlah=poin_didapat)
            self.riwayatPoin.append(riwayat_baru)
            self.evaluasi_tier()
    
    def tukar_poin(self, hadiah: HadiahDTO):
        if self.poinTersedia < hadiah.hargaPoin:
            raise ValueError("Point tidak mencukupi.")
        
        self.poinTersedia -= hadiah.hargaPoin

        penukaran_baru = Penukaran(hadiahId=hadiah.hadiahId, poinDitukar=hadiah.hargaPoin)
        self.riwayatPenukaran.append(penukaran_baru)

        riwayat_baru = RiwayatPoin(tipeMutasi=TipeMutasi.REDEEMED, jumlah=hadiah.hargaPoin)
        self.riwayatPoin.append(riwayat_baru)

    #helper
    def evaluasi_tier(self):
        if self.poinTersedia >= 1000:
            self.currentTier = Tier(nama="Gold", level=3)
        elif self.poinTersedia >= 500:
            self.currentTier = Tier(nama="Silver", level=2)