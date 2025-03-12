# import module
from flask import Flask, render_template, request, session, redirect, flash, url_for
from datetime import date, datetime
from flask_session import Session
import dao

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from PIL import Image

# create the application
app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'   

login_manager = LoginManager()                      
login_manager.login_view = 'login'                  
login_manager.init_app(app)

PROFILE_IMG_HEIGHT = 130                            #dimensioni immagini
SERIE_IMG_WIDTH = 300

#homepage
@app.route('/', methods=['GET', 'POST'])                
def home():
    series = dao.get_all_series()                        
    if current_user.is_authenticated:          
        create = dao.get_serie_create(current_user.id)
        seguite = dao.get_serie_seguite(current_user.id)
        return render_template('home.html', series=series, create=create, seguite=seguite)
    else:
        return render_template('home.html', series=series)

#accedi
@app.route('/accedi')                                   
def login():
    return render_template('login.html')                

@app.route('/accedi', methods=['POST'])
def login_post():
    nickname = request.form.get('nicknameIn')
    password = request.form.get('passwordIn')

    utente = dao.get_user_by_nickname(nickname)           
   
    if not utente or not check_password_hash(utente['password'], password):         
        flash('Inserite credenziali errate, riprovare', 'danger')                    
        return redirect(url_for('login'))                                       
    else:                                                                                   
        new = User(id=utente['id'], email=utente['email'], nickname=utente['nickname'], password=utente['password'], immagine_profilo=utente['immagine_profilo'], creatore=utente['creatore'])
        login_user(new, True)                                 
        return redirect(url_for('home'))
    
@login_manager.user_loader                              
def load_user(id):
    utente = dao.get_utente_by_id(id)                

    if utente is not None:
        log_user = User(id=utente['id'], email=utente['email'], nickname=utente['nickname'], password=utente['password'], immagine_profilo=utente['immagine_profilo'], creatore=utente['creatore'])
    else:
        log_user = None
        
    return log_user

#iscriviti
@app.route('/iscriviti') 
def signup():
    return render_template('signup.html')

@app.route('/iscriviti', methods=['POST'])              
def signup_post():
    nickname = request.form.get('nickname')
    email = request.form.get('email')
    password = request.form.get('password')
    creatore = request.form.get('creatore')
    
    
    user_in_db = dao.get_user_by_nickname(nickname)
    user2_in_db = dao.get_user_by_email(email)

    if user_in_db:
        flash('Esiste già un utente registrato con questo nickname', 'danger')
        return redirect(url_for('signup'))
    
    elif user2_in_db:
        flash('Esiste già un utente registrato con questa mail, fai il login', 'danger')
        return redirect(url_for('signup'))
    
    elif '@' in email:  
        img_profilo = ''
        usr_image = request.files['immagine_profilo'] 
        if usr_image:  
            img = Image.open(usr_image)    
            width, height = img.size                    
            new_width = PROFILE_IMG_HEIGHT * width / height
            size = new_width, PROFILE_IMG_HEIGHT
            img.thumbnail(size, Image.ANTIALIAS) 
            left = (new_width/2 - PROFILE_IMG_HEIGHT/2)
            top = 0
            right = (new_width/2 + PROFILE_IMG_HEIGHT/2)
            bottom = PROFILE_IMG_HEIGHT
            img = img.crop((left, top, right, bottom)) 
            ext = usr_image.filename.split('.')[1]
            img.save('static/' + nickname.lower() + '.' + ext)
            img_profilo = nickname.lower() + '.' + ext
        else:
            img_profilo="nopicture.jpeg"
        

        new_user = {
            "nickname": nickname,
            "email": email,
            "password": generate_password_hash(password, method='sha256'),
            "immagine_profilo": img_profilo,
            "creatore": creatore
        }                                                      

        success = dao.add_user(new_user)                     

        if success:
            flash('Utente creato correttamente', 'success')
            return redirect(url_for('home'))
        else:
            flash('Errore nella creazione: riprova!', 'danger')
    else:
        flash('Errore nella creazione, verifica mail: riprova!', 'danger')

    return redirect(url_for('signup'))

#profilo
@app.route('/profile')
@login_required
def profile():
    id=current_user.id
    series = dao.get_serie_seguite( id )                      
    return render_template('profile.html',  series=series)

#pagina serie
@app.route('/serie<int:id>')                           
def single_serie(id): 
    serie=dao.get_serie(id)          
    if current_user.is_authenticated:
        id_u=current_user.id
        if serie['autore'] == id_u:
            episodi=dao.get_all_episodi(id)
            return render_template('serie.html', serie=serie, episodi=episodi, oggi=date.today())
        else:
            episodi=dao.get_episodi(id) 
            is_follower=dao.isfollower(id, id_u)
            return render_template('serie.html', serie=serie, episodi=episodi, is_follower=is_follower, oggi=date.today())   
    else:
        episodi=dao.get_episodi(id) 
        return render_template('serie.html', serie=serie, episodi=episodi, oggi=date.today())

#pagina episodio
@app.route('/series<int:id>/episode<int:id_e>')                          
def single_episodio(id, id_e):    
    episodi=dao.get_episodio(id_e)                                       
    comments = dao.get_comments(id_e)             
    serie= dao.get_serie(id)
    return render_template('episodio.html', serie=serie, episodi=episodi, comments=comments)   

#creazione nuova serie
@app.route('/serie/new', methods=['GET', 'POST'])
@login_required
def new_serie():
    if request.method == 'POST':                        
        if current_user.is_authenticated:               
            serie = request.form.to_dict()               
                        
            if serie['testo'] == '':                     
                app.logger.error('La serie non può essere vuota!')                              
                flash('Serie non creata correttamente: il testo non può essere vuoto!', 'danger')   
                return redirect(url_for('home'))

            if serie['titolo_serie'] == '':                     
                app.logger.error('Il titolo non può essere vuoto!')                               
                flash('Serie non creata correttamente: il titolo non può essere vuoto!', 'danger') 
                return redirect(url_for('home'))            
            
            if serie['categoria'] == '':                     
                app.logger.error('La categoria non può essere vuota!')                               
                flash('Serie non creata correttamente: la categoria non può essere vuota!', 'danger')
                return redirect(url_for('home'))            
                   
            serie_image = request.files['immagine_serie'] 
            if serie_image:
                if serie_image.filename.endswith('.jpg') or serie_image.filename.endswith('.jpeg') or serie_image.filename.endswith('.png'):
                    img = Image.open(serie_image)            
                    width, height = img.size               
                    new_height = height/width * SERIE_IMG_WIDTH  
                    size = SERIE_IMG_WIDTH, new_height                

                    img.thumbnail(size, Image.ANTIALIAS)
                    img.save('static/' + serie_image.filename)
                    serie['immagine_serie'] = serie_image.filename
                    id = current_user.id           
                    serie['autore'] = id       
                    success = dao.add_serie(serie)
                else:
                    flash('Errore nella creazione della serie, problemi con immagine: riprova!', 'danger')       
                    return redirect(url_for('home'))
            else:
                success=False   
             
            if success:                                         
                flash('Serie creata correttamente', 'success')   
            else:                                                                   
                flash('Errore nella creazione della serie: riprova!', 'danger')       
                
    return redirect(url_for('home'))                          

#creazione nuovo episodio
@app.route('/episodio/new', methods=['GET', 'POST'])
@login_required
def new_episode():
    if request.method == 'POST':                       
        if current_user.is_authenticated:               
            episodio = request.form.to_dict()        

            id_s=episodio['serie']            
            if episodio['titolo_episodio'] == '':      
                app.logger.error('Il titolo non può essere vuoto!')
                flash('Episodio non creato correttamente: il titolo non può essere vuoto!', 'danger')  
                return redirect(url_for('single_serie', id=id_s))
 
            if episodio['testo'] == '':
                app.logger.error('La descrizione non può essere vuota!')                               
                flash('Episodio non creato correttamente: la descrizione non può essere vuota!', 'danger')
                return redirect(url_for('single_serie', id=id_s))                     

            if episodio['data_pubblicazione'] == '':
                episodio['data_pubblicazione']=date.today() 
            elif datetime.strptime(episodio['data_pubblicazione'], '%Y-%m-%d').date() < date.today(): 
                app.logger.error('Data errata')
                flash('Episodio non creato correttamente: la data deve essere maggiore o uguale di quella corrente!', 'danger')
                return redirect(url_for('single_serie', id=id_s))
                                                                      
            episodio_file = request.files['sound'] 
            if episodio_file:
                if episodio_file.filename.endswith(".mp3"):
                    episodio_file.save('static/' + episodio_file.filename) 
                    episodio['sound'] = episodio_file.filename 
                    success = dao.add_episodio(episodio)
                else:
                    flash('Errore nella creazione dell\'episodio, problemi con estensione audio: riprova!', 'danger')
                    return redirect(url_for('single_serie', id=id_s))
            else:
                success=False
            
            if success:
                flash('Episodio creato correttamente', 'success')
            else:                                                                  
                flash('Errore nella creazione dell\'episodio: riprova!', 'danger')     

    return redirect(url_for('single_serie', id=id_s))

#creazione nuovo commento
@app.route('/comments/new', methods=['POST'])
@login_required           
def new_comment():
    comment = request.form.to_dict()
    if comment['testo'] == '':
        app.logger.error('Il commento non può essere vuoto!')
        flash(
            'Commento non creato correttamente: il commento non può essere vuoto!', 'danger')
        return redirect(url_for('single_episodio', id=id ,id_e=comment['id_episodio']))

    id = current_user.id
    success = dao.add_comment(comment, id)

    if success:
        flash('Commento creato correttamente', 'success')
    else:
        flash('Errore nella creazione del commento: riprova!', 'danger')

    return redirect(url_for('single_episodio',  id=comment['serie'], id_e=comment['id_episodio']))


#modifiche
@app.route('/serie/update', methods=['GET' , 'POST'])
@login_required
def modifica_serie():
    if request.method == 'POST':                       
        if current_user.is_authenticated:               
            serie = request.form.to_dict() 
            id_s=serie['id_serie']
             
                        
            if serie['testo'] == '':
                app.logger.error('La descrizione non può essere vuota!')
                flash('Serie non modficata correttamente: la descrizione non può essere vuota!', 'danger')
                return redirect(url_for('single_serie', id=id_s))
            
            if serie['categoria'] == '':       
                app.logger.error('La categoria non può essere vuota!')
                flash('Serie non modificata correttamente: la categoria non può essere vuota!', 'danger')   
                return redirect(url_for('single_serie', id=id_s))            

            id = current_user.id                        
            serie['autore'] = id                       
        
            success = dao.update_serie(serie)                           
 
            if success:                                        
                flash('Serie modificata correttamente', 'success')   
            else:                                                                   
                flash('Errore nella modifica della serie: riprova!', 'danger')      

    return redirect(url_for('single_serie', id=id_s))        

@app.route('/episodio/update', methods=['GET' , 'POST'])
@login_required
def modifica_episodio():
    if request.method == 'POST':                       
        if current_user.is_authenticated:               
            episodio = request.form.to_dict()           
            id_e=episodio['id_episodio']
            id_s=episodio['id_serie']
                        
            if episodio['titolo'] == '':                    
                app.logger.error('Il titolo non può essere vuoto!')  
                flash('Episodio non modificato: il titolo non può essere vuoto!', 'danger') 
                return redirect(url_for('single_episodio',  id=id_s, id_e=id_e))
                        
                        
            if episodio['testo'] == '':                   
                app.logger.error('La descrizione non può essere vuota!')   
                flash('Episodio non modificato: la descrizione non può essere vuota!', 'danger')
                return redirect(url_for('single_episodio',  id=id_s, id_e=id_e))

            id = current_user.id            
            
            success = dao.update_episodio(episodio)                        
            if success:                                         
                flash('Episodio modificato correttamente', 'success')   
            else:                                                                   
                flash('Errore nella modifica dell\'episodio: riprova!', 'danger')  

    return redirect(url_for('single_episodio',  id=id_s, id_e=id_e))
   
#eliminazioni
@app.route("/elimina_serie<int:id_s>")
@login_required
def elimina_serie(id_s):
    success=False
    id_u=current_user.id
    serie= dao.get_serie(id_s)
    if (serie['autore'] ==id_u):
        success = dao.elimina_serie_by_id(id_s)
    
    if success:
        flash('Eliminazione della serie effettuata correttamente', 'success')  
    else:                                                                   
        flash('Errore, eliminazione non effettuata' , 'danger')

    return redirect(url_for('home', id=id_s))

@app.route("/elimina_episodio<int:id_e>")
@login_required
def elimina_episodio(id_e):
    success=False
    id_u=current_user.id
    episodio= dao.get_episodio(id_e)
    if (episodio['autore'] ==id_u):
        success = dao.elimina_episodio_by_id(id_e)
    
    if success:
        flash('Eliminazione effettuata correttamente', 'success')   
    else:                                                                   
        flash('Errore, eliminazione non effettuata' , 'danger')

    return redirect(url_for('single_serie', id=episodio['serie']))     
     
@app.route('/series<int:id>/episode<int:id_e>/delete<int:id_c>')  
@login_required                         
def elimina_commento(id, id_e, id_c):
    success=False
    success=dao.delete_commento_by_id(id_c)
    episodi=dao.get_episodio(id_e)                                       
    comments = dao.get_comments(id_e)             
    serie= dao.get_serie(id)
    if success:                                         
        flash('Commento eliminato', 'success')   
    else:                                                                  
        flash('Errore nell\'eliminazione del commento: riprova!', 'danger')    
    return render_template('episodio.html', serie=serie, episodi=episodi, comments=comments)


#operazioni di follow e unfollow
@app.route("/follow_serie<int:id_s>")
@login_required
def follow(id_s):
    id_u=current_user.id
    dao.segui(id_s, id_u)
    return redirect(url_for('single_serie', id=id_s))

@app.route("/unfollow_seriep<int:id_s>")
@login_required
def u_by_profile(id_s):
    id_u=current_user.id
    dao.nonsegui(id_s, id_u)
    return redirect(url_for('profile'))

@app.route("/unfollow_serie<int:id_s>")
@login_required
def unfollow(id_s):
    id_u=current_user.id
    dao.nonsegui(id_s, id_u)
    return redirect(url_for('single_serie', id=id_s))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)