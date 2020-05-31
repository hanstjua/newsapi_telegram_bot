import telepot
import urllib3


# platform value is to be stored in bot_config.py as variable named "PLATFORM"
def setup_bot(platform: str):
	if platform == 'PYTHONANYWHERE':
		# You can leave this bit out if you're using a paid PythonAnywhere account
		proxy_url = "http://proxy.server:3128"
		telepot.api._pools = {
    		'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
		}
		telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))
		# end of the stuff that's only needed for free accounts
