import os.path
import smtplib
import time

import cssutils

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import WebDriverWait


def get_js():
    with open(os.path.dirname(__file__) + '/hack/css.js', encoding='utf-8') as fp:
        text = fp.read()
        return text


def inject_js(driver, *files):
    code = []
    for f in files:
        with open(os.path.dirname(__file__) + '/' + f, encoding='utf-8') as fp:
            code.append(fp.read())
            print('inject js', f)
    driver.execute_script('\n'.join(code))
    time.sleep(1)


def run():
    public_url = 'http://server:5000/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
    webserver = 'http://127.0.0.1:4440/wd/hub'
    options = webdriver.ChromeOptions()
    debug = False
    if debug:
        # public_url = 'http://localhost:8080/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
        public_url = 'http://localhost:5001/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
        webserver = 'http://127.0.0.1:4444/wd/hub'
    else:
        options.add_argument('--headless')
    snapshot(public_url, webserver, debug)


def snapshot(public_url, webserver, debug):
    options = webdriver.ChromeOptions()
    t1 = time.time()
    if not debug:
        options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200x1600")
    driver = webdriver.Remote(
        command_executor=webserver,
        options=options,
    )
    try:
        print('start ', public_url, 'webserver', webserver)
        driver.get(public_url)
        print('get', public_url, 'ok')
        screen = 'new-%d.png' % time.time()
        # print('screen', screen)
        # driver.save_screenshot(screen)
        inject_js(driver, 'hack/beautify.min.js')
        inject_js(driver, 'hack/beautify-css.min.js')

        for i in range(10):
            print('start wait h3')
            try:
                element = WebDriverWait(driver, 300).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h3"))
                )
                if not element:
                    print('wait title')
                    continue
                title = element.get_attribute('innerText').strip()
                print('dashboard title:', element.get_attribute('innerText'), element.get_attribute('innerHTML'))
                if title == '':
                    print('wait title')
                    continue
                break
            except Exception as e:
                print('get exception', e)
                pass
        if title == '':
            raise Exception('wait title fail!')

        element = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.email-table-layout"))
        )
        print('wait email-table-layout', element)

        screen = 'new-%d.png' % time.time()
        print('screen', screen)
        # driver.save_screenshot(screen)

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
            inject_js(driver, 'hack/CSSOM.js', 'hack/css.js')

            for i in range(30):
                time.sleep(1)
                html = driver.execute_script('return window.last_html')

                if html is None or len(html) < 200:
                    print('wait html snapshot')
                    continue
                print('get html snapshot ok')
                f = 'test-%d.html' % time.time()
                print('write', f, 'size', len(html), type(html))
                with open(f, 'w', encoding='utf-8') as fp:
                    fp.write(html)
                send_mail(title + '-' + os.path.basename(f), html)
                break
            if html is None or len(html) < 200:
                raise Exception('wait html snapshot timeout')
        except Exception as e:
            print('get Exception', e)
            time.sleep(60)
            pass
        # driver.save_screenshot("out.png")

        return {'public_url': public_url}
    except Exception as e:
        print('get Exception', e)
        time.sleep(60)

    finally:
        print('cost time:', time.time() - t1)
        if debug:
            time.sleep(60)
        driver.quit()


def send_mail(title, html):
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    Server = "localhost"
    # Server = "host.docker.internal"
    Port = 2526
    User = "admin"
    Password = "admin"

    sender_email = "dongming.shen@sap.com"
    receiver_email = "dongming.shen@sap.com"

    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender_email
    message["To"] = receiver_email
    print('send to ', receiver_email, 'size:', len(html))
    text = 'Please enable html mode'
    part1 = MIMEText(text, "plain", _charset='utf-8')
    part2 = MIMEText(html, "html", _charset='utf-8')

    message.attach(part1)
    message.attach(part2)

    host = smtplib.SMTP(Server, Port)
    # host.debuglevel = 1
    # host.login(User, Password)
    ret = host.sendmail(
        sender_email, receiver_email, message.as_string()
    )
    print('sendmail result', ret)
    time.sleep(3)

    pass


if __name__ == '__main__':
    # send_mail('test-test-1636683693-ok.html',open('test-1636683693-ok.html',encoding='utf-8').read())
    # send_mail('test-1636682536-err.html',open('test-1636682536-err.html',encoding='utf-8').read())
    for i in range(60):
        run()
        time.sleep(60)
