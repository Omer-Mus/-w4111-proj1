"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://om2349:4506@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  #
  # example of a database query
  #

  cursor = g.conn.execute("""SELECT * FROM allergies""")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)



@app.route('/search_food', methods=['POST'])
def search_food():
  print(request.args)

  name = request.form['search_food']
  name = ' '.join(word[0].upper() + word[1:] for word in name.split())


  # cursor = g.conn.execute(text(F"SELECT DISTINCT F.name as Dish, R.name as Restaurant, F.category FROM Foods F, Restaurants R, reviewed_at Rev, reviews S, found_at AT, Locations L WHERE  F.category LIKE '%{name}%' AND Rev.rid = S.rid AND  Rev.fid = F.fid AND AT.GM_link = Rev.GM_link AND AT.GM_link = L.GM_link AND AT.res_id = R.res_id;"))
  cursor = g.conn.execute(text(F"""SELECT F.name AS Food , R.name AS restaurant, AVG(S.rating), f.price
                                    FROM Foods F, Restaurants R, reviewed_at Rev, reviews S, found_at AT, Locations L, Users U 
                                    WHERE  (F.name LIKE '%{name}%' OR F.name = '{name}') AND Rev.rid = S.rid AND Rev.fid = F.fid AND AT.GM_link = Rev.GM_link 
                                    AND AT.GM_link = L.GM_link AND AT.res_id = R.res_id AND U.user_name = Rev.user_name
                                    GROUP BY Food, restaurant, f.price"""))

  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()


  context = dict(data = names)


  return render_template("search.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#


@app.route('/search.html')
def another():
  return render_template("search.html")


@app.route('/comments.html')
def comments():
    print(request.args)

    # comment = request.form('comment')
    cursor = g.conn.execute(text("""SELECT DISTINCT F.name AS Food, F.fid, R.name AS restaurant, AT.GM_link, S.picture
                                      FROM Foods F, Restaurants R, reviewed_at Rev, found_at AT, Locations L, Reviews S
                                      WHERE  Rev.fid = F.fid AND  AT.GM_link = Rev.GM_link AND
                                      AT.GM_link = L.GM_link AND AT.res_id = R.res_id AND Rev.rid = S.rid;"""))
    names = []

    for result in cursor:
        names.append(result)
    cursor.close()

    context = dict(data=names)

    return render_template("/comments.html", **context)


@app.route('/make_comment', methods=['POST'])
def make_comment():
    try:
        Dish_num = request.form['Dish_num']
        user_name = request.form['user_name']
        rating = request.form['rating']
        comment = request.form['comment']
        picture = request.form['picture']
        date = request.form['date']
        print("Type of: ", type(rating))

        # Generate a new rid for the review.
        cursor = g.conn.execute(text("""SELECT rid
                                          FROM Reviews 
                                          ORDER BY reviews 
                                          DESC LIMIT 1;"""))
        rid = str(cursor.fetchone())[2:-3]
        rid = str(int(str(rid)) + 1)
        cursor.close()

        # print("rid=", rid)

        # fetches the GM_link and the fid for the review.

        cursor = g.conn.execute(text("""SELECT DISTINCT F.name AS Food, F.fid, R.name AS restaurant, AT.GM_link
                                      FROM Foods F, Restaurants R, reviewed_at Rev, found_at AT, Locations L
                                      WHERE  Rev.fid = F.fid AND  AT.GM_link = Rev.GM_link AND
                                      AT.GM_link = L.GM_link AND AT.res_id = R.res_id;"""))
        names = []
        for result in cursor:
            names.append(result)
        cursor.close()

        fid = names[int(Dish_num)][1]
        GM_link = names[int(Dish_num)][3]

        # print(fid)
        # print(GM_link)
        # print(names[int(Dish_num)][0])
        # Create a review and the create a reviewed_At relation to bond all of the components together.

        g.conn.execute('INSERT INTO reviews(rid, rating, picture, comment) VALUES(%s, %s, %s, %s)', rid, rating, picture, comment)
        # try:
        g.conn.execute('INSERT INTO Reviewed_At(fid, user_name, rid, GM_link, date) VALUES (%s, %s, %s, %s, %s)', fid, user_name, rid, GM_link, date)
        # except Exception as E:
        #     g.conn.execute(text(f"""DELETE FROM Review WHERE rid='{rid}'; """))
        #     return render_template('comments.html', error=f'ERROR:\nSomething went wrong. wrong date. Please input a vaild date.')
    except Exception as E:
        g.conn.execute(text(f"""DELETE FROM Reviews WHERE rid='{rid}'; """))
        return render_template('comments.html', error=f'ERROR:\nSomething went wrong. i.e., Foods index DNE, invalid date, wrong username, etc.')
    return redirect("/comments.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(request.args)
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('index')
    return render_template('login.html', error=error)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    user_name = request.form['user_name']
    name = request.form['name']
    email = request.form['email']
    sex = request.form['sex']

    try:
        g.conn.execute('INSERT INTO Users(user_name, name, email, sex) VALUES (%s, %s, %s, %s)', user_name, name, email, sex)
        return redirect('/')
    except Exception as E:
        return render_template('index.html', error=f'ERROR:\nThe user name {user_name} or the email {email} already exist.')


@app.route('/search_by_location', methods=['POST'])
def search_by_location():
    print(request.args)
    name = request.form['search_by_location']
    name = ' '.join(word[0].upper() + word[1:] for word in name.split())

    zip_code = request.form['zip_code']
    cursor = g.conn.execute(text(F"""SELECT F.name as Dish, R.name as Restaurant, AVG(S.rating) as rating, F.price
                      FROM Foods F, Restaurants R, reviewed_at Rev, reviews S, found_at AT, Locations L 
                      WHERE L.zip_code LIKE '%{zip_code}%' AND F.name LIKE '%{name}%' AND Rev.rid = S.rid AND
                      Rev.fid = F.fid AND  AT.GM_link = Rev.GM_link AND AT.GM_link = L.GM_link 
                      AND AT.res_id = R.res_id GROUP BY F.name, R.name, F.price;"""))

    # SELECT F.name AS Food, R.name AS restaurant, U.user_name, S.rating, S.comment
    names = []
    for result in cursor:
      names.append(result)  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("search.html", **context)




# @app.route('/dish_comments.html')
# def another():
#     return render_template("dish_comments.html")



# @app.route('/dish_comments.html', methods=['POST'])
# def search_by_location():
#     print(request.args)

#     fid = request.form['fid']
#     cursor = g.conn.execute(text(f"""SELECT F.name AS Food, R.name AS restaurant, Rev.date, S.comment, S.picture, S.rating
#                                      FROM Foods F, Restaurants R, reviewed_at Rev, found_at AT, Locations L, Reviews S
#                                      WHERE  Rev.fid = F.fid  AND F.fid = '{fid}' AND  AT.GM_link = Rev.GM_link AND
#                                      AT.GM_link = L.GM_link AND AT.res_id = R.res_id
#                                      AND S.rid = Rev.rid;"""))

#     names = []
#     for result in cursor:
#         names.append(result)  # can also be accessed using result[0]
#     cursor.close()

#     context = dict(data=names)

#     return render_template('/dish_comments.html', **context)


# New Page for Comment History!!!!!!

@app.route('/comments_history.html')
def comments_history():
    print(request.args)

    # comment = request.form('comment')
    # try:
    cursor = g.conn.execute(text("""SELECT DISTINCT F.name AS Food, F.fid, R.name AS restaurant, AT.GM_link
                                      FROM Foods F, Restaurants R, reviewed_at Rev, found_at AT, Locations L
                                      WHERE  Rev.fid = F.fid AND  AT.GM_link = Rev.GM_link AND
                                      AT.GM_link = L.GM_link AND AT.res_id = R.res_id;"""))
    names = []

    for result in cursor:
        names.append(result)
    cursor.close()

    context = dict(data=names)

    return render_template("comments_history.html")
    # except Exception as E:
    #     return render_template("comments_history.html", error = f'ERROR:\nThe user name {names[0]} Does not exist')


@app.route('/comments_history_search', methods=['POST'])
def comments_history_search():
    print(request.args)
    user_name = request.form['user_name']

    cursor = g.conn.execute(text(F"""SELECT F.name AS Food, R.name AS restaurant, Rev.date, S.comment, S.picture
                                     FROM Foods F, Restaurants R, reviewed_at Rev, found_at AT, Locations L, Reviews S
                                     WHERE  Rev.fid = F.fid AND  AT.GM_link = Rev.GM_link AND
                                     AT.GM_link = L.GM_link AND AT.res_id = R.res_id AND Rev.user_name = '{user_name}'
                                     AND S.rid = Rev.rid;
                                      """))

    names = []
    for result in cursor:
        names.append(result)  # can also be accessed using result[0]
    cursor.close()

    context = dict(data=names)

    return render_template("comments_history.html", **context)

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()


