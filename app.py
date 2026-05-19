import streamlit as st
import pandas as pd
import re
import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import difflib
import math
from collections import defaultdict
from itertools import combinations
 
# Попробуем импортировать дополнительные библиотеки для новых функций
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    LANG_DETECT_AVAILABLE = True
except ImportError:
    LANG_DETECT_AVAILABLE = False

# Настройка страницы
st.set_page_config(
    page_title="Анализатор списка литературы | Expert Edition",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================== РАСШИРЕННЫЙ CSS ДИЗАЙН ========================
st.markdown("""
<style>
    /* Основные стили */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Карточки метрик */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        margin-bottom: 15px;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .metric-number {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-label {
        color: #666;
        font-size: 14px;
        margin-top: 8px;
    }
    
    /* Прогресс-бары для топ-листов */
    .rank-item {
        background: white;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        transition: all 0.3s;
        border-left: 3px solid #667eea;
    }
    .rank-item:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .rank-number {
        font-weight: bold;
        color: #667eea;
        font-size: 18px;
        display: inline-block;
        width: 40px;
    }
    .rank-name {
        display: inline-block;
        width: 200px;
        font-weight: 500;
    }
    .rank-count {
        float: right;
        color: #666;
    }
    .progress-bar-custom {
        background: #e0e0e0;
        border-radius: 10px;
        height: 8px;
        margin-top: 8px;
        overflow: hidden;
    }
    .progress-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s;
    }
    
    /* Бейджи статусов */
    .badge-success {
        background: #d4edda;
        color: #155724;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-warning {
        background: #fff3cd;
        color: #856404;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-danger {
        background: #f8d7da;
        color: #721c24;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-info {
        background: #d1ecf1;
        color: #0c5460;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Заголовки секций */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-weight: 600;
    }
    
    /* Адаптивные сетки */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    /* Кастомные табы */
    .custom-tab {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Фильтры и таблицы */
    .dataframe-container {
        background: white;
        border-radius: 10px;
        padding: 15px;
        overflow-x: auto;
    }
    
    /* Карточки концептов */
    .concept-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 10px;
        padding: 12px;
        margin: 8px;
        text-align: center;
        border: 1px solid #667eea30;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

# ======================== КЭШИРОВАНИЕ ========================
@st.cache_data(ttl=3600, show_spinner=False)
def cache_crossref_lookup(doi: str) -> Optional[Dict]:
    """Кэшированный запрос к Crossref"""
    return fetch_crossref(doi)

@st.cache_data(ttl=3600, show_spinner=False)
def cache_openalex_lookup(doi: str) -> Optional[Dict]:
    """Кэшированный запрос к OpenAlex"""
    return fetch_openalex(doi)

@st.cache_data(ttl=7200, show_spinner=False)
def cache_issn_lookup(issn: str) -> Optional[Dict]:
    """Кэшированный запрос к ISSN Portal"""
    try:
        url = f"https://portal.issn.org/api/hub?issn={issn}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# ======================== ИЗВЛЕЧЕНИЕ DOI ========================
def extract_doi_from_text(text: str) -> Optional[str]:
    """Извлечение DOI из строки с учетом всех возможных форматов"""
    # Очищаем текст
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Паттерны для DOI в разных форматах (от более специфичных к общим)
    patterns = [
        # https://doi.org/10.xxxx/xxxx
        r'https?://doi\.org/(10\.\d{4,9}/[^\s<>"\'()]+)',
        # https://dx.doi.org/10.xxxx/xxxx
        r'https?://dx\.doi\.org/(10\.\d{4,9}/[^\s<>"\'()]+)',
        # doi:10.xxxx/xxxx (с двоеточием)
        r'doi[:]\s*(10\.\d{4,9}/[^\s<>"\'()]+)',
        # DOI:10.xxxx/xxxx (с двоеточием и заглавными)
        r'DOI[:]\s*(10\.\d{4,9}/[^\s<>"\'()]+)',
        # doi = 10.xxxx/xxxx
        r'doi\s*=\s*(10\.\d{4,9}/[^\s<>"\'()]+)',
        # Просто 10.xxxx/xxxx в конце строки или перед пробелом/пунктуацией
        r'(10\.\d{4,9}/[^\s<>"\'()]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                # Очищаем от trailing punctuation
                doi_raw = re.sub(r'[.,;:)]+$', '', match)
                doi_raw = doi_raw.strip()
                # Валидируем формат DOI
                if re.match(r'10\.\d{4,9}/', doi_raw):
                    return doi_raw
    
    return None

# ======================== API ЗАПРОСЫ ========================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_crossref(doi: str) -> Optional[Dict]:
    """Запрос к Crossref API"""
    try:
        url = f"https://api.crossref.org/works/{doi}"
        headers = {'User-Agent': 'LiteratureAnalyzer/2.0 (mailto:analyzer@example.com)'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()['message']
        return None
    except:
        return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_openalex(doi: str) -> Optional[Dict]:
    """Запрос к OpenAlex API"""
    try:
        encoded_doi = requests.utils.quote(doi)
        url = f"https://api.openalex.org/works/doi/{encoded_doi}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_openalex_concepts(work_id: str) -> List[Dict]:
    """Извлечение концептов из OpenAlex"""
    try:
        url = f"https://api.openalex.org/works/{work_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('concepts', [])
    except:
        pass
    return []

# ======================== НОРМАЛИЗАЦИЯ АВТОРОВ ========================
def normalize_author_name(name: str) -> Tuple[str, str]:
    """Нормализация имени автора"""
    if not name:
        return "", ""
    
    name = name.strip()
    
    if ',' in name:
        last, first = name.split(',', 1)
        last = last.strip()
        first = first.strip()
        initials = ''.join([p[0] for p in first.split() if p and p[0].isalpha()])
        display_name = f"{last} {initials}" if initials else last
        compare_name = f"{last.lower()} {initials.lower()}"
        return compare_name, display_name
    else:
        parts = name.split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = ''.join([p[0] for p in parts[:-1] if p and p[0].isalpha()])
            display_name = f"{last} {initials}" if initials else last
            compare_name = f"{last.lower()} {initials.lower()}"
            return compare_name, display_name
        return name.lower(), name

def extract_authors_from_crossref(data: Dict) -> List[Dict]:
    """Извлечение авторов из Crossref"""
    authors = []
    if 'author' in data and data['author']:
        for author in data['author']:
            given = author.get('given', '')
            family = author.get('family', '')
            orcid = author.get('ORCID', None)
            if family and given:
                raw_name = f"{given} {family}"
                compare_name, display_name = normalize_author_name(raw_name)
                authors.append({
                    'compare_name': compare_name,
                    'display_name': display_name,
                    'raw_name': raw_name,
                    'orcid': orcid,
                    'family': family,
                    'given': given
                })
            elif family:
                compare_name, display_name = normalize_author_name(family)
                authors.append({
                    'compare_name': compare_name,
                    'display_name': display_name,
                    'raw_name': family,
                    'orcid': orcid,
                    'family': family,
                    'given': ''
                })
    return authors

def extract_authors_from_openalex(data: Dict) -> List[Dict]:
    """Извлечение авторов из OpenAlex"""
    authors = []
    if 'authorships' in data and data['authorships']:
        for authorship in data['authorships']:
            author = authorship.get('author', {})
            display_name_raw = author.get('display_name', '')
            orcid = author.get('orcid', None)
            institutions = authorship.get('institutions', [])
            country = institutions[0].get('country_code', '') if institutions else ''
            
            if display_name_raw:
                compare_name, display_name = normalize_author_name(display_name_raw)
                authors.append({
                    'compare_name': compare_name,
                    'display_name': display_name,
                    'raw_name': display_name_raw,
                    'orcid': orcid,
                    'country': country,
                    'institution': institutions[0].get('display_name', '') if institutions else ''
                })
    return authors

def merge_authors(authors_list: List[Dict]) -> List[Dict]:
    """Объединение дублирующихся авторов"""
    merged = {}
    for author in authors_list:
        key = author.get('orcid') or author.get('compare_name', '')
        if key and key in merged:
            existing = merged[key]
            if not existing.get('orcid') and author.get('orcid'):
                existing['orcid'] = author['orcid']
            if len(author.get('display_name', '')) > len(existing.get('display_name', '')):
                existing['display_name'] = author['display_name']
        elif key:
            merged[key] = author.copy()
    return list(merged.values())

# ======================== ПОИСК ДУБЛИКАТОВ ========================
def find_duplicate_references(references: List[str], threshold: float = 0.85) -> List[Dict]:
    """Поиск дубликатов в списке литературы"""
    duplicates = []
    for i, ref1 in enumerate(references):
        doi1 = extract_doi_from_text(ref1)
        clean1 = re.sub(r'\s+', ' ', ref1).lower()
        clean1 = re.sub(r'[^\w\s]', '', clean1)
        
        for j, ref2 in enumerate(references[i+1:], i+1):
            doi2 = extract_doi_from_text(ref2)
            
            if doi1 and doi2 and doi1 == doi2:
                duplicates.append({
                    'index1': i, 'index2': j,
                    'ref1': ref1[:200], 'ref2': ref2[:200],
                    'reason': f'Одинаковый DOI: {doi1}'
                })
                continue
            
            clean2 = re.sub(r'\s+', ' ', ref2).lower()
            clean2 = re.sub(r'[^\w\s]', '', clean2)
            similarity = difflib.SequenceMatcher(None, clean1, clean2).ratio()
            
            if similarity > threshold:
                duplicates.append({
                    'index1': i, 'index2': j,
                    'ref1': ref1[:200], 'ref2': ref2[:200],
                    'reason': f'Схожесть текста: {similarity:.1%}'
                })
    return duplicates

# ======================== НОВЫЕ ФУНКЦИИ АНАЛИЗА ========================

def extract_concepts_from_references(results: List[Dict]) -> Dict:
    """Анализ концептов из OpenAlex"""
    concept_counter = Counter()
    concept_details = defaultdict(lambda: {'score_sum': 0, 'count': 0})
    
    for result in results:
        if result.get('openalex_data') and 'concepts' in result['openalex_data']:
            for concept in result['openalex_data']['concepts']:
                concept_name = concept.get('display_name', '')
                score = concept.get('score', 0)
                if concept_name:
                    concept_counter[concept_name] += 1
                    concept_details[concept_name]['score_sum'] += score
                    concept_details[concept_name]['count'] += 1
    
    # Рассчитываем средний score
    for concept in concept_details:
        concept_details[concept]['avg_score'] = concept_details[concept]['score_sum'] / concept_details[concept]['count']
    
    return {
        'concepts': concept_counter.most_common(20),
        'details': concept_details,
        'unique_concepts': len(concept_counter)
    }

def analyze_geographic_distribution(results: List[Dict]) -> Dict:
    """Географический анализ по странам авторов"""
    country_counter = Counter()
    institution_counter = Counter()
    
    for result in results:
        for author in result.get('authors', []):
            if author.get('country'):
                country_counter[author['country']] += 1
            if author.get('institution'):
                institution_counter[author['institution']] += 1
    
    # Карта стран (коды в названия)
    country_names = {
        'US': 'USA', 'GB': 'UK', 'CN': 'China', 'DE': 'Germany', 'FR': 'France',
        'JP': 'Japan', 'CA': 'Canada', 'AU': 'Australia', 'RU': 'Russia', 'BR': 'Brazil',
        'IN': 'India', 'KR': 'South Korea', 'IT': 'Italy', 'ES': 'Spain', 'NL': 'Netherlands'
    }
    
    countries_display = {}
    for code, count in country_counter.most_common(15):
        name = country_names.get(code, code)
        countries_display[name] = count
    
    return {
        'countries': countries_display,
        'institutions': institution_counter.most_common(10),
        'total_countries': len(country_counter),
        'international_percent': (len([c for c in country_counter if c != '']) / len(country_counter) * 100) if country_counter else 0
    }

def analyze_collaboration_network(results: List[Dict]) -> Dict:
    """Анализ сетей соавторства"""
    author_pairs = Counter()
    author_works = defaultdict(set)
    
    for result in results:
        authors = result.get('authors', [])
        author_names = [a.get('compare_name', '') for a in authors if a.get('compare_name')]
        
        for author in author_names:
            author_works[author].add(result.get('doi', ''))
        
        for author1, author2 in combinations(author_names, 2):
            if author1 < author2:
                author_pairs[(author1, author2)] += 1
    
    # Топ коллабораций
    top_collaborations = []
    for (a1, a2), count in author_pairs.most_common(20):
        # Находим отображаемые имена
        name1 = next((a['display_name'] for r in results for a in r.get('authors', []) 
                     if a.get('compare_name') == a1), a1)
        name2 = next((a['display_name'] for r in results for a in r.get('authors', []) 
                     if a.get('compare_name') == a2), a2)
        top_collaborations.append({'author1': name1, 'author2': name2, 'count': count})
    
    # Выявление core authors (авторы, связанные с многими другими)
    author_connections = {}
    for (a1, a2), count in author_pairs.items():
        author_connections[a1] = author_connections.get(a1, 0) + 1
        author_connections[a2] = author_connections.get(a2, 0) + 1
    
    core_authors = sorted(author_connections.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'top_collaborations': top_collaborations[:10],
        'core_authors': [(next((a['display_name'] for r in results for a in r.get('authors', []) 
                               if a.get('compare_name') == name), name), count) 
                         for name, count in core_authors],
        'total_collaborations': len(author_pairs)
    }

def analyze_temporal_citations(results: List[Dict]) -> Dict:
    """Временной анализ накопленных цитирований"""
    yearly_citations = defaultdict(int)
    paper_ages = []
    
    for result in results:
        if result.get('year'):
            year = result['year']
            if isinstance(year, (int, float)) and 1900 < year <= datetime.now().year:
                yearly_citations[year] += 1
                age = datetime.now().year - year
                paper_ages.append(age)
    
    # Накопленные цитирования
    cumulative = {}
    sorted_years = sorted(yearly_citations.keys())
    running_total = 0
    for year in sorted_years:
        running_total += yearly_citations[year]
        cumulative[year] = running_total
    
    # Медианный возраст
    median_age = sorted(paper_ages)[len(paper_ages)//2] if paper_ages else 0
    
    # "Sleeping beauties" (старые статьи с недавними цитированиями - упрощенно)
    recent_years = [y for y in sorted_years if y >= datetime.now().year - 3]
    old_years = [y for y in sorted_years if y <= datetime.now().year - 10]
    
    sleeping_beauties = []
    for result in results:
        if result.get('year') and result['year'] <= datetime.now().year - 10:
            # Проверяем, цитируется ли в последние годы (по данным API)
            if result.get('openalex_data') and 'cited_by_count' in result['openalex_data']:
                if result['openalex_data']['cited_by_count'] > 10:
                    sleeping_beauties.append({
                        'title': result.get('openalex_data', {}).get('title', 'Unknown')[:100],
                        'year': result['year'],
                        'citations': result['openalex_data']['cited_by_count']
                    })
    
    return {
        'yearly_distribution': dict(sorted(yearly_citations.items())),
        'cumulative_citations': cumulative,
        'median_age': median_age,
        'sleeping_beauties': sleeping_beauties[:5],
        'average_age': sum(paper_ages) / len(paper_ages) if paper_ages else 0
    }

def analyze_publisher_diversity(results: List[Dict]) -> Dict:
    """Анализ разнообразия издателей (индекс Херфиндаля)"""
    publisher_counter = Counter()
    
    for result in results:
        if result.get('publisher'):
            publisher_counter[result['publisher']] += 1
    
    total_pubs = sum(publisher_counter.values())
    if total_pubs == 0:
        return {
            'hhi': 0, 
            'diversity': 'N/A', 
            'top_publishers': [],
            'unique_publishers': 0  # ← ДОБАВИТЬ ЭТУ СТРОКУ
        }
    
    # Индекс Херфиндаля-Хиршмана
    hhi = sum((count / total_pubs * 100) ** 2 for count in publisher_counter.values())
    
    # Интерпретация
    if hhi < 1500:
        diversity = "Высокое разнообразие"
    elif hhi < 2500:
        diversity = "Среднее разнообразие"
    else:
        diversity = "Низкое разнообразие (зависимость от немногих издателей)"
    
    return {
        'hhi': round(hhi, 2),
        'diversity': diversity,
        'unique_publishers': len(publisher_counter),  # ← ДОБАВИТЬ ЭТУ СТРОКУ
        'top_publishers': publisher_counter.most_common(10)
    }

def analyze_orcid_coverage(results: List[Dict]) -> Dict:
    """Анализ покрытия ORCID"""
    total_authors = 0
    authors_with_orcid = 0
    orcid_by_country = Counter()
    
    for result in results:
        for author in result.get('authors', []):
            total_authors += 1
            if author.get('orcid'):
                authors_with_orcid += 1
                if author.get('country'):
                    orcid_by_country[author['country']] += 1
    
    coverage_percent = (authors_with_orcid / total_authors * 100) if total_authors > 0 else 0
    
    return {
        'total_authors': total_authors,
        'with_orcid': authors_with_orcid,
        'coverage_percent': coverage_percent,
        'orcid_by_country': dict(orcid_by_country.most_common(10))
    }

def analyze_language_distribution(results: List[Dict]) -> Dict:
    """Анализ языкового распределения заголовков"""
    if not LANG_DETECT_AVAILABLE:
        return {'available': False, 'message': 'Установите langdetect: pip install langdetect'}
    
    language_counter = Counter()
    
    for result in results:
        # Пробуем получить заголовок из Crossref или OpenAlex
        title = None
        if result.get('crossref_data') and 'title' in result['crossref_data']:
            title = result['crossref_data']['title'][0] if result['crossref_data']['title'] else None
        elif result.get('openalex_data') and 'title' in result['openalex_data']:
            title = result['openalex_data']['title']
        
        if title:
            try:
                lang = detect(title)
                language_counter[lang] += 1
            except:
                pass
    
    return {
        'available': True,
        'languages': dict(language_counter.most_common()),
        'non_english_percent': (sum(count for lang, count in language_counter.most_common() 
                                    if lang != 'en') / sum(language_counter.values()) * 100) if language_counter else 0
    }

def detect_predatory_journals(results: List[Dict]) -> List[Dict]:
    """Выявление потенциально хищнических журналов (признаки)"""
    predatory_signs = []
    
    # Список подозрительных издателей (пример)
    suspicious_publishers = ['OMICS', 'WASET', 'Scientific & Academic Publishing', 'Ashdin Publishing']
    
    for result in results:
        signs = []
        if result.get('publisher'):
            for sp in suspicious_publishers:
                if sp.lower() in result['publisher'].lower():
                    signs.append(f"Издатель {result['publisher']} в списке подозрительных")
        
        # Отсутствие DOI при наличии всех признаков
        if not result.get('doi') and result.get('journal'):
            signs.append("Нет DOI у статьи в журнале")
        
        # Подозрительно быстрая публикация (если есть даты)
        if result.get('crossref_data'):
            posted = result['crossref_data'].get('posted', {})
            issued = result['crossref_data'].get('issued', {})
            if posted and issued:
                signs.append("Возможна очень быстрая публикация")
        
        if signs:
            predatory_signs.append({
                'reference': result['original_text'][:200],
                'signs': signs,
                'journal': result.get('journal', 'Unknown')
            })
    
    return predatory_signs[:20]

def calculate_shannon_diversity(results: List[Dict], field: str = 'authors') -> float:
    """Индекс разнообразия Шеннона для авторов или журналов"""
    counter = Counter()
    
    for result in results:
        if field == 'authors':
            for author in result.get('authors', []):
                if author.get('compare_name'):
                    counter[author['compare_name']] += 1
        elif field == 'journals' and result.get('journal'):
            counter[result['journal']] += 1
        elif field == 'publishers' and result.get('publisher'):
            counter[result['publisher']] += 1
    
    total = sum(counter.values())
    if total == 0:
        return 0
    
    shannon = -sum((count / total) * math.log(count / total) for count in counter.values())
    return round(shannon, 3)

def identify_citation_classics(results: List[Dict]) -> List[Dict]:
    """Определение citation classics (статьи с аномально высокой цитируемостью)"""
    citation_counts = []
    
    for result in results:
        citations = 0
        if result.get('openalex_data') and 'cited_by_count' in result['openalex_data']:
            citations = result['openalex_data']['cited_by_count']
        elif result.get('crossref_data') and 'is-referenced-by-count' in result['crossref_data']:
            citations = result['crossref_data']['is-referenced-by-count']
        
        if citations > 0:
            citation_counts.append(citations)
    
    if len(citation_counts) < 5:
        return []
    
    mean_citations = sum(citation_counts) / len(citation_counts)
    std_citations = (sum((c - mean_citations) ** 2 for c in citation_counts) / len(citation_counts)) ** 0.5
    threshold = mean_citations + 2 * std_citations
    
    classics = []
    for result in results:
        citations = 0
        if result.get('openalex_data') and 'cited_by_count' in result['openalex_data']:
            citations = result['openalex_data']['cited_by_count']
        elif result.get('crossref_data') and 'is-referenced-by-count' in result['crossref_data']:
            citations = result['crossref_data']['is-referenced-by-count']
        
        if citations >= threshold:
            title = result.get('openalex_data', {}).get('title', '') or \
                    result.get('crossref_data', {}).get('title', [''])[0]
            classics.append({
                'title': title[:150],
                'citations': citations,
                'year': result.get('year', 'Unknown'),
                'journal': result.get('journal', 'Unknown')
            })
    
    return sorted(classics, key=lambda x: x['citations'], reverse=True)[:10]

# ======================== ОСНОВНАЯ ЛОГИКА АНАЛИЗА ========================
def parse_reference_list(references_text: str) -> List[str]:
    """Разбиение списка литературы на отдельные ссылки (поддержка множества форматов)"""
    lines = references_text.strip().split('\n')
    references = []
    current_ref = []
    
    # Паттерны для определения начала новой ссылки
    patterns = [
        r'^\d+\.',      # 1.
        r'^\[\d+\]',    # [1]
        r'^\(\d+\)',    # (1)
        r'^\d+\)',      # 1)
        r'^\d+\s+[A-Z]' # 1 Y. Zheng (без точки)
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Проверяем, начинается ли строка с маркера ссылки
        is_new_ref = False
        for pattern in patterns:
            if re.match(pattern, line):
                is_new_ref = True
                break
        
        if is_new_ref:
            # Сохраняем предыдущую ссылку
            if current_ref:
                references.append(' '.join(current_ref))
            
            # Очищаем маркер из начала строки
            cleaned_line = line
            for pattern in patterns:
                cleaned_line = re.sub(pattern, '', cleaned_line, count=1)
            cleaned_line = cleaned_line.strip()
            current_ref = [cleaned_line]
        else:
            # Продолжаем текущую ссылку
            if current_ref:
                current_ref.append(line)
            else:
                # Если нет текущей ссылки, начинаем новую
                current_ref = [line]
    
    # Добавляем последнюю ссылку
    if current_ref:
        references.append(' '.join(current_ref))
    
    return references

def analyze_reference_batch(references: List[str], progress_bar, progress_start: int, progress_end: int, paper_authors: Set[str] = None) -> List[Dict]:
    """Анализ батча ссылок (расширенная версия)"""
    results = []
    batch_size = len(references)
    
    for idx, ref in enumerate(references):
        doi = extract_doi_from_text(ref)
        
        result = {
            'original_text': ref,
            'doi': doi,
            'crossref_data': None,
            'openalex_data': None,
            'crossref_status': False,
            'openalex_status': False,
            'authors': [],
            'authors_display': [],
            'journal': None,
            'year': None,
            'type': None,
            'publisher': None,
            'crossmark_issues': [],
            'is_preprint': False,
            'has_erratum': False,
            'is_retracted': False,
            'is_self_citation': False,
            'issn': None,
            'license': None,
            'references_count': 0,
            'citations_count': 0
        }
        
        if doi:
            with ThreadPoolExecutor(max_workers=2) as executor:
                crossref_future = executor.submit(fetch_crossref, doi)
                openalex_future = executor.submit(fetch_openalex, doi)
                crossref_data = crossref_future.result()
                openalex_data = openalex_future.result()
            
            if crossref_data:
                result['crossref_data'] = crossref_data
                result['crossref_status'] = True
                
                authors_data = extract_authors_from_crossref(crossref_data)
                result['authors'].extend(authors_data)
                
                for auth in authors_data:
                    result['authors_display'].append(auth['display_name'])
                
                if 'container-title' in crossref_data and crossref_data['container-title']:
                    result['journal'] = crossref_data['container-title'][0]
                
                if 'ISSN' in crossref_data and crossref_data['ISSN']:
                    result['issn'] = crossref_data['ISSN'][0]
                
                if 'issued' in crossref_data and 'date-parts' in crossref_data['issued']:
                    date_parts = crossref_data['issued']['date-parts']
                    if date_parts and date_parts[0] and len(date_parts[0]) > 0:
                        result['year'] = date_parts[0][0]
                
                if 'type' in crossref_data:
                    result['type'] = crossref_data['type']
                
                if 'publisher' in crossref_data:
                    result['publisher'] = crossref_data['publisher']
                
                if 'license' in crossref_data:
                    result['license'] = crossref_data['license'][0].get('URL', '') if crossref_data['license'] else None
                
                if 'is-referenced-by-count' in crossref_data:
                    result['citations_count'] = crossref_data['is-referenced-by-count']
                
                if 'crossmark' in crossref_data:
                    for cm in crossref_data.get('crossmark', []):
                        if 'type' in cm:
                            result['crossmark_issues'].append(cm['type'])
            
            if openalex_data:
                result['openalex_data'] = openalex_data
                result['openalex_status'] = True
                
                authors_data = extract_authors_from_openalex(openalex_data)
                existing_compare = {a['compare_name'] for a in result['authors']}
                for auth in authors_data:
                    if auth['compare_name'] not in existing_compare:
                        result['authors'].append(auth)
                        result['authors_display'].append(auth['display_name'])
                        existing_compare.add(auth['compare_name'])
                
                if openalex_data.get('type') == 'posted_content':
                    result['is_preprint'] = True
                
                if openalex_data.get('is_retracted'):
                    result['is_retracted'] = True
                
                if not result['year'] and 'publication_year' in openalex_data:
                    result['year'] = openalex_data['publication_year']
                
                if not result['journal'] and 'host_venue' in openalex_data and openalex_data['host_venue']:
                    result['journal'] = openalex_data['host_venue'].get('display_name', '')
                
                if not result['type'] and 'type' in openalex_data:
                    result['type'] = openalex_data['type']
                
                if 'referenced_works_count' in openalex_data:
                    result['references_count'] = openalex_data['referenced_works_count']
                
                if 'cited_by_count' in openalex_data:
                    result['citations_count'] = max(result['citations_count'], openalex_data['cited_by_count'])
        
        if paper_authors and result['authors']:
            for author in result['authors']:
                for paper_author in paper_authors:
                    paper_norm, _ = normalize_author_name(paper_author)
                    if author['compare_name'] == paper_norm:
                        result['is_self_citation'] = True
                        break
        
        if result['authors']:
            result['authors'] = merge_authors(result['authors'])
            result['authors_display'] = [a['display_name'] for a in result['authors']]
        
        results.append(result)
        
        progress = progress_start + int((idx + 1) / batch_size * (progress_end - progress_start))
        progress_bar.progress(progress / 100)
    
    return results

def analyze_all_references(references: List[str], batch_size: int = 50, paper_authors: Set[str] = None) -> List[Dict]:
    """Анализ всех ссылок с батчированием"""
    all_results = []
    total_batches = (len(references) + batch_size - 1) // batch_size
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(references))
        batch = references[start_idx:end_idx]
        
        status_text.text(f"📊 Анализ батча {batch_num + 1} из {total_batches} (ссылки {start_idx + 1}-{end_idx} из {len(references)})")
        
        progress_start = (batch_num * 100) // total_batches
        progress_end = ((batch_num + 1) * 100) // total_batches
        
        batch_results = analyze_reference_batch(batch, progress_bar, progress_start, progress_end, paper_authors)
        all_results.extend(batch_results)
    
    status_text.text("✅ Анализ завершен!")
    progress_bar.progress(100)
    
    return all_results

# ======================== РАСШИРЕННАЯ СТАТИСТИКА ========================
def generate_advanced_statistics(results: List[Dict]) -> Dict:
    """Генерация расширенной статистики с новыми метриками"""
    
    # Базовая статистика
    doi_status = {'both': 0, 'crossref_only': 0, 'openalex_only': 0, 'none': 0}
    author_counter = Counter()
    journal_counter = Counter()
    type_counter = Counter()
    year_counter = Counter()
    publisher_counter = Counter()
    problematic_refs = []
    
    for result in results:
        if result['doi']:
            if result['crossref_status'] and result['openalex_status']:
                doi_status['both'] += 1
            elif result['crossref_status']:
                doi_status['crossref_only'] += 1
            elif result['openalex_status']:
                doi_status['openalex_only'] += 1
            else:
                doi_status['none'] += 1
        else:
            doi_status['none'] += 1
        
        if result['journal']:
            journal_counter[result['journal']] += 1
        
        if result['type']:
            type_name = result['type'].replace('journal-', '').replace('-', ' ')
            type_counter[type_name] += 1
        
        if result['year'] and isinstance(result['year'], (int, float)) and 1900 < result['year'] <= datetime.now().year:
            year_counter[int(result['year'])] += 1
        
        if result['publisher']:
            publisher_counter[result['publisher']] += 1
        
        has_problem = False
        problems = []
        if result['is_retracted']:
            problems.append('Ретрагирована')
            has_problem = True
        if result['is_preprint']:
            problems.append('Препринт')
            has_problem = True
        if result['crossmark_issues']:
            problems.extend(result['crossmark_issues'])
            has_problem = True
        
        if has_problem:
            problematic_refs.append({'text': result['original_text'][:300], 'problems': ', '.join(problems)})
    
    # Топ авторов (с ORCID)
    author_details = {}
    for result in results:
        for author in result['authors']:
            key = author.get('orcid') or author.get('compare_name', '')
            if key:
                if key not in author_details:
                    author_details[key] = {
                        'display_name': author['display_name'],
                        'orcid': author.get('orcid'),
                        'count': 0,
                        'country': author.get('country', '')
                    }
                author_details[key]['count'] += 1
    
    sorted_authors = sorted(author_details.values(), key=lambda x: x['count'], reverse=True)
    top_authors_formatted = []
    for author in sorted_authors[:20]:
        orcid_str = f" 🔗 ORCID: {author['orcid']}" if author.get('orcid') else ""
        display = ' '.join([part.capitalize() for part in author['display_name'].split()])
        top_authors_formatted.append(f"{display}{orcid_str} — {author['count']} цит.")
    
    # Citation stacking
    total_refs_with_journal = sum(journal_counter.values())
    citation_stacking = []
    if total_refs_with_journal > 0:
        for journal, count in journal_counter.most_common():
            if count / total_refs_with_journal >= 0.10:
                citation_stacking.append({
                    'journal': journal,
                    'count': count,
                    'percentage': f"{count/total_refs_with_journal:.1%}"
                })
    
    # Часто цитируемые исследователи
    frequently_cited = [a for a in sorted_authors if a['count'] >= 5]
    
    unique_doi_count = len([r for r in results if r['doi']])
    current_year = datetime.now().year
    years_last_5 = sum(count for year, count in year_counter.items() if year >= current_year - 5)
    
    # Новые метрики
    concepts_data = extract_concepts_from_references(results)
    geo_data = analyze_geographic_distribution(results)
    collab_data = analyze_collaboration_network(results)
    temporal_data = analyze_temporal_citations(results)
    publisher_diversity = analyze_publisher_diversity(results)
    orcid_data = analyze_orcid_coverage(results)
    language_data = analyze_language_distribution(results)
    predatory = detect_predatory_journals(results)
    shannon_authors = calculate_shannon_diversity(results, 'authors')
    shannon_journals = calculate_shannon_diversity(results, 'journals')
    shannon_publishers = calculate_shannon_diversity(results, 'publishers')
    citation_classics = identify_citation_classics(results)
    
    return {
        'total_references': len(results),
        'total_with_doi': unique_doi_count,
        'doi_status': doi_status,
        'top_authors': top_authors_formatted,
        'top_journals': [f"{journal} — {count}" for journal, count in journal_counter.most_common(15)],
        'top_types': [f"{type_name} — {count}" for type_name, count in type_counter.most_common()],
        'year_distribution': dict(sorted(year_counter.items())),
        'years_last_5': years_last_5,
        'top_publishers': [f"{publisher} — {count}" for publisher, count in publisher_counter.most_common(10)],
        'problematic_refs': problematic_refs[:20],
        'citation_stacking': citation_stacking[:10],
        'frequently_cited': [f"{a['display_name']} — {a['count']}" for a in frequently_cited[:10]],
        'self_citations_count': len([r for r in results if r['is_self_citation']]),
        'self_citations_percent': (len([r for r in results if r['is_self_citation']]) / len(results) * 100) if results else 0,
        
        # Новые данные
        'concepts': concepts_data,
        'geography': geo_data,
        'collaboration': collab_data,
        'temporal': temporal_data,
        'publisher_diversity': publisher_diversity,
        'orcid_coverage': orcid_data,
        'language': language_data,
        'predatory_journals': predatory,
        'shannon_index': {
            'authors': shannon_authors,
            'journals': shannon_journals,
            'publishers': shannon_publishers
        },
        'citation_classics': citation_classics,
        'total_citations_sum': sum(r.get('citations_count', 0) for r in results),
        'avg_citations': sum(r.get('citations_count', 0) for r in results) / len(results) if results else 0
    }

# ======================== HTML ОТЧЕТ (НОВЫЙ ДИЗАЙН) ========================
def generate_html_report_advanced(results: List[Dict], stats: Dict, paper_authors: Set[str] = None) -> str:
    """Генерация расширенного HTML отчета с новым дизайном"""
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Расширенный анализ списка литературы</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 0;
            margin: 0;
        }}
        .report-wrapper {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        /* Sidebar Navigation */
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 260px;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            overflow-y: auto;
            z-index: 1000;
        }}
        .sidebar h3 {{
            margin-bottom: 20px;
            font-size: 18px;
        }}
        .sidebar a {{
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 8px;
            transition: all 0.3s;
        }}
        .sidebar a:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }}
        .main-content {{
            margin-left: 260px;
            padding: 30px 40px;
        }}
        /* Header */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .header .date {{
            opacity: 0.9;
        }}
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stat-label {{
            color: #666;
            margin-top: 10px;
            font-size: 14px;
        }}
        /* Section */
        .section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .section-title {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            display: inline-block;
        }}
        /* Rank Lists */
        .rank-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
            transition: all 0.3s;
        }}
        .rank-number {{
            font-weight: bold;
            color: #667eea;
            font-size: 18px;
            display: inline-block;
            width: 40px;
        }}
        .rank-name {{
            display: inline-block;
            width: 300px;
            font-weight: 500;
        }}
        .rank-count {{
            float: right;
            color: #666;
        }}
        .progress-bar {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 8px;
            margin-top: 8px;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            border-radius: 10px;
        }}
        /* Concept Cards */
        .concepts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .concept-card {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid #667eea30;
        }}
        .concept-name {{
            font-weight: 600;
            color: #667eea;
        }}
        .concept-score {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        /* Badges */
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin: 2px;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .badge-info {{ background: #d1ecf1; color: #0c5460; }}
        /* Footer */
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
            margin-top: 30px;
        }}
        @media print {{
            .sidebar {{ display: none; }}
            .main-content {{ margin-left: 0; }}
            .stat-card, .section {{ break-inside: avoid; }}
        }}
        @media (max-width: 768px) {{
            .sidebar {{ display: none; }}
            .main-content {{ margin-left: 0; padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>📊 Навигация</h3>
        <a href="#overview">📈 Общая статистика</a>
        <a href="#doi-status">🔍 Статус DOI</a>
        <a href="#authors">👨‍🎓 Авторы</a>
        <a href="#journals">📖 Журналы</a>
        <a href="#concepts">🧠 Концепты</a>
        <a href="#geography">🌍 География</a>
        <a href="#collaboration">🤝 Коллаборации</a>
        <a href="#temporal">📅 Временной анализ</a>
        <a href="#diversity">🔄 Разнообразие</a>
        <a href="#classics">⭐ Citation Classics</a>
        <a href="#problems">⚠️ Проблемы</a>
    </div>
    
    <div class="main-content">
        <div class="header">
            <h1>📚 Расширенный анализ списка литературы</h1>
            <div class="date">Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
            <div style="margin-top: 15px;">
                <span class="badge badge-success">✅ Crossref + OpenAlex</span>
                <span class="badge badge-info">📊 {stats['total_references']} ссылок</span>
            </div>
        </div>
        
        <div id="overview" class="section">
            <div class="section-title">📈 Общая статистика</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['total_references']}</div>
                    <div class="stat-label">Всего ссылок</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_with_doi']}</div>
                    <div class="stat-label">Найдено DOI</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['years_last_5']}</div>
                    <div class="stat-label">Ссылки за 5 лет</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['self_citations_count']}</div>
                    <div class="stat-label">Самоцитирования</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.get('total_citations_sum', 0)}</div>
                    <div class="stat-label">Суммарная цитируемость</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.get('avg_citations', 0):.1f}</div>
                    <div class="stat-label">Средняя цитируемость</div>
                </div>
            </div>
        </div>
        
        <div id="doi-status" class="section">
            <div class="section-title">🔍 Статус DOI</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['both']}</div>
                    <div class="stat-label">✅ Crossref + OpenAlex</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['crossref_only']}</div>
                    <div class="stat-label">⚠️ Только Crossref</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['openalex_only']}</div>
                    <div class="stat-label">⚠️ Только OpenAlex</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['none']}</div>
                    <div class="stat-label">❌ Нет данных</div>
                </div>
            </div>
        </div>
        
        <div id="authors" class="section">
            <div class="section-title">👨‍🎓 Топ авторов</div>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{author.split(" — ")[0]}</span><span class="rank-count">{author.split(" — ")[1] if " — " in author else ""}</span><div class="progress-bar"><div class="progress-fill" style="width: {min(100, int(author.split(" — ")[1].split()[0]) / int(stats["top_authors"][0].split(" — ")[1].split()[0]) * 100) if stats["top_authors"] and " — " in author else 0}%;"></div></div></div>' for i, author in enumerate(stats['top_authors'][:15])])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Индекс Шеннона (авторы): {stats['shannon_index']['authors']}</span>
                <span class="badge badge-info">Авторов с ORCID: {stats['orcid_coverage']['with_orcid']} ({stats['orcid_coverage']['coverage_percent']:.1f}%)</span>
            </div>
        </div>
        
        <div id="journals" class="section">
            <div class="section-title">📖 Топ журналов</div>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{journal.split(" — ")[0]}</span><span class="rank-count">{journal.split(" — ")[1] if " — " in journal else ""}</span><div class="progress-bar"><div class="progress-fill" style="width: {min(100, int(journal.split(" — ")[1].split()[0]) / int(stats["top_journals"][0].split(" — ")[1].split()[0]) * 100) if stats["top_journals"] and " — " in journal else 0}%;"></div></div></div>' for i, journal in enumerate(stats['top_journals'][:10])])}
            </div>
        </div>
        
        <div id="concepts" class="section">
            <div class="section-title">🧠 Ключевые концепты (OpenAlex)</div>
            <div class="concepts-grid">
                {''.join([f'<div class="concept-card"><div class="concept-name">{concept[0]}</div><div class="concept-score">Частота: {concept[1]}</div></div>' for concept in stats['concepts']['concepts'][:12]])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Уникальных концептов: {stats['concepts']['unique_concepts']}</span>
            </div>
        </div>
        
        <div id="geography" class="section">
            <div class="section-title">🌍 Географическое распределение</div>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-name">{country}</span><span class="rank-count">{count} авторов</span><div class="progress-bar"><div class="progress-fill" style="width: {count / max(stats["geography"]["countries"].values()) * 100 if stats["geography"]["countries"] else 0}%;"></div></div></div>' for country, count in list(stats['geography']['countries'].items())[:10]])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Стран представлено: {stats['geography']['total_countries']}</span>
                <span class="badge badge-info">Международное сотрудничество: {stats['geography']['international_percent']:.1f}%</span>
            </div>
        </div>
        
        <div id="collaboration" class="section">
            <div class="section-title">🤝 Топ коллабораций</div>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{collab["author1"]} + {collab["author2"]}</span><span class="rank-count">{collab["count"]} работ</span></div>' for i, collab in enumerate(stats['collaboration']['top_collaborations'][:8])])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Core authors: {', '.join([f"{author[0]} ({author[1]} связей)" for author in stats['collaboration']['core_authors'][:5]])}</span>
            </div>
        </div>
        
        <div id="temporal" class="section">
            <div class="section-title">📅 Временной анализ</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['temporal']['median_age']}</div>
                    <div class="stat-label">Медианный возраст (лет)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['temporal']['average_age']:.1f}</div>
                    <div class="stat-label">Средний возраст (лет)</div>
                </div>
            </div>
            <div>
                <h4>Накопленные цитирования по годам:</h4>
                {''.join([f'<div class="rank-item"><span class="rank-name">{year}</span><span class="rank-count">{count} ссылок</span><div class="progress-bar"><div class="progress-fill" style="width: {count / max(stats["temporal"]["yearly_distribution"].values()) * 100 if stats["temporal"]["yearly_distribution"] else 0}%;"></div></div></div>' for year, count in list(stats["temporal"]["yearly_distribution"].items())[-10:]])}
            </div>
            {f'<div style="margin-top: 15px;"><h4>💤 "Sleeping Beauties":</h4>{"".join([f"<div class=rank-item>📖 {beauty['title'][:80]}... ({beauty['year']}) — {beauty['citations']} цитирований</div>" for beauty in stats["temporal"]["sleeping_beauties"][:3]])}</div>' if stats['temporal']['sleeping_beauties'] else ''}
        </div>
        
        <div id="diversity" class="section">
            <div class="section-title">🔄 Разнообразие источников</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['publisher_diversity']['unique_publishers']}</div>
                    <div class="stat-label">Уникальных издателей</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['publisher_diversity']['hhi']}</div>
                    <div class="stat-label">Индекс Херфиндаля (HHI)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="font-size: 24px;">{stats['publisher_diversity']['diversity']}</div>
                    <div class="stat-label">Оценка разнообразия</div>
                </div>
            </div>
            <div>
                <h4>Индексы Шеннона:</h4>
                <span class="badge badge-info">Авторы: {stats['shannon_index']['authors']}</span>
                <span class="badge badge-info">Журналы: {stats['shannon_index']['journals']}</span>
                <span class="badge badge-info">Издатели: {stats['shannon_index']['publishers']}</span>
            </div>
        </div>
        
        <div id="classics" class="section">
            <div class="section-title">⭐ Citation Classics (аномально высокая цитируемость)</div>
            {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{classic["title"][:80]}...</span><span class="rank-count">📊 {classic["citations"]} цитирований</span><div style="font-size: 12px; color: #666; margin-top: 5px;">{classic["journal"]} ({classic["year"]})</div></div>' for i, classic in enumerate(stats['citation_classics'][:8])]) if stats['citation_classics'] else '<p>Не обнаружено</p>'}
        </div>
        
        <div id="problems" class="section">
            <div class="section-title">⚠️ Проблемные ссылки</div>
            {''.join([f'<div class="rank-item"><span class="badge badge-danger">⚠️ {ref["problems"]}</span><div style="margin-top: 8px;">{ref["text"]}...</div></div>' for ref in stats['problematic_refs'][:10]]) if stats['problematic_refs'] else '<p>✅ Не обнаружено</p>'}
            {f'<div style="margin-top: 15px;"><h4>🚨 Потенциально хищнические журналы:</h4>{"".join([f"<div class=rank-item>📕 {pred['journal']}<br><span style=font-size:12px;color:#666;>{', '.join(pred['signs'])}</span></div>" for pred in stats['predatory_journals'][:5]])}</div>' if stats['predatory_journals'] else ''}
        </div>
        
        <div class="footer">
            Отчет сгенерирован автоматически на основе данных Crossref и OpenAlex API.
            <br>© Анализатор списка литературы | Expert Edition
        </div>
    </div>
</body>
</html>"""
    
    return html

# ======================== UI ИНТЕРФЕЙС (ОБНОВЛЕННЫЙ) ========================
def main():
    st.title("📚 Анализатор списка литературы для научных редакций")
    st.markdown("### Расширенная версия с аналитикой Crossref + OpenAlex")
    st.markdown("---")
    
    # Боковая панель с улучшенным дизайном
    with st.sidebar:
        st.markdown("## ⚙️ Настройки")
        batch_size = st.slider("Размер батча", 10, 100, 50, help="Количество ссылок, обрабатываемых за один раз")
        
        st.markdown("---")
        st.markdown("## 👥 Авторы статьи (опционально)")
        st.markdown("*Для анализа самоцитирований*")
        
        authors_input = st.text_area(
            "Авторы (каждый с новой строки)",
            placeholder="E.V. Ramos-Fernandez\nJung HS\nZhang Wei\nSadykov V",
            help="Укажите авторов в любом формате"
        )
        
        paper_authors = set()
        if authors_input:
            for line in authors_input.strip().split('\n'):
                if line.strip():
                    paper_authors.add(line.strip())
            st.success(f"✅ Добавлено авторов: {len(paper_authors)}")
        
        st.markdown("---")
        st.info("💡 **Советы:**\n- Для больших списков (>500 ссылок) процесс может занять несколько минут\n- Доступны новые метрики: концепты, география, коллаборации, citation classics")
    
    # Основная область с табами
    tab1, tab2, tab3 = st.tabs(["📥 Загрузка данных", "📊 Расширенная аналитика", "📄 HTML Отчет"])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.header("Загрузка списка литературы")
        
        input_method = st.radio("Выберите способ ввода", ["Вставка текста", "Загрузка файла (.txt)"])
        
        references_text = ""
        
        if input_method == "Вставка текста":
            references_text = st.text_area(
                "Вставьте список литературы",
                height=400,
                placeholder="1. Jung HS, Kim BG, Kwon JH, Bae JW. Thermocatalytic technologies...\n2. Liew WM, Ainirazali N. Cutting-edge innovations..."
            )
        else:
            uploaded_file = st.file_uploader("Загрузите файл .txt", type=['txt'])
            if uploaded_file:
                references_text = uploaded_file.read().decode('utf-8')
                st.success(f"✅ Файл загружен, размер: {len(references_text)} символов")
        
        if st.button("🚀 Начать расширенный анализ", type="primary", disabled=not references_text.strip()):
            if references_text.strip():
                with st.spinner("📖 Парсинг списка литературы..."):
                    references = parse_reference_list(references_text)
                    st.info(f"📄 Найдено {len(references)} ссылок")
                    
                    with st.expander("🔍 Предпросмотр первых 3 ссылок"):
                        for i, ref in enumerate(references[:3]):
                            st.text(f"{i+1}. {ref[:200]}...")
                
                if len(references) > 2000:
                    st.error(f"❌ Превышен лимит в 2000 ссылок. Найдено {len(references)} ссылок.")
                else:
                    with st.spinner("🔍 Поиск дубликатов..."):
                        duplicates = find_duplicate_references(references)
                        if duplicates:
                            st.warning(f"⚠️ Найдено {len(duplicates)} потенциальных дубликатов")
                            with st.expander("Просмотр дубликатов"):
                                for dup in duplicates[:10]:
                                    st.text(f"Ссылка {dup['index1']+1} и {dup['index2']+1}")
                                    st.text(f"Причина: {dup['reason']}")
                                    st.markdown("---")
                    
                    st.session_state['references'] = references
                    st.session_state['paper_authors'] = paper_authors
                    st.session_state['batch_size'] = batch_size
                    st.session_state['analysis_started'] = True
                    
                    with st.spinner("🔄 Расширенный анализ ссылок (это может занять несколько минут)..."):
                        results = analyze_all_references(references, batch_size, paper_authors if paper_authors else None)
                        st.session_state['results'] = results
                        st.session_state['analysis_complete'] = True
                    
                    st.success(f"✅ Анализ завершен! Найдено DOI: {len([r for r in results if r['doi']])} из {len(results)} ссылок")
                    st.balloons()
                    st.info("👈 Перейдите на вкладку 'Расширенная аналитика' для детального просмотра")
            else:
                st.warning("⚠️ Пожалуйста, введите список литературы")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
            results = st.session_state['results']
            paper_authors = st.session_state.get('paper_authors', set())
            
            with st.spinner("📊 Генерация расширенной статистики..."):
                stats = generate_advanced_statistics(results)
            
            # Основные метрики в виде карточек
            st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['total_references']}</div>
                    <div class="metric-label">📄 Всего ссылок</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['total_with_doi']} ({stats['total_with_doi']/stats['total_references']*100 if stats['total_references'] > 0 else 0:.0f}%)</div>
                    <div class="metric-label">🔗 Найдено DOI</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['years_last_5']}</div>
                    <div class="metric-label">📅 Ссылки за 5 лет</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)</div>
                    <div class="metric-label">🔄 Самоцитирования</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Дополнительные метрики
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats.get('total_citations_sum', 0)}</div>
                    <div class="metric-label">📊 Суммарная цитируемость</div>
                </div>
                """, unsafe_allow_html=True)
            with col6:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats.get('avg_citations', 0):.1f}</div>
                    <div class="metric-label">⭐ Средняя цитируемость</div>
                </div>
                """, unsafe_allow_html=True)
            with col7:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['orcid_coverage']['coverage_percent']:.1f}%</div>
                    <div class="metric-label">🎯 ORCID покрытие</div>
                </div>
                """, unsafe_allow_html=True)
            with col8:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['publisher_diversity'].get('unique_publishers', 0)}</div>
                    <div class="metric-label">🏢 Уникальных издателей</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Группировка по категориям
            tab_metrics, tab_concepts, tab_geo, tab_collab, tab_temporal, tab_diversity, tab_classics, tab_problems = st.tabs([
                "📊 Метрики", "🧠 Концепты", "🌍 География", "🤝 Коллаборации", 
                "📅 Временной анализ", "🔄 Разнообразие", "⭐ Citation Classics", "⚠️ Проблемы"
            ])
            
            with tab_metrics:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 🔍 Статус DOI")
                    doi_data = pd.DataFrame([
                        {"Статус": "Crossref + OpenAlex", "Количество": stats['doi_status']['both']},
                        {"Статус": "Только Crossref", "Количество": stats['doi_status']['crossref_only']},
                        {"Статус": "Только OpenAlex", "Количество": stats['doi_status']['openalex_only']},
                        {"Статус": "Нет данных", "Количество": stats['doi_status']['none']}
                    ])
                    st.dataframe(doi_data, use_container_width=True)
                    
                    st.markdown("### 👨‍🎓 Топ авторов")
                    for i, author in enumerate(stats['top_authors'][:10], 1):
                        parts = author.split(" — ")
                        name = parts[0]
                        count = parts[1] if len(parts) > 1 else ""
                        st.markdown(f"""
                        <div class="rank-item">
                            <span class="rank-number">{i}.</span>
                            <span class="rank-name">{name[:50]}</span>
                            <span class="rank-count">{count}</span>
                            <div class="progress-bar-custom">
                                <div class="progress-fill" style="width: {int(count.split()[0]) / int(stats['top_authors'][0].split(' — ')[1].split()[0]) * 100 if stats['top_authors'] else 0}%;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### 📖 Топ журналов")
                    for i, journal in enumerate(stats['top_journals'][:10], 1):
                        parts = journal.split(" — ")
                        name = parts[0]
                        count = parts[1] if len(parts) > 1 else ""
                        st.markdown(f"""
                        <div class="rank-item">
                            <span class="rank-number">{i}.</span>
                            <span class="rank-name">{name[:50]}</span>
                            <span class="rank-count">{count}</span>
                            <div class="progress-bar-custom">
                                <div class="progress-fill" style="width: {int(count.split()[0]) / int(stats['top_journals'][0].split(' — ')[1].split()[0]) * 100 if stats['top_journals'] else 0}%;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("### 🏢 Топ издателей")
                    for i, pub in enumerate(stats['top_publishers'][:5], 1):
                        st.markdown(f"{i}. {pub}")
            
            with tab_concepts:
                st.markdown("### 🧠 Ключевые научные концепты")
                st.markdown("*На основе данных OpenAlex*")
                
                concepts_df = pd.DataFrame(stats['concepts']['concepts'][:15], columns=["Концепт", "Частота"])
                st.dataframe(concepts_df, use_container_width=True)
                
                if stats['concepts']['details']:
                    st.markdown("### 📊 Средние scores концептов")
                    concept_scores = [(name, data['avg_score']) for name, data in stats['concepts']['details'].items()]
                    concept_scores.sort(key=lambda x: x[1], reverse=True)
                    for name, score in concept_scores[:10]:
                        st.markdown(f"• **{name}**: {score:.3f}")
            
            with tab_geo:
                st.markdown("### 🌍 Географическое распределение авторов")
                if stats['geography']['countries']:
                    geo_df = pd.DataFrame(list(stats['geography']['countries'].items()), columns=["Страна", "Количество авторов"])
                    st.dataframe(geo_df, use_container_width=True)
                    
                    st.markdown(f"**Всего стран:** {stats['geography']['total_countries']}")
                    st.markdown(f"**Доля международного сотрудничества:** {stats['geography']['international_percent']:.1f}%")
                else:
                    st.info("Нет данных о географическом распределении")
                
                if stats['geography']['institutions']:
                    st.markdown("### 🏫 Топ институтов")
                    for inst, count in stats['geography']['institutions'][:10]:
                        st.markdown(f"• {inst}: {count} авторов")
            
            with tab_collab:
                st.markdown("### 🤝 Сети соавторства")
                if stats['collaboration']['top_collaborations']:
                    st.markdown("#### Топ коллабораций (авторские пары)")
                    for i, collab in enumerate(stats['collaboration']['top_collaborations'][:10], 1):
                        st.markdown(f"{i}. **{collab['author1']}** + **{collab['author2']}** — {collab['count']} совместных работ")
                else:
                    st.info("Недостаточно данных для анализа коллабораций")
                
                st.markdown("#### Core Authors (наиболее связанные)")
                for author, connections in stats['collaboration']['core_authors'][:10]:
                    st.markdown(f"• **{author}** — {connections} связей")
            
            with tab_temporal:
                st.markdown("### 📅 Временной анализ")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Медианный возраст статей:** {stats['temporal']['median_age']} лет")
                    st.markdown(f"**Средний возраст статей:** {stats['temporal']['average_age']:.1f} лет")
                
                with col2:
                    st.markdown(f"**Всего цитирований в выборке:** {stats.get('total_citations_sum', 0)}")
                    st.markdown(f"**Средняя цитируемость:** {stats.get('avg_citations', 0):.1f}")
                
                if stats['temporal']['yearly_distribution']:
                    st.markdown("#### Распределение по годам")
                    years_df = pd.DataFrame(list(stats['temporal']['yearly_distribution'].items()), columns=["Год", "Количество"])
                    st.bar_chart(years_df.set_index("Год"))
                
                if stats['temporal']['sleeping_beauties']:
                    st.markdown("#### 💤 'Sleeping Beauties' (старые статьи с высоким цитированием)")
                    for beauty in stats['temporal']['sleeping_beauties'][:5]:
                        st.markdown(f"• **{beauty['title'][:100]}...** ({beauty['year']}) — {beauty['citations']} цитирований")
            
            with tab_diversity:
                st.markdown("### 🔄 Анализ разнообразия")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-number">{stats['shannon_index']['authors']}</div>
                        <div class="metric-label">Индекс Шеннона (авторы)</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-number">{stats['shannon_index']['journals']}</div>
                        <div class="metric-label">Индекс Шеннона (журналы)</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-number">{stats['shannon_index']['publishers']}</div>
                        <div class="metric-label">Индекс Шеннона (издатели)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### 🏢 Издательское разнообразие")
                st.markdown(f"**Индекс Херфиндаля (HHI):** {stats['publisher_diversity']['hhi']}")
                st.markdown(f"**Оценка:** {stats['publisher_diversity']['diversity']}")
                st.markdown(f"**Уникальных издателей:** {stats['publisher_diversity']['unique_publishers']}")
            
            with tab_classics:
                st.markdown("### ⭐ Citation Classics")
                st.markdown("*Статьи с аномально высокой цитируемостью (>2 std от среднего)*")
                
                if stats['citation_classics']:
                    for i, classic in enumerate(stats['citation_classics'][:10], 1):
                        with st.expander(f"{i}. {classic['title'][:100]}..."):
                            st.markdown(f"**Цитирований:** {classic['citations']}")
                            st.markdown(f"**Журнал:** {classic['journal']}")
                            st.markdown(f"**Год:** {classic['year']}")
                else:
                    st.info("Не обнаружено статей с аномально высокой цитируемостью")
            
            with tab_problems:
                st.markdown("### ⚠️ Проблемные ссылки")
                if stats['problematic_refs']:
                    for ref in stats['problematic_refs'][:15]:
                        st.warning(f"**{ref['problems']}**\n\n{ref['text']}")
                else:
                    st.success("✅ Проблемные ссылки не обнаружены")
                
                if stats['predatory_journals']:
                    st.markdown("### 🚨 Потенциально хищнические журналы")
                    for pred in stats['predatory_journals'][:10]:
                        with st.expander(f"📕 {pred['journal']}"):
                            st.markdown(f"**Признаки:** {', '.join(pred['signs'])}")
                            st.markdown(f"**Ссылка:** {pred['reference']}")
            
            st.markdown("---")
            st.markdown("### 📋 Полный список ссылок с фильтрацией")
            
            # Фильтры для таблицы
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                show_doi_only = st.checkbox("Только с DOI")
            with col_filter2:
                show_problems_only = st.checkbox("Только проблемные")
            with col_filter3:
                search_term = st.text_input("Поиск по тексту", placeholder="Введите ключевое слово...")
            
            filtered_results = results
            if show_doi_only:
                filtered_results = [r for r in filtered_results if r['doi']]
            if show_problems_only:
                filtered_results = [r for r in filtered_results if r['is_retracted'] or r['is_preprint'] or r['crossmark_issues']]
            if search_term:
                filtered_results = [r for r in filtered_results if search_term.lower() in r['original_text'].lower()]
            
            st.markdown(f"**Показано {len(filtered_results)} из {len(results)} ссылок**")
            
            for i, result in enumerate(filtered_results[:50]):
                status_icon = "✅" if result['doi'] else "❌"
                problems_badges = []
                if result['is_retracted']:
                    problems_badges.append('<span class="badge-danger">Ретрагирована</span>')
                if result['is_preprint']:
                    problems_badges.append('<span class="badge-warning">Препринт</span>')
                if result['is_self_citation']:
                    problems_badges.append('<span class="badge-info">Самоцитирование</span>')
                
                badges_html = ' '.join(problems_badges)
                
                with st.expander(f"{status_icon} {result['original_text'][:150]}..."):
                    st.markdown(f"**DOI:** {result['doi'] if result['doi'] else 'Не найден'}")
                    st.markdown(f"**Статус:** Crossref: {'✅' if result['crossref_status'] else '❌'} | OpenAlex: {'✅' if result['openalex_status'] else '❌'}")
                    if result['journal']:
                        st.markdown(f"**Журнал:** {result['journal']}")
                    if result['year']:
                        st.markdown(f"**Год:** {result['year']}")
                    if result['authors_display']:
                        st.markdown(f"**Авторы:** {', '.join(result['authors_display'][:5])}")
                    if result.get('citations_count', 0) > 0:
                        st.markdown(f"**Цитирований:** {result['citations_count']}")
                    if badges_html:
                        st.markdown(f"**Проблемы:** {badges_html}", unsafe_allow_html=True)
                    st.markdown("**Полный текст:**")
                    st.text(result['original_text'])
            
            if len(filtered_results) > 50:
                st.info(f"Показаны первые 50 из {len(filtered_results)} ссылок")
            
        else:
            st.info("👈 Пожалуйста, загрузите список литературы на вкладке 'Загрузка данных' и нажмите 'Начать расширенный анализ'")
    
    with tab3:
        if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
            results = st.session_state['results']
            paper_authors = st.session_state.get('paper_authors', set())
            stats = generate_advanced_statistics(results)
            
            st.markdown("### 📄 Экспорт расширенного отчета")
            st.markdown("Скачайте HTML отчет с полной аналитикой для сохранения или отправки")
            
            html_report = generate_html_report_advanced(results, stats, paper_authors)
            
            st.download_button(
                label="💾 Скачать HTML отчет (Expert Edition)",
                data=html_report.encode('utf-8'),
                file_name=f"literature_analysis_expert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
            
            st.markdown("---")
            st.markdown("### 📋 Текстовая выгрузка")
            
            # Расширенная текстовая выгрузка
            copy_text = f"""
=== РАСШИРЕННЫЙ АНАЛИЗ СПИСКА ЛИТЕРАТУРЫ ===
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

=== ОСНОВНАЯ СТАТИСТИКА ===
Всего ссылок: {stats['total_references']}
Найдено DOI: {stats['total_with_doi']} ({stats['total_with_doi']/stats['total_references']*100 if stats['total_references'] > 0 else 0:.1f}%)
Ссылки за 5 лет: {stats['years_last_5']}
Самоцитирования: {stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)
Суммарная цитируемость: {stats.get('total_citations_sum', 0)}
Средняя цитируемость: {stats.get('avg_citations', 0):.1f}

=== СТАТУС DOI ===
Crossref + OpenAlex: {stats['doi_status']['both']}
Только Crossref: {stats['doi_status']['crossref_only']}
Только OpenAlex: {stats['doi_status']['openalex_only']}
Нет данных: {stats['doi_status']['none']}

=== ТОП АВТОРОВ ===
{chr(10).join(stats['top_authors'][:15])}

=== ORCID ПОКРЫТИЕ ===
Всего авторов: {stats['orcid_coverage']['total_authors']}
С ORCID: {stats['orcid_coverage']['with_orcid']} ({stats['orcid_coverage']['coverage_percent']:.1f}%)

=== ТОП ЖУРНАЛОВ ===
{chr(10).join(stats['top_journals'][:10])}

=== КЛЮЧЕВЫЕ КОНЦЕПТЫ (OpenAlex) ===
{chr(10).join([f"{c[0]}: {c[1]}" for c in stats['concepts']['concepts'][:10]])}

=== ГЕОГРАФИЯ ===
{chr(10).join([f"{country}: {count}" for country, count in list(stats['geography']['countries'].items())[:10]])}

=== CITATION CLASSICS ===
{chr(10).join([f"{c['title'][:100]}: {c['citations']} цитирований" for c in stats['citation_classics'][:5]]) if stats['citation_classics'] else 'Не обнаружено'}

=== ИНДЕКСЫ РАЗНООБРАЗИЯ ===
Авторы (Шеннон): {stats['shannon_index']['authors']}
Журналы (Шеннон): {stats['shannon_index']['journals']}
Издатели (Шеннон): {stats['shannon_index']['publishers']}
HHI (издатели): {stats['publisher_diversity']['hhi']} - {stats['publisher_diversity']['diversity']}
"""
            
            st.text_area("Скопируйте данные:", copy_text, height=400)
            
            if st.button("📋 Копировать в буфер обмена"):
                st.write("✅ Данные скопированы! (используйте Ctrl+C)")
        else:
            st.info("👈 Сначала выполните анализ на вкладке 'Загрузка данных'")

if __name__ == "__main__":
    main()
