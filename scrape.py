from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
def scrapeTopGames(hl, gl):
    try:
        options = Options()
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage") 
        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)
        driver.get("https://play.google.com/store/games?hl="+hl+"&gl="+gl)
        categories = driver.find_elements(By.XPATH, "//div[@class = 'kW9Bj']")
        categories = categories[len(categories)-3:]
        allApps = {
            'category' : [],
            'top' : {}
        }
        for category in categories:
            allApps['category'].append(category.text)
            category.click()
            apps = []
            time.sleep(1)
            anchorTags = driver.find_elements(By.XPATH, "//a[@class = 'Si6A0c itIJzb']")
            anchorLinks = []
            imageTags = driver.find_elements(By.XPATH, "//img[@class = 'T75of stzEZd']")
            for anchor in anchorTags:
                anchorLinks.append(anchor.get_attribute('href'))
                # print(anchor.text)
            for line in range(len(anchorLinks)):
                topApps = anchorTags[line].text.split('\n')
                game = {}
                game['name']=topApps[1]
                game['type']=topApps[2]
                game['rating']=topApps[3]
                game['link']=anchorLinks[line]
                game['logo']=imageTags[line].get_attribute('src')
                game['key']=anchorLinks[line][anchorLinks[line].index('=')+1:]
                apps.append(game)
            allApps['top'][category.text] = apps

        # print(allApps)
    except:
        # print("error")
        driver.quit()
        return None

    driver.quit()
    return allApps  


def getAppDetails(id, hl, gl):
    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    url = 'https://play.google.com/store/apps/details?id=' + id + "&hl="+hl+"&gl="+gl
    driver.get(url)
    details = []
    try:
        game = {}
        desc = driver.find_element(By.CLASS_NAME, "bARER")
        game['desc'] = desc.text
        allImg = driver.find_elements(By.XPATH, "//img[@class = 'T75of B5GQxf']")
        images = []
        for img in allImg:
            images.append(img.get_attribute('src'))
        game['images'] = images
        details.append(game)
    except:
        pass

    driver.quit()
    return details