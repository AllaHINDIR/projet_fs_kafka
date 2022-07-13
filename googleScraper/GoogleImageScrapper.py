# import selenium drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# import helper libraries
import time
import os
from saveimage import save_image



class GoogleImageScraper():

    def __init__(self, image_path, search_key="Donald Trump", number_of_images=1):

        # check parameter types
        image_path = os.path.join(image_path, search_key['name'])
        # image_path = os.path.join(image_path, search_key)
        if (type(number_of_images) != int):
            print("[Error] Number of images must be integer value.")
            return
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)

        # check if chromedriver is updated
        try:
            options = Options()
            options.add_argument("headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
        except Exception as e:
            print("[EXCEPTION] There is an exception !")
            print(str(e))
            exit()

        self.driver = driver
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.image_path = image_path
        self.url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947" % (search_key['name'])

    def find_image_urls(self):
        """
        cette fonction consiste à chercher et parcourir les images sur google images, puis les stocker sur la base de données
        une fois qu'elles sont vérifiées.
        :return: la liste des liens des images récupérées.
        """
        print("[INFO] Scraping for image link... Please wait.")
        image_urls = []
        count = 0
        number_of_unable_click = 0
        self.driver.get(self.url)
        time.sleep(1.5)
        numero_image = 1
        while self.number_of_images > count:
            if numero_image > self.number_of_images * 2:
                print('[ATTENTION] Research stoped because of numbre of image scrolled : ', self.search_key)
                break
            try:
                # find and click image
                imgurl = self.driver.find_element_by_xpath(
                    '//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (str(numero_image)))
                imgurl.click()
                number_of_unable_click = 0
            except Exception:
                # print("[-] Unable to click this photo.")
                number_of_unable_click = number_of_unable_click + 1
                if (number_of_unable_click > 10):
                    print("[INFO] No more photos.")
                    break

            try:
                # select image from the popup
                time.sleep(1)
                class_names = ["n3VNCb"]
                images = [self.driver.find_elements_by_class_name(class_name) for class_name in class_names if
                          len(self.driver.find_elements_by_class_name(class_name)) != 0][0]

                for image in images:
                    # only download images that starts with https
                    src_link = image.get_attribute("src")
                    if ("https" in src_link):
                        print("[INFO] %d. %s" % (count, src_link))
                        if save_image.save_image(src_link, count, self.image_path, self.search_key['name'],self.search_key['profession']):
                            image_urls.append(src_link)
                            count += 1
                            break
            except Exception:
                print("[INFO] Unable to get link")

            try:
                # scroll page to load next image
                if (count % 3 == 0):
                    self.driver.execute_script("window.scrollTo(0, " + str(numero_image * 60) + ");")
                element = self.driver.find_element_by_class_name("mye4qd")
                element.click()
                print("[INFO] Loading more photos")
                time.sleep(1.5)
            except Exception:
                time.sleep(1)
            numero_image += 1
        self.driver.quit()
        print("[INFO] Google search ended")
        return image_urls



