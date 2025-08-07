import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test sendmail from gs3 test#5")
msg['Subject'] = f'Test Process & Push message'
msg['From'] = 'janine@ucar.edu'
msg['To'] = 'janine@ucar.edu'

s = smtplib.SMTP('localhost')
s.sendmail('janine@ucar.edu', 'janine@ucar.edu', msg.as_string())
s.quit()
