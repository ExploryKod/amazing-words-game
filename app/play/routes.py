from app.play import bp
from random import randint
from datetime import timedelta
from flask import Flask, request, redirect, session, url_for, flash
from flask.templating import render_template
fl_session = session
from app.models.game_tables import db
from app.models.authentication_check import *
from app.models.authentication_tables import User
from words import chose_list, list_of_words
from letters import letter_blend
 
with app.app_context():  # From SQLAlchemy 3.0 
    db.create_all()
    
# function to render index page (home)
@bp.route('/')
def index():
	# Query all data and then pass it to the template
    user_words = Guess.query.all()
    resp = Secrets.query.all()
    player = Users.query.all() 
    points = Scores.query.all()
    return render_template('index.html', user_words=user_words, resp=resp, player=player, points=points, fl_session=fl_session)

@bp.route('/add_data')
def add_data():
    is_a_turn = False
    round_num = randint(1,3)
    db.session.query(Secrets).delete()
    db.session.query(Guess).delete()
    db.session.query(Letters).delete()
    db.session.commit()
    base_list = chose_list(round_num)
    secret_words = list_of_words(base_list)
    
    if secret_words != '':
        letters = letter_blend(secret_words)
        blend_words = Letters(round_1=letters) 
        secret_1 = secret_words[0]
        secret_2 = secret_words[1]
        secret_3 = secret_words[2]
        first = Secrets(secret_1=secret_1, secret_2=secret_2,secret_3=secret_3)
        db.session.add(first)
        db.session.add(blend_words)
        db.session.commit()
            
    words_star = Secrets.query.all()
    
    return render_template('play.html', fl_session=fl_session, letters=letters, secret_words=secret_words, word_1=secret_1,word_2=secret_2,word_3=secret_3,first=first, words_star=words_star, is_a_turn = is_a_turn, blend_words=blend_words)

@bp.route('/turn')
def turns():
    words_star = Secrets.query.all()
    blend_words = Letters.query.all()
    is_a_turn = True
    return render_template('play.html', words_star=words_star, is_a_turn = is_a_turn, blend_words=blend_words, fl_session=fl_session)

# function to add profiles
@bp.route('/add', methods=["POST"])
def profile():
    word = request.form.get("word")
    pseudo = request.form.get("pseudo")
    words_star = Secrets.query.all()
    if word == words_star[-1].secret_1 or word == words_star[-1].secret_2 or word == words_star[-1].secret_3:
        point = 1
    else:
        point = 0
    db.session.query(Guess).delete()
    db.session.commit()
	# create an object of the Guess class of models
	# and store data as a row in our datatable
    if word != '' and pseudo != '':
        answ = Guess(word=word, user_id=pseudo)
        you = Users(pseudo=pseudo, guess=word)
        # encore faudra t-il créer la relation (scores_id (FK) => PK de Users via users_scores rel)
        points = Scores(score=point,score_object=word, scores_id = pseudo)
        db.session.add(answ)
        db.session.add(you)
        db.session.add(points)
        db.session.commit()
        return redirect(url_for('index'))
    elif word != words_start:
        return render_template('index.html', words_star=words_star, word=word, fl_session=fl_session)
    else:
	    return redirect(url_for('index'))

@bp.route('/delete/<int:id>')
def erase(id):
	# Deletes the data on the basis of unique id and
	# redirects to home page
	data = Guess.query.get(id)
	db.session.delete(data)
	db.session.commit()
	return redirect('/')

@bp.route('/delete_all/<int:id>')
def delete_all(id):
    data = Secrets.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/')

# if __name__ == '__main__':
#     app.secret_key = os.urandom(12)
#     app.run(debug=True,host='0.0.0.0', port=4000)