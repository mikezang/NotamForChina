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

from myModules import constants

################################################################################################
def scrollBottom(driver: webdriver.Firefox):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

################################################################################################
def passProxy(driver) -> None:
    try:
        elementInput(driver, 20, constants.XPATH_INPUT_USERNAME, constants.PROXY_ID)
        elementClick(driver, 5, constants.XPATH_INPUT_SUBMIT)
        elementInput(driver, 20, constants.XPATH_INPUT_PASSWORD, constants.PROXY_PW)
        elementClick(driver, 5, constants.XPATH_INPUT_SUBMIT)
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
def elementId(driver: webdriver.Firefox, time: float, id: str):
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.ID, id)))

################################################################################################
def elementClass(driver: webdriver.Firefox, time: float, className: str):
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, className)))

################################################################################################
def elementXPath(driver, time, xPath):
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.XPATH, xPath)))

################################################################################################
def elementInvisibleXPath(driver, time, xPath):
    return WebDriverWait(driver, time).until(EC.invisibility_of_element((By.XPATH, xPath)))

################################################################################################
def elementXPathFocus(driver: webdriver.Firefox, xpath: str, preventScroll: bool):
  JavaScriptFocusToElement = "arguments[0].focus({'preventScroll': arguments[1]})"
  element = driver.find_element(By.XPATH, xpath)
  driver.execute_script(JavaScriptFocusToElement, element, preventScroll)

################################################################################################
def elementClick(driver, time, xPath):
    elementXPath(driver, time, xPath).click()

################################################################################################
def elementInput(driver, time, xPath, value):
    elementXPath(driver, time, xPath).send_keys(value)

################################################################################################
def getXmlTextContent(html):
    return lxml.html.document_fromstring(html).text_content()

################################################################################################
def findElementsByClass(driver: webdriver.Firefox, className: str):
    return driver.find_elements(By.CLASS_NAME, className)

################################################################################################
def findElementByCssSelector(driver: webdriver.Firefox, cssSelector: str):
    return driver.find_element(By.CSS_SELECTOR, cssSelector)

################################################################################################
def findElementByClass(driver: webdriver.Firefox, className: str):
    return driver.find_element(By.CLASS_NAME, className)

################################################################################################
def findElementsByXPath(driver: webdriver.Firefox, xPath: str):
    return driver.find_elements(By.XPATH, xPath)

################################################################################################
def findElementsByLinkText(driver: webdriver.Firefox, linkText: str):
    return driver.find_elements(By.LINK_TEXT, linkText)

################################################################################################
def findElementsByTag(driver, tagName):
    return driver.find_elements(By.TAG_NAME, tagName)

################################################################################################
def findElementByTag(driver, tagName):
    return driver.find_element(By.TAG_NAME, tagName)

################################################################################################
def findElementByTag(driver, tagName):
    return driver.find_element(By.TAG_NAME, tagName)

################################################################################################
def getFirefoxDriver(headless=1, disableImage=True, log=False) -> webdriver:
    options = FirefoxOptions()
    # options.set_preference("permissions.default.stylesheet", 2)
    # options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", 'false')
    options.set_preference('general.useragent.override', constants.header['User-Agent'])
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


