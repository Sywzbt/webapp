import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

def init_db():
    """初始化資料庫"""
    conn = sqlite3.connect('membership.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            iid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            birthdate TEXT
        )
    ''')
    
    # 插入初始資料
    c.execute('''
        INSERT OR IGNORE INTO members (username, email, password, phone, birthdate)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@example.com', 'admin123', '0912345678', '1990-01-01'))
    
    conn.commit()
    conn.close()

@app.template_filter('add_stars')
def add_stars(s):
    """為用戶名添加星號的自訂過濾器"""
    return f'★{s}★'

@app.route('/')
def index():
    """首頁路由"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """註冊路由"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        birthdate = request.form.get('birthdate')
        
        if not all([username, email, password]):
            return render_template('error.html', message='請輸入用戶名、電子郵件和密碼')
        
        conn = sqlite3.connect('membership.db')
        c = conn.cursor()
        
        # 檢查用戶名是否已存在
        c.execute('SELECT 1 FROM members WHERE username = ?', (username,))
        if c.fetchone():
            conn.close()
            return render_template('error.html', message='用戶名已存在')
        
        # 檢查電子郵件是否已存在
        c.execute('SELECT 1 FROM members WHERE email = ?', (email,))
        if c.fetchone():
            conn.close()
            return render_template('error.html', message='電子郵件已被使用')
        
        # 插入新用戶
        c.execute('''
            INSERT INTO members (username, email, password, phone, birthdate)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password, phone, birthdate))
        
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登入路由"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([email, password]):
            return render_template('error.html', message='請輸入電子郵件和密碼')
        
        conn = sqlite3.connect('membership.db')
        c = conn.cursor()
        c.execute('SELECT iid, username FROM members WHERE email = ? AND password = ?',
                 (email, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            return render_template('welcome.html', username=user[1], iid=user[0])
        else:
            return render_template('error.html', message='電子郵件或密碼錯誤')
    
    return render_template('login.html')

@app.route('/edit_profile/<int:iid>', methods=['GET', 'POST'])
def edit_profile(iid):
    """修改基本資料路由"""
    conn = sqlite3.connect('membership.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        birthdate = request.form.get('birthdate')
        
        if not all([email, password]):
            conn.close()
            return render_template('error.html', message='請輸入電子郵件和密碼')
        
        # 檢查電子郵件是否已被其他用戶使用
        c.execute('SELECT 1 FROM members WHERE email = ? AND iid != ?', (email, iid))
        if c.fetchone():
            conn.close()
            return render_template('error.html', message='電子郵件已被使用')
        
        # 更新用戶資料
        c.execute('''
            UPDATE members 
            SET email = ?, password = ?, phone = ?, birthdate = ?
            WHERE iid = ?
        ''', (email, password, phone, birthdate, iid))
        
        conn.commit()
        conn.close()
        return redirect(url_for('welcome', iid=iid))
    
    # 獲取用戶資料
    c.execute('SELECT username, email, password, phone, birthdate FROM members WHERE iid = ?', (iid,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return render_template('error.html', message='用戶不存在')
    
    return render_template('edit_profile.html', 
                         username=user[0],
                         email=user[1],
                         password=user[2],
                         phone=user[3],
                         birthdate=user[4],
                         iid=iid)

@app.route('/delete/<int:iid>')
def delete_user(iid):
    """刪除用戶路由"""
    conn = sqlite3.connect('membership.db')
    c = conn.cursor()
    c.execute('DELETE FROM members WHERE iid = ?', (iid,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/welcome/<int:iid>')
def welcome(iid):
    """歡迎頁面路由"""
    conn = sqlite3.connect('membership.db')
    c = conn.cursor()
    c.execute('SELECT username FROM members WHERE iid = ?', (iid,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return render_template('error.html', message='用戶不存在')
    
    return render_template('welcome.html', username=user[0], iid=iid)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000) 