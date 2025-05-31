document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('offerForm');
    const generateBtn = document.getElementById('generateBtn');
    const status = document.getElementById('status');
    const downloadSection = document.getElementById('downloadSection');
    
    // Auto-calculate earnest money suggestion
    const offerPrice = document.getElementById('offerPrice');
    const earnestMoney = document.getElementById('earnestMoney');
    
    offerPrice.addEventListener('input', function() {
        const price = parseFloat(this.value);
        if (price > 0) {
            const suggested = Math.round(price * 0.02); // 2% suggestion
            earnestMoney.placeholder = suggested.toString();
        }
    });
    
    // Format currency inputs
    function formatCurrency(input) {
        input.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = Math.round(value);
            }
        });
    }
    
    formatCurrency(offerPrice);
    formatCurrency(earnestMoney);
    
    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        generateBtn.disabled = true;
        generateBtn.textContent = '⏳ Generating...';
        status.className = 'status';
        status.textContent = 'Processing your offer documents...';
        downloadSection.className = 'download-section hidden';
        
        // Collect form data
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            if (key === 'sellerPaysBroker' || key === 'hasSeptic' || key === 'hasWell') {
                data[key] = true;
            } else {
                data[key] = value;
            }
        }
        
        // Add unchecked checkboxes as false
        ['sellerPaysBroker', 'hasSeptic', 'hasWell'].forEach(field => {
            if (!data[field]) data[field] = false;
        });
        
        try {
            const response = await fetch('/api/generate-offer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();            
            if (result.success) {
                status.className = 'status hidden';
                downloadSection.className = 'download-section';
                
                const downloadLinks = document.getElementById('downloadLinks');
                downloadLinks.innerHTML = `
                    <a href="/download/complete-offer-package.pdf" class="btn-primary" style="display: inline-block; text-decoration: none; margin: 10px;">
                        📥 Download Complete Offer Package
                    </a>
                `;
            } else {
                status.textContent = 'Error: ' + result.error;
                status.style.color = 'red';
            }
            
        } catch (error) {
            status.textContent = 'Network error. Please try again.';
            status.style.color = 'red';
        }
        
        // Reset button
        generateBtn.disabled = false;
        generateBtn.textContent = '📄 Generate Offer Package';
    });
});