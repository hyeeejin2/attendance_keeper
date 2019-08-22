from flask import Flask, app, render_template, request, url_for, redirect, session, escape
from datetime import timedelta
import pymysql, json, hashlib, os, binascii

app=Flask(__name__)
app.config['DEBUG']=True
app.config['SECRET_KEY']=binascii.hexlify(os.urandom(24))

@app.before_request
def befor_request():
    session.permanent=True
    app.permanent_session_lifetime=timedelta(minutes=30)

@app.route("/")
@app.route("/<error>")
def main(error=None):
    if 'username' in session:
        user=None
        string="님"
        result='%s' % escape(session['username'])

        db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
        cursor=db.cursor()

        query="SELECT NAME FROM TUTEE_INFO WHERE EMAIL=%s;"
        value=(result)

        cursor.execute(query, value)
        tutee=(cursor.fetchall())

        query="SELECT NAME FROM TUTOR_INFO WHERE EMAIL=%s;"
        value=(result)

        cursor.execute(query, value)
        tutor=(cursor.fetchall())

        if tutee:
            for row in tutee:
                tutee=row[0]

            cursor.close()
            db.close()
            return render_template('index.html', user=tutee, tutee=tutee, string=string, error=error)
        elif tutor:
            for row in tutor:
                tutor=row[0]

            cursor.close()
            db.close()
            return render_template('index.html', user=tutor, tutor=tutor, string=string, error=error)

    else:
        return render_template('index.html', error=error)

@app.route("/login")
@app.route("/login/<error>")
def login(error=None):
    if 'username' in  session:
        return redirect(url_for('main'))
    else:
        return render_template("login.html",error=error)

@app.route("/loginProcess", methods=["POST"])
def loginProcess():
    if request.method=="POST":
        if request.form['email'] == '' or request.form['password'] == '' or request.form.get('user', None) == None:
            error={"error":"빈칸을 채우시오."}
            r=json.dumps(error)
            loaded_r=json.loads(r)
            return redirect(url_for('login', error=loaded_r))
        else:
            salt="AbI!mNsWzo#fK&qP"
            email=request.form["email"]
            pw=request.form["password"]
            encode_pw=pw.encode()
            encode_salt=salt.encode()
            hash_pw=hashlib.pbkdf2_hmac('sha256',password=encode_pw, salt=encode_salt, iterations=1)
            hash_pw=binascii.hexlify(hash_pw)
            user=request.form['user']

            if user=='tutee':
                db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
                cursor=db.cursor()

                query="SELECT NAME FROM TUTEE_INFO WHERE EMAIL=%s AND PASSWORD =%s;"
                value=(email, hash_pw)

                cursor.execute(query, value)
                data=(cursor.fetchall())
            
                cursor.close()
                db.close()

                for row in data:
                    data=row[0]
                
                if data:
                    session['username']=request.form['email']
                    return redirect(url_for('sessionCheck'))
                else:
                    error={"error":"이메일 또는 비밀번호를 잘못 입력하셨습니다."}
                    r = json.dumps(error)
                    loaded_r = json.loads(r)
                    return redirect(url_for('login',error=loaded_r))
            elif user=='tutor':
                db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
                cursor=db.cursor()
                    
                query="SELECT NAME FROM TUTOR_INFO WHERE EMAIL=%s AND PASSWORD =%s;"
                value=(email, hash_pw)
                    
                cursor.execute(query, value)
                data=(cursor.fetchall())
                    
                cursor.close()
                db.close()
                    
                for row in data:
                    data=row[0]
                if data:
                    session['username']=request.form['email']
                    return redirect(url_for('sessionCheck'))
                else:
                    error={"error":"이메일 또는 비밀번호를 잘못 입력하셨습니다."}
                    r = json.dumps(error)
                    loaded_r = json.loads(r)
                    return redirect(url_for('login',error=loaded_r))

@app.route("/sessionCheck")
def sessionCheck():
    if 'username' in session:
        error={'error':"로그인 성공!"}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=error))
    else:
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    if 'username' in session:
        session.pop('username', None)
        error={'error':"로그아웃 성공!"}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))
    else:
        error={'error':"이미 로그아웃 되었습니다."}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))

@app.route("/tuteeSignup")
@app.route("/tuteeSignup/<error>")
def tuteeSignup(error=None):
    return render_template("tutee_register.html",error=error)

@app.route("/tuteeSignupProcess",methods=["POST"])
def tuteeSignupProcess():
    if request.method=="POST":
        if request.form['email'] == '' or request.form['password'] == '' or request.form['name'] == '' or request.form['mac_address'] == '' or request.form['repeat_password'] == '':
            error={"error":"빈칸을 채우시오!"}
            r=json.dumps(error)
            loaded_r=json.loads(r)
            return redirect(url_for('tuteeSignup', error=loaded_r))
        else:
            salt="AbI!mNsWzo#fK&qP"
            email=request.form["email"]
            pw=request.form["password"]
            name=request.form["name"]
            mac_address=request.form["mac_address"]
            repeat_pw=request.form["repeat_password"]
            encode_pw=pw.encode()
            encode_salt=salt.encode()
            hash_pw=hashlib.pbkdf2_hmac('sha256',password=encode_pw, salt=encode_salt, iterations=1)
            hash_pw=binascii.hexlify(hash_pw)
            encode_mac=mac_address.encode()
            hash_mac=hashlib.pbkdf2_hmac('sha256', password=encode_mac, salt=encode_salt, iterations=1)
            hash_mac=binascii.hexlify(hash_mac)

            if pw==repeat_pw and len(pw)>10 and len(repeat_pw)>10:
                db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
                cursor=db.cursor()

                query = "SELECT NAME FROM TUTEE_INFO WHERE EMAIL=%s;"
                value=(email)

                cursor.execute(query,value)
                data=(cursor.fetchall())
        
                query="SELECT NAME FROM TUTOR_INFO WHERE EMAIL=%s;"
                value=(email)

                cursor.execute(query,value)
                exsit=(cursor.fetchall())

                if exsit:
                    cursor.close()
                    db.close()
                    error={'error':'이미 이메일이 존재합니다.'}
                    r=json.dumps(error)
                    loaded_r=json.loads(r)
                    return redirect(url_for('tuteeSignup', error=loaded_r))

                else:
                    for row in data:
                        data=row[0]

                    if data:
                        cursor.close()
                        db.close()
                        error={'error':'이미 이메일이 존재합니다.'}
                        r=json.dumps(error)
                        loaded_r=json.loads(r)
                        return redirect(url_for('tuteeSignup',error=loaded_r))
        
                    else:
                        query="SELECT auto_increment FROM information_schema.tables WHERE table_name = 'TUTEE_INFO';"
                        cursor.execute(query)
                        num=(cursor.fetchall())

                        for row in num:
                            num=row[0]

                        query="INSERT INTO TUTEE_INFO VALUES(%s, %s, %s, %s, %s)"
                        value=(int(num), email, hash_pw, name, hash_mac)
    
                        cursor.execute(query, value)
                        data=(cursor.fetchall())

                        query="set @cnt=0;"
                        cursor.execute(query)
    
                        query="update TUTEE_INFO set TUTEE_INFO.TUTEE_ID=@cnt:=@cnt+1;"
                        cursor.execute(query)

                        if not data:
                            db.commit()
                            cursor.close()
                            db.close()
                            error={'error':'회원가입 성공!'}
                            r=json.dumps(error)
                            loaded_r=json.loads(r)
                            return redirect(url_for('login', error=error))
                        else:
                            db.rollback()
                            cursor.close()
                            db.close()
                            error={'error':'회원가입 실패!'}
                            r=json .dumps(error)
                            loaded_r=json.loads(r)
                            return redirect(url_for('tuteeSignup',error=loaded_r))
            else:
                error={'error':'비밀번호를 확인하시오.'}
                r=json.dumps(error)
                loaded_r=json.loads(r)
                return redirect(url_for('tuteeSignup', error=loaded_r))

@app.route("/tutorSignup")
@app.route("/tutorSignup/<error>")
def tutorSignup(error=None):
    return render_template('tutor_register.html', error=error)

@app.route("/tutorSignupProcess", methods=['POST'])
def tutorSignupProcess():
    if request.method=="POST":
        if request.form['email'] == '' or request.form['password'] == '' or request.form['name'] == '' or request.form['repeat_password'] == '':
            error={"error":"빈칸을 채우시오."}
            r=json.dumps(error)
            loaded_r=json.loads(r)
            return redirect(url_for('tutorSignup', error=loaded_r))
        else:
            salt="AbI!mNsWzo#fK&qP"
            email=request.form["email"]
            pw=request.form["password"]
            name=request.form["name"]
            repeat_pw=request.form["repeat_password"]
            encode_pw=pw.encode()
            encode_salt=salt.encode()
            hash_pw=hashlib.pbkdf2_hmac('sha256',password=encode_pw, salt=encode_salt, iterations=1)
            hash_pw=binascii.hexlify(hash_pw)

            if pw==repeat_pw and len(pw)>10:
                db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
                cursor=db.cursor()
    
                query = "SELECT NAME FROM TUTOR_INFO WHERE EMAIL=%s;"
                value=(email)

                cursor.execute(query,value)
                data=(cursor.fetchall())

                query="SELECT NAME FROM TUTEE_INFO WHERE EMAIL=%s;"
                value=(email)

                cursor.execute(query,value)
                exsit=(cursor.fetchall())

                if exsit:
                    cursor.close()
                    db.close()
                    error={'error':'이미 이메일이 존재합니다.'}
                    r=json.dumps(error)
                    loaded_r=json.loads(r)
                    return redirect(url_for('tutorSignup', error=loaded_r))

                else:
                    for row in data:
                        data=row[0]

                    if data:
                        cursor.close()
                        db.close()
                        error={'error':'이미 이메일이 존재합니다.'}
                        r=json.dumps(error)
                        loaded_r=json.loads(r)
                        return redirect(url_for('tutorSignup',error=loaded_r))

                    else:
                        query="SELECT auto_increment FROM information_schema.tables WHERE table_name = 'TUTOR_INFO';"
                        cursor.execute(query)
                        num=(cursor.fetchall())

                        for row in num:
                            num=row[0]

                        query="INSERT INTO TUTOR_INFO VALUES(%s, %s, %s, %s)"
                        value=(int(num), email, hash_pw, name)

                        cursor.execute(query, value)
                        data=(cursor.fetchall())
    
                        query="set @cnt=0;"
                        cursor.execute(query)

                        query="update TUTOR_INFO set TUTOR_INFO.TUTOR_ID=@cnt:=@cnt+1;"
                        cursor.execute(query)

                        if not data:
                            db.commit()
                            cursor.close()
                            db.close()
                            error={'error':'회원가입 성공!'}
                            r=json.dumps(error)
                            loaded_r=json.loads(r)
                            return redirect(url_for('login', error=error))
                        else:
                            db.rollback()
                            cursor.close()
                            db.close()
                            error={'error':'회원가입 실패!'}
                            r=json.dumps(error)
                            loaded_r=json.loads(r)
                            return redirect(url_for('tutorSignup',error=loaded_r))
            else:
                error={'error':'비밀번호를 확인하시오.'}
                r=json.dumps(error)
                loaded_r=json.loads(r)
                return redirect(url_for('tuteeSignup', error=loaded_r))

@app.route("/setLecture")
@app.route("/setLecture/<error>")
def setLecture(error=None):
    if 'username' in session:
        result='%s' % escape(session['username'])

        db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
        cursor=db.cursor()

        query="SELECT NAME FROM TUTOR_INFO WHERE EMAIL=%s;"
        value=(result)

        cursor.execute(query, value)
        data=(cursor.fetchall())

        for row in data:
            data=row[0]

        cursor.close()
        db.close()

        if data:
            return render_template('create_class.html', tutor_name=data, error=error)

        else:
            error={'error':'접근 권한이 없습니다.'}
            r=json.dumps(error)
            loaded_r=json.loads(r)
            return redirect(url_for('main', error=loaded_r))
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r)) 

@app.route("/setLectureProcess", methods=['POST'])
def setLectureProcess():
    if 'username' in session:
        if request.method=='POST':
            if request.form['class_name'] == '' or request.form['tutor_name'] == '' or request.form['class_date'] == '' or request.form['class_time'] == '' or request.form['class_room'] == '' or request.form['class_describe'] == '' or request.form['limit_entry'] == '' or request.form['limit_late'] == '' or request.form['limit_fail'] == '':
                error={"error":"빈칸을 채우시오."}
                r=json.dumps(error)
                loaded_r=json.loads(r)
                return redirect(url_for('setLecture', error=loaded_r))
            else:
                name=request.form['class_name']
                tutor_name=request.form['tutor_name']
                date=request.form['class_date']
                time=request.form['class_time']
                room=request.form['class_room']
                describe=request.form['class_describe']
                entry=request.form['limit_entry']
                LATE=request.form['limit_late']
                FAIL=request.form['limit_fail']

                db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
                cursor=db.cursor()

                query="SELECT auto_increment FROM information_schema.tables WHERE table_name = 'CLASS_INFO';"
                cursor.execute(query)
                num=(cursor.fetchall())
            
                query="SELECT TUTOR_ID FROM TUTOR_INFO WHERE NAME=%s;"
                value=(tutor_name)

                cursor.execute(query, value)
                tutor_id=(cursor.fetchall())
        
                for row in tutor_id:
                    tutor_id=row[0]
                
                query="INSERT INTO CLASS_INFO VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                value=(num, name, tutor_id, date, time, room, describe, entry, LATE, FAIL)
        
                cursor.execute(query, value)
                data=(cursor.fetchall())

                query="set @cnt=0;"
                cursor.execute(query)
    
                query="update CLASS_INFO set CLASS_INFO.CLASS_ID=@cnt:=@cnt+1;"
                cursor.execute(query)
    
                if not data:
                    db.commit()
                    cursor.close()
                    db.close()
                    error={'error':'강의 설립에 성공했습니다.'}
                    r=json.dumps(error)
                    loaded_r=json.loads(r)
                    return redirect(url_for('tutorMypage', error=loaded_r))
                else:
                    db.rollback()
                    cursor.close()
                    db.close()
                    error={'error':'강의 설립에 실패했습니다.'}
                    r=json.dumps(error)
                    loaded_r=json.loads(r)
                    return redirect(url_for('setLecture', error=loaded_r))
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))

@app.route("/lectureList")
@app.route("/lectureList/<error>")
def lectureList(error=None):
    if 'username' in session:
        user=None
        string="님"
        result='%s' % escape(session['username'])

        db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
        cursor=db.cursor()

        query="SELECT NAME FROM TUTEE_INFO WHERE EMAIL=%s;"
        value=(result)

        cursor.execute(query, value)
        tutee=(cursor.fetchall())

        query="SELECT NAME FROM TUTOR_INFO WHERE EMAIL=%s;"
        value=(result)

        cursor.execute(query, value)
        tutor=(cursor.fetchall())

        if tutee:
            for row in tutee:
                tutee=row[0]

            cursor.close()
            db.close()
            return render_template('select_class.html', user=tutee, tutee=tutee, string=string, error=error)
        elif tutor:
            for row in tutor:
                tutor=row[0]

            cursor.close()
            db.close()
            return render_template('select_class.html', user=tutor, tutor=tutor, string=string, error=error)
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))

@app.route("/lectureListProcess", methods=['GET'])
def lectureListProcess():
    if 'username' in session:
        if request.method=='GET':
            db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
            cursor=db.cursor()

            query="SELECT count(*) FROM CLASS_INFO;"
            cursor.execute(query)
            total=(cursor.fetchall())

            for row in total:
                total=row[0]

            query="SELECT CLASS_ID, CLASS_NAME, NAME, CLASS_DATE, CLASS_TIME, CLASS_ROOM FROM CLASS_INFO, TUTOR_INFO WHERE CLASS_INFO.TUTOR_ID=TUTOR_INFO.TUTOR_ID;"
            cursor.execute(query)
            data=(cursor.fetchall())

            cursor.close()
            db.close()

            datalist=[]
            for row in data:
                dic={'class_id':row[0],'class_name':row[1], 'tutor_id':row[2], 'class_date': row[3], 'class_time': row[4], 'class_room':row[5]}
                datalist.append(dic)

            json_datalist={'data': datalist}
            r=json.dumps(json_datalist)
            loaded_r=json.loads(r)
            return loaded_r
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))

@app.route("/selectLecture", methods=['GET'])
def selectLecture():
    if 'username' in session:
        if request.method=='GET':
            class_id=request.args.get('class_id')

            db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
            cursor=db.cursor()

            query="SELECT CLASS_ID, CLASS_NAME, NAME, CLASS_DATE, CLASS_TIME, CLASS_ROOM, CLASS_DESCRIBE, LIMIT_ENTRY, LIMIT_LATE, LIMIT_FAIL FROM CLASS_INFO, TUTOR_INFO WHERE CLASS_INFO.CLASS_ID=%s AND CLASS_INFO.TUTOR_ID=TUTOR_INFO.TUTOR_ID;"
            value=(class_id)

            cursor.execute(query, value)
            data=(cursor.fetchall())

            cursor.close()
            db.close()

            if data:
                datalist=[]
                for row in data:
                    dic={'class_id':row[0],'class_name':row[1],'tutor_id':row[2],'class_date':row[3], 'class_time':row[4], 'class_room':row[5], 'class_describe':row[6], 'limit_entry':row[7],'limit_late':row[8], 'limit_fail':row[9]}
                    datalist.append(dic)

                json_datalist={'data': datalist}
                r=json.dumps(json_datalist)
                loaded_r=json.loads(r)
                return loaded_r
            else:
                error={'error':'정보가 없습니다.'}
                r=json.dumps(error)
                loaded_r=json.loads(r)
                return redirect(url_for('lectureList', error=loaded_r))
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))

@app.route("/requestLecture", methods=['POST'])
def requestLecture():
    if 'username' in session:
        if request.method=='POST':
            result='%s' % escape(session['username'])

            db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
            cursor=db.cursor()

            query="SELECT TUTEE_ID FROM TUTEE_INFO WHERE EMAIL=%s;"
            value=(result)

            cursor.execute(query, value)
            tutee_check=(cursor.fetchall())

            for row in tutee_check:
                tutee_check=row[0]

            if tutee_check:
                class_id=request.form['class_id']
                query="SELECT count(*) FROM TUTEE_CLASS_MAPPING WHERE CLASS_ID=%s;"
                value=(class_id)

                cursor.execute(query, value)
                class_count=(cursor.fetchall())

                query="SELECT LIMIT_ENTRY FROM CLASS_INFO WHERE CLASS_ID=%s;"
                value=(class_id)

                cursor.execute(query, value)
                limit_count=(cursor.fetchall())

                query="SELECT MAPPING_ID FROM TUTEE_CLASS_MAPPING WHERE CLASS_ID=%s AND TUTEE_ID=%s"
                value=(class_id, tutee_check)

                cursor.execute(query, value)
                lecture_check=(cursor.fetchall())

                if lecture_check:
                    cursor.close()
                    db.close()
                    error={'error':'이미 강의를 신청했습니다.'}
                    r=json.dumps(error)
                    loaded_r=json.loads(r)
                    return redirect(url_for('lectureList', error=loaded_r))
                else:
                    if class_count<limit_count:
                        query="SELECT auto_increment FROM information_schema.tables WHERE table_name = 'TUTEE_CLASS_MAPPING';"
                
                        cursor.execute(query)
                        num=(cursor.fetchall())

                        for row in num:
                            num=row[0]

                        query="INSERT INTO TUTEE_CLASS_MAPPING VALUES(%s, %s, %s);"
                        value=(num, tutee_check, class_id)

                        cursor.execute(query, value)
                        data=(cursor.fetchall())
    
                        query="set @cnt=0;"
                        cursor.execute(query)

                        query="update TUTEE_CLASS_MAPPING set TUTEE_CLASS_MAPPING.MAPPING_ID=@cnt:=@cnt+1;"
                        cursor.execute(query)

                        if not data:
                            db.commit()
                            cursor.close()
                            db.close()
                            error={'error':'강의 신청에 성공했습니다.'}
                            r=json.dumps(error)
                            loaded_r=json.loads(r)
                            return redirect(url_for('lectureList', error=loaded_r))
                        else:
                            db.rollback()
                            cursor.close()
                            db.close()
                            error={'error':'강의 신청에 실패했습니다.'}
                            r=json.dumps(error)
                            loaded_r=json.loads(r)
                            return redirect(url_for('lectureLst', error=loaded_r)) 

                    else:
                        cursor.close()
                        db.close()
                        error={'error':'수강 인원을 초과했습니다.'}
                        r=json.dumps(error)
                        loaded_r=json.loads(r)
                        return redirect(url_for('lectureList', error=loaded_r))

            else:
                cursor.close()
                db.close()
                error={'error':'접근 권한이 없습니다.'}
                r=json.dumps(error)
                loaded_r=json.loads(r)
                return redirect(url_for('main', error=loaded_r))
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))

@app.route("/tuteeMypage")
def tuteeMypage():
    if 'username' in session:
        result='%s' %escape(session['username'])

        db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
        cursor=db.cursor()

        query="SELECT NAME FROM TUTEE_INFO WHERE EMAIL=%s;"
        value=(result)

        cursor.execute(query, value)
        tutee_check=(cursor.fetchall())

        cursor.close()
        db.close()

        for row in tutee_check:
            tutee_check=row[0]

        if tutee_check:
            return render_template('tutee_mypage.html', tutee=tutee_check)
        else:
            error={'error':'접근 권한이 없습니다.'}
            r=json.dumps(error)
            loaded_r=json.loads(r)
            return redirect(url_for('main', error=loaded_r))
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))

@app.route("/tuteeLectureList", methods=['POST'])
def tuteeLectureList():
    if 'username' in session:
        result='%s' %escape(session['username'])

        db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
        cursor=db.cursor()

        query="SELECT TUTEE_ID FROM TUTEE_INFO WHERE EMAIL=%s;"
        value=(result)

        cursor.execute(query, value)
        tutee_id=(cursor.fetchall())

        for row in tutee_id:
            tutee_id=row[0]

        query="SELECT CLASS_INFO.CLASS_ID, CLASS_NAME FROM CLASS_INFO, TUTEE_CLASS_MAPPING WHERE TUTEE_CLASS_MAPPING.TUTEE_ID=%s AND TUTEE_CLASS_MAPPING.CLASS_ID=CLASS_INFO.CLASS_ID;"
        value=(tutee_id)

        cursor.execute(query, value)
        lecture=(cursor.fetchall())

        cursor.close()
        db.close()

        lecturelist=[]
        for row in lecture:
            dic={'class_id':row[0], 'class_name':row[1]}
            lecturelist.append(dic)

        json_lecturelist={'data':lecturelist}
        r=json.dumps(json_lecturelist)
        loaded_r=json.loads(r)
        return loaded_r
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))

@app.route("/tuteeLectureAttendance", methods=['POST'])
def tuteeLectureAttendance():
    if 'username' in session:
        class_id=request.form['class_id']
        result='%s' %escape(session['username'])

        db = pymysql.connect(host='127.0.0.1', port=3306, user='attendance', password='keeper1418!@#', db='attendance_keeper', charset='utf8')
        cursor=db.cursor()

        query="SELECT TUTEE_ID FROM WHERE EMAIL=%s;"
        value=(result)

        cursor.execute(query, value)
        tutee_id=(cursor.fetchall())

        query="SELECT MAPPING_ID FROM TUTEE_CLASS_MAPPING WHERE CLASS_ID=%s AND TUTEE_ID=%s;"
        value=(class_id, tutee_id)

        cursor.execute(query, value)
        mapping_id=(cursor.fetchall())

        query="SELECT DATE, CLASS_TIME, STATUS, ENGAGEMENT FROM ATTENDANCE, CLASS_INFO WHERE ATTENDANCE.MAPPING_ID=5 AND CLASS_INFO.CLASS_ID=2;"
        value=(mapping_id, class_id)

        cursor.execute(query)
        attendance=(cursor.fetchall())

        cursor.close()
        db.close()

        attendancelist=[]
        for row in attendance:
            dic={'date':row[0], 'class_time':row[1], 'status':row[2], 'engagement':row[3]}
            attendancelist.append(dic)

        json_list={'data':attendancelist}

        r=json.dumps(json_list)
        loaded_r=json.loads(r)
        return loaded_r
    else:
        error={'error':'접근 권한이 없습니다.'}
        r=json.dumps(error)
        loaded_r=json.loads(r)
        return redirect(url_for('main', error=loaded_r))
