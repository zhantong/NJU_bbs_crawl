import urllib.request
from lxml import etree
headers={
	'Host': 'bbs.nju.edu.cn',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
	'Accept-Encoding': 'deflate, sdch',
}

def get_board_list():
	s=urllib.request.urlopen('http://bbs.nju.edu.cn/bbsall')
	con=s.read().decode('gb2312')
	root=etree.HTML(con)
	trs=root.xpath('//tr')
	for tr in trs[1:]:
		tds=tr.findall('td')
		no=tds[0].text
		board=tds[1].find('a').text
		category=tds[2].text[1:-1]
		name=tds[3].find('a').text[3:]
		print(name)

def get_post_list(board_id,start=''):
	s=urllib.request.urlopen('http://bbs.nju.edu.cn/bbstdoc?board=M_Logistic'+'&start='+start)
	con=s.read().decode('gb2312')
	root=etree.HTML(con)
	trs=root.xpath('//tr')
	for tr in trs[1:]:
		tds=tr.findall('td')
		if not tds[0].text:
			continue
		no=tds[0].text
		author=tds[2].find('a').text
		date=tds[3].text
		a_title=tds[4].find('a')
		id=a_title.get('href').rsplit('=',1)[-1]
		title=a_title.text[2:]
		print(id)

if __name__=='__main__':
	get_post_list('aaa')
