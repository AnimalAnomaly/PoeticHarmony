from app import db
from datetime import datetime

class Composition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    poem_text = db.Column(db.Text, nullable=False)
    midi_filename = db.Column(db.String(100), nullable=False)
    audio_filename = db.Column(db.String(100), nullable=True)
    analysis_data = db.Column(db.Text, nullable=True)  # JSON string of analysis results
    instruments = db.Column(db.String(200), nullable=True)  # Comma-separated instrument list
    tempo = db.Column(db.Integer, default=120)
    key_signature = db.Column(db.String(10), default='C')
    time_signature = db.Column(db.String(10), default='4/4')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Composition {self.title}>'
