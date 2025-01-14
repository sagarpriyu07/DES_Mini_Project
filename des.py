
from flask import Flask, render_template_string, request, send_file
import os
import webbrowser
from Crypto.Cipher import DES

app = Flask(__name__)

# Helper functions for padding and unpadding
def pad_data(data):
    padding_len = 8 - (len(data) % 8)
    return data + bytes([padding_len] * padding_len)

def unpad_data(padded_data):
    padding_len = padded_data[-1]
    return padded_data[:-padding_len]

# File encryption function
def encrypt_file(input_file, output_file, key):
    des = DES.new(key, DES.MODE_ECB)
    with open(input_file, 'rb') as f:
        plaintext = f.read()

    padded_data = pad_data(plaintext)
    ciphertext = des.encrypt(padded_data)

    with open(output_file, 'wb') as f:
        f.write(ciphertext)

# File decryption function
def decrypt_file(input_file, output_file, key):
    des = DES.new(key, DES.MODE_ECB)
    with open(input_file, 'rb') as f:
        ciphertext = f.read()

    decrypted_data = des.decrypt(ciphertext)
    unpadded_data = unpad_data(decrypted_data)

    with open(output_file, 'wb') as f:
        f.write(unpadded_data)

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Encryptor/Decryptor</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        /* Body Styling */
        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: #333;
            background-image: url('https://via.placeholder.com/1600x900'); /* Add a background image */
            background-size: cover;
            background-position: center;
        }

        /* Container Styling */
        .container {
            max-width: 600px;
            width: 100%;
            background: rgba(255, 255, 255, 0.9); /* Add transparency for the container */
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
            animation: fadeIn 1s ease-out;
        }

        /* Header Styling */
        h1 {
            font-weight: 600;
            font-size: 2.5em;
            color: #4CAF50;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* Logo Styling */
        .logo {
            max-width: 150px;
            margin: 0 auto 30px;
        }

        /* Description Styling */
        .description {
            color: #777;
            font-size: 18px;
            margin-bottom: 30px;
            font-weight: 500;
        }

        /* Form Styling */
        .form-label {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 8px;
            display: block;
            text-align: left;
        }

        input, select, button {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border: 1px solid #ddd;
            font-size: 16px;
            background-color: #f9f9f9;
            transition: all 0.3s ease-in-out;
            box-sizing: border-box;
        }

        input:focus, select:focus, button:focus {
            outline: none;
            border-color: #4CAF50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.4);
        }

        button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
        }

        /* Footer Styling */
        .footer {
            font-size: 14px;
            color: #666;
            margin-top: 30px;
        }

        .footer a {
            color: #4CAF50;
            text-decoration: none;
            font-weight: 600;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        /* Animation */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

    </style>
</head>
<body>
    <div class="container">
        <!-- Logo Section -->
        <img src="https://via.placeholder.com/150" alt="Logo" class="logo">
        
        <h1>File Encryptor/Decryptor</h1>
        <p class="description">Easily encrypt or decrypt your files securely using a personal key of your choice.</p>

        <form action="/process" method="POST" enctype="multipart/form-data">
            <label for="file" class="form-label">Select File:</label>
            <input type="file" id="file" name="file" required>

            <label for="operation" class="form-label">Choose Operation:</label>
            <select id="operation" name="operation" required>
                <option value="Encrypt">Encrypt</option>
                <option value="Decrypt">Decrypt</option>
            </select>

            <label for="key" class="form-label">Enter Key (8 characters):</label>
            <input type="password" id="key" name="key" maxlength="8" required>

            <label for="output_filename" class="form-label">Output File Name:</label>
            <input type="text" id="output_filename" name="output_filename" required>

            <button type="submit">Process</button>
        </form>

        <div class="footer">
            <p>Created by <a href="https://www.example.com" target="_blank">Priyanka Sagar</a></p>
        </div>
    </div>
</body>
</html>

'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_file():
    operation = request.form['operation']
    key = request.form['key']
    if len(key) != 8:
        return "Error: Key must be exactly 8 characters long."
    
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return "Error: No file selected."

    input_filename = uploaded_file.filename
    input_filepath = os.path.join('uploads', input_filename)
    uploaded_file.save(input_filepath)

    output_filename = request.form['output_filename']
    output_filepath = os.path.join('uploads', output_filename)

    try:
        if operation == 'Encrypt':
            encrypt_file(input_filepath, output_filepath, key.encode('utf-8'))
        elif operation == 'Decrypt':
            decrypt_file(input_filepath, output_filepath, key.encode('utf-8'))
        else:
            return "Error: Invalid operation selected."
        
        return send_file(output_filepath, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)  # Ensure uploads directory exists
    port = 5000
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)  # Open the default web browser
    app.run(port=port, debug=True)
