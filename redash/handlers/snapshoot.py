import time

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def get_js():
    return '''
    (function () {
    /**
     * download file
     * @param {String} filename - filename, any illetal character will be replaced with underline
     * @param {String} text - file content
     */
    function download(filename, text) {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }


    /**
     * 简单的 xhr get 请求
     * @param {String} url
     * @return {Promise}
     */
    function simpleGet(url) {
        return new Promise(function(resolve, reject) {
            const xhr = new XMLHttpRequest();
            xhr.onload = function() {
                resolve(this.responseText);
            };
            xhr.onabort = function() {
                reject(`reason=abort; url=${url}`);
            };
            xhr.onerror = function() {
                reject(`reason=error; url=${url}`);
            };
            xhr.ontimeout = function() {
                reject(`reason=timeout; url=${url}`);
            };
            xhr.open('get', url, true);
            xhr.send();
        });
    }


    function inlineSameOriginExternalStyles() {
        styles = Array.from(document.getElementsByTagName('link'))
            .filter(function(node) {
                return (node.rel == 'stylesheet' || node.type == 'text/css')
                    && (new URL(node.href)).origin == location.origin;
            });
        return Promise.all(styles.map(function(node) {
            const url = node.href;
            return simpleGet(url)
                .then(function(value) {
                    const c = document.createComment(url)
                    node.parentNode.insertBefore(c, node);
                    const n = document.createElement('style');
                    n.type = 'text/css';
                    n.innerHTML = value;
                    node.parentNode.insertBefore(n, node);
                    node.remove();
                });
        }));
    }


    function getHTML() {
        return '<!doctype html>\n<!-- ' + location.href + ' -->\n' + document.documentElement.outerHTML;
    }


    function normalizeURL(text) {
        // //... => http(s)://...
        text = text.replace(/(\s*(href|src)\s*=\s*['"])(\/\/[^/])/gi, `$1${location.protocol}$3`);
        // /a/b => http(s)://x.com/a/b
        text = text.replace(/(\s*(href|src)\s*=\s*['"])(\/[^/])/gi, `$1${location.origin}$3`);
        const baseURL = new URL('./', location.href).href;
        // ./a/b => http(s)://x.com/c/a/b
        text = text.replace(/(\s*(href|src)\s*=\s*['"])\.\/([^/])/gi, `$1${baseURL}$3`);
        // ../a/b => http(s)://x.com/c/../a/b
        text = text.replace(/(\s*(href|src)\s*=\s*['"])(\.\.\/[^/])/gi, `$1${baseURL}$3`);
        // a/b => http(s)://.../a/b
        text = text.replace(/(\s*(href|src)\s*=\s*['"])([^:./'"]+[/'"])/gi, `$1${baseURL}$3`);
        return text;
    }


    function omitScript(text) {
        return text.replace(/(<script (.|\n)+?<\/script>|<script>(.|\n)+?<\/script>)/gi, '<!-- script -->');
    }


    function omitIframeSrc(text) {
        return text.replace(/(<iframe [^>]*?src\s*?=\s*?['"]).+?(['"].+?<\/iframe>)/gi, '$1$2');
    }


    function dumpCSSText(element) {
        var s = '';
        var o = getComputedStyle(element);
        for (var i = 0; i < o.length; i++) {
            s += o[i] + ':' + o.getPropertyValue(o[i]) + ';';
        }
        return s;
    }


    function clean_elements(){
        document.querySelectorAll('*[style*="display: none;"]')
    }

    {
                inlineSameOriginExternalStyles()
                    .then(function() {
                        text = getHTML();
                        text = omitScript(text);
                        text = omitIframeSrc(text);
                        text = normalizeURL(text);

                        filename = location.href + '-' + (new Date()).toISOString() + '.html';
                        download(filename, text);

                        sendResponse({
                            ok: true
                        });
                    })
                    .onerror(function(reason) {
                        console.log(`SNAPSHOT AS HTML ERROR: ${reason}`);
                    });
            }



})()
    '''
def run():
    # public_url = 'http://localhost:8080/public/email-dashboards/czUPwJVQW09FwJr7pQl6kI2PuqqySnfvjwwWT2cv?org_slug=default'
    public_url = 'http://localhost:8080/public/dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
    public_url = 'http://localhost:8080/public/email-dashboards/5psvb8ozcfwlfAwuvA1rSfH5ukdxegdpvPSrzyZ4?org_slug=default&p_TimeRange=LastWeek&p_project=ome'
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        options=webdriver.ChromeOptions(),
    )
    driver.get(public_url)

    time.sleep(3)

    eles = driver.find_elements(by=By.CLASS_NAME, value='visualization-renderer')
    # eles = driver.find_elements(by=By.CLASS_NAME, value='svg-container')
    print('find ele',len(eles))
    for i, ele in enumerate(eles):
        print('rect', i, ele.rect)

        check = ele.find_elements(by=By.CLASS_NAME, value='svg-container')
        if len(check) == 0:
            print('pass',i)
            continue

        js = '''
                let div  = document.querySelectorAll('div.visualization-renderer')[arguments[0]];
                div.scrollIntoView()
                '''
        print('js', js)
        driver.execute_script(js, i,)
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
    except:
        pass
    # driver.save_screenshot("out.png")

    time.sleep(1800)
    return {'public_url': public_url}


if __name__ == '__main__':
    run()
