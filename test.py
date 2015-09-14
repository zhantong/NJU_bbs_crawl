import urllib.request
from lxml import etree
import re
import mysql.connector

url_split=re.compile(r'board=(.*?)&file=(.*?)&num=(\d+)$')
content_split=re.compile(r'2015\)\s+(.*?)\s+\[.*?来源.*?\[FROM: (.*?)\]',re.S)
modify=re.compile(r'修改:．(.*?) 於 (.*?) 修改本文．\[FROM: (.*?)\]')
download=re.compile(r'http://bbs\.nju\.edu\.cn/file/(.*?)/(.*?)\s')


headers={
	'Host': 'bbs.nju.edu.cn',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
	'Accept-Encoding': 'deflate, sdch',
}

db={
	'user':'root',
	'password':'123456',
	'database':'njubbs'
}

class NJU_BBS():
	def __init__(self):
		self.cnx=mysql.connector.connect(**db)
		self.cursor=self.cnx.cursor()
	def get_html(self,url):
		get=urllib.request.urlopen(url)
		content=get.read().decode('gb2312')
		root=etree.HTML(content)
		return root
	def get_board_list(self):
		board_list=[]
		url='http://bbs.nju.edu.cn/bbsall'
		root=self.get_html(url)
		trs=root.xpath('//tr')
		for tr in trs[1:]:
			tds=tr.findall('td')
			board={
				'no':tds[0].text,
				'board':tds[1].find('a').text,
				'category':tds[2].text[1:-1],
				'name':tds[3].find('a').text[3:]
			}
			board_list.append(board)
		return(board_list)

	def save_board_list_to_db(self):
		drop="""
		DROP TABLE IF EXISTS board
		"""
		create="""
		CREATE TABLE `board` (
			`no` int(3) NOT NULL PRIMARY KEY,
			`board` varchar(20) NOT NULL,
			`category` varchar(10) NOT NULL,
			`name` varchar(20) NOT NULL
			)
		"""
		insert="""
		INSERT INTO board 
		(no,board,category,name)
		VALUES
		('%(no)s','%(board)s','%(category)s','%(name)s')
		"""
		self.cursor.execute(drop)
		self.cursor.execute(create)
		lis=self.get_board_list()
		for board in lis:
			self.cursor.execute(insert%board)
		self.cnx.commit()

	def get_post_list(self,board,start=''):
		url='http://bbs.nju.edu.cn/bbsdoc?&type=doc'+'&board='+board+'&start='+start
		root=self.get_html(url)
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


	def get_post(self,board,file,num=''):
		url='http://bbs.nju.edu.cn/bbscon?board='+board+'&file='+file+'&num='+num
		root=self.get_html(url)
		content=root.find('.//textarea').text
		con=content_split.findall(content)[0]
		ip=modify.findall(content)
		gid=root.find('.//center/a[4]').get('href').rsplit('=',1)[-1]
		dl_list=download.findall(content)
		print(dl_list)


if __name__=='__main__':
	bbs=NJU_BBS()
	print(bbs.save_board_list_to_db())
