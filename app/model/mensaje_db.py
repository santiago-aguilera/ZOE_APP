"""
Modelo SQLAlchemy para MENSAJE.
Mantiene los métodos POO originales.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .db import db


class Mensaje(db.Model):
    __tablename__ = "MENSAJE"

    id = Column(Integer, primary_key=True, autoincrement=True)
    remitente_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    destinatario_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    asunto = Column(String(255), nullable=False)
    cuerpo = Column(Text, nullable=True)
    enviado_en = Column(DateTime, default=datetime.now)
    leido = Column(Boolean, default=False)
    eliminado_remitente = Column(Boolean, default=False)
    eliminado_destinatario = Column(Boolean, default=False)

    # Relaciones
    remitente = relationship("Usuario", back_populates="mensajes_enviados", foreign_keys=[remitente_id])
    destinatario = relationship("Usuario", back_populates="mensajes_recibidos", foreign_keys=[destinatario_id])

    def __init__(self, id=None, remitente=None, destinatario=None, asunto=None, cuerpo=None, **kwargs):
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        if remitente is not None:
            self.remitente_id = remitente.id if hasattr(remitente, 'id') else remitente
            self.remitente = remitente if hasattr(remitente, 'id') else None
        if destinatario is not None:
            self.destinatario_id = destinatario.id if hasattr(destinatario, 'id') else destinatario
            self.destinatario = destinatario if hasattr(destinatario, 'id') else None
        self.asunto = asunto
        self.cuerpo = cuerpo

    def get_id(self):
        return self.id

    def get_remitente(self):
        return self.remitente

    def get_destinatario(self):
        return self.destinatario

    def get_asunto(self):
        return self.asunto

    def get_cuerpo(self):
        return self.cuerpo

    def es_leido(self):
        return self.leido

    def enviarMensaje(self):
        db.session.add(self)
        db.session.commit()
        print(f"Mensaje enviado de {self.remitente.nombre} a {self.destinatario.nombre}")

    def leerMensaje(self):
        self.leido = True
        db.session.commit()
        print(f"Mensaje leído: {self.asunto}")

    def mostrarInfo(self):
        estado = "Leído" if self.leido else "No leído"
        print(f"[Mensaje] {self.id} - {self.asunto} | Estado: {estado}")

    def __repr__(self):
        return f"<Mensaje {self.asunto}>"