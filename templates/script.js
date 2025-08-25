document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const uploadArea = document.getElementById('upload-area');
    const imageInput = document.getElementById('image-input');
    const uploadInstructions = document.getElementById('upload-instructions');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const ocrBtn = document.getElementById('ocr-btn');
    const clearBtn = document.getElementById('clear-btn');
    const loaderOverlay = document.getElementById('loader-overlay');
    const resultsContent = document.getElementById('results-content');
    const placeholder = document.getElementById('placeholder');
    const toastContainer = document.getElementById('toast-container');

    // State Variables
    let currentFile = null;
    let lastUploadedFilename = null;

    // --- Toast Notification System ---
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        let iconClass, title;

        switch (type) {
            case 'success':
                iconClass = 'fa-solid fa-check-circle';
                title = 'Success';
                break;
            case 'error':
                iconClass = 'fa-solid fa-times-circle';
                title = 'Error';
                break;
            default:
                iconClass = 'fa-solid fa-info-circle';
                title = 'Info';
        }

        toast.className = `toast text-white p-5 rounded-xl shadow-lg flex items-start gap-4 backdrop-blur-md`;
        toast.innerHTML = `
            <div class="shrink-0 pt-1">
                <i class="${iconClass} text-2xl"></i>
            </div>
            <div class="flex-1 min-w-0">
                <h4 class="font-bold text-lg mb-1">${title}</h4>
                <p class="text-base toast-message break-words">${message}</p>
            </div>
            <button class="toast-close text-2xl opacity-70 hover:opacity-100 transition-opacity shrink-0">&times;</button>
        `;

        toastContainer.appendChild(toast);
        toast.classList.add('toast-in');

        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => removeToast(toast));

        setTimeout(() => removeToast(toast), 6000);
    }

    function removeToast(toast) {
        if (toast.parentElement) {
            toast.classList.add('toast-out');
            toast.addEventListener('animationend', () => {
                if (toast.parentElement) {
                    toast.parentElement.removeChild(toast);
                }
            });
        }
    }


    // --- File Handling Functions ---
    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            showToast('Please select a valid image file (PNG, JPG, WEBP).', 'error');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            showToast('File size must be less than 10MB.', 'error');
            return;
        }

        currentFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            uploadInstructions.classList.add('hidden');
            imagePreviewContainer.classList.remove('hidden');
            ocrBtn.disabled = false;
            lastUploadedFilename = null; // Force re-upload if a new file is selected
            showToast('Image loaded! Ready to analyze.', 'success');
        };
        reader.readAsDataURL(file);
    }

    // --- UI State Management ---
    function setLoadingState(isLoading) {
        if (isLoading) {
            loaderOverlay.classList.remove('hidden');
            loaderOverlay.classList.add('flex');
        } else {
            loaderOverlay.classList.add('hidden');
            loaderOverlay.classList.remove('flex');
        }
        ocrBtn.disabled = isLoading;
        clearBtn.disabled = isLoading;
    }

    function resetUI() {
        currentFile = null;
        lastUploadedFilename = null;
        imageInput.value = '';
        uploadInstructions.classList.remove('hidden');
        imagePreviewContainer.classList.add('hidden');
        imagePreview.src = '#';
        ocrBtn.disabled = true;
        resultsContent.innerHTML = '';
        resultsContent.appendChild(placeholder);
        
        fetch('/clear-images', { method: 'POST' })
         .then(res => res.json())
         .then(data => showToast(data.message || 'Cleared successfully.', 'success'))
         .catch(() => showToast('Failed to clear server images.', 'error'));
    }

    // --- Data Processing Utilities ---
    function safeParseJSON(str) {
        try { return JSON.parse(str); } catch { return null; }
    }

    function extractJsonFromMessage(msg) {
        if (!msg || typeof msg !== 'string') return null;
        const first = msg.indexOf('{');
        const last = msg.lastIndexOf('}');
        if (first === -1 || last === -1 || last < first) return null;
        const slice = msg.slice(first, last + 1).trim();
        return safeParseJSON(slice);
    }

    function normalizeDetails(payload) {
        if (!payload) return {};
        if (payload.rc_vehicle_no || payload.rc_version) return payload;
        if (payload.result && payload.result.extraction_output) return payload.result.extraction_output;
        if (payload.data && (payload.data.rc_vehicle_no || payload.data.rc_version)) return payload.data;
        return payload;
    }

    // --- Results Rendering ---
    function renderResults(data) {
        let plate = 'N/A';
        let details = {};
        let rawForDisplay = '';

        if (data && typeof data === 'object' && !('message' in data)) {
            details = normalizeDetails(data);
            rawForDisplay = JSON.stringify(data, null, 2);
        } else {
            const msg = typeof data?.message === 'string' ? data.message : '';
            rawForDisplay = msg || '';
            if (msg) {
                const plateMatch = msg.match(/[A-Z]{2}[ -]?[0-9]{1,2}[ -]?[A-Z]{1,3}[ -]?[0-9]{1,4}/);
                if (plateMatch) plate = plateMatch[0].replace(/\s+/g, '');
                const extracted = extractJsonFromMessage(msg);
                if (extracted) details = normalizeDetails(extracted);
            }
        }

        plate = details.rc_vehicle_no || plate || 'N/A';

        const out = {
            plate: plate || 'N/A',
            owner: details.rc_owner_name || details.owner_name || 'N/A',
            makeModel: [details.rc_maker_desc, details.rc_maker_model].filter(Boolean).join(' ') || details.manufacturer_model || 'N/A',
            colour: details.colour || details.rc_color || 'N/A',
            fuel: details.rc_fuel_desc || details.fuel_type || 'N/A',
            regDate: details.rc_regn_dt || details.registration_date || 'N/A',
            insuranceUntil: details.rc_insurance_upto || details.insurance_validity || 'N/A',
            registeredAt: details.rc_registered_at || details.registered_place || 'N/A',
            status: details.rc_status || details.status_verification || 'N/A',
            statusAsOn: details.rc_status_as_on || null
        };

        const outputHTML = `
            <div class="p-6 h-full">
                <!-- Vehicle Summary Card -->
                <div class="card p-8 mb-6">
                    <h3 class="text-2xl font-bold text-blue-400 mb-6 border-b pb-2 border-blue-500/30">Vehicle Summary</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        ${createDetailRow('Plate Number', out.plate, false, 'text-xl font-bold text-gray-100')}
                        ${createDetailRow('Owner Name', out.owner)}
                        ${createDetailRow('Make & Model', out.makeModel)}
                        ${createDetailRow('Fuel Type', out.fuel)}
                        ${createDetailRow('Registration', out.regDate)}
                        ${createDetailRow('Insurance Until', out.insuranceUntil)}
                        ${createDetailRow('Registered At', out.registeredAt)}
                        ${out.statusAsOn ? createDetailRow('Status As On', out.statusAsOn) : ''}
                    </div>
                </div>
                
                <!-- Collapsible Terminal Response -->
                <div class="card">
                    <button id="toggle-terminal" class="w-full flex items-center justify-between p-6 hover:bg-white/5 transition-colors rounded-t-xl border-b border-blue-500/30">
                        <div class="flex items-center gap-3">
                            <div class="feature-icon w-10 h-10 rounded-lg flex items-center justify-center">
                                <i class="fa-solid fa-terminal"></i>
                            </div>
                            <div class="text-left">
                                <h4 class="text-lg font-semibold text-gray-100">Terminal Response</h4>
                                <p class="text-sm text-gray-400">View raw API response data</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-2">
                            <span id="toggle-text" class="text-sm text-gray-300 font-medium">Show Details</span>
                            <i id="toggle-icon" class="fa-solid fa-chevron-down text-gray-500 transition-transform duration-300"></i>
                        </div>
                    </button>
                    <div id="terminal-content" class="max-h-0 overflow-hidden transition-all duration-500 ease-in-out">
                        <div class="p-6 pt-0">
                            <pre class="whitespace-pre-wrap text-xs text-gray-300 bg-black/50 p-6 rounded-xl border border-blue-500/30 leading-relaxed font-mono max-h-[500px] overflow-auto">${rawForDisplay || 'No response data.'}</pre>
                        </div>
                    </div>
                </div>
            </div>`;
        
        resultsContent.innerHTML = outputHTML;
        document.getElementById('toggle-terminal').addEventListener('click', toggleTerminalResponse);
    }

    function createDetailRow(label, value, isStatus = false, valueClass = '') {
        const val = (value ?? 'N/A');
        const valStr = typeof val === 'string' ? val : JSON.stringify(val);
        return `
            <div class="flex justify-between items-center py-2 border-b border-gray-700/50">
                <span class="font-medium text-gray-400">${label}:</span>
                <span class="font-semibold text-gray-200 text-right ${valueClass}">${valStr || 'N/A'}</span>
            </div>`;
    }

    // --- Terminal Response Toggle Function ---
    function toggleTerminalResponse() {
        const content = document.getElementById('terminal-content');
        const toggleText = document.getElementById('toggle-text');
        const toggleIcon = document.getElementById('toggle-icon');

        if (!content) return;

        if (content.classList.contains('max-h-0')) {
            content.classList.remove('max-h-0');
            content.classList.add('max-h-[600px]');
            toggleText && (toggleText.textContent = 'Hide Details');
            toggleIcon && toggleIcon.classList.add('rotate-180');
        } else {
            content.classList.remove('max-h-[600px]');
            content.classList.add('max-h-0');
            toggleText && (toggleText.textContent = 'Show Details');
            toggleIcon && toggleIcon.classList.remove('rotate-180');
        }
    }

    // --- Event Listeners ---
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const file = e.dataTransfer.files && e.dataTransfer.files[0];
        if (file) handleFile(file);
    });

    clearBtn.addEventListener('click', resetUI);

    ocrBtn.addEventListener('click', async () => {
        if (!currentFile) {
            showToast('No file selected for analysis.', 'error');
            return;
        }
        
        setLoadingState(true);
        resultsContent.innerHTML = '';
        
        try {
            // Step 1: Upload image if it's a new file
            if (lastUploadedFilename !== currentFile.name) {
                const formData = new FormData();
                formData.append('image', currentFile);
                
                const uploadResponse = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (!uploadResponse.ok) {
                    throw new Error('Image upload failed. Please try again.');
                }
                
                const uploadData = await uploadResponse.json();
                showToast(uploadData.message || 'Image uploaded successfully.', 'info');
                lastUploadedFilename = currentFile.name;
            }
            
            // Step 2: Run OCR analysis
            const ocrResponse = await fetch('/run-ocr', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!ocrResponse.ok) {
                throw new Error('Analysis failed on the server. Please try again.');
            }
            
            const ocrData = await ocrResponse.json();
            renderResults(ocrData);
            showToast('Analysis completed successfully!', 'success');
            
        } catch (error) {
            console.error('Analysis error:', error);
            resultsContent.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full text-center p-12">
                    <div class="feature-icon w-20 h-20 rounded-full flex items-center justify-center mb-6">
                        <i class="fa-solid fa-exclamation-triangle text-red-400 text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-100 mb-2">Analysis Failed</h3>
                    <p class="text-gray-400 mb-4">${error.message}</p>
                    <button id="retry-btn" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                        Try Again
                    </button>
                </div>`;
            document.getElementById('retry-btn').addEventListener('click', () => ocrBtn.click());
            showToast(error.message || 'An unknown error occurred.', 'error');
        } finally {
            setLoadingState(false);
        }
    });

    // --- Keyboard shortcuts ---
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'u':
                    e.preventDefault();
                    imageInput.click();
                    break;
                case 'Enter':
                    if (!ocrBtn.disabled) {
                        e.preventDefault();
                        ocrBtn.click();
                    }
                    break;
                case 'Backspace':
                    if (currentFile) {
                        e.preventDefault();
                        resetUI();
                    }
                    break;
            }
        }
    });
});
