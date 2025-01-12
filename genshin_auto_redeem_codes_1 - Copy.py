"""
I mostly made this with a mix of readability and performance in mind, so thats why theres comments.


LICENSE
==================================================================
# Sleepy's Open Source License v1.1 (OSLv1)

**1. Permission to Use, Modify, and Redistribute**  
Permission is hereby granted to use, modify, and redistribute the code ("Software"), provided that any modified versions of the Software are distributed under the same terms as this license.

**2. Attribution and Notification**  
Any individual or organization using, modifying, or redistributing the Software, in whole or in part, must provide clear notification that the Software is being used and must include a link to a relevant webpage or repository associated with the Software, if such a webpage or repository exists. If no such webpage or repository exists, this requirement is waived.

**3. Profit Sharing**  
Any individual or organization that generates revenue or profit from the use, modification, or redistribution of the Software, in whole or in part, is required to share 30% of the profits with the owner of the Software. Payments must be made on a quarterly basis, accompanied by a financial report detailing the revenue and profit generated from the Software.

**4. Revocation of Rights**  
The owner of the Software reserves the right to revoke any individual's or organization's permission to use, modify, or redistribute the Software at any time, for any reason or no reason at all. Upon revocation, the individual or organization must cease all use, modification, and redistribution of the Software.

**5. Disclaimer of Warranties and Liability**  
The Software is provided "as-is," without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the owner of the Software be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the Software or the use or other dealings in the Software.
==================================================================
"""
import requests
import asyncio
import re


active_codes = []

def update_active_codes():
    global active_codes # it doesnt work without this dont ask me why i have no clue all i know is that if u remove it then the entire world will die (jk) but it will break
    response = requests.get("https://genshin-impact.fandom.com/wiki/Promotional_Code")
    active_codes = re.findall(r"<code>(.*?)</code>", response.text)
    print(f"Updated active codes and got {active_codes}") # here for debugging



uid_prefixes = {
    6: "os_usa",
    7: "os_euro",
    8: "os_asia",
    18: "os_asia",
    9: "os_cht"
} # i got the uid prefix data from [here](https://genshin-impact.fandom.com/wiki/UID#Format) and i got the strings to send in the request from digging through the network logs while changing servers [here](https://genshin.hoyoverse.com/en/gift)

class UnsupportedUIDError(Exception):
    def __init__(self, uid: str):
        self.message = f"The UID {uid} is not supported."
        super().__init__(self.message)

def parse_genshin_uid_for_region(uid: str) -> str:
    prefix = int(uid[0])
    if prefix in uid_prefixes:
        return uid_prefixes[prefix]
    if uid.startswith("18"): # bcuz single number parsing wont work like i would want to do it
        return "os_asia"
    raise UnsupportedUIDError(uid)





def redeem_code(uid: str, region: str, code: str) -> dict:
    redeem_headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Opera GX\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "Referer": "https://genshin.hoyoverse.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    request_url = f"https://public-operation-hk4e.hoyoverse.com/common/apicdkey/api/webExchangeCdkey?uid={uid}&region={region}&lang=en&cdkey={code}&game_biz=hk4e_global&sLangKey=en-us"
    response = requests.get(url = request_url, headers = redeem_headers)
    print(response.text)
    input(response.status_code)
    return response.json()


def redeem_all_codes_for_user(uid: str) -> dict:
    region = parse_genshin_uid_for_region(uid)
    responses = {}
    for code in active_codes:
        response = redeem_code(uid, region, code)
        responses[code] = response
    return responses
