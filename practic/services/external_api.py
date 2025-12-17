import json
import os
from typing import Dict, Any, List

DATA_FILE = os.path.join(os.path.dirname(__file__), 'grades_data.json')


class ExternalDataService:
    """
    Класс, отвечающий за доступ к данным и вычисление статуса оценки.
    """

    def __init__(self):
        self.student_data: Dict[str, List[Dict[str, Any]]] = self._load_data()

    def _load_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Загружает данные студентов из JSON-файла с проверками."""
        data_map = {}
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

                if not isinstance(raw_data, list):
                    print(f"ERROR: JSON data is not a list in {DATA_FILE}. Aborting load.")
                    return {}

                for item in raw_data:
                    if isinstance(item, dict) and 'name' in item and 'grades' in item:
                        data_map[item['name']] = item['grades']
                    else:
                        print(f"WARNING: Skipping malformed item in JSON: {item}")

        except FileNotFoundError:
            print(f"ERROR: Data file not found at {DATA_FILE}")
            return {}
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON format in {DATA_FILE}")
            return {}

        return data_map

    def _calculate_status(self, grade: int) -> str:
        """
        Вычисляет статус оценки на основе балла.
        """
        if grade > 80:
            return "Отлично"
        elif grade >= 60:
            return "Хорошо"
        elif grade >= 40:
            return "Удовлетворительно"
        else:
            return "Неудовлетворительно"

    def get_grades_for_user(self, user_name: str) -> List[Dict[str, Any]]:
        """
        Извлекает данные и добавляет рассчитанный статус.
        """
        raw_grades = self.student_data.get(user_name, [])

        if not raw_grades:
            print(f"DATA_ACCESS: No data found for user: {user_name}")
            return [{"subject": "Нет данных", "grade": 0, "max": 0, "status": "—"}]

        processed_grades = []
        for item in raw_grades:
            processed_item = item.copy()
            grade = processed_item.get('grade', 0)
            processed_item['status'] = self._calculate_status(grade)
            processed_grades.append(processed_item)

        print(f"DATA_ACCESS: Grades found and statuses calculated for user: {user_name}")
        return processed_grades

    def get_all_users(self) -> List[str]:
        """Возвращает список всех доступных имен студентов."""
        return list(self.student_data.keys())


data_service = ExternalDataService()
