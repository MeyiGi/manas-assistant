import asyncio
import httpx
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Protocol, Dict
import time

# ==========================================
# 1. DOMAIN & LOGIC
# ==========================================

@dataclass
class Course:
    department_id: int
    day: str
    time: str
    code: str
    name: str
    instructor: str
    room: str

class ManasParser:
    def parse(self, html: str, department_id: int) -> List[Course]:
        soup = BeautifulSoup(html, 'html.parser')
        courses = []
        tables = soup.find_all('table')

        for table in tables:
            header = table.find('tr')
            if not header: continue
            tds = header.find_all('td')
            if len(tds) < 2: continue
            days = [td.get_text(strip=True) for td in tds[1:]]
            
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if not cols: continue
                time_slot = cols[0].get_text(strip=True)
                
                for i, cell in enumerate(cols[1:]):
                    if i >= len(days): break
                    divs = cell.find_all('div')
                    for div in divs:
                        lines = div.get_text(separator='\n', strip=True).split('\n')
                        if lines:
                            full_title = lines[0]
                            parts = full_title.split(' ', 1)
                            code = parts[0]
                            name = parts[1] if len(parts) > 1 else ""
                            instructor = lines[1] if len(lines) > 1 else "?"
                            room = lines[2] if len(lines) > 2 else "?"
                            
                            courses.append(Course(department_id, days[i], time_slot, code, name, instructor, room))
        return courses

class TargetFilter:
    def is_match(self, course: Course) -> bool:
        if "UNS" not in course.code.upper(): return False
        if "-" in course.code:
            parts = course.code.split("-")
            # Проверка на 3 курс (начинается с 3)
            if len(parts) > 1 and len(parts[1]) > 0 and parts[1][0] == '3':
                return True
        return False

# ==========================================
# 2. PRESENTATION (FIXED & IMPROVED)
# ==========================================

class TablePresenter:
    """Отвечает за очистку, группировку и красивый вывод"""
    
    DAY_ORDER = {
        "Pazartesi": 1, "Salı": 2, "Çarşamba": 3, "Perşembe": 4, "Cuma": 5, 
        "Cumartesi": 6, "Pazar": 7
    }

    def _merge_times(self, times: List[str]) -> str:
        """Объединяет ['10:45-11:30', '11:40-12:25'] -> '10:45-12:25'"""
        if not times: return ""
        unique_times = sorted(list(set(times)))
        if not unique_times: return ""
        
        # Берем начало самого раннего и конец самого позднего
        start = unique_times[0].split('-')[0]
        end = unique_times[-1].split('-')[-1]
        return f"{start}-{end}"

    def _clean_name(self, name: str) -> str:
        """Убирает UNS-XXX из названия"""
        # Regex: убрать 'UNS-' затем цифры/точки, затем пробел
        return re.sub(r'^UNS-[\d\.]+\s+', '', name).strip()

    def print_table(self, courses: List[Course]):
        # 1. ГРУППИРОВКА (Убираем дубликаты разных департаментов)
        # Ключ: (День, Код, Преподаватель, Аудитория) -> Список времен
        grouped_data: Dict[tuple, List[str]] = {}
        course_names: Dict[str, str] = {} # Сохраняем лучшее имя для кода

        for c in courses:
            # Нормализуем данные для ключа
            key = (c.day, c.code, c.instructor, c.room)
            
            if key not in grouped_data:
                grouped_data[key] = []
            
            # Добавляем время, если его еще нет
            if c.time not in grouped_data[key]:
                grouped_data[key].append(c.time)
            
            # Сохраняем имя (иногда оно обрезано, берем самое длинное)
            clean = self._clean_name(c.name)
            if c.code not in course_names or len(clean) > len(course_names.get(c.code, "")):
                course_names[c.code] = clean

        # 2. ПОДГОТОВКА СТРОК
        display_rows = []
        for key, times in grouped_data.items():
            day, code, instructor, room = key
            
            merged_time = self._merge_times(times)
            final_name = course_names.get(code, "")
            
            # Сокращаем имя преподавателя (берем последнее слово/фамилию)
            short_instructor = instructor.split(' ')[-1] if instructor != "?" else "?"
            if len(instructor.split()) > 2: # Если имя длинное, пробуем инициал + фамилия
                 parts = instructor.split()
                 short_instructor = f"{parts[0][0]}. {parts[-1]}"

            display_rows.append({
                "day": day,
                "sort_day": self.DAY_ORDER.get(day, 99),
                "time": merged_time,
                "code": code,
                "name": final_name[:35], # Обрезаем слишком длинные названия
                "room": room,
                "instructor": short_instructor
            })

        # 3. СОРТИРОВКА (День -> Время)
        display_rows.sort(key=lambda x: (x["sort_day"], x["time"]))

        # 4. ВЫВОД
        print("\n")
        # Шапка
        print(f"{'DAY':<10} | {'TIME':<11} | {'CODE':<10} | {'COURSE NAME':<35} | {'ROOM':<20} | {'INSTRUCTOR'}")
        print("-" * 120)

        last_day = ""
        for row in display_rows:
            day_print = row["day"] if row["day"] != last_day else ""
            last_day = row["day"]
            
            # Подсветка кода (Green) и данных
            c_code = f"\033[92m{row['code']}\033[0m"
            
            print(f"{day_print:<10} | {row['time']:<11} | {c_code:<19} | {row['name']:<35} | {row['room']:<20} | {row['instructor']}")
        
        print("-" * 120)

# ==========================================
# 3. SERVICE & MAIN
# ==========================================

class AsyncTimetableService:
    def __init__(self, base_url: str, parser: ManasParser, filters: List[TargetFilter]):
        self.base_url = base_url
        self.parser = parser
        self.filters = filters
        self.sem = asyncio.Semaphore(20)

    async def _process(self, client, dept_id):
        url = f"{self.base_url}/{dept_id}"
        async with self.sem:
            try:
                resp = await client.get(url)
                if resp.status_code == 200 and resp.text.strip():
                    return self.parser.parse(resp.text, dept_id)
            except: pass
        return []

    async def run(self, start, end):
        async with httpx.AsyncClient(timeout=20.0, verify=False) as client:
            tasks = [self._process(client, i) for i in range(start, end + 1)]
            results = await asyncio.gather(*tasks)
        
        flat = [c for sub in results for c in sub]
        filtered = [c for c in flat if all(f.is_match(c) for f in self.filters)]
        return filtered

async def main():
    print("Загрузка данных... (ID 95-141)")
    service = AsyncTimetableService(
        "http://timetable.manas.edu.kg/department-printer",
        ManasParser(),
        [TargetFilter()]
    )
    
    courses = await service.run(95, 141)
    
    presenter = TablePresenter()
    presenter.print_table(courses)
    print(f"Всего уникальных пар: {len(courses)} (после фильтрации)")

if __name__ == "__main__":
    asyncio.run(main())