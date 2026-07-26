document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('.roadmap-checkbox');
    if (!checkboxes.length) return;

    const container = document.getElementById('roadmap-steps');
    const roadmapId = container.getAttribute('data-career-id');
    const roadmapType = container.getAttribute('data-roadmap-type');
    const totalSteps = parseInt(container.getAttribute('data-total-steps'), 10);
    const fillBar = document.getElementById('progress-bar-fill');
    const pctText = document.getElementById('progress-pct-text');

    checkboxes.forEach(cb => {
        cb.addEventListener('change', async (e) => {
            const stepId = cb.getAttribute('data-step-id');
            const completed = cb.checked;
            
            // Toggle visual class immediately for snappy UI
            const card = cb.closest('.roadmap-step-card');
            if (completed) {
                card.classList.add('completed');
            } else {
                card.classList.remove('completed');
            }

            try {
                const response = await fetch('/api/roadmap/toggle', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        roadmap_type: roadmapType,
                        roadmap_id: parseInt(roadmapId, 10),
                        step_id: parseInt(stepId, 10),
                        completed: completed,
                        total_steps: totalSteps
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    // Update progress bar
                    fillBar.style.width = data.progress_pct + '%';
                    pctText.textContent = data.progress_pct + '% Complete';
                }
            } catch (err) {
                console.error("Failed to save progress", err);
                // Revert visual if failed
                cb.checked = !completed;
                if (!completed) card.classList.add('completed');
                else card.classList.remove('completed');
            }
        });
    });
});
