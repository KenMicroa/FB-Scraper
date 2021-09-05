import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import sys
from random import randint


FB_URL = "https://www.facebook.com/login/device-based/regular/login/"
FB_USER = "YOUE FB USERNAME / EMAIL / NUMBER HERE"
FB_PASS = "PASSWORD HERE"
FB_FRIENDS_URL = "https://www.facebook.com/profile.php?id=12222254111100&sk=friends" # << < This is sample link

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77"
                  " Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Chrome Driver Options
options = Options()
options.add_argument("disable-notifications")
options.add_argument("disable-popup")
options.add_argument('headless')  # Will not show browser window

# Setting up Chrome Driver and bs4
chrome_driver_path = "chromedriver.exe" # add chrome drover Path
driver = webdriver.Chrome(chrome_driver_path, options=options)
response = requests.get(url=FB_URL, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')


# Animation function
def animated_loading(name):
    chars = "/—\|"
    for char in chars:
        sys.stdout.write('\r'+name+char)
        sleep(.1)
        sys.stdout.flush()


# Logging to FB Account
def fb_login():
    try:
        animated_loading("[+] logging to FB account...")
        driver.get(FB_URL)
        sleep(randint(5, 8))
        driver.find_element_by_id("email").send_keys(FB_USER)
        driver.find_element_by_id("pass").send_keys(FB_PASS)
        driver.find_element_by_id("loginbutton").click()
        sleep(randint(5, 8))
    except NoSuchElementException:
        block_text = driver.find_element_by_xpath('//*[@id="error_box"]/div[1]').text
        if "You can't use this feature at the moment" == block_text:
            animated_loading("[*] Account is Blocked!!")
            driver.quit()
        animated_loading("[+] re-logging to FB account...")
        sleep(randint(5, 8))
        fb_login()


# Re_direction to FB friend page
def load_fb_friend_page():
    try:
        animated_loading("[+] loading friend url & setting up...")
        sleep(randint(5, 8))
        driver.get(url=FB_FRIENDS_URL)
        sleep(randint(5, 8))
        for _ in range(4):  # <<< Make sure set the range, it depend on your friend list amount, and it will scroll
            # page to get load all names >>>
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(randint(5, 8))
    except NoSuchElementException:
        animated_loading("[+] re_loading friend url...")
        sleep(randint(5, 8))
        load_fb_friend_page()


# Collect all FB friends names
def get_friend_names():
    try:
        animated_loading("[+] collecting friends names...")
        sleep(randint(5, 8))
        list_item = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/"
                                                 "div/div[4]/div/div/div/div/div/div/div/div/div[3]")
        names = list_item.find_elements_by_css_selector(".oajrlxb2 span")
        sleep(randint(4, 8))
        all_names = []
        for nam in names:
            if "mutual friend" in nam.text:
                pass
            else:
                all_names.append(nam.text)
        cleaned_all_names = list(filter(None, all_names))
        return cleaned_all_names
    except NoSuchElementException:
        animated_loading("[+] re-collecting friends names...")
        sleep(randint(5, 8))
        get_friend_names()


# Collect and set all FB profile links form that FB names
def get_profile_link():
    try:
        animated_loading("[+] collecting profile links...")
        sleep(randint(4, 8))
        link_item = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/"
                                                 "div/div[4]/div/div/div/div/div/div/div/div/div[3]")
        links = link_item.find_elements_by_tag_name("a")
        sleep(randint(4, 8))
        all_links = []
        for link in links:
            href = link.get_attribute("href")
            if "friends_mutual" in href:
                pass
            else:
                all_links.append(href)

        cleaned_all_links = list(dict.fromkeys(all_links))
        return cleaned_all_links

    except NoSuchElementException:
        animated_loading("[+] re-collecting profile links...")
        sleep(randint(4, 8))
        get_profile_link()


# Collecting FB data: [ Names, FB Profile Links, Phone Number, Gender, Birth Day ]
def get_data_info():
    all_friends_phone_numbers = []
    all_friends_gender = []
    all_friends_date = []
    all_friends_year = []
    # Have to separate each link, because some of profile links have username, and others just default fb numbers

    for each_link in get_profile_link():
        animated_loading("[+] gathering data...")
        print("\n")
        print(f"[+] Current Link: {each_link} <<<")
        try:
            if "profile.php" in each_link:
                driver.get(url=f"{each_link}&sk=about_contact_and_basic_info")
                sleep(randint(1, 3))
                phone = driver.find_elements_by_css_selector(".d2edcug0 span")
                ph_num = []
                for pn in phone:
                    ph_num.append(pn.text)
                for pn in ph_num:
                    if pn == "Contact info":
                        item_id = ph_num.index(pn) + 1
                        all_friends_phone_numbers.append(ph_num[item_id])
                    try:
                        if pn == "Gender":
                            item_info = ph_num.index(pn) + 1
                            all_friends_gender.append(ph_num[item_info])
                        else:
                            all_friends_gender.append("No Gender Provided")
                    except NoSuchElementException:
                        pass
                    if pn == "Birth date":
                        item_date = ph_num.index(pn) - 1
                        all_friends_date.append(ph_num[item_date])
                    if pn == "Birth year":
                        item_year = ph_num.index(pn) - 1
                        all_friends_year.append(ph_num[item_year])

            else:
                driver.get(url=f"{each_link}/about_contact_and_basic_info")
                sleep(randint(1, 3))
                phone = driver.find_elements_by_css_selector(".d2edcug0 span")
                ph_num = []
                for pn in phone:
                    ph_num.append(pn.text)
                for pn in ph_num:
                    if pn == "Contact info":
                        item_id = ph_num.index(pn) + 1
                        all_friends_phone_numbers.append(ph_num[item_id])
                    try:
                        if pn == "Gender":
                            item_info = ph_num.index(pn) + 1
                            all_friends_gender.append(ph_num[item_info])
                        else:
                            all_friends_gender.append("No Gender Provided")
                    except NoSuchElementException:
                        pass
                    if pn == "Birth date":
                        item_date = ph_num.index(pn) - 1
                        all_friends_date.append(ph_num[item_date])
                    if pn == "Birth year":
                        item_year = ph_num.index(pn) - 1
                        all_friends_year.append(ph_num[item_year])
            sleep(2)
        except NoSuchElementException:
            print("No Details")
            continue
    return all_friends_phone_numbers, all_friends_gender, all_friends_date, all_friends_year


# Loading logo
art = '''
  _____  ____         ____    ____  ____      _     ____   _____  ____  
 |  ___|| __ )       / ___|  / ___||  _ \    / \   |  _ \ | ____||  _ \ 
 | |_   |  _ \  _____\___ \ | |    | |_) |  / _ \  | |_) ||  _|  | |_) |
 |  _|  | |_) ||_____|___) || |___ |  _ <  / ___ \ |  __/ | |___ |  _ < 
 |_|    |____/       |____/  \____||_| \_\/_/   \_\|_|    |_____||_| \_\
                                                                        

'''

print(art)
sleep(2)

# Calling all the functions
fb_login()
load_fb_friend_page()
fb_names = get_friend_names()
fb_links = get_profile_link()
fb_numbers, fb_gender, fb_birth_date, fb_birth_year = get_data_info()
sleep(randint(4, 8))

# Print final result in to console, also save in text file current directory
for i in range(len(fb_names)):
    data = f"{fb_names[i]} | {fb_links[i]} | {fb_numbers[i]} | {fb_gender[i]} | " \
           f"{fb_birth_date[i]}-{fb_birth_year[i]}"
    print(data)
    with open("fb_data.txt", "a", encoding="utf-8") as file:
        file.write(f"{data}\n")

# Closing the selenium driver
driver.quit()
