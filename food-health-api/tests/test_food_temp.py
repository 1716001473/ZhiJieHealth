import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.models import food as food_models
from app.services.food_service import FoodService


class FoodTempTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_search_includes_temp_food(self):
        service = FoodService(self.db)
        if not hasattr(service, "upsert_temp_food"):
            self.fail("FoodService.upsert_temp_food not implemented")

        service.upsert_temp_food(
            name="咖喱杂菜",
            nutrition={"calories": 43, "protein": 1.5, "fat": 2, "carb": 6},
            source="deepseek_ai",
        )
        results = service.search_foods("咖喱")
        self.assertTrue(any(r.name == "咖喱杂菜" for r in results))
        match = next(r for r in results if r.name == "咖喱杂菜")
        self.assertEqual(getattr(match, "data_source", None), "deepseek_ai")

    def test_database_food_has_data_source(self):
        self.db.add(
            food_models.Food(
                name="测试饭",
                calories=100,
                protein=2,
                fat=1,
                carbohydrate=20,
            )
        )
        self.db.commit()

        service = FoodService(self.db)
        results = service.search_foods("测试")
        self.assertEqual(len(results), 1)
        self.assertEqual(getattr(results[0], "data_source", None), "database")


if __name__ == "__main__":
    unittest.main()
