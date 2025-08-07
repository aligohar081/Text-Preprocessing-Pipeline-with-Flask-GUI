# app.py
from flask import Flask, render_template, request, jsonify, send_file
from text_preprocessing import TextPreprocessor
import io
import csv
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize preprocessor
preprocessor = TextPreprocessor()

@app.route('/')
def index():
    """Main page with the preprocessing interface."""
    return render_template('index.html')

@app.route('/preprocess', methods=['POST'])
def preprocess_text():
    """Process text based on selected options."""
    try:
        data = request.get_json()
        
        text = data.get('text', '')
        if not text.strip():
            return jsonify({'error': 'Please provide text to preprocess'}), 400
        
        # Get preprocessing options
        options = {
            'lowercase': data.get('lowercase', True),
            'remove_punct': data.get('removePunctuation', True),
            'remove_special': data.get('removeSpecial', False),
            'tokenize_text': data.get('tokenize', True),
            'remove_stops': data.get('removeStopwords', True),
            'lemmatize_text': data.get('lemmatize', True),
            'stem_text': data.get('stem', False)
        }
        
        result = preprocessor.preprocess(text, **options)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads for batch processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        
        # Read file content
        if filename.endswith('.txt'):
            content = file.read().decode('utf-8')
            texts = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Get preprocessing options from form
            options = {
                'lowercase': request.form.get('lowercase') == 'true',
                'remove_punct': request.form.get('removePunctuation') == 'true',
                'remove_special': request.form.get('removeSpecial') == 'true',
                'tokenize_text': request.form.get('tokenize') == 'true',
                'remove_stops': request.form.get('removeStopwords') == 'true',
                'lemmatize_text': request.form.get('lemmatize') == 'true',
                'stem_text': request.form.get('stem') == 'true'
            }
            
            results = preprocessor.process_batch(texts, **options)
            
            return jsonify({
                'success': True,
                'results': results,
                'count': len(results)
            })
            
        elif filename.endswith('.csv'):
            content = file.read().decode('utf-8')
            text_column = request.form.get('textColumn', 'text')
            
            options = {
                'lowercase': request.form.get('lowercase') == 'true',
                'remove_punct': request.form.get('removePunctuation') == 'true',
                'remove_special': request.form.get('removeSpecial') == 'true',
                'tokenize_text': request.form.get('tokenize') == 'true',
                'remove_stops': request.form.get('removeStopwords') == 'true',
                'lemmatize_text': request.form.get('lemmatize') == 'true',
                'stem_text': request.form.get('stem') == 'true'
            }
            
            df_result = preprocessor.process_csv_content(content, text_column, **options)
            
            return jsonify({
                'success': True,
                'results': df_result.to_dict('records'),
                'count': len(df_result)
            })
        
        else:
            return jsonify({'error': 'Only .txt and .csv files are supported'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<format>')
def download_results(format):
    """Download processed results in specified format."""
    # This would need to be implemented with session storage or database
    # For now, return a sample response
    return jsonify({'error': 'Download functionality requires session storage implementation'}), 501

if __name__ == '__main__':
    app.run(debug=True)