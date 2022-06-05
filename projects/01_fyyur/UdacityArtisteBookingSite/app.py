#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, request_finished, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, or_, true
from datetime import date, datetime
from forms import *
from wtforms.validators import DataRequired

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__, template_folder='templates')
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:bire1234@localhost:5432/tris'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(180), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    show = db.relationship('Show', backref='Venue', lazy=True)

    def __init__(self, name, city, state, address, phone, image_link, facebook_link, genres, website_link, seeking_talent, seeking_description):
      self.name = name
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.genres = genres
      self.website_link = website_link
      self.seeking_talent = seeking_talent
      self.seeking_description = seeking_description
      

    def __repr__(self) -> str:
       return f'<Venue ID: {self.id}, Venue: {self.name}, City: {self.city}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(60))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    
    show = db.relationship('Show', backref='Artist', lazy=True)
    
    def __init__(self, name, city, state, phone, genres, image_link, facebook_link, website_link, seeking_venue, seeking_description):
      self.name = name
      self.city = city
      self.state = state
      self.phone = phone
      self.genres = genres
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.website_link = website_link
      seeking_venue = seeking_venue
      seeking_description = seeking_description
      

    def __repr__(self):
       return f'<Artist ID: {self.id}, Name: {self.name}, Genres: {self.genres}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  def __init__(self, artist_id, venue_id, start_time):
    self.artist_id = artist_id
    self.venue_id = venue_id
    self.start_time = start_time
     

  def __repr__(self):
     return f'<Show ID:{self.id}, Artist ID: {self.artist_id}, Venue ID: {self.venue_id}, Start Time: {self.start_time}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%S:%M')
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  venue_state_and_city = ''
  data = []

  for venue in venues:
    print(venue)
    upcoming_shows = venue.query.filter(Show.start_time > current_time).all()
    if venue_state_and_city == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": len(upcoming_shows) 
      })
    else:
      venue_state_and_city == venue.city + venue.state
      data.append({
        "city":venue.city,
        "state":venue.state,
        "venues": [{
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })


  return render_template('pages/venues.html', areas=data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #  venue_search = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))

  data = []
  venues = []
  search_term = request.form.get("search_term").lower()
  for venue in db.session.query(Venue):
    if search_term in venue.name:
      venues.append(venue)
  for venue in venues:
    next_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.utcnow().strftime('%d-%m-%y %H:%M:%S')).all()
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(next_shows)
        })
    response = {
        "count": len(venues),
        "data": venues
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term',''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venues = Venue.query.get(venue_id)
  if venues:
    venue_info = venue_info(venues)
    current_time = datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')
    upcoming = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
    upcoming_shows = list(map(Show.artist_info, upcoming))
    venue_info["upcoming_shows"] = upcoming_shows
    venue_info["upcoming_shows_count"] = len(upcoming_shows)
    past = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time < current_time).all()
    past_shows = list(map(Show.artist_info, past))
    venue_info["past_shows"] = past_shows
    venue_info["past_shows_count"] = len(past_shows)

    return render_template('pages/show_venue.html', venue=venue_info)
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  #return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
 
    seeking_talent = False
    seeking_description = ''
    if 'seeking_talent' in request.form:
      seeking_talent = request.form['seeking_talent'] == 'y'
    if 'seeking_description' in request.form:
      seeking_description = request.form['seeking_description']
    venues = Venue(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'],
      genres=request.form['genres'],
      website_link=request.form['website_link'],
      seeking_talent=seeking_talent,
      seeking_description=seeking_description,
    )
    db.session.add(venues)
    db.session.commit()
    flash('Congratulations! Venue ' + request.form['name'] + ' located at: ' + request.form['address'] + ' was successfully added!')
    return render_template('pages/home.html')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  upcoming_show = db.session.query(Show).filter(Show.start_time >= date.today())
  if Show.id == venue_id and Show.start_time.date() == date.today():
    flash('Sorry, you cannot delete a venue scheduled to host a show today!')
  else:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue: '+ Venue.name + ' has been deleted successfully!')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.order_by(Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
 data = []
 artists = []
 search_term = request.form.get("search_term").lower()
 #searched = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
 for artist in db.session.query(Artist):
    if search_term in artist.name:
      artists.append(artist)
 for artist in artists:
    next_shows = Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > datetime.utcnow().strftime('%d-%m-%y %H:%M:%S')).all()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(next_shows)
        })
    response = {
        "count": len(artists),
        "data": artists
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term',''))

 

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_select = Artist.query.get(artist_id)
  artist_show = Artist.query.get(artist_id)
  if artist_show:
    artist_info = Artist.info(artist_show)
    current_time = datetime.utcnow().strftime('%d-%m-%y %H:%M:%S')
    upcoming = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
    upcoming_shows = list(map(Show.name, upcoming))
    artist_info["upcoming_shows"] = upcoming_shows
    artist_info["upcoming_shows_count"] = len(upcoming)
    past = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time < current_time).all()
    past_shows = list(map(Show.name, past))
    artist_info["past_shows"] = past_shows
    artist_info["past_shows_count"] = len(past_shows)
 
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artist_info)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_edit = Artist.query.get(artist_id)
  if artist_edit:
    Artist_data = Artist_data(artist_edit)
    form.name.data = Artist_data["name"]
    form.city.data = Artist_data["city"]
    form.state.data = Artist_data["state"]
    form.phone.data = Artist_data["phone"]
    form.genres.data = Artist_data["genres"]
    form.facebook_link.data = Artist_data["facebook_link"]
    form.image_link.data = Artist_data["image_link"]
    form.website_link.data = Artist_data["website_link"]
    form.seeking_venue.data = Artist_data["seeking_venue"]
    form.seeking_description.data = Artist_data["seeking_description"]
    return render_template('forms/edit_artist.html', form=form, artist=Artist_data)

  # TODO: populate form with fields from artist with ID <artist_id>
 # return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  if form.on_submit_validate():
    setattr(artist, 'name', request.form['name'])
    setattr(artist, 'city', request.form['city'])
    setattr(artist, 'state', request.form['state'])
    setattr(artist, 'phone', request.form['phone'])    
    setattr(artist, 'genres', request.form.getlist('genres'))
    setattr(artist, 'facebook_link', request.form['facebook_link'])
    setattr(artist, 'image_link', request.form['image_link'])
    setattr(artist, 'website_link', request.form['website_link'])
    setattr(artist, 'seeking_venue', request.form['seeking_venue'])
    setattr(artist, 'seeking_description', request.form['seeking_description'])


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_edit = Venue.query.get(venue_id)
  if venue_edit:
    venue_data = venue_data(venue_edit)
    form.name.data = venue_data["name"]
    form.city.data = venue_data["city"]
    form.state.data = venue_data["state"]
    form.address.data = venue_data["address"]
    form.phone.data = venue_data["phone"]
    form.genres.data = venue_data["genres"]
    form.facebook_link.data = venue_data["facebook_link"]
    form.image_link.data = venue_data["image_link"]
    form.website_link.data = venue_data["website_link"]
    form.seeking_talent.data = venue_data["seeking_talent"]
    form.seeking_description.data = venue_data["seeking_description"]
    return render_template('forms/edit_venue.html', form=form, venue=venue_data)
  
  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  seeking_venue = False
  seeking_description = ''
  if 'seeking_talent' in request.form:
    seeking_venue = request.form['seeking_venue'] == 'y'
    if 'seeking_description' in request.form:
      seeking_description = request.form['seeking_description']
  artists = Artist(
    name=request.form['name'],
    city=request.form['city'],
    state=request.form['state'],
    genres=request.form['genres'],
    phone=request.form['phone'],
    image_link=request.form['image_link'],
    facebook_link=request.form['facebook_link'],
    website_link=request.form['website_link'],
    seeking_venue=seeking_venue,
    seeking_description=seeking_description,
    )
  db.session.add(artists)
  db.session.commit()
  flash('Congratulations! Artist ' + request.form['name'] + ' from: ' + request.form['city'] + ' was successfully added!')
  
  return render_template('pages/home.html')

 
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  show_data = db.session.query(Show.Venue).options(db.joinedload(Show.Artist), db.joinedload(Venue.Artist)).order_by('start_time').all()
  data = list(map(Show.detail, show_data))
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  show = ShowForm(request.form)
  if request.method == 'POST':
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  else:
    db.session.rollback()
    flash('An error occurred. Show could not be listed!')
  return render_template('pages/home.html')


  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
