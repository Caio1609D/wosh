import flask as f
import sqlalchemy as sql
import sqlalchemy.orm as orm
from create_db import engine, User, Clothes, Cart, Orders
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = f.Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

prods = [
    {"name": "Camisetas", "imagelink":"../static/camisetas.png"}, 
    {"name": "Toucas", "imagelink":"../static/Toucas.png"},
    {"name": "Moletons", "imagelink":"../static/Moletons.png"},
    {"name": "Calças", "imagelink":"../static/calcas.png"},
    {"name": "Acessórios", "imagelink":"../static/acessorios.png"},  
    {"name": "Promo", "imagelink":"../static/promocao.png"}, 
    {"name": "Novidades", "imagelink":"../static/novidades.png"}
]

clothes_list = []

with orm.Session(engine) as session:
    stmt = sql.select(Clothes)
    rows = session.scalars(stmt)
    for i in rows:
        clothes_list.append({"id": i.id, "name":i.name, "sizes":i.sizes, "colors":i.colors, "image":i.image, "price":i.price})

for i in clothes_list:
    print(i)

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if f.session.get("user_id") is None:
            return f.redirect("/login")
        return func(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    actual_clothes = [[]]
    count = 0

    for i in clothes_list:
        if len(actual_clothes[count]) > 2:
            actual_clothes.append([])
            count += 1
        actual_clothes[count].append(i)
    
    username = ''

    with orm.Session(engine) as sess:
        stmt = sql.select(User).where(User.id == f.session.get("user_id"))
        print(stmt)
        scalars = sess.scalars(stmt)
        print(scalars)
        for i in scalars:
            username = i.name
            print(username)
            break
        session.commit()

    return f.render_template("index.html", prods=prods, clothes=actual_clothes, username=username)

@app.route("/prod/<id>")
def prod(id):
    with orm.Session(engine) as session:
        stmt = sql.select(Clothes).where(Clothes.id == id)
        clothing = session.scalar(stmt)
        if clothing == None:
            return f.redirect("/prod/1")
    return f.render_template("prod.html", clothing=clothing)

#@app.route("/custom", methods=["POST", "GET"])
#@login_required
#def custom():
#    if f.request.method == "GET":
#        print(f.session.get("user_id"))
#        return f.render_template("custom.html")
#    else:
#        # Here it will handle the POST
#        print(f.request.form)
#        return f.redirect("/")

@app.route("/query", methods=["GET"])
def query():
    like = f"%{f.request.args.get('key')}%"
    if f.request.args.get('key') == '':
        print("No key detected")
        like = "%.%"
    clothings = []
    with orm.Session(engine) as session:
        stmt = sql.select(Clothes).where((Clothes.name.like(like)) | (Clothes.colors.like(like)) | Clothes.keywords.like(like))
        print(stmt)
        scalars = session.scalars(stmt)
        for i in scalars:
            clothings.append(i)
    return f.render_template("search.html", clothings=clothings)

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    print(f.request.method)
    if f.request.method == "GET":
        items = []
        with orm.Session(engine) as session:
            stmt = sql.select(Cart).where(Cart.user_id == f.session.get("user_id"))
            scalars = session.scalars(stmt)
            for i in scalars:
                stmti = sql.select(Clothes).where(Clothes.id == i.clothing_id)
                scalar = session.scalar(stmti)
                items.append({"item": scalar, "order": i})
        return f.render_template("cart.html", items=items)
    else:
        with orm.Session(engine) as session:
            stmt = sql.insert(Cart).values(user_id=f.session.get("user_id"), clothing_id=f.request.form["id"], clothing_size=f.request.form["size"], clothing_color=f.request.form["color"])
            session.execute(stmt)
            session.commit()
        return f.redirect("/cart")      

@app.route("/cart_del", methods=["POST"])
@login_required
def cart_del():
    with orm.Session(engine) as sess:
        stmt = sql.delete(Cart).where(Cart.id == f.request.form["id"] and Cart.user_id == f.session.get("user_id"))
        sess.execute(stmt)
        sess.commit()
    return f.redirect("/cart")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if f.request.method == "POST":
        with orm.Session(engine) as sess:
            stmt = sql.select(Cart).where(Cart.user_id == f.session.get("user_id"))
            scalars = sess.scalars(stmt)
            for i in scalars:
                stmt_select = sql.select(Clothes).where(Clothes.id == i.clothing_id)
                scalar = sess.scalar(stmt_select)
                stmt_ins = sql.insert(Orders).values(user_id=i.user_id, clothing_id=i.clothing_id, user_bank_name=f.request.form["user_bank_name"], adress=f.request.form["adress"],  clothing_size=i.clothing_size, clothing_color=i.clothing_color, value=scalar.price)
                sess.execute(stmt_ins)
                sess.commit()
                stmt_del = sql.delete(Cart).where(Cart.id == i.id)
                sess.execute(stmt_del)
                sess.commit()
            sess.close()
        return f.redirect("/buy")
    if f.request.method == "GET":
        return f.render_template("buy.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if f.request.method == "GET":
        return f.render_template("register.html")
    else:
        data = f.request.form
        
        for key in data:
            if data[key] == '':
                return "Todos os campos tem que ser preenchidos"

        if data["password"] != data["confirm_password"]:
            return "A senha difere da senha esperada"
        
        with orm.Session(engine) as session:
            new_user = User(name=data["name"], e_mail=data["e_mail"], password=generate_password_hash(data["password"]))
            session.add(new_user)
            session.commit()
        
        return f.redirect("/")

        
@app.route("/error")
def error():
    return f.render_template("error.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    f.session.clear()
    
    if f.request.method == "GET":
        return f.render_template("login.html")
    else:
        data = f.request.form

        for key in data:
            if data[key] == '':
                return "Todos os campos tem que ser preenchidos"

        with orm.Session(engine) as session:
            stmt = sql.select(User).where(User.name == data["name"])
            rows = session.scalars(stmt)
            user = None

            for i in rows:
                if i.name == data["name"]:
                    user = i
                    print(user)
                    break

            if user == None:
                return "Nome de Usuário Inexistente"

            if not check_password_hash(user.password, f.request.form.get("password")):
                return "Senha Incorreta, tente novamente"

            f.session["user_id"] = user.id

            return f.redirect("/")

def main():
    app.run()

main()