import asyncio
from pyppeteer import launch
import socket
from usr_data import *

HOST = "127.0.0.1"
PORT = 9090
def send(txt):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send(txt.encode("utf-8"))

async def get_data():
    """
    This function mainly used for getting the data from the browser but if there is any error happens end this
    using print to communicate with the browser thread and using socket to communicate with progressbar thread
    """
    browser = await launch(headless = True)
    try:
        page = await browser.newPage()
        await page.goto("https://my.te.eg/")
        send("20")
        await page.waitForSelector("#login-service-number-et")
        await page.type("#login-service-number-et", user_name)
        send("40")
        await page.click("body > app-root > div > div.top-relative.p-mt-5 > app-login > div > div > div > p-card:nth-child(2) > div > div > div > form > div > div.row > div.col.ng-star-inserted > app-service-number-type > div > p-dropdown > div > div.p-dropdown-trigger.ng-tns-c86-6 > span")
        await page.waitForSelector("body > app-root > div > div.top-relative.p-mt-5 > app-login > div > div > div > p-card:nth-child(2) > div > div > div > form > div > div.row > div.col.ng-star-inserted > app-service-number-type > div > p-dropdown > div > div.ng-trigger.ng-trigger-overlayAnimation.ng-tns-c86-6.p-dropdown-panel.p-component.ng-star-inserted > div > ul > p-dropdownitem:nth-child(1) > li")
        await page.click("body > app-root > div > div.top-relative.p-mt-5 > app-login > div > div > div > p-card:nth-child(2) > div > div > div > form > div > div.row > div.col.ng-star-inserted > app-service-number-type > div > p-dropdown > div > div.ng-trigger.ng-trigger-overlayAnimation.ng-tns-c86-6.p-dropdown-panel.p-component.ng-star-inserted > div > ul > p-dropdownitem:nth-child(1) > li")
        send("60")
        await page.waitForSelector("#login-password-et")
        await page.type("#login-password-et", password)
        
        await page.click("#login-login-btn")
        while True:
            true_number = 6
            for i in range(6, 10):
                try:
                    await page.waitForSelector(f"#pr_id_{i} > div > div > div > div > div > app-gauge > div.usage > span.remaining-details.ng-star-inserted", timeout = 100)
                    true_number = i
                    send("80")
                    break
                except:
                    continue
            try:
                data = await page.evaluate('(element) => element.textContent', await page.querySelector(f"#pr_id_{true_number} > div > div > div > div > div > app-gauge > div.usage > span.remaining-details.ng-star-inserted"))
                break
            except:
                continue
        data = float(data.split()[0])
        print(data)
        send("100")
        await browser.close()       

    except:
        print("None")
        await browser.close()       
        
    


asyncio.run(get_data())
