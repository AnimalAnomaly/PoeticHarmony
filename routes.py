import os
import json
import logging
from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app, db
from models import Composition
from poetry_analyzer import PoetryAnalyzer
from midi_generator import MIDIGenerator

# Initialize components
analyzer = PoetryAnalyzer()
midi_gen = MIDIGenerator()

@app.route('/')
def index():
    """Main page"""
    recent_compositions = Composition.query.order_by(Composition.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_compositions=recent_compositions)

@app.route('/analyze', methods=['POST'])
def analyze_poem():
    """Analyze poem and generate MIDI"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        poem_text = data.get('poem_text', '').strip()
        title = data.get('title', 'Untitled Poem').strip()
        selected_instruments = data.get('instruments', ['piano'])
        
        if not poem_text:
            return jsonify({'error': 'Please provide poem text'}), 400
        
        if not title:
            title = 'Untitled Poem'
        
        # Validate instruments
        valid_instruments = ['piano', 'acoustic_guitar', 'electric_guitar', 'strings', 'violin', 'cello', 'flute', 'clarinet', 'drums']
        instruments = [inst for inst in selected_instruments if inst in valid_instruments]
        if not instruments:
            instruments = ['piano']
        
        logging.info(f"Analyzing poem: {title}")
        
        # Analyze the poem
        analysis = analyzer.analyze_poem(poem_text)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 400
        
        logging.info(f"Analysis completed. Generating MIDI with instruments: {instruments}")
        
        # Generate MIDI
        midi_filename = midi_gen.generate_composition(
            analysis, 
            title=title, 
            instruments=instruments
        )
        
        # Save to database
        composition = Composition(
            title=title,
            poem_text=poem_text,
            midi_filename=midi_filename,
            analysis_data=json.dumps(analysis),
            instruments=','.join(instruments),
            tempo=analysis.get('tempo_suggestion', 120),
            key_signature=analysis.get('key_suggestion', 'C'),
            time_signature=analysis.get('time_signature', '4/4')
        )
        
        db.session.add(composition)
        db.session.commit()
        
        logging.info(f"Composition saved with ID: {composition.id}")
        
        return jsonify({
            'success': True,
            'composition_id': composition.id,
            'analysis': analysis,
            'midi_filename': midi_filename,
            'message': 'Poem analyzed and music generated successfully!'
        })
        
    except Exception as e:
        logging.error(f"Error in analyze_poem: {str(e)}")
        return jsonify({'error': f'An error occurred while processing your poem: {str(e)}'}), 500

@app.route('/download/<int:composition_id>')
def download_midi(composition_id):
    """Download MIDI file"""
    try:
        composition = Composition.query.get_or_404(composition_id)
        midi_path = os.path.join('static', 'midi', composition.midi_filename)
        
        if not os.path.exists(midi_path):
            flash('MIDI file not found.', 'error')
            return redirect(url_for('index'))
        
        return send_file(
            midi_path,
            as_attachment=True,
            download_name=f"{composition.title}.mid",
            mimetype='audio/midi'
        )
        
    except Exception as e:
        logging.error(f"Error downloading MIDI: {str(e)}")
        flash('Error downloading file.', 'error')
        return redirect(url_for('index'))

@app.route('/composition/<int:composition_id>')
def view_composition(composition_id):
    """View composition details"""
    composition = Composition.query.get_or_404(composition_id)
    
    try:
        analysis_data = json.loads(composition.analysis_data) if composition.analysis_data else {}
    except:
        analysis_data = {}
    
    return render_template('composition.html', composition=composition, analysis=analysis_data)

@app.route('/api/midi/<filename>')
def serve_midi(filename):
    """Serve MIDI file for playback"""
    try:
        midi_path = os.path.join('static', 'midi', filename)
        if os.path.exists(midi_path):
            return send_file(midi_path, mimetype='audio/midi')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logging.error(f"Error serving MIDI: {str(e)}")
        return jsonify({'error': 'Error serving file'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
