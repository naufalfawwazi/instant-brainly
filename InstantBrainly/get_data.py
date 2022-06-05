import re, requests, random
from bs4 import BeautifulSoup

def cari_link(keyword):
	url = f'https://www.google.com/search?q={keyword} Brainly&ie=UTF-8'
	A = (
		"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
		)
	Agent = A[random.randrange(len(A))]
	headers = {'user-agent': Agent}

	r = requests.get(url, headers=headers)
	soup = BeautifulSoup(r.content, 'html.parser')
	link = 'https://brainly.co.id/tugas/'
	soup = f'{soup}'

	results = [m.start() for m in re.finditer(link, soup)]
	res = []
	for indeks in results:
		stopkey = soup[indeks:].index('&') + indeks
		res.append(soup[indeks+len(link) : stopkey])
	return res

def ambil_jawaban(url):
	A = (
		"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
		)
	Agent = A[random.randrange(len(A))]
	headers = {'user-agent': Agent}
	source = requests.get(url, headers=headers)
	soup = BeautifulSoup(source.text,"html.parser")

	soal = soup.find('h1',attrs={'data-test':'question-box-text'}).text.strip()
	cari = soup.find_all('div', attrs={'data-test':'answer-box-text'})
	for i in range(len(cari)):
		cari[i] = f'{cari[i]}'.replace('<p>','\n').replace('<br/>','\n')
	listdelete = []
	for i in range(len(cari)):
		if '<' and '>' in cari[i]:
			indeks_1 = 0
			indeks_2 = 0
			for j in range(len(cari[i])):
				if cari[i][j] == '<':
					indeks_1 = j
				elif cari[i][j] == '>':
					indeks_2 = j
					listdelete.append(cari[i][indeks_1:indeks_2+1])
		else:
			break
	cari =  '~~~'.join(cari)
	cari = f'{cari}'
	for i in range(len(listdelete)):
		cari = cari.replace(listdelete[i],'')
	jawaban = '\n\n<b><i>-- JAWABAN LAIN --</i></b>\n\n'.join([item.strip() for item in cari.split('~~~')])
	return [soal, jawaban]

def convert_vn(path):
	import speech_recognition as sr 
	import os 
	from pydub import AudioSegment
	from pydub.silence import split_on_silence

	tpath = 'D:\\Programming\\Python\\Projects\\dataset\\' + path
	res  = 'D:\\Programming\\Python\\Projects\\dataset\\' + path[:-4] + '.wav'
	AudioSegment.from_file(tpath).export(res, format='wav')
	os.remove(tpath)
	path = res

	r = sr.Recognizer()
	sound = AudioSegment.from_wav(path)
	chunks = split_on_silence(sound,
		min_silence_len = 500,
		silence_thresh = sound.dBFS-14,
		keep_silence=500,
	)

	folder_name = "audio-chunks"
	if not os.path.isdir(folder_name):
		os.mkdir(folder_name)

	whole_text = ""
	for i, audio_chunk in enumerate(chunks, start=1):
		chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
		audio_chunk.export(chunk_filename, format="wav")
		with sr.AudioFile(chunk_filename) as source:
			audio_listened = r.record(source)
			try:
				text = r.recognize_google(audio_listened, language="id")
			except sr.UnknownValueError as e:
				pass
			else:
				text = f"{text.capitalize()}. "
				whole_text += text
	os.remove(path)
	return whole_text