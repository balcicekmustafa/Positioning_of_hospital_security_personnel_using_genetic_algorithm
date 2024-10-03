from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import random
import pandas as pd
from deap import base, creator, tools, algorithms
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
app = Flask(__name__)
app.secret_key='your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# MySQL bağlantısı
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="M.mustafa27",  # Buraya veritabanı şifrenizi yazın
        database="hospital_security"
    )
    return conn

@app.before_request
def before_request():
    g.conn = get_db_connection()
    g.cursor = g.conn.cursor(buffered=True)

@app.teardown_request
def teardown_request(exception):
    cursor = getattr(g, 'cursor', None)
    if cursor is not None:
        cursor.close()
    conn = getattr(g, 'conn', None)
    if conn is not None:
        conn.close()

class Admin(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(admin_id):
    # İstek bağlamı dışında olduğumuz için kendi bağlantımızı oluşturuyoruz
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM Admin WHERE id = %s", (admin_id,))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()
    if admin:
        return Admin(admin[0], admin[1])
    return None

# Giriş sayfası rotası ve veritabanındaki kullanıcı adı ve şifre eşleşmesi ile giriş yapabilme.
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        g.cursor.execute("SELECT id, password FROM Admin WHERE username = %s", (username,))
        admin = g.cursor.fetchone()

        if admin and admin[1] == password:
            admin_user = Admin(admin[0], username)
            login_user(admin_user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Şifre veya Kullanıcı Adı Hatalı!!!', 'danger')

    return render_template('admin_login.html')

# Admin sayfası için rota
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Admin ekleme rotası
@app.route('/add_admin', methods=['POST'])
@login_required
def add_admin():
    new_username = request.form['username']
    new_password = request.form['password']

    g.cursor.execute("INSERT INTO Admin (username, password) VALUES (%s, %s)", (new_username, new_password))
    g.conn.commit()
    flash('Yeni Admin Başarıyla Eklendi.', 'success')
    return redirect(url_for('admin_dashboard'))

# Çıkış rotası
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin_login'))

# Yapay veri üretimi
def generate_fake_data():
    # İstek bağlamı dışında olduğumuz için kendi bağlantımızı oluşturuyoruz
    conn = get_db_connection()
    cursor = conn.cursor()

    # Olay türleri ekleme
    olay_turleri = [
        ('Sözlü tartışma', 1),
        ('Kavga', 2),
        ('Kesici-delici alet kullanımı', 3),
        ('Ateşli silah kullanımı', 4)
    ]
    for tur, carpan in olay_turleri:
        cursor.execute("INSERT INTO OlayTuru (tur, carpan) VALUES (%s, %s)", (tur, carpan))

    # Bölge ekleme
    bolgeler = ['Acil Servis', 'Cerrahi', 'Yoğun Bakım', 'Poliklinik', 'Yemekhane']
    for bolge in bolgeler:
        cursor.execute("INSERT INTO Bolge (ad) VALUES (%s)", (bolge,))

    # Personel ekleme
    personeller = ['Güvenlik 1', 'Güvenlik 2', 'Güvenlik 3', 'Güvenlik 4', 'Güvenlik 5']
    for personel in personeller:
        sure = random.uniform(3.0, 10.0)  # Müdahale süresi
        basari = random.randint(5, 10)  # Başarı puanı
        cursor.execute("INSERT INTO Personel (ad, sure, basari) VALUES (%s, %s, %s)", (personel, sure, basari))

    # Olay ekleme
    cursor.execute("SELECT id FROM Bolge")
    bolge_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id, carpan FROM OlayTuru")
    olay_turu_data = cursor.fetchall()

    for bolge_id in bolge_ids:
        olay_siddeti = random.randint(1, 10)
        olay_sikligi = random.randint(5, 20)
        for _ in range(olay_sikligi):
            olay_turu_id, carpan = random.choice(olay_turu_data)
            zaman = random.randint(1, 24)
            cursor.execute("INSERT INTO Olay (bolge_id, olay_turu_id, olay_siddeti, zaman) VALUES (%s, %s, %s, %s)",
                           (bolge_id, olay_turu_id, olay_siddeti, zaman))

    conn.commit()
    cursor.close()
    conn.close()

# Yapay veri oluşturma rotası
@app.route('/generate_fake_data')
@login_required
def generate_fake_data_route():
    generate_fake_data()
    flash('Yapay veri başarıyla oluşturuldu.', 'success')
    return redirect(url_for('index'))

def run_genetic_algorithm():
    # Verileri hazırlayın
    g.cursor.execute("""
        SELECT Olay.bolge_id, Olay.olay_siddeti, OlayTuru.carpan, Bolge.tehlike_seviyesi 
        FROM Olay 
        JOIN Bolge ON Olay.bolge_id = Bolge.id
        JOIN OlayTuru ON Olay.olay_turu_id = OlayTuru.id
    """)
    olaylar = g.cursor.fetchall()

    olay_df = pd.DataFrame(olaylar, columns=['Bölge ID', 'Olay Şiddeti', 'Çarpan', 'Tehlike Seviyesi'])
    olay_df['Toplam Şiddet'] = olay_df['Olay Şiddeti'] * olay_df['Çarpan']

    g.cursor.execute("SELECT id, sure, basari FROM Personel")
    personeller = g.cursor.fetchall()
    personel_df = pd.DataFrame(personeller, columns=['id', 'Müdahale Süresi', 'Başarı'])

    num_bolge = len(olay_df['Bölge ID'].unique())
    num_personel = len(personel_df)

    def fitness(individual):
        score = 0
        if len(set(individual)) != num_bolge:
            return -float('inf'),  # Geçersiz birey

        for i in range(num_bolge):
            assigned_personel = individual[i]
            personel_basari = personel_df.iloc[assigned_personel]['Başarı']
            personel_sure = personel_df.iloc[assigned_personel]['Müdahale Süresi']
            bolge_siddeti = olay_df['Toplam Şiddet'].iloc[i]
            bolge_tehlike = olay_df['Tehlike Seviyesi'].iloc[i]

            score += (personel_basari - personel_sure) * bolge_siddeti * bolge_tehlike
        return score,

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, range(num_personel), num_bolge)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", fitness)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=50)
    algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=40, verbose=False)

    best_individual = tools.selBest(pop, k=1)[0]
    return best_individual, best_individual.fitness.values[0]
@app.route('/run_genetic_algorithm')
@login_required
def run_genetic_algorithm_route():
    best_individual, fitness_score = run_genetic_algorithm()
    print("Best individual:", best_individual)
    print("Fitness score:", fitness_score)

    # Bölge ve personel listelerini al
    g.cursor.execute("SELECT id, tehlike_seviyesi FROM Bolge")
    bolge_list = [row for row in g.cursor.fetchall()]
    g.cursor.execute("SELECT id FROM Personel")
    personel_list = [row[0] for row in g.cursor.fetchall()]

    # Personel atamalarını güncelle
    update_personel_atamalari(best_individual, bolge_list, personel_list)

    flash('Genetik algoritma başarıyla çalıştırıldı ve personel atamaları güncellendi.', 'success')
    return redirect(url_for('index'))
def update_personel_atamalari(best_individual, bolge_list, personel_list):
    g.cursor.execute("DELETE FROM PersonelAtama")  # önceki atamayı silme
    assigned_personel = set()  # yeni atananı işaretleme

    # Güvenliklerin performans sıralaması
    g.cursor.execute("SELECT id FROM Personel ORDER BY basari DESC")
    sorted_personel = [row[0] for row in g.cursor.fetchall()]

    # Bölgelerin tehlike seviyesine göre sıralanması
    sorted_bolge_list = sorted(bolge_list, key=lambda x: x[1], reverse=True)  # Sort by tehlike_seviyesi

    bolge_personel_count = {bolge[0]: 0 for bolge in sorted_bolge_list}

    # Her bölgede en az bir güvenlik olmasını sağlayan kod
    for i, bolge in enumerate(sorted_bolge_list):
        personel = sorted_personel[i % len(sorted_personel)]
        g.cursor.execute("INSERT INTO PersonelAtama (personel_id, bolge_id) VALUES (%s, %s)", (personel, bolge[0]))
        bolge_personel_count[bolge[0]] += 1
        assigned_personel.add(personel)

    # Kalan personellerin en tehlikeli bölgeye dağıtılması için olan kod
    remaining_personel = [p for p in sorted_personel if p not in assigned_personel]

    for personel in remaining_personel:
        target_bolge = min(sorted_bolge_list, key=lambda x: bolge_personel_count[x[0]])
        g.cursor.execute("INSERT INTO PersonelAtama (personel_id, bolge_id) VALUES (%s, %s)", (personel, target_bolge[0]))
        bolge_personel_count[target_bolge[0]] += 1

    g.conn.commit()

# Ana sayfa rotası
@app.route('/')
@login_required
def index():
    # Olay verileri
    g.cursor.execute("""
        SELECT Olay.id, Bolge.ad, OlayTuru.tur, Olay.olay_siddeti, Olay.zaman 
        FROM Olay
        JOIN Bolge ON Olay.bolge_id = Bolge.id
        JOIN OlayTuru ON Olay.olay_turu_id = OlayTuru.id
    """)
    olaylar = g.cursor.fetchall()

    # Her olay için personelleri al
    olaylar_detay = []
    for olay in olaylar:
        olay_id = olay[0]
        g.cursor.execute("""
            SELECT Personel.ad 
            FROM Olay_Personel
            JOIN Personel ON Olay_Personel.personel_id = Personel.id
            WHERE Olay_Personel.olay_id = %s
        """, (olay_id,))
        personeller = g.cursor.fetchall()
        olaylar_detay.append({
            'id': olay[0],
            'bolge_ad': olay[1],
            'olay_turu': olay[2],
            'olay_siddeti': olay[3],
            'zaman': olay[4],
            'personeller': [p[0] for p in personeller]
        })

    # Diğer veriler
    g.cursor.execute("SELECT * FROM Personel")
    personeller = g.cursor.fetchall()

    g.cursor.execute("SELECT id, ad, tehlike_seviyesi FROM Bolge ORDER BY tehlike_seviyesi DESC")
    bolgeler = g.cursor.fetchall()

    bolgeler_with_personel = []
    for bolge in bolgeler:
        g.cursor.execute("""
            SELECT Personel.id, Personel.ad FROM PersonelAtama
            JOIN Personel ON PersonelAtama.personel_id = Personel.id
            WHERE PersonelAtama.bolge_id = %s
        """, (bolge[0],))
        personeller_in_bolge = g.cursor.fetchall()
        bolgeler_with_personel.append({
            "id": bolge[0],
            "ad": bolge[1],
            "tehlike_seviyesi": bolge[2],
            "personeller": personeller_in_bolge
        })

    g.cursor.execute("SELECT id, tur FROM OlayTuru")
    olay_turleri = g.cursor.fetchall()

    g.cursor.execute("""
        SELECT Personel.ad, Bolge.ad 
        FROM PersonelAtama
        JOIN Personel ON PersonelAtama.personel_id = Personel.id
        JOIN Bolge ON PersonelAtama.bolge_id = Bolge.id
    """)
    atamalar = g.cursor.fetchall()

    g.cursor.execute("""
        SELECT ad, basari, sure FROM Personel ORDER BY basari DESC
    """)
    personel_siralamasi = g.cursor.fetchall()

    return render_template('index.html', olaylar=olaylar_detay, personeller=personeller, bolgeler=bolgeler_with_personel, olay_turleri=olay_turleri, atamalar=atamalar, personel_siralamasi=personel_siralamasi)

# Yeni olay ekleme
@app.route('/add_olay', methods=['POST'])
@login_required
def add_olay():
    bolge_id = int(request.form['bolge_id'])
    olay_turu_id = int(request.form['olay_turu_id'])
    olay_siddeti = int(request.form['olay_siddeti'])
    zaman = request.form['zaman']
    personel_ids = request.form.getlist('personel_id')

    # Olay tablosuna yeni durumu ekleme
    g.cursor.execute(
        "INSERT INTO Olay (bolge_id, olay_turu_id, olay_siddeti, zaman) VALUES (%s, %s, %s, %s)",
        (bolge_id, olay_turu_id, olay_siddeti, zaman)
    )
    olay_id = g.cursor.lastrowid

    for personel_id in personel_ids:
        personel_id = int(personel_id)

        # Formdan her personel için müdahale süresi ve başarı puanını çekiyoruz
        sure_field = f'sure_{personel_id}'
        basari_field = f'basari_{personel_id}'

        # Güvenlik personelinin müdahale süresi ve başarı puanını al
        sure = float(request.form.get(sure_field, 0))
        basari = int(request.form.get(basari_field, 0))

        # Olay ile personelin ilişkisini Olay_Personel tablosuna ekle
        g.cursor.execute("INSERT INTO Olay_Personel (olay_id, personel_id) VALUES (%s, %s)", (olay_id, personel_id))

        # Güvenlik personelinin skorunu güncelleme
        update_personel_score(personel_id, sure, basari)

    # Bölgenin tehlike seviyesini olay şiddetine göre arttırmak
    danger_increment = olay_siddeti

    g.cursor.execute("SELECT tehlike_seviyesi FROM Bolge WHERE id = %s", (bolge_id,))
    current_danger_level = g.cursor.fetchone()[0]

    new_danger_level = current_danger_level + danger_increment

    # Tehlike seviyesinin güncellenmesi
    g.cursor.execute("UPDATE Bolge SET tehlike_seviyesi = %s WHERE id = %s", (new_danger_level, bolge_id))
    g.conn.commit()

    return redirect(url_for('index'))

def update_personel_score(personel_id, sure_degisim, basari_degisim):
    g.cursor.execute("SELECT sure, basari FROM Personel WHERE id=%s", (personel_id,))
    personel = g.cursor.fetchone()
    if personel:
        yeni_sure = personel[0] + sure_degisim
        yeni_basari = personel[1] + basari_degisim
        g.cursor.execute("UPDATE Personel SET sure=%s, basari=%s WHERE id=%s", (yeni_sure, yeni_basari, personel_id))
        g.conn.commit()

# Yeni güvenlik personeli ekleme rotası
@app.route('/add_personel', methods=['POST'])
@login_required
def add_personel():
    personel_ad = request.form['personel_ad']
    personel_sure = float(request.form['personel_sure'])
    personel_basari = int(request.form['personel_basari'])
    g.cursor.execute("INSERT INTO Personel (ad, sure, basari) VALUES (%s, %s, %s)", (personel_ad, personel_sure, personel_basari))
    g.conn.commit()
    flash('Yeni güvenlik personeli başarıyla eklendi.', 'success')
    return redirect(url_for('index'))

# Güvenlik personeli silme rotası
@app.route('/delete_personel', methods=['POST'])
@login_required
def delete_personel():
    personel_id = int(request.form['personel_id'])

    try:
        g.cursor.execute("DELETE FROM PersonelAtama WHERE personel_id = %s", (personel_id,))
        g.cursor.execute("DELETE FROM Olay_Personel WHERE personel_id = %s", (personel_id,))
        g.cursor.execute("DELETE FROM Personel WHERE id = %s", (personel_id,))
        g.conn.commit()
        flash('Güvenlik personeli başarıyla silindi.', 'success')
    except Exception as e:
        g.conn.rollback()
        flash(f'Hata oluştu: {e}', 'danger')
        print(f'Hata oluştu: {e}')
    return redirect(url_for('index'))

# Yeni bölge ekleme rotası
@app.route('/add_bolge', methods=['POST'])
@login_required
def add_bolge():
    bolge_ad = request.form['bolge_ad']
    bolge_tehlike = int(request.form['bolge_tehlike'])
    g.cursor.execute("INSERT INTO Bolge (ad, tehlike_seviyesi) VALUES (%s, %s)", (bolge_ad, bolge_tehlike))
    g.conn.commit()
    flash('Yeni bölge başarıyla eklendi.', 'success')
    return redirect(url_for('index'))

# Bölge silme rotası
@app.route('/delete_bolge', methods=['POST'])
@login_required
def delete_bolge():
    bolge_id = int(request.form['bolge_id'])

    try:
        g.cursor.execute("DELETE FROM PersonelAtama WHERE bolge_id = %s", (bolge_id,))
        g.cursor.execute("DELETE FROM Olay WHERE bolge_id = %s", (bolge_id,))
        g.cursor.execute("DELETE FROM Bolge WHERE id = %s", (bolge_id,))
        g.conn.commit()
        flash('Bölge başarıyla silindi.', 'success')
    except Exception as e:
        g.conn.rollback()
        flash(f'Hata oluştu: {e}', 'danger')
        print(f'Hata oluştu: {e}')
    return redirect(url_for('index'))

# Bölge tehlike seviyesini güncelleme rotası
@app.route('/update_danger_level', methods=['POST'])
@login_required
def update_danger_level():
    bolge_id = request.form['bolge_id']
    bolge_tehlike = request.form['bolge_tehlike']

    g.cursor.execute("UPDATE Bolge SET tehlike_seviyesi = %s WHERE id = %s", (bolge_tehlike, bolge_id))
    g.conn.commit()

    flash('Bölge tehlike seviyesi güncellendi.', 'success')
    return redirect(url_for('index'))
@app.route('/diagram')
@login_required
def diagram():
    # Bölge ve atanan personel verilerini al
    g.cursor.execute("SELECT id, ad, tehlike_seviyesi FROM Bolge ORDER BY tehlike_seviyesi DESC")
    bolgeler = g.cursor.fetchall()

    bolgeler_with_personel = []
    for bolge in bolgeler:
        g.cursor.execute("""
            SELECT Personel.id, Personel.ad FROM PersonelAtama
            JOIN Personel ON PersonelAtama.personel_id = Personel.id
            WHERE PersonelAtama.bolge_id = %s
        """, (bolge[0],))
        personeller_in_bolge = g.cursor.fetchall()
        bolgeler_with_personel.append({
            "id": bolge[0],
            "ad": bolge[1],
            "tehlike_seviyesi": bolge[2],
            "personeller": personeller_in_bolge
        })

    return render_template('diagram.html', bolgeler=bolgeler_with_personel)

if __name__ == '__main__':
    app.run(debug=True)
