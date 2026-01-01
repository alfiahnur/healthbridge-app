import { useState } from "react";
import axios from "axios";
import "./index.css";

function App() {
  // State untuk mengatur halaman (Landing Page vs Form)
  const [isStarted, setIsStarted] = useState(false);
  
  // State untuk Data Form
  const [name, setName] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleDiagnose = async () => {
    if (!name || !symptoms) {
      alert("Harap isi nama dan keluhan!");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/diagnose", {
        patient_name: name,
        symptoms: symptoms,
      });
      setResult(response.data);
    } catch (error) {
      console.error("Error:", error);
      alert("Gagal terhubung ke backend!");
    } finally {
      setLoading(false);
    }
  };

  // --- HALAMAN 1: LANDING PAGE (AWAL) ---
  if (!isStarted) {
    return (
      <div className="app-container">
        <div className="hero-section">
          {/* Logo Melayang */}
          <div className="hero-logo">🤖💊</div>
          
          <h1 className="hero-title">HealthBridge AI</h1>
          <p className="hero-subtitle">
            Asisten kesehatan pribadi Anda yang didukung oleh Artificial Intelligence.
            Diagnosa awal cepat, akurat, dan mudah.
          </p>
          
          <button className="btn-start" onClick={() => setIsStarted(true)}>
            Mulai Konsultasi ➔
          </button>
        </div>
      </div>
    );
  }

  // --- HALAMAN 2: FORM DIAGNOSA (UTAMA) ---
  return (
    <div className="app-container">
      {/* Tombol Back Kecil di Pojok Kiri */}
      <div style={{textAlign: "left", marginBottom: "10px"}}>
        <button 
            onClick={() => setIsStarted(false)} 
            style={{background:"none", border:"none", cursor:"pointer", color:"#666"}}
        >
            ⬅ Kembali
        </button>
      </div>

      <h1>🏥 Konsultasi AI</h1>
      <p style={{ color: "#777", marginBottom: "2rem" }}>
        Silakan jelaskan keluhan Anda secara detail.
      </p>

      <div className="form-group">
        <label>Nama Pasien</label>
        <input
          type="text"
          placeholder="Masukkan nama Anda..."
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Keluhan Utama</label>
        <textarea
          placeholder="Contoh: Saya merasa pusing berputar, mual, dan keringat dingin..."
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
        ></textarea>
      </div>

      <button 
        className="btn-diagnose" 
        onClick={handleDiagnose} 
        disabled={loading}
      >
        {loading ? "Sedang Menganalisa..." : "✨ Cek Diagnosa Sekarang"}
      </button>

      {result && (
        <div className="result-box">
          <div className="result-title">
            📋 Hasil Analisa untuk <strong>{result.patient}</strong>
          </div>
          
          <div className="result-item-container delay-1">
            <span className="label-result">🤖 Diagnosa AI:</span>
            <div className="highlight-diagnosis">
              {result.ai_diagnosis}
            </div>
          </div>

          <div className="result-item-container delay-2">
            <span className="label-result">💡 Saran & Tindakan:</span>
            <div className="highlight-suggestion">
              {result.suggestion}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;