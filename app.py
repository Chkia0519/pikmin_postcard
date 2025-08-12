from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, sqlite3
from werkzeug.utils import secure_filename #將文件名字自動轉換為可適用字符
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DATABASE'] = 'database2.db'

# 初始化資料庫
def init_db():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                address TEXT,
                whereg TEXT,
                latitude REAL,
                longitude REAL
            )
        """)

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image'] #
        whereget = request.form.get('where') #哪裡得到明信片的
        address = request.form.get('address') #地址
        lat = request.form.get('latitude') #經緯度
        lon = request.form.get('longitude') #經緯度

        if address and (not lat or not lon):
            try:
                geocode_url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
                response = requests.get(geocode_url).json()
                if response:
                    lat = response[0]['lat']
                    lon = response[0]['lon']
            except:
                lat, lon = None, None

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        with sqlite3.connect(app.config['DATABASE']) as conn:
            conn.execute("INSERT INTO uploads (filename, address, whereg, latitude, longitude) VALUES (?, ?, ?, ?, ?)", 
                         (filename, whereget, address, lat, lon))

        return redirect(url_for('index'))

    with sqlite3.connect(app.config['DATABASE']) as conn:
        uploads = conn.execute("SELECT * FROM uploads").fetchall()
    return render_template('index.html',uploads=uploads )

@app.route('/updata')
def updata():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        uploads = conn.execute("SELECT * FROM uploads").fetchall()
    return render_template('updata.html',uploads=uploads )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
