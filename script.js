let selectedFiles = [];

// Screen navigation
function showWelcomeScreen() {
    document.getElementById('welcomeScreen').classList.remove('hidden');
    document.getElementById('uploadScreen').classList.add('hidden');
    document.getElementById('resultsScreen').classList.add('hidden');
}

function showUploadScreen() {
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('uploadScreen').classList.remove('hidden');
    document.getElementById('resultsScreen').classList.add('hidden');
    resetUpload();
}

function showResultsScreen() {
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('uploadScreen').classList.add('hidden');
    document.getElementById('resultsScreen').classList.remove('hidden');
}

function resetUpload() {
    selectedFiles = [];
    document.getElementById('filesList').innerHTML = '';
    document.getElementById('analyzeBtn').classList.add('hidden');
    document.getElementById('fileInput').value = '';
}

// File upload handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#9747FF';
    uploadArea.style.background = 'rgba(151, 71, 255, 0.05)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'rgba(151, 71, 255, 0.5)';
    uploadArea.style.background = 'white';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'rgba(151, 71, 255, 0.5)';
    uploadArea.style.background = 'white';

    const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
    if (files.length > 0) {
        handleFiles(files);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFiles(Array.from(e.target.files));
    }
});

function handleFiles(files) {
    selectedFiles = files;
    displayFilesList();
    document.getElementById('analyzeBtn').classList.remove('hidden');
}

function displayFilesList() {
    const filesList = document.getElementById('filesList');
    filesList.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            <span>${file.name}</span>
            <svg class="check-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
        `;
        filesList.appendChild(fileItem);
    });
}

// Analyze resume
async function analyzeResume() {
    if (selectedFiles.length === 0) return;

    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('spinner');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const jobRole = document.getElementById('jobRoleInput').value || 'Web Developer';

    // Show loading state
    btnText.textContent = 'Analyzing...';
    spinner.classList.remove('hidden');
    analyzeBtn.disabled = true;

    try {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch(`http://127.0.0.1:8000/analyze?job_role=${encodeURIComponent(jobRole)}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error('Analysis failed: ' + errorText);
        }

        const data = await response.json();
        displayResults(data, jobRole);
        showResultsScreen();

    } catch (error) {
        alert('Error analyzing resume: ' + error.message);
        console.error(error);
    } finally {
        btnText.textContent = 'Analyze All Resumes';
        spinner.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

function displayResults(data, jobRole) {
    const shortlisted = data.shortlisted || [];

    // Update header info
    document.getElementById('selectedRole').textContent = jobRole;
    document.getElementById('totalResumes').textContent = selectedFiles.length;
    document.getElementById('topCount').textContent = Math.min(10, shortlisted.length);

    // Display candidates list
    const candidatesList = document.getElementById('candidatesList');
    candidatesList.innerHTML = '';

    shortlisted.forEach((candidate, index) => {
        const score = Math.round(candidate.score * 100);
        const confidence = Math.round(candidate.confidence * 100);

        const candidateCard = document.createElement('div');
        candidateCard.className = 'candidate-card';
        candidateCard.innerHTML = `
            <div class="candidate-rank">#${index + 1}</div>
            <div class="candidate-info">
                <h3>${candidate.name}</h3>
                <p><strong>Predicted Role:</strong> ${candidate.predicted}</p>
                <p><strong>Match Score:</strong> ${score}%</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${score}%"></div>
                </div>
                <!-- <p class="confidence-text">Confidence: ${confidence}%</p> -->
            </div>
            <button class="download-btn" onclick="downloadCV('${candidate.name}')">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Download
            </button>
        `;
        candidatesList.appendChild(candidateCard);
    });
}

function downloadCV(filename) {
    // Download the CV file from the server
    const url = `http://127.0.0.1:8000/download/${encodeURIComponent(filename)}`;

    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
