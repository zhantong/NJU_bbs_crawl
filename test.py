import urllib.request
from lxml import etree
import re

url_split=re.compile(r'board=(.*?)&file=(.*?)&num=(\d+)$')

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
	s=urllib.request.urlopen('http://bbs.nju.edu.cn/bbsdoc?board=M_Logistic&type=doc'+'&start='+start)
	con=s.read().decode('gb2312')
	root=etree.HTML(con)
	trs=root.xpath('//tr')
	for tr in trs[1:]:
		tds=tr.findall('td')
		if tds[0].text==None or not tds[0].text.isdigit():
			continue
		no=tds[0].text
		author=tds[2].find('a').text
		date=tds[4].find('nobr').text
		a_title=tds[4].find('nobr/td/a')
		t=url_split.findall(a_title.get('href'))[0]
		board=t[0]
		file=t[1]
		num=t[2]
		title=a_title.text
		print(title)

def get_post():
	s=urllib.request.urlopen('http://bbs.nju.edu.cn/bbstcon?board=M_Logistic&file=M.1441702873.A')
	con=s.read().decode('gb2312')
	root=etree.HTML(con)
	tables=root.xpath('/html/body/center[1]/table')
	for table in tables:
		a_s=table.findall('./tr/td/a')
		id=a_s[0].get('href').rsplit('=',1)[-1]
		author=a_s[2].text
		con=table.find('.//textarea').text
		print(author)
if __name__=='__main__':
	get_post_list('aaa')
