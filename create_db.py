import sqlalchemy as sql
import sqlalchemy.orm as orm
from re import search
from os import listdir
from json import load

Base = orm.declarative_base()
images = []

for i in listdir("./static"):
    print(i)
    regex = r"Shirt_\d.png(?!:Zone)"
    print(search(regex, i))
    if search(regex, i):
        with open("./static/" + i.split(".")[0] + ".json", "r") as Json:
            current = load(Json)
            print(current)
            current["image"] = "./static/" + i
        images.append(current)
    print()

class User(Base):
    __tablename__ = "user_account"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String, unique=True)
    e_mail = sql.Column(sql.String)
    password = sql.Column(sql.String)
    cart = orm.relationship("Cart")
    orders = orm.relationship("Orders")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, e_mail={self.e_mail!r}, password={self.password!r})"

class Clothes(Base):
    __tablename__ = "clothes"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String)
    sizes = sql.Column(sql.String)
    colors = sql.Column(sql.String)
    image = sql.Column(sql.String)
    price = sql.Column(sql.Float)
    keywords = sql.Column(sql.String)
    cart = orm.relationship("Cart")
    orders = orm.relationship("Orders")

    def __repr__(self):
        return f"Clothes(id={self.id!r}, name={self.name!r}, sizes={self.sizes!r}, colors={self.colors!r}, image={self.image!r}, price={self.price!r}, keywords={self.keywords!r})"

class Cart(Base):
    __tablename__ = "cart"

    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("user_account.id"))
    clothing_id = sql.Column(sql.Integer, sql.ForeignKey("clothes.id"))
    clothing_size = sql.Column(sql.String)
    clothing_color = sql.Column(sql.String)

    def __repr__(self):
        return f"Cart(id={self.id!r}, user_id={self.user_id!r}, clothing_id={self.clothing_id!r}, clothing_size={self.clothing_size!r}, clothing_color={self.clothing_color!r})"

class Orders(Base):
    __tablename__ = "orders"

    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("user_account.id"))
    clothing_id = sql.Column(sql.Integer, sql.ForeignKey("clothes.id"))
    user_bank_name = sql.Column(sql.String)
    adress = sql.Column(sql.String)
    clothing_size = sql.Column(sql.String)
    clothing_color = sql.Column(sql.String)
    delivered = sql.Column(sql.Boolean)
    value = sql.Column(sql.Float)

    def __repr__(self):
        return f"Orders(id={self.id!r}, user_id={self.user_id!r}, clothing_id={self.clothing_id!r}, user_bank_name={self.user_bank_name!r}, adress={self.adress!r}, clothing_size={self.clothing_size!r}, clothing_color={self.clothing_color!r}, delivered={self.delivered!r})"



engine = sql.create_engine("sqlite:///wosh.db", echo=True, future=True)

Base.metadata.create_all(engine)

with orm.Session(engine) as session:
    #print(images)
    stmt = sql.select(Clothes.name)
    rows = session.scalars(stmt)
    cloth_names = rows

    for i in images:
        if i["name"] not in cloth_names:
            print(i)
            with orm.Session(engine) as session:
                stmt = sql.insert(Clothes).values(name=i["name"], sizes=i["sizes"], image=i["image"], colors=i["colors"], price=i["price"], keywords=i["keywords"])
                print(stmt)
                session.execute(stmt)
                session.commit()

#with orm.Session(engine) as session:
#    stmt = sql.select(User)
#    users = session.scalars(stmt)
#
#    have_scalars = False
#    for i in users:
#        have_scalars = True
#        break
#    
#    if not have_scalars:
#        luna = User(name="luna", e_mail="emailda@luna.com.br", password="eu_uso_designer123")
#        session.add(luna)
#
#    session.commit()

