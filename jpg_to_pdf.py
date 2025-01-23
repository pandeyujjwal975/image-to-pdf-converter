from flask import Flask, request, send_file, render_template_string
from PIL import Image
import os
import uuid

app = Flask(__name__)

# Define the path for uploads directory
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

# Ensure that the uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                flex-direction: column;
            }
            .container {
                background-color: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                width: 400px;
                text-align: center;
            }
            h1 {
                font-size: 24px;
                color: #333;
                margin-bottom: 20px;
            }
            input[type="file"] {
                margin-bottom: 20px;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
            input[type="submit"] {
                padding: 12px 25px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
            .footer {
                margin-top: 20px;
                font-size: 14px;
                color: #777;
                text-align: center;
            }
            #preview {
                display: none;
                margin-top: 20px;
                max-width: 100%;
                max-height: 300px;
            }
            #loading {
                display: none;
                font-size: 18px;
                color: #555;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Upload JPG to Convert to PDF</h1>
            <form id="upload-form" action="/convert" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/jpeg" id="file-input" />
                <br><br>
                <input type="submit" value="Convert to PDF" id="submit-btn" />
            </form>
            <img id="preview" src="" alt="Image Preview" />
            <div id="loading">Converting... Please wait.</div>
            <div id="footer" class="footer">
                <p>Created by Ujjwal</p>
            </div>
        </div>

        <script>
            // Handle image preview
            document.getElementById('file-input').addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const preview = document.getElementById('preview');
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            });

            // Handle form submission
            document.getElementById('upload-form').addEventListener('submit', function(event) {
                event.preventDefault(); // Prevent the form from submitting normally
                const formData = new FormData(this);
                const submitButton = document.getElementById('submit-btn');
                const loadingText = document.getElementById('loading');

                // Show loading
                submitButton.disabled = true;
                loadingText.style.display = 'block';

                // Make AJAX request to convert the file
                fetch('/convert', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        return response.blob();
                    } else {
                        throw new Error('Failed to convert the image');
                    }
                })
                .then(blob => {
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = 'converted.pdf'; // Name of the downloaded PDF
                    link.click();
                    submitButton.disabled = false;
                    loadingText.style.display = 'none';
                })
                .catch(error => {
                    alert(error.message);
                    submitButton.disabled = false;
                    loadingText.style.display = 'none';
                });
            });
        </script>
    </body>
    </html>
    '''

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    # Get the uploaded file
    file = request.files['file']
    if not file:
        return "No file uploaded", 400
    
    # Define file paths
    file_name = str(uuid.uuid4()) + ".jpg"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    pdf_path = os.path.join(UPLOAD_FOLDER, file_name.replace('.jpg', '.pdf'))
    
    # Save the file temporarily
    file.save(file_path)
    
    # Convert the image to PDF
    try:
        image = Image.open(file_path)
        image.convert('RGB').save(pdf_path)
        
        # Return the generated PDF file to the user
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return f"Error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)