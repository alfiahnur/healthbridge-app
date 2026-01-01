from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests 
import json

# ==========================================
# 1. KONFIGURASI GEMINI (HYBRID)
# ==========================================
# Pastikan Kunci ini benar
RAW_API_KEY = "yyyy" 
GOOGLE_API_KEY = RAW_API_KEY.strip()

# Kita gunakan model 'gemini-pro' (paling pintar)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"

# ==========================================
# 2. DATABASE SETUP
# ==========================================
DATABASE_URL = "sqlite:///./healthbridge.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PatientRecord(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    symptoms = Column(Text)
    diagnosis = Column(String)
    advice = Column(Text)

Base.metadata.create_all(bind=engine)

# ==========================================
# 3. SETUP APLIKASI
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SymptomCheck(BaseModel):
    patient_name: str
    symptoms: str

@app.get("/")
def read_root():
    return {"message": "HealthBridge AI is Running!"}

# ==========================================
# 4. API DIAGNOSA (UPGRADED BRAIN)
# ==========================================
@app.post("/api/diagnose")
def diagnose_symptoms(data: SymptomCheck, db: Session = Depends(get_db)):
    
    diagnosis_clean = "Analisa Umum"
    advice_clean = "Istirahat yang cukup dan perbanyak minum air putih."

    # --- OTAK 1: REAL AI (GEMINI) ---
    try:
        headers = {"Content-Type": "application/json"}
        # Prompt dibuat lebih tegas agar Gemini mau menjawab penyakit apapun
        payload = {
            "contents": [{
                "parts": [{"text": f"Kamu adalah dokter AI profesional. Pasien bernama {data.patient_name} memiliki keluhan: '{data.symptoms}'. Berikan diagnosa medis kemungkinan (nama penyakit) dan saran pengobatan praktis. Jawab singkat padat."}]
            }]
        }
        
        # Timeout diperpanjang jadi 10 detik biar loading penyakit berat sempat
        response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result:
                full_text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Memecah jawaban Gemini biar rapi (Asumsi Gemini jawab panjang)
                # Kita ambil kalimat pertama sebagai diagnosa, sisanya saran
                sentences = full_text.split('.')
                diagnosis_clean = sentences[0] # Kalimat pertama jadi diagnosa
                advice_clean = " ".join(sentences[1:]).strip() # Sisanya saran
                if len(advice_clean) < 5: advice_clean = full_text # Jaga-jaga kalau error
                
            else:
                raise Exception("Google menolak menjawab (Safety Filter)")
        else:
            raise Exception(f"Koneksi Gagal: {response.status_code}")

    except Exception as e:
        # --- OTAK 2: MODE SIMULASI (AUTO-DETECT) ---
        print(f"⚠️ Pindah ke Mode Simulasi karena: {e}")
        
        s_lower = data.symptoms.lower()
        
        # Logika Manual Diperbanyak
        if "demam" in s_lower or "panas" in s_lower:
            diagnosis_clean = "Demam (Viral Infection)"
            advice_clean = "Minum Paracetamol, kompres hangat, cek suhu berkala."
        elif "perut" in s_lower or "mual" in s_lower or "lambung" in s_lower:
            diagnosis_clean = "Dispepsia / Maag"
            advice_clean = "Hindari makanan pedas/asam, makan teratur, minum obat lambung."
        elif "kepala" in s_lower or "pusing" in s_lower or "migrain" in s_lower:
            diagnosis_clean = "Cephalgia (Sakit Kepala)"
            advice_clean = "Istirahat di ruang gelap, hindari layar HP, minum obat pereda nyeri."
        elif "gatal" in s_lower or "kulit" in s_lower or "merah" in s_lower:
            diagnosis_clean = "Dermatitis / Alergi Kulit"
            advice_clean = "Jangan digaruk, gunakan bedak salisil atau salep gatal."
        elif "batuk" in s_lower or "pilek" in s_lower or "flu" in s_lower:
            diagnosis_clean = "Common Cold (ISPA Ringan)"
            advice_clean = "Istirahat total, minum vitamin C, gunakan masker."
        elif "tulang" in s_lower or "nyeri" in s_lower or "pegal" in s_lower:
            diagnosis_clean = "Myalgia (Nyeri Otot)"
            advice_clean = "Pijat ringan, gunakan krim otot panas, istirahat."
        else:
            # JAWABAN UMUM KALAU PENYAKIT TIDAK DIKENALI
            diagnosis_clean = "Gejala Umum / Kelelahan"
            advice_clean = f"Keluhan '{data.symptoms}' membutuhkan observasi lebih lanjut. Sarankan istirahat total dan kunjungi dokter jika berlanjut 3 hari."

    # Simpan
    new_record = PatientRecord(
        name=data.patient_name,
        symptoms=data.symptoms,
        diagnosis=diagnosis_clean,
        advice=advice_clean
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return {
        "status": "success",
        "id": new_record.id,
        "patient": new_record.name,
        "ai_diagnosis": new_record.diagnosis,
        "suggestion": new_record.advice
    }