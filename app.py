#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

#connect to a local postgresql database
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  id      = db.Column(db.Integer, primary_key=True)
  name    = db.Column(db.String, nullable=False)
  city    = db.Column(db.String(120), nullable=False)
  state   = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone   = db.Column(db.String(120))
  genres  = db.Column(db.ARRAY(db.String()), nullable=False)
  facebook_link = db.Column(db.String(120))
  image_link    = db.Column(db.String(500))
  website  =   db.Column(db.String(120))
  seeking_talent  = db.Column(db.Boolean)
  seeking_description  = db.Column(db.String(500))

  show = db.relationship('Shows', backref='venues', lazy=True)

  def __repr__(self):
    return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
  __tablename__ = 'artists'

  id     = db.Column(db.Integer, primary_key=True)
  name   = db.Column(db.String, nullable=False)
  city   = db.Column(db.String(120), nullable=False)
  state  = db.Column(db.String(120), nullable=False)
  phone  = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String()), nullable=False)
  facebook_link = db.Column(db.String(120))
  image_link    = db.Column(db.String(500))
  website  = db.Column(db.String(120))
  seeking_venue  = db.Column(db.Boolean)
  seeking_description  =  db.Column(db.String(500))

  show = db.relationship('Shows', backref='artists', lazy=True)

  def __repr__(self):
    return f'<Artist {self.id} {self.name}>'


class Shows(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  venue_id   = db.Column(db.Integer,db.ForeignKey('venues.id'),  nullable=False)
  artist_id  = db.Column(db.Integer,db.ForeignKey('artists.id'), nullable=False)
  start_time = db.Column(db.DateTime,nullable=False)

  def __repr__(self):
    return f'<Show {self.id} {self.venue_id} {self.artist_id}>'



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')



#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  error = False
  form = VenueForm()  
  try:
    name    = request.form['name']
    city    = request.form['city']
    state   = request.form['state']
    address = request.form['address']
    phone   = request.form['phone']
    genres  = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link    = request.form['image_link']
    website       = request.form['website'] 
    seeking_talent       = form.seeking_talent.data
    seeking_description  = request.form['seeking_description']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')



#  Update Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data  = venue.name    
  form.city.data  = venue.city    
  form.state.data = venue.state   
  form.address.data = venue.address 
  form.phone.data    = venue.phone   
  form.genres.data   = venue.genres  
  form.facebook_link.data = venue.facebook_link 
  form.image_link.data   = venue.image_link    
  form.website.data      = venue.website       
  form.seeking_talent.data     = venue.seeking_talent       
  form.seeking_description.data = venue.seeking_description 

  # populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm() 
  venue = Venue.query.get(venue_id)

  try:
    venue.name    = request.form['name']
    venue.city    = request.form['city']
    venue.state   = request.form['state']
    venue.address = request.form['address']
    venue.phone   = request.form['phone']
    venue.genres  = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.image_link    = request.form['image_link']
    venue.website       = request.form['website'] 
    venue.seeking_talent       = form.seeking_talent.data
    venue.seeking_description  = request.form['seeking_description']
   
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue could not be updated.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated')
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash('Venue could not be deleted.')
  else: 
    flash('Venue was successfully deleted.')
  return render_template('pages/home.html')


#  Show Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  data =[]
  areas = Venue.query.distinct(Venue.city, Venue.state).all()
  for area in areas:
    query_result = Venue.query.join(Shows).filter(Shows.start_time > datetime.now(), Shows.venue_id == area.id).all()
    upcoming_shows = len(query_result)
    data.append({
      "city": area.city,
      "state": area.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": upcoming_shows}for venue in Venue.query.filter_by(city=area.city, state=area.state).all()]})

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  search_term = request.form.get('search_term', '')
  search_response = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  
  for venue in search_response:
    query_result = Venue.query.join(Shows).filter(Shows.start_time > datetime.now(), Shows.venue_id == venue.id).all()
    data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(query_result)
        })

    response = {
        "count": len(search_response),
        "data": data
    }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)




@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  data = []
  past_shows = []
  upcoming_shows = []

  venue = Venue.query.filter_by(id=venue_id).first()
  shows = Shows.query.filter_by(venue_id = venue.id).all()
 
  for show in shows:
    artist = Artist.query.filter_by(id=show.artist_id).first()
    start_time = format_datetime(str(show.start_time))
    artist_show = {
    "artist_id": artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": start_time
    }
    if show.start_time >= datetime.now():
      upcoming_shows.append(artist_show)
    elif show.start_time < datetime.now():
      past_shows.append(artist_show)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows": upcoming_shows,
    "upcoming_shows_count": len(upcoming_shows)
    }

  return render_template('pages/show_venue.html', venue=data)



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  form = ArtistForm()
  error = False
  try:
    name    = request.form['name']
    city    = request.form['city']
    state   = request.form['state']
    phone   = request.form['phone']
    genres  = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link    = request.form['image_link']
    website       = request.form['website']
    seeking_venue        = form.seeking_venue.data
    seeking_description  = request.form['seeking_description']
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue =seeking_venue , seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:  
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

      

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data   = artist.name 
  form.city.data   = artist.city 
  form.state.data  = artist.state 
  form.phone.data  = artist.phone 
  form.genres.data = artist.genres 
  form.facebook_link.data = artist.facebook_link
  form.image_link.data    = artist.image_link
  form.website.data       = artist.website 
  form.seeking_venue.data = artist.seeking_venue 
  form.seeking_description.data = artist.seeking_description

  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm()  
  artist = Artist.query.get(artist_id)

  try:
    artist.name    = request.form['name']
    artist.city    = request.form['city']
    artist.state   = request.form['state']
    artist.phone   = request.form['phone']
    artist.genres  = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.image_link    = request.form['image_link']
    artist.website       = request.form['website']
    artist.seeking_venue        = form.seeking_venue.data
    artist.seeking_description  = request.form['seeking_description']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist could not be updated.')
  else:  
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated')
  return redirect(url_for('show_artist', artist_id=artist_id))

#  Show Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database

  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({"id": artist.id,"name": artist.name})

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  search_term = request.form.get('search_term', '')
  search_response = Artist.query.filter(Artist.name.ilike('%' + search_term  +'%')).all()
  
  for artist in search_response:
    query_result = Artist.query.join(Shows).filter(Shows.start_time > datetime.now(), Shows.artist_id == artist.id).all()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(query_result)
      })
    response = {
      "count": len(search_response),
      "data": data
      }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  data = []   
  past_shows = []
  upcoming_shows = []

  shows =  Shows.query.filter_by(artist_id = artist_id).all()
  artist = Artist.query.filter_by(id=artist_id).first()
 
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    start_time = format_datetime(str(show.start_time))

    venue_show = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(start_time)
    }
    if show.start_time >= datetime.now():
        upcoming_shows.append(venue_show)
    elif show.start_time < datetime.now():
        past_shows.append(venue_show)

  data = {
          "id": artist.id,
          "name": artist.name,
          "genres": artist.genres,
          "city": artist.city,
          "state": artist.state,
          "phone": artist.phone,
          "facebook_link": artist.facebook_link,
          "website": artist.website,
          "image_link": artist.image_link,
          "seeking_venue": artist.seeking_venue,
          "seeking_description": artist.seeking_description,
          "past_shows": past_shows,
          "past_shows_count": len(past_shows),
          "upcoming_shows":  upcoming_shows,
          "upcoming_shows_count": len(upcoming_shows)
       }

  return render_template('pages/show_artist.html', artist=data)


#  Create Shows
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  error = False
  try:

    venue_id   = request.form['venue_id']  
    artist_id  = request.form['artist_id']
    start_time = request.form['start_time']

    show = Shows(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Shows.query.all()
  for show in shows:
    artist = Artist.query.filter_by(id=show.artist_id).first()
    venue = Venue.query.filter_by(id=show.venue_id).first()
    data.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "artist_id": artist.id,
          "artist_name":artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(show.start_time)
      })

  return render_template('pages/shows.html', shows=data)




#  Error Handler
#  ----------------------------------------------------------------

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
