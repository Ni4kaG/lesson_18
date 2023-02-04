#
# Поиск вакансий
import requests

from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

url = 'https://api.hh.ru/vacancies'
engine = create_engine('sqlite:///orm.sqlite', echo=True)
Base = declarative_base()
skill_list = []

class Skill(Base):
    __tablename__ = 'skill'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Region(Base):
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(Integer, nullable=True)

    # note = Column(String, nullable=True)

    def __init__(self, name, number):
        self.name = name
        self.number = number

    def __str__(self):
        return f'{self.id}) {self.name}: {self.number}'


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Связь 1 - много, связь внешний ключ
    region_id = Column(Integer, ForeignKey('region.id'))

    def __init__(self, name, region_id):
        self.name = name
        self.region_id = region_id


# Создание таблицы
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

# Регионы
session.add_all([Region('Москва', 1), Region('Питер', 78)])
session.commit()

regions = session.query(Region).all()

for region in regions:
    req_name = f'{region}'
    params = {
        'text': req_name,
            # теперь идем по страницам
        'page': 1
    }
    result = requests.get(url, params=params).json()

    items = result['items']
    for item in items:
        new_vacancy = Vacancy(item['name'], region.id)
        session.add(new_vacancy)
        # новый запрос для вакансии по УРЛ для сборa ключевых навыков
        res_key_skills = requests.get(item['url']).json()
        for key_skill in res_key_skills['key_skills']:
            if not key_skill['name'] in skill_list:
                skill_list.append(key_skill['name'])
                new_skill = Skill(key_skill['name'])
                session.add(new_skill)

session.commit()


# Выборка данных
# 1. Все регионы которые есть в базе
skill_query = session.query(Skill).all()
for skill in skill_query:
    print(skill.name)


