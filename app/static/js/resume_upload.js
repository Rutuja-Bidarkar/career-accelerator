document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('resume-file');
    const fileDisplay = document.getElementById('file-name-display');
    const form = document.getElementById('resume-form');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loading = document.getElementById('resume-loading');
    const resultsPanel = document.getElementById('results-panel');

    // Drag and drop handlers
    dropzone.addEventListener('click', () => fileInput.click());
    
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#ff8c00';
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = '#4a5568';
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#4a5568';
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateFileDisplay();
        }
    });
    
    fileInput.addEventListener('change', updateFileDisplay);
    
    function updateFileDisplay() {
        if (fileInput.files.length > 0) {
            fileDisplay.textContent = 'Selected: ' + fileInput.files[0].name;
            fileDisplay.style.display = 'block';
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files.length) {
            alert('Please select a file first.');
            return;
        }

        const formData = new FormData(form);
        
        analyzeBtn.disabled = true;
        loading.style.display = 'flex';
        resultsPanel.style.display = 'none';

        try {
            const res = await fetch('/services/resume', {
                method: 'POST',
                body: formData
            });
            
            const data = await res.json();
            
            if (data.success) {
                document.getElementById('res-score').textContent = data.overall_score;
                
                const buildList = (arr) => arr.map(i => `<li>${i}</li>`).join('');
                const buildTags = (arr) => arr.map(i => `<span>${i}</span>`).join('');
                
                document.getElementById('res-strengths').innerHTML = buildList(data.strengths);
                document.getElementById('res-weaknesses').innerHTML = buildList(data.weaknesses);
                document.getElementById('res-courses').innerHTML = buildList(data.suggested_courses);
                
                document.getElementById('res-existing').innerHTML = buildTags(data.existing_skills);
                document.getElementById('res-missing').innerHTML = buildTags(data.missing_skills);
                
                resultsPanel.style.display = 'block';
                
                // Transient banner
                const banner = document.getElementById('success-banner');
                banner.style.display = 'block';
                setTimeout(() => { banner.style.opacity = '0'; }, 3000);
            } else {
                alert('Analysis failed: ' + data.error);
            }
        } catch (err) {
            console.error(err);
            alert('Network error during analysis.');
        } finally {
            analyzeBtn.disabled = false;
            loading.style.display = 'none';
        }
    });
});
