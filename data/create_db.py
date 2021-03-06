from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, String, Float, Date, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, backref

Base = declarative_base()

#1. Teams Table
class Team(Base):
    '''An SQL Alchemy class used in creating the teams table'''
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer)
    min_year = Column(Integer)
    max_year = Column(Integer)
    abbreviation = Column(String(60))
    nickname = Column(String(60))
    city = Column(String(100))
    arena = Column(String(100), nullable=False)
    arena_capacity = Column(Float)
    owner = Column(String(100))
    generalmanager = Column(String(100))
    headcoach = Column(String(100))
    d_league_affiliation = Column(String(100))

#2. Player Table
class Player(Base):
    '''An SQL Alchemy class used in creating the players table'''
    __tablename__ = 'player'
    id = Column(String(), nullable=False, primary_key=True)
    player_name = Column(String(60))

#3. TeamPlayer Table
class TeamPlayer(Base):
    '''An SQL Alchemy class used in creating the team players (players by season) table'''
    __tablename__ = 'team_player'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('player.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    season = Column(Integer)
    players = relationship('Player', backref=backref('teams', lazy='dynamic'))
    teams = relationship('Team', backref=backref('players', lazy='dynamic'))

#4. Rankings Table
class Ranking(Base):
    '''An SQL Alchemy class used in creating the rankings table'''
    __tablename__ = 'ranking'
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    season_id = Column(Integer)
    standings_date = Column(Date())
    conference = Column(String(60))
    games = Column(Integer)
    wins = Column(Integer)
    loses = Column(Integer)
    home_record = Column(String(10))
    road_record = Column(String(10))
    return_to_play = Column(String(10))
    teams = relationship('Team', backref=backref('ranks', lazy='dynamic'))   

#5. Games Table
class Game(Base):
    '''An SQL Alchemy class used in creating the games table'''
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    game_date_est = Column(Date())
    home_team_id = Column(Integer, ForeignKey('team.id'))
    visitor_team_id = Column(Integer, ForeignKey('team.id'))
    game_status_text = Column(String(60))
    season = Column(Integer)
    home_team = relationship('Team', foreign_keys=[home_team_id], backref=backref('away_games', lazy='dynamic'))
    away_team = relationship('Team', foreign_keys=[visitor_team_id], backref=backref('home_games', lazy='dynamic'))

#6. Statistics Table
class Statistics(Base):
    '''An SQL Alchemy class used in creating the games_details table'''
    __tablename__ = 'statistics'
    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    comment = Column(String(300), default='Empty Comment')
    minute = Column(String(10))
    field_g_made = Column(Float)
    field_g_attempts = Column(Float)
    field_g3_made = Column(Float)
    field_g3_attempts = Column(Float)
    free_throws_made = Column(Float)
    free_throw_attempts = Column(Float)
    off_rebound = Column(Float)
    def_rebound = Column(Float)
    assist = Column(Float)
    steal = Column(Float)
    block = Column(Float)
    turnover = Column(Float)
    personal_foul = Column(Float)
    points = Column(Float)
    plus_minus = Column(Float)
    team = relationship('Team', backref=backref('stats', lazy='dynamic'))
    game = relationship('Game', backref=backref('stats', lazy='dynamic'), cascade="all, delete")
    player = relationship('Player', backref=backref('stats', lazy='dynamic'))

def create_database(database_filepath='my_db'):
    '''Main. Creates a predefined SQlite database using SQL alchemy.
    When run on the system, it takes an argument variable.
    Uses this variable to create the database.
    '''
    print('Creating the database....')
    if database_filepath[-3:] != '.db':
        database_filepath+='.db'
    engine = create_engine('sqlite:///'+database_filepath)
    Base.metadata.create_all(engine)
    print(f'database {database_filepath} succesfully created')
