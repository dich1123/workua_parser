from flask import Flask, render_template, request, redirect, flash, send_file
import datetime as dt
import workua_parse as wp
import os

app = Flask(__name__)
app.secret_key = 'very secret'

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        search = request.form['search']
        sal_from = request.form['from']
        sal_to = request.form['to']
        info = [search, sal_from, sal_to]
        if '' in info:
            flash('All fields must be not empty!')
            return render_template('index.html')
        try:
            sal_from = int(sal_from)
            sal_to = int(sal_to)
        except ValueError:
            flash('Salary must be integer!')
            return render_template('index.html')

        filename = './results/' + str(dt.datetime.now()) + '.txt'
        parsing = wp.ParseWorkUa(search, sal_from, sal_to, filename)
        parsing.parse_all_and_save()
        all_results = os.listdir('./results')
        all_results.sort(key=lambda x: os.path.getmtime(f'./results/{x}'))
        return send_file(f'./results/{all_results[-1]}', attachment_filename='your_results.txt')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)