from flask import Flask, send_from_directory, jsonify, request
import os
from models import db, Document,JsonEntity
from parser import parse_html,parse_json
import json
import re



app = Flask(__name__)


# Static folder configuration
app.config['TEMPLATES_FOLDER'] = 'templates'
# Update the path to your database
app.config['STATIC_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.sqlite3'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['HTML_FOLDER'] = 'data'
print(app.config['SQLALCHEMY_DATABASE_URI'])

db.init_app(app)




def process_documents_on_launch():
    """
    Process all HTML and JSON files in the specified folder and insert them into the database.
    """
    html_folder = app.config['HTML_FOLDER']

    if not os.path.exists(html_folder):
        print(f"HTML folder '{html_folder}' does not exist.")
        return

    for filename in os.listdir(html_folder):
        # Get corresponding JSON and HTML file paths
        json_file_path = os.path.join(html_folder, filename)
        html_filename = filename.replace('.json', '.html')  # Get corresponding HTML file name
        html_file_path = os.path.join(html_folder, html_filename)

        # Process if both JSON and HTML files exist
        if filename.endswith('.json') and os.path.exists(html_file_path):
            try:
                with open(json_file_path, 'r') as json_file:
                    # Parse the JSON file
                    entries = parse_json(json_file)
                    
                with open(html_file_path, 'rb') as html_file:
                    print("processing ",html_file_path)
                    # Parse the HTML file
                    processo, tribunal, sumario, descritores, relator, decisao, data, main_content = parse_html(html_file)
                    
                    # Modify main_content by replacing names with links
                    main_content = add_links_to_names(main_content, entries)

                    # Check if the document already exists in the database
                    document = Document.query.filter_by(processo=processo).first()

                    if document:
                        # Add JSON entries to the JsonEntity table
                        for name, label, url in entries:
                            json_entry = JsonEntity(
                                processo=processo,  # Directly associate with 'processo'
                                name=name,
                                label=label,
                                url=url
                            )
                            db.session.add(json_entry)
                    else:
                        # If the document doesn't exist, create a new document entry
                        document = Document(
                            processo=processo,
                            tribunal=tribunal,
                            sumario=sumario,
                            descritores=descritores,
                            relator=relator,
                            decisao=decisao,
                            data=data,
                            main_content=main_content  # Store the modified content
                        )
                        db.session.add(document)

            except Exception as e:
                print(f"Error processing JSON or HTML file '{filename}': {e}")

        # Process HTML files without corresponding JSON
        elif filename.endswith('.html') and not os.path.exists(json_file_path):
            try:
                with open(html_file_path, 'rb') as html_file:
                    # Parse the HTML file
                    
                    processo, tribunal, sumario, descritores, relator, decisao, data, main_content = parse_html(html_file)
                    
                    # Check if the document already exists to avoid duplicates
                    if not Document.query.filter_by(processo=processo).first():
                        document = Document(
                            processo=processo,
                            tribunal=tribunal,
                            sumario=sumario,
                            descritores=descritores,
                            relator=relator,
                            decisao=decisao,
                            data=data,
                            main_content=main_content
                        )
                        db.session.add(document)

            except Exception as e:
                print(f"Error processing HTML file '{filename}': {e}")

        # Process JSON files without corresponding HTML
        elif filename.endswith('.json') and not os.path.exists(html_file_path):
            try:
                with open(json_file_path, 'r') as json_file:
                    # Parse the JSON file
                    entries = parse_json(json_file)

                # Handle JSON data (e.g., save to JsonEntity or other logic)
                for name, label, url in entries:
                    # You can store these entries in a separate database table if needed
                    # For now, it's just a placeholder
                    json_entry = JsonEntity(
                        name=name,
                        label=label,
                        url=url
                    )
                    db.session.add(json_entry)

            except Exception as e:
                print(f"Error processing JSON file '{filename}': {e}")

    db.session.commit()  # Commit all changes after processing


def add_links_to_names(main_content, entries):
    
    """
    Replace names in the main content with corresponding links from the JSON entries.
    """
    
    
    for name, _, url in entries:
        # Escape the name to make it safe for regex (in case there are special characters)
        name_escaped = re.escape(name)

        # Define the regex pattern to match the name in the content
        pattern = r'(?<!\w)' + name_escaped + r'(?!\w)'


        # Replace the name with a hyperlink that keeps the original text and adds highlighting
        link = f'<a href="{url}" target="_blank" style="color: blue; text-decoration: underline;">{name}</a>'
        
        # Use re.sub to replace all occurrences of the name in the content
        main_content = re.sub(pattern, link, main_content)

    return main_content


# Serve the main page
@app.route('/')
def index():
    return send_from_directory(app.config['TEMPLATES_FOLDER'], 'index.html')


# Route to get all documents (GET)
@app.route('/api/documents', methods=['GET'])
def get_documents():
    documents = Document.query.all()
    return jsonify([{
        'id': doc.id,
        'processo': doc.processo,
        'tribunal': doc.tribunal,
        'sumario': doc.sumario,
        'descritores': doc.descritores,
        'relator': doc.relator,
        'decisao': doc.decisao,
        'data': doc.data,
        
    } for doc in documents]), 200

# Route to get a specific document by ID (GET)


@app.route('/api/documents/<int:id>', methods=['DELETE'])
def delete_document(id):
    document = Document.query.get(id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404  # Not found
    db.session.delete(document)
    db.session.commit()
    return jsonify({'message': 'Document deleted successfully'}), 200  # Success



@app.route('/document_details.html')
def document_details():
    return send_from_directory(app.config['TEMPLATES_FOLDER'], 'document_details.html')

@app.route('/api/documents/<int:id>', methods=['GET'])
def get_document_detail(id):
    """
    Get the detailed view of a document by its ID.
    """
    document = Document.query.get(id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404


    metadata = {
        'processo': document.processo,
        'tribunal': document.tribunal,
        'sumario': document.sumario,
        'descritores': document.descritores,
        'relator': document.relator,
        'decisao': document.decisao,
        'data': document.data,
        'main_content': document.main_content
    }
    return jsonify(metadata)

# Route to upload and parse a document (POST)
@app.route('/api/documents', methods=['POST'])
def parse_and_add_documents():
    html_file = request.files.get('html_file')
    
    if not html_file:
        return jsonify({'error': 'No file uploaded'}), 400

    # Parse the HTML file using the parse_html function
    processo, tribunal, sumario, descritores, relator, decisao, data = parse_html(html_file)
    
    # Create a new Document entry in the database
    document = Document(
        processo=processo,
        tribunal=tribunal,
        sumario=sumario,
        descritores=descritores,
        relator=relator,
        decisao=decisao,
        data=data
    )
    
    # Add the new document to the session and commit
    db.session.add(document)
    db.session.commit()
    
    return jsonify({
        'message': 'Document added successfully',
        'document': {
            'id': document.id,
            'processo': document.processo,
            'tribunal': document.tribunal,
            'sumario': document.sumario,
            'descritores': document.descritores,
            'relator': document.relator,
            'decisao': document.decisao,
            'data': document.data
        }
    }), 201
with app.app_context():
    db.create_all()
    process_documents_on_launch()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000,debug=True)
