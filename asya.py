import speech_recognition as sr
from datetime import datetime
import locale
import webbrowser
import time
from gtts import gTTS
import random
from random import choice
import os
import requests
import json
import feedparser
import colorama
from colorama import Fore
from bs4 import BeautifulSoup
from urllib.parse import quote
import pygame
import unicodedata
from pytube import Search
import re
import subprocess
import wikipedia

colorama.init()
r = sr.Recognizer()

# Hava durumu için OpenWeatherMap API'si
API_KEY = "xxx"

#FONKSİYONLAR----------------------------

# Uyandırma komutunu dinleme fonksiyonu
def wake_up():
    with sr.Microphone() as source:
        print("Bekleme modundayım.( Asya diye seslenerek uyandırabilirsiniz.)")
        while True:
            try:
                audio = r.listen(source)
                command = r.recognize_google(audio, language="tr-TR").lower()
                if "asya" in command:
                    speak("Dinliyorum!")
                    print("Asya: Dinliyorum?")
                    return True
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                speak("Sistemde bir sorun var, lütfen tekrar deneyin.")
                print("Sistemde bir sorun var, lütfen tekrar deneyin.")
                return False

# Sesli yanıt fonksiyonu
def speak(text):
    tts = gTTS(text, lang='tr')
    file = "temp.mp3"
    tts.save(file)
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        if os.path.exists(file):
            os.remove(file)

# Kullanıcıdan komut alma fonksiyonu
def record(ask=False):
    with sr.Microphone() as source:
        if ask:
            speak(ask)
            print(Fore.BLUE)
            print(ask)
        print("Komutunuzu bekliyorum...")
        try:
            audio = r.listen(source, timeout=10)
            return r.recognize_google(audio, language='tr-TR').lower()
        except sr.UnknownValueError:
            speak("Bekleme moduna geçiyorum.")
        except sr.RequestError:
            speak("Sistem şu anda çalışmıyor.")
        except sr.WaitTimeoutError:
            speak("Dinleme zaman aşımına uğradı. Tekrar 'Asya' diyerek uyandırabilirsiniz.")
            print("Dinleme zaman aşımına uğradı.")
        return ""
    
#Günün başlangıcı ve özeti fonksiyonu
def start_day():
   
    locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
    current_time = datetime.now()
    day_name = current_time.strftime("%A")
    date_str = current_time.strftime("%d %B %Y")
    time_str = current_time.strftime("%H:%M")
    speak(f"Günaydın. Bugün günlerden {date_str}, {day_name} ve saat {time_str}.")
    print(Fore.GREEN + f"Asya: Günaydın. Bugün günlerden {date_str}, {day_name} ve saat {time_str}.")

    # Hava durumu
    city = "İzmir"  
    API_KEY = "09ad0b5c37373353d673573167677a00"
    try:
        city_processed = city.lower().replace("ç", "c").replace("ğ", "g").replace("ı", "i").replace("ö", "o").replace("ş", "s").replace("ü", "u")
        city_normalized = unicodedata.normalize('NFKD', city_processed).encode('ascii', 'ignore').decode('utf-8')

        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_normalized}&appid={API_KEY}&units=metric&lang=tr"
        current_response = requests.get(current_url).json()

        if current_response.get("weather"):
            current_description = current_response["weather"][0]["description"]
            current_temp = current_response["main"]["temp"]
            suggestion = "Şemsiye almayı unutma!" if "yağmur" in current_description else "Hava güzel, dışarı çıkmak için harika bir gün."
            speak(f"İzmir'de şu anda hava {current_description}, sıcaklık {current_temp} derece. {suggestion}")
            print(Fore.GREEN + f"Asya: İzmir'de şu anda hava {current_description}, sıcaklık {current_temp} derece. {suggestion}")
        else:
            speak("Hava durumu bilgisi alınamadı.")
    except Exception as e:
        speak("Hava durumu bilgisi alınırken bir hata oluştu.")
        print(Fore.RED + f"Hata: {e}")

    # Günün notlarını okuma
    try:
        with open('notlar.txt', 'r', encoding='utf-8') as f:
            notes = f.readlines()
        if notes:
            speak("Almış olduğun notlar :")
            for note in notes[-3:]:
                speak(note.strip())
                print(Fore.GREEN + f"Asya: {note.strip()}")
        else:
            speak("Hiç notun yok.")
    except FileNotFoundError:
        speak("Hiç notun yok.")

    # Güncel haberleri okuma
    try:
        url = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "xml")
        headlines = soup.find_all("title", limit=5)
        speak("İşte bugünün haber başlıkları:")
        for headline in headlines:
            speak(headline.text)
            print(Fore.GREEN + f"Asya: {headline.text}")
    except Exception as e:
        speak("Haberler alınırken bir hata oluştu.")
        print(Fore.RED + f"Hata: {e}")

    # Gün bitiş mesajı
    speak("Umarım güzel bir gün geçirirsin. Yardımcı olmamı istediğin bir konu olursa senin için her zaman buradayım.")
    print(Fore.GREEN + "Asya: Umarım güzel bir gün geçirirsin. Yardımcı olmamı istediğin bir konu olursa senin için her zaman buradayım.")


# Mevcut tarayıcıyı kapatma fonksiyonu
def close_browser():
    if os.name == 'nt':  # Windows
        os.system("taskkill /IM chrome.exe /F")
    elif os.name == 'posix':  # macOS ve Linux(Raspberry Pi)
        os.system("pkill -f chrome")

# YouTube şarkı çalma fonksiyonu
def play_youtube_song(song_name):
    try:
        # Mevcut tarayıcıyı kapat
        close_browser()
        time.sleep(1)  

        # Şarkıyı YouTube'da ara
        search = Search(song_name)
        video = search.results[0]  # İlk sonucu al
        video_url = f"https://www.youtube.com/watch?v={video.video_id}"
        
        # YouTube linkini aç
        webbrowser.open(video_url)
        speak(f"{song_name} şarkısını YouTube'da çalıyorum.")
        print(Fore.GREEN + f"Asya: {song_name} şarkısını YouTube'da çalıyorum. Link: {video_url}")
    except Exception as e:
        speak("Şarkıyı bulamadım, lütfen başka bir şarkı ismi söyleyin.")
        print(Fore.RED + f"Hata: {e}")
 
 #YouTube video oynatma fonksiyonu       
def play_youtube_video(video_name):
    try:
        # Mevcut tarayıcıyı kapat
        close_browser()
        time.sleep(1)  

        # Videoyu YouTube'da ara
        search = Search(video_name)
        video = search.results[0]  # İlk sonucu al
        video_url = f"https://www.youtube.com/watch?v={video.video_id}"
        
        # YouTube linkini aç
        webbrowser.open(video_url)
        speak(f"{video_name} adlı videoyu YouTube'da oynatıyorum.")
        print(Fore.GREEN + f"Asya: {video_name} adlı videoyu YouTube'da oynatıyorum. Link: {video_url}")
    except Exception as e:
        speak("Videoyu bulamadım, lütfen başka bir video ismi söyleyin.")
        print(Fore.RED + f"Hata: {e}")

# Haber okuma fonksiyonu
def get_news():
    url = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    headlines = soup.find_all("title", limit=5)
    speak("İşte bugünün haber başlıkları:")
    for headline in headlines:
        speak(headline.text)
        print(Fore.GREEN + f"Asya: {headline.text}")

# KOMUT FONKSİYONLARI:
def response(voice):
    if 'nasılsın' in voice or 'naber' in voice or 'ne haber' in voice or 'nabersin' in voice:
        responses = ["İyiyim, sen nasılsın?", "Gayet iyi, ya sen?", "Her şey yolunda, senin için ne yapabilirim?"]
        reply = choice(responses)
        speak(reply)
        print(Fore.GREEN + f"Asya: {reply}")
        
    elif 'teşekkür ederim'  in voice or 'teşekkürler' in voice or 'sağol' in voice or 'sağ ol' in voice or 'eyvallah' in voice:
        responses = ["Rica ederim", "Lafı olmaz", "Önemli değil", "Benim işim bu"]
        reply = choice(responses)
        speak(reply)
        print(Fore.GREEN + f"Asya: {reply}")    
        
    elif 'tarih' in voice or 'bugün' in voice:
        locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
        current_date = datetime.now().strftime("%d %B %Y, %A")
        speak(f"Bugünün tarihi: {current_date}.")
        print(Fore.GREEN + f"Asya: Bugünün tarihi: {current_date}.")
        
    elif 'iyiyim' in voice:
        print(Fore.GREEN)
        print("Asya  = iyi olmana sevindim senin için ne yapabilirim")
        speak("iyi olmana sevindim senin için ne yapabilirim")
        
    elif 'kötüyüm'  in voice:
        sozlerOlumsuz = ["üzüldüm senin adına yapabileceğim bir şey var mı",
                "sıkma canını benim yapabileceğim bir şey var mı",
                "boşver iyi olmaya bak senin için birşey yapabilir miyim"

                
        ]
        secimolumsuz=choice(sozlerOlumsuz)

        speak(secimolumsuz)
        
    elif 'hava' in voice:  
        city = record("Hangi il için hava durumunu öğrenmek istiyorsunuz?")  
        if city:
            
            city_processed = city.lower()
            city_processed = city_processed.replace("ç", "c").replace("ğ", "g").replace("ı", "i") \
                                        .replace("ö", "o").replace("ş", "s").replace("ü", "u")
            
            city_normalized = unicodedata.normalize('NFKD', city_processed).encode('ascii', 'ignore').decode('utf-8')
            
            try:
                
                current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_normalized}&appid={API_KEY}&units=metric&lang=tr"
                current_response = requests.get(current_url).json()
                
                
                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_normalized}&appid={API_KEY}&units=metric&lang=tr"
                forecast_response = requests.get(forecast_url).json()
                
                if current_response.get("weather") and forecast_response.get("list"):
                    # Anlık hava durumu
                    current_description = current_response["weather"][0]["description"]
                    current_temp = current_response["main"]["temp"]
                    
                    # Yarınki hava durumu
                    tomorrow = forecast_response["list"][8]  # 8 * 3 saatlik tahmin = yarının ilk saati
                    tomorrow_description = tomorrow["weather"][0]["description"]
                    tomorrow_temp = tomorrow["main"]["temp"]
                    
                    # Tek cümlede hava durumu
                    full_report = (
                        f"{city.capitalize()} için şu anda hava {current_description}, sıcaklık {current_temp} derece. "
                        f"Yarın ise hava {tomorrow_description}, sıcaklık {tomorrow_temp} derece olacak."
                    )
                    
                    speak(full_report)
                    print(Fore.GREEN)
                    print(f"Asya = {full_report}")
                else:
                    speak("Bu şehir için hava durumu bilgisi alınamadı. Lütfen doğru bir şehir adı verin.")
            except Exception as e:
                speak("Hava durumu bilgisi alınırken bir hata oluştu.")
                print(Fore.RED)
                print("Hata:", e)
        else:
            speak("Şehir adını anlayamadım. Lütfen tekrar söyleyin.")

    elif 'hava' in voice:  
        city = record("Hangi il için hava durumunu öğrenmek istiyorsunuz?")  
        if city:
            
            city_processed = city.lower()
            city_processed = city_processed.replace("ç", "c").replace("ğ", "g").replace("ı", "i") \
                                        .replace("ö", "o").replace("ş", "s").replace("ü", "u")

            city_normalized = unicodedata.normalize('NFKD', city_processed).encode('ascii', 'ignore').decode('utf-8')
            
            try:
                
                current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_normalized}&appid={API_KEY}&units=metric&lang=tr"
                current_response = requests.get(current_url).json()
                
                
                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_normalized}&appid={API_KEY}&units=metric&lang=tr"
                forecast_response = requests.get(forecast_url).json()
                
                if current_response.get("weather") and forecast_response.get("list"):
                    # Anlık hava durumu
                    current_description = current_response["weather"][0]["description"]
                    current_temp = current_response["main"]["temp"]
                    
                    # Yarınki hava durumu
                    tomorrow = forecast_response["list"][8]  # 8 * 3 saatlik tahmin = yarının ilk saati
                    tomorrow_description = tomorrow["weather"][0]["description"]
                    tomorrow_temp = tomorrow["main"]["temp"]
                    
                    # Tek cümlede hava durumu
                    full_report = (
                        f"{city.capitalize()} için şu anda hava {current_description}, sıcaklık {current_temp} derece. "
                        f"Yarın ise hava {tomorrow_description}, sıcaklık {tomorrow_temp} derece olacak."
                    )
                    
                    speak(full_report)
                    print(Fore.GREEN)
                    print(f"Asya = {full_report}")
                else:
                    speak("Bu şehir için hava durumu bilgisi alınamadı. Lütfen doğru bir şehir adı verin.")
            except Exception as e:
                speak("Hava durumu bilgisi alınırken bir hata oluştu.")
                print(Fore.RED)
                print("Hata:", e)
        else:
            speak("Şehir adını anlayamadım. Lütfen tekrar söyleyin.")
    
    elif 'özlü söz' in voice:
        quotes = [
            "Başarı, hazırlıkla fırsatın buluştuğu yerdir. – Bobby Unser",
            "Hiçbir şey bilmediğini bilmek, bilgeliktir. – Sokrates",
            "Hayat, biz başka planlar yaparken başımıza gelenlerdir. – John Lennon",
            "İki şey sonsuzdur: insanın aptallığı ve evren; ve ben evrenden o kadar emin değilim. – Albert Einstein",
            "Mutluluk, ne olduğumuz ve ne istediğimiz arasındaki dengeyi bulmaktır. – Epiktetos",
            "Düşünceleriniz ne ise hayatınız da odur. Hayatınızın yönünü düşünceleriniz belirler. – Marcus Aurelius",
            "Kendini fetheden kişi, en güçlü kişidir. – Lao Tzu",
            "Bir işi doğru yapmanın zamanı her zaman şimdidir. – Martin Luther King Jr.",
            "Cesaret, korkunun yokluğu değil, ona rağmen devam etmektir. – Nelson Mandela",
            "Bilgi güçtür; ancak bilgiyi uygulamak daha güçlüdür. – Francis Bacon",
            "Hayatta en büyük zafer, hiç düşmemek değil, her düştüğünde ayağa kalkmaktır. – Nelson Mandela",
            "Hayal gücü bilgiden daha önemlidir. Çünkü bilgi sınırlıdır, hayal gücü ise sınırsızdır. – Albert Einstein",
            "Başarısızlık, daha zekice başlama fırsatından başka bir şey değildir. – Henry Ford",
            "Kendi ışığını bul. – Buda",
            "Hedefe ulaşmak için öncelikle ona inanmak gerekir. – Napoleon Hill",
            "Düşüncelerini değiştir, hayatın değişsin. – Norman Vincent Peale",
            "Kimse seni senden daha iyi tanıyamaz. – Ralph Waldo Emerson",
            "Zaman en adil yargıçtır; ne kadar iyi kullandığın senin elindedir. – Seneca",
            "Başarı, küçük çabaların tekrar ve tekrar gösterilmesidir. – Robert Collier",
            "Hayat, cesur bir macera ya da hiçbir şeydir. – Helen Keller"
        ]
        quote = choice(quotes)
        speak(quote)
        print(Fore.GREEN + f"Asya: {quote}")

    elif 'haber oku' in voice:
        get_news()
        
    elif 'not al' in voice:
        note_text = record("Ne not almak istersiniz?")
        if note_text:
            with open('notlar.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {note_text}\n")
            speak("Notunuzu kaydettim.")
            print(Fore.GREEN + "Asya: Not kaydedildi.")
            
    elif 'notları oku' in voice:
        try:
            with open('notlar.txt', 'r', encoding='utf-8') as f:
                notes = f.readlines()
            if notes:
                speak("İşte notlarınız:")
                for note in notes[-3:]:
                    speak(note.strip())
                    print(Fore.GREEN + f"Asya: {note.strip()}")
            else:
                speak("Henüz bir notunuz yok.")
        except FileNotFoundError:
            speak("Henüz bir not kaydetmediniz.")
            
    elif any(word in voice for word in ['hesapla', 'işlem yap', 'toplama', 'çıkarma', 'çarpma', 'bölme']):
            try:
                
                numbers = re.findall(r'\d+', voice)
                operation = None
                if 'topla' in voice or 'artı' in voice:
                    operation = '+'
                elif 'çıkar' in voice or 'eksi' in voice:
                    operation = '-'
                elif 'çarp' in voice or 'çarpı' in voice:
                    operation = '*'
                elif 'böl' in voice or 'bölü' in voice:
                    operation = '/'
                
                if operation and len(numbers) >= 2:
                    result = eval(f"{numbers[0]} {operation} {numbers[1]}")
                    response_text = f"Sonuç: {result}"
                    speak(response_text)
                    print(Fore.GREEN + f"Asya = {response_text}")
                return
            except:
                speak("Hesaplama yapılırken bir hata oluştu")        
            
    elif 'neler yapabilirsin' in voice:
        speak('Seninle basitçe sohbet edebilirim ,Saati ve tarihi söyleyebiilirim ,Senin için not alabilirim,Hava durumunu söyleyebilirim,Güncel haberleri okuyabilirim,Senin yerine googleda arama yapabilirim ,Özlü söz söyleyebilirim,Dört işlem yapabilirim,Youtube dan müzik veya video oynatabilirim.Peki sen ne yapmamı istersin')
        print(Fore.GREEN)
        print('Seninle basitçe sohbet edebilirim ,Saati ve tarihi söyleyebiilirim ,Senin için not alabilirim,Hava durumunu söyleyebilirim,Güncel haberleri okuyabilirim,Senin yerine googleda arama yapabilirim ,Özlü söz söyleyebilirim,Dört işlem yapabilirim,Youtube dan müzik veya video oynatabilirim.Peki sen ne yapmamı istersin')

    elif 'kimsin'  in voice:
        print(Fore.GREEN)
        speak('Benim adım Asya,Ben bir sesli asistanım,Senin için 7 24 buradayım')
        print('Asya  = Benim adım Asya,Ben bir sesli asistanım,Senin için 7 24 buradayım')

    elif 'saat' in voice:
        speak(datetime.now().strftime('%H:%M:%S'))
        print(Fore.GREEN)
        print("Asya  = "+datetime.now().strftime('%H:%M:%S'))

    elif 'arama' in voice:  
        search = record('Ne aramamı istersin?')  
        url = 'https://google.com/search?q=' + search  
        webbrowser.get().open(url)  
        speak(search + ' için bulduğum sonuçlar')
        print(Fore.GREEN)
        print("Asya = " + search + ' için bulduğum sonuçlar')
        # Wikipedia'dan bilgi alma
        try:
            wikipedia.set_lang("tr")  
            summary = wikipedia.summary(search, sentences=2)  
            speak("Ayrıca, " + search + " hakkında kısa bilgi vereyim.")
            speak(summary)
            print(Fore.GREEN + f"Asya: {summary}")
        except wikipedia.exceptions.DisambiguationError as e:
            speak("Bu konuda birden fazla sonuç buldum. Daha spesifik bir şey söyleyebilir misin?")
        except wikipedia.exceptions.PageError:
            speak("Bu konuda bilgi bulamadım.")
        except Exception as e:
            speak("Bir hata oluştu, lütfen tekrar deneyin.")
            print(Fore.RED + f"Hata: {e}")

    elif "youtube" in voice:
        searchy = record('ne aramamı istersin')
        urly ='https://www.youtube.com/results?search_query='+searchy
        webbrowser.get().open(urly)
        speak(searchy+' için bulduğum sonuçlar')
        print(Fore.GREEN)
        print("Asya  = "+searchy+' için bulduğum sonuçlar')     

    elif 'güle güle' in voice or 'hoşça kal' in voice or 'bay bay' in voice:
        speak('Görüşmek üzere,Sistemi tamemen kapatıyorum.')
        print(Fore.GREEN)
        print((speak))
        exit()
        
    elif 'iyi geceler' in voice:
        speak('İyi geceler,sistemimi kapatıyorum.')
        print(Fore.GREEN)
        print("Asya  = İyi geceler,sistemimi kapatıyorum.")
        exit()

    elif 'günümü başlat' in voice:
        start_day()
        
    elif 'şarkı' in voice:
        song_name = record("Hangi şarkıyı çalmamı istersin?")
        if song_name:
            play_youtube_song(song_name)
            
    elif 'değiştir' in voice:
        song_name = record("Hangi şarkıyla değiştirmemi istersin?")
        if song_name:
            play_youtube_song(song_name)
    
    elif 'kapat' in voice:
        if os.name == 'nt':
            os.system("taskkill /IM chrome.exe /F")
        elif os.name == 'posix':
            os.system("pkill -f chrome")
        speak("Kapattım.")
        print(Fore.GREEN + "Asya: Kapattım.")
        close_browser()

    elif 'oynat' in voice:
        video_name = record("Ne oynatmamı istersin?")
        if video_name:
            play_youtube_video(video_name)

    elif 'nedir' in voice or 'kimdir' in voice:
            try:
                import wikipedia
                wikipedia.set_lang("tr")
                
                query = voice.replace('nedir', '').replace('kimdir', '').strip()
                try:
                    
                    search_results = wikipedia.search(query, results=1)
                    if search_results:
                        
                        result = wikipedia.summary(search_results[0], sentences=2)
                        speak(result)
                        print(Fore.GREEN + f"Johnny = {result}")
                    else:
                        speak("Bu konu hakkında bilgi bulamadım")
                except wikipedia.exceptions.DisambiguationError as e:
                    
                    result = wikipedia.summary(e.options[0], sentences=2)
                    speak(result)
                    print(Fore.GREEN + f"Johnny = {result}")
                except wikipedia.exceptions.PageError:
                    speak("Bu konu hakkında bilgi bulamadım")
                return
            except Exception as e:
                print(f"Wikipedia hatası: {str(e)}")
                speak("Bu konu hakkında bilgi bulamadım")
                
# Ana döngü
while True:
    if wake_up():  
        while True:
            voice = record()
            if voice:
                response(voice)  
            else:
                print("Dinleme modu sona erdi. Tekrar uyandırmak için 'Asya' diyebilirsiniz.")
                break

