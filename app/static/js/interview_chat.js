document.addEventListener('DOMContentLoaded', () => {
    let sessionId = null;
    
    const setupPanel = document.getElementById('setup-panel');
    const chatPanel = document.getElementById('chat-panel');
    const summaryPanel = document.getElementById('summary-panel');
    
    const roleInput = document.getElementById('job-role');
    const startBtn = document.getElementById('start-btn');
    const roleBadge = document.getElementById('role-badge');
    
    const thread = document.getElementById('chat-thread');
    const chatInput = document.getElementById('chat-input');
    const submitBtn = document.getElementById('submit-btn');
    const endBtn = document.getElementById('end-btn');
    
    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `chat-message ${role === 'interviewer' ? 'ai-msg' : 'user-msg'}`;
        div.innerHTML = `<div class="msg-bubble">${text}</div>`;
        thread.appendChild(div);
        thread.scrollTop = thread.scrollHeight;
    }

    startBtn.addEventListener('click', async () => {
        const role = roleInput.value.trim();
        if(!role) return;
        
        startBtn.disabled = true;
        startBtn.textContent = "Starting...";
        
        try {
            const res = await fetch('/api/interview/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({job_role: role})
            });
            const data = await res.json();
            if(data.session_id) {
                sessionId = data.session_id;
                roleBadge.textContent = role;
                setupPanel.style.display = 'none';
                chatPanel.style.display = 'flex';
                appendMessage('interviewer', data.question);
            }
        } catch (e) {
            alert("Error starting session");
            startBtn.disabled = false;
            startBtn.textContent = "Start Session";
        }
    });

    submitBtn.addEventListener('click', async () => {
        const answer = chatInput.value.trim();
        if(!answer || !sessionId) return;
        
        appendMessage('user', answer);
        chatInput.value = '';
        submitBtn.disabled = true;
        
        // Add loading indicator
        const loadingId = 'loading-' + Date.now();
        const div = document.createElement('div');
        div.id = loadingId;
        div.className = `chat-message ai-msg`;
        div.innerHTML = `<div class="msg-bubble"><span class="loading-dots">Typing...</span></div>`;
        thread.appendChild(div);
        thread.scrollTop = thread.scrollHeight;

        try {
            const res = await fetch('/api/interview/answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: sessionId, answer: answer})
            });
            const data = await res.json();
            
            document.getElementById(loadingId).remove();
            
            appendMessage('interviewer', data.question);
            
            if (data.question.includes("Thank you, that concludes our interview.")) {
                chatInput.disabled = true;
                submitBtn.style.display = 'none';
                endBtn.textContent = "View Summary";
            } else {
                submitBtn.disabled = false;
                chatInput.focus();
            }
        } catch (e) {
            document.getElementById(loadingId).remove();
            alert("Error sending answer");
            submitBtn.disabled = false;
        }
    });

    endBtn.addEventListener('click', async () => {
        if(!sessionId) return;
        
        chatPanel.style.display = 'none';
        summaryPanel.style.display = 'block';
        document.getElementById('summary-text').innerHTML = '<span class="loading-dots">Generating evaluation...</span>';
        
        try {
            const res = await fetch('/api/interview/end', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: sessionId})
            });
            const data = await res.json();
            
            document.getElementById('final-score').textContent = data.score;
            document.getElementById('summary-text').innerHTML = `<p>${data.summary}</p>`;
            
        } catch (e) {
            document.getElementById('summary-text').innerHTML = '<span class="error-text">Failed to generate summary.</span>';
        }
    });
});
