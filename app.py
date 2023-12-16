from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import requests

client = MongoClient('mongodb+srv://lxTraining:lxTraining@cluster0.xi7oq7q.mongodb.net/?retryWrites=true&w=majority')
db = client.feconomic
app = Flask(__name__)
SECRET_KEY = "SPARTA"

@app.route('/')
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.account.find_one({"email": payload['id']})
        return render_template('product.html',userinfo=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/admin')
def admin():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.account.find_one({"email": payload['id']})
        print("solomon", user_info)
        return render_template('indexAdmin.html',userinfo=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template(
        'index.html',
        msg=msg
    )

@app.route('/sign_in', methods=['POST'])
def sign_in():
    email_receive = request.form['email_give']
    pass_receive = request.form['pass_give']
    pw_hash = hashlib.sha256(pass_receive.encode("utf-8")).hexdigest()
    result = db.account.find_one(
        {
            "email": email_receive,
            "pass": pw_hash,
        }
    )
    if result['role'] == 'Pembeli':
        payload = {
            "id": email_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode("utf-8")
        return jsonify(
            {
                "result": "success_pembeli",
                "token": token,
            }
        )
    elif result['role'] == 'Penjual':
        payload = {
            "id": email_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode("utf-8")
        return jsonify(
            {
                "result": "success_penjual",
                "token": token,
            }
        )
    elif result['role'] == 'Admin':
        payload = {
            "id": email_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode("utf-8")
        return jsonify(
            {
                "result": "success_admin",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )

@app.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect('/login?msg=There+was+problem+logging+you+in'))
    response.set_cookie('mytoken', '', expires=0)
    # Ganti 'cookie_name' dengan nama cookie yang ingin Anda hapus
    return response

@app.route('/akun', methods=['POST'])
def akun_post():
    nama_receive = request.form['nama_give']
    pass_receive = request.form['pass_give']
    email_receive = request.form['email_give']
    role_receive = request.form['role_give']
    pass_hash = hashlib.sha256(pass_receive.encode("utf-8")).hexdigest()

    doc = {
        'nama': nama_receive,
        'pass': pass_hash,
        'email': email_receive,
        'role': role_receive,
    }

    db.account.insert_one(doc)
    return jsonify({'msg': 'Akun Berhasil Disimpan!'})

@app.route('/akun', methods=['GET'])
def akun_get():
    account_list = list(db.account.find({},{'_id':False}))
    return jsonify({'account':account_list})

@app.route('/daftar-toko', methods=['GET'])
def daftartoko():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.account.find_one({"email": payload['id']})
        return render_template('daftarToko.html',userinfo=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/daftar-toko', methods=['POST'])
def daftarToko():
    nama_receive = request.form['nama_give']
    nomor_receive = request.form['nomor_give']
    jenis_receive = request.form['jenis_give']
    deskripsi_receive = request.form['deskripsi_give']
    email_receive = request.form['email_give']

    #update one ya man
    db.account.update_one(
        {'email' : email_receive},
        {'$set' :{
            'role' : 'Penjual',
            'nama_toko' : nama_receive,
            'nomor_hp' : nomor_receive,
            'jenis_toko' : jenis_receive,
            'deskripsi_toko' : deskripsi_receive,
            }}
    )
    return jsonify({'msg' : 'Update Berhasil'})

@app.route('/profil-toko', methods=['GET'])
def profilToko() :
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.account.find_one({"email": payload['id']})
        return render_template('profilToko.html',userinfo=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/update/profil-toko', methods=['POST'])
def updateProfilToko():
    nama_receive = request.form['nama_give']
    nomor_receive = request.form['nomorHP_give']
    jenis_receive = request.form['jenis_give']
    deskripsi_receive = request.form['description_give']
    email_receive = request.form['email_give']

    #update one ya man
    db.account.update_one(
        {'email' : email_receive},
        {'$set' :{
            'nama' : nama_receive,
            'nomor_hp' : nomor_receive,
            'jenis_toko' : jenis_receive,
            'deskripsi_toko' : deskripsi_receive,
            }}
    )
    return jsonify({'msg' : 'Update Profil Berhasil'})

@app.route('/update/produk', methods=['POST'])
def updateProduk():
    nama_receive = request.form['nama_give']
    harga_receive = request.form['harga_give']
    jenis_receive = request.form['jenis_give']
    desc_receive = request.form['desc_give']
    id_receive = request.form['id_give']
    id_get = int(id_receive)
    #update one ya man
    db.produk.update_one(
        {'id' : id_get},
        {'$set' :{
            'name' : nama_receive,
            'price' : harga_receive,
            'jenis' : jenis_receive,
            'description' : desc_receive,
        }}
    )
    return jsonify({'msg' : 'Update Produk Berhasil'})


@app.route('/list-produk', methods=['GET'])
def listBarang() :
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.account.find_one({"email": payload['id']})
        return render_template('listProduk.html',userinfo=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/tambah-produk', methods=['GET'])
def tambah_produk_get() :
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.account.find_one({"email": payload['id']})
        return render_template('tambahProduk.html',userinfo=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/tambah-produk', methods=['POST'])
def tambah_produk() :
    # count = db.produk.count_documents({})
    
    nama_receive = request.form.get('nama_give')
    harga_receive = request.form.get('harga_give')
    deskripsi_receive = request.form.get('deskripsi_give')
    jenis_receive = request.form.get('jenis_give')
    email_receive = request.form.get('email_give')
    namaToko_receive = request.form.get('namaToko_give')
    # Ambil file gambar yang diunggah
    
    if(list(db.produk.find({},{'_id':False})) == []):
        count = db.produk.count_documents({})
        file = request.files['gambar_give']
        extension = file.filename.split('.')[-1]
        filename = f'{count}-file.{extension}'
        save_to = f'static/img/{filename}'
        file.save(save_to)
        doc = {
            "id" : count,
            "name" : nama_receive,
            "price" : harga_receive,
            "description" : deskripsi_receive,
            "image" : save_to,
            "jenis" : jenis_receive,
            "email" : email_receive,
            "nama_toko" : namaToko_receive
        }
    else:
        latest_document = db.produk.find({}, {'_id': 0, 'id': 1}, sort=[('id', -1)]).limit(1)
        latest_id = None
        for document in latest_document:
            latest_id = document['id']
            break
        id_receive = latest_id + 1
        file = request.files['gambar_give']
        extension = file.filename.split('.')[-1]
        filename = f'{id_receive}-file.{extension}'
        save_to = f'static/img/{filename}'
        file.save(save_to)
        doc = {
            "id" : id_receive,
            "name" : nama_receive,
            "price" : harga_receive,
            "description" : deskripsi_receive,
            "image" : save_to,
            "jenis" : jenis_receive,
            "email" : email_receive,
            "nama_toko" : namaToko_receive
        }
    db.produk.insert_one(doc)
    return jsonify({'msg' : 'Produk Berhasil Ditambahkan'})

@app.route('/produk', methods=['GET'])
def produk_get():
    produk_list = list(db.produk.find({},{'_id':False}))
    return jsonify({'produk':produk_list})

@app.route('/delete-item', methods=['POST'])
def delete_item():
    id_receive = request.form['id_give']
    db.produk.delete_one({'id': int(id_receive)})
    return jsonify({'msg': 'Berhasil Dihapus'})

@app.route('/kirim-pesan', methods=['POST'])
def kirim_pesan():
    pesan_receive = request.form['pesan_give']
    pengirim_receive = request.form['pengirim_give']
    penerima_receive = request.form['penerima_give']
    namaToko_receive = request.form['namaToko_give']
    id_receive = request.form['id_give']
    nama_receive = request.form['nama_give']
    doc = {
        "pesan" : pesan_receive,
        "pengirim" : pengirim_receive,
        "penerima" : penerima_receive,
        "nama_toko" : namaToko_receive,
        "id_prod" : id_receive, 
        "nama" : nama_receive, 
    }

    db.chat.insert_one(doc)
    return jsonify({'msg': 'Berhasil Dikirim'})

@app.route('/chat', methods=['GET'])
def chat_get():
    chat_list = list(db.chat.find({},{'_id':False}))
    return jsonify({'chat':chat_list})

@app.route('/list-chat', methods=['GET'])
def listChat() :
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.account.find_one({"email": payload['id']})
        return render_template('chat.html',userinfo=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))


@app.route('/kelola-akun', methods=["GET"])
def kelola_admin():
    msg = request.args.get("msg")
    return render_template(
        'kelolaAkun.html',
        msg=msg
    )

@app.route('/digital')
def digital():
    msg = request.args.get("msg")
    return render_template(
        'kategori_digital.html',
        msg=msg
    )

@app.route('/kategori-nondigital')
def kategori_nondigital():
    msg = request.args.get("msg")
    return render_template(
        'kategori_nondigital.html',
        msg=msg
    )

@app.route('/hapus/akun', methods=["POST"])
def hapus_acc():
    email_receive = request.form['email_give']
    db.account.delete_one({'email':email_receive})
    return jsonify({'msg':'Berhasil Dihapus'})


@app.route("/api/nick", methods=["GET"])
def api_valid():
    token_receive = request.cookies.get("mytoken")

		# apakah anda sudah melihat pernyataan try/catch sebelumnya?
    try:
				# kita akan coba decode tokennya dengan kunci rahasia
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
				# jika tidak ada masalah, kita seharusnya melihat
				# payload terdekripsi muncul di terminal kita!
        print(payload)

				# payload terdekripsinya seharusnya berisi id user
				# kita bisa menggunakan id ini untuk mencari data user
				# dari database dan mengembalikannya ke user
        userinfo = db.account.find_one({"id": payload["id"]}, {"_id": 0})
        return jsonify({"result": "success", "email": userinfo["email"]})
    except jwt.ExpiredSignatureError:
				# jika anda mencoba untuk mendekripsi token yang sudah expired
				# anda akan mendapatkan error khusus, kita menangani error nya disini
        return jsonify({"result": "fail", "msg": "Your token has expired"})
    except jwt.exceptions.DecodeError:
				# jika ada permasalahan lain ketika proses decoding,
        # kita akan tangani di sini
        return jsonify(
            {"result": "fail", "msg": "There was an error while logging you in"}
        )

@app.route("/api/login", methods=["POST"])
def api_login():
    id_receive = request.form["id_give"]
    pw_receive = request.form["pw_give"]

		# Kita akan mengenkripsi passwordnya disini dengan 
    # cara yang sama seperti user pertama kali mendaftar untuk layanan web
    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

		# Jika kita bisa menemukan user tersebut, kita membuat
    # Token JWT baru untuk mereka
    result = db.account.find_one({"id": id_receive, "pw": pw_hash})

    if result is not None:
		# Untuk menghasilkan token JWT, kita perlu 
        # suatu "payload" dan "kunci rahasia"

        # "kunci rahasia" diperlukan untuk mendekripsi 
        # token dan melihat payload 

        # payload dibawah membawa id user dan tanggal expired token, 
        # artinya anda jika anda dekripsi tokennya, anda  
        # bisa tau id user 

        # jika kita mengatur "exp" tanggal expired, lalu suatu errror 
        # muncul ketika kita mencoba dekripsi tokennya menggunakan 
        # kunci rahasia ketika token telah expired. Ini merupakan hal bagus!
        payload = {
            "id": id_receive,
            "exp": datetime.utcnow() + timedelta(seconds = 60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode("utf-8")

        # mengembalikan token ke client
        return jsonify({"result": "success", "token": token})
		# Jika kita tidak bisa menemukan user di database,
    # kita bisa menangani kasus tersebut disini
    else:
        return jsonify(
            {"result": "fail", "msg": "Either your email or your password is incorrect"}
        )


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)