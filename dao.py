import sqlite3
import datetime


# Operazioni sulle serie

#tutte le serie da database
def get_all_series():                                   
    conn = sqlite3.connect('db/podcast_db.db')         
    conn.row_factory = sqlite3.Row              
    cursor = conn.cursor()        
    sql = 'SELECT serie.id_serie, serie.titolo_serie, serie.descrizione, serie.categoria, serie.immagine_serie, serie.ultima_modifica, utenti.nickname \
            FROM serie LEFT JOIN utenti ON serie.autore = utenti.id \
            ORDER BY ultima_modifica ASC'
    cursor.execute(sql)     
    series = cursor.fetchall()   
    
    cursor.close()                 
    conn.close()                  
    return series

#serie create da current user
def get_serie_create(id):                                 
    conn = sqlite3.connect('db/podcast_db.db')         
    conn.row_factory = sqlite3.Row                          
    cursor = conn.cursor()                                  
    sql = 'SELECT serie.id_serie, serie.titolo_serie, serie.descrizione, serie.categoria, serie.immagine_serie, serie.ultima_modifica, utenti.nickname \
            FROM serie LEFT JOIN utenti ON serie.autore = utenti.id \
            WHERE serie.autore=? \
            ORDER BY ultima_modifica DESC'
    cursor.execute(sql, (id,))                                     
    series = cursor.fetchall()    
    
    cursor.close()                                          
    conn.close()                                            
    return series

#prende singola serie da id
def get_serie(id_s):                                     
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT serie.id_serie, serie.titolo_serie, serie.descrizione, serie.categoria, serie.immagine_serie, serie.ultima_modifica, serie.autore, utenti.nickname\
            FROM serie LEFT JOIN utenti ON serie.autore = utenti.id \
            WHERE serie.id_serie = ?'
    cursor.execute(sql, (id_s,))
    serie = cursor.fetchone()

    cursor.close()
    conn.close()

    return serie

#serie seguite da current user
def get_serie_seguite(id):
    conn = sqlite3.connect('db/podcast_db.db')          
    conn.row_factory = sqlite3.Row                          
    cursor = conn.cursor()                                 
    sql = 'SELECT serie.id_serie, serie.titolo_serie, serie.descrizione, serie.categoria, serie.immagine_serie, serie.ultima_modifica, utenti.nickname \
            FROM serie LEFT JOIN followers \
            ON serie.id_serie = followers.serie \
            LEFT JOIN utenti ON serie.autore=utenti.id\
            WHERE followers.utente = ? \
            ORDER BY ultima_modifica DESC'
    cursor.execute(sql, (id,))                                  
    series = cursor.fetchall()    
    
    cursor.close()                                  
    conn.close()                            
    return series

def isfollower(id_s, usr):
    conn = sqlite3.connect('db/podcast_db.db')          
    conn.row_factory = sqlite3.Row                         
    cursor = conn.cursor()       
    
    sql = 'SELECT * \
            FROM followers \
            WHERE followers.utente = ? AND followers.serie = ?'
    cursor.execute(sql, (usr , id_s))                                    
    cnt = cursor.fetchone()    
    
    cursor.close()                                     
    conn.close()                                       
    return cnt 

#singolo episodio
def get_episodio(id_e):                                      
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT episodi.id_episodio, episodi.titolo, episodi.file, episodi.descrizione, episodi.serie, episodi.data_pubblicazione, serie.titolo_serie, serie.autore\
            FROM episodi LEFT JOIN serie ON episodi.serie = serie.id_serie \
            WHERE episodi.id_episodio = ? '
    cursor.execute(sql, (id_e,))
    episodi = cursor.fetchone()

    cursor.close()
    conn.close()

    return episodi


#tutti gli episodi con data inferiore a oggi
def get_episodi(id_s):                                      
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    oggi=datetime.date.today()

    sql = 'SELECT episodi.id_episodio, episodi.titolo, episodi.file, episodi.descrizione, episodi.data_pubblicazione, serie.titolo_serie\
            FROM episodi LEFT JOIN serie ON episodi.serie = serie.id_serie \
            WHERE serie.id_serie = ? AND episodi.data_pubblicazione <= ?\
            ORDER BY data_pubblicazione DESC'
    cursor.execute(sql, (id_s, oggi))
    episodi = cursor.fetchall()

    cursor.close()
    conn.close()
    return episodi

def get_all_episodi(id_s):                                      
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT episodi.id_episodio, episodi.titolo, episodi.file, episodi.descrizione, episodi.data_pubblicazione, serie.titolo_serie\
            FROM episodi LEFT JOIN serie ON episodi.serie = serie.id_serie \
            WHERE serie.id_serie = ? \
            ORDER BY data_pubblicazione DESC'
    cursor.execute(sql, (id_s,))
    episodi = cursor.fetchall()

    cursor.close()
    conn.close()
    return episodi

#tutti i commenti di un episodio
def get_comments(id_e): 
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT commenti.id_commento, commenti.data_pubb_commento, commenti.testo_commento, commenti.id_utente ,utenti.nickname, utenti.immagine_profilo, episodi.serie \
            FROM commenti LEFT JOIN utenti ON commenti.id_utente = utenti.id \
                LEFT JOIN episodi ON commenti.id_episodio=episodi.id_episodio \
            WHERE commenti.id_episodio = ?'
    cursor.execute(sql, (id_e,))
    comments = cursor.fetchall()

    cursor.close()
    conn.close()
    return comments


#operazioni di inserimento
def add_serie(serieIn): 
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    x = datetime.datetime.now()
    
    success = False                                         
    sql = "INSERT INTO serie(titolo_serie,descrizione,categoria,immagine_serie,autore,ultima_modifica) VALUES(?,?,?,?,?,?)"
       
    cursor.execute(sql, (serieIn['titolo_serie'], serieIn['testo'], serieIn['categoria'], serieIn['immagine_serie'], serieIn['autore'], x.strftime("%Y-%m-%d")))
    try:                                                    
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))                               
        conn.rollback()

    cursor.close()
    conn.close()
    return success

def add_episodio(episode):                                         
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    success = False                                         
    sql = "INSERT INTO episodi(titolo,file,descrizione,data_pubblicazione,serie) VALUES(?,?,?,?,?)"
    cursor.execute(sql, (episode['titolo_episodio'], episode['sound'], episode['testo'], episode['data_pubblicazione'], episode['serie']))
    try:                                                   
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))                              
        conn.rollback()
    if success == False:
         return success                                          

    success = False                                         
    sql = "UPDATE serie SET ultima_modifica=?"
    cursor.execute(sql, (episode['data_pubblicazione'],))
    try:                                                   
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()
    return success                                        

def add_comment(comment, id):      
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    x = datetime.datetime.now()                            

    sql = 'INSERT INTO commenti(data_pubb_commento,testo_commento,id_episodio, id_serie, id_utente) VALUES(?,?,?,?,?)'
    cursor.execute(sql, (x.strftime("%Y-%m-%d"), comment['testo'], comment['id_episodio'], comment['serie'], id))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()
    return success


#gestione follow
def segui(id_s, id_u):
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False

    sql = 'INSERT INTO followers(serie, utente) VALUES(?,?)'
    cursor.execute(sql, (id_s, id_u))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success
      
def nonsegui(id_s, id_u):
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False

    sql = 'DELETE FROM followers \
        WHERE serie= ? AND utente= ?'
    cursor.execute(sql, (id_s, id_u))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success


#operazioni di aggiornamento
def update_serie(serieIn):
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "UPDATE serie SET descrizione=? , categoria= ? WHERE serie.id_serie = ?;"
 
    cursor.execute(sql, (serieIn['testo'], serieIn['categoria'], serieIn['id_serie']))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()
    return success

def update_episodio(ep):
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "UPDATE episodi SET descrizione=? , titolo= ? WHERE episodi.id_episodio = ?;"
 
    cursor.execute(sql, (ep['testo'], ep['titolo'], ep['id_episodio']))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()
    return success

    
#operazioni di eliminazione
def delete_commento_by_id(id_c):
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False

    sql = 'DELETE FROM commenti \
        WHERE id_commento = ?'
    cursor.execute(sql, (id_c,))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()
    return success

def elimina_serie_by_id(id_s):
    conn = sqlite3.connect('db/podcast_db.db')
    conn.execute("PRAGMA foreign_keys = 1")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False

    sql = 'DELETE FROM serie \
        WHERE id_serie = ?'
    cursor.execute(sql, (id_s,))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()
    return success
    
def elimina_episodio_by_id(id_e):
    conn = sqlite3.connect('db/podcast_db.db')
    conn.execute("PRAGMA foreign_keys = 1")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False

    sql = 'DELETE FROM episodi \
        WHERE id_episodio = ?'
    cursor.execute(sql, (id_e,))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()
    return success


#operazioni su utente
def get_user_by_nickname(nickname):                     
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE nickname = ?'
    cursor.execute(sql, (nickname,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user

def get_user_by_email(email):
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE email = ?'
    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user

def get_utente_by_id(id):                                    
    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE id = ?'
    cursor.execute(sql, (id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user

def add_user(user):                                         

    conn = sqlite3.connect('db/podcast_db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO utenti(nickname,email,password,immagine_profilo,creatore) VALUES(?,?,?,?,?)'   

    try:                                                                           
        cursor.execute(
            sql, (user['nickname'], user['email'], user['password'], user['immagine_profilo'], user['creatore']))
        conn.commit()   
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()
    return success