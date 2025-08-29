"""Dream categories system for Wanty bot."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class DreamCategory:
    """Dream category data structure."""
    id: str
    name: str
    description: str
    emoji: str
    examples: List[str]
    color: str = "#4A90E2"


class DreamCategorySystem:
    """Manages dream categories and filtering."""
    
    def __init__(self):
        """Initialize category system."""
        self.categories = self._initialize_categories()
    
    def _initialize_categories(self) -> Dict[str, DreamCategory]:
        """Initialize all available dream categories."""
        return {
            "entertainment": DreamCategory(
                id="entertainment",
                name="Развлечения",
                description="Веселые и интересные активности для досуга",
                emoji="🎭",
                examples=[
                    "Сходить в кино на новый фильм",
                    "Посетить концерт любимой группы",
                    "Сыграть в настольные игры",
                    "Сходить в театр",
                    "Посетить выставку или музей"
                ],
                color="#FF6B6B"
            ),
            "sports": DreamCategory(
                id="sports",
                name="Спорт и активность",
                description="Спортивные мероприятия и активный отдых",
                emoji="⚽",
                examples=[
                    "Пробежка в парке",
                    "Игра в футбол",
                    "Поход в горы",
                    "Велосипедная прогулка",
                    "Занятия йогой"
                ],
                color="#4ECDC4"
            ),
            "food": DreamCategory(
                id="food",
                name="Кулинария и еда",
                description="Кулинарные эксперименты и гастрономические приключения",
                emoji="🍽️",
                examples=[
                    "Попробовать новую кухню",
                    "Научиться готовить",
                    "Сходить в ресторан",
                    "Устроить пикник",
                    "Посетить кулинарный мастер-класс"
                ],
                color="#FFE66D"
            ),
            "travel": DreamCategory(
                id="travel",
                name="Путешествия",
                description="Поездки и исследование новых мест",
                emoji="✈️",
                examples=[
                    "Поездка в другой город",
                    "Путешествие за границу",
                    "Поход в лес",
                    "Поездка на море",
                    "Экскурсия по историческим местам"
                ],
                color="#95E1D3"
            ),
            "learning": DreamCategory(
                id="learning",
                name="Обучение и развитие",
                description="Получение новых знаний и навыков",
                emoji="📚",
                examples=[
                    "Изучить новый язык",
                    "Научиться играть на инструменте",
                    "Посетить мастер-класс",
                    "Изучить новую профессию",
                    "Научиться рисовать"
                ],
                color="#A8E6CF"
            ),
            "social": DreamCategory(
                id="social",
                name="Общение и знакомства",
                description="Социальные активности и новые знакомства",
                emoji="👥",
                examples=[
                    "Найти новых друзей",
                    "Устроить вечеринку",
                    "Присоединиться к клубу по интересам",
                    "Участвовать в групповых активностях",
                    "Организовать встречу единомышленников"
                ],
                color="#FFB6C1"
            ),
            "creative": DreamCategory(
                id="creative",
                name="Творчество и искусство",
                description="Творческие проекты и художественная деятельность",
                emoji="🎨",
                examples=[
                    "Создать картину",
                    "Написать рассказ",
                    "Сделать фотографии",
                    "Создать музыку",
                    "Участвовать в выставке"
                ],
                color="#DDA0DD"
            ),
            "wellness": DreamCategory(
                id="wellness",
                name="Здоровье и благополучие",
                description="Забота о здоровье и душевном состоянии",
                emoji="🧘",
                examples=[
                    "Заняться медитацией",
                    "Посетить спа",
                    "Начать заниматься спортом",
                    "Правильно питаться",
                    "Научиться управлять стрессом"
                ],
                color="#98FB98"
            ),
            "business": DreamCategory(
                id="business",
                name="Бизнес и карьера",
                description="Профессиональное развитие и предпринимательство",
                emoji="💼",
                examples=[
                    "Начать свой бизнес",
                    "Сменить профессию",
                    "Получить повышение",
                    "Найти наставника",
                    "Развить новые навыки"
                ],
                color="#F0E68C"
            ),
            "adventure": DreamCategory(
                id="adventure",
                name="Приключения и экстрим",
                description="Экстремальные виды спорта и приключения",
                emoji="🏔️",
                examples=[
                    "Прыжок с парашютом",
                    "Скалолазание",
                    "Дайвинг",
                    "Рафтинг",
                    "Парапланеризм"
                ],
                color="#FF8C00"
            )
        }
    
    def get_category(self, category_id: str) -> Optional[DreamCategory]:
        """Get category by ID."""
        return self.categories.get(category_id)
    
    def get_all_categories(self) -> List[DreamCategory]:
        """Get all available categories."""
        return list(self.categories.values())
    
    def get_categories_by_popularity(self, limit: int = 5) -> List[DreamCategory]:
        """Get most popular categories (placeholder for future implementation)."""
        # В будущем здесь можно добавить логику подсчета популярности
        return list(self.categories.values())[:limit]
    
    def search_categories(self, query: str) -> List[DreamCategory]:
        """Search categories by name or description."""
        query = query.lower()
        results = []
        
        for category in self.categories.values():
            if (query in category.name.lower() or 
                query in category.description.lower() or
                any(query in example.lower() for example in category.examples)):
                results.append(category)
        
        return results
    
    def get_category_stats(self) -> Dict[str, int]:
        """Get basic statistics for categories (placeholder)."""
        # В будущем здесь можно добавить реальную статистику
        return {cat.id: 0 for cat in self.categories.values()}
    
    def get_random_examples(self, category_id: str, count: int = 3) -> List[str]:
        """Get random examples for a category."""
        category = self.get_category(category_id)
        if not category:
            return []
        
        import random
        examples = category.examples.copy()
        random.shuffle(examples)
        return examples[:count]


# Глобальный экземпляр системы категорий
category_system = DreamCategorySystem()
