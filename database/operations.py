from sqlalchemy.orm import sessionmaker
from datetime import datetime

def store_sale(session, sale_data):
    new_sale = AudiR8Sale(
        listing_name=sale_data['name'],
        sale_price=sale_data['price'],
        sale_date=sale_data['date'],
        year=sale_data['year'],
        is_manual=sale_data['is_manual'],
        is_v10=sale_data['is_v10'],
        created_at=datetime.now()
    )
    session.add(new_sale)
    session.commit()