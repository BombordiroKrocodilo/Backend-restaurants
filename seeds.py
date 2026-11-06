from app.db import SessionLocal
from app.models import Restaurant, Review

def seed():
    db = SessionLocal()
    try:
        if db.query(Restaurant).count() > 0:
            print("База не пустая — сиды пропущены.")
            return
        r1 = Restaurant(title="Пушкин", address="Тверская 1", cuisine="русская")
        r2 = Restaurant(title="Марио", address="Арбат 10", cuisine="итальянская")
        r3 = Restaurant(title="Токио", address="Ленинский 20", cuisine="японская")
        db.add_all([r1, r2, r3])
        db.flush()

        db.add_all([
            Review(restaurant_id=r1.id, author="Иванов", rating=5, text="Отлично!"),
            Review(restaurant_id=r1.id, author="Петров", rating=4, text="Хорошо"),
            Review(restaurant_id=r2.id, author="Сидоров", rating=5, text="Паста супер"),
        ])
        db.commit()
        print("Сиды загружены: 3 ресторана, 3 отзыва.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()