from flask import Flask, render_template, request, redirect, url_for, session, flash
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
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="M.mustafa27",
    database="hospital_security"
)
cursor = conn.cursor()


class Admin(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(admin_id):
    cursor.execute("SELECT id, username FROM Admin WHERE id = %s", (admin_id,))
    admin = cursor.fetchone()
    if admin:
        return Admin(admin[0], admin[1])
    return None


#giriş sayfası rotası ve veritabanındaki kullanıcı adı ve şifre eşleşmesi ile giriş yapabilme.
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT id, password FROM Admin WHERE username = %s", (username,))
        admin = cursor.fetchone()

        if admin and admin[1] == password:
            admin_user = Admin(admin[0], username)
            login_user(admin_user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Şifre veya Kullanıcı Adı Hatalı!!!', 'danger')

    return render_template('admin_login.html')

# admin sayfası için rota
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# admin ekleme rotası
@app.route('/add_admin', methods=['POST'])
@login_required
def add_admin():
    new_username = request.form['username']
    new_password = request.form['password']

    cursor.execute("INSERT INTO Admin (username, password) VALUES (%s, %s)", (new_username, new_password))
    conn.commit()
    flash('Yeni Admin Başarıyla Eklendi.', 'success')
    return redirect(url_for('admin_dashboard'))


# çıkış rotası
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin_login'))
# Yapay veri üretimi
def generate_fake_data():
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


def run_genetic_algorithm():
    cursor.execute("""
        SELECT Olay.bolge_id, Olay.olay_siddeti, OlayTuru.carpan, Bolge.tehlike_seviyesi 
        FROM Olay 
        JOIN Bolge ON Olay.bolge_id = Bolge.id
        JOIN OlayTuru ON Olay.olay_turu_id = OlayTuru.id
    """)
    olaylar = cursor.fetchall()

    olay_df = pd.DataFrame(olaylar, columns=['Bölge ID', 'Olay Şiddeti', 'Çarpan', 'Tehlike Seviyesi'])
    olay_df['Toplam Şiddet'] = olay_df['Olay Şiddeti'] * olay_df['Çarpan']

    cursor.execute("SELECT id, sure, basari FROM Personel")
    personeller = cursor.fetchall()
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


def update_personel_atamalari(best_individual, bolge_list, personel_list):
    cursor.execute("DELETE FROM PersonelAtama")  # önceki atamayı silme
    assigned_personel = set()  # yeni atananı işaretleme

    # Güvenliklerin performans sıralaması
    cursor.execute("SELECT id FROM Personel ORDER BY basari DESC")
    sorted_personel = [row[0] for row in cursor.fetchall()]

    # Bölgelerin tehlike seviyesine göre sıralanması
    sorted_bolge_list = sorted(bolge_list, key=lambda x: x[1], reverse=True)  # Sort by tehlike_seviyesi

    bolge_personel_count = {bolge[0]: 0 for bolge in sorted_bolge_list}

    # Her bölgede en az bir güvenlik olmasını sağlayan kod
    for i, bolge in enumerate(sorted_bolge_list):
        personel = sorted_personel[i]
        cursor.execute("INSERT INTO PersonelAtama (personel_id, bolge_id) VALUES (%s, %s)", (personel, bolge[0]))
        bolge_personel_count[bolge[0]] += 1
        assigned_personel.add(personel)

    # Her yere 1 güvenlik dağıtıldıktan sonra kalanların en tehlikeli bölgeden başlaması
    remaining_personel = [p for p in sorted_personel if p not in assigned_personel]

    # Kalan personellerin en tehlikeli bölgeye dağıtılması için olan kod
    for personel in remaining_personel:
        target_bolge = min(sorted_bolge_list, key=lambda x: bolge_personel_count[x[0]])
        cursor.execute("INSERT INTO PersonelAtama (personel_id, bolge_id) VALUES (%s, %s)", (personel, target_bolge[0]))
        bolge_personel_count[target_bolge[0]] += 1

    conn.commit()


# Yeni olay eklendiğinde personelin performansını güncelle
def update_personel_score(personel_id, sure_degisim, basari_degisim):
    cursor.execute("SELECT sure, basari FROM Personel WHERE id=%s", (personel_id,))
    personel = cursor.fetchone()
    yeni_sure = personel[0] + sure_degisim
    yeni_basari = personel[1] + basari_degisim
    cursor.execute("UPDATE Personel SET sure=%s, basari=%s WHERE id=%s", (yeni_sure, yeni_basari, personel_id))
    conn.commit()
# Yeni olay eklendiğinde bölgenin tehlike seviyesini güncelle
@app.route('/update_danger_level', methods=['POST'])
def update_danger_level():
    # Get the form data
    bolge_id = request.form['bolge_id']
    bolge_tehlike = request.form['bolge_tehlike']

    # Update the danger level of the selected region in the database
    cursor.execute("UPDATE Bolge SET tehlike_seviyesi = %s WHERE id = %s", (bolge_tehlike, bolge_id))
    conn.commit()

    # Redirect back to the homepage after updating
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    # Olay verileri
    cursor.execute("""
        SELECT Olay.id, Bolge.ad, OlayTuru.tur, Olay.olay_siddeti, Olay.zaman 
        FROM Olay
        JOIN Bolge ON Olay.bolge_id = Bolge.id
        JOIN OlayTuru ON Olay.olay_turu_id = OlayTuru.id
    """)
    olaylar = cursor.fetchall()

    # personel verilerini eşleme
    cursor.execute("SELECT * FROM Personel")
    personeller = cursor.fetchall()

    # bölgeler ve tehlike seviyelerini eşleme
    cursor.execute("SELECT id, ad, tehlike_seviyesi FROM Bolge ORDER BY tehlike_seviyesi DESC")
    bolgeler = cursor.fetchall()

    # personel ve görevlendirildiği bölgeyi eşleme
    bolgeler_with_personel = []
    for bolge in bolgeler:
        cursor.execute("""
            SELECT Personel.id, Personel.ad FROM PersonelAtama
            JOIN Personel ON PersonelAtama.personel_id = Personel.id
            WHERE PersonelAtama.bolge_id = %s
        """, (bolge[0],))
        personeller_in_bolge = cursor.fetchall()
        bolgeler_with_personel.append({
            "id": bolge[0],
            "ad": bolge[1],
            "tehlike_seviyesi": bolge[2],
            "personeller": personeller_in_bolge
        })

    cursor.execute("SELECT id, tur FROM OlayTuru")
    olay_turleri = cursor.fetchall()

    cursor.execute("""
        SELECT Personel.ad, Bolge.ad 
        FROM PersonelAtama
        JOIN Personel ON PersonelAtama.personel_id = Personel.id
        JOIN Bolge ON PersonelAtama.bolge_id = Bolge.id
    """)
    atamalar = cursor.fetchall()

    cursor.execute("""
        SELECT ad, basari FROM Personel ORDER BY basari DESC
    """)
    personel_siralamasi = cursor.fetchall()

    return render_template('index.html', olaylar=olaylar, personeller=personeller, bolgeler=bolgeler_with_personel, olay_turleri=olay_turleri, atamalar=atamalar, personel_siralamasi=personel_siralamasi)

# Yeni olay ekleme
@app.route('/add_olay', methods=['POST'])
def add_olay():
    bolge_id = int(request.form['bolge_id'])
    olay_turu_id = int(request.form['olay_turu_id'])
    olay_siddeti = int(request.form['olay_siddeti'])
    zaman = int(request.form['zaman'])
    personel_id = int(request.form['personel_id'])
    sure = float(request.form['sure'])
    basari = int(request.form['basari'])

    # Olay tablosuna yeni durumu ekleme
    cursor.execute("INSERT INTO Olay (bolge_id, olay_turu_id, olay_siddeti, zaman) VALUES (%s, %s, %s, %s)",
                   (bolge_id, olay_turu_id, olay_siddeti, zaman))
    conn.commit()

    # Güvenlik personelinin skorunu güncelleme
    update_personel_score(personel_id, sure, basari)

    # Bölgenin tehlike seviyesini olay şiddetine göre arttırmak
    danger_increment = olay_siddeti  # You can adjust this to a fixed increment if needed (e.g., danger_increment = 1)

    cursor.execute("SELECT tehlike_seviyesi FROM Bolge WHERE id = %s", (bolge_id,))
    current_danger_level = cursor.fetchone()[0]

    new_danger_level = current_danger_level + danger_increment

    # Tehlike seviyesinin güncellenmesi
    cursor.execute("UPDATE Bolge SET tehlike_seviyesi = %s WHERE id = %s", (new_danger_level, bolge_id))
    conn.commit()

    return redirect(url_for('index'))



@app.route('/add_personel', methods=['POST'])
def add_personel():
    personel_ad = request.form['personel_ad']
    personel_sure = float(request.form['personel_sure'])
    personel_basari = int(request.form['personel_basari'])

    cursor.execute("INSERT INTO Personel (ad, sure, basari) VALUES (%s, %s, %s)", (personel_ad, personel_sure, personel_basari))
    conn.commit()

    return redirect(url_for('index'))


@app.route('/add_bolge', methods=['POST'])
def add_bolge():
    bolge_ad = request.form['bolge_ad']
    bolge_tehlike = int(request.form['bolge_tehlike'])

    cursor.execute("INSERT INTO Bolge (ad, tehlike_seviyesi) VALUES (%s, %s)", (bolge_ad, bolge_tehlike))
    conn.commit()

    return redirect(url_for('index'))


@app.route('/generate_fake_data')
def generate_fake_data_route():
    generate_fake_data()
    return redirect(url_for('index'))


@app.route('/run_genetic_algorithm')
def run_genetic_algorithm_route():
    best_individual, fitness_score = run_genetic_algorithm()
    print("Best individual:", best_individual)
    print("Fitness score:", fitness_score)

    cursor.execute("SELECT id, tehlike_seviyesi FROM Bolge")
    bolge_list = [row for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM Personel")
    personel_list = [row[0] for row in cursor.fetchall()]

    update_personel_atamalari(best_individual, bolge_list, personel_list)

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
