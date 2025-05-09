
from flask import Flask, render_template_string, request, redirect, session
import random
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta-supersegura'

# Banco de dados simples (em memória)
users = {}

# HTML base
login_html = """
<h2>Login</h2>
<form method="POST">
  Email: <input name="email" type="email" required><br>
  Senha: <input name="password" type="password" required><br>
  <button type="submit">Entrar</button>
</form>
<p>Não tem conta? <a href="/cadastro">Cadastre-se</a></p>
"""

cadastro_html = """
<h2>Cadastro</h2>
<form method="POST">
  Email: <input name="email" type="email" required><br>
  Senha: <input name="password" type="password" required><br>
  <button type="submit">Cadastrar</button>
</form>
<p>Já tem conta? <a href="/">Faça login</a></p>
"""

painel_html = """
<h2>Bem-vindo, {{ email }}</h2>
<p>Números gerados: {{ numeros }}</p>
<form method="POST">
  <button type="submit">Gerar e Enviar por E-mail</button>
</form>
<a href="/logout">Sair</a>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        if email in users and users[email] == senha:
            session['email'] = email
            return redirect('/painel')
        else:
            return 'Login inválido'
    return render_template_string(login_html)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        users[email] = senha
        return redirect('/')
    return render_template_string(cadastro_html)

@app.route('/painel', methods=['GET', 'POST'])
def painel():
    if 'email' not in session:
        return redirect('/')
    email = session['email']
    numeros = gerar_lotofacil()
    if request.method == 'POST':
        enviar_email(email, numeros)
    return render_template_string(painel_html, email=email, numeros=numeros)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

def gerar_lotofacil():
    return sorted(random.sample(range(1, 26), 15))

def enviar_email(destinatario, numeros):
    conteudo = f"Seus números da Lotofácil: {numeros}"
    msg = EmailMessage()
    msg.set_content(conteudo)
    msg['Subject'] = 'Seus números da Lotofácil'
    msg['From'] = os.environ['EMAIL_USER']
    msg['To'] = destinatario

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASS'])
        smtp.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)
