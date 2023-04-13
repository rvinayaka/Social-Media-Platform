from flask import Flask, flash, request, jsonify
from conn import set_connection     # import database connection file
from settings import logger, handle_exceptions
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'

# Query
# create_query = """CREATE TABLE socials(sno SERIAL PRIMARY KEY ,
#                     username VARCHAR(200) NOT NULL ,
#                     liked BOOL NOT NULL ,
#                     comments VARCHAR(300) NOT NULL);"""

# Socials Table
#  sno | username | liked |   comments    | post |         interests
# -----+----------+-------+---------------+------+----------------------------
#    1 | KIWI     | t     | Nice Picture  | NEW  | National Geographic
#    2 | Anti     | f     | Nice          | NEW  | NASA, ISRO, Gossips Akka
#    3 | Anti     | f     | Nice          | NEW  | Collective memes
#    4 | Anya     | t     | Mind reader   | NEW  | Virally India
#    5 | Parsya   | t     | Active fellow | OLD  | Techy bhau
#    6 | Loid     | t     | Intelligent   | OLD  | Me Mumbaikar, Amchi Mumbai


# Posts Table
#  post_id | user_id | content  | views
# ---------+---------+----------+-------
#        1 |       1 | New Post |   200
#        2 |       2 | Variety  |  1000



@app.route("/accounts", methods=["GET", "POST"])  # CREATE an account
@handle_exceptions
def create_user():
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to create user")

    if request.method == "POST":
        # Inserting values into it
        username = request.json["username"]
        liked = request.json["liked"]
        comments = request.json["comments"]
        post = request.json["post"]

        # input_format ={
        #     "username": "KIWI",
        #     "liked": "True",
        #     "comments": "Nice Picture",
        #     "post": "NEW"
        #     }

        # insert query
        postgres_insert_query = """ INSERT INTO socials (username,
                                       liked, comments, post) VALUES (%s, %s, %s, %s)"""
        record_to_insert = (username, liked, comments, post)

        # execute query
        cur.execute(postgres_insert_query, record_to_insert)

        # Log the details into logger file
        logger(__name__).info(f"{username}'s account created")

        # commit to database
        conn.commit()
    return jsonify({"message": "Account created"}), 200


@app.route("/", methods=["GET"], endpoint='get_profile')
@handle_exceptions
def get_profile():
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to display list of accounts")

    cur.execute("SELECT * FROM socials")
    data = cur.fetchall()
    # Log the details into logger file
    logger(__name__).info("Displayed list of all accounts")

    return jsonify({"message": data}), 202

@app.route("/like/<string:username>", methods=["PUT"], endpoint='like_post')
@handle_exceptions
def like_post(username):
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to like the post")

    postgres_query = "UPDATE socials SET liked = TRUE WHERE username = %s"
    cur.execute(postgres_query, (username,))

    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"post liked by {username}")
    return jsonify({"message": "post liked"}), 200

#
#
@app.route("/comment/<string:username>", methods=["PUT"], endpoint='comment_post')
@handle_exceptions
def comment_post(username):
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to update the details ")

    comment = request.json["comment"]

    postgres_query = "UPDATE socials SET comments = %s WHERE username = %s"
    cur.execute(postgres_query, (comment, username))

    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"{username} commented on post")
    return jsonify({"message": "commented on post"}), 200


@app.route("/create_post/<int:sno>", methods=["POST"], endpoint='create_post')
@handle_exceptions
def create_post(sno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to create post")

    # Get values from the user
    data = request.get_json()
    post_id = data.get('postId')
    user_id = sno
    content = data.get('content')

    # query and values
    query = "INSERT INTO posts(post_id, user_id, content) VALUES (%s, %s, %s);"
    values = (post_id, user_id, content)

    cur.execute(query, values)
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Created new post with account no. {sno}")

    return jsonify({"message": data}), 202


@app.route("/accounts/<int:sno>", methods=["PUT"], endpoint='update_account_details')
@handle_exceptions
def update_account_details(sno):
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to update the details ")

    # get the username, user wants to update
    cur.execute("SELECT username from socials where sno = %s", (sno,))
    get_character = cur.fetchone()

    if not get_character:
        return jsonify({"message": "Character not found"}), 200

    data = request.get_json()
    # get the values user wants to update
    username = data.get('username')
    liked = data.get('liked')
    comments = data.get('comments')

    if username:
        cur.execute("UPDATE game SET username = %s WHERE sno = %s", (username, sno))
    elif liked:
        cur.execute("UPDATE game SET liked = %s WHERE sno = %s", (liked, sno))
    elif comments:
        cur.execute("UPDATE game SET comments = %s WHERE sno = %s", (comments, sno))

    # commit changes to table
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Account updated: {data}")

    logger(__name__).warning("Hence accounts updated, closing the connection")
    return jsonify({"message": "Account updated", "Details": data}), 200


@app.route("/delete/<int:sno>", methods=["DELETE"], endpoint='delete_user')      # DELETE user in the list
@handle_exceptions
def delete_user(sno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to delete the account")

    # delete query
    delete_query = "DELETE from socials WHERE sno = %s"

    # execute query
    cur.execute(delete_query, (sno,))

    # commit changes to table
    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"Account no {sno} deleted from the table")
    return jsonify({"message": "Deleted Successfully", "holder_name_no": sno}), 200


@app.route("/search/<string:username>", methods=["GET"], endpoint='search_user')      # search user in the list
@handle_exceptions
def search_user(username):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to search user")

    # Search query
    query = "SELECT * FROM socials WHERE username = %s"

    # execute query
    cur.execute(query, (username,))
    get_user = cur.fetchone()

    if not get_user:
        # Log the details into logger file
        logger(__name__).info(f"{username} not found in the list")
        return jsonify({"message": f"{username} not found in the list"}), 200
    else:
        # Log the details into logger file
        logger(__name__).info(f"{username} found in the list")
        return jsonify({"message": f"{username} found in the list", "details": get_user}), 200


@app.route("/views/<int:post_id>", methods=["PUT"], endpoint='views_count')      # count the views on post
@handle_exceptions
def views_count(post_id):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to COUNT views")

    # get the username, user wants to update
    cur.execute("SELECT user_id from posts where post_id = %s", (post_id,))
    get_user = cur.fetchone()

    if not get_user:
        # Log the details into logger file
        logger(__name__).info(f"Post with {post_id} not found in the table")
        return jsonify({"message": f"Post with {post_id} not found in the table"}), 200

    # values taken from the user
    data = request.get_json()
    views = data.get('views')

    # update query
    query = "UPDATE posts SET views = %s WHERE post_id = %s;"
    # execute query
    cur.execute(query, (views, post_id))

    # commit changes to table
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Account no {get_user[0]} got views count of {views}")
    return jsonify({"message": f"Account no {get_user[0]} got views count of {views}"}), 200


@app.route("/interests/<int:sno>", methods=["PUT"], endpoint='interest_in')      # users interest
@handle_exceptions
def interest_in(sno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to enter interest of user")

    # take all interests from the user
    interests = request.json.get('interests')

    # insert query
    query = "UPDATE socials SET interests = %s WHERE sno = %s"
    values = (interests, sno)

    # execute query
    cur.execute(query, values)

    # commit changes to table
    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"Interest of user account no {sno} in the table")
    return jsonify({"message": f"Interest of user account no {sno} in the table"}), 200



if __name__ == "__main__":
    app.run(debug=True, port=5000)
