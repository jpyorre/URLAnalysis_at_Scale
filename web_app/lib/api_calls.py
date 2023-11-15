from investigate import Investigate
import requests
import base64

with open('lib/investigatetoken.txt') as investigate_api_key:
    token = investigate_api_key.read()
    api_key = token.rstrip()
    inv = Investigate(api_key)

with open('lib/virustotaltoken.txt') as virustotal_api_key:
    token = virustotal_api_key.read()
    virustotal_api_key = token.rstrip()

class apicalls:
    def __init__(self):
        pass

    def inv_pdns(self,domain):
        passive_dns = inv.pdns_name(domain)
        return(passive_dns)
    
    def negative_urls_from_investigate(self, urls):
        returnlist = []
        for w in urls:
            domain = w['domain']
            try:
                inv_results = inv.categorization(domain)
                for domain, data in inv_results.items():
                    status = data['status']
                    if status == -1:
                        w['score'] -= 1
                        if 'reason' in w:
                            reason = w['reason'] + ', Investigate'
                            w['reason'] = reason
                        else:
                            w['reason'] = 'Investigate'
                    else:
                        pass
            except:
                pass # investigate might not have the results
            returnlist.append(w)
        return(returnlist)
    
    def negative_urls_from_virustotal(self,urls):
        returnlist = []
        headers = {'x-apikey': virustotal_api_key}
        
        for w in urls:
            url = w['url']
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            vt_url = "https://www.virustotal.com/api/v3/urls/{}".format(url_id)
            response = requests.get(vt_url, headers=headers)
            data = response.json()
            try:
                for k, v in data.items():
                    last_analysis_stats = (v['attributes']['last_analysis_stats'])
                    if last_analysis_stats['malicious'] > 2:
                        w['score'] -= 1
                        if 'reason' in w:
                            reason = w['reason'] + ', Virustotal'
                            w['reason'] = reason
                        else:
                            w['reason'] = 'Virustotal'
                    else:
                        pass
                returnlist.append(w)    # send back the negative results
            except:
                returnlist.append(w)    # send back the non-negative results
        return(returnlist)