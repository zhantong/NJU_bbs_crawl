import urllib.request
from lxml import etree
import re
import mysql.connector
import time

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
		self.boards={}
	def get_html(self,url):
		get=urllib.request.urlopen(url)
		try:
			content=get.read().decode('gb2312','ignore')
		except Exception as e:
			print(e)
			print(url)
			print(get.getcode())
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
		post_list=[]
		url='http://bbs.nju.edu.cn/bbsdoc?&type=doc'+'&board='+board+'&start='+start
		root=self.get_html(url)
		trs=root.xpath('//tr')
		for tr in trs[1:]:
			tds=tr.findall('td')
			if tds[0].text==None or not tds[0].text.isdigit():
				continue
			a_title=tds[4].find('nobr/td/a')
			t=url_split.findall(a_title.get('href'))[0]
			post={
				'no':tds[0].text,
				'author':tds[2].find('a').text,
				'date':tds[4].find('nobr').text,
				'board':t[0],
				'file':t[1],
				'num':t[2],
				'title':re.escape(a_title.text)
			}
			post_list.append(post)
		return post_list

	def query_board_list_from_db(self):
		query="""
		SELECT
		no,board
		FROM
		board
		"""
		self.cursor.execute(query)
		for (no,board) in self.cursor:
			self.boards[board]=no

	def get_all_posts(self):
		self.post_list_db()
		self.query_board_list_from_db()
		for board in self.boards:
			post_list=self.get_post_list(board)
			print(post_list)
			start=int(post_list[0]['no'])
			while start>=0:
				start-=20
				post_list=self.get_post_list(board,str(start))
				print(post_list[0]['no'],post_list[-1]['no'])
				self.save_post_list_to_db(post_list)
				time.sleep(0.6)

	def post_list_db(self):
		drop="""
		DROP TABLE IF EXISTS post_list
		"""
		create="""
		CREATE TABLE `post_list` (
			`no` int(6) NOT NULL,
			`author` varchar(20) NOT NULL,
			`date` varchar(20) NOT NULL,
			`board` varchar(20) NOT NULL,
			`file` varchar(20) NOT NULL PRIMARY KEY,
			`num` int(6) NOT NULL,
			`title` varchar(60) NOT NULL
			)
		"""
		self.cursor.execute(drop)
		self.cursor.execute(create)
	def save_post_list_to_db(self,post_list):
		insert="""
		INSERT INTO post_list
		(no,author,date,board,file,num,title)
		VALUES
		('%(no)s','%(author)s','%(date)s','%(board)s','%(file)s','%(num)s','%(title)s')
		"""
		for post in post_list:
			self.cursor.execute(insert%post)
		self.cnx.commit()

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
	bbs.get_all_posts()
