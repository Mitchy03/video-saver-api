from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/get-video-url', methods=['POST'])
def get_video_url():
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', 'low')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best' if quality == 'high' else 'worst[ext=mp4]/worst',
            'noplaylist': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_url = info.get('url')
            if not video_url and info.get('formats'):
                for f in reversed(info['formats']):
                    if f.get('url'):
                        video_url = f['url']
                        break
            
            title = info.get('title', 'video')
            thumbnail = info.get('thumbnail', '')
            ext = info.get('ext', 'mp4')
            
            return jsonify({
                'success': True,
                'video_url': video_url,
                'title': title,
                'thumbnail': thumbnail,
                'ext': ext,
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
