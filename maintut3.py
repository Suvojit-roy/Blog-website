from flask import Flask,render_template,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import math
# from flask_mail import Mail, Message

with open('config.json','r') as c:
    params=json.load(c)["params"]

local_server=True

app = Flask(__name__)
app.secret_key='super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = params['my_email']
app.config['MAIL_PASSWORD'] = params['password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app) 

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=True, nullable=False)
    msg = db.Column(db.String(20), unique=False, nullable=False)
    date = db.Column(db.String(120), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Blogpost(db.Model):
    slug = db.Column(db.String(20))
    sno = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(20), unique=True, nullable=False)
    content= db.Column(db.String(200), unique=False, nullable=False)
    img_file= db.Column(db.String(12), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)


# @app.route('/')
# def home():
#     posts=Blogpost.query.filter_by().all()[0:params['no_of_posts']]
#     posts=Blogpost.query.filter_by().all()
#     last=math.ceil(len(posts)/int(params['no_of_posts']))
    
#     page=request.args.get('page')
#     if(not str(page).isnumeric()):
#         page=1

#     page=int(page)

#     posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
#     if(page==1):
#         prev="#"
#         next="/?page="+str(page+1)
#     elif (page==last):
#         next="#"
#         prev="/?page="+str(page-1)
#     else:
#         prev="/?page="+str(page-1)
#         next="/?page="+str(page+1)
        

#     return render_template('index.html',params=params,posts=posts,prev=prev,next=next)
    # return render_template('index.html',params=params,posts=posts)

@app.route('/about')
def about():
    
    return render_template('about.html')


@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post=Blogpost.query.filter_by(slug=post_slug).first()

    return render_template('post.html',post=post)

@app.route('/contact',methods=["GET","POST"])
def contact():
    if(request.method=="POST"): 
    
        name=request.form.get("name")
        email=request.form.get("email")
        phone=request.form.get("phone")
        message=request.form.get("message")

        entry=Contacts(name=name,phone_num=phone,msg=message,date=datetime.now(),email=email)

        db.session.add(entry)
        db.session.commit()
        
        mail.send_message('This message is from '+name,
                            sender=email,
                            recipients='suvojit.royuvo@gmail.com',
                            body=message

        )

    
       
        
        
    return render_template('contact.html')

@app.route('/post')
def post():
    
    return render_template('post.html')



@app.route('/dashboard',methods=["GET","POST"])
def dash():


    if('user' in session and session['user']==params['admin_user']):
        posts=Blogpost.query.all()
        return render_template('dashboard.html',params=params,posts=posts)

    if request.method=="POST":
        username=request.form.get("uname")
        userpass=request.form.get("pass")
        if(username==params['admin_user'] and userpass==params['admin_password']):
            session['user']=username
            posts=Blogpost.query.all()
            return render_template('dashboard.html',params=params,posts=posts)       
    
    else :
        return render_template('admin.html',params=params)

    return render_template('admin.html',params=params)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/")
def home():
    posts=Blogpost.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))
    
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1

    page=int(page)

    posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    elif (page==last):
        next="#"
        prev="/?page="+str(page-1)
    else:
        prev="/?page="+str(page-1)
        next="/?page="+str(page+1)
        

    return render_template('index.html',params=params,posts=posts,prev=prev,next=next)

    

    



@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete(sno):
    if('user' in session and session['user']==params['admin_user']):
        post=Blogpost.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

@app.route("/edit/<string:sno>",methods=["GET","POST"])
def edit(sno):
    if('user' in session and session['user']==params['admin_user']):
        if(request.method=="POST"):
            box_title=request.form.get('title')
            content=request.form.get('content')
            slug=request.form.get('slug')
            img_file=request.form.get('img_file')
            date=datetime.now()

            if(sno=='0'):
                post=Blogpost(title=box_title,content=content,slug=slug,img_file=img_file,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post=Blogpost.query.filter_by(sno=sno).first()
                post.title=box_title
                post.content=content
                post.slug=slug
                post.img_file=img_file
                post.date=date
                db.session.commit()

                return redirect('/edit/'+sno)


    post=Blogpost.query.filter_by(sno=sno).first()
    return render_template('edit.html',params=params,sno=sno,post=post)
            


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() 

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
            return "Uploaded Successfully"  
    











app.run(debug=True)