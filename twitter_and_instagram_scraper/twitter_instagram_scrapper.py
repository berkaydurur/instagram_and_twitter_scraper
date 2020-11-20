from twitterscraper.query import query_user_info, query_tweets_from_user
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time

global twitter_user_info
twitter_user_info = []


def get_follower_number(username):
    main_url = 'https://www.instagram.com/' + username #Sitenin url'ine ulaşıyor.
    req=requests.get(main_url).text #Ulaştığı url'deki HTML dosyasını çekiyor.

    start = '"edge_followed_by":{"count":'
    end = '},"followed_by_viewer"' #İnstagramda takip edilen sayısı bu iki tag arasında sayısı. Buradaki kısım bu aradaki sayıyı alıyor.
    followers = req[req.find(start) + len(start):req.rfind(end)]

    start = '"edge_follow":{"count":'
    end = '},"follows_viewer"' #İnstagramda takipçi sayısı bu iki tag arasında sayısı. Buradaki kısım bu aradaki sayıyı alıyor.
    following = req[req.find(start) + len(start):req.rfind(end)]
    print(followers+" Takipçi", following+" Takip Edilen") #Sayıları yazdırıyoruz.
    f = open(username+" takip sayıları.txt", 'w')
    f.write("Takipci Sayısı: %s \n Takip Edilen Sayısı: %s" % (followers,following))
    f.close()


def downloader(photo_url,temp,username):
    photo_no=str(temp)  #Son işlem olarak çektiğimiz fotoğrafların linklerini indireceğiz.
    print('Fotoğraf sayısı:' + photo_no)
    requests_url = requests.get(photo_url)
    f = open(username + photo_no +'.jpg', 'ab')
    f.write(requests_url.content) #Fotoğrafı açtığımız dosyaya .jpg formatında yazdırıyor ve kapatıyoruz.
    print('İndiriliyor')
    f.close()
    print('İndirme Tamamlandı')

def find_photo_url(requests_url):
    soup = BeautifulSoup(requests_url, 'lxml') #Text olarak alınan html'de "og:image" takısı aranıyor. Bu takının contenti
    photo_url = soup.find("meta", property="og:image") #fotografın linkini içermektedir.
    return photo_url["content"]

def requests_start_url(start_url):
    response = requests.get(start_url) #Getirilen postun html dosyasını text haline getiriyoruz.
    html = response.text
    return html


def instagram_get_photo(username,driver):
    driver.get("https://www.instagram.com/"+username) #Giriş yaptıktan sonra bilgi çekeceğimiz hesaba giriyoruz
    lenOfPage=driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount=lenOfPage
        time.sleep(3)
        lenOfPage=driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True #Bu kısımda sayfanın en aşağısına inmek için JavaScript kullanıyoruz. Çünkü instagramda fotoğraflar sadece aşağı indikçe
            #yükleniyor ve ulaşılabilir oluyor.

    posts = [] #Bu kısım tek tek postların linklerini bulup listeler çünkü fotoğrafların linklerine sadece post linklerinden ulaşabiliyoruz.
    links = driver.find_elements_by_tag_name('a') #Post linklerinin bulup listelendiği kısım.
    temp =0
    for link in links:
        post=link.get_attribute('href')
        if '/p/' in post: #instagramda her postun linki /p/.... ile başlar bundan dolayı bunları arıyoruz
            posts.append(post) #tüm postları bulup listeledik.

    for post in posts: #Şimdi her post için bir kaç method çalıştıracağız.
        temp=temp+1
        start_url = post
        requests_url = requests_start_url(start_url)
        photo_url = find_photo_url(requests_url)
        downloader(photo_url,temp,username) #Bu işlemler sonrasında elimizde fotoğraflar ve takip edilen ve takipçi sayısı bulunuyor.

def instagram_login(username):
    driver = webdriver.Chrome() #Chrome'u açmak için selenium ile webdriver kullanarak açıyoruz.
    driver.get('https://www.instagram.com/accounts/login/?source=auth_switcher') #Fotografları görebilmek için giriş yapmak gerekiyor.
    time.sleep(3) #Sayfa yüklenmesi bekleniyor
    driver.find_element_by_name("username").send_keys('webcrawlornek')
    driver.find_element_by_name("password").send_keys('webcrawl1234') #Örnek hesabımızla giriş yapıyoruz ve bilgileri giriş kısmına yazdırıyoruz.
    driver.find_element_by_name("password").send_keys(u'\ue007')
    time.sleep(3) #Sayfa yüklenmesi bekleniyor
    temp = 0
    instagram_get_photo(username,driver)
    get_follower_number(username)


def queringTweets(username):
    filename = "{}.json".format(username)
    filename1 = "{}.txt".format(username)
    tweets = query_tweets_from_user(username)
    f = open(username + ".txt", "a")
    j = []
    for t in tweets:
        t.timestamp = t.timestamp.isoformat()
        f.write(" Tweet ID:{} Tarih:{}: {} \n".format(t.tweet_id, t.timestamp, t.text))
        #j.append(t.__dict__)
    f.close()
    """with open(filename, "w") as f:
        f.write(json.dumps(j))
    with open(filename1, "w") as f:
        f.write(json.dumps(j))"""


def queringUserInfo(username):
    user_info = query_user_info(user=username)
    f = open(username + ".txt", "w")
    twitter_user_data = {}
    twitter_user_data["Kullanıcı ismi"] = user_info.user
    twitter_user_data["Tam isim"] = user_info.full_name
    twitter_user_data["Tweet Sayısı"] = user_info.tweets
    twitter_user_data["Takip ettiği"] = user_info.following
    twitter_user_data["Takipçi"] = user_info.followers

    f.write("Kullanıcı Adı:{} \n Tweet Sayısı:{} \n Takip Edilen Sayısı:{} \n Takipçi Sayısı:{}\n".format(twitter_user_data["Kullanıcı ismi"],twitter_user_data["Tweet Sayısı"],twitter_user_data["Takip ettiği"],twitter_user_data["Takipçi"]))
    f.close()

    with open(username + ".txt", "a", encoding="utf-8") as f1:
        f1.write("Tam İsim:{} \n".format(twitter_user_data["Tam isim"]))
    f1.close()

    queringTweets(username)
    return twitter_user_data


def main():
    print("Twitter sorgulamaları için 1'e, Instagram sorgulamaları için 2'ye basınız: ")
    choice = int(input())

    if choice == 1:
        print("Twitter için kullanıcı adı giriniz:")
        username = input()
        start = time.time()
        queringUserInfo(username)
        print(queringUserInfo(username))
        elapsed = time.time() - start
        print(f"Geçen süre: {elapsed}")
    elif choice == 2:
        print("Instagram için kullanıcı adı giriniz:")
        username = input()
        start = time.time()
        instagram_login(username)
        elapsed = time.time() - start
        print(f"Geçen süre: {elapsed}")

    else:
        print("Yanlış bir değer girdiniz. Programı yeniden başlatın.")

if __name__ == '__main__':
    main()