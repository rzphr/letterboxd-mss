from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = create_engine("sqlite:///reviews.db")
Session = sessionmaker(bind=engine)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    movie_name = Column(String, index=True)
    review_text = Column(Text)

Base.metadata.create_all(engine)

def store_reviews(movie_name, reviews):
    session = Session()
    for review in reviews:
        session.add(Review(movie_name=movie_name, review_text=review))
    session.commit()
    session.close()

def get_cached_reviews(movie_name):
    session = Session()
    results = session.query(Review).filter_by(movie_name=movie_name).all()
    session.close()
    return [r.review_text for r in results]
