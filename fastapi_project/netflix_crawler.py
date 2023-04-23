from concurrent.futures import ThreadPoolExecutor
import json
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import urllib
import time
from selenium.webdriver.chrome.options import Options

class NetflixCrawler:
    def __init__(self):
        options = Options()
        options.add_argument("lang=ko_KR")  # 언어 설정
        # options.add_argument("start-maximized") # 창 크기 최대로
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")    
        options.add_experimental_option('detach', True)  # 브라우저 안 닫히게
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 시스템 장치 에러 숨기기
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')  

        self.driver = webdriver.Chrome('./chromedriver.exe', options=options)
        self.languages = []
        self.id = "01046182620"
        self.pw = "@@!!zapzap12"

    def login_and_get_lang_list(self):
        print("넷플릭스 접속 중...")
        # get 명령으로 접근하고 싶은 주소 지정
        url="https://www.netflix.com/browse/original-audio"  
        self.driver.get(url)  #브라우저 접속

        #로그인 
        self.driver.implicitly_wait(5)  #대기
        self.driver.find_element(By.ID, 'id_userLoginId').send_keys(self.id)  #id값
        self.driver.find_element(By.ID, 'id_password').send_keys(self.pw)

        self.driver.find_element(By.XPATH, '//*[@id="appMountPoint"]/div/div[3]/div/div/div[1]/form/button').click()  #로그인 버튼
        self.driver.implicitly_wait(10)

        #넷플릭스 시청할 프로필 선택
        self.driver.find_elements(By.CLASS_NAME, 'profile-link')[0].click() #프로필 버튼
        print("넷플릭스 접속 완료")
        self.driver.implicitly_wait(10)

        # 언어 선택 메뉴
        language_drop_down = self.driver.find_element(By.CLASS_NAME, 'languageDropDown')
        language_drop_down.click()
        self.driver.implicitly_wait(3)

        # 언어 링크 리스트
        sub_menu_links = language_drop_down.find_elements(By.CLASS_NAME, 'sub-menu-link')

        self.languages = [sub_menu_link.get_attribute("text") for sub_menu_link in sub_menu_links]

        self.driver.close()

    def crawling_contents(self, language):
        options = Options()
        options.add_argument("lang=ko_KR")  # 언어 설정
        # options.add_argument("start-maximized") # 창 크기 최대로
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")    
        options.add_experimental_option('detach', True)  # 브라우저 안 닫히게
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 시스템 장치 에러 숨기기
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')  

        driver = webdriver.Chrome('./chromedriver.exe', options=options)

        print("넷플릭스 접속 중...")
        # get 명령으로 접근하고 싶은 주소 지정
        url="https://www.netflix.com/browse/original-audio"  
        driver.get(url)  #브라우저 접속

        #로그인 
        driver.implicitly_wait(10)  #대기
        driver.find_element(By.ID, 'id_userLoginId').send_keys(self.id)  #id값
        driver.find_element(By.ID, 'id_password').send_keys(self.pw)

        driver.find_element(By.XPATH, '//*[@id="appMountPoint"]/div/div[3]/div/div/div[1]/form/button').click()  #로그인 버튼
        driver.implicitly_wait(10)

        #넷플릭스 시청할 프로필 선택
        driver.find_elements(By.CLASS_NAME, 'profile-link')[0].click() #프로필 버튼
        print("넷플릭스 접속 완료")
        driver.implicitly_wait(10)

        # 언어 선택 메뉴
        language_drop_down = driver.find_element(By.CLASS_NAME, 'languageDropDown')
        language_drop_down.click()
        driver.implicitly_wait(3)

        language_drop_down.find_element(By.LINK_TEXT, language).click()
        driver.implicitly_wait(3)

        # 스크롤 깊이 측정하기 
        last_height = driver.execute_script("return document.body.scrollHeight") 

        # 스크롤 끝까지 내리기 
        while True:  
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
            # 페이지 로딩 기다리기 
            time.sleep(5) 
            # 더 보기 요소 있을 경우 클릭하기 
            new_height = driver.execute_script("return document.body.scrollHeight") 

            if new_height == last_height: 
                break 

            last_height = new_height 

        # 컨텐츠 id 목록 가져오기
        target_list = driver.find_elements(By.CLASS_NAME, 'slider-refocus')
        print(len(target_list))
        content_id_list = []
        for target in target_list:
            href = target.get_attribute("href").strip()
            # print(href)
            content_id = href.split("https://www.netflix.com/watch/")[1].split("?")[0]
            content_id_list.append(content_id)
        print(content_id_list)

        # id 기준으로 metadata 가져오기
        content_list = []
        for idx, content_id in enumerate(content_id_list):
            print(idx, content_id)
            url = "https://www.netflix.com/watch/{netflix_id}".format(netflix_id=content_id)
            response = requests.get(url, headers={"Accept-Language": "ko-kr"})
            soup = BeautifulSoup(response.content, "html.parser")
            metadata_script_tag = soup.find("script", type="application/ld+json")
            metadata = json.loads(metadata_script_tag.string)
            metadata["content_id"] = content_id

            content_list.append(metadata)

        print(content_list)

        data = {
            "total_count": len(content_list),
            "language": language,
            "data": content_list
        }

        with open(f'data-{language}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        driver.close()
   
    def run(self):
        self.login_and_get_lang_list()

        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.map(self.crawling_contents, ["영어"])
        
        
nfc = NetflixCrawler()
nfc.run()

# content_list = []
# content_id_list = ['81682438', '81460361', '81676321', '81672245', '81672263', '81517155', '81689378', '81450827', '81603171', '81503026', '81447461', '81671939', '81649877', '81357304', '81465109', '81503026', '81679532', '81680439', '81674880', '81493078', '81614459', '81683746', '81651389', '80991107', '81159258', '81503026', '81682438', '81671939', '81519223', '81680439', '81679532', '81683746', '81651389', '81504944', '81503026', '81682438', '81687538', '81614459', '81503026', '81410436', '81608495', '81460361', '81689378', '81517155', '81478985', '81676321', '81674880', '81460361', '81517155', '81194641', '81598180', '80242619', '80165484', '81478985', '81091393', '80238012', '81574246', '81511410', '81511687', '81278456', '81020819', '80179798', '81341928', '81239224', '81610893', '81357286', '81323914', '81568411', '81296695', '81486372', '81517188', '81280917', '81568842', '80187302', '81587446', '81193309', '81556908', '80067290', '80165295', '81486372', '80203144', '80165484', '81405844', '81457091', '81661882', '81168885', '81646769', '81650113', '81623319', '70143365', '81517188', '80214406', '81267691', '81030062', '80991107', '81510733', '81482512', '81260283', '80161700', '81340251', '80242724', '80116922', '80997343', '80234304', '81177634', '80203144', '81463556', '81222923', '70019508', '80091595', '81399639', '80011542', '81057361', '81652327', '81161926', '80163352', '81044647', '81211284', '81012510', '70143836', '80057918', '80165295', '81224926', '81205849', '81370670', '80209553', '81090386', '80241318', '81357268', '80203144', '80231442', '80027042', '81237994', '81646769', '81614145', '81646770', '81623319', '81667052', '81639613', '81646757', '81646760', '81646755', '81609065', '81521115', '81650113', '80216781', '81280962', '70170417', '70259456', '81161926', '60023642', '70028883', '80068209', '81518991', '80057281', '80186863', '81628859', '81486372', '81435649', '80117291', '81517168', '81105888', '81517168', '80990668', '81280917', '81323551', '80188833', '81350913', '81661882', '81357268', '81639613', '81413647', '81061734', '81177545', '81610166', '81365087', '81486374', '81193309', '80214406', '80990381', '80174608', '81020819', '81261669', '81040344', '80113037', '81511704', '81275353', '81256675', '81287562', '70201181', '70299544', '81342504', '81370441', '70270715', '80177865', '80208531', '81280962', '81019389', '81492861', '81680066', '81436209', '81683307', '81672318', '81341876', '81425164', '81176026', '81437299', '80163352', '81504496', '70101374', '81511779', '70143365', '81489837', '81199145', '81160697', '81639613', '80179798', '70195800', '81642342', '80045948', '70177057', '81011508', '80214406', '80027042', '81457086', '81106901', '60023642', '70159333', '80208531', '80221908', '81105789', '81336431', '80068209', '81157374', '81437733', '80987077', '81205849', '81267633', '81144925', '81159258', '81237994', '81403973', '81610895', '81397558', '81011211', '81054853', '80002479', '80192098', '80177458', '81502485', '60024206', '70270998', '81640988', '80224105', '80081961', '80113804', '81457086', '70270998', '81105789', '70291334', '81324206', '70299043', '80107103', '81442520', '80023687', '80992228', '80117291', '80063153', '80050063', '80186926', '70224562', '80187163', '70205125', '70043301', '70116706', '80239019', '80014426', '81172898', '70044873', '81572781', '81610897', '81349896', '81443941', '81037371', '81647228', '81340251', '80199128', '81025696', '81482494', '81568400', '81167137', '70283264', '80188730', '81030241', '80156759', '80192098', '80098478', '81199145', '81198933', '81439253', '70307658', '80187362', '81404278', '80211726', '81488657', '70217910', '81312802', '70204995', '80200575', '81410834', '70024218', '81287006', '81054853', '81205849', '81461539', '80099081', '81283663', '81198916', '81628965', '81648721', '70033005', '81648576', '81458416', '80217525', '81010699', '80117824', '81160697', '81105952', '81198948', '80092171', '81646760', '80170613', '81324206', '80166224', '81422314', '81293372', '80156759', '81149450', '81394573', '81394625', '80154882', '81313229', '80242619', '80214406', '80117291', '80199128', '80116922', '80236133', '80242619']
# for idx, content_id in enumerate(content_id_list[:1]):
#     print(idx, content_id)
#     url = "https://www.netflix.com/watch/{netflix_id}".format(netflix_id=content_id)
#     response = requests.get(url, headers={"Accept-Language": "ko-kr"})
#     soup = BeautifulSoup(response.content, "html.parser")
#     print(soup)
#     metadata_script_tag = soup.find("script", type="application/ld+json")
#     metadata = json.loads(metadata_script_tag.string)
#     print(metadata)

#     content_list.append(metadata)

# print(content_list)

# data = {
#     "data": content_list
# }

# with open('data.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)

