from app.database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reference_id = db.Column(db.String(50), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    organization_id = db.Column(db.String(120), nullable=True)
    organization_name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(120), nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'organization': self.organization_name,
            'role': self.role
        }