from flask import Flask, render_template, request, jsonify
import requests
from textblob import TextBlob
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import re
from googletrans import Translator
from gtts import gTTS
import base64
from io import BytesIO

try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')
except:
    pass

app = Flask(__name__)
translator = Translator()

LANGUAGES = {
    'en': {'name': 'English', 'code': 'en'},
    'hi': {'name': 'Hindi', 'code': 'hi'},
    'ml': {'name': 'Malayalam', 'code': 'ml'}
}

def extract_text_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        content_selectors = [
            'article', '.article-body', '.post-content', '.entry-content',
            '.content', 'main', '.story-body', '.article-content'
        ]
        
        text = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                text = ' '.join([elem.get_text() for elem in elements])
                break
        
        if not text:
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
        
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

def summarize_text(text, num_sentences=3):
    try:
        sentences = sent_tokenize(text)
        
        if len(sentences) <= num_sentences:
            return text
        
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalnum() and word not in stop_words]
        
        word_freq = Counter(words)
        
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words_in_sentence = word_tokenize(sentence.lower())
            words_in_sentence = [word for word in words_in_sentence if word.isalnum()]
            
            score = sum(word_freq.get(word, 0) for word in words_in_sentence)
            word_count = len(words_in_sentence)
            sentence_scores[i] = score / word_count if word_count > 0 else 0
        
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
        top_sentences = sorted([x[0] for x in top_sentences])
        
        summary = ' '.join([sentences[i] for i in top_sentences])
        return summary
    
    except Exception as e:
        return f"Error in summarization: {str(e)}"

def analyze_bias(text):
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        polarity_label = "Positive" if polarity > 0.1 else "Negative" if polarity < -0.1 else "Neutral"
        subjectivity_label = "Highly Subjective" if subjectivity > 0.6 else "Moderately Subjective" if subjectivity > 0.3 else "Mostly Objective"

        return {
            'polarity': round(polarity, 3),
            'polarity_label': polarity_label,
            'subjectivity': round(subjectivity, 3),
            'subjectivity_label': subjectivity_label
        }
    
    except Exception as e:
        return {
            'polarity': 0,
            'polarity_label': 'Error',
            'subjectivity': 0,
            'subjectivity_label': f'Error: {str(e)}'
        }

def translate_text(text, target_language):
    try:
        if target_language == 'en':
            return text

        max_chunk_size = 4000
        if len(text) <= max_chunk_size:
            return translator.translate(text, dest=target_language).text

        sentences = sent_tokenize(text)
        translated_sentences = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk + sentence) <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                result = translator.translate(current_chunk.strip(), dest=target_language)
                translated_sentences.append(result.text)
                current_chunk = sentence + " "

        if current_chunk:
            result = translator.translate(current_chunk.strip(), dest=target_language)
            translated_sentences.append(result.text)

        return " ".join(translated_sentences)
    
    except Exception as e:
        return f"Translation error: {str(e)}"

def summary_to_audio(summary_text, language_code):
    try:
        
        gtts_lang = language_code
        if language_code == 'ml':
            gtts_lang = 'ml'  
        elif language_code == 'hi':
            gtts_lang = 'hi'
        else:
            gtts_lang = 'en'

        tts = gTTS(text=summary_text, lang=gtts_lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
        return audio_base64
    except Exception as e:
        return None

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        input_type = data.get('input_type')
        content = data.get('content', '').strip()
        language = data.get('language', 'en')

        if not content:
            return jsonify({'error': 'Please provide content to analyze'})

        if input_type == 'url':
            if not content.startswith(('http://', 'https://')):
                content = 'https://' + content
            text = extract_text_from_url(content)
            if text.startswith('Error'):
                return jsonify({'error': text})
        else:
            text = content

        if len(text.strip()) < 50:
            return jsonify({'error': 'Text is too short for analysis. Please provide at least 50 characters.'})

        summary = summarize_text(text)
        bias_analysis = analyze_bias(text)

        if language != 'en':
            summary = translate_text(summary, language)
            bias_labels = {
                'polarity_label': translate_text(bias_analysis['polarity_label'], language),
                'subjectivity_label': translate_text(bias_analysis['subjectivity_label'], language)
            }
            bias_analysis.update(bias_labels)
            static_translations = {
                'summary_title': translate_text('Summary', language),
                'bias_title': translate_text('Bias Analysis', language),
                'polarity_title': translate_text('Polarity', language),
                'subjectivity_title': translate_text('Subjectivity', language)
            }
        else:
            static_translations = {
                'summary_title': 'Summary',
                'bias_title': 'Bias Analysis',
                'polarity_title': 'Polarity',
                'subjectivity_title': 'Subjectivity'
            }

        
        audio_base64 = summary_to_audio(summary, language)

        return jsonify({
            'summary': summary,
            'bias': bias_analysis,
            'translations': static_translations,
            'original_length': len(text),
            'summary_length': len(summary),
            'audio_base64': audio_base64
        })

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

@app.route('/tts', methods=['POST'])
def tts():
    try:
        data = request.json
        text = data.get('text', '')
        lang = data.get('lang', 'en')  

        if not text.strip():
            return jsonify({'error': 'No text provided for speech.'}), 400



        tts = gTTS(text=text, lang=lang)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        return send_file(
            mp3_fp,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='summary.mp3'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
