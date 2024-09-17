
# Hastane Güvenlik Personeli Optimizasyonu

Bu proje, hastanelerdeki güvenlik personelinin dinamik olarak optimize edilmesini hedefleyen bir yapay zeka uygulamasıdır. Proje, genetik algoritmalar kullanarak güvenlik personelinin olaylara müdahale süresi ve başarısına göre en riskli bölgelere atanmasını sağlar. Sistem, yeni olay ve personel verileri eklendikçe kendini günceller ve en verimli güvenlik dağıtımını sağlar.

## Projenin Amacı ve Kapsamı

Projenin amacı, hastane ortamında güvenlik personelinin etkinliğini ve verimliliğini artırmaktır. Genetik algoritmalar kullanarak:
- Farklı bölgelerdeki olayların sıklığı ve şiddeti analiz edilir.
- Güvenlik personelinin geçmiş performansına göre dinamik olarak görevlendirmeler yapılır.
- Yeni veriler eklendikçe güvenlik dağılımı yeniden optimize edilir.
- Web tabanlı bir arayüz üzerinden personel ve olay yönetimi gerçekleştirilir.

Bu sistem, sürekli değişen hastane güvenlik ihtiyaçlarına hızlı ve etkili bir çözüm sunmayı hedefler.

## Kurulum ve Çalıştırma Talimatları

1. **Gereksinimler:** Projeyi çalıştırmadan önce aşağıdaki gereksinimlerin sisteminizde kurulu olduğundan emin olun:
   - Python 3.7 veya üzeri
   - `pip` paket yöneticisi

2. **Depoyu Kopyalayın:** Bu projeyi yerel makinenize klonlayın:
   ```bash
   git clone <repository-url>
   cd HastaneGuvenlikOptimizasyonu
   ```

3. **Sanal Ortam Oluşturun:** Projenin bağımlılıklarını izole etmek için sanal bir Python ortamı oluşturun:
   ```bash
   python -m venv venv
   ```

4. **Sanal Ortamı Aktif Edin:** 
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - macOS / Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Gereksinimleri Yükleyin:** `requirements.txt` dosyasındaki bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

6. **Projeyi Çalıştırın:** `app.py` dosyasını çalıştırarak web uygulamasını başlatın:
   ```bash
   python app.py
   ```

7. **Web Arayüzünü Kullanın:** Tarayıcınızda [http://localhost:5000](http://localhost:5000) adresine giderek uygulamanın web arayüzünü açabilirsiniz.

## Gereksinimler ve Bağımlılıklar

Projenin çalışabilmesi için gereken Python paketleri şunlardır:
- Flask
- numpy
- pandas
- sklearn
- matplotlib

Bağımlılıkların tam listesi için `requirements.txt` dosyasına bakabilirsiniz.

## Projenin İşlevselliği Hakkında Kısa Bir Açıklama

Bu proje, hastane güvenlik personelinin olaylara etkin müdahale edebilmesi için dinamik ve otomatik bir dağıtım sağlar. Ana özellikleri:
- **Güvenlik Personeli ve Olay Yönetimi:** Web arayüzü üzerinden yeni güvenlik personeli ve bölgeler ekleyebilirsiniz. Ayrıca, olayları sisteme kaydedebilir ve bu bilgilere göre atamaların otomatik olarak güncellenmesini sağlayabilirsiniz.
- **Genetik Algoritma Kullanımı:** Güvenlik personelinin performansına göre, genetik algoritmalar kullanılarak en verimli bölge atamaları gerçekleştirilir.
- **Performans İzleme:** Güvenlik personelinin olaylara müdahale süreleri ve başarı oranları sistemde saklanır ve atamalar bu veriler doğrultusunda optimize edilir.

## Katkı Sağlama Yönergeleri (İsteğe Bağlı)

Projeye katkıda bulunmak isterseniz, lütfen şu adımları izleyin:

1. Bu depoyu forklayın.
2. Yeni bir özellik eklemek için bir branch oluşturun (`git checkout -b feature/ÖzellikAdı`).
3. Yaptığınız değişiklikleri commitleyin (`git commit -m "Özelliği ekledim"`).
4. Branch'i bu depoya pushlayın (`git push origin feature/ÖzellikAdı`).
5. Bir Pull Request oluşturun.

Her türlü geri bildirimi ve katkıyı memnuniyetle karşılarız!
