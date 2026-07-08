from time import time
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import service as fs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import inspect
import socket
import lxml.html

from myModules import myConst


################################################################################################
def waitForPageLoaded(driver, timeout):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

################################################################################################
def scrollBottom(driver: webdriver.Firefox):
    return driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

################################################################################################
def passProxy(driver) -> None:
    try:
        elementInput(driver, myConst.XPATH_INPUT_USERNAME, myConst.PROXY_ID)
        elementClick(driver, myConst.XPATH_INPUT_SUBMIT)
        elementInput(driver, myConst.XPATH_INPUT_PASSWORD, myConst.PROXY_PW)
        elementClick(driver, myConst.XPATH_INPUT_SUBMIT)
        sleep(5)
    except Exception as e:
        print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        pass

################################################################################################
def elementAttributes(driver: webdriver.Firefox, element):
    script  = 'var items = {}; '
    script += 'for (index = 0; index < arguments[0].attributes.length; ++index) { '
    script += '  items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value'
    script += '}; '
    script += 'return items;'
    return driver.execute_script(script, element)
    # driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', element)

################################################################################################
def elementLocatedBy(driver: webdriver.Firefox, by: By, value: str, timeout: float=120):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

################################################################################################
def elementInvisibleXPath(driver, time, xPath):
    return WebDriverWait(driver, time).until(EC.invisibility_of_element((By.XPATH, xPath)))

################################################################################################
def elementXPathFocus(driver: webdriver.Firefox, xpath: str, preventScroll: bool):
  JavaScriptFocusToElement = "arguments[0].focus({'preventScroll': arguments[1]})"
  element = driver.find_element(By.XPATH, xpath)
  driver.execute_script(JavaScriptFocusToElement, element, preventScroll)

################################################################################################
def windowOpened(driver, windowHandles, timeout=60):
    WebDriverWait(driver, timeout).until(EC.new_window_is_opened(windowHandles))

################################################################################################
def elementClick(driver, xPath, timeout=60):
    elementLocatedBy(driver, By.XPATH, xPath, timeout).click()

################################################################################################
def elementInput(driver, xPath, value, timeout=60):
    elementLocatedBy(driver, By.XPATH, xPath, timeout).send_keys(value)

################################################################################################
def getXmlTextContent(html):
    return lxml.html.document_fromstring(html).text_content()

################################################################################################
def getFirefoxDriver(headless=1, disableImage=True, log=False) -> webdriver:
    options = FirefoxOptions()
    # options.set_preference("permissions.default.stylesheet", 2)
    # options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", 'false')
    options.set_preference("intl.accept_languages", "zh-CN,zh")
    options.set_preference("extensions.translations.disabled", True)
    options.set_preference("general.useragent.override", myConst.header["User-Agent"])
    
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("media.volume_scale", "0.0")
    options.set_preference("browser.tabs.warnOnClose", False)
    options.set_preference("browser.tabs.warnOnOpe", False)
    options.set_preference("tookkit.startip.max_resumed_crashes", -1)

    if headless == 1:
        options.headless = True
        options.add_argument('--headless')
    if disableImage:
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.set_preference("permissions.default.image", 2)
    if log is False:
        service = fs.Service(log_path=os.path.devnull)
        driver = webdriver.Firefox(options=options, service=service)
    else:
        # options.log.level = "trace"
        driver = webdriver.Firefox(options=options)
    return driver

################################################################################################
def setTimeout(driver, t):
    driver.set_page_load_timeout(t)

################################################################################################
def getLocalIp() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

################################################################################################
def isVPN(show=False) -> bool:
#    ip = socket.gethostbyname(socket.gethostname())
    ip = getLocalIp()

    if '192.168.' in ip or '100.' in ip or '172.16' in ip:
        if show:
            print(f"VPN Off (ip: {ip})\n")
        return False
    else:
        if show:
            print(f"VPN On (ip: {ip})\n")
        return True

################################################################################################
def checkVPN(driver) -> None:
    global isFirstTime

    if isFirstTime:
        isFirstTime = False
        if isVPN(False):
            passProxy(driver)

################################################################################################
def waitForVisible(driver, xPath, timeout=20):
    start_time = time()
    while True:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script('return document.body != null'))        
        scrollBottom(driver)
        sleep(0.5)
        noMore = elementLocatedBy(driver, By.XPATH, xPath)
        if noMore.is_displayed():
            break
        if time() - start_time > timeout:
            print("Timeout reached while waiting for the page to fully load.")
            break

################################################################################################
def getScrollHeight(driver):
    return driver.execute_script("return document.body.scrollHeight")

################################################################################################
def waitForFullPageLoad(driver: webdriver.Firefox, timeout=60):
    """Scrolls until all dynamic content is loaded and the page is stable."""
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script('return document.body != null'))
    # last_height = getScrollHeight(driver)
    last_height = driver.execute_script("return document.body.scrollHeight")
    # lastPageSource = driver.page_source
    scroll_pause_time = 1.0
    start_time = time()

    while True:
        scrollBottom(driver)
        sleep(scroll_pause_time)
        # pageSource = driver.page_source
        new_height = getScrollHeight(driver)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height != last_height:
        # if pageSource != lastPageSource:
            sleep(scroll_pause_time)
            # new_height = getScrollHeight(driver)
            new_height = driver.execute_script("return document.body.scrollHeight")
            # pageSource = driver.page_source
            # lastPageSource = pageSource
            last_height = new_height
        # if pageSource == lastPageSource:
        # if new_height == last_height:
        else:
            break
        if time() - start_time > timeout:
            print("Timeout reached while waiting for the page to fully load.")
            break
