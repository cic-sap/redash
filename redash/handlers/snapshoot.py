import os.path
import time

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import WebDriverWait


def get_js():
    with open(os.path.dirname(__file__) + '/clean.js', encoding='utf-8') as fp:
        text = fp.read()
        return text


def run():
    # public_url = 'http://localhost:8080/public/email-dashboards/czUPwJVQW09FwJr7pQl6kI2PuqqySnfvjwwWT2cv?org_slug=default'
    public_url = 'http://localhost:8080/public/dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
    public_url = 'http://localhost:8080/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
    public_url = 'http://server:5000/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200x1200")
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4440/wd/hub',
        options=options,
    )
    try:
        print('start ', public_url)
        driver.get(public_url)
        screen = 'new-%d.png' % time.time()
        print('screen', screen)
        driver.save_screenshot(screen)
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        print('dashboard title:', element.get_attribute('innerHTML'))

        screen = 'new-%d.png' % time.time()
        print('screen', screen)
        driver.save_screenshot(screen)

        # //spinner
        out = WebDriverWait(driver, 600).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.spinner')),
            message='wait spinner timeout'
        )
        print('get out', out)

        eles = driver.find_elements(by=By.CLASS_NAME, value='visualization-renderer')
        # eles = driver.find_elements(by=By.CLASS_NAME, value='svg-container')
        print('find ele', len(eles))
        for i, ele in enumerate(eles):
            print('rect', i, ele.rect)

            check = ele.find_elements(by=By.CLASS_NAME, value='svg-container')
            if len(check) == 0:
                print('pass', i)
                continue

            js = '''
                    let div  = document.querySelectorAll('div.visualization-renderer')[arguments[0]];
                    div.scrollIntoView()
                    '''
            print('js', js)
            driver.execute_script(js, i, )
            time.sleep(1)
            print('snap')
            data = ele.screenshot_as_base64
            print('base64', len(data))
            js = '''
             let div  = document.querySelectorAll('div.visualization-renderer')[arguments[0]];
            div.innerHTML='<img style="max-height:100%;" width="100%" src="data:image/png;base64, '+arguments[1]+'" />'
            '''
            print('js', js)
            driver.execute_script(js, i, data)

        try:
            driver.execute_script(get_js())
            for i in range(30):
                time.sleep(1)
                html = driver.execute_script('return window.last_html')
                if html == "":
                    print('wait html snapshot')
                    continue
                f = 'test-%d.html' % time.time()
                print('write', f)
                with open(f, 'w', encoding='utf-8') as fp:
                    fp.write(html)
                break
        except:
            pass
        # driver.save_screenshot("out.png")

        return {'public_url': public_url}
    finally:
        driver.quit()


if __name__ == '__main__':
    run()
