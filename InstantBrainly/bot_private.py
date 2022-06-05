import telebot, os, pytesseract
from get_data import cari_link, ambil_jawaban, convert_vn

token = '1770762855:AAEm2UxMVf92CBlO1ZPNaRwrcZIVDvEUloE'
bot = telebot.TeleBot(token=token, threaded=False)
urls = {}

@bot.message_handler(commands=["start"])
def welcome(message):
	print(f'[{message.chat.type}] {message.from_user.first_name}{f" {message.from_user.last_name} " if message.from_user.last_name != None else " "}@{message.from_user.username} : {message.text}')
	nama = message.from_user.first_name
	pesan = f"Hai, selamat datang {nama}👋\n\nKetik /help untuk melihat bantuan dan fitur-fitur InstantBrainly Bot"
	bot.send_message(message.chat.id,pesan)

@bot.message_handler(commands=["help"])
def bantuan(message):
	print(f'[{message.chat.type}] {message.from_user.first_name}{f" {message.from_user.last_name} " if message.from_user.last_name != None else " "}@{message.from_user.username} : {message.text}')
	pesan = "<b>• Ketik soal lalu kirim</b>\n<i>Contoh: Kapan terjadinya peristiwa Reformasi 98?</i>\n\n<b>• Ketik kode Brainly lalu kirim</b>\n<i>https://brainly,co,id/tugas/<u>30159932</u>\nContoh: 30159932</i>\n\n<b>• Foto soal dan crop soal lalu kirim</b>\n\n<b>• Rekam suara menggunakan voice note lalu kirim</b>\n\n<b>• Gunakan tombol Sebelumnya dan Selanjutnya</b> untuk melihat <u>contoh soal lain</u> yang terkait dengan pertanyaanmu.\n\nBerikut adalah video tutorial singkat pemakaian fitur-fitur InstantBrainly Bot"
	bot.send_message(message.chat.id,pesan, parse_mode='HTML')
	bot.send_video(message.chat.id, 'BAACAgUAAxkBAAIKUGEopWr9HslruOfQRZ2gCQhQ2HGhAAK1AgACuRpJVXe1SYnHWrciIAQ')

@bot.message_handler(commands=["info"])
def informasi(message):
	print(f'[{message.chat.type}] {message.from_user.first_name}{f" {message.from_user.last_name} " if message.from_user.last_name != None else " "}@{message.from_user.username} : {message.text}')
	pesan = 'Bot sederhana ini dibuat menggunakan Python yang bertujuan untuk menampilkan secara langsung jawaban dari soal yang dicari pada hasil teratas pencarian Brainly.co.id.\n\nKritik/saran bisa ke @naufalfawwazi.\nSemoga bermanfaat ^-^\n#NugasAntiRibet'
	bot.send_message(message.chat.id,pesan)

@bot.message_handler(content_types=['text', 'photo', 'voice'])
def main(message):
	msg = ''	
	if message.content_type == 'text':
		msg = message.text
	elif message.content_type == 'photo':
		file = message.photo[-1]
		file_info = bot.get_file(file.file_id)
		downloaded_file = bot.download_file(file_info.file_path)
		fotouser = f'D:\\Programming\\Python\\Projects\\dataset\\soalfoto-{message.from_user.id}.png'
		with open(fotouser, 'wb') as new_file:
			new_file.write(downloaded_file)
		pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
		res = pytesseract.image_to_string(r'{}'.format(fotouser))[:-1].replace('\n', ' ')
		os.remove(fotouser)
		msg = res
	elif message.content_type == 'voice':
		file_info = bot.get_file(message.voice.file_id)
		downloaded_file = bot.download_file(file_info.file_path)
		vnuser = f'D:\\Programming\\Python\\Projects\\dataset\\soalvn-{message.from_user.id}.ogg'
		with open(vnuser, 'wb') as new_file:
			new_file.write(downloaded_file)
		res = convert_vn(f'soalvn-{message.from_user.id}.ogg')
		msg = res

	print(f'[{message.chat.type}] {message.from_user.first_name}{f" {message.from_user.last_name} " if message.from_user.last_name != None else " "}@{message.from_user.username} : {msg}')

	if len(msg)<10 and msg.isnumeric():	
		kode = msg.replace(' ','')
		soal, jawaban = ambil_jawaban(f'https://brainly.co.id/tugas/{kode}')
		result = f'<b><u>Soal untuk kode {kode}:</u></b>\n\n{soal}\n\n<b><u>Jawaban untuk kode {kode}:</u></b>\n\n{jawaban}'
		bot.reply_to(message, result, parse_mode='HTML')
	else:
		global  urls
		urls[message.from_user.id] = cari_link(msg)
		links = urls[message.from_user.id]
		index = 0

		url  = 'https://brainly.co.id/tugas/' + links[index]
		soal, jawaban = ambil_jawaban(url)

		result = f'<b><u>Soal yang serupa:</u></b>\n\n{soal}\n\n<b><u>Jawaban yang tersedia:</u></b>\n\n{jawaban}\n\n<b><i>Hasil {index+1} dari {len(links)} ditemukan</i></b>'
		markup = telebot.types.InlineKeyboardMarkup()

		btnKembali = telebot.types.InlineKeyboardButton('⬅️ Sebelumnya',callback_data=f'/kembali~{index}~{message.chat.id}')
		btnContohSoalLain = telebot.types.InlineKeyboardButton('⬇️  Tampilkan Hasil Soal Lainnya  ⬇️',callback_data='/')
		btnLanjut = telebot.types.InlineKeyboardButton('Selanjutnya ➡️',callback_data=f'/lanjut~{index}~{message.chat.id}')

		markup.row(btnContohSoalLain)
		markup.row(btnKembali, btnLanjut)
		bot.reply_to(message, result, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda msg: 'kembali' in msg.data or 'lanjut' in msg.data)
def callback_kembali(message):
	global urls
	links = urls[message.from_user.id]
	msgid = int(message.data.split('~')[2])

	index = eval(message.data.split('~')[1])
	if message.data.split('~')[0] == '/kembali':
		if index == 0:
			index  = len(links)-1
		else:
			index -= 1
	elif message.data.split('~')[0] == '/lanjut':
		if index == len(links)-1:
			index  = 0
		else:
			index += 1

	url = 'https://brainly.co.id/tugas/' + links[index]
	soal, jawaban = ambil_jawaban(url)

	result = f'<b><u>Soal yang serupa:</u></b>\n\n{soal}\n\n<b><u>Jawaban yang tersedia:</u></b>\n\n{jawaban}\n\n<b><i>Hasil {index+1} dari {len(links)} ditemukan</i></b>'
	markup = telebot.types.InlineKeyboardMarkup()

	btnKembali = telebot.types.InlineKeyboardButton('⬅️ Sebelumnya',callback_data=f'/kembali~{index}~{msgid}')
	btnContohSoalLain = telebot.types.InlineKeyboardButton('⬇️  Tampilkan Hasil Soal Lainnya  ⬇️',callback_data='/')
	btnLanjut = telebot.types.InlineKeyboardButton('Selanjutnya ➡️',callback_data=f'/lanjut~{index}~{msgid}')

	markup.row(btnContohSoalLain)
	markup.row(btnKembali, btnLanjut)
	bot.send_message(msgid, result, parse_mode='HTML', reply_markup=markup)

print("Running..")
while True:
	try:
		bot.polling()
	except:
		bot.stop_polling()