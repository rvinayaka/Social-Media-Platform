from flask import Flask, flash, request, jsonify
from conn import set_connection     # import database connection file
from settings import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'

# Query
# create_query = """CREATE TABLE socials(sno SERIAL PRIMARY KEY ,
#                     username VARCHAR(200) NOT NULL ,
#                     liked BOOL NOT NULL ,
#                     comments VARCHAR(300) NOT NULL);"""

# Socials Table
#  sno | username | liked |   comments    | post
# -----+----------+-------+---------------+------
#    1 | KIWI     | t     | Nice Picture  | NEW
#    2 | Anti     | f     | Nice          | NEW
#    3 | Anti     | f     | Nice          | NEW
#    4 | Anya     | f     | Cute          | NEW
#    5 | Parsya   | t     | Active fellow | OLD
#    6 | Loid     | t     | Intelligent   | OLD

# Posts Table
#  post_id | user_id | content
# ---------+---------+----------
#        1 |       1 | New Post
#        2 |       2 | Variety




@app.route("/accounts", methods=["GET", "POST"])  # CREATE an account
def create_user():
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to create user")

    try:
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
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence account created, closing the connection")


@app.route("/", methods=["GET"])
def get_profile():
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to display list of accounts")

    try:
        cur.execute("SELECT * FROM socials")
        data = cur.fetchall()
        # Log the details into logger file
        logger(__name__).info("Displayed list of all accounts")

        return jsonify({"message": data}), 202
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence accounts displayed, closing the connection")


@app.route("/like/<string:username>", methods=["PUT"])
def like_post(username):
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to like the post")

    try:

        postgres_query = "UPDATE socials SET liked = TRUE WHERE username = %s"
        cur.execute(postgres_query, (username, ))

        conn.commit()
        # Log the details into logger file
        logger(__name__).info(f"post liked by {username}")
        return jsonify({"message": "post liked"}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence post liked, closing the connection")

#
#
@app.route("/comment/<string:username>", methods=["PUT"])
def comment_post(username):
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to update the details ")
    try:
        comment = request.json["comment"]

        postgres_query = "UPDATE socials SET comments = %s WHERE username = %s"
        cur.execute(postgres_query, (comment, username))

        conn.commit()

        # Log the details into logger file
        logger(__name__).info( f"{username} commented on post")
        return jsonify({"message": "commented on post"}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence commented on the post, closing the connection")



@app.route("/create_post/<int:sno>", methods=["POST"])
def create_post(sno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to create post")

    try:
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
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence post created, closing the connection")




@app.route("/accounts/<int:sno>", methods=["PUT"])
def update_account_details(sno):
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to update the details ")

    try:
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
        return jsonify({"message": "Account updated", "Details": data}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": "request method not found"}), 500
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence accounts updated, closing the connection")



@app.route("/delete/<int:sno>", methods=["DELETE"])      # DELETE an item from cart
def delete_user(sno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to delete the account")

    try:
        # delete query
        delete_query = "DELETE from socials WHERE sno = %s"

        # execute query
        cur.execute(delete_query, (sno,))

        # commit changes to table
        conn.commit()
        # Log the details into logger file
        logger(__name__).info(f"Account no {sno} deleted from the table")
        return jsonify({"message": "Deleted Successfully", "holder_name_no": sno}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence accounts deleted, closing the connection")



if __name__ == "__main__":
    app.run(debug=True, port=5000)
