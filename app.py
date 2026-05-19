import streamlit as st
import pandas as pd
import re
import asyncio
import aiohttp
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential
import time

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
</style>
""", unsafe_allow_html=True)

# ======================== КЭШИРОВАНИЕ ========================
def get_cache_key(doi: str, source: str) -> str:
    """Создание ключа для кэша"""
    return hashlib.md5(f"{doi}_{source}".encode()).hexdigest()

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
    # Паттерн для DOI в разных форматах
    patterns = [
        r'10\.\d{4,9}/[-._;()/:A-Z0-9]+',  # голый DOI
        r'doi:10\.\d{4,9}/[-._;()/:A-Z0-9]+',  # с doi:
        r'DOI:10\.\d{4,9}/[-._;()/:A-Z0-9]+',  # с DOI:
        r'https?://doi\.org/10\.\d{4,9}/[-._;()/:A-Z0-9]+',  # https://doi.org
        r'https?://dx\.doi\.org/10\.\d{4,9}/[-._;()/:A-Z0-9]+'  # https://dx.doi.org
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi_raw = match.group(0)
            # Очистка от префиксов и точки в конце
            doi_raw = re.sub(r'^(doi:|DOI:|https?://doi\.org/|https?://dx\.doi\.org/)', '', doi_raw, flags=re.IGNORECASE)
            doi_raw = doi_raw.rstrip('.,;:')
            return doi_raw
    return None

# ======================== API ЗАПРОСЫ ========================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_crossref(doi: str) -> Optional[Dict]:
    """Запрос к Crossref API"""
    try:
        url = f"https://api.crossref.org/works/{doi}"
        headers = {
            'User-Agent': 'LiteratureAnalyzer/1.0 (mailto:your-email@example.com)'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['message']
        elif response.status_code == 404:
            return None
        else:
            st.warning(f"Crossref error for {doi}: {response.status_code}")
            return None
    except Exception as e:
        st.warning(f"Crossref request failed for {doi}: {str(e)}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_openalex(doi: str) -> Optional[Dict]:
    """Запрос к OpenAlex API"""
    try:
        url = f"https://api.openalex.org/works/doi/{doi}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            st.warning(f"OpenAlex error for {doi}: {response.status_code}")
            return None
    except Exception as e:
        st.warning(f"OpenAlex request failed for {doi}: {str(e)}")
        return None

# ======================== НОРМАЛИЗАЦИЯ АВТОРОВ ========================
def normalize_author_name(name: str, orcid: Optional[str] = None) -> str:
    """Нормализация имени автора для сравнения"""
    if not name:
        return ""
    
    # Убираем лишние пробелы
    name = name.strip()
    
    # Варианты: "E.V. Ramos-Fernandez" -> "Ramos-Fernandez E"
    # "Ramos-Fernandez, E.V." -> "Ramos-Fernandez E"
    
    # Если есть запятая
    if ',' in name:
        last, first = name.split(',', 1)
        last = last.strip()
        first = first.strip()
        # Берем первую букву имени
        if first:
            first_initial = first[0] if first[0].isalpha() else ''
        else:
            first_initial = ''
        return f"{last} {first_initial}".strip()
    else:
        # Формат "E.V. Ramos-Fernandez"
        parts = name.split()
        if len(parts) >= 2:
            last = parts[-1]
            first_initials = ''.join([p[0] for p in parts[:-1] if p and p[0].isalpha()])
            return f"{last} {first_initials}".strip()
        return name

def extract_authors_from_crossref(data: Dict) -> List[Tuple[str, Optional[str]]]:
    """Извлечение авторов и ORCID из Crossref"""
    authors = []
    if 'author' in data:
        for author in data['author']:
            given = author.get('given', '')
            family = author.get('family', '')
            orcid = author.get('ORCID', None)
            
            if family and given:
                # Берем первую букву имени
                first_initial = given[0] if given else ''
                name = f"{family} {first_initial}"
            elif family:
                name = family
            else:
                name = given
                
            authors.append((name, orcid))
    return authors

def extract_authors_from_openalex(data: Dict) -> List[Tuple[str, Optional[str]]]:
    """Извлечение авторов и ORCID из OpenAlex"""
    authors = []
    if 'authorships' in data:
        for authorship in data['authorships']:
            author = authorship.get('author', {})
            display_name = author.get('display_name', '')
            orcid = author.get('orcid', None)
            
            if display_name:
                authors.append((display_name, orcid))
    return authors

# ======================== АНАЛИЗ САМОЦИТИРОВАНИЙ ========================
def check_self_citation(author_name: str, paper_authors: Set[str], orcid_map: Dict[str, Set[str]]) -> bool:
    """Проверка является ли автор из списка одним из авторов статьи"""
    # Нормализуем имя
    normalized = normalize_author_name(author_name, None)
    
    # Проверяем по имени
    for paper_author in paper_authors:
        if normalized == normalize_author_name(paper_author, None):
            return True
    
    # Проверка по ORCID (если есть)
    # Это более сложная логика, упрощенно:
    if author_name in orcid_map:
        return True
    
    return False

# ======================== ОСНОВНАЯ ЛОГИКА АНАЛИЗА ========================
def parse_reference_list(references_text: str) -> List[str]:
    """Разбиение списка литературы на отдельные ссылки"""
    # Разбиваем по номерам (1., 2., и т.д.)
    lines = references_text.strip().split('\n')
    references = []
    current_ref = []
    
    for line in lines:
        # Если строка начинается с цифры и точки - новая ссылка
        if re.match(r'^\d+\.', line.strip()):
            if current_ref:
                references.append(' '.join(current_ref))
            current_ref = [line.strip()]
        else:
            if current_ref:
                current_ref.append(line.strip())
    
    if current_ref:
        references.append(' '.join(current_ref))
    
    return references

async def analyze_reference_batch(references: List[str], session, progress_bar, progress_start: int, progress_end: int) -> List[Dict]:
    """Асинхронный анализ батча ссылок"""
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
            'journal': None,
            'year': None,
            'type': None,
            'publisher': None,
            'crossmark_issues': [],
            'is_preprint': False,
            'has_erratum': False,
            'is_retracted': False
        }
        
        if doi:
            # Параллельные запросы к Crossref и OpenAlex
            crossref_task = asyncio.create_task(asyncio.to_thread(fetch_crossref, doi))
            openalex_task = asyncio.create_task(asyncio.to_thread(fetch_openalex, doi))
            
            crossref_data = await crossref_task
            openalex_data = await openalex_task
            
            if crossref_data:
                result['crossref_data'] = crossref_data
                result['crossref_status'] = True
                
                # Извлекаем метаданные из Crossref
                result['authors'].extend(extract_authors_from_crossref(crossref_data))
                
                if 'container-title' in crossref_data and crossref_data['container-title']:
                    result['journal'] = crossref_data['container-title'][0]
                
                if 'issued' in crossref_data and 'date-parts' in crossref_data['issued']:
                    date_parts = crossref_data['issued']['date-parts']
                    if date_parts and date_parts[0]:
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
                result['authors'].extend(extract_authors_from_openalex(openalex_data))
                
                # Проверка на препринт, ретракцию, эрратум
                if openalex_data.get('type') == 'posted_content':
                    result['is_preprint'] = True
                
                if openalex_data.get('is_retracted'):
                    result['is_retracted'] = True
                
                # Проверка на erratum через отношения
                if 'related_works' in openalex_data:
                    # Упрощенная проверка
                    pass
        
        results.append(result)
        
        # Обновляем прогресс
        progress = progress_start + int((idx + 1) / batch_size * (progress_end - progress_start))
        progress_bar.progress(progress / 100)
    
    return results

async def analyze_all_references(references: List[str], batch_size: int = 50) -> List[Dict]:
    """Анализ всех ссылок с батчированием"""
    all_results = []
    total_batches = (len(references) + batch_size - 1) // batch_size
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    async with aiohttp.ClientSession() as session:
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(references))
            batch = references[start_idx:end_idx]
            
            status_text.text(f"Анализ батча {batch_num + 1} из {total_batches} (ссылки {start_idx + 1}-{end_idx} из {len(references)})")
            
            progress_start = (batch_num * 100) // total_batches
            progress_end = ((batch_num + 1) * 100) // total_batches
            
            batch_results = await analyze_reference_batch(batch, session, progress_bar, progress_start, progress_end)
            all_results.extend(batch_results)
    
    status_text.text("Анализ завершен!")
    progress_bar.progress(100)
    
    return all_results

# ======================== СТАТИСТИЧЕСКИЙ АНАЛИЗ ========================
def generate_statistics(results: List[Dict], paper_authors: Optional[Set[str]] = None) -> Dict:
    """Генерация статистики по результатам анализа"""
    
    # 1. Статус DOI
    doi_status = {
        'both': 0,
        'crossref_only': 0,
        'openalex_only': 0,
        'none': 0
    }
    
    # 2. Частота авторов
    author_counter = Counter()
    author_orcid_map = defaultdict(set)
    
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
    
    # 8. Самоцитирования
    self_citations = []
    
    for result in results:
        # Статус DOI
        if result['crossref_status'] and result['openalex_status']:
            doi_status['both'] += 1
        elif result['crossref_status']:
            doi_status['crossref_only'] += 1
        elif result['openalex_status']:
            doi_status['openalex_only'] += 1
        else:
            doi_status['none'] += 1
        
        # Авторы (уникальные)
        unique_authors = set()
        for author_name, orcid in result['authors']:
            if author_name:
                normalized = normalize_author_name(author_name, orcid)
                if normalized not in unique_authors:
                    unique_authors.add(normalized)
                    author_counter[normalized] += 1
                    if orcid:
                        author_orcid_map[normalized].add(orcid)
        
        # Журнал
        if result['journal']:
            journal_counter[result['journal']] += 1
        
        # Тип
        if result['type']:
            type_counter[result['type']] += 1
        
        # Год
        if result['year'] and result['year'] > 1900 and result['year'] <= datetime.now().year:
            year_counter[result['year']] += 1
        
        # Издатель
        if result['publisher']:
            publisher_counter[result['publisher']] += 1
        
        # Проблемные ссылки
        has_problem = False
        problems = []
        
        if result['is_retracted']:
            problems.append('Ретрагирована')
            has_problem = True
        
        if result['has_erratum']:
            problems.append('Имеет Erratum')
            has_problem = True
        
        if result['is_preprint']:
            problems.append('Препринт')
            has_problem = True
        
        if result['crossmark_issues']:
            problems.extend(result['crossmark_issues'])
            has_problem = True
        
        if has_problem:
            problematic_refs.append({
                'text': result['original_text'][:200],
                'problems': ', '.join(problems)
            })
        
        # Самоцитирования
        if paper_authors:
            for author_name, _ in result['authors']:
                if check_self_citation(author_name, paper_authors, author_orcid_map):
                    self_citations.append(result)
                    break
    
    # Дедупликация авторов с ORCID
    authors_with_orcid = []
    for author, count in author_counter.most_common(50):
        orcid_info = ''
        if author in author_orcid_map and author_orcid_map[author]:
            orcid_info = f" (ORCID: {', '.join(author_orcid_map[author])})"
        authors_with_orcid.append(f"{author}{orcid_info} - {count}")
    
    return {
        'total_references': len(results),
        'doi_status': doi_status,
        'top_authors': authors_with_orcid[:15],
        'top_journals': [f"{journal} - {count}" for journal, count in journal_counter.most_common(15)],
        'top_types': [f"{type_name} - {count}" for type_name, count in type_counter.most_common()],
        'year_distribution': dict(sorted(year_counter.items())),
        'years_last_5': sum(count for year, count in year_counter.items() if year >= datetime.now().year - 5),
        'top_publishers': [f"{publisher} - {count}" for publisher, count in publisher_counter.most_common(10)],
        'problematic_refs': problematic_refs[:20],
        'self_citations_count': len(self_citations),
        'self_citations_percent': (len(self_citations) / len(results) * 100) if results else 0,
        'unique_doi_percent': ((doi_status['both'] + doi_status['crossref_only'] + doi_status['openalex_only']) / len(results) * 100) if results else 0,
        'duplicate_rate': 0  # Упрощенно
    }

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
            placeholder="E.V. Ramos-Fernandez\nJung HS\nZhang Wei",
            help="Укажите авторов в любом формате. Программа нормализует имена для поиска совпадений"
        )
        
        paper_authors = set()
        if authors_input:
            for line in authors_input.strip().split('\n'):
                if line.strip():
                    paper_authors.add(line.strip())
        
        st.markdown("---")
        st.info("💡 **Совет**: Для больших списков (более 500 ссылок) процесс может занять несколько минут. Рекомендуется использовать батчи по 50-100 ссылок.")
    
    # Основная область
    tab1, tab2 = st.tabs(["📥 Загрузка данных", "📊 Результаты анализа"])
    
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
                st.success(f"Файл загружен, размер: {len(references_text)} символов")
        
        if st.button("🚀 Начать анализ", type="primary", disabled=not references_text.strip()):
            if references_text.strip():
                # Парсим список
                with st.spinner("Парсинг списка литературы..."):
                    references = parse_reference_list(references_text)
                    st.info(f"Найдено {len(references)} ссылок")
                
                if len(references) > 2000:
                    st.error(f"Превышен лимит в 2000 ссылок. Найдено {len(references)} ссылок. Пожалуйста, уменьшите количество.")
                else:
                    # Сохраняем в session_state
                    st.session_state['references'] = references
                    st.session_state['paper_authors'] = paper_authors
                    st.session_state['batch_size'] = batch_size
                    st.session_state['analysis_started'] = True
                    
                    # Запускаем анализ
                    with st.spinner("Анализ ссылок..."):
                        results = asyncio.run(analyze_all_references(references, batch_size))
                        st.session_state['results'] = results
                        st.session_state['analysis_complete'] = True
                    
                    st.success("✅ Анализ завершен! Перейдите на вкладку 'Результаты анализа'")
            else:
                st.warning("Пожалуйста, введите список литературы")
    
    with tab2:
        if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
            results = st.session_state['results']
            paper_authors = st.session_state.get('paper_authors', set())
            
            # Генерируем статистику
            with st.spinner("Генерация статистики..."):
                stats = generate_statistics(results, paper_authors if paper_authors else None)
            
            # Общая статистика
            st.header("📈 Общая статистика")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Всего ссылок", stats['total_references'])
            with col2:
                st.metric("Уникальных DOI", f"{stats['unique_doi_percent']:.1f}%")
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
                for author in stats['top_authors'][:10]:
                    st.write(f"• {author}")
            else:
                st.info("Нет данных об авторах")
            
            # Топ журналов
            st.subheader("📖 Топ журналов")
            if stats['top_journals']:
                for journal in stats['top_journals'][:10]:
                    st.write(f"• {journal}")
            else:
                st.info("Нет данных о журналах")
            
            # Типология
            st.subheader("📚 Типология источников")
            if stats['top_types']:
                for type_name in stats['top_types']:
                    st.write(f"• {type_name}")
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
                    st.write(f"• {publisher}")
            else:
                st.info("Нет данных об издателях")
            
            # Проблемные ссылки
            if stats['problematic_refs']:
                st.subheader("⚠️ Проблемные ссылки")
                for ref in stats['problematic_refs'][:10]:
                    with st.expander(f"Проблема: {ref['problems']}"):
                        st.text(ref['text'])
            
            # Экспорт
            st.subheader("💾 Экспорт результатов")
            if st.button("Экспортировать в CSV"):
                # Подготовка данных для экспорта
                export_data = []
                for result in results:
                    export_data.append({
                        'DOI': result['doi'],
                        'Crossref': 'Да' if result['crossref_status'] else 'Нет',
                        'OpenAlex': 'Да' if result['openalex_status'] else 'Нет',
                        'Журнал': result['journal'],
                        'Год': result['year'],
                        'Тип': result['type'],
                        'Издатель': result['publisher'],
                        'Препринт': 'Да' if result['is_preprint'] else 'Нет',
                        'Ретрагирована': 'Да' if result['is_retracted'] else 'Нет',
                        'Оригинальный текст': result['original_text'][:500]
                    })
                
                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                
                st.download_button(
                    label="📥 Скачать CSV",
                    data=csv,
                    file_name=f"literature_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("👈 Пожалуйста, загрузите список литературы на вкладке 'Загрузка данных' и нажмите 'Начать анализ'")

if __name__ == "__main__":
    main()
