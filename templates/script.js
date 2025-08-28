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
    const toastContainer = document.getElementById('toast-container');

    // Placeholder HTML is stored to be reused
    const placeholderHTML = `
        <div id="placeholder" class="flex flex-col items-center justify-center h-full text-center p-16">
            <div class="feature-icon w-40 h-40 rounded-3xl flex items-center justify-center mb-10 animate-pulse-slow">
                <i class="fa-solid fa-search text-6xl"></i>
            </div>
            <h3 class="text-3xl font-bold text-gray-200 mb-6">Ready to Analyze</h3>
            <p class="text-gray-400 max-w-md leading-relaxed text-lg">
                Upload a vehicle image and we'll tell you all about it.
            </p>
        </div>`;
    
    resultsContent.innerHTML = placeholderHTML;

    // State Variables
    let currentFile = null;
    let lastUploadedFilename = null;

    // --- Toast Notification System ---
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        let iconClass, title;

        switch (type) {
            case 'success': iconClass = 'fa-solid fa-check-circle'; title = 'Success'; break;
            case 'error': iconClass = 'fa-solid fa-times-circle'; title = 'Error'; break;
            default: iconClass = 'fa-solid fa-info-circle'; title = 'Info';
        }

        toast.className = `toast text-white p-5 rounded-xl shadow-lg flex items-start gap-4 backdrop-blur-md`;
        toast.innerHTML = `
            <div class="shrink-0 pt-1"><i class="${iconClass} text-2xl"></i></div>
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
            toast.addEventListener('animationend', () => toast.parentElement?.removeChild(toast));
        }
    }

    // --- File Handling Functions ---
    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            showToast('Please select a valid image file (PNG, JPG, WEBP).', 'error');
            return;
        }
        currentFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            uploadInstructions.classList.add('hidden');
            imagePreviewContainer.classList.remove('hidden');
            ocrBtn.disabled = false;
            lastUploadedFilename = null;
            showToast('Image loaded! Ready to analyze.', 'success');
        };
        reader.readAsDataURL(file);
    }

    // --- UI State Management ---
    function setLoadingState(isLoading) {
        loaderOverlay.classList.toggle('hidden', !isLoading);
        loaderOverlay.classList.toggle('flex', isLoading);
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
        resultsContent.innerHTML = placeholderHTML;
        
        fetch('/clear-images', { method: 'POST' })
         .then(res => res.json())
         .then(data => showToast(data.message || 'Cleared successfully.', 'success'))
         .catch(() => showToast('Failed to clear server images.', 'error'));
    }

    // --- Results Rendering with TABS ---
    function renderResults(results) {
        resultsContent.innerHTML = ''; // Clear placeholder

        if (!results || results.length === 0) {
            resultsContent.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full text-center p-12">
                    <div class="feature-icon w-20 h-20 rounded-full flex items-center justify-center mb-6">
                        <i class="fa-solid fa-question-circle text-yellow-400 text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-100 mb-2">No Details Found</h3>
                    <p class="text-gray-400">Could not retrieve information for any detected plates.</p>
                </div>`;
        } else {
            // Create tab navigation and content containers
            const tabNav = document.createElement('div');
            tabNav.className = 'flex border-b border-gray-700/50 space-x-1 flex-wrap';

            const tabContentContainer = document.createElement('div');
            tabContentContainer.className = 'flex-grow p-1 relative overflow-auto';

            results.forEach((vehicleData, index) => {
                const plate = vehicleData.plate_number_queried || `Result ${index + 1}`;
                const button = document.createElement('button');
                button.className = 'px-6 py-3 font-semibold text-gray-400 border-b-2 border-transparent hover:text-white hover:bg-white/5 transition-all duration-300 rounded-t-lg';
                button.textContent = plate;
                button.dataset.tab = `tab-${index}`;
                tabNav.appendChild(button);

                const content = document.createElement('div');
                content.id = `tab-${index}`;
                content.className = 'tab-content hidden';
                content.innerHTML = createVehicleDetailHTML(vehicleData);
                tabContentContainer.appendChild(content);

                if (index === 0) {
                    button.classList.add('active-tab');
                    content.classList.remove('hidden');
                }
            });

            resultsContent.appendChild(tabNav);
            resultsContent.appendChild(tabContentContainer);

            // Add event listener for tab switching
            tabNav.addEventListener('click', (e) => {
                if (e.target.tagName === 'BUTTON') {
                    const tabId = e.target.dataset.tab;
                    tabNav.querySelectorAll('button').forEach(btn => btn.classList.remove('active-tab'));
                    tabContentContainer.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
                    e.target.classList.add('active-tab');
                    const activeContent = document.getElementById(tabId);
                    activeContent.classList.remove('hidden');
                    activeContent.querySelector('.toggle-raw-response')?.addEventListener('click', toggleRawResponse);
                }
            });
            document.querySelector('.tab-content:not(.hidden) .toggle-raw-response')?.addEventListener('click', toggleRawResponse);
        }
    }

    function createVehicleDetailHTML(data) {
        if (!data || typeof data !== 'object') {
            return `<div class="p-8 text-center text-red-400">Invalid data format received.</div>`;
        }
        if (data.error) {
            return `
                <div class="p-8 text-center">
                    <h3 class="text-lg font-bold text-red-400 mb-2">API Error</h3>
                    <p class="text-gray-300">Could not retrieve details for plate: <strong>${data.plate_number_queried || 'Unknown'}</strong></p>
                    <p class="text-sm text-gray-500 mt-2">Reason: ${data.error}</p>
                </div>`;
        }

        const out = {
            plate: data.plate_number_queried || 'N/A',
            owner: data.rc_owner_name || 'N/A',
            makeModel: [data.rc_maker_desc, data.rc_maker_model].filter(Boolean).join(' ') || 'N/A',
            fuel: data.rc_fuel_desc || 'N/A',
            regDate: data.rc_regn_dt || 'N/A',
            insuranceUntil: data.rc_insurance_upto || 'N/A',
            registeredAt: data.rc_registered_at || 'N/A',
        };
        const rawForDisplay = JSON.stringify(data, null, 2);

        return `
            <div class="p-4 h-full animate-fadeIn">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    ${createDetailRow('Plate Number', out.plate, 'text-xl font-bold text-gray-100')}
                    ${createDetailRow('Owner Name', out.owner)}
                    ${createDetailRow('Make & Model', out.makeModel)}
                    ${createDetailRow('Fuel Type', out.fuel)}
                    ${createDetailRow('Registration Date', out.regDate)}
                    ${createDetailRow('Insurance Valid Until', out.insuranceUntil)}
                    ${createDetailRow('Registered At', out.registeredAt)}
                </div>
                <div class="card mt-6">
                    <button class="toggle-raw-response w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors rounded-t-xl border-b border-blue-500/30">
                        <h4 class="text-md font-semibold text-gray-100">Raw API Response</h4>
                        <i class="fa-solid fa-chevron-down text-gray-500 transition-transform duration-300"></i>
                    </button>
                    <div class="raw-response-content max-h-0 overflow-hidden transition-all duration-500 ease-in-out">
                        <pre class="whitespace-pre-wrap text-xs text-gray-300 bg-black/50 p-4 rounded-b-xl font-mono max-h-[300px] overflow-auto">${rawForDisplay}</pre>
                    </div>
                </div>
            </div>`;
    }

    function createDetailRow(label, value, valueClass = '') {
        return `
            <div class="flex justify-between items-center py-2 border-b border-gray-700/50">
                <span class="font-medium text-gray-400">${label}:</span>
                <span class="font-semibold text-gray-200 text-right ${valueClass}">${value || 'N/A'}</span>
            </div>`;
    }

    function toggleRawResponse(event) {
        const button = event.currentTarget;
        const content = button.nextElementSibling;
        const icon = button.querySelector('i');
        if (content.classList.contains('max-h-0')) {
            content.classList.remove('max-h-0');
            content.classList.add('max-h-[400px]');
            icon.classList.add('rotate-180');
        } else {
            content.classList.remove('max-h-[400px]');
            content.classList.add('max-h-0');
            icon.classList.remove('rotate-180');
        }
    }

    // --- Event Listeners ---
    imageInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('drag-over'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('drag-over'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        handleFile(e.dataTransfer.files[0]);
    });
    clearBtn.addEventListener('click', resetUI);

    ocrBtn.addEventListener('click', async () => {
        if (!currentFile) { showToast('No file selected.', 'error'); return; }
        setLoadingState(true);
        resultsContent.innerHTML = '';
        
        try {
            // Step 1: Upload the image if it's a new one
            if (lastUploadedFilename !== currentFile.name) {
                const formData = new FormData();
                formData.append('image', currentFile);
                const uploadResponse = await fetch('/upload', { method: 'POST', body: formData });
                if (!uploadResponse.ok) {
                    const errData = await uploadResponse.json();
                    throw new Error(errData.error || 'Image upload failed.');
                }
                lastUploadedFilename = currentFile.name;
            }
            
            // Step 2: Run the OCR and API pipeline
            const ocrResponse = await fetch('/run-ocr', { method: 'POST' });
            
            // FIX: Check if the server responded with an error status code
            if (!ocrResponse.ok) {
                const errorData = await ocrResponse.json();
                throw new Error(errorData.error || `Server responded with status: ${ocrResponse.status}`);
            }

            // If the response is OK, parse the JSON
            const responseData = await ocrResponse.json();
            
            renderResults(responseData);
            showToast('Analysis complete!', 'success');
            
        } catch (error) {
            console.error('Analysis error:', error);
            showToast(error.message, 'error');
            resultsContent.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full text-center p-12">
                    <div class="feature-icon w-20 h-20 rounded-full flex items-center justify-center mb-6 bg-red-500/20 text-red-400">
                        <i class="fa-solid fa-triangle-exclamation text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-100 mb-2">Analysis Failed</h3>
                    <p class="text-gray-400">${error.message}</p>
                </div>`;
        } finally {
            setLoadingState(false);
        }
    });
});