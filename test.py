import urllib.request
from lxml import etree
headers={
	'Host': 'bbs.nju.edu.cn',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
	'Accept-Encoding': 'deflate, sdch',
}

s=urllib.request.urlopen('http://bbs.nju.edu.cn/bbsall')
con=s.read().decode('gb2312')
root=etree.HTML(con)
#trs=root.xpath('//tr/td[1]|//tr/td[2]/a|//tr/td[3]|//tr/td[4]/a')
trs=root.xpath('//tr')
for tr in trs[1:]:
	tds=tr.findall('td')
	no=tds[0].text
	board=tds[1].find('a').text
	category=tds[2].text[1:-1]
	name=tds[3].find('a').text[3:]
	print(name)
