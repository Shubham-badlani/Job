// Chart visualization functions

document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});

function initializeCharts() {
    // Candidate scores overview chart
    const scoreChartElem = document.getElementById('candidate-scores-chart');
    if (scoreChartElem) {
        createCandidateScoresChart(scoreChartElem);
    }
    
    // Skills match chart
    const skillsMatchElem = document.getElementById('skills-match-chart');
    if (skillsMatchElem) {
        const candidateId = skillsMatchElem.dataset.candidateId;
        if (candidateId) {
            createSkillsMatchChart(skillsMatchElem, candidateId);
        }
    }
    
    // Category distribution chart
    const categoryDistElem = document.getElementById('category-distribution-chart');
    if (categoryDistElem) {
        createCategoryDistributionChart(categoryDistElem);
    }
}

function createCandidateScoresChart(canvas) {
    // Fetch data from API endpoint
    fetch('/api/candidates/scores')
        .then(response => response.json())
        .then(data => {
            // Create the chart
            const ctx = canvas.getContext('2d');
            
            // Sort data by score descending
            data.sort((a, b) => b.score - a.score);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(item => item.name),
                    datasets: [{
                        label: 'Match Score (%)',
                        data: data.map(item => item.score),
                        backgroundColor: data.map(item => {
                            // Color based on score
                            if (item.score >= 75) return 'rgba(40, 167, 69, 0.7)';
                            if (item.score >= 50) return 'rgba(255, 193, 7, 0.7)';
                            return 'rgba(220, 53, 69, 0.7)';
                        }),
                        borderColor: data.map(item => {
                            if (item.score >= 75) return 'rgb(40, 167, 69)';
                            if (item.score >= 50) return 'rgb(255, 193, 7)';
                            return 'rgb(220, 53, 69)';
                        }),
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Match Score: ${context.raw}%`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching candidate scores:', error);
            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-danger';
            errorMsg.textContent = 'Failed to load candidate scores data.';
            canvas.parentNode.replaceChild(errorMsg, canvas);
        });
}

function createSkillsMatchChart(canvas, candidateId) {
    // Fetch data for a specific candidate
    fetch(`/api/candidates/${candidateId}/skills-match`)
        .then(response => response.json())
        .then(data => {
            const ctx = canvas.getContext('2d');
            
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: data.map(item => item.skill),
                    datasets: [{
                        label: 'Candidate Skill Level',
                        data: data.map(item => item.candidateLevel * 100),
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        pointBackgroundColor: 'rgb(54, 162, 235)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(54, 162, 235)'
                    }, {
                        label: 'Required Level',
                        data: data.map(item => item.requiredLevel * 100),
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgb(255, 99, 132)',
                        pointBackgroundColor: 'rgb(255, 99, 132)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(255, 99, 132)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: {
                                display: true
                            },
                            suggestedMin: 0,
                            suggestedMax: 100
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching skills match data:', error);
            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-danger';
            errorMsg.textContent = 'Failed to load skills match data.';
            canvas.parentNode.replaceChild(errorMsg, canvas);
        });
}

function createCategoryDistributionChart(canvas) {
    // Fetch data for match category distribution
    fetch('/api/candidates/category-distribution')
        .then(response => response.json())
        .then(data => {
            const ctx = canvas.getContext('2d');
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        data: Object.values(data),
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.7)',
                            'rgba(255, 193, 7, 0.7)',
                            'rgba(220, 53, 69, 0.7)'
                        ],
                        borderColor: [
                            'rgb(40, 167, 69)',
                            'rgb(255, 193, 7)',
                            'rgb(220, 53, 69)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} candidates (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching category distribution data:', error);
            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-danger';
            errorMsg.textContent = 'Failed to load category distribution data.';
            canvas.parentNode.replaceChild(errorMsg, canvas);
        });
}
