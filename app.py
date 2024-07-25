from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import spacy
import fitz  # PyMuPDF

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# Import the Resume model
# from models import Resumes

# Load Spacy model
nlp = spacy.load("en_core_web_sm")

def extract_information(text):
    doc = nlp(text)
    extracted_info = {
        "name": None,
        "email": None,
        "skills": []
    }

    for ent in doc.ents:
        if ent.label_ == "PERSON" and not extracted_info["name"]:
            extracted_info["name"] = ent.text
        elif ent.label_ == "EMAIL":
            extracted_info["email"] = ent.text

    for token in doc:
        if token.pos_ == "NOUN" and token.dep_ == "compound":
            extracted_info["skills"].append(token.text)

    return extracted_info

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    if file and file.filename.endswith('.pdf'):
        content = extract_text_from_pdf(file)
        extracted_info = extract_information(content)
        
        name = extracted_info["name"]
        email = extracted_info["email"]
        skills = ', '.join(extracted_info["skills"])

        new_resume = Resumes(name=name, email=email, skills=skills)
        db.session.add(new_resume)
        db.session.commit()
        
        return jsonify(extracted_info)
    

class Resumes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    skills = db.Column(db.Text)

    def __init__(self, name, email, skills):
        self.name = name
        self.email = email
        self.skills = skills

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
