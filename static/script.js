// Input sanitization utility functions
function sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    
    // Remove potentially dangerous HTML tags and scripts
    const div = document.createElement('div');
    div.textContent = input;
    let sanitized = div.innerHTML;
    
    // Remove common XSS patterns
    sanitized = sanitized
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
        .replace(/javascript:/gi, '')
        .replace(/on\w+\s*=/gi, '')
        .replace(/data:\s*text\/html/gi, '')
        .replace(/vbscript:/gi, '')
        .replace(/expression\s*\(/gi, '');
    
    // Limit length to prevent DoS
    return sanitized.substring(0, 10000);
}

function sanitizeFormData(data) {
    const sanitized = {};
    for (const [key, value] of Object.entries(data)) {
        if (typeof value === 'string') {
            sanitized[key] = sanitizeInput(value);
        } else {
            sanitized[key] = value;
        }
    }
    return sanitized;
}

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
        
        // Sanitize form data before sending
        const sanitizedData = sanitizeFormData(data);
        
        try {
            const response = await fetch('/api/generate-offer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sanitizedData)
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

document.addEventListener('DOMContentLoaded', function() {
    const submitConversationBtn = document.getElementById('submit_conversation_btn');
    const conversationTextInput = document.getElementById('conversation_text_input');
    const conversationResultDisplay = document.getElementById('conversation_result_display');

    if (submitConversationBtn && conversationTextInput && conversationResultDisplay) {
        console.log("Process Conversation UI elements found. Adding event listener.");
        submitConversationBtn.addEventListener('click', async function() {
            const rawConversationText = conversationTextInput.value.trim();
            conversationResultDisplay.innerHTML = ''; // Clear previous results
            conversationResultDisplay.style.display = 'none';

            if (!rawConversationText) {
                conversationResultDisplay.innerHTML = '<div class="alert alert-warning">Please paste some text to process.</div>';
                conversationResultDisplay.style.display = 'block';
                return;
            }

            // Sanitize the conversation text before sending
            const conversationText = sanitizeInput(rawConversationText);

            conversationResultDisplay.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Processing...';
            conversationResultDisplay.style.display = 'block';

            try {
                const response = await fetch('/process_email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email_content: conversationText })
                });

                const data = await response.json();
                conversationResultDisplay.innerHTML = ''; // Clear processing message

                if (response.ok) {
                    if (data.proposed_operation && data.proposed_operation.proposal_text) {
                        let html = `<p>${data.proposed_operation.proposal_text}</p>`;
                        html += '<h6>Extracted Data:</h6><ul class="list-group mb-3">';
                        for (const [key, value] of Object.entries(data.proposed_operation.data)) {
                            html += `<li class="list-group-item d-flex justify-content-between align-items-center">
                                ${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                <span class="badge bg-primary rounded-pill">${value}</span>
                            </li>`;
                        }
                        html += '</ul>';

                        const confirmButton = document.createElement('button');
                        confirmButton.textContent = 'Confirm';
                        confirmButton.className = 'btn btn-success me-2';
                        confirmButton.dataset.operationId = data.operation_id;
                        confirmButton.addEventListener('click', handleOperationConfirmation);

                        const cancelButton = document.createElement('button');
                        cancelButton.textContent = 'Cancel';
                        cancelButton.className = 'btn btn-danger';
                        cancelButton.dataset.operationId = data.operation_id;
                        cancelButton.addEventListener('click', handleOperationConfirmation);

                        const buttonDiv = document.createElement('div');
                        buttonDiv.appendChild(confirmButton);
                        buttonDiv.appendChild(cancelButton);

                        conversationResultDisplay.innerHTML = html;
                        conversationResultDisplay.appendChild(buttonDiv);

                    } else if (data.message) {
                         conversationResultDisplay.innerHTML = `<div class="alert alert-info">${data.message}</div>`;
                         if (data.extracted_entities) {
                            let entitiesHtml = '<h6>Raw Extracted Entities:</h6><ul class="list-group mb-3">';
                            for (const [key, value] of Object.entries(data.extracted_entities)) {
                                 entitiesHtml += `<li class="list-group-item d-flex justify-content-between align-items-center">
                                    ${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    <span class="badge bg-secondary rounded-pill">${value}</span>
                                </li>`;
                            }
                            entitiesHtml += '</ul>';
                            conversationResultDisplay.innerHTML += entitiesHtml;
                         }
                    } else {
                        conversationResultDisplay.innerHTML = `<div class="alert alert-warning">${data.error || 'Unknown response from server.'}</div>`;
                    }
                } else {
                    // Handle HTTP errors (e.g., 400, 500)
                    let errorMsg = `<div class="alert alert-danger">Error: ${data.message || response.statusText}</div>`;
                    if (data.validation_errors) {
                        errorMsg += '<h6>Validation Errors:</h6><ul class="list-group">';
                        data.validation_errors.forEach(err => {
                            errorMsg += `<li class="list-group-item list-group-item-danger">${err}</li>`;
                        });
                        errorMsg += '</ul>';
                    }
                     if (data.extracted_entities) {
                        let entitiesHtml = '<h6>Raw Extracted Entities (before validation):</h6><ul class="list-group mb-3">';
                        for (const [key, value] of Object.entries(data.extracted_entities)) {
                             entitiesHtml += `<li class="list-group-item d-flex justify-content-between align-items-center">
                                ${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                <span class="badge bg-secondary rounded-pill">${value}</span>
                            </li>`;
                        }
                        entitiesHtml += '</ul>';
                        errorMsg += entitiesHtml;
                     }
                    conversationResultDisplay.innerHTML = errorMsg;
                }
            } catch (error) {
                console.error('Error processing conversation:', error);
                conversationResultDisplay.innerHTML = `<div class="alert alert-danger">Network error or server issue. Please try again. ${error.message}</div>`;
            }
            conversationResultDisplay.style.display = 'block';
        });

        async function handleOperationConfirmation(event) {
            const operationId = event.target.dataset.operationId;
            const confirmed = event.target.textContent === 'Confirm';

            conversationResultDisplay.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Confirming...';

            try {
                const response = await fetch('/confirm_operation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ operation_id: operationId, confirmed: confirmed })
                });
                const data = await response.json();

                if (response.ok && data.status === 'completed') {
                     conversationResultDisplay.innerHTML = `<div class="alert alert-success">${data.message || 'Operation completed successfully!'}</div>`;
                } else if (data.status === 'rejected') {
                     conversationResultDisplay.innerHTML = `<div class="alert alert-info">${data.message || 'Operation cancelled.'}</div>`;
                }
                else {
                    conversationResultDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.message || data.error || 'Failed to confirm operation.'}</div>`;
                }
            } catch (error) {
                console.error('Error confirming operation:', error);
                conversationResultDisplay.innerHTML = `<div class="alert alert-danger">Network error during confirmation. ${error.message}</div>`;
            }
            conversationResultDisplay.style.display = 'block';
        }
    } else {
        console.log("Process Conversation UI elements NOT found on this page.");
    }
});

async function displayFormPreview(formId, clientId, propertyId, transactionId, targetDivId) {
    const targetDiv = document.getElementById(targetDivId);
    if (!targetDiv) {
        console.error(`Target div with ID ${targetDivId} not found.`);
        return;
    }

    targetDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Loading preview...';
    targetDiv.style.display = 'block'; // Make it visible

    try {
        const response = await fetch('/api/forms/preview_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                form_id: formId,
                client_id: clientId,
                property_id: propertyId,
                transaction_id: transactionId
            })
        });

        const data = await response.json();
        targetDiv.innerHTML = ''; // Clear loading message

        if (response.ok && data.success && data.preview_fields) {
            let html = `<h5>Preview: ${data.form_name}</h5>`;
            html += '<ul class="list-group mb-3">';
            data.preview_fields.forEach(field => {
                html += `<li class="list-group-item">
                            <strong>${field.display_label}:</strong> ${field.value_from_crm || '<em class="text-muted">Not set/empty</em>'}
                            <br><small class="text-muted">Source: ${field.crm_source_expression} | Page: ${field.page} | Coords: ${JSON.stringify(field.coordinates)}</small>
                         </li>`;
            });
            html += '</ul>';

            const generateButton = document.createElement('button');
            generateButton.textContent = 'Generate PDF';
            generateButton.className = 'btn btn-success';
            generateButton.addEventListener('click', async () => {
                targetDiv.innerHTML += '<div id="pdf_generation_status" class="mt-2 alert alert-info"><div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Generating PDF...</div>';
                try {
                    const populateResponse = await fetch('/api/forms/populate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            form_id: formId,
                            client_id: clientId,
                            property_id: propertyId,
                            transaction_id: transactionId
                        })
                    });
                    const populateData = await populateResponse.json();
                    const pdfStatusDiv = document.getElementById('pdf_generation_status');

                    if (populateResponse.ok && populateData.success && populateData.population_result && populateData.population_result.success) {
                        const result = populateData.population_result;
                        const pdfFileName = result.output_path ? result.output_path.split('/').pop() : 'form.pdf';
                        // The /download URL should be /api/forms/download/<form_id>/<filename> based on form_api_backend.py
                        const downloadUrl = `/api/forms/download/${formId}/${encodeURIComponent(pdfFileName)}`;

                        if(pdfStatusDiv) {
                            pdfStatusDiv.className = 'mt-2 alert alert-success';
                            pdfStatusDiv.innerHTML = `PDF generated: <a href="${downloadUrl}" target="_blank" class="alert-link">Download ${pdfFileName}</a>
                                                      <br><small>Fields Populated: ${result.field_count}, Processing Time: ${result.processing_time_ms}ms</small>`;
                        }
                    } else {
                        if(pdfStatusDiv) {
                            pdfStatusDiv.className = 'mt-2 alert alert-danger';
                            pdfStatusDiv.innerHTML = `Error generating PDF: ${populateData.error || (populateData.population_result ? populateData.population_result.message : 'Unknown error')}`;
                        }
                    }
                } catch (populateError) {
                    console.error('Error populating form:', populateError);
                     const pdfStatusDiv = document.getElementById('pdf_generation_status');
                     if(pdfStatusDiv) {
                        pdfStatusDiv.className = 'mt-2 alert alert-danger';
                        pdfStatusDiv.innerHTML = `Network error during PDF generation: ${populateError.message}`;
                     }
                }
            });

            targetDiv.innerHTML = html; // Add the preview list first
            targetDiv.appendChild(generateButton); // Then append the button

        } else {
            targetDiv.innerHTML = `<div class="alert alert-danger">Error loading preview: ${data.error || 'Unknown server error.'}</div>`;
        }

    } catch (error) {
        console.error('Error fetching form preview:', error);
        targetDiv.innerHTML = `<div class="alert alert-danger">Network error or server issue fetching preview. ${error.message}</div>`;
    }
}

// Test invocation for displayFormPreview
document.addEventListener('DOMContentLoaded', function() {
    const testPreviewBtn = document.getElementById('test_form_preview_btn');
    if (testPreviewBtn) {
        testPreviewBtn.addEventListener('click', function() {
            // Using placeholder IDs. Replace with actual IDs from your CRM for real testing.
            const testFormId = 'buyer_representation_agreement'; // Ensure this form_id exists in your config
            const testClientId = 'client_001';
            const testPropertyId = 'property_001';
            const testTransactionId = 'transaction_001'; // Can be null if not always required
            const targetDivId = 'form_preview_output';

            console.log(`Test button clicked. Calling displayFormPreview with:
                formId=${testFormId}, clientId=${testClientId}, propertyId=${testPropertyId}, transactionId=${testTransactionId}, targetDivId=${targetDivId}`);

            displayFormPreview(testFormId, testClientId, testPropertyId, testTransactionId, targetDivId);
        });
    }
});