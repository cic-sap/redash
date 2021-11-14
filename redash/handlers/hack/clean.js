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


  function inlineSameOriginExternalStyles() {
    styles = Array.from(document.getElementsByTagName('link'))
      .filter(function (node) {
        return (node.rel == 'stylesheet' || node.type == 'text/css')
          && (new URL(node.href)).origin == location.origin;
      });
    return Promise.all(styles.map(function (node) {
      const url = node.href;
      console.log('load css url:',url)
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


  function load_js(js) {
    return new Promise(function (ok, reject) {
      let tag = document.createElement('script')
      tag.src = js
      tag.onload = function () {
        console.log('load js ok', js)
        ok()
      }
      tag.onerror = reject
      document.getElementsByTagName('head')[0].appendChild(tag)
    })
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

  function css_is_used(css) {
    return true
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

  // Dump all document.styleSheets[*].cssRules[*].cssText to console:

  (function (s, c, r, i, j) {
    for (i = 0; i < s.length; i++) {
      c = s[i].cssRules;
      for (j = 0; j < c.length; j++) {
        r = c[j].cssText;
        console.log('document.styleSheets[' + i + '].cssRules[' + j + '].cssText = "' + r + '";')
      }
    }
  })(document.styleSheets);

  function check_rules() {
    let all = []
    let count = 0
    //clean
    for (let i = 0; i < document.styleSheets.length; i++) {
      let s = document.styleSheets[i];
      let buf = []
      for (let j = s.cssRules.length - 1; j >= 0; j--) {

        if (!css_is_used(s.cssRules[j].selectorText)) {
          console.log('remove', s.cssRules[j].selectorText,s.cssRules[j].cssText)

          s.deleteRule(j)
        } else {
          buf.push(s.cssRules[j].cssText)
        }
      }
      if (s.cssRules.length === 0) {
        s.disabled = true
      }
      if (buf.length > 0) {
        count += buf.length
        // all.push(css_beautify(buf.join("\n")));
        console.log('add css', buf.join("\n"))
        all.push(buf.join("\n"));
      }

    }
    try {

      console.log('all count', count)

      let styles = document.getElementsByTagName('style');
      console.log('before remove style len', document.getElementsByTagName('style').length)
      let parent;
      for (let i = styles.length - 1; i >= 0; i--) {
        let s = styles[i]
        // s.innerHTML = newCss
        parent = s.parentElement
        //parent.removeChild(s)
      }
      console.log('after remove style len', document.getElementsByTagName('style').length)
      for (let i = 0; i < all.length; i++) {
        let s = document.createElement('style')
        s.innerHTML = all[i]
        console.log('style', i, all[i].length)
        parent.appendChild(s)
      }
      console.log('after insert style len', document.getElementsByTagName('style').length)
    } catch (e) {
      console.log('get e', e)
    }

  }

  function getHTML() {
    return new Promise(function (ok, reject) {

      check_rules()
      console.log('all js done')
      let node = document.documentElement.cloneNode(true)

      if (false) {
        let styles = node.getElementsByTagName('style');
        let buf = []
        let parent;
        for (let i = styles.length - 1; i >= 0; i--) {
          let s = styles[i]
          let old = s.innerHTML
          let newCss = css_beautify(old)
          split_css(newCss, buf, 1024)
          console.log('newCss', newCss.length, 'old', old.length)
          // s.innerHTML = newCss
          parent = s.parentElement
          parent.removeChild(s)
        }
        for (let i = 0; i < buf.length; i++) {
          let s = node.ownerDocument.createElement('style')
          s.innerHTML = buf[i]
          console.log('append css', buf[i].length)
          parent.appendChild(s)
        }
      }

      setTimeout(function () {
        ok('<!doctype html>\n<!-- ' + location.href + ' -->\n' + node.outerHTML);
      }, 6000)

    })

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


  function clean_elements() {
    let div = document.querySelector('.loading-indicator');
    div && div.parentElement.removeChild(div);
    div = document.getElementById('js-plotly-tester')
    div && div.parentElement.removeChild(div);
    let div2 = document.querySelectorAll('*[style*="display: none;"]')
    for (let i = 0; i < div2.length; i++) {
      div2[i].parentElement.removeChild(div2[i]);
    }

    let inject = document.querySelectorAll('div.widget-visualization');
    for (let i = 0; i < inject.length; i++) {
      inject[i].style.flexDirection = 'column';
    }
  }

  clean_elements()

  inlineSameOriginExternalStyles()
    .then(function () {
      getHTML().then(function (text) {
        text = omitScript(text);
        text = omitIframeSrc(text);
        text = normalizeURL(text);

        window.last_html = text
        let filename = location.href + '-' + (new Date()).toISOString() + '.html';
        download(filename, text);

      });

    })

})()
