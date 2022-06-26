from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time, pickle, datetime, random
import pandas as pd
import numpy as np

my_id = ''
my_pw = ''

def my_click(xpath):
    """ xpath 입력 시 해당 부분 클릭 """
    driver.find_element_by_xpath(xpath).click()


def my_input(xpath, keyword):
    """ xpath랑 입력할 단어 """
    driver.find_element_by_xpath(xpath).send_keys(keyword)


def initial_setting():
    """ 크롬드라이버 켜고 초기 세팅 진행 """

    global driver

    # # 옵션 생성
    # options = webdriver.ChromeOptions()
    # # 창 숨기는 옵션 추가
    # options.add_argument("headless")
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--no-sandbox')
    # driver = Chrome('chromedriver.exe', options=options)
    
    driver = Chrome('chromedriver.exe')
    ## 로딩안되면 5초동안은 기다리기
    driver.implicitly_wait(5)

    driver.get('https://www.skku.edu/skku/')

    time.sleep(1)

    ## 로그인 버튼 클릭
    try:
        my_click('//*[@id="item_body"]/div[2]/div[1]/div/ul/li[4]/a')
    except:
        pass

    try:
        my_click('//*[@id="item_body"]/div[1]/div[1]/div/ul/li[4]/a')
    except:
        pass

    try:
        my_click('//*[@id="item_body"]/div/div[1]/div[1]/div/ul/li[4]/a')
    except:
        print('로그인을 할 수 없습니다. 담당자에게 알려주시기 바랍니다.')
        restart_bot(1, rep=1)


    ## 아이디, 패스워드 입력
    driver.switch_to.window(driver.window_handles[1])
    my_input('//*[@id="userid"]', my_id)
    my_input('//*[@id="userpwd"]', my_pw)
    my_click('//*[@id="loginBtn"]')

    time.sleep(3)

    # 메일들어가기
    time.sleep(1)
    # driver.get('https://mail3.skku.edu/portal.nsf/menulist_new?readform&comtype=&selnodecode=&count=1000&menu=MAIL&expand=&node=2&content=/mail_h/riasmster.nsf/view?readform&viewtitle=&dhxr1630651509134#')
    # my_click('//*[@id="mypage"]/form[1]/div/div[1]/div[2]/div/ul/li[2]/a')
    # time.sleep(3)
    # my_click('//*[@id="treebox_A02"]/div/table/tbody/tr[3]/td[2]/table')

    print('초기 세팅 완료')


def read_gsheet():
    """ 구글 스프레드 링크로 불러오기 """
    sheet_id = ''
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv'
    dat = pd.read_csv(url)
    return dat


def data_cleaning(df):
    """ 아웃풋 순서 (timestamp, name, email, subject, total_price)
        dictionary 형태로 반환
    """
    studentTF = df['신청 유형']=='학생'
    applyTF = df[['수강 과목 [2/10(목)-2/11(금) / SPSS 특강]', '수강 과목 [2/14(월)-2/16(수) / R 특강]',\
                     '수강 과목 [2/17(목)-2/18(금) / R 빅데이터 특강]']] == '신청'

    if studentTF==True:
        total_price = applyTF.dot([100000, 180000, 150000])
    elif studentTF==False:
        total_price = applyTF.dot([150000, 300000, 200000])
    total_price = str(total_price)
    total_price = total_price[:3]+','+total_price[3:]

    subject = ', '.join(np.array(['SPSS 특강', 'R 기초 특강', 'R 빅데이터 특강'])[applyTF])

    name = df['성명'].lstrip()
    email = df['이메일 주소'].lstrip()
    timestamp = df['타임스탬프'].lstrip()


    address = df['주소 '].lstrip()
    zipcode = df['우편번호'].lstrip()


    # f'[수강 신청강좌 : {subject} / 총 입금금액 : {total_price}원]'
    # f'[주소] {address} ({zipcode})'

    dic = {'timestamp':timestamp, 'name':name, 'email':email,
            'subject':subject, 'total_price':total_price,
            'address':address, 'zipcode':zipcode}
    time.sleep(3)
    return dic


def send_mail(dic):
    """ 메일 보내는 부분 """

    title_text = '[성균관대학교 응용통계연구소] 수강료 납부에 대한 안내 메일입니다.'
    main_text = f'''
<font face="돋움">안녕하세요, 성균관대학교 응용통계연구소 입니다.

2022년 여름 온라인 통계특강을 신청해주셔서 감사합니다.
(이번 특강의 경우, webex를 통한 실시간 양방향 온라인 강의로 진행됩니다.)

<b>저희 연구소 입금계좌는 
[우리은행 1006-101-468527 성균관대학교]이며,</b>
 
수강료는 한 강좌당, 등록비 1만원을 포함하여  

SPSS: 학생 100,000원, 일반 150,000원
R 기초: 학생 180,000원, 일반 300,000원
R 빅데이터: 학생 150,000원, 일반 200,000원
※ 학생(대학원생, 타대학 학부/대학원생 모두 포함)

입니다.

강좌 당, 등록비 1만원은 환불이 불가하며 수강 취소로 인한 환불 규정은 아래와 같습니다.

절차 상의 문제로 강좌 기간 이후 일괄 환불될 예정으로 환불이 늦어질 수 있는점 을 고려하여서 입금 부탁드립니다.

1. 신청 마감일(7/27) 이전 환불시 각 강좌당 등록비 1만원 제외하고 환불됩니다. 
2. 신청 마감일(7/27) 이후 환불시 각 강좌당 교재비, 등록비 포함 3만원 제외하고 환불됩니다.

그리고 저희가 수강료 납부자를 확인 할 수 있도록 수강하시는 분의 성함으로 보내주시거나,
수강하시는 분의 성함이 아닐 경우 예금주 명을 메일로 알려주시기 바랍니다.

-------------------------------------------------------------------------------------------
<b>
[수강 신청강좌 : {dic['subject']} / 총 입금금액 : {dic['total_price']}원]

[주소] {dic['address']}

(SPSS 강좌의 경우 기입하신 주소로 교재를 보내드릴 예정이며, R기초와 R빅데이터 강의 교재는 현장에서 제공됩니다.)

<u>
입금 기한은 원활한 특강 준비를 위해<font color="red"> 7월 27일 23시59분</font> 까지입니다.</u></b>

다만, 정원 초과시, 조기마감될 수 있는 점 양해부탁드립니다.
이 점 고려하여, 수강을 희망하시는 분들께서는 입금을 서둘러주시면 감사하겠습니다. 
강좌당 기준 인원 미달 시 폐강 될 수 있으며, 폐강 시 전액 환불해드릴 예정입니다.

감사합니다.

응용통계연구소 드림.</font>'''

    # my_click('/html/body/form/div/div/div/div[1]/ul[1]/li/a')
    my_click('//*[@id="mypage"]/form[1]/div/div[2]/div[2]/div[1]/div/div[4]/section/div[3]/div/div[3]/a') #밖에서클릭
    # my_click('/html/body/form/div/div/div/div[1]/ul[1]/li/a') #보낸메일함에서 클릭

    driver.switch_to.window(driver.window_handles[2])

    ## 받는 사람 입력
    my_input('//*[@id="inSendTo"]', dic['email'])
    time.sleep(1)
    ## 제목 입력
    my_input('//*[@id="DisSubject"]/input', title_text)
    ## 내용입력
    ## 본문 접근이 안되서 위에서 tab으로 접근
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="DisSubject"]/input').click()
    time.sleep(1)
    actions = ActionChains(driver)
    actions.key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).\
        key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).\
        key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).\
        key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).\
        key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).key_down(Keys.TAB).pause(0.2).\
        send_keys(Keys.ENTER).pause(1).send_keys(main_text).pause(2).key_down(Keys.TAB).send_keys(Keys.ENTER).perform()
    
    time.sleep(3)

    ## 보내기 버튼 클릭
    # my_click('//*[@id="GWpop"]/div[1]/div[1]/a[1]') #보내기버튼
    my_click('//*[@id="GWpop"]/div[1]/div[1]/a[5]') #닫기버튼 테스트용
    time.sleep(3)
    # driver.switch_to_alert().accept()
    driver.switch_to.alert.accept()
    driver.switch_to.window(driver.window_handles[1])


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def num_of_sentmail():
    try:
        dat = pd.read_csv('sent_mail_box.csv', index_col=0, encoding='CP949')
    except:
        dat = pd.DataFrame()
    return len(dat)


def save_sentmail(dic):
    try:
        save_dat = pd.read_csv('sent_mail_box.csv', index_col=0, encoding='CP949')
    except:
        save_dat = pd.DataFrame()

    temp_dat = pd.DataFrame.from_dict(dic, orient='index').T
    save_dat = pd.concat([save_dat, temp_dat], axis=0)
    save_dat.to_csv('sent_mail_box.csv',encoding='CP949')
    print(f'총 보낸 인원수: {len(save_dat)}명입니다. 보낸 기록을 저장하였습니다.')
    time.sleep(5)
    

def print_sent_result(dic):
    timestamp = dic['timestamp']
    name = dic['name']
    print(f'{timestamp}에 들어온 신청에 대해 {name}님께 메일을 발송하였습니다.{now()}')


def print_monitoring():
    randint = random.randint(1,3)
    # randint=1
    if randint == 1:
        right = '('
        left = ')'
    elif randint == 2:
        right = '['
        left = ']'
    else:
        right = left = ' '
    print(f'<실시간 확인 중입니다. 새로운 신청이 없습니다.>{right}{now()}{left}',end='\r')


def restart_bot(i, rep = 500):
    if i % rep == 0:
        driver.quit()
        time.sleep(3)
        initial_setting()
        print(f'<프로그램을 재부팅 하였습니다.>{now()}')
    else:
        pass


def main():
    initial_setting()
    n = 1
    while True:
        try:
            data = read_gsheet()
        except:
            print(f'구글 드라이브 사용중, 잠시 멈추기.{now()}')
            pass
            
        old_count = num_of_sentmail()
        new_count = len(data)

        wait = new_count - old_count
        if wait > 0:
            for i in range(wait):
                dic = data_cleaning(data.iloc[old_count + i])
                send_mail(dic)
                print_sent_result(dic)
                save_sentmail(dic)

        else:
            print_monitoring()
            n += 1

        time.sleep(5)
        restart_bot(n, rep=2500) # 프로그램 재시작

if __name__ == "__main__":
    main()

