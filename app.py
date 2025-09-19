
from flask import Flask, request, render_template_string, send_from_directory
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)
folder_name = "dukesu15a_flask_website"

def render_page(content):
    template = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cumberland Dukes U15A</title>
    <link rel="stylesheet" href="/style.css">
    </head>
    <body>
    <header>
    <img src="/images/dukes-logo.png" alt="Cumberland Dukes Logo">
    <h1>Cumberland Dukes U15A</h1>
    </header>
    <nav>
    <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/sponsors">Sponsors</a></li>
    <li><a href="/sponsorship">Sponsorship</a></li>
    <li><a href="/schedule">Schedule</a></li>
    <li><a href="/contact">Contact Us</a></li>
    </ul>
    </nav>
    <main>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Contact | Cumberland Dukes U15A</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
<img src="images/dukes-logo.png" alt="Cumberland Dukes Logo">
<h1>Cumberland Dukes U15A</h1>
</header>
<nav>
<ul>
<li><a href="index.html">Home</a></li>
<li><a href="sponsors.html">Sponsors</a></li>
<li><a href="sponsorship.html">Sponsorship</a></li>
<li><a href="schedule.html">Schedule</a></li>
<li><a href="contact.html">Contact Us</a></li>
</ul>
</nav>
<main>
<section>
<h2>Contact Us</h2>
<form action="mailto:lucmilloy@gmail.com" method="post" enctype="text/plain">
<label for="name">Name:</label><br>
<input type="text" id="name" name="name" required><br><br>
<label for="email">Email:</label><br>
<input type="email" id="email" name="email" required><br><br>
<label for="message">Message:</label><br>
<textarea id="message" name="message" rows="5" required></textarea><br><br>
<input type="submit" value="Send Message">
</form>
</section>
</main>
<footer>&copy; 2025 Cumberland Dukes U15A</footer>
</body>
</html>
</main>
    <footer>&copy; 2025 Cumberland Dukes U15A</footer>
    </body>
    </html>
    '''
    return template

@app.route('/style.css')
def style(): return send_from_directory(folder_name, 'style.css')
@app.route('/images/<path:path>')
def images(path): return send_from_directory(os.path.join(folder_name,'images'), path)

@app.route('/')
def index(): return render_template_string(render_page("""
<h2>Welcome!</h2>
<p>Welcome to the official website of the Cumberland Dukes U15A hockey team! Follow our season, support our sponsors, and get in touch with us for sponsorship opportunities.</p>
<h2>About the Team</h2>
<p>The Cumberland Dukes U15A team is dedicated to fostering young talent, promoting sportsmanship, and competing at the highest level in our league.</p>
"""))
@app.route('/sponsors')
def sponsors(): return render_template_string(render_page("""
<h2>Our Sponsors</h2>
<p>We would like to thank our generous sponsors for supporting the Cumberland Dukes U15A team:</p>
<div class="sponsor-logos">
<a href="https://applehvac.ca/" target="_blank"><img src="/images/apple.png" alt="Apple"></a>
<a href="https://toprankinmortgages.com/" target="_blank"><img src="/images/toprankin.png" alt="TopRankin"></a>
<img src="/images/your_logo.png" alt="Your Logo">
</div>
"""))
@app.route('/sponsorship')
def sponsorship(): return render_template_string(render_page("""
<h2>Sponsorship Request</h2>
<p>Fill out the form below to request sponsorship information:</p>
<form action="/submit_sponsorship" method="post">
<label for="name">Name:</label><br>
<input type="text" id="name" name="name" required><br>
<label for="email">Your email address:</label><br>
<input type="email" id="email" name="email" required><br>
<label for="message">Message:</label><br>
<textarea id="message" name="message" rows="5" required></textarea><br>
<input type="submit" value="Send Request">
</form>
<h3>Our Sponsors</h3>
<div class="sponsor-logos">
<a href="https://applehvac.ca/" target="_blank"><img src="/images/apple.png" alt="Apple"></a>
<a href="https://toprankinmortgages.com/" target="_blank"><img src="/images/toprankin.png" alt="TopRankin"></a>
<img src="/images/your_logo.png" alt="Your Logo">
</div>
"""))
@app.route('/schedule')
def schedule(): return render_template_string(render_page("""
<h2>Game Schedule</h2>
<table>
<tr><th>Date</th><th>Opponent</th><th>Home/Away</th><th>Time</th><th>Location</th></tr>
<tr><td>Sept 25, 2025</td><td>Team A</td><td>Home</td><td>6:00 PM</td><td>Home Arena</td></tr>
<tr><td>Oct 2, 2025</td><td>Team B</td><td>Away</td><td>7:00 PM</td><td>Away Arena</td></tr>
</table>
"""))
@app.route('/contact')
def contact(): return render_template_string(render_page("""
<h2>Contact Us</h2>
<form action="/submit_contact" method="post">
<label for="name">Name:</label><br>
<input type="text" id="name" name="name" required><br>
<label for="email">Your email address:</label><br>
<input type="email" id="email" name="email" required><br>
<label for="message">Message:</label><br>
<textarea id="message" name="message" rows="5" required></textarea><br>
<input type="submit" value="Send Message">
</form>
"""))

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'youremail@example.com'   # replace with your SMTP email
    msg['To'] = 'lucmilloy@gmail.com'
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('youremail@example.com', 'yourpassword')  # replace with SMTP password
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    success = send_email("Dukes U15A Contact Request", f"Name: {{name}}\nEmail: {{email}}\nMessage: {{message}}")
    return render_template_string(render_page(f"<h2>{{'Message sent!' if success else 'Error sending message'}}</h2>"))

@app.route('/submit_sponsorship', methods=['POST'])
def submit_sponsorship():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    success = send_email("Dukes U15A Sponsorship Request", f"Name: {{name}}\nEmail: {{email}}\nMessage: {{message}}")
    return render_template_string(render_page(f"<h2>{{'Request sent!' if success else 'Error sending request'}}</h2>"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
