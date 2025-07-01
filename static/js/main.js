// Poetry to Music - Main JavaScript functionality

class PoetryToMusic {
    constructor() {
        this.currentComposition = null;
        this.isAnalyzing = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.validateForm();
    }

    bindEvents() {
        // Form submission
        const form = document.getElementById('poemForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Text area input validation
        const poemText = document.getElementById('poemText');
        if (poemText) {
            poemText.addEventListener('input', () => this.validateForm());
        }

        // Instrument selection validation
        const instrumentCheckboxes = document.querySelectorAll('input[type="checkbox"][id^="inst_"]');
        instrumentCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.validateInstruments());
        });

        // Download button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'downloadBtn' || e.target.closest('#downloadBtn')) {
                this.handleDownload();
            }
            if (e.target.id === 'playBtn' || e.target.closest('#playBtn')) {
                this.handlePlay();
            }
        });
    }

    validateForm() {
        const poemText = document.getElementById('poemText');
        const submitBtn = document.querySelector('button[type="submit"]');
        
        if (poemText && submitBtn) {
            const isValid = poemText.value.trim().length > 0;
            submitBtn.disabled = !isValid || this.isAnalyzing;
        }
    }

    validateInstruments() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][id^="inst_"]');
        const checkedBoxes = Array.from(checkboxes).filter(cb => cb.checked);
        
        if (checkedBoxes.length === 0) {
            // Auto-select piano if no instruments selected
            const pianoCheckbox = document.getElementById('inst_piano');
            if (pianoCheckbox) {
                pianoCheckbox.checked = true;
            }
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (this.isAnalyzing) return;

        const formData = this.getFormData();
        if (!formData) return;

        this.showLoading();
        this.hideResults();
        this.hideError();

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.currentComposition = result;
                this.showResults(result);
            } else {
                this.showError(result.error || 'An error occurred while analyzing your poem.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Network error occurred. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    getFormData() {
        const poemText = document.getElementById('poemText');
        const poemTitle = document.getElementById('poemTitle');
        
        if (!poemText || !poemText.value.trim()) {
            this.showError('Please enter poem text.');
            return null;
        }

        // Get selected instruments
        const instrumentCheckboxes = document.querySelectorAll('input[type="checkbox"][id^="inst_"]:checked');
        const instruments = Array.from(instrumentCheckboxes).map(cb => cb.value);

        if (instruments.length === 0) {
            instruments.push('piano'); // Default fallback
        }

        return {
            poem_text: poemText.value.trim(),
            title: poemTitle ? poemTitle.value.trim() || 'Untitled Poem' : 'Untitled Poem',
            instruments: instruments
        };
    }

    showLoading() {
        this.isAnalyzing = true;
        const spinner = document.getElementById('loadingSpinner');
        const submitBtn = document.querySelector('button[type="submit"]');
        
        if (spinner) spinner.style.display = 'block';
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
        }
    }

    hideLoading() {
        this.isAnalyzing = false;
        const spinner = document.getElementById('loadingSpinner');
        const submitBtn = document.querySelector('button[type="submit"]');
        
        if (spinner) spinner.style.display = 'none';
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Music';
        }
    }

    showResults(result) {
        const resultsDiv = document.getElementById('results');
        const analysisDiv = document.getElementById('analysisResults');
        
        if (!resultsDiv || !analysisDiv) return;

        const analysis = result.analysis;
        const analysisHtml = this.generateAnalysisHtml(analysis);
        
        analysisDiv.innerHTML = analysisHtml;
        resultsDiv.style.display = 'block';

        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    generateAnalysisHtml(analysis) {
        const sentiment = analysis.sentiment || {};
        const mood = sentiment.mood || 'neutral';
        const moodIcon = this.getMoodIcon(mood);
        const moodColor = this.getMoodColor(mood);

        return `
            <div class="row">
                <div class="col-md-6">
                    <h5><i class="fas fa-chart-line me-2"></i>Poem Analysis</h5>
                    <div class="analysis-item">
                        <strong>Lines:</strong> ${analysis.line_count || 0}
                        <small class="text-muted d-block">Each line becomes a musical phrase</small>
                    </div>
                    <div class="analysis-item">
                        <strong>Total Syllables:</strong> ${analysis.total_syllables || 0}
                        <small class="text-muted d-block">Determines overall composition length</small>
                    </div>
                    <div class="analysis-item">
                        <strong>Meter:</strong> ${this.formatMeter(analysis.meter)}
                        <small class="text-muted d-block">${this.getMeterExplanation(analysis.meter)}</small>
                    </div>
                    <div class="analysis-item">
                        <strong>Rhyme Scheme:</strong> ${analysis.rhyme_scheme || 'Free'}
                        <small class="text-muted d-block">${this.getRhymeExplanation(analysis.rhyme_scheme)}</small>
                    </div>
                </div>
                <div class="col-md-6">
                    <h5><i class="fas fa-music me-2"></i>Musical Translation</h5>
                    <div class="analysis-item">
                        <strong>Mood:</strong> 
                        <span class="text-${moodColor}">
                            <i class="${moodIcon} me-1"></i>${mood.charAt(0).toUpperCase() + mood.slice(1)}
                        </span>
                        <small class="text-muted d-block">${this.getMoodMusicalExplanation(mood)}</small>
                    </div>
                    <div class="analysis-item">
                        <strong>Key:</strong> <span class="musical-info">${analysis.key_suggestion || 'C'}</span>
                        <small class="text-muted d-block">${this.getKeyExplanation(analysis.key_suggestion)}</small>
                    </div>
                    <div class="analysis-item">
                        <strong>Tempo:</strong> <span class="musical-info">${analysis.tempo_suggestion || 120} BPM</span>
                        <small class="text-muted d-block">${this.getTempoExplanation(analysis.tempo_suggestion)}</small>
                    </div>
                    <div class="analysis-item">
                        <strong>Time Signature:</strong> <span class="musical-info">${analysis.time_signature || '4/4'}</span>
                        <small class="text-muted d-block">Sets the rhythmic foundation</small>
                    </div>
                </div>
            </div>
            
            ${this.generateLiteraryDevicesHtml(analysis.literary_devices)}
            
            ${this.generateDetailedAnalysisHtml(analysis)}
        `;
    }

    generateLiteraryDevicesHtml(devices) {
        if (!devices) return '';

        const detectedDevices = [];
        Object.keys(devices).forEach(deviceKey => {
            const device = devices[deviceKey];
            if (device && device.detected) {
                detectedDevices.push({
                    name: this.formatDeviceName(deviceKey),
                    explanation: device.explanation,
                    musical_impact: device.musical_impact
                });
            }
        });

        if (detectedDevices.length === 0) return '';

        return `
            <div class="mt-4">
                <h5><i class="fas fa-palette me-2"></i>Literary Devices & Musical Impact</h5>
                <div class="accordion" id="literaryDevicesAccordion">
                    ${detectedDevices.map((device, index) => `
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="heading${index}">
                                <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" 
                                        data-bs-toggle="collapse" data-bs-target="#collapse${index}">
                                    <span class="badge bg-info me-2">${device.name}</span>
                                    Literary Device Detected
                                </button>
                            </h2>
                            <div id="collapse${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                                 data-bs-parent="#literaryDevicesAccordion">
                                <div class="accordion-body">
                                    <p><strong>What it is:</strong> ${device.explanation}</p>
                                    <p class="text-info mb-0"><strong>Musical Translation:</strong> ${device.musical_impact}</p>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getMoodIcon(mood) {
        const icons = {
            'positive': 'fas fa-smile',
            'negative': 'fas fa-frown',
            'neutral': 'fas fa-meh'
        };
        return icons[mood] || 'fas fa-meh';
    }

    getMoodColor(mood) {
        const colors = {
            'positive': 'success',
            'negative': 'danger',
            'neutral': 'secondary'
        };
        return colors[mood] || 'secondary';
    }

    formatMeter(meter) {
        if (!meter) return 'Free verse';
        return meter.replace('_', ' ').split(' ').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    formatDeviceName(deviceKey) {
        const names = {
            'alliteration': 'Alliteration',
            'repetition': 'Repetition',
            'metaphor_simile': 'Metaphor/Simile',
            'imagery': 'Imagery',
            'assonance': 'Assonance'
        };
        return names[deviceKey] || deviceKey;
    }

    getMeterExplanation(meter) {
        const explanations = {
            'iambic': 'Creates steady, marching rhythm (da-DUM da-DUM)',
            'trochaic': 'Creates falling rhythm (DUM-da DUM-da)',
            'free_verse': 'Allows flexible, experimental rhythms',
            'regular': 'Produces consistent, structured musical phrases'
        };
        return explanations[meter] || 'Influences rhythmic patterns';
    }

    getRhymeExplanation(rhyme) {
        const explanations = {
            'ABAB': 'Creates alternating harmonic patterns',
            'AABB': 'Produces paired harmonic progressions',
            'free': 'Allows varied harmonic exploration',
            'none': 'Focuses on melodic rather than harmonic structure'
        };
        return explanations[rhyme] || 'Affects harmonic structure';
    }

    getMoodMusicalExplanation(mood) {
        const explanations = {
            'positive': 'Translated to major keys and brighter tempos',
            'negative': 'Expressed through minor keys and slower tempos',
            'neutral': 'Balanced approach with moderate musical elements'
        };
        return explanations[mood] || 'Influences overall musical character';
    }

    getKeyExplanation(key) {
        const explanations = {
            'C': 'Major key - bright, optimistic sound',
            'Am': 'Minor key - contemplative, melancholic sound',
            'G': 'Major key - warm, uplifting character',
            'Em': 'Minor key - gentle, introspective mood',
            'F': 'Major key - peaceful, stable feeling',
            'Dm': 'Minor key - serious, dramatic tone'
        };
        return explanations[key] || 'Sets the emotional foundation';
    }

    getTempoExplanation(tempo) {
        if (tempo >= 140) return 'Fast tempo - energetic, exciting feel';
        if (tempo >= 120) return 'Moderate tempo - comfortable, steady pace';
        if (tempo >= 100) return 'Relaxed tempo - calm, thoughtful mood';
        return 'Slow tempo - contemplative, meditative feel';
    }

    generateDetailedAnalysisHtml(analysis) {
        const syllableCounts = analysis.syllable_counts || [];
        const avgSyllables = syllableCounts.length > 0 ? 
            (syllableCounts.reduce((a, b) => a + b, 0) / syllableCounts.length).toFixed(1) : 0;

        return `
            <div class="mt-4">
                <h5><i class="fas fa-microscope me-2"></i>Detailed Analysis</h5>
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Syllable Distribution</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Average syllables per line:</strong> ${avgSyllables}</p>
                                <p><strong>Line lengths:</strong> ${syllableCounts.join(', ')}</p>
                                <small class="text-muted">Each syllable becomes a musical note, creating phrases of varying lengths</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Sentiment Analysis</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Emotional polarity:</strong> ${this.formatPolarity(analysis.sentiment?.polarity)}</p>
                                <p><strong>Subjectivity:</strong> ${this.formatSubjectivity(analysis.sentiment?.subjectivity)}</p>
                                <small class="text-muted">These values determine musical key choices and dynamic expression</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    formatPolarity(polarity) {
        if (polarity === undefined) return 'Neutral';
        if (polarity > 0.3) return `Positive (${polarity.toFixed(2)})`;
        if (polarity < -0.3) return `Negative (${polarity.toFixed(2)})`;
        return `Neutral (${polarity.toFixed(2)})`;
    }

    formatSubjectivity(subjectivity) {
        if (subjectivity === undefined) return 'Balanced';
        if (subjectivity > 0.7) return `Highly subjective (${subjectivity.toFixed(2)})`;
        if (subjectivity < 0.3) return `Objective (${subjectivity.toFixed(2)})`;
        return `Moderately subjective (${subjectivity.toFixed(2)})`;
    }

    hideResults() {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) resultsDiv.style.display = 'none';
    }

    showError(message) {
        const errorDiv = document.getElementById('errorDisplay');
        const errorMsg = document.getElementById('errorMessage');
        
        if (errorDiv && errorMsg) {
            errorMsg.textContent = message;
            errorDiv.style.display = 'block';
            errorDiv.scrollIntoView({ behavior: 'smooth' });
        }
    }

    hideError() {
        const errorDiv = document.getElementById('errorDisplay');
        if (errorDiv) errorDiv.style.display = 'none';
    }

    handleDownload() {
        if (!this.currentComposition) return;
        
        const compositionId = this.currentComposition.composition_id;
        window.location.href = `/download/${compositionId}`;
    }

    handlePlay() {
        if (!this.currentComposition) return;
        
        const midiFilename = this.currentComposition.midi_filename;
        this.showMessage('MIDI playback in browser is limited. Please download the file to play in your preferred music software.', 'info');
        
        // For now, we'll show a message since MIDI playback in browsers is complex
        // In a full implementation, you'd use Web Audio API or a MIDI library
    }

    showMessage(message, type = 'info') {
        // Create temporary message
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PoetryToMusic();
});

// Utility functions for future enhancements
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PoetryToMusic;
}
