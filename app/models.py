from app.__init__ import mysql


class User:
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash']
        )

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users')
        data = cur.fetchall()
        users = [User.from_dict(row) for row in data]
        cur.close()
        return users

    @staticmethod
    def get_by_id(id):
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE id = %s', (id,))
        data = cur.fetchone()
        user = User.from_dict(data)
        cur.close()
        return user

    def save(self):
        cur = mysql.connection.cursor()
        if self.id:
            cur.execute('UPDATE users SET username=%s, email=%s, password_hash=%s WHERE id=%s',
                        (self.username, self.email, self.password_hash, self.id))
        else:
            cur.execute('INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
                        (self.username, self.email, self.password_hash))
            self.id = cur.lastrowid
        mysql.connection.commit()
        cur.close()

    def delete(self):
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM users WHERE id=%s', (self.id,))
        mysql.connection.commit()
        cur.close()


class Post:
    def __init__(self, id, body, timestamp, user_id):
        self.id = id
        self.body = body
        self.timestamp = timestamp
        self.user_id = user_id

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            body=data['body'],
            timestamp=data['timestamp'],
            user_id=data['user_id']
        )

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM posts')
        data = cur.fetchall()
        posts = [Post.from_dict(row) for row in data]
        cur.close()
        return posts

    @staticmethod
    def get_by_id(id):
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM posts WHERE id = %s', (id,))
        data = cur.fetchone()
        post = Post.from_dict(data)
        cur.close()
        return post

    def save(self):
        cur = mysql.connection.cursor()
        if self.id:
            cur.execute('UPDATE posts SET body=%s, timestamp=%s, user_id=%s WHERE id=%s',
                        (self.body, self.timestamp, self.user_id, self.id))
        else:
            cur.execute('INSERT INTO posts (body, timestamp, user_id) VALUES (%s, %s, %s)',
                        (self.body, self.timestamp, self.user_id))
            self.id = cur.lastrowid
        mysql.connection.commit()
        cur.close()

    def delete(self):
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM posts WHERE id=%s', (self.id,))
        mysql.connection.commit()
        cur.close()


class BusDepot():
    # id = mysql.Column(mysql.Integer, primary_key=True)
    # code = mysql.Column(mysql.String(80), unique=True, nullable=False)
    # name = mysql.Column(mysql.String(80), nullable=False)
    # status = mysql.Column(mysql.String(80), nullable=False)
    # address = mysql.Column(mysql.String(120), nullable=False)
    pass


class BusLine():
    pass
    # id = mysql.Column(mysql.Integer, primary_key=True)
    # code = mysql.Column(mysql.String(80), unique=True, nullable=False)
    # name = mysql.Column(mysql.String(80), nullable=False)
    # status = mysql.Column(mysql.String(80), nullable=False)
    # depot_id = mysql.Column(mysql.Integer, mysql.ForeignKey('bus_depot.id'), nullable=False)
    # depot = mysql.relationship('BusDepot', backref=mysql.backref('bus_lines', lazy=True))


class BusStop():
    pass
    # id = mysql.Column(mysql.Integer, primary_key=True)
    # code = mysql.Column(mysql.String(80), unique=True, nullable=False)
    # name = mysql.Column(mysql.String(80), nullable=False)
    # direction = mysql.Column(mysql.String(80), nullable=False)
    # latitude = mysql.Column(mysql.Float, nullable=False)
    # longitude = mysql.Column(mysql.Float, nullable=False)
    # status = mysql.Column(mysql.String(80), nullable=False)
    # line_id = mysql.Column(mysql.Integer, mysql.ForeignKey('bus_line.id'), nullable=False)
    # line = mysql.relationship('BusLine', backref=mysql.backref('bus_stops', lazy=True))


class Post:
    pass
