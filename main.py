import csv, os, smtplib, copy, random, time
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()
EMAIL_ADDR = os.getenv("EMAIL_ADDR")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def get_data(path : str):
	data = []
	with open(path, mode ='r') as file:
		csvFile = csv.reader(file)
		for line in csvFile:
			data.append(line)
	return {line[1] : line for line in data[1::]}

def send_email(to_email, subject, body, attachment_path=None):
	try:
		# Create email
		msg = MIMEMultipart()
		msg['From'] = EMAIL_ADDR
		msg['To'] = to_email
		msg['Subject'] = subject
		# Add email body
		msg.attach(MIMEText(body, 'plain'))
		# Add attachment if provided
		if attachment_path:
			with open(attachment_path, 'rb') as attachment:
				part = MIMEBase('application', 'octet-stream')
				part.set_payload(attachment.read())
				encoders.encode_base64(part)
				part.add_header(
					'Content-Disposition',
					f'attachment; filename={attachment_path.split("/")[-1]}')
				msg.attach(part)
		# Connect to SMTP server and send email
		with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
			server.login(EMAIL_ADDR, EMAIL_PASS)
			server.send_message(msg)
		print(f"Email sent successfully! {to_email}")
	except Exception as e:
		print(f"Failed to send email: {e}")
		print(f"for {to_email}")

def create_body(santa : str, elf : str, data : dict):
	elf_data = data[elf]
	elf_name = elf_data[2]
	elf_ideas = elf_data[3]
	elf_image = elf_data[4]
	santa_data = data[santa]
	santa_name = santa_data[2]
	placeholder = '' if elf_image != '' else '\n\nThey did not choose to supply an image so i gave you a placeholder.'
	body = f"""Hello {santa_name},

You are the Santa for {elf_name},
Their present ideas where:
{elf_ideas}{placeholder}

From your cryptic Christmas companion,
- H
	"""
	return body

def get_attatchment(santa : str, elf : str, data : dict):
	elf_data = data[elf]
	elf_image = elf_data[4]
	if (elf_image == ''):
		elf_image = "data/static/placeholder.png"
	return elf_image

# elf is to recieve the present!
def main():
	create_subject = lambda: "Secret Santa 2024"
	data = get_data("data/data.csv")
	keys = data.keys()
	santas_array = copy.copy(list(keys))
	random.shuffle(santas_array)
	elves_array = copy.copy(santas_array)
	shuffle = random.randint(1,len(elves_array)-1)
	while (shuffle == len(elves_array) or shuffle == 0):
		shuffle = random.randint(1,len(elves_array)-1)
	elves_array = elves_array[shuffle:] + elves_array[:shuffle]
	for i in range(len(elves_array)):
		if elves_array[i] == santas_array[i]:
			i = 0
			elves_array = elves_array[shuffle:] + elves_array[:shuffle]
	for i in range(len(elves_array)):
		santa = santas_array[i]
		elf = elves_array[i]
		send_email(santa, create_subject(), create_body(santa, elf, data), get_attatchment(santa, elf, data))
		time.sleep((20))


if __name__ == "__main__":
	main()