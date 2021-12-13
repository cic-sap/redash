import os.path
import smtplib
import time
import traceback
import logging
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium.webdriver.support.ui import WebDriverWait
from email.charset import Charset, BASE64

logger = logging.getLogger(__name__)

def inject_js(driver, *files):
    code = []
    for f in files:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/' + f, encoding='utf-8') as fp:
            code.append(fp.read())
            logger.info('inject js:%s', f)
    driver.execute_script('\n'.join(code))
    time.sleep(1)


def run():
    # demo
    public_url = 'http://server:5000/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
    webserver = 'http://127.0.0.1:4440/wd/hub'
    if 'WEB_DRIVER' in os.environ:
        webserver = os.environ['WEB_DRIVER']
    options = webdriver.ChromeOptions()
    debug = False
    if debug:
        # public_url = 'http://localhost:8080/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
        public_url = 'http://localhost:5001/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
        webserver = 'http://127.0.0.1:4444/wd/hub'
    else:
        options.add_argument('--headless')
    snapshot(public_url, webserver, debug)


def send_snapshot(email, public_url):
    debug = False
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    webserver = 'http://127.0.0.1:4440/wd/hub'
    if os.environ['WEB_DRIVER'] != '':
        webserver = os.environ['WEB_DRIVER']
    snapshot(public_url, webserver, debug, email)


def get_options(debug: bool) -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    t1 = time.time()
    if not debug:
        options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200x1600")
    return options


def snapshot(public_url, webserver, debug, email=''):
    t1 = time.time()
    driver = webdriver.Remote(
        command_executor=webserver,
        options=get_options(debug),
    )
    try:
        logger.info('start public_url:%s, webserver:%s', public_url, webserver)
        driver.get(public_url)
        logger.info('get: public_url %s ok')
        # print('screen', screen)
        # driver.save_screenshot(screen)
        # inject_js(driver, 'hack/beautify.min.js')
        inject_js(driver, 'hack/beautify-css.min.js')
        title = ''
        for i in range(30):
            logger.info('start wait h3')
            try:
                element = WebDriverWait(driver, 300).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h3"))
                )
                if not element:
                    logger.info('wait title')
                    time.sleep(3)
                    continue
                title = element.get_attribute('innerText').strip()
                logger.info('dashboard title::%s', title)
                if title == '':
                    logger.info('wait title')
                    time.sleep(3)
                    continue
                break
            except Exception as e:
                logger.exception('get exception:%e', e)
                pass
        if title == '':
            raise Exception('wait title fail!')

        element = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.email-table-layout"))
        )
        logger.info('wait email-table-layout result:%s', element)
        # //spinner
        out = WebDriverWait(driver, 600).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.spinner')),
            message='wait spinner timeout'
        )
        logger.info('get out:%s', out)

        nodes = driver.find_elements(by=By.CLASS_NAME, value='visualization-renderer')
        # nodes = driver.find_elements(by=By.CLASS_NAME, value='svg-container')
        logger.info('find ele:%d', len(nodes))
        for i, ele in enumerate(nodes):
            logger.info('rect:%d,%s', i, ele.rect)
            check = ele.find_elements(by=By.CLASS_NAME, value='svg-container')
            if len(check) == 0:
                logger.info('pass:%d', i)
                continue

            js = '''
                    let div  = document.querySelectorAll('div.visualization-renderer')[arguments[0]];
                    div.scrollIntoView()
                    '''
            logger.info('js:%s', js)
            driver.execute_script(js, i, )
            time.sleep(.5)
            logger.info('snap')
            data = ele.screenshot_as_base64
            logger.info('base64:%d', len(data))
            js = '''
             let div  = document.querySelectorAll('div.visualization-renderer')[arguments[0]];
            div.innerHTML='<img style="max-height:100%;" width="100%" src="data:image/png;base64, '+arguments[1]+'" />'
            '''
            logger.info('js:%s', js)
            driver.execute_script(js, i, data)
            time.sleep(.5)

        try:
            inject_js(driver, 'hack/CSSOM.js', 'hack/css.js')
            html = ''
            for i in range(30):
                time.sleep(1)
                html = driver.execute_script('return window.last_html')
                if html is None or len(html) < 200:
                    logger.info('wait html snapshot')
                    continue
                logger.info('get html snapshot ok')
                f = ''
                email_title = title
                if os.path.isdir('/app'):
                    f = '/app/test-%d.html' % time.time()
                    email_title = title + '-' + f
                    logger.info('write:%s,size:%s', f, len(html))
                    with open(f, 'w', encoding='utf-8') as fp:
                        fp.write(html)
                send_mail(email_title, html, email)
                break
            if html is None or len(html) < 200:
                raise Exception('wait html snapshot timeout')
        except Exception as e:
            logger.exception('get Exception', e)
            traceback.print_exc()
            time.sleep(60)
            pass
        # driver.save_screenshot("out.png")

        return {'public_url': public_url}
    except Exception as e:
        logger.exception('get Exception:%e', e)
        traceback.print_exc()
        time.sleep(60)
    finally:
        logger.info('cost time:%.2f', time.time() - t1)
        if debug:
            time.sleep(60)
        driver.quit()




def send_mail(title, html, receiver_email=''):
    if type(html) == str:
        html = html.encode('utf-8')
    #   REDASH_MAIL_SERVER: "email"
    #   REDASH_MAIL_PORT: "25"
    # Server = "host.docker.internal"
    REDASH_MAIL_SERVER = os.environ.get("REDASH_MAIL_SERVER", "localhost")
    REDASH_MAIL_PORT = int(os.environ.get("REDASH_MAIL_PORT", "2526"))

    sender_email = "dongming.shen@sap.com"
    if receiver_email == '':
        receiver_email = "dongming.shen@sap.com"
    # receiver_email = "dongming.shen@outlook.com"

    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender_email
    message["To"] = receiver_email
    logger.info('send to :%s,size,%d,smtp:%s:%d', receiver_email, len(html), REDASH_MAIL_SERVER, REDASH_MAIL_PORT)

    text = title + '(Please enable html mode)'
    utf8 = Charset(input_charset='utf-8')
    utf8.body_encoding = BASE64

    part1 = MIMEText(text, "plain", _charset=utf8)
    part2 = MIMEText(html, "html", _charset=utf8)

    message.attach(part1)
    message.attach(part2)

    if os.path.isdir('/app'):
        f = '/app/' + title.replace('/', '-') + '.eml'
        logger.info('write eml:%s', f)
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(message.as_string())
    host = smtplib.SMTP(REDASH_MAIL_SERVER, REDASH_MAIL_PORT)
    # host.debuglevel = 1
    # host.login(User, Password)
    ret = host.sendmail(
        sender_email, receiver_email, message.as_string()
    )
    print('sendmail result', ret)
    logger.info('sendmail result:%s', ret)
    time.sleep(3)

    pass


def test2():
    message = MIMEMultipart("alternative")
    message["Subject"] = 'title'
    text = 'title' + '(Please enable html mode)'
    html = '<h1>'
    part1 = MIMEText(text, "plain", _charset='utf-8')
    part2 = MIMEText(html, "html", )

    message.attach(part1)
    message.attach(part2)
    print(message.as_string())


def test1():
    text = '''<style>
        p{color:red}
        h1{color:red}</style>
        ''' * 10000
    body = '''
        <h1>hello</h1>
        ''' * 10000
    body = body + text
    print('body', len(body))
    send_mail('test-email%d' % time.time(), body)


if __name__ == '__main__':
    # send_mail('test-test-1636683693-ok.html',open('test-1636683693-ok.html',encoding='utf-8').read())
    # language:html

    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.DEBUG)
    run()
    # for i in range(60):
    #     run()
    #     time.sleep(60)
