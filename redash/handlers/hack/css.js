(function () {
  function css_is_used(css) {
    // return true;
    if (!css) {
      return true
    }
    if (css.indexOf(':') !== -1) {
      console.log('old css name', css)
      css = css.replace(/:+[a-zA-Z0-9_-]+/g, '')
      console.log('new css name', css)
    }

    let arr = css.split(',')
    if (arr.length > 1) {
      for (let i = 0; i < arr.length; i++) {
        if (css_is_used(arr[i])) {
          return true
        }
      }
    } else {
      try {
        if (document.querySelector(css)) {
          return true
        }
      } catch (e) {
        console.log('err', css, e)
        return true
      }

      let arr = css.split(/[ >+]/);
      if (arr.length > 1) {
        for (let i = 0; i < arr.length; i++) {
          if (css_is_used(arr[i])) {
            return true
          }
        }
      }
    }
    return false
  }

  let node = document.documentElement

  function clean_unused(cssText) {
    //let parser = new cssjs();
    let parser = CSSOM.parse(cssText);

    // let rules = parser.parseCSS(cssText)
    console.log('raw input', cssText.length, 'rules', parser.cssRules.length, cssText)

    for (let i = 0; i < parser.cssRules.length; i++) {

      let item = parser.cssRules[i]
      console.log('check:', item.selectorText)
      if (!css_is_used(item.selectorText)) {
        console.log('clean:', item.selectorText)
        parser.cssRules.splice(i, 1)
        i--
      }
    }
    let out = parser.toString()
    console.log('raw output', out.length, out)
    return out
  }

  function split_css(css, buf, max_length) {
    top1:
      while (css.length > max_length) {
        for (let i = max_length; i > 0; i--) {
          if (css.substr(i, 2) == '}\n') {
            let text = css.substr(0, i + 2)
            if (text.length > 0) {
              buf.push(text)
            }
            css = css.substr(i + 2)
            continue top1
          }
        }
        break
      }
    if (css.length > 0) {
      buf.push(css)
    }
    return buf
  }

  function check_rules() {
    let all = []
    let count = 0
    //clean
    try {

      console.log('all count', count)

      let styles = document.getElementsByTagName('style');
      console.log('before remove style len', document.getElementsByTagName('style').length)
      let parent;
      for (let i = styles.length - 1; i >= 0; i--) {
        let s = styles[i]
        // s.innerHTML = newCss
        console.log('old css:', s.innerHTML)

        // split_css(css_beautify(clean_unused(s.innerHTML)), all, 150)
        all.push(css_beautify(clean_unused(s.innerHTML)))

        //s.innerHTML = clean_unused(s.innerHTML)
        console.log('new css:', s.innerHTML)

        parent = s.parentElement;
        parent.removeChild(s)
      }
      for (let i = 0; i < all.length; i++) {
        let n = document.createElement('style')
        n.id = 'css-' + i + '-' + all[i].length;
        n.type = 'text/css';
        n.innerHTML = all[i]
        parent.appendChild(n)

      }

    } catch (e) {
      console.log('get e', e)
    }

  }

  function ok(text) {

    window.last_html = text
    let filename = location.href + '-' + (new Date()).toISOString() + '.html';
    download(filename, text);
  }

  function download(filename, text) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }

  function inlineSameOriginExternalStyles() {

    function simpleGet(url) {
      return new Promise(function (resolve, reject) {
        const xhr = new XMLHttpRequest();
        xhr.onload = function () {
          resolve(this.responseText);
        };
        xhr.onabort = function () {
          reject(`reason=abort; url=${url}`);
        };
        xhr.onerror = function () {
          reject(`reason=error; url=${url}`);
        };
        xhr.ontimeout = function () {
          reject(`reason=timeout; url=${url}`);
        };
        xhr.open('get', url, true);
        xhr.send();
      });
    }

    styles = Array.from(document.getElementsByTagName('link'))
      .filter(function (node) {
        return (node.rel == 'stylesheet' || node.type == 'text/css')
          && (new URL(node.href)).origin == location.origin;
      });
    return Promise.all(styles.map(function (node) {
      const url = node.href;
      console.log('load css url:', url)
      return simpleGet(url)
        .then(function (value) {
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

  inlineSameOriginExternalStyles().then(function () {
    check_rules()

    let cleans = document.querySelectorAll('.loading-indicator');
    for (let i = 0; i < cleans.length; i++) {
      let e = cleans[i];
      e.parentElement.removeChild(e)
    }

    setTimeout(function () {
      let text = node.outerHTML
      text = omitScript(text);
      text = omitIframeSrc(text);
      text = normalizeURL(text);


      ok('<!doctype html>\n<!-- ' + location.href + ' -->\n' + text);
    }, 6000)
  })


})()
