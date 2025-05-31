from flask import Flask, render_template, request, send_file, jsonify
import os
import json
from offer_engine import OfferEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'narissa-realty-offer-creator-2025'

# Initialize offer engine
offer_engine = OfferEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-offer', methods=['POST'])
def generate_offer():
    """Generate completed offer documents"""
    try:
        form_data = request.json
        
        # Validate required fields
        required_fields = ['buyerName', 'buyerEmail', 'propertyAddress', 'offerPrice', 'escrowDays', 'earnestMoney']
        for field in required_fields:
            if not form_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate offer package
        result = offer_engine.generate_offer_package(form_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated PDF file"""
    try:
        file_path = os.path.join('output', filename)
        if os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    print("🏠 Offer Creator - Narissa Realty")
    print("=" * 40)
    print("✅ Server starting...")
    print("📱 Local access: http://localhost:5000")    
    # Get WSL IP for Windows browser access
    try:
        import subprocess
        result = subprocess.run(['ip', 'addr', 'show', 'eth0'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line and '127.0.0.1' not in line:
                wsl_ip = line.strip().split()[1].split('/')[0]
                print(f"🌐 Windows access: http://{wsl_ip}:5000")
                break
    except:
        pass
    
    print("=" * 40)
    print("📋 Ready to generate real estate offers!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)