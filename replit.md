# Poetry to Music Application

## Overview

This application algorithmically translates poems into expressive musical compositions using natural language processing and MIDI generation. Users input poetry text, which is analyzed for structural elements (meter, rhythm, sentiment) and converted into corresponding musical patterns through algorithmic composition techniques.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM
- **Database**: SQLite (default) with PostgreSQL support via environment configuration
- **Core Processing**: Python-based poetry analysis and MIDI generation modules
- **Data Persistence**: Compositions stored with metadata including analysis results and generated file references

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **JavaScript**: Vanilla JS for form handling, validation, and user interactions
- **Styling**: Custom CSS with Bootstrap integration and Font Awesome icons
- **User Interface**: Single-page form-based interface with real-time feedback

### Processing Pipeline
1. **Input**: Poetry text and configuration (title, instruments)
2. **Analysis**: NLP processing using NLTK, spaCy, and TextBlob
3. **Translation**: Algorithmic mapping of poetic elements to musical parameters
4. **Generation**: MIDI file creation using MIDIUtil library
5. **Storage**: Composition metadata and file references persisted to database

## Key Components

### Poetry Analyzer (`poetry_analyzer.py`)
- **Natural Language Processing**: Sentiment analysis, meter detection, rhyme scheme identification
- **Structural Analysis**: Syllable counting, line structure, literary device recognition
- **Dependencies**: NLTK (punkt, cmudict), spaCy (en_core_web_sm), TextBlob
- **Output**: Comprehensive analysis dictionary for musical translation

### MIDI Generator (`midi_generator.py`)
- **Algorithmic Composition**: Maps poetic analysis to musical parameters
- **Instrument Support**: Piano, guitars, strings, woodwinds, percussion
- **Musical Elements**: Scales (major/minor keys), chord progressions, tempo mapping
- **File Generation**: Creates MIDI files using MIDIUtil library

### Database Models (`models.py`)
- **Composition Entity**: Stores poem text, analysis data, generated files, and metadata
- **Schema Design**: Supports versioning, instrument tracking, and musical parameters
- **Relationships**: Single-table design with JSON storage for complex analysis data

### Web Interface (`routes.py`, templates)
- **REST API**: JSON-based communication for analysis requests
- **File Serving**: MIDI file download functionality
- **Error Handling**: Comprehensive validation and user feedback
- **Recent Compositions**: Dashboard showing user's composition history

## Data Flow

1. **User Input**: Poetry text and instrument selection submitted via web form
2. **Validation**: Server-side validation of text content and instrument choices
3. **Analysis Phase**: Poetry analyzer processes text for structural and semantic elements
4. **Musical Translation**: Analysis results mapped to musical parameters (tempo, key, rhythm)
5. **MIDI Generation**: Algorithmic composition creates multi-track MIDI file
6. **Persistence**: Composition metadata and file references stored in database
7. **Response**: Generated MIDI file made available for download with analysis summary

## External Dependencies

### Python Libraries
- **Flask Stack**: Flask, Flask-SQLAlchemy for web framework and ORM
- **NLP Libraries**: NLTK, spaCy, TextBlob for poetry analysis
- **MIDI Generation**: MIDIUtil for musical file creation
- **Database**: SQLAlchemy with SQLite/PostgreSQL support

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library for enhanced UX
- **Vanilla JavaScript**: No additional JS framework dependencies

### Optional Dependencies
- **spaCy Model**: en_core_web_sm for advanced NLP (graceful degradation if unavailable)
- **NLTK Data**: Downloaded automatically (punkt tokenizer, CMU pronunciation dictionary)

## Deployment Strategy

### Environment Configuration
- **Database**: Configurable via DATABASE_URL environment variable
- **Session Security**: SESSION_SECRET for production security
- **Development Mode**: Debug mode enabled for local development
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### File Storage
- **MIDI Files**: Generated in application directory with title-based naming
- **Static Assets**: CSS/JS served via Flask static file handling
- **Database**: SQLite for development, PostgreSQL for production scalability

### Production Considerations
- **Database Pooling**: Connection pool with recycling and health checks
- **Logging**: Configurable logging levels for monitoring and debugging
- **Error Handling**: Comprehensive exception handling with user-friendly messages

## Changelog

```
Changelog:
- June 30, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```