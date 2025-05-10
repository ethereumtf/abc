// Helper function to convert string to title case
String.prototype.toTitleCase = function() {
    return this.charAt(0).toUpperCase() + this.slice(1).toLowerCase();
};

const toastContainer = document.createElement('div');
toastContainer.className = 'toast-container';
document.body.appendChild(toastContainer);

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }, 100);
}

// Initialize with default repository
const defaultRepo = {
    owner: 'tensorus',
    repo: 'tensorus'
};

// Set default repository URL
const repoUrlInput = document.getElementById('repo-url');
repoUrlInput.value = 'https://github.com/tensorus/tensorus';
repoUrlInput.disabled = true;

// Update UI with default repository
const repoStatus = document.getElementById('repo-status');
repoStatus.textContent = `Connected to ${defaultRepo.owner}/${defaultRepo.repo}`;
repoStatus.classList.add('success');

// Enable buttons by default
const actionButtons = document.querySelectorAll('.action-btn');
actionButtons.forEach(btn => btn.disabled = false);
const analyzeBtn = document.getElementById('analyze-btn');
analyzeBtn.disabled = false;
const createIssuesBtn = document.getElementById('create-issues-btn');
createIssuesBtn.disabled = false;

// Store current repo
let currentRepo = defaultRepo;

async function analyzeIssues() {
    try {
        showToast('Analyzing issues...', 'info');
        const response = await fetch('http://localhost:8001/api/analyze/issues', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentRepo)
        });
        const data = await response.json();
        
        displayAnalysisResults(data, 'issues');
        showToast('Issue analysis complete!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error analyzing issues', 'error');
    }
}

async function analyzeDocs() {
    try {
        showToast('Analyzing documentation...', 'info');
        const response = await fetch('http://localhost:8001/api/analyze/docs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentRepo)
        });
        const data = await response.json();
        
        displayAnalysisResults(data, 'docs');
        showToast('Documentation analysis complete!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error analyzing documentation', 'error');
    }
}

async function analyzeCode() {
    try {
        showToast('Analyzing code...', 'info');
        const response = await fetch('http://localhost:8001/api/analyze/code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentRepo)
        });
        const data = await response.json();
        
        displayAnalysisResults(data, 'code');
        showToast('Code analysis complete!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error analyzing code', 'error');
    }
}

async function analyzeTests() {
    try {
        showToast('Analyzing tests...', 'info');
        const response = await fetch('http://localhost:8001/api/analyze/tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentRepo)
        });
        const data = await response.json();
        
        displayAnalysisResults(data, 'tests');
        showToast('Test analysis complete!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error analyzing tests', 'error');
    }
}

async function createIssues() {
    try {
        showToast('Creating issues...', 'info');
        const response = await fetch('http://localhost:8001/api/create_issues', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentRepo)
        });
        const data = await response.json();
        
        displayAnalysisResults(data);
        refreshIssues();
        showToast(`Created ${data.issues_created} new issues!`, 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error creating issues', 'error');
    }
}

async function refreshIssues() {
    try {
        showToast('Refreshing issues...', 'info');
        const response = await fetch('http://localhost:8001/api/issues', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentRepo)
        });
        const issues = await response.json();
        
        displayIssues(issues);
        showToast('Issues refreshed!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Error fetching issues', 'error');
    }
}

function displayAnalysisResults(data, category) {
    const suggestionsDiv = document.getElementById('suggestions');
    suggestionsDiv.innerHTML = '';

    if (!data || !data.suggestions) {
        return;
    }

    for (const [cat, suggestions] of Object.entries(data.suggestions)) {
        if (!suggestions || !Array.isArray(suggestions)) {
            continue;
        }

        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'category-card';
        categoryDiv.innerHTML = `
            <h3>${cat.replace('_', ' ').toTitleCase()}</h3>
            <div class="suggestion-list">
                ${suggestions.map(s => `
                    <div class="suggestion-item">
                        <p>${s}</p>
                        <div class="priority-badge">
                            Priority: ${s.priority || 'Medium'}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        suggestionsDiv.appendChild(categoryDiv);
    }
}

function displayIssues(issues) {
    const issuesDiv = document.getElementById('issues');
    issuesDiv.innerHTML = '';

    if (issues.length === 0) {
        issuesDiv.innerHTML = '<p>No issues found</p>';
        return;
    }

    const issuesList = document.createElement('div');
    issuesList.className = 'issues-list';

    issues.forEach(issue => {
        const issueCard = document.createElement('div');
        issueCard.className = 'issue-card';
        issueCard.innerHTML = `
            <h4>${issue.title}</h4>
            <div class="issue-details">
                <div class="status ${issue.state === 'open' ? 'open' : 'closed'}">
                    ${issue.state === 'open' ? 'Open' : 'Closed'}
                </div>
                <p>${issue.body}</p>
                <div class="issue-meta">
                    <span><i class="fas fa-calendar"></i> Created: ${new Date(issue.created_at).toLocaleDateString()}</span>
                    <span><i class="fas fa-calendar"></i> Updated: ${new Date(issue.updated_at).toLocaleDateString()}</span>
                    <span><i class="fas fa-comments"></i> Comments: ${issue.comments}</span>
                </div>
            </div>
        `;
        issuesList.appendChild(issueCard);
    });

    issuesDiv.appendChild(issuesList);
}

// Add event listeners for buttons
document.getElementById('analyze-issues-btn').addEventListener('click', analyzeIssues);
document.getElementById('analyze-docs-btn').addEventListener('click', analyzeDocs);
document.getElementById('analyze-code-btn').addEventListener('click', analyzeCode);
document.getElementById('analyze-tests-btn').addEventListener('click', analyzeTests);
document.getElementById('create-issues-btn').addEventListener('click', createIssues);
document.getElementById('refresh-btn').addEventListener('click', refreshIssues);

// Initialize repository connection
window.addEventListener('load', () => {
    // Update UI with default repository
    const repoStatus = document.getElementById('repo-status');
    repoStatus.textContent = `Connected to ${defaultRepo.owner}/${defaultRepo.repo}`;
    repoStatus.classList.add('success');
});
