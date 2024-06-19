import os
import os
import re
from time import sleep

import bcrypt
import chardet
import pandas as pd
from flask import Blueprint, jsonify, send_file, abort, current_app
from flask import render_template, request, redirect, url_for, flash, session

from app.db import mysql
from app.utils import get_random_color

bp = Blueprint('route', __name__)


# 错误处理
@bp.app_errorhandler(Exception)
def handle_error(e):
    print(session)
    print(e)
    if '用户名' not in session:
        return render_template('index.html')
    return render_template('error.html', error=e)


@bp.route('/')
def home():
    if session.get('用户名'):  # 自动登录功能的实现
        return redirect(url_for('route.index'))
    return render_template('index.html')


def print_status_code(response):
    print(request.path, "状态码：", response.status_code)
    return response


bp.after_request(print_status_code)


# 用户管理模块
@bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])
        email = str(request.form['email'])
        con_pwd = str(request.form['confirm_password'])
        if password != con_pwd:
            flash('两次密码不一致', 'error')
            return render_template('register.html')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM 用户 WHERE 用户名 = %s', (username,))
        row = cursor.fetchone()
        print(row)
        if row:
            abort(400, '用户名已存在')
        cursor.execute('INSERT INTO 用户 (用户名, 密码,邮箱) VALUES (%s, %s,%s)', (username, hashed_password, email))
        mysql.connection.commit()
        cur = cursor.execute('SELECT 编号 FROM 用户 WHERE 用户名 = %s', (username,))
        print(cur)
        flash('注册成功', 'success')
        sleep(3)
        session['用户名'] = username
        session['编号'] = cur
        cursor.close()
        return redirect(url_for('route.home'))
    return render_template('register.html')


@bp.route('/index')
def index():
    username = session['用户名']
    cur = mysql.connection.cursor()
    # 加载用户
    cur.execute("SELECT 用户名, 密码,邮箱,状态,编号 FROM 用户")
    users = [dict(name=row[0], password=row[1], email=row[2], state=row[3], id=row[4]) for row in cur.fetchall()]
    # 加载线路
    cur.execute("SELECT 编号, 名称,所属车场号,状态,包含站点编号,上下行 FROM 线路")
    rows = cur
    lines = []
    for row in rows:
        ids = row[4].split(',')
        names = []
        for id1 in ids:
            scur = mysql.connection.cursor()
            scur.execute("SELECT 名称 FROM 站点 WHERE 编号 = %s", (id1,))
            name = scur.fetchone()[0]
            names.append(name)
        rows = ','.join(names)
        row = list(row)
        row[4] = rows
        lines.append(dict(id=row[0], name=row[1], home=row[2], statue=row[3], stop=row[4], towards=row[5]))# []
    print(lines)
    # 加载车场
    cur.execute("SELECT 编号, 名称,地址,状态 FROM 车场")
    bhs = [dict(id=row[0], name=row[1], ads=row[2], statue=row[3]) for row in cur.fetchall()]
    # 加载车站
    cur.execute("SELECT 编号, 名称,经度,纬度,状态 FROM 站点")
    stops = [dict(id=row[0], name=row[1], location1=row[2], location2=row[3], status=row[4]) for row in cur.fetchall()]
    # 加载统计

    # 查询车场表，获取车场号和车场名称
    cur.execute("SELECT 编号, 名称 FROM 车场")
    carparks = cur.fetchall()

    result = []

    # 对每个车场，线路表，统计线路数量，查询站点表，统计站点数量
    for carpark in carparks:
        carpark_id, carpark_name = carpark

        # 统计线路数量
        cur.execute(f"SELECT COUNT(*) FROM 线路 WHERE 所属车场号 ={carpark_id}")
        line_count = cur.fetchone()[0]

        # 统计站点数量
        cur.execute(f"SELECT 包含站点编号 FROM 线路 WHERE 所属车场号 = {carpark_id}")
        station_ids = cur.fetchall()
        unique_station_ids = set()
        for station_id_str in station_ids:
            unique_station_ids.update(station_id_str[0].split(','))

        station_count = len(unique_station_ids)

        # 将结果组合成元组
        result.append((carpark_id, carpark_name, line_count, station_count))

    # 输出结果
    for item in result:
        print(item)
    su = [dict(id=row[0], name=row[1], sum1=row[2], sum2=row[3]) for row in result]
    print(su)
    return render_template("mag.html", username=username, users=users, roue=lines, stations=stops, bhs=bhs,
                           routes=lines, sus=su)


# 添加用户
@bp.route('/add_user', methods=['POST', 'GET'])
def add_user():
    cursor = mysql.connection.cursor()
    username = request.form['name']
    cursor.execute('SELECT * FROM 用户 WHERE 用户名 = %s', (username,))
    row = cursor.fetchone()
    if row:
        abort(400, '用户名已存在')
    password = request.form['password']
    email = request.form['email']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO 用户 (用户名, 密码,邮箱) VALUES (%s, %s,%s)', (username, hashed_password, email))
    mysql.connection.commit()
    cursor.close()
    flash('注册成功', 'success')
    return redirect(url_for('route.index'))


# 登录
@bp.route('/login', methods=['POST', 'GET'])
def login():
    username = (request.form['username'])
    password = (request.form['password'])
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM 用户 WHERE 用户名 = %s', (username,))
    user = cursor.fetchone()
    print(user)
    cursor.close()
    if user is not None and bcrypt.checkpw(password.encode('utf-8'), (user[1]).encode('utf-8')) and user[3] == '启用':
        session['user_id'] = user[2]
        print(user[0])
        session['用户名'] = user[0]
        return redirect(url_for('route.index'))
    else:
        flash('用户名或密码错误', 'error')
        return redirect(url_for('route.home'))


# 用户信息删除
@bp.route('/profile_del', methods=['POST'])
def profile_del():
    user_name = request.form.get('user_name')
    if user_name:
        # 从数据库中删除指定ID的用户数据
        if user_name == session.get('用户名'):
            return jsonify({'status': 'error', 'message': '不能删除当前用户'})
        else:
            cursor = mysql.connection.cursor()
            cursor.execute('DELETE  FROM 用户 WHERE 用户名 = %s', (user_name,))
            mysql.connection.commit()
            cursor.close()
        # 返回一个响应告诉前端删除操作已经完成
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': '不存在该用户'})


# 用户信息编辑
@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    idd = request.form['id']
    name = request.form['name']
    password = request.form['password']
    email = request.form['email']
    state = request.form['state']
    print(idd, name, password, email, state)
    cur = mysql.connection.cursor()
    cur.execute('SELECT 用户名 FROM 用户 WHERE 编号 =%s', (idd,))
    row = cur.fetchone()
    if row is not None and session.get('用户名') == row[0]:
        return jsonify({'status': 'error', 'message': '不能编辑当前用户'})
    cur.execute('SELECT * FROM 用户 WHERE 用户名 = %s AND 编号 !=%s', (name, idd,))
    row = cur.fetchone()
    print(row)
    if row:
        # abort(400, '用户名已存在')
        return jsonify({'result': 'error', 'message': '用户名已存在'})
    print("用户名不存在")
    try:
        hashed_password = password
        cur.execute('SELECT 密码 FROM 用户 WHERE 编号 =%s', (idd,))
        row = cur.fetchone()
        if password != row[0]:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute('UPDATE 用户 SET 用户名=%s, 密码=%s, 邮箱=%s, 状态=%s WHERE 编号=%s',
                    (name, hashed_password, email, state, idd,))
        mysql.connection.commit()
        print("更新完成")
    except Exception as e:
        print("更新数据失败：", e)
        return jsonify({'result': 'error', 'message': '更新失败'})
    finally:
        cur.execute('SELECT * FROM 用户 WHERE 编号 = %s', (idd,))
        row = cur.fetchone()
        print(row)
        cur.close()
        return jsonify({'result': 'success'})


# 添加车场
@bp.route('/add_bush', methods=['GET', 'POST'])
def add_bush():
    cursor = mysql.connection.cursor()
    name = request.form['name']
    ads = request.form['ads']
    cursor.execute('SELECT * FROM 车场 WHERE 名称 = %s', (name,))
    row = cursor.fetchone()
    if row is not None:
        abort(400, '该车场已存在！')
    cursor.execute('SELECT * FROM 车场 WHERE 地址 = %s', (ads,))
    row = cursor.fetchone()
    if row is not None:
        abort(400, '该地已存在车场！')
    st = request.form['status']

    cursor.execute('INSERT INTO 车场 (名称,地址,状态) VALUES (%s, %s,%s)',
                   (name, ads, st,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('route.index'))


# 线路编辑
@bp.route('/edit_rt', methods=['POST'])
def edit_rt():
    print(request)
    print(request.form)
    idd = request.form['id']
    name = request.form['name']
    home = request.form['home']
    shops = request.form['shops']
    pattern = r'^\d+(,\d+)*$'  # 匹配数字和逗号组成的字符串，其中逗号可以重复出现
    up = 0
    if re.match(pattern, shops):
        up = 1
    state = request.form['state']
    ts = request.form['ts']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM 车场 WHERE 编号=%s', (home,))
    row = cur.fetchone()
    if row is None:
        print(row)
        abort(400, '该车场不存在！')
    cur.execute('SELECT * FROM 线路 WHERE 上下行 = %s AND 包含站点编号=%s', (ts, shops,))
    row = cur.fetchone()
    if row is not None:
        print(row)
        abort(400, '该方向线路已经存在！')
    print(row)
    try:
        cur.execute('UPDATE 线路 SET 名称=%s, 所属车场号=%s,状态=%s,上下行=%s WHERE 编号=%s',
                    (name, home, state, ts, idd,))
        if up == 1:
            cur.execute('UPDATE 线路 SET 包含站点编号=%s WHERE 编号=%s',
                        (shops, idd,))
        mysql.connection.commit()
        print("更新完成")
    except Exception as e:
        print("更新数据失败：", e)
        return jsonify({'result': 'error', 'message': '更新失败'})
    finally:
        # cur.execute('SELECT * FROM 站点 WHERE 编号 = %s', (idd,))
        # row = cur.fetchone()
        # print(row)
        cur.close()
        return jsonify({'result': 'success'})


# 线路删除
@bp.route('/delete_rt', methods=['POST'])
def delete_rt():
    idd = request.form.get('rt_id')
    if idd:
        print("idd == ", idd)
        # 从数据库中删除指定ID的用户数据
        cursor = mysql.connection.cursor()
        # 删除该线路
        cursor.execute('DELETE FROM 线路 WHERE 编号 = %s', (idd,))
        mysql.connection.commit()
        cursor.close()
        # 返回一个响应告诉前端删除操作已经完成
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': '不存在该公交车场'})


# 删除公交车场功能
@bp.route('/delete_bh', methods=['POST'])
def delete_bh():
    idd = request.form.get('bh_id')
    if idd:
        print("idd == ", idd)
        # 从数据库中删除指定ID的用户数据
        cursor = mysql.connection.cursor()
        # 删除该车场下的线路
        cursor.execute('DELETE FROM 线路 WHERE 所属车场号 = %s', (idd,))
        mysql.connection.commit()
        # 删除该车场
        cursor.execute('DELETE  FROM 车场 WHERE 编号 = %s', (idd,))
        mysql.connection.commit()
        cursor.close()
        # 返回一个响应告诉前端删除操作已经完成
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': '不存在该公交车场'})


# 添加线路功能
@bp.route('/add_route', methods=['GET', 'POST'])
def add_route():
    cursor = mysql.connection.cursor()
    name = request.form['name']
    homenum = request.form['homenum']
    cursor.execute('SELECT * FROM 车场 WHERE 编号 = %s', (homenum,))
    row = cursor.fetchone()
    if row is None:
        abort(400, '没有该车场！')
    stops = request.form['stops']
    st = request.form['status']
    ts = request.form['towards']
    cursor.execute('SELECT * FROM 线路 WHERE 上下行 = %s AND 包含站点编号=%s', (ts, stops,))
    row = cursor.fetchone()
    if row is not None:
        print(row)
        abort(400, '该方向线路已经存在！')
    cursor.execute('INSERT INTO 线路 (名称,所属车场号,包含站点编号,状态,上下行) VALUES (%s, %s,%s,%s,%s)',
                   (name, homenum, stops, st, ts,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('route.index'))


# 车场修改功能
@bp.route('/edit_bh', methods=['POST'])
def edit_bh():
    print(request)
    print(request.form)
    idd = request.form['id']
    name = request.form['name']
    ads = request.form['ads']
    state = request.form['state']
    print(idd, name, ads, state)
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM 车场 WHERE 地址=%s AND 编号!=%s ', (ads, idd,))
    row = cur.fetchone()
    if row is not None:
        return jsonify({'status': 'error', 'message': '当前位置已经存在车场'})
    print(row)
    try:
        cur.execute('UPDATE 车场 SET 名称=%s, 地址=%s, 状态=%s WHERE 编号=%s',
                    (name, ads, state, idd,))
        mysql.connection.commit()
        print("更新完成")
    except Exception as e:
        print("更新数据失败：", e)
        return jsonify({'result': 'error', 'message': '更新失败'})
    finally:
        # cur.execute('SELECT * FROM 站点 WHERE 编号 = %s', (idd,))
        # row = cur.fetchone()
        # print(row)
        cur.close()
        return jsonify({'result': 'success'})


# 添加公交车站
@bp.route('/add_bus_station', methods=['GET', 'POST'])
def add_station():
    cursor = mysql.connection.cursor()
    name = request.form['name']
    l1 = request.form['location1']
    l2 = request.form['location2']
    st = request.form['status']
    cursor.execute('SELECT * FROM 站点 WHERE 经度 = %s AND 纬度=%s', (l1, l2,))
    row = cursor.fetchone()
    if row:
        abort(400, '该位置已存在公交站！')
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO 站点 (名称,经度,纬度,状态) VALUES (%s, %s,%s,%s)', (name, l1, l2, st))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('route.index'))


# 公交站编辑，经纬度相同的地方只有一个站点
@bp.route('/edit_bus_stop', methods=['GET', 'POST'])
def edit_bus_stop():
    print(request)
    print(request.form)
    idd = request.form['id']
    name = request.form['name']
    l1 = request.form['l1']
    l2 = request.form['l2']
    state = request.form['state']
    print(idd, name, l1, l2, state)
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM 站点 WHERE 经度 =%s AND 纬度=%s AND 编号!=%s ', (l1, l2, idd,))
    row = cur.fetchone()
    if row is not None:
        return jsonify({'status': 'error', 'message': '当前位置已经存在公交站点'})
    print(row)
    try:
        cur.execute('UPDATE 站点 SET 名称=%s, 经度=%s, 纬度=%s, 状态=%s WHERE 编号=%s',
                    (name, l1, l2, state, idd,))
        mysql.connection.commit()
        print("更新完成")
    except Exception as e:
        print("更新数据失败：", e)
        return jsonify({'result': 'error', 'message': '更新失败'})
    finally:
        cur.execute('SELECT * FROM 站点 WHERE 编号 = %s', (idd,))
        row = cur.fetchone()
        print(row)
        cur.close()
        return jsonify({'result': 'success'})


# 删除站点
@bp.route('/delete_bus_stop', methods=['POST'])
def delete_bus_stop():
    idd = request.form.get('station_id')
    print(request.form)
    if idd:
        # 从数据库中删除指定ID的用户数据
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE  FROM 站点 WHERE 编号 = %s', (idd,))
        mysql.connection.commit()
        cursor.close()
        # 返回一个响应告诉前端删除操作已经完成
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': '不存在该公交车站'})




# 导入文件
@bp.route('/importf', methods=['POST'])
def importf():
    file = request.files.get('file')
    table_name = request.form.get('table')
    # 设置数据块大小
    chunksize = 1000
    # 将上传的CSV文件保存到本地文件系统中
    file_path = f"uploads/{file.filename}"
    file.save(file_path)
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        for df in pd.read_csv(file_path, chunksize=chunksize, encoding=encoding):
            # 将数据插入到MySQL表中
            cursor = mysql.connection.cursor()
            for index, row in df.iterrows():
                try:
                    columns = row.index.tolist()
                    values = row.tolist()
                    placeholders = ','.join(['%s'] * len(columns))
                    sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    cursor.execute(sql, values)
                except Exception as e:
                    # 输出错误信息
                    print("循环内部错误:", str(e))
                    continue

    except Exception as e:
        # 输出错误信息
        print("错误:", str(e))
    finally:
        # 删除上传的CSV文件
        os.remove(file_path)
        # 关闭游标
        mysql.connection.commit()
        cursor.close()
        return home()


@bp.route('/backup', methods=['POST', 'GET'])
def backup():
    print(request)
    print(request.form.get('table'))
    table = request.form['table']
    print(table)
    filename = table + '备份.csv'
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM {table}")
    data = cur.fetchall()

    # 将数据转换为DataFrame对象
    df = pd.DataFrame(data, columns=[col[0] for col in cur.description])
    filepath = os.path.join(current_app.root_path, 'static', filename)
    df.to_csv(filepath, index=False, encoding='gbk')
    cur.close()
    # 下载CSV文件
    return send_file(filepath, as_attachment=True)


# 返回给地图各个站点的情况
@bp.route('/get_points')
def get_points():
    cur = mysql.connection.cursor()
    cur.execute("SELECT 经度,纬度,名称,编号 FROM 站点")
    data = [{'longitude': row[0], 'latitude': row[1], 'title': row[2] + ',' + str(row[3])} for row in cur.fetchall()]
    # print(data)
    cur.close()
    return jsonify(data)


@bp.route('/get_lines')
def get_lines():
    cur = mysql.connection.cursor()
    cur.execute("SELECT 名称,包含站点编号 FROM 线路 ")
    rows = cur.fetchall()
    lines = []
    if not rows:
        return jsonify(lines)
    for row in rows:
        ids = row[1].split(',')
        point = []
        for id1 in ids:
            scur = mysql.connection.cursor()
            scur.execute("SELECT 经度,纬度 FROM 站点 WHERE 编号 = %s", (id1,))
            poww = scur.fetchone()
            point.append({'longitude': poww[0], 'latitude': poww[1]})
            # print(point)
        color = get_random_color()
        # print('color==',color)
        lines.append({'points': point, 'color': color, 'name': row[0]})
    # print('line == ',lines)
    return jsonify(lines)


@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('route.home'))




