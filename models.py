from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app
app = Flask(__name__)

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/filip/Desktop/NeuralShift/dms_project/instance/documents.sqlite3'  # Ensure path is correct
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but suppresses a warning

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Document model
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    processo = db.Column(db.String(100))
    tribunal = db.Column(db.String(100))
    sumario = db.Column(db.String(200))
    descritores = db.Column(db.String(200))
    relator = db.Column(db.String(100))
    decisao = db.Column(db.String(100))
    data = db.Column(db.String(20))
    main_content= db.Column(db.Text)

    def __repr__(self):
        return f'<Document {self.processo}>'

class JsonEntity(db.Model):
    __tablename__ = 'json_entities'
    
    id = db.Column(db.Integer, primary_key=True)
    processo = db.Column(db.String(255), db.ForeignKey('document.processo'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=True)
    
    document = db.relationship('Document', backref=db.backref('json_entities', lazy=True))

    def __repr__(self):
        return f"<JsonEntity(name={self.name}, label={self.label}, url={self.url})>"

# Create the database and tables
with app.app_context():
    db.create_all()  # Creates the document table if it doesn't exist



# Check if the table was created and the record was inserted
with app.app_context():
    document = Document.query.first()  # Fetch the first document
    print(document)
