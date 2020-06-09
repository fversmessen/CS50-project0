import os

from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#engine = create_engine(os.getenv("DATABASE_URL"))
#engine = create_engine("sqlite:///Airport.db")
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

print(f"PASSEER STAP 1")

@app.route("/")
def index():
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("index.html", flights=flights)

@app.route("/book", methods=["POST"])
def book():
    """Book a flight."""

    # Get form information.
    name = request.form.get("name")
    print(f"name=  {name}")

    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")

    # Make sure flight exists.
    bestaat = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount
    print(f"bestaat=  {bestaat}")
    if bestaat == 0:
        return render_template("error.html", message="No such flight with that id.")

    # Make sure passenger is not on the flight yet.
    aantal = db.execute("SELECT * FROM passengers WHERE name = :name AND flight_id = :flight_id", {"name": name, "flight_id": flight_id}).fetchone()
    print(f"aantal mensen met die naam = {aantal}")
    if aantal != None:
        return render_template ("error.html", message="Already passenger with that name on that flight.") 

    # If all OK, then assign passenger to flight.    
    db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
            {"name": name, "flight_id": flight_id})
    db.commit()
    return render_template("success.html")

@app.route("/flights")
def flights():
    """Lists all flights."""
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("flightsoverview.html", flights=flights)

@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    """Lists details about a single flight."""

    # Make sure flight exists.
    flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
    if flight is None:
        return render_template("error.html", message="No such flight.")

    # Get all passengers.
    passengers = db.execute("SELECT name FROM passengers WHERE flight_id = :flight_id",
                            {"flight_id": flight_id}).fetchall()
    return render_template("flightdetails.html", flight=flight, passengers=passengers)


if __name__ == "__main__":
    app.run(debug=True)