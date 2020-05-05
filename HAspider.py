import ssl, sqlite3, time
from bs4 import BeautifulSoup
from urllib import request


#Creating new db 
conn = sqlite3.connect('datadb.sqlite')
cur = conn.cursor()

#Maak de taable leeg voor het oefenen!
#cur.execute('DROP TABLE IF EXISTS Locations')

#Make a table and columns
cur.execute(''' CREATE TABLE IF NOT EXISTS Locations
	( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	Praktijk TEXT,
	Adres TEXT,
	Postcode TEXT,
	Plaats TEXT,
	Tel INTEGER,
	Web TEXT ) ''')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#Source files
home = ('https://www.zorgkaartnederland.nl')
url = 'https://www.zorgkaartnederland.nl/huisartsenpraktijk/amsterdam/pagina'

#How much did we catch
count = 0
catch = 0

#Numbers of the pages in the URL of the web browser
for page in range(1, 13):

	#HTML request
	source = request.urlopen(url + str(page), context=ctx).read()
	soup = BeautifulSoup(source, 'html.parser')

	for praktijken in soup.find_all(class_='media'):
		count += 1

		try:
			praktijk_naam = praktijken.h4.a.string
		except:
			pass
		
		
		#Find if there is a match in the database
		cur.execute("SELECT Praktijk FROM Locations WHERE Praktijk= ?",
	        ( praktijk_naam, ) )
		try:
			data = cur.fetchone()[0]
			#print('=================')
			continue
		except:
			pass
		

		try:
			url_p = praktijken.h4.a.get('href')
		except Exception as e:
			url_p = None

		source_praktijk = request.urlopen(home + url_p, context=ctx).read()
		soup_p = BeautifulSoup(source_praktijk, 'html.parser')

		#Find practice data
		praktijk = soup_p.find(class_='col-xs-12 col-sm-6 col-md-7')

		try:
			adress = praktijk.find('span', class_='address_content').text.strip()
		except Exception as e:
			adress = None
				
		try:
			postcode = praktijk.find_all('span')[2].text.strip()
		except Exception as e:
			postcode = None

		try:
			woonplaats = praktijk.find_all('span')[3].text.strip()
		except Exception as e:
			woonplaats = None

		try:
			telefoon = praktijk.find('span', itemprop='telephone').text.strip()
		except Exception as e:
			telefoon = None

		try:
			website = praktijk.a.get('href')
		except Exception as e:
			website = None


		#collected item
		print('Praktijk naam:', praktijk_naam)
		print('Adres:', adress)
		print('Poscode:', postcode)
		print('Plaats:', woonplaats)
		print('Tel:', telefoon)
		print('Web:', website)
		print('-----------')
		catch += 1


		#Add to the database
		cur.execute( '''INSERT INTO Locations
			( Praktijk, Adres, Postcode, Plaats, Tel, Web )
			VALUES ( ?, ?, ?, ?, ?, ? )''',
			( praktijk_naam, adress, postcode, woonplaats, telefoon, website ) )
		
		conn.commit()
		
		
		#Rest time for the server
		if count % 10 == 0 :
			print('Iedere 10 hebben we even pauze')
			time.sleep(5)


cur.close()
print( 'De totale catch is', catch )










