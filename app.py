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

# Настройка страницы
st.set_page_config(
    page_title="Анализатор списка литературы",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стилизация
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .report-metric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .warning {
        background-color: #ffeb3b;
        padding: 10px;
        border-radius: 5px;
    }
    .error {
        background-color: #ffcdd2;
        padding: 10px;
        border-radius: 5px;
    }
    .success {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
    }
    .check-card {
        background: white;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .check-passed { border-left: 4px solid #28a745; }
    .check-failed { border-left: 4px solid #dc3545; }
    .check-warning { border-left: 4px solid #ffc107; }
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

# ======================== ИЗВЛЕЧЕНИЕ DOI ========================
def extract_doi_from_text(text: str) -> Optional[str]:
    """Извлечение DOI из строки с учетом различных форматов"""
    # Сначала очищаем текст от лишних пробелов и переносов строк
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Паттерн для DOI в разных форматах (более гибкий)
    patterns = [
        r'https?://doi\.org/(10\.\d{4,9}/[^\s]+)',
        r'https?://dx\.doi\.org/(10\.\d{4,9}/[^\s]+)',
        r'doi[:]\s*(10\.\d{4,9}/[^\s]+)',
        r'DOI[:]\s*(10\.\d{4,9}/[^\s]+)',
        r'(10\.\d{4,9}/[^\s]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi_raw = match.group(1) if match.lastindex else match.group(0)
            doi_raw = re.sub(r'[.,;:)]+$', '', doi_raw)
            doi_raw = doi_raw.strip()
            if re.match(r'10\.\d{4,9}/', doi_raw):
                return doi_raw
    return None

# ======================== API ЗАПРОСЫ ========================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_crossref(doi: str) -> Optional[Dict]:
    """Запрос к Crossref API"""
    try:
        url = f"https://api.crossref.org/works/{doi}"
        headers = {
            'User-Agent': 'LiteratureAnalyzer/1.0 (mailto:analyzer@example.com)'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data['message']
        elif response.status_code == 404:
            return None
        else:
            return None
    except Exception as e:
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
        elif response.status_code == 404:
            return None
        else:
            return None
    except Exception as e:
        return None

# ======================== НОРМАЛИЗАЦИЯ АВТОРОВ ========================
def normalize_author_name(name: str) -> Tuple[str, str]:
    """
    Нормализация имени автора
    Возвращает (нормализованное_для_сравнения, отображаемое_имя)
    """
    if not name:
        return "", ""
    
    name = name.strip()
    
    # Формат "Фамилия, Имя"
    if ',' in name:
        last, first = name.split(',', 1)
        last = last.strip()
        first = first.strip()
        
        # Извлекаем инициалы
        initials = ''
        for part in first.split():
            if part and part[0].isalpha():
                initials += part[0]
        
        # Отображаемое имя: "Фамилия И."
        display_name = f"{last} {initials}" if initials else last
        
        # Для сравнения: "фамилия инициалы"
        compare_name = f"{last.lower()} {initials.lower()}"
        
        return compare_name, display_name
    
    # Формат "И.О. Фамилия"
    else:
        parts = name.split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = ''.join([p[0] for p in parts[:-1] if p and p[0].isalpha()])
            
            # Отображаемое имя: "Фамилия И."
            display_name = f"{last} {initials}" if initials else last
            
            # Для сравнения: "фамилия инициалы"
            compare_name = f"{last.lower()} {initials.lower()}"
            
            return compare_name, display_name
        
        # Если не удалось разобрать
        return name.lower(), name

def format_author_name(author_info: Dict) -> str:
    """Форматирование имени автора для отображения"""
    if 'display_name' in author_info:
        return author_info['display_name']
    if 'raw_name' in author_info:
        raw = author_info['raw_name']
        # Пытаемся красиво отформатировать
        if ',' in raw:
            last, first = raw.split(',', 1)
            first = first.strip()
            if first:
                return f"{last.strip()} {first[0]}."
        return raw
    return "Unknown"

def extract_authors_from_crossref(data: Dict) -> List[Dict]:
    """Извлечение авторов и ORCID из Crossref"""
    authors = []
    if 'author' in data and data['author']:
        for author in data['author']:
            given = author.get('given', '')
            family = author.get('family', '')
            orcid = author.get('ORCID', None)
            
            if family and given:
                # Формируем полное имя для отображения
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
    """Извлечение авторов и ORCID из OpenAlex"""
    authors = []
    if 'authorships' in data and data['authorships']:
        for authorship in data['authorships']:
            author = authorship.get('author', {})
            display_name_raw = author.get('display_name', '')
            orcid = author.get('orcid', None)
            
            if display_name_raw:
                compare_name, display_name = normalize_author_name(display_name_raw)
                authors.append({
                    'compare_name': compare_name,
                    'display_name': display_name,
                    'raw_name': display_name_raw,
                    'orcid': orcid,
                    'family': '',
                    'given': ''
                })
    return authors

def merge_authors(authors_list: List[Dict]) -> List[Dict]:
    """
    Объединение дублирующихся авторов по ORCID или normalized name
    """
    merged = {}
    
    for author in authors_list:
        key = None
        
        # Сначала пробуем по ORCID
        if author.get('orcid'):
            key = author['orcid']
        else:
            # Иначе по нормализованному имени
            key = author.get('compare_name', '')
        
        if key and key in merged:
            # Объединяем, сохраняем лучший display_name
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
    """
    Поиск дубликатов в списке литературы
    Использует сравнение строк и извлеченные DOI
    """
    duplicates = []
    seen = {}
    
    for i, ref1 in enumerate(references):
        # Извлекаем DOI
        doi1 = extract_doi_from_text(ref1)
        
        # Очищаем строку для сравнения
        clean1 = re.sub(r'\s+', ' ', ref1).lower()
        clean1 = re.sub(r'[^\w\s]', '', clean1)
        
        for j, ref2 in enumerate(references[i+1:], i+1):
            doi2 = extract_doi_from_text(ref2)
            
            # Если DOI совпадают и не None - явный дубликат
            if doi1 and doi2 and doi1 == doi2:
                duplicates.append({
                    'index1': i,
                    'index2': j,
                    'ref1': ref1[:200],
                    'ref2': ref2[:200],
                    'reason': f'Одинаковый DOI: {doi1}'
                })
                continue
            
            # Сравнение строк
            clean2 = re.sub(r'\s+', ' ', ref2).lower()
            clean2 = re.sub(r'[^\w\s]', '', clean2)
            
            # Вычисляем схожесть
            similarity = difflib.SequenceMatcher(None, clean1, clean2).ratio()
            
            if similarity > threshold:
                duplicates.append({
                    'index1': i,
                    'index2': j,
                    'ref1': ref1[:200],
                    'ref2': ref2[:200],
                    'reason': f'Высокая схожесть текста: {similarity:.1%}'
                })
    
    return duplicates

# ======================== ОСНОВНАЯ ЛОГИКА АНАЛИЗА ========================
def parse_reference_list(references_text: str) -> List[str]:
    """Разбиение списка литературы на отдельные ссылки"""
    lines = references_text.strip().split('\n')
    references = []
    current_ref = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Если строка начинается с цифры и точки - новая ссылка
        if re.match(r'^\d+\.', line):
            if current_ref:
                references.append(' '.join(current_ref))
            current_ref = [line]
        else:
            if current_ref:
                current_ref.append(line)
    
    if current_ref:
        references.append(' '.join(current_ref))
    
    return references

def analyze_reference_batch(references: List[str], progress_bar, progress_start: int, progress_end: int, paper_authors: Set[str] = None) -> List[Dict]:
    """Анализ батча ссылок"""
    results = []
    batch_size = len(references)
    
    for idx, ref in enumerate(references):
        # Извлекаем DOI
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
            'is_self_citation': False
        }
        
        if doi:
            # Параллельные синхронные запросы
            with ThreadPoolExecutor(max_workers=2) as executor:
                crossref_future = executor.submit(fetch_crossref, doi)
                openalex_future = executor.submit(fetch_openalex, doi)
                crossref_data = crossref_future.result()
                openalex_data = openalex_future.result()
            
            if crossref_data:
                result['crossref_data'] = crossref_data
                result['crossref_status'] = True
                
                # Извлекаем авторов из Crossref
                authors_data = extract_authors_from_crossref(crossref_data)
                result['authors'].extend(authors_data)
                
                for auth in authors_data:
                    result['authors_display'].append(auth['display_name'])
                
                if 'container-title' in crossref_data and crossref_data['container-title']:
                    result['journal'] = crossref_data['container-title'][0]
                
                if 'issued' in crossref_data and 'date-parts' in crossref_data['issued']:
                    date_parts = crossref_data['issued']['date-parts']
                    if date_parts and date_parts[0] and len(date_parts[0]) > 0:
                        result['year'] = date_parts[0][0]
                
                if 'type' in crossref_data:
                    result['type'] = crossref_data['type']
                
                if 'publisher' in crossref_data:
                    result['publisher'] = crossref_data['publisher']
                
                # Проверка CrossMark
                if 'crossmark' in crossref_data:
                    for cm in crossref_data.get('crossmark', []):
                        if 'type' in cm:
                            result['crossmark_issues'].append(cm['type'])
            
            if openalex_data:
                result['openalex_data'] = openalex_data
                result['openalex_status'] = True
                
                # Извлекаем авторов из OpenAlex
                authors_data = extract_authors_from_openalex(openalex_data)
                existing_compare = {a['compare_name'] for a in result['authors']}
                for auth in authors_data:
                    if auth['compare_name'] not in existing_compare:
                        result['authors'].append(auth)
                        result['authors_display'].append(auth['display_name'])
                        existing_compare.add(auth['compare_name'])
                
                # Проверка на препринт, ретракцию
                if openalex_data.get('type') == 'posted_content':
                    result['is_preprint'] = True
                
                if openalex_data.get('is_retracted'):
                    result['is_retracted'] = True
                
                # Обновляем год
                if not result['year'] and 'publication_year' in openalex_data:
                    result['year'] = openalex_data['publication_year']
                
                # Обновляем журнал
                if not result['journal'] and 'host_venue' in openalex_data and openalex_data['host_venue']:
                    result['journal'] = openalex_data['host_venue'].get('display_name', '')
                
                # Обновляем тип
                if not result['type'] and 'type' in openalex_data:
                    result['type'] = openalex_data['type']
        
        # Проверка на самоцитирование
        if paper_authors and result['authors']:
            for author in result['authors']:
                for paper_author in paper_authors:
                    paper_norm, _ = normalize_author_name(paper_author)
                    if author['compare_name'] == paper_norm:
                        result['is_self_citation'] = True
                        break
        
        # Объединяем авторов
        if result['authors']:
            result['authors'] = merge_authors(result['authors'])
            result['authors_display'] = [a['display_name'] for a in result['authors']]
        
        results.append(result)
        
        # Обновляем прогресс
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
        
        status_text.text(f"Анализ батча {batch_num + 1} из {total_batches} (ссылки {start_idx + 1}-{end_idx} из {len(references)})")
        
        progress_start = (batch_num * 100) // total_batches
        progress_end = ((batch_num + 1) * 100) // total_batches
        
        batch_results = analyze_reference_batch(batch, progress_bar, progress_start, progress_end, paper_authors)
        all_results.extend(batch_results)
    
    status_text.text("Анализ завершен!")
    progress_bar.progress(100)
    
    return all_results

# ======================== СТАТИСТИЧЕСКИЙ АНАЛИЗ ========================
def generate_statistics(results: List[Dict]) -> Dict:
    """Генерация статистики по результатам анализа"""
    
    # 1. Статус DOI
    doi_status = {
        'both': 0,
        'crossref_only': 0,
        'openalex_only': 0,
        'none': 0
    }
    
    # 2. Частота авторов (объединение по ORCID и имени)
    author_counter = Counter()
    author_details = {}  # {normalized_name: {display_name, orcid, count}}
    
    # 3. Частота журналов
    journal_counter = Counter()
    
    # 4. Типология
    type_counter = Counter()
    
    # 5. Годы
    year_counter = Counter()
    
    # 6. Издатели
    publisher_counter = Counter()
    
    # 7. Проблемные ссылки
    problematic_refs = []
    
    # 8. Citation stacking (чрезмерное цитирование журналов)
    total_refs_with_journal = 0
    
    for result in results:
        # Статус DOI
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
        
        # Журнал для citation stacking
        if result['journal']:
            journal_counter[result['journal']] += 1
            total_refs_with_journal += 1
        
        # Тип
        if result['type']:
            type_name = result['type'].replace('journal-', '').replace('-', ' ')
            type_counter[type_name] += 1
        
        # Год
        if result['year'] and isinstance(result['year'], (int, float)) and 1900 < result['year'] <= datetime.now().year:
            year_counter[int(result['year'])] += 1
        
        # Издатель
        if result['publisher']:
            publisher_counter[result['publisher']] += 1
        
        # Проблемные ссылки
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
            problematic_refs.append({
                'text': result['original_text'][:300],
                'problems': ', '.join(problems)
            })
    
    # 2. Анализ авторов (объединение по ORCID и имени)
    for result in results:
        for author in result['authors']:
            key = None
            # Приоритет: ORCID
            if author.get('orcid'):
                key = author['orcid']
            else:
                key = author.get('compare_name', '')
            
            if key:
                if key not in author_details:
                    author_details[key] = {
                        'display_name': author['display_name'],
                        'orcid': author.get('orcid'),
                        'count': 0,
                        'compare_name': author.get('compare_name', '')
                    }
                author_details[key]['count'] += 1
    
    # Сортируем авторов по частоте
    sorted_authors = sorted(author_details.values(), key=lambda x: x['count'], reverse=True)
    
    # Форматируем авторов для отображения
    top_authors_formatted = []
    for author in sorted_authors[:20]:
        orcid_str = f" (ORCID: {author['orcid']})" if author.get('orcid') else ""
        # Красивое отображение имени
        display = author['display_name']
        # Делаем первую букву заглавной, остальные строчные
        display = ' '.join([part.capitalize() for part in display.split()])
        top_authors_formatted.append(f"{display}{orcid_str} — {author['count']}")
    
    # 3. Citation stacking (журналы с >10% цитирований)
    citation_stacking = []
    if total_refs_with_journal > 0:
        threshold = 0.10  # 10%
        for journal, count in journal_counter.most_common():
            percentage = count / total_refs_with_journal
            if percentage >= threshold:
                citation_stacking.append({
                    'journal': journal,
                    'count': count,
                    'percentage': f"{percentage:.1%}"
                })
    
    # Часто цитируемые исследователи (авторы с >5 цитированиями)
    frequently_cited = [a for a in sorted_authors if a['count'] >= 5]
    
    # Подсчет уникальных DOI
    unique_doi_count = len([r for r in results if r['doi']])
    unique_doi_percent = (unique_doi_count / len(results) * 100) if results else 0
    
    # Подсчет ссылок за последние 5 лет
    current_year = datetime.now().year
    years_last_5 = sum(count for year, count in year_counter.items() if year >= current_year - 5)
    
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
        'self_citations_percent': (len([r for r in results if r['is_self_citation']]) / len(results) * 100) if results else 0
    }

# ======================== ГЕНЕРАЦИЯ HTML ОТЧЕТА ========================
def generate_html_report(results: List[Dict], stats: Dict, paper_authors: Set[str] = None) -> str:
    """Генерация HTML отчета для скачивания"""
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Анализ списка литературы</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 40px 20px;
        }}
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header .date {{ opacity: 0.9; font-size: 14px; }}
        .content {{ padding: 30px 40px; }}
        .section {{
            margin-bottom: 40px;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 30px;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 8px;
        }}
        .check-cards {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .check-card {{
            flex: 1;
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .check-number {{
            font-size: 36px;
            font-weight: bold;
        }}
        .check-passed .check-number {{ color: #28a745; }}
        .check-failed .check-number {{ color: #dc3545; }}
        .check-warning .check-number {{ color: #ffc107; }}
        .list {{
            list-style: none;
            padding: 0;
        }}
        .list li {{
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .reference-item {{
            background: #f8f9fa;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            font-size: 13px;
            line-height: 1.5;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 8px;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        @media (max-width: 768px) {{
            .content {{ padding: 20px; }}
            .stats-grid {{ grid-template-columns: 1fr 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>📊 Анализ списка литературы</h1>
            <div class="date">Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
        </div>
        <div class="content">
            <div class="section">
                <div class="section-title">Общая статистика</div>
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
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Статус DOI</div>
                <div class="check-cards">
                    <div class="check-card check-passed">
                        <div class="check-number">{stats['doi_status']['both']}</div>
                        <div>✅ Crossref + OpenAlex</div>
                    </div>
                    <div class="check-card check-warning">
                        <div class="check-number">{stats['doi_status']['crossref_only']}</div>
                        <div>⚠️ Только Crossref</div>
                    </div>
                    <div class="check-card check-warning">
                        <div class="check-number">{stats['doi_status']['openalex_only']}</div>
                        <div>⚠️ Только OpenAlex</div>
                    </div>
                    <div class="check-card check-failed">
                        <div class="check-number">{stats['doi_status']['none']}</div>
                        <div>❌ Нет данных</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">👨‍🎓 Топ авторов</div>
                <ul class="list">
                    {''.join([f'<li>• {author}</li>' for author in stats['top_authors'][:15]])}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-title">📖 Топ журналов</div>
                <ul class="list">
                    {''.join([f'<li>• {journal}</li>' for journal in stats['top_journals'][:10]])}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-title">🏢 Топ издателей</div>
                <ul class="list">
                    {''.join([f'<li>• {pub}</li>' for pub in stats['top_publishers'][:5]])}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-title">⚠️ Citation Stacking (Чрезмерное цитирование)</div>
                {f'<ul class="list">{"".join([f"<li>• {item["journal"]} — {item["count"]} ссылок ({item["percentage"]})</li>" for item in stats["citation_stacking"]])}</ul>' if stats['citation_stacking'] else '<p>Не обнаружено</p>'}
            </div>
            
            <div class="section">
                <div class="section-title">⭐ Часто цитируемые исследователи (≥5 раз)</div>
                {f'<ul class="list">{"".join([f"<li>• {author}</li>" for author in stats["frequently_cited"]])}</ul>' if stats['frequently_cited'] else '<p>Не обнаружено</p>'}
            </div>
            
            <div class="section">
                <div class="section-title">⚠️ Проблемные ссылки</div>
                {''.join([f'<div class="reference-item">🔴 <strong>{ref["problems"]}</strong><br>{ref["text"]}...</div>' for ref in stats['problematic_refs'][:10]]) if stats['problematic_refs'] else '<p>Не обнаружено</p>'}
            </div>
            
            <div class="section">
                <div class="section-title">📄 Полный список ссылок</div>
                {''.join([f'<div class="reference-item"><strong>{i+1}.</strong> {ref["original_text"]}</div>' for i, ref in enumerate(results)])}
            </div>
        </div>
        <div class="footer">
            Отчет сгенерирован автоматически. Данные получены из Crossref и OpenAlex API.
        </div>
    </div>
</body>
</html>"""
    
    return html

# ======================== UI ИНТЕРФЕЙС ========================
def main():
    st.title("📚 Анализатор списка литературы для научных редакций")
    st.markdown("---")
    
    # Боковая панель
    with st.sidebar:
        st.header("⚙️ Настройки")
        batch_size = st.slider("Размер батча", 10, 100, 50, help="Количество ссылок, обрабатываемых за один раз")
        
        st.markdown("---")
        st.header("👥 Авторы статьи (опционально)")
        st.markdown("Введите авторов статьи для анализа самоцитирований")
        
        authors_input = st.text_area(
            "Авторы (каждый с новой строки)",
            placeholder="E.V. Ramos-Fernandez\nJung HS\nZhang Wei\nSadykov V",
            help="Укажите авторов в любом формате. Программа нормализует имена для поиска совпадений"
        )
        
        paper_authors = set()
        if authors_input:
            for line in authors_input.strip().split('\n'):
                if line.strip():
                    paper_authors.add(line.strip())
            st.success(f"✅ Добавлено авторов: {len(paper_authors)}")
        
        st.markdown("---")
        st.info("💡 **Совет**: Для больших списков (более 500 ссылок) процесс может занять несколько минут.")
    
    # Основная область
    tab1, tab2, tab3 = st.tabs(["📥 Загрузка данных", "📊 Результаты анализа", "📄 HTML Отчет"])
    
    with tab1:
        st.header("Загрузка списка литературы")
        
        input_method = st.radio(
            "Выберите способ ввода",
            ["Вставка текста", "Загрузка файла (.txt)"]
        )
        
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
        
        if st.button("🚀 Начать анализ", type="primary", disabled=not references_text.strip()):
            if references_text.strip():
                # Парсим список
                with st.spinner("📖 Парсинг списка литературы..."):
                    references = parse_reference_list(references_text)
                    st.info(f"📄 Найдено {len(references)} ссылок")
                    
                    with st.expander("🔍 Предпросмотр первых 3 ссылок"):
                        for i, ref in enumerate(references[:3]):
                            st.text(f"{i+1}. {ref[:200]}...")
                
                if len(references) > 2000:
                    st.error(f"❌ Превышен лимит в 2000 ссылок. Найдено {len(references)} ссылок.")
                else:
                    # Поиск дубликатов
                    with st.spinner("🔍 Поиск дубликатов..."):
                        duplicates = find_duplicate_references(references)
                        if duplicates:
                            st.warning(f"⚠️ Найдено {len(duplicates)} потенциальных дубликатов")
                            with st.expander("Просмотр дубликатов"):
                                for dup in duplicates[:10]:
                                    st.text(f"Ссылка {dup['index1']+1} и {dup['index2']+1}")
                                    st.text(f"Причина: {dup['reason']}")
                                    st.text(f"1: {dup['ref1']}")
                                    st.text(f"2: {dup['ref2']}")
                                    st.markdown("---")
                    
                    # Сохраняем в session_state
                    st.session_state['references'] = references
                    st.session_state['paper_authors'] = paper_authors
                    st.session_state['batch_size'] = batch_size
                    st.session_state['analysis_started'] = True
                    
                    # Запускаем анализ
                    with st.spinner("🔄 Анализ ссылок..."):
                        results = analyze_all_references(references, batch_size, paper_authors if paper_authors else None)
                        st.session_state['results'] = results
                        st.session_state['analysis_complete'] = True
                    
                    st.success(f"✅ Анализ завершен! Найдено DOI: {len([r for r in results if r['doi']])} из {len(results)} ссылок")
                    st.info("👈 Перейдите на вкладку 'Результаты анализа' для детального просмотра")
            else:
                st.warning("⚠️ Пожалуйста, введите список литературы")
    
    with tab2:
        if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
            results = st.session_state['results']
            paper_authors = st.session_state.get('paper_authors', set())
            
            # Генерируем статистику
            with st.spinner("📊 Генерация статистики..."):
                stats = generate_statistics(results)
            
            # Общая статистика
            st.header("📈 Общая статистика")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Всего ссылок", stats['total_references'])
            with col2:
                st.metric("Найдено DOI", f"{stats['total_with_doi']} ({stats['total_with_doi']/stats['total_references']*100:.1f}%)")
            with col3:
                st.metric("Ссылки за 5 лет", stats['years_last_5'])
            with col4:
                if paper_authors:
                    st.metric("Самоцитирования", f"{stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)")
                else:
                    st.metric("Самоцитирования", "Не анализировались")
            
            # Статус DOI
            st.subheader("🔍 Статус DOI")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Crossref + OpenAlex", stats['doi_status']['both'])
            with col2:
                st.metric("⚠️ Только Crossref", stats['doi_status']['crossref_only'])
            with col3:
                st.metric("⚠️ Только OpenAlex", stats['doi_status']['openalex_only'])
            with col4:
                st.metric("❌ Нет данных", stats['doi_status']['none'])
            
            # Топ авторов
            st.subheader("👨‍🎓 Топ авторов по частоте упоминаний")
            if stats['top_authors']:
                for author in stats['top_authors']:
                    st.markdown(f"• {author}")
            else:
                st.info("Нет данных об авторах")
            
            # Топ журналов
            st.subheader("📖 Топ журналов")
            if stats['top_journals']:
                for journal in stats['top_journals'][:10]:
                    st.markdown(f"• {journal}")
            else:
                st.info("Нет данных о журналах")
            
            # Citation Stacking
            st.subheader("⚠️ Citation Stacking (Чрезмерное цитирование)")
            if stats['citation_stacking']:
                for item in stats['citation_stacking']:
                    st.warning(f"• {item['journal']} — {item['count']} ссылок ({item['percentage']})")
            else:
                st.success("✅ Не обнаружено")
            
            # Часто цитируемые исследователи
            st.subheader("⭐ Часто цитируемые исследователи (≥5 раз)")
            if stats['frequently_cited']:
                for author in stats['frequently_cited']:
                    st.markdown(f"• {author}")
            else:
                st.info("Нет исследователей с ≥5 цитированиями")
            
            # Типология
            st.subheader("📚 Типология источников")
            if stats['top_types']:
                for type_name in stats['top_types']:
                    st.markdown(f"• {type_name}")
            else:
                st.info("Нет данных о типах источников")
            
            # Хронология
            st.subheader("📅 Распределение по годам")
            if stats['year_distribution']:
                years_df = pd.DataFrame(list(stats['year_distribution'].items()), columns=['Год', 'Количество'])
                st.bar_chart(years_df.set_index('Год'))
            else:
                st.info("Нет данных о годах публикации")
            
            # Топ издателей
            st.subheader("🏢 Топ издателей")
            if stats['top_publishers']:
                for publisher in stats['top_publishers'][:5]:
                    st.markdown(f"• {publisher}")
            else:
                st.info("Нет данных об издателях")
            
            # Проблемные ссылки
            if stats['problematic_refs']:
                st.subheader("⚠️ Проблемные ссылки")
                for ref in stats['problematic_refs'][:10]:
                    with st.expander(f"⚠️ {ref['problems']}"):
                        st.text(ref['text'])
            
            # Детальный просмотр всех ссылок
            st.subheader("🔬 Детальный просмотр всех ссылок")
            
            show_doi_only = st.checkbox("Показать только ссылки с DOI")
            
            filtered_results = [r for r in results if not (show_doi_only and not r['doi'])]
            
            for i, result in enumerate(filtered_results):
                with st.expander(f"{i+1}. {'✅' if result['doi'] else '❌'} {result['original_text'][:100]}..."):
                    st.text(f"DOI: {result['doi'] if result['doi'] else 'Не найден'}")
                    st.text(f"Crossref: {'✅' if result['crossref_status'] else '❌'}")
                    st.text(f"OpenAlex: {'✅' if result['openalex_status'] else '❌'}")
                    if result['journal']:
                        st.text(f"Журнал: {result['journal']}")
                    if result['year']:
                        st.text(f"Год: {result['year']}")
                    if result['type']:
                        st.text(f"Тип: {result['type']}")
                    if result['publisher']:
                        st.text(f"Издатель: {result['publisher']}")
                    if result['authors_display']:
                        st.text(f"Авторы: {', '.join(result['authors_display'][:5])}")
                    if result['is_preprint']:
                        st.warning("⚠️ Препринт")
                    if result['is_retracted']:
                        st.error("⚠️ Ретрагирована")
                    if result['is_self_citation']:
                        st.warning("⚠️ Самоцитирование")
                    if result['crossmark_issues']:
                        st.info(f"CrossMark: {', '.join(result['crossmark_issues'])}")
                    st.text("Полный текст:")
                    st.text(result['original_text'])
        else:
            st.info("👈 Пожалуйста, загрузите список литературы на вкладке 'Загрузка данных' и нажмите 'Начать анализ'")
    
    with tab3:
        if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
            results = st.session_state['results']
            paper_authors = st.session_state.get('paper_authors', set())
            stats = generate_statistics(results)
            
            st.subheader("📄 Экспорт отчета")
            st.markdown("Скачайте отчет в формате HTML для сохранения или отправки")
            
            html_report = generate_html_report(results, stats, paper_authors)
            
            st.download_button(
                label="💾 Скачать HTML отчет",
                data=html_report.encode('utf-8'),
                file_name=f"literature_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
            
            st.markdown("---")
            st.subheader("📋 Копирование данных")
            
            # Подготовка текста для копирования
            copy_text = f"""
=== АНАЛИЗ СПИСКА ЛИТЕРАТУРЫ ===
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

=== ОБЩАЯ СТАТИСТИКА ===
Всего ссылок: {stats['total_references']}
Найдено DOI: {stats['total_with_doi']} ({stats['total_with_doi']/stats['total_references']*100:.1f}%)
Ссылки за 5 лет: {stats['years_last_5']}
Самоцитирования: {stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)

=== СТАТУС DOI ===
Crossref + OpenAlex: {stats['doi_status']['both']}
Только Crossref: {stats['doi_status']['crossref_only']}
Только OpenAlex: {stats['doi_status']['openalex_only']}
Нет данных: {stats['doi_status']['none']}

=== ТОП АВТОРОВ ===
{chr(10).join(stats['top_authors'][:15])}

=== ТОП ЖУРНАЛОВ ===
{chr(10).join(stats['top_journals'][:10])}

=== CITATION STACKING ===
{chr(10).join([f"{item['journal']} — {item['count']} ссылок ({item['percentage']})" for item in stats['citation_stacking']]) if stats['citation_stacking'] else 'Не обнаружено'}

=== ЧАСТО ЦИТИРУЕМЫЕ ИССЛЕДОВАТЕЛИ ===
{chr(10).join(stats['frequently_cited']) if stats['frequently_cited'] else 'Не обнаружено'}

=== ПРОБЛЕМНЫЕ ССЫЛКИ ===
{chr(10).join([f"{ref['problems']}: {ref['text']}" for ref in stats['problematic_refs'][:10]]) if stats['problematic_refs'] else 'Не обнаружено'}
"""
            
            st.text_area("Скопируйте данные:", copy_text, height=400)
            
            if st.button("📋 Копировать в буфер обмена"):
                st.write("✅ Данные скопированы! (используйте Ctrl+C)")
        else:
            st.info("👈 Сначала выполните анализ на вкладке 'Загрузка данных'")

if __name__ == "__main__":
    main()
