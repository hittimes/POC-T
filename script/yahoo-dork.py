# -*- coding: utf-8 -*-
# @Author: zeroyu
# @Date:   2018-12-22 16:53:36
# @Last Modified by:   zeroyu
# @Last Modified time: 2018-12-22 16:57:35


import pychrome
import urllib.parse
import threading
from lib.core.data import paths,th,logger
from lib.controller.engine import output2file

# 环境配置:
# 	本地配置chrome的headless，执行如下命令:
# 	headless mode (chrome version >= 59):
# 	$ google-chrome --headless --disable-gpu --remote-debugging-port=9222

# 	或者直接使用docker
# 	$ docker pull fate0/headless-chrome
# 	$ docker run -it --rm --cap-add=SYS_ADMIN -p9222:9222 fate0/headless-chrome

# 	PS:使用google-dork的时候打开ss就好

# 使用说明:
# 	对目标使用google dork语法，程序会返回抓取的域名
# 	python POC-T.py -iS "site:test.com" -s test.py -eG
# 	默认对域名做了去重输出，根据需要可以修改script

def subdomin_finder_by_yahoo(target):

	# create a browser instance
	browser = pychrome.Browser(url="http://127.0.0.1:9222")

	# create a tab
	tab = browser.new_tab()

	# start the tab
	tab.start()

	tab.Page.enable()

	# call method
	tab.Network.enable()
	tab.Runtime.enable()

	step=1

	subdomins=[]

	while(1):

		url="https://search.yahoo.com/search?p={}".format(target)
		url=url+"&b={}&pz=40".format(step)
		# stepinfo="step:"+str(step)
		# logger.info(stepinfo)
		step=step+40


		try:
			# call method with timeout
			tab.Page.navigate(url=url, _timeout=5)
			tab.wait(5)

			exp='document.getElementsByClassName(" ac-algo fz-l ac-21th lh-24").length'
			length= tab.Runtime.evaluate(expression=exp)		

			# 360so就看报不报错，报错了的话document.getElementsByClassName("res-title").length是为0的
			if length['result']['value']==0:
				break

			#从每一页上抓取url
			for l in range(0,length['result']['value']):
				# tab.wait(1)
				exp1='document.getElementsByClassName(" ac-algo fz-l ac-21th lh-24")[{}].href'.format(l)
				res1= tab.Runtime.evaluate(expression=exp1)
				logger.info(res1['result']['value'])
				subdomins.append(res1['result']['value'])
		except:
			pass

	tab.stop()
	browser.close_tab(tab)
	return subdomins

def poc(target):
	subdomins=subdomin_finder_by_yahoo(target)
	tmp=[]
	for sub in subdomins:
		url=urllib.parse.urlparse(sub)
		tmp.append(url.scheme+"://"+url.netloc)
	# 去重
	subdomins=list(set(tmp))
	if subdomins:
		for s in subdomins:
			s="=>"+s
			output2file(s.replace("=>",""))
			logger.success(s)
		return True
	return False