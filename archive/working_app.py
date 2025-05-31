from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from real_pdf_filler import RealPDFFiller

app = Flask(__name__)
app.config['SECRET_KEY'] = 'narissa-realty-offer-creator-2025'

# Initialize PDF filler
pdf_filler = RealPDFFiller()

@app.route('/')
def index():
    return render_template('working_form.html')

@app.route('/api/generate-real-offer', methods=['POST'])
def generate_real_offer():
    """Generate actual filled PDF forms"""
    try:
        form_data = request.json
        print(f"📋 Received form data: {form_data}")
        
        # Validate required fields
        required_fields = ['buyerName', 'buyerEmail', 'propertyAddress', 'offerPrice', 'escrowDays', 'earnestMoney']
        for field in required_fields:
            if not form_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate real offer package
        result = pdf_filler.generate_real_offer(form_data)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Error generating offer: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated files"""
    try:
        file_path = os.path.join('generated_offers', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/list-offers')
def list_offers():
    """List all generated offers"""
    try:
        offers = []
        if os.path.exists('generated_offers'):
            for folder in os.listdir('generated_offers'):
                folder_path = os.path.join('generated_offers', folder)
                if os.path.isdir(folder_path):
                    files = [f for f in os.listdir(folder_path) if f.endswith(('.pdf', '.txt'))]
                    offers.append({
                        'folder': folder,
                        'files': files,
                        'count': len(files)
                    })
        return jsonify({'offers': offers})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🏠 REAL Offer Creator - Narissa Realty")
    print("=" * 50)
    print("🚀 Starting REAL PDF generation server...")
    print("📱 Local: http://localhost:5001")
    
    # Get WSL IP
    try:
        import subprocess
        result = subprocess.run(['ip', 'addr', 'show', 'eth0'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line and '127.0.0.1' not in line:
                wsl_ip = line.strip().split()[1].split('/')[0]
                print(f"🌐 Windows: http://{wsl_ip}:5001")
                break
    except:
        pass
    
    print("=" * 50)
    print("📋 Ready to generate REAL offer documents!")
    
    app.run(debug=True, host='0.0.0.0', port=5001)