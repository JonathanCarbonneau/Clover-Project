import smtplib
import json
from xml.dom.minidom import Element
import requests
import statistics
import datetime
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask_table import Table, Col


def updateJson(merchantID, apiKey):
    url = "https://sandbox.dev.clover.com/v3/merchants/" + \
        merchantID + "/orders?expand=payment.cardTransaction"

    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + apiKey
    }

    response = requests.get(url, headers=headers)
    data = response.text
    StructuredData = json.loads(data)
    # print(StructuredData['elements'])
    listTotal = []
    listTimes = []
    costomers = {}
    transactions = []
    totalPerCostomer = []
    for i in StructuredData['elements']:
        # print(i.keys())
        total = 0
        time = '0000-00-00 00:00:00'

        if 'total' in i:
            total = (float(i['total']) / 100)
            time = (datetime.datetime.fromtimestamp(
                int(i['clientCreatedTime']) / 1000).strftime("%Y-%m-%d %H:%M:%S"))
            listTimes.append(time)
            listTotal.append(float(total))

        if 'payments' in i:
            payment = i['payments']['elements'][0]['cardTransaction']
        # print(payment.keys())
            creditCards = [
                payment['cardType'], payment['first6'], payment['last4']
            ]
            transaction = [creditCards, total, time]
            if str(creditCards) in costomers:
                costomers[str(creditCards)]['total'] += total
            else:
                costomers[str(creditCards)] = {
                    'total': total, 'creditCards': creditCards}
            transactions.append(transaction)
    costomers = dict(
        sorted(costomers.items(), key=lambda item: item[1]['total'], reverse=True))
    print(costomers)
    newurl = "https://sandbox.dev.clover.com/v3/merchants/" + \
        merchantID + "/customers?expand=addresses,emailAddresses,phoneNumbers,cards,metadata"
    newresponse = requests.get(newurl, headers=headers)
    newdata = newresponse.text
    newStructuredData = json.loads(newdata)
    for i in newStructuredData['elements']:
        if 'cards' in i:
            if i['cards']['elements']:
                currentcard = i['cards']['elements'][0]
                if 'cardType' and 'first6' and 'last4' in currentcard:
                    cardInfo = str(
                        [currentcard['cardType'], currentcard['first6'], currentcard['last4']])
                    if costomers[cardInfo]:
                        if 'firstName' in i:
                            costomers[cardInfo]['firstName'] = i['firstName']
                        if 'lastName' in i:
                            costomers[cardInfo]['lastName'] = i['lastName']
                        if 'emailAddresses' in i:
                            costomers[cardInfo]['emailAddresses'] = i['emailAddresses']
                        if 'phoneNumbers' in i:
                            costomers[cardInfo]['phoneNumbers'] = i['phoneNumbers']
                        totalPerCostomer.append(
                            float(costomers[cardInfo]['total']))
    customerstd = statistics.stdev(totalPerCostomer)
    listTotalstd = statistics.stdev(listTotal)
    costomerQuantiles = [round(q, 1)
                         for q in statistics.quantiles(totalPerCostomer, n=10)]
    transactionQuantiles = [round(q, 1)
                            for q in statistics.quantiles(listTotal, n=10)]
    return(transactions, costomers, customerstd, listTotalstd, listTimes, listTotal, costomerQuantiles, transactionQuantiles)


def sendmail(costomers, listTotal, fromEmail, toEmail):
    #print(max(costomers, key=costomers.get))
    msg = MIMEMultipart()
    msg['From'] = fromEmail
    msg['To'] = toEmail
    msg['Subject'] = 'Prototype clover script email'
    message = 'Here is the data: The coustomer who spent the most is ' + str(
        max(costomers, key=costomers.get)) + ' with a spending of $' + str(
            round(costomers[str(max(costomers, key=costomers.get))], 2)
    ) + ' The coustomer who spent the least is ' + str(
            min(costomers, key=costomers.get)) + ' with a spending of $' + str(
                round(costomers[str(min(costomers, key=costomers.get))], 2)
    ) + ' The avarage customer spending is: ' + str(
                statistics.mean(
                    listTotal)) + ' We expect coustomers to spend around: ' + str(
                        statistics.mode(listTotal))

    msg.attach(MIMEText(message))
    mailserver = smtplib.SMTP('smtp.gmail.com', 587)
    # identify ourselves to smtp gmail client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    mailserver.login(fromEmail, 'wkputaniqeufvsjh')
    mailserver.sendmail(toEmail, toEmail, msg.as_string())
    mailserver.quit()


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    # return(transactions,0 costomers,1 customerstd,2 listTotalstd,3 listTimes,4 listTotal,5 costomerQuantiles,6 transactionQuantiles7)
    post = get_post(post_id)
    transactionData = updateJson(post['merchantID'], post['apiKey'])
    print(len(transactionData[4]), len(transactionData[5]))
    names = []
    values = []
    for i in transactionData[1].items():
        print(i)
        names.append(i[1]['firstName'] + " " + i[1]['lastName'])
        values.append(i[1]['total'])
    return render_template('post.html', post=post, customers=transactionData[1], listTimes=transactionData[4], listTotal=transactionData[5], names=names, values=values)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        email = request.form['email']
        title = request.form['title']
        content = request.form['content']
        merchantID = request.form['merchantID']
        apiKey = request.form['apiKey']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (email, merchantID, apiKey, title, content) VALUES (?, ?, ?, ?, ?)',
                         (email, merchantID, apiKey, title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))
