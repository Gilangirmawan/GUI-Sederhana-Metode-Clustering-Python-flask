import os
import json
import io
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Inisialisasi aplikasi Flask
with open('static/config.json', 'r') as f:
    config = json.load(f)

app = Flask(config['app_name'])
UPLOAD_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route untuk halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# Route untuk mengupload file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    try:
        df = pd.read_csv(filepath)
        # Generate preview table with Bootstrap styling
        preview = df.head().to_html(classes='table table-striped table-bordered', border=0)
        return jsonify({
            'success': True,
            'preview': preview,
            'filename': file.filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route untuk clustering
@app.route('/cluster', methods=['POST'])
def run_clustering():
    try:
        data = request.get_json()
        filename = data.get('filename')
        min_k = int(data.get('min_k', 2))
        max_k = int(data.get('max_k', 10))
        
        # Validasi input
        if min_k >= max_k:
            return jsonify({'error': 'min_k must be less than max_k'}), 400
        
        # Load data
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        df = pd.read_csv(filepath)
        
        # Preprocessing - hanya ambil kolom numerik
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) == 0:
            return jsonify({'error': 'No numeric columns found in dataset'}), 400
            
        df_numeric = df[numeric_cols]
        
        # Standardisasi data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_numeric)
        
        # Hitung inertia untuk setiap K
        inertias = {}
        for k in range(min_k, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(scaled_data)
            inertias[k] = kmeans.inertia_
        
        # Buat elbow plot
        plt.figure(figsize=(10, 6))
        plt.plot(list(inertias.keys()), list(inertias.values()), 'bx-')
        plt.xlabel('Number of clusters (K)')
        plt.ylabel('Inertia')
        plt.title('Elbow Method For Optimal K')
        plt.xticks(list(inertias.keys()))
        plt.grid(True)
        
        # Konversi plot ke base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return jsonify({
            'success': True,
            'plot': plot_data,
            'inertias': inertias,
            'message': 'Clustering completed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)