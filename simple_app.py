#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify, send_file
import os
import json
from datetime import datetime
from offer_generator import OfferGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'narissa-realty-2025'

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Offer Creator - Narissa Realty</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }
        .section { background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .form-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 3px; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .result { padding: 15px; margin: 15px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 Offer Creator</h1>
        <p>Automated Real Estate Offer Generation for Narissa Realty</p>
    </div>
    
    <form id="offerForm">
        <div class="section">
            <h2>Property Information</h2>
            <div class="form-group">
                <label>Property Address:</label>
                <input type="text" name="property_address" value="456 Pine Ridge Drive" required>
            </div>
            <div class="form-group">
                <label>City:</label>
                <input type="text" name="property_city" value="Nevada City" required>
            </div>
            <div class="form-group">
                <label>ZIP Code:</label>
                <input type="text" name="property_zip" value="95959" required>
            </div>
            <div class="form-group">
                <label>County:</label>
                <input type="text" name="property_county" value="Nevada">
            </div>
            <div class="form-group">
                <label>Purchase Price:</label>
                <input type="number" name="purchase_price" value="825000" required>
            </div>
        </div>
        
        <div class="section">
            <h2>Buyer Information</h2>
            <div class="form-group">
                <label>Buyer Full Name:</label>
                <input type="text" name="buyer_name" value="Michael and Sarah Johnson" required>
            </div>
            <div class="form-group">
                <label>Phone:</label>
                <input type="tel" name="buyer_phone" value="(530) 555-0198" required>
            </div>
            <div class="form-group">
                <label>Email:</label>
                <input type="email" name="buyer_email" value="mjohnson@email.com" required>
            </div>
        </div>
        
        <div class="section">
            <h2>Seller Information</h2>
            <div class="form-group">
                <label>Seller Full Name:</label>
                <input type="text" name="seller_name" value="Robert and Linda Martinez" required>
            </div>
        </div>
        
        <div class="section">
            <h2>Transaction Details</h2>
            <div class="form-group">
                <label>Offer Date:</label>
                <input type="date" name="offer_date" required>
            </div>
            <div class="form-group">
                <label>Deposit Amount:</label>
                <input type="number" name="deposit_amount" value="25000" required>
            </div>
        </div>
        
        <button type="submit" class="btn">Generate Offer Package</button>
    </form>
    
    <div id="result"></div>
    
    <script>
        document.getElementById('offerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<p>Generating offer package...</p>';
            
            try {
                const response = await fetch('/generate-offer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let html = '<div class="result success"><h3>✅ Offer Package Generated Successfully!</h3><ul>';
                    result.files.forEach(file => {
                        html += `<li><a href="/download/${file}" target="_blank">${file}</a></li>`;
                    });
                    html += '</ul></div>';
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="result error"><h3>❌ Error</h3><p>${result.error}</p></div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error"><h3>❌ Error</h3><p>${error.message}</p></div>`;
            }
        });
        
        // Set today's date as default
        document.querySelector('input[name="offer_date"]').value = new Date().toISOString().split('T')[0];
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate-offer', methods=['POST'])
def generate_offer():
    try:
        form_data = request.json
        
        # Organize data for the generator
        client_data = {
            'property': {
                'address': form_data.get('property_address', ''),
                'city': form_data.get('property_city', ''),
                'zip': form_data.get('property_zip', ''),
                'county': form_data.get('property_county', 'Nevada')
            },
            'buyer': {
                'name': form_data.get('buyer_name', ''),
                'phone': form_data.get('buyer_phone', ''),
                'email': form_data.get('buyer_email', '')
            },
            'seller': {
                'name': form_data.get('seller_name', '')
            },
            'purchase_details': {
                'purchase_price': form_data.get('purchase_price', ''),
                'deposit_amount': form_data.get('deposit_amount', ''),
                'offer_date': form_data.get('offer_date', '')
            }
        }
        
        # Generate offer package
        generator = OfferGenerator()
        files = generator.generate_offer_package(client_data)
        
        return jsonify({
            'success': True,
            'files': files,
            'message': f'Generated {len(files)} documents'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join('output', filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    print("🏠 Offer Creator for Narissa Realty")
    print("=" * 50)
    print("Starting web application...")
    print("Local access: http://localhost:5001")
    
    # Get WSL IP for Windows access
    try:
        import subprocess
        result = subprocess.run(['ip', 'addr', 'show', 'eth0'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line and '127.0.0.1' not in line:
                wsl_ip = line.strip().split()[1].split('/')[0]
                print(f"Windows access: http://{wsl_ip}:5001")
                break
    except:
        pass
    
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)