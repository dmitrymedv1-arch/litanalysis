import streamlit as st
import pandas as pd
import re
import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import difflib
import math
from collections import defaultdict
from itertools import combinations
import html  # Добавлено для экранирования HTML

# Try to import additional libraries for new features
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    LANG_DETECT_AVAILABLE = True
except ImportError:
    LANG_DETECT_AVAILABLE = False

# ======================== LOCALIZATION DICTIONARY ========================
TEXTS = {
    'en': {
        # General UI
        'app_title': "Comprehensive Reference List Analysis",
        'app_subtitle': "Enhanced version with Crossref + OpenAlex analytics",
        'settings': "⚙️ Settings",
        'batch_size': "Batch size",
        'batch_size_help': "Number of references processed at once",
        'paper_authors': "👥 Paper authors (optional)",
        'paper_authors_help': "For self-citation analysis",
        'format_hint': "**Format:** `FirstInitial LastName` (e.g., `N. Fukatsu`, `N Fukatsu`, `Z. Wei`)",
        'separator_hint': "**Separators:** comma, tab, or new line",
        'authors_placeholder': "N. Fukatsu\nZ. Wei\nJ. Smith\nor\nN. Fukatsu, Z. Wei, J. Smith",
        'authors_added': "✅ Added {} authors",
        'authors_warning': "⚠️ No valid authors added. Please use format: N. Fukatsu or N Fukatsu",
        'language': "🌐 Language",
        'language_english': "English",
        'language_russian': "Russian",
        'journal_name_label': "📝 Journal name (optional)",
        'journal_name_help': "If not specified, 'Chimica Techno Acta' will be used",
        'article_number_label': "🔢 Article number (optional)",
        'article_number_help': "Example: 1224, CTA-1234, CTA/1224",
        
        # Tabs
        'tab_upload': "📥 Data Upload",
        'tab_analytics': "📊 Enhanced Analytics",
        'tab_report': "📄 HTML Report",
        
        # Upload tab
        'upload_header': "Literature Reference Upload",
        'input_method': "Select input method",
        'text_paste': "Text paste",
        'file_upload': "File upload (.txt)",
        'paste_placeholder': "1. Jung HS, Kim BG, Kwon JH, Bae JW. Thermocatalytic technologies...\n2. Liew WM, Ainirazali N. Cutting-edge innovations...",
        'upload_success': "✅ File uploaded, size: {} characters",
        'start_analysis': "🚀 Start Enhanced Analysis",
        'parsing': "📖 Parsing reference list...",
        'found_refs': "📄 Found {} references",
        'preview': "🔍 Preview first 3 references",
        'searching_duplicates': "🔍 Searching for duplicates...",
        'found_duplicates': "⚠️ Found {} potential duplicates",
        'view_duplicates': "View duplicates",
        'reason': "Reason",
        'analysis_started': "🔄 Enhanced reference analysis (this may take several minutes)...",
        'analysis_complete': "✅ Analysis complete! Found DOI: {} out of {} references",
        'go_to_analytics': "👈 Go to 'Enhanced Analytics' tab for detailed results",
        'enter_reference_list': "⚠️ Please enter a reference list",
        'limit_exceeded': "❌ Limit of 2000 references exceeded. Found {} references.",
        
        # Analytics tab - metrics
        'total_references': "📄 Total references",
        'doi_found': "🔗 DOI found",
        'last_5_years': "📅 References (last 5 years)",
        'self_citations': "🔄 Self-citations",
        'total_citations': "📊 Total citations",
        'avg_citations': "⭐ Average citations",
        'orcid_coverage': "🎯 ORCID coverage",
        'unique_publishers': "🏢 Unique publishers",
        
        # Analytics tab - sections
        'analysis_sections': "📑 Analysis Sections",
        'doi_status': "🔍 DOI Status",
        'citation_metrics': "📊 Citation Metrics",
        'identifier_coverage': "🔍 Identifier Coverage Analysis",
        'top_authors': "👨‍🎓 Top Authors (with intelligent merging)",
        'all_journals': "📖 All Journals (sorted by frequency)",
        'all_publishers': "🏢 All Publishers (sorted by frequency)",
        'yearly_stats': "📅 Yearly Statistics",
        'recent_years_summary': "Recent years summary",
        'distribution_by_year': "Distribution by year",
        'detailed_yearly_data': "Detailed yearly data",
        'key_concepts': "🧠 Key Scientific Concepts",
        'geographic_distribution': "🌍 Geographic Distribution",
        'collaboration_networks': "🤝 Collaboration Networks",
        'top_author_pairs': "Top author pairs",
        'core_authors': "Core authors",
        'diversity_analysis': "🔄 Diversity Analysis",
        'citation_classics': "⭐ Citation Classics",
        'crossref_only': "⚠️ References with Only Crossref (OpenAlex missing)",
        'openalex_only': "⚠️ References with Only OpenAlex (Crossref missing)",
        'suspicious_dois': "🔍 Suspicious DOIs (Not found in any database)",
        'suspicious_dois_hint': "These DOIs were extracted from references but returned no data from Crossref or OpenAlex. May be invalid, typo, or AI-generated.",
        'non_doi_sources': "📄 Non-DOI Sources (Books, Theses, Conference Papers, etc.)",
        'url_sources': "🔗 URL Sources (Web links without DOI)",
        'problematic_refs': "⚠️ Problematic References",
        'predatory_journals': "🚨 Potentially Predatory Journals",
        'full_reference_list': "📋 Full Reference List with Filters",
        'showing': "Showing {} of {} references",
        'showing_first': "Showing first {} of {} references",
        
        # Filters
        'only_with_doi': "Only with DOI",
        'only_non_doi': "Only non-DOI",
        'url_links': "URL-links",
        'only_crossref': "Only Crossref",
        'only_openalex': "Only OpenAlex",
        'problematic_only': "⚠️ Problematic only",
        'self_cited_only': "🔄 Self-cited only",
        'search_in_text': "Search in text",
        'search_placeholder': "Enter keyword...",
        
        # Reference display
        'not_found': "Not found",
        'status': "Status",
        'journal': "Journal",
        'year': "Year",
        'authors': "Authors",
        'citations': "Citations",
        'issues': "Issues",
        'full_text': "Full text",
        'retracted': "Retracted",
        'preprint': "Preprint",
        'self_citation': "Self-citation",
        'suspicious_doi_badge': "⚠️ Suspicious DOI",
        
        # Statistics strings
        'status_both': "Crossref + OpenAlex",
        'status_crossref_only': "Only Crossref",
        'status_openalex_only': "Only OpenAlex",
        'status_none': "No data",
        'references_with_known_year': "References with known year",
        'references_with_unknown_year': "References with unknown year",
        'last_3_years': "Last 3 years",
        'last_5_years_metric': "Last 5 years",
        'last_10_years': "Last 10 years",
        'unique_authors': "Unique authors",
        'unique_journals': "Unique journals",
        'unique_publishers_metric': "Unique publishers",
        'shannon_authors': "Authors Shannon index",
        'shannon_journals': "Journals Shannon index",
        'shannon_publishers': "Publishers Shannon index",
        'total_countries': "Total countries",
        'international_collaboration': "International collaboration",
        'no_citation_classics': "No citation classics detected",
        'no_crossref_only': "✅ No references with only Crossref data",
        'no_openalex_only': "✅ No references with only OpenAlex data",
        'no_suspicious_dois': "✅ No suspicious DOIs detected",
        'all_have_doi': "✅ All references have DOI identifiers",
        'no_url_only': "✅ No URL-only references found",
        'no_problematic': "✅ No problematic references detected",
        'none_detected': "None detected",
        
        # Export
        'export_report': "📄 Export Enhanced Report",
        'download_html': "💾 Download HTML Report (Expert Edition)",
        'text_export': "📋 Text Export",
        'copy_to_clipboard': "📋 Copy to clipboard",
        'copied': "✅ Data copied! (use Ctrl+C)",
        'run_analysis_first': "👈 Please run analysis in 'Data Upload' tab first",
        'upload_first': "👈 Please upload a reference list in the 'Data Upload' tab and click 'Start Enhanced Analysis'",
        
        # HTML Report
        'html_overview': "📈 Overview",
        'html_identifier_coverage': "🔍 Identifier Coverage",
        'html_authors': "👨‍🎓 Authors",
        'html_journals': "📖 Journals",
        'html_publishers': "🏢 Publishers",
        'html_yearly': "📅 Yearly Statistics",
        'html_concepts': "🧠 Concepts",
        'html_geography': "🌍 Geography",
        'html_collaborations': "🤝 Collaborations",
        'html_diversity': "🔄 Diversity",
        'html_classics': "⭐ Citation Classics",
        'html_self_citations': "📝 Self-Citations",
        'html_crossref_only': "⚠️ Only Crossref",
        'html_openalex_only': "⚠️ Only OpenAlex",
        'html_suspicious_doi': "🔍 Suspicious DOIs",
        'html_non_doi': "📄 Non-DOI Sources",
        'html_url_sources': "🔗 URL Sources",
        'html_problems': "⚠️ Problems",
        'html_generated': "Generated",
        'html_footer': "",
        'html_copyright': "© Comprehensive Reference List Analysis / Created by daM / Chimica Techno Acta https://chimicatechnoacta.ru",
        'html_rank': "Rank",
        'html_count': "Count",
        'html_percentage': "Percentage",
        'html_citations_count': "citations",
        'html_frequency': "Frequency",
        'html_authors_count': "authors",
        'html_connections': "connections",
        'html_joint_works': "joint works",
        'html_citations_label': "citations",
        'html_total_self_citations': "Total self-citations",
        'html_attention': "⚠️ Attention: invalid/suspicious DOI",
        'html_not_found': "Not found",
        'html_works': "works",
        'html_journal_label': "Journal",
        'html_article_number_label': "Article number",
        'html_self_citation_authors_label': "Paper authors for self-citation analysis",
        
        # Additional UI
        'authors_warning_text': "Author name format not recognized: '{}'. Expected format: 'N. Fukatsu' or 'N Fukatsu'",
        'with_orcid': "With ORCID",
        'unique_concepts': "Unique concepts",
        'median_age': "Median age",
        'average_age': "Average age",
        'core_authors_label': "Core authors",
        'orcid_label': "ORCID",
        'institution_label': "Institution",
        'country_label': "Country",
        'yearly_distribution': "Distribution by year (from newest to oldest):",
        'cumulative_percentage': "Cumulative percentage:",
        'references_count': "references",
        'percent_sign': "%",
        'cumulative': "cumulative",
    },
    'ru': {
        # General UI
        'app_title': "Комплексный анализ списка литературы",
        'app_subtitle': "Расширенная версия с аналитикой Crossref + OpenAlex",
        'settings': "⚙️ Настройки",
        'batch_size': "Размер пакета",
        'batch_size_help': "Количество ссылок, обрабатываемых за раз",
        'paper_authors': "👥 Авторы статьи (опционально)",
        'paper_authors_help': "Для анализа самоцитирования",
        'format_hint': "**Формат:** `Инициал Фамилия` (например, `Н. Фукацу`, `Н Фукацу`, `З. Вэй`)",
        'separator_hint': "**Разделители:** запятая, табуляция или новая строка",
        'authors_placeholder': "Н. Фукацу\nЗ. Вэй\nД. Смит\nили\nН. Фукацу, З. Вэй, Д. Смит",
        'authors_added': "✅ Добавлено {} авторов",
        'authors_warning': "⚠️ Не добавлено ни одного корректного автора. Используйте формат: Н. Фукацу или Н Фукацу",
        'language': "🌐 Язык",
        'language_english': "Английский",
        'language_russian': "Русский",
        'journal_name_label': "📝 Название журнала (опционально)",
        'journal_name_help': "Если не указано, будет использовано 'Chimica Techno Acta'",
        'article_number_label': "🔢 Номер статьи (опционально)",
        'article_number_help': "Пример: 1224, CTA-1234, CTA/1224",
        
        # Tabs
        'tab_upload': "📥 Загрузка данных",
        'tab_analytics': "📊 Расширенная аналитика",
        'tab_report': "📄 HTML отчет",
        
        # Upload tab
        'upload_header': "Загрузка списка литературы",
        'input_method': "Выберите способ ввода",
        'text_paste': "Вставка текста",
        'file_upload': "Загрузка файла (.txt)",
        'paste_placeholder': "1. Иванов ИИ, Петров ПП. Новые технологии...\n2. Сидоров АБ. Инновации в науке...",
        'upload_success': "✅ Файл загружен, размер: {} символов",
        'start_analysis': "🚀 Запустить расширенный анализ",
        'parsing': "📖 Разбор списка литературы...",
        'found_refs': "📄 Найдено {} ссылок",
        'preview': "🔍 Предпросмотр первых 3 ссылок",
        'searching_duplicates': "🔍 Поиск дубликатов...",
        'found_duplicates': "⚠️ Найдено {} потенциальных дубликатов",
        'view_duplicates': "Показать дубликаты",
        'reason': "Причина",
        'analysis_started': "🔄 Выполняется расширенный анализ ссылок (это может занять несколько минут)...",
        'analysis_complete': "✅ Анализ завершен! Найдено DOI: {} из {} ссылок",
        'go_to_analytics': "👈 Перейдите на вкладку 'Расширенная аналитика' для просмотра результатов",
        'enter_reference_list': "⚠️ Пожалуйста, введите список литературы",
        'limit_exceeded': "❌ Превышен лимит в 2000 ссылок. Найдено {} ссылок.",
        
        # Analytics tab - metrics
        'total_references': "📄 Всего ссылок",
        'doi_found': "🔗 Найдено DOI",
        'last_5_years': "📅 Ссылок (последние 5 лет)",
        'self_citations': "🔄 Самоцитирований",
        'total_citations': "📊 Всего цитирований",
        'avg_citations': "⭐ Среднее цитирований",
        'orcid_coverage': "🎯 Покрытие ORCID",
        'unique_publishers': "🏢 Уникальных издательств",
        
        # Analytics tab - sections
        'analysis_sections': "📑 Разделы анализа",
        'doi_status': "🔍 Статус DOI",
        'citation_metrics': "📊 Метрики цитирований",
        'identifier_coverage': "🔍 Анализ покрытия идентификаторами",
        'top_authors': "👨‍🎓 Топ авторов (с интеллектуальным объединением)",
        'all_journals': "📖 Все журналы (по частоте)",
        'all_publishers': "🏢 Все издательства (по частоте)",
        'yearly_stats': "📅 Годовая статистика",
        'recent_years_summary': "Сводка за последние годы",
        'distribution_by_year': "Распределение по годам",
        'detailed_yearly_data': "Детальные данные по годам",
        'key_concepts': "🧠 Ключевые концепции",
        'geographic_distribution': "🌍 Географическое распределение",
        'collaboration_networks': "🤝 Сети сотрудничества",
        'top_author_pairs': "Топ пар авторов",
        'core_authors': "Ядерные авторы",
        'diversity_analysis': "🔄 Анализ разнообразия",
        'citation_classics': "⭐ Классики цитирования",
        'crossref_only': "⚠️ Ссылки только с Crossref (нет в OpenAlex)",
        'openalex_only': "⚠️ Ссылки только с OpenAlex (нет в Crossref)",
        'suspicious_dois': "🔍 Подозрительные DOI (не найдены ни в одной базе)",
        'suspicious_dois_hint': "Эти DOI были извлечены из ссылок, но не вернули данных из Crossref или OpenAlex. Возможно, недействительны, содержат опечатку или сгенерированы ИИ.",
        'non_doi_sources': "📄 Источники без DOI (книги, диссертации, материалы конференций и т.д.)",
        'url_sources': "🔗 Источники с URL (веб-ссылки без DOI)",
        'problematic_refs': "⚠️ Проблемные ссылки",
        'predatory_journals': "🚨 Потенциально хищнические журналы",
        'full_reference_list': "📋 Полный список литературы с фильтрами",
        'showing': "Показано {} из {} ссылок",
        'showing_first': "Показаны первые {} из {} ссылок",
        
        # Filters
        'only_with_doi': "Только с DOI",
        'only_non_doi': "Только без DOI",
        'url_links': "Только URL-ссылки",
        'only_crossref': "Только Crossref",
        'only_openalex': "Только OpenAlex",
        'problematic_only': "⚠️ Только проблемные",
        'self_cited_only': "🔄 Только самоцитирования",
        'search_in_text': "Поиск в тексте",
        'search_placeholder': "Введите ключевое слово...",
        
        # Reference display
        'not_found': "Не найдено",
        'status': "Статус",
        'journal': "Журнал",
        'year': "Год",
        'authors': "Авторы",
        'citations': "Цитирований",
        'issues': "Проблемы",
        'full_text': "Полный текст",
        'retracted': "Отозвана",
        'preprint': "Препринт",
        'self_citation': "Самоцитирование",
        'suspicious_doi_badge': "⚠️ Подозрительный DOI",
        
        # Statistics strings
        'status_both': "Crossref + OpenAlex",
        'status_crossref_only': "Только Crossref",
        'status_openalex_only': "Только OpenAlex",
        'status_none': "Нет данных",
        'references_with_known_year': "Ссылок с известным годом",
        'references_with_unknown_year': "Ссылок с неизвестным годом",
        'last_3_years': "Последние 3 года",
        'last_5_years_metric': "Последние 5 лет",
        'last_10_years': "Последние 10 лет",
        'unique_authors': "Уникальных авторов",
        'unique_journals': "Уникальных журналов",
        'unique_publishers_metric': "Уникальных издательств",
        'shannon_authors': "Индекс Шеннона (авторы)",
        'shannon_journals': "Индекс Шеннона (журналы)",
        'shannon_publishers': "Индекс Шеннона (издательства)",
        'total_countries': "Всего стран",
        'international_collaboration': "Международное сотрудничество",
        'no_citation_classics': "Классики цитирования не обнаружены",
        'no_crossref_only': "✅ Нет ссылок только с Crossref",
        'no_openalex_only': "✅ Нет ссылок только с OpenAlex",
        'no_suspicious_dois': "✅ Подозрительных DOI не обнаружено",
        'all_have_doi': "✅ Все ссылки имеют DOI",
        'no_url_only': "✅ Ссылок только с URL не найдено",
        'no_problematic': "✅ Проблемных ссылок не обнаружено",
        'none_detected': "Не обнаружено",
        
        # Export
        'export_report': "📄 Экспорт расширенного отчета",
        'download_html': "💾 Скачать HTML отчет (Expert Edition)",
        'text_export': "📋 Текстовый экспорт",
        'copy_to_clipboard': "📋 Копировать в буфер",
        'copied': "✅ Данные скопированы! (используйте Ctrl+C)",
        'run_analysis_first': "👈 Сначала запустите анализ на вкладке 'Загрузка данных'",
        'upload_first': "👈 Загрузите список литературы на вкладке 'Загрузка данных' и нажмите 'Запустить расширенный анализ'",
        
        # HTML Report
        'html_overview': "📈 Обзор",
        'html_identifier_coverage': "🔍 Покрытие идентификаторами",
        'html_authors': "👨‍🎓 Авторы",
        'html_journals': "📖 Журналы",
        'html_publishers': "🏢 Издательства",
        'html_yearly': "📅 Годовая статистика",
        'html_concepts': "🧠 Концепции",
        'html_geography': "🌍 География",
        'html_collaborations': "🤝 Сотрудничество",
        'html_diversity': "🔄 Разнообразие",
        'html_classics': "⭐ Классики цитирования",
        'html_self_citations': "📝 Самоцитирования",
        'html_crossref_only': "⚠️ Только Crossref",
        'html_openalex_only': "⚠️ Только OpenAlex",
        'html_suspicious_doi': "🔍 Подозрительные DOI",
        'html_non_doi': "📄 Источники без DOI",
        'html_url_sources': "🔗 URL-источники",
        'html_problems': "⚠️ Проблемы",
        'html_generated': "Сгенерирован",
        'html_footer': "",
        'html_copyright': "© Comprehensive Reference List Analysis / Created by daM / Chimica Techno Acta https://chimicatechnoacta.ru",
        'html_rank': "Ранг",
        'html_count': "Количество",
        'html_percentage': "Процент",
        'html_citations_count': "цитирований",
        'html_frequency': "Частота",
        'html_authors_count': "авторов",
        'html_connections': "связей",
        'html_joint_works': "совместных работ",
        'html_citations_label': "цитирований",
        'html_total_self_citations': "Всего самоцитирований",
        'html_attention': "⚠️ Внимание: недействительный/подозрительный DOI",
        'html_not_found': "Не найден",
        'html_works': "работ",
        'html_journal_label': "Журнал",
        'html_article_number_label': "Номер статьи",
        'html_self_citation_authors_label': "Авторы статьи для анализа самоцитирований",
        
        # Additional UI
        'authors_warning_text': "Формат имени автора не распознан: '{}'. Ожидаемый формат: 'Н. Фукацу' или 'Н Фукацу'",
        'with_orcid': "С ORCID",
        'unique_concepts': "Уникальных концепций",
        'median_age': "Медианный возраст",
        'average_age': "Средний возраст",
        'core_authors_label': "Ядерные авторы",
        'orcid_label': "ORCID",
        'institution_label': "Учреждение",
        'country_label': "Страна",
        'yearly_distribution': "Распределение по годам (от новых к старым):",
        'cumulative_percentage': "Накопленный процент:",
        'references_count': "ссылок",
        'percent_sign': "%",
        'cumulative': "накоплено",
    }
}

def get_text(key: str) -> str:
    """Get localized text by key"""
    lang = st.session_state.get('language', 'en')
    return TEXTS[lang].get(key, TEXTS['en'].get(key, key))

# Page configuration
st.set_page_config(
    page_title="Comprehensive Reference List Analysis",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize language in session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
    
# Initialize bad DOIs cache in session state
if 'bad_dois' not in st.session_state:
    st.session_state.bad_dois = set()

# Initialize journal and article number in session state
if 'journal_name' not in st.session_state:
    st.session_state.journal_name = ''
if 'article_number' not in st.session_state:
    st.session_state.article_number = ''

# ======================== COLORED PROGRESS BAR ========================
def update_colored_progress(progress_percent: float, success_rate: float = None, data_density: float = None):
    """
    Update progress bar with color based on:
    - progress_percent: 0-100 completion percentage
    - success_rate: 0-1 ratio of successful API responses (optional)
    - data_density: 0-1 ratio of found DOIs to total references (optional)
    """
    
    # Determine color based on multiple factors
    if success_rate is not None:
        # Color by API success rate (better metric)
        if success_rate >= 0.8:
            color = "#00CC96"  # Rich green - excellent
        elif success_rate >= 0.6:
            color = "#FFA042"  # Orange - good
        elif success_rate >= 0.4:
            color = "#FF6B6B"  # Coral - moderate
        elif success_rate >= 0.2:
            color = "#FF4444"  # Red - poor
        else:
            color = "#CC0000"  # Dark red - critical
    elif data_density is not None:
        # Color by data density (how many DOIs found)
        if data_density >= 0.9:
            color = "#00CC96"  # Green - dense data
        elif data_density >= 0.7:
            color = "#00B5F1"  # Blue - good data
        elif data_density >= 0.5:
            color = "#FFA042"  # Orange - moderate
        elif data_density >= 0.3:
            color = "#FF6B6B"  # Coral - sparse
        else:
            color = "#FF4444"  # Red - very sparse
    else:
        # Default: gradient from green to red based on progress
        if progress_percent < 30:
            # Green to yellow-green
            r = int(0 + (255 * progress_percent / 30))
            g = 255
            b = int(100 - (100 * progress_percent / 30))
        elif progress_percent < 70:
            # Yellow to orange
            r = 255
            g = int(255 - (255 * (progress_percent - 30) / 40))
            b = 0
        else:
            # Orange to red
            r = 255
            g = int(100 - (100 * (progress_percent - 70) / 30))
            b = 0
        color = f"rgb({r}, {g}, {b})"
    
    # Create custom HTML/CSS for colored progress bar
    progress_html = f"""
    <style>
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    .colored-progress-container {{
        width: 100%;
        background-color: #f0f0f0;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        margin: 10px 0;
    }}
    
    .colored-progress-bar {{
        width: {progress_percent}%;
        height: 28px;
        background: linear-gradient(90deg, 
            {color} 0%, 
            {color}CC 50%,
            {color} 100%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite linear;
        border-radius: 20px;
        transition: width 0.5s ease-in-out;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-shadow: 0 0 2px rgba(0,0,0,0.5);
    }}
    
    .colored-progress-bar::after {{
        content: "{progress_percent:.1f}%";
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        white-space: nowrap;
    }}
    
    .progress-stats {{
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #666;
        margin-top: 5px;
    }}
    
    .progress-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }}
    
    .badge-green {{ background: #d4edda; color: #155724; }}
    .badge-blue {{ background: #d1ecf1; color: #0c5460; }}
    .badge-orange {{ background: #fff3cd; color: #856404; }}
    .badge-red {{ background: #f8d7da; color: #721c24; }}
    </style>
    
    <div class="colored-progress-container">
        <div class="colored-progress-bar"></div>
    </div>
    """
    
    return progress_html

def get_progress_color_by_metrics(doi_found_count: int, total_refs: int, api_success_count: int = None) -> Tuple[str, str, str]:
    """
    Determine color and badge text based on actual data metrics
    Returns: (color_hex, badge_text, badge_class)
    """
    data_density = doi_found_count / total_refs if total_refs > 0 else 0
    
    if api_success_count is not None:
        api_success_rate = api_success_count / total_refs if total_refs > 0 else 0
        if api_success_rate >= 0.8 and data_density >= 0.8:
            return "#00CC96", "🚀 Excellent data quality", "badge-green"
        elif api_success_rate >= 0.6:
            return "#00B5F1", "📊 Good API response rate", "badge-blue"
        elif api_success_rate >= 0.4:
            return "#FFA042", "⚠️ Moderate data quality", "badge-orange"
        else:
            return "#FF4444", "❌ Low API success rate", "badge-red"
    else:
        if data_density >= 0.8:
            return "#00CC96", "✅ High DOI coverage", "badge-green"
        elif data_density >= 0.6:
            return "#00B5F1", "📈 Good DOI coverage", "badge-blue"
        elif data_density >= 0.4:
            return "#FFA042", "⚠️ Moderate DOI coverage", "badge-orange"
        elif data_density >= 0.2:
            return "#FF6B6B", "⚠️ Low DOI coverage", "badge-red"
        else:
            return "#CC0000", "❌ Very low DOI coverage", "badge-red"

# ======================== ENHANCED CSS DESIGN ========================
st.markdown("""
<style>
    /* Main styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Metric cards */
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
    
    /* Progress bars for top lists */
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
    
    /* Status badges */
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
    
    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-weight: 600;
    }
    
    /* Responsive grids */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    /* Custom tabs */
    .custom-tab {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Custom tab buttons */
    .custom-tab-button {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        border: none;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .custom-tab-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }
    .custom-tab-button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .custom-tab-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }
    .custom-tab-title {
        font-weight: 600;
        font-size: 14px;
    }
    .custom-tab-subtitle {
        font-size: 11px;
        opacity: 0.8;
        margin-top: 4px;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Filters and tables */
    .dataframe-container {
        background: white;
        border-radius: 10px;
        padding: 15px;
        overflow-x: auto;
    }
    
    /* Concept cards */
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
    
    /* Clickable links */
    .clickable-link {
        color: #667eea;
        text-decoration: none;
        transition: all 0.3s;
    }
    .clickable-link:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    /* Disabled filter styling */
    .disabled-filter {
        opacity: 0.5;
        pointer-events: none;
    }
    
    /* Full text container with scroll */
    .full-text-container {
        max-height: 150px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: monospace;
        font-size: 12px;
        background: #f5f5f5;
        padding: 8px;
        border-radius: 5px;
        margin-top: 5px;
    }
    
    /* Self-citation highlight */
    .self-citation-author {
        color: #d9534f;
        font-weight: bold;
        background-color: #f8d7da;
        padding: 2px 4px;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# ======================== OPTIMIZED API REQUESTS ========================
@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
def fetch_crossref(doi: str) -> Optional[Dict]:
    """Request to Crossref API - OPTIMIZED with faster retry"""
    try:
        encoded_doi = requests.utils.quote(doi)
        url = f"https://api.crossref.org/works/{encoded_doi}"
        headers = {'User-Agent': 'LiteratureAnalyzer/2.0 (mailto:analyzer@example.com)'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()['message']
        elif response.status_code in [429, 500, 502, 503, 504]:
            return None
        else:
            st.session_state.bad_dois.add(doi)
            return None
    except:
        return None

@retry(stop=stop_after_attempt(2), wait=wait_random(min=0.5, max=1.5))
def fetch_openalex(doi: str) -> Optional[Dict]:
    """Request to OpenAlex API - OPTIMIZED with faster retry"""
    try:
        encoded_doi = requests.utils.quote(doi)
        url = f"https://api.openalex.org/works/doi/{encoded_doi}"
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_openalex_concepts(work_id: str) -> List[Dict]:
    """Extract concepts from OpenAlex"""
    try:
        url = f"https://api.openalex.org/works/{work_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('concepts', [])
    except:
        pass
    return []

# ======================== OPTIMIZED BATCH PROCESSING ========================
def analyze_reference_batch_optimized(references: List[str], progress_callback=None, paper_authors: Set[str] = None, batch_num: int = 0, total_batches: int = 1) -> List[Dict]:
    """Analyze batch of references using optimized ThreadPoolExecutor with full OpenAlex support for journals and publishers"""
    results = []
    batch_size = len(references)
    
    # Step 1: Extract all DOIs with their indices
    dois_with_indices = []
    ref_doi_map = {}
    for idx, ref in enumerate(references):
        identifiers = extract_identifiers(ref)
        doi = identifiers['doi']
        ref_doi_map[idx] = {'doi': doi, 'identifiers': identifiers}
        if doi:
            dois_with_indices.append((idx, doi))
    
    # Step 2: Fetch data using ThreadPoolExecutor (optimized approach)
    crossref_results = {}
    openalex_results = {}
    
    if dois_with_indices:
        # OPTIMIZATION 1: Single global ThreadPoolExecutor for all DOIs in batch
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {}
            for idx, doi in dois_with_indices:
                # Check if DOI is in bad cache
                if doi in st.session_state.bad_dois:
                    futures[(idx, 'crossref')] = None
                    futures[(idx, 'openalex')] = None
                else:
                    futures[(idx, 'crossref')] = executor.submit(fetch_crossref, doi)
                    futures[(idx, 'openalex')] = executor.submit(fetch_openalex, doi)
            
            # Collect results
            for (idx, api_type), future in futures.items():
                if future is not None:
                    try:
                        result = future.result(timeout=15)
                        if api_type == 'crossref':
                            crossref_results[idx] = result
                        else:
                            openalex_results[idx] = result
                    except Exception:
                        if api_type == 'crossref':
                            crossref_results[idx] = None
                        else:
                            openalex_results[idx] = None
                else:
                    if api_type == 'crossref':
                        crossref_results[idx] = None
                    else:
                        openalex_results[idx] = None
            
            # Mark bad DOIs for caching
            for idx, doi in dois_with_indices:
                if crossref_results.get(idx) is None and openalex_results.get(idx) is None:
                    st.session_state.bad_dois.add(doi)
    
    # Step 3: Build results for each reference
    for idx, ref in enumerate(references):
        identifiers = ref_doi_map[idx]
        doi = identifiers['doi']
        
        # Get fetched data (if any)
        crossref_data = crossref_results.get(idx) if dois_with_indices else None
        openalex_data = openalex_results.get(idx) if dois_with_indices else None
        
        result = {
            'original_text': ref,
            'doi': doi,
            'identifiers': identifiers,
            'crossref_data': None,
            'openalex_data': None,
            'crossref_status': False,
            'openalex_status': False,
            'authors': [],
            'authors_display': [],
            'journal': None,
            'journal_from': None,  # Track source: 'crossref', 'openalex', or None
            'year': None,
            'type': None,
            'publisher': None,
            'publisher_from': None,  # Track source: 'crossref', 'openalex', or None
            'crossmark_issues': [],
            'is_preprint': False,
            'has_erratum': False,
            'is_retracted': False,
            'is_self_citation': False,
            'issn': None,
            'license': None,
            'references_count': 0,
            'citations_count': 0,
            'is_suspicious_doi': False
        }
        
        if doi:
            # Check for suspicious DOI
            if crossref_data is None and openalex_data is None:
                result['is_suspicious_doi'] = True
                result['crossmark_issues'].append('⚠️ Attention: invalid/suspicious DOI (not found in Crossref or OpenAlex)')
            
            # ==================== PROCESS CROSSREF DATA ====================
            if crossref_data:
                result['crossref_data'] = crossref_data
                result['crossref_status'] = True
                
                # Extract authors from Crossref
                authors_data = extract_authors_from_crossref(crossref_data)
                result['authors'].extend(authors_data)
                
                for auth in authors_data:
                    result['authors_display'].append(auth['display_name'])
                
                # Extract journal from Crossref
                if 'container-title' in crossref_data and crossref_data['container-title']:
                    journal_name = crossref_data['container-title'][0]
                    if journal_name and journal_name.strip():
                        result['journal'] = journal_name.strip()
                        result['journal_from'] = 'crossref'
                
                # Extract ISSN from Crossref
                if 'ISSN' in crossref_data and crossref_data['ISSN']:
                    result['issn'] = crossref_data['ISSN'][0]
                
                # Extract year from Crossref
                if 'issued' in crossref_data and 'date-parts' in crossref_data['issued']:
                    date_parts = crossref_data['issued']['date-parts']
                    if date_parts and date_parts[0] and len(date_parts[0]) > 0:
                        result['year'] = date_parts[0][0]
                
                # Extract publication type
                if 'type' in crossref_data:
                    result['type'] = crossref_data['type']
                
                # Extract publisher from Crossref
                if 'publisher' in crossref_data and crossref_data['publisher']:
                    publisher_name = crossref_data['publisher']
                    if publisher_name and publisher_name.strip():
                        result['publisher'] = publisher_name.strip()
                        result['publisher_from'] = 'crossref'
                
                # Extract license
                if 'license' in crossref_data:
                    result['license'] = crossref_data['license'][0].get('URL', '') if crossref_data['license'] else None
                
                # Extract citation count
                if 'is-referenced-by-count' in crossref_data:
                    result['citations_count'] = crossref_data['is-referenced-by-count']
                
                # Extract Crossmark issues
                if 'crossmark' in crossref_data:
                    for cm in crossref_data.get('crossmark', []):
                        if 'type' in cm:
                            result['crossmark_issues'].append(cm['type'])
            
            # ==================== PROCESS OPENALEX DATA ====================
            if openalex_data:
                result['openalex_data'] = openalex_data
                result['openalex_status'] = True
                
                # Extract authors from OpenAlex (add only unique ones)
                authors_data = extract_authors_from_openalex(openalex_data)
                existing_compare = {a['compare_name'] for a in result['authors']}
                for auth in authors_data:
                    if auth['compare_name'] not in existing_compare:
                        result['authors'].append(auth)
                        result['authors_display'].append(auth['display_name'])
                        existing_compare.add(auth['compare_name'])
                
                # Check if preprint
                if openalex_data.get('type') == 'posted_content':
                    result['is_preprint'] = True
                
                # Check if retracted
                if openalex_data.get('is_retracted'):
                    result['is_retracted'] = True
                
                # Extract year from OpenAlex (if not already set by Crossref)
                if not result['year'] and 'publication_year' in openalex_data:
                    result['year'] = openalex_data['publication_year']
                
                # Extract publication type from OpenAlex (if not set)
                if not result['type'] and 'type' in openalex_data:
                    result['type'] = openalex_data['type']
                
                # ========== EXTRACT JOURNAL FROM OPENALEX (MULTIPLE SOURCES) ==========
                journal_from_openalex = None
                
                # Method 1: host_venue (most common for journal articles)
                if openalex_data.get('host_venue'):
                    host_venue = openalex_data['host_venue']
                    if isinstance(host_venue, dict):
                        if host_venue.get('display_name'):
                            journal_from_openalex = host_venue['display_name'].strip()
                        elif host_venue.get('name'):
                            journal_from_openalex = host_venue['name'].strip()
                
                # Method 2: primary_location (more reliable for some records)
                if not journal_from_openalex and openalex_data.get('primary_location'):
                    primary = openalex_data['primary_location']
                    if isinstance(primary, dict):
                        if primary.get('source') and isinstance(primary['source'], dict):
                            if primary['source'].get('display_name'):
                                journal_from_openalex = primary['source']['display_name'].strip()
                            elif primary['source'].get('name'):
                                journal_from_openalex = primary['source']['name'].strip()
                
                # Method 3: locations array (iterate through all locations)
                if not journal_from_openalex and openalex_data.get('locations'):
                    for loc in openalex_data['locations']:
                        if isinstance(loc, dict) and loc.get('source'):
                            source = loc['source']
                            if isinstance(source, dict):
                                if source.get('display_name'):
                                    journal_from_openalex = source['display_name'].strip()
                                    break
                                elif source.get('name'):
                                    journal_from_openalex = source['name'].strip()
                                    break
                
                # Method 4: best_open_access (sometimes contains source info)
                if not journal_from_openalex and openalex_data.get('best_open_access'):
                    best_oa = openalex_data['best_open_access']
                    if isinstance(best_oa, dict) and best_oa.get('host_venue'):
                        host = best_oa['host_venue']
                        if isinstance(host, dict):
                            if host.get('display_name'):
                                journal_from_openalex = host['display_name'].strip()
                
                # Set journal if found and not already set by Crossref
                if journal_from_openalex and journal_from_openalex.strip():
                    if not result['journal']:
                        result['journal'] = journal_from_openalex
                        result['journal_from'] = 'openalex'
                    # If both have data, keep Crossref as primary but log that OpenAlex also has it
                    elif result['journal'] and journal_from_openalex != result['journal']:
                        # Optionally, you could prefer the longer/more complete name
                        if len(journal_from_openalex) > len(result['journal']):
                            result['journal'] = journal_from_openalex
                            result['journal_from'] = 'openalex_override'
                
                # ========== EXTRACT PUBLISHER FROM OPENALEX (MULTIPLE SOURCES) ==========
                publisher_from_openalex = None
                
                # Method 1: host_venue publisher
                if openalex_data.get('host_venue'):
                    host_venue = openalex_data['host_venue']
                    if isinstance(host_venue, dict):
                        if host_venue.get('publisher'):
                            publisher_from_openalex = host_venue['publisher'].strip()
                        elif host_venue.get('publisher_name'):
                            publisher_from_openalex = host_venue['publisher_name'].strip()
                
                # Method 2: primary_location source publisher
                if not publisher_from_openalex and openalex_data.get('primary_location'):
                    primary = openalex_data['primary_location']
                    if isinstance(primary, dict) and primary.get('source'):
                        source = primary['source']
                        if isinstance(source, dict):
                            if source.get('publisher'):
                                publisher_from_openalex = source['publisher'].strip()
                            elif source.get('publisher_name'):
                                publisher_from_openalex = source['publisher_name'].strip()
                
                # Method 3: locations array source publisher
                if not publisher_from_openalex and openalex_data.get('locations'):
                    for loc in openalex_data['locations']:
                        if isinstance(loc, dict) and loc.get('source'):
                            source = loc['source']
                            if isinstance(source, dict):
                                if source.get('publisher'):
                                    publisher_from_openalex = source['publisher'].strip()
                                    break
                                elif source.get('publisher_name'):
                                    publisher_from_openalex = source['publisher_name'].strip()
                                    break
                
                # Method 4: host_organization (for preprints, repositories, institutional papers)
                if not publisher_from_openalex and openalex_data.get('host_organization'):
                    host_org = openalex_data['host_organization']
                    if isinstance(host_org, dict):
                        if host_org.get('display_name'):
                            publisher_from_openalex = host_org['display_name'].strip()
                        elif host_org.get('name'):
                            publisher_from_openalex = host_org['name'].strip()
                    elif isinstance(host_org, str):
                        publisher_from_openalex = host_org.strip()
                
                # Method 5: host_organization_name (alternative field)
                if not publisher_from_openalex and openalex_data.get('host_organization_name'):
                    publisher_from_openalex = openalex_data['host_organization_name'].strip()
                
                # Method 6: best_open_access host_venue publisher
                if not publisher_from_openalex and openalex_data.get('best_open_access'):
                    best_oa = openalex_data['best_open_access']
                    if isinstance(best_oa, dict) and best_oa.get('host_venue'):
                        host = best_oa['host_venue']
                        if isinstance(host, dict):
                            if host.get('publisher'):
                                publisher_from_openalex = host['publisher'].strip()
                
                # Set publisher if found and not already set by Crossref
                if publisher_from_openalex and publisher_from_openalex.strip():
                    if not result['publisher']:
                        result['publisher'] = publisher_from_openalex
                        result['publisher_from'] = 'openalex'
                    # If both have data, keep Crossref as primary but log that OpenAlex also has it
                    elif result['publisher'] and publisher_from_openalex != result['publisher']:
                        # Optionally, you could prefer the longer/more complete name
                        if len(publisher_from_openalex) > len(result['publisher']):
                            result['publisher'] = publisher_from_openalex
                            result['publisher_from'] = 'openalex_override'
                
                # Extract reference count
                if 'referenced_works_count' in openalex_data:
                    result['references_count'] = openalex_data['referenced_works_count']
                
                # Extract citation count (take max from both sources)
                if 'cited_by_count' in openalex_data:
                    result['citations_count'] = max(result['citations_count'], openalex_data['cited_by_count'])
        
        # ==================== SELF-CITATION DETECTION ====================
        if paper_authors and result['authors']:
            for author in result['authors']:
                for paper_author in paper_authors:
                    paper_norm, _ = normalize_author_name(paper_author)
                    if author['compare_name'] == paper_norm:
                        result['is_self_citation'] = True
                        break
        
        # Merge authors (deduplicate)
        if result['authors']:
            result['authors'] = merge_authors(result['authors'])
            result['authors_display'] = [a['display_name'] for a in result['authors']]
        
        results.append(result)
        
        # Update progress less frequently (only at batch level)
        if progress_callback and idx % 10 == 0:
            progress_callback(batch_num, idx, batch_size, total_batches)
    
    return results

def analyze_all_references_optimized(references: List[str], batch_size: int = 50, paper_authors: Set[str] = None) -> List[Dict]:
    """Analyze all references with optimized batching and COLORED progress updates"""
    all_results = []
    total_batches = (len(references) + batch_size - 1) // batch_size
    
    # Calculate expected DOI count for color coding
    expected_doi_count = 0
    for ref in references:
        if extract_doi_from_text(ref):
            expected_doi_count += 1
    data_density_estimate = expected_doi_count / len(references) if references else 0
    
    # Create colored progress container
    progress_placeholder = st.empty()
    metrics_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Initial progress bar with estimate-based color
    initial_color, initial_badge, badge_class = get_progress_color_by_metrics(expected_doi_count, len(references))
    initial_html = f"""
    <div class="colored-progress-container">
        <div class="colored-progress-bar" style="width: 0%; background: linear-gradient(90deg, {initial_color} 0%, {initial_color}CC 50%, {initial_color} 100%);"></div>
    </div>
    <div class="progress-stats">
        <span>📊 Estimated DOI coverage: {data_density_estimate:.1%}</span>
        <span class="progress-badge {badge_class}">{initial_badge}</span>
    </div>
    """
    progress_placeholder.markdown(initial_html, unsafe_allow_html=True)
    
    # Track metrics for dynamic color updates
    total_dois_found = 0
    total_api_success = 0
    processed_refs = 0
    
    def update_progress(batch_num, ref_idx, batch_len, total_batches):
        """Update progress with dynamic coloring based on actual metrics"""
        nonlocal total_dois_found, total_api_success, processed_refs
        
        # This is called from inside the batch, need to update counts carefully
        # We'll use a simpler approach: update after each batch completion
        pass
    
    status_container = st.status(f"📊 Analyzing {len(references)} references...", expanded=True)
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(references))
        batch = references[start_idx:end_idx]
        
        # Update status text
        status_container.update(
            label=f"📊 Analyzing batch {batch_num + 1} of {total_batches} (references {start_idx + 1}-{end_idx} of {len(references)})",
            state="running"
        )
        
        # Process batch with optimized function
        batch_results = analyze_reference_batch_optimized(
            batch, 
            progress_callback=None,  # Disable internal callback, we'll update manually
            paper_authors=paper_authors,
            batch_num=batch_num,
            total_batches=total_batches
        )
        
        # Update metrics after batch completion
        for result in batch_results:
            processed_refs += 1
            if result.get('doi'):
                total_dois_found += 1
            if result.get('crossref_status') or result.get('openalex_status'):
                total_api_success += 1
        
        all_results.extend(batch_results)
        
        # Calculate current progress and metrics
        progress_percent = (processed_refs / len(references)) * 100
        current_data_density = total_dois_found / processed_refs if processed_refs > 0 else 0
        api_success_rate = total_api_success / processed_refs if processed_refs > 0 else 0
        
        # Get dynamic color based on actual metrics
        color, badge_text, badge_class = get_progress_color_by_metrics(
            total_dois_found, 
            processed_refs,
            total_api_success
        )
        
        # Create animated shimmer effect based on progress speed
        shimmer_speed = "2s" if progress_percent < 50 else "1s"
        
        # Update colored progress bar with metrics
        progress_html = f"""
        <style>
        @keyframes shimmer{{
            0% {{ background-position: -1000px 0; }}
            100% {{ background-position: 1000px 0; }}
        }}
        
        .colored-progress-container {{
            width: 100%;
            background-color: #f0f0f0;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
            margin: 10px 0;
        }}
        
        .colored-progress-bar {{
            width: {progress_percent:.1f}%;
            height: 32px;
            background: linear-gradient(90deg, 
                {color} 0%, 
                {color}DD 25%,
                {color} 50%,
                {color}DD 75%,
                {color} 100%);
            background-size: 200% 100%;
            animation: shimmer {shimmer_speed} infinite linear;
            border-radius: 20px;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 13px;
            text-shadow: 0 0 2px rgba(0,0,0,0.5);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .colored-progress-bar::after {{
            content: "{progress_percent:.1f}%";
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            white-space: nowrap;
        }}
        
        .progress-stats {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 8px;
            font-size: 12px;
        }}
        
        .stat-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .progress-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: {color}20;
            color: {color};
            border: 1px solid {color}40;
        }}
        
        .badge-green {{ background: #d4edda; color: #155724; border-color: #15572440; }}
        .badge-blue {{ background: #d1ecf1; color: #0c5460; border-color: #0c546040; }}
        .badge-orange {{ background: #fff3cd; color: #856404; border-color: #85640440; }}
        .badge-red {{ background: #f8d7da; color: #721c24; border-color: #721c2440; }}
        
        .data-metric {{
            font-family: monospace;
            font-size: 11px;
            background: #f8f9fa;
            padding: 2px 8px;
            border-radius: 12px;
        }}
        
        .progress-legend {{
            display: flex;
            gap: 15px;
            margin-top: 5px;
            font-size: 10px;
            color: #666;
        }}
        
        .legend-dot {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 4px;
        }}
        </style>
        
        <div class="colored-progress-container">
            <div class="colored-progress-bar"></div>
        </div>
        <div class="progress-stats">
            <div class="stat-item">
                <span>📊</span>
                <span><strong>{processed_refs}/{len(references)}</strong> references</span>
            </div>
            <div class="stat-item">
                <span>🔗</span>
                <span><strong>{total_dois_found}</strong> DOIs found</span>
                <span class="data-metric">({current_data_density:.1%})</span>
            </div>
            <div class="stat-item">
                <span>✅</span>
                <span><strong>{total_api_success}</strong> API successes</span>
                <span class="data-metric">({api_success_rate:.1%})</span>
            </div>
            <span class="progress-badge {badge_class}">{badge_text}</span>
        </div>
        <div class="progress-legend">
            <span><span class="legend-dot" style="background: #00CC96;"></span> Excellent (80%+)</span>
            <span><span class="legend-dot" style="background: #00B5F1;"></span> Good (60-80%)</span>
            <span><span class="legend-dot" style="background: #FFA042;"></span> Moderate (40-60%)</span>
            <span><span class="legend-dot" style="background: #FF6B6B;"></span> Low (20-40%)</span>
            <span><span class="legend-dot" style="background: #CC0000;"></span> Critical (<20%)</span>
        </div>
        """
        
        progress_placeholder.markdown(progress_html, unsafe_allow_html=True)
        
        # Also update the main Streamlit progress bar for compatibility
        st.progress(progress_percent / 100)
    
    status_container.update(label="✅ Analysis completed!", state="complete")
    
    # Final progress bar with completion status
    final_color, final_badge, _ = get_progress_color_by_metrics(total_dois_found, len(references), total_api_success)
    final_html = f"""
    <div class="colored-progress-container">
        <div class="colored-progress-bar" style="width: 100%; background: linear-gradient(90deg, {final_color} 0%, {final_color}CC 50%, {final_color} 100%);"></div>
    </div>
    <div class="progress-stats">
        <span>✅ Analysis complete!</span>
        <span class="progress-badge {badge_class}">{final_badge}</span>
    </div>
    <div class="progress-stats" style="margin-top: 10px;">
        <span>📊 Final stats: {total_dois_found}/{len(references)} DOIs ({total_dois_found/len(references)*100:.1f}%)</span>
        <span>🔗 API success rate: {total_api_success/len(references)*100:.1f}%</span>
    </div>
    """
    progress_placeholder.markdown(final_html, unsafe_allow_html=True)
    
    return all_results

# ======================== CACHING ========================
@st.cache_data(ttl=3600, show_spinner=False)
def cache_crossref_lookup(doi: str) -> Optional[Dict]:
    """Cached Crossref request"""
    return fetch_crossref(doi)

@st.cache_data(ttl=3600, show_spinner=False)
def cache_openalex_lookup(doi: str) -> Optional[Dict]:
    """Cached OpenAlex request"""
    return fetch_openalex(doi)

@st.cache_data(ttl=7200, show_spinner=False)
def cache_issn_lookup(issn: str) -> Optional[Dict]:
    """Cached ISSN Portal request"""
    try:
        url = f"https://portal.issn.org/api/hub?issn={issn}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# ======================== IDENTIFIER EXTRACTION (NEW) ========================
def extract_identifiers(text: str) -> Dict[str, Optional[str]]:
    """Extract all types of identifiers from text (DOI, URL, arXiv, PMID, ISBN)"""
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    result = {
        'doi': None,
        'url': None,
        'arxiv': None,
        'pmid': None,
        'isbn': None
    }
    
    # Extract DOI - IMPROVED: handle parentheses, brackets, and special characters
    doi_patterns = [
        r'https?://doi\.org/(10\.\d{4,9}/[^\s<>"\'()\[\]{}]+(?:\([^)]*\))?(?:[^\s<>"\'()\[\]{}]*)?)',
        r'https?://dx\.doi\.org/(10\.\d{4,9}/[^\s<>"\'()\[\]{}]+(?:\([^)]*\))?(?:[^\s<>"\'()\[\]{}]*)?)',
        r'doi[:]\s*(10\.\d{4,9}/[^\s<>"\'()\[\]{}]+(?:\([^)]*\))?(?:[^\s<>"\'()\[\]{}]*)?)',
        r'DOI[:]\s*(10\.\d{4,9}/[^\s<>"\'()\[\]{}]+(?:\([^)]*\))?(?:[^\s<>"\'()\[\]{}]*)?)',
        r'doi\s*=\s*(10\.\d{4,9}/[^\s<>"\'()\[\]{}]+(?:\([^)]*\))?(?:[^\s<>"\'()\[\]{}]*)?)',
        r'(10\.\d{4,9}/[^\s<>"\'()\[\]{}]+(?:\([^)]*\))?(?:[^\s<>"\'()\[\]{}]*)?)'
    ]
    
    for pattern in doi_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                doi_raw = match.strip()
                # Remove trailing punctuation that might be part of sentence
                doi_raw = re.sub(r'[.,;:!?)]+$', '', doi_raw)
                # Ensure closing parenthesis is preserved if it's part of DOI
                if '(' in doi_raw and doi_raw.count('(') > doi_raw.count(')'):
                    # Try to find matching closing parenthesis
                    open_count = doi_raw.count('(')
                    close_needed = open_count - doi_raw.count(')')
                    # Look ahead for more closing parentheses
                    remaining_text = text[text.find(doi_raw) + len(doi_raw):]
                    for _ in range(close_needed):
                        match_close = re.search(r'\)', remaining_text)
                        if match_close:
                            doi_raw += ')'
                            remaining_text = remaining_text[match_close.start() + 1:]
                        else:
                            break
                
                # Validate DOI format (must have prefix and suffix)
                if re.match(r'10\.\d{4,9}/.+', doi_raw):
                    # Additional validation: DOI should not end with invalid characters
                    if not re.search(r'[.,;:!?]$', doi_raw):
                        result['doi'] = doi_raw
                        break
            if result['doi']:
                break
    
    # If DOI still not found with complex pattern, try simpler but more robust pattern
    if not result['doi']:
        simple_pattern = r'(10\.\d{4,9}/[^\s]+)'
        matches = re.findall(simple_pattern, text)
        for match in matches:
            # Clean up the match
            doi_clean = re.sub(r'[.,;:!?)]+$', '', match)
            # Ensure parentheses are properly matched
            if '(' in doi_clean and ')' not in doi_clean:
                # Try to find closing parenthesis
                remaining = text[text.find(doi_clean) + len(doi_clean):]
                close_match = re.search(r'\)', remaining)
                if close_match:
                    doi_clean += ')'
            if re.match(r'10\.\d{4,9}/', doi_clean):
                result['doi'] = doi_clean
                break
    
    # Extract URL (general web links)
    url_pattern = r'https?://[^\s<>"\'()\[\]]+'
    url_matches = re.findall(url_pattern, text)
    if url_matches:
        # Filter out DOI URLs (already captured)
        for url in url_matches:
            if 'doi.org' not in url and 'dx.doi.org' not in url:
                result['url'] = url
                break
    
    # Extract arXiv ID
    arxiv_patterns = [
        r'arxiv\.org/abs/([^\s<>"\'()]+)',
        r'arxiv\.org/pdf/([^\s<>"\'()]+)',
        r'arXiv[:]\s*([^\s<>"\'()]+)',
        r'arXiv:\s*([^\s<>"\'()]+)',
        r'([0-9]{4}\.[0-9]{4,5})(?:\s|$)'
    ]
    
    for pattern in arxiv_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            result['arxiv'] = matches[0].strip()
            break
    
    # Extract PMID (PubMed ID)
    pmid_patterns = [
        r'PMID[:]\s*(\d+)',
        r'PMID:\s*(\d+)',
        r'pubmed.ncbi.nlm.nih.gov/(\d+)'
    ]
    
    for pattern in pmid_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            result['pmid'] = matches[0].strip()
            break
    
    # Extract ISBN (books)
    isbn_pattern = r'ISBN[:]?\s*([0-9]{3}-?[0-9]{1,5}-?[0-9]{1,7}-?[0-9X]{1})'
    matches = re.findall(isbn_pattern, text, re.IGNORECASE)
    if matches:
        result['isbn'] = matches[0].strip()
    
    return result


def extract_doi_from_text(text: str) -> Optional[str]:
    """Extract DOI from string (legacy function, now uses extract_identifiers)"""
    identifiers = extract_identifiers(text)
    return identifiers['doi']

# ======================== ENHANCED AUTHOR NORMALIZATION ========================
def normalize_author_name(name: str) -> Tuple[str, str]:
    """Normalize author name with first initial only for disambiguation"""
    if not name:
        return "", ""
    
    name = name.strip()
    
    if ',' in name:
        # Last, First format
        last, first = name.split(',', 1)
        last = last.strip()
        first = first.strip()
        # Take only first letter of first initial
        first_initial = first[0] if first and first[0].isalpha() else ''
        display_name = f"{last} {first_initial}" if first_initial else last
        compare_name = f"{last.lower()} {first_initial.lower()}"
        return compare_name, display_name
    else:
        # First Last format
        parts = name.split()
        if len(parts) >= 2:
            last = parts[-1]
            # Take first letter of first name only
            first_initial = parts[0][0] if parts[0] and parts[0][0].isalpha() else ''
            display_name = f"{last} {first_initial}" if first_initial else last
            compare_name = f"{last.lower()} {first_initial.lower()}"
            return compare_name, display_name
        return name.lower(), name

def get_author_disambiguation_key(author: Dict) -> str:
    """Create disambiguation key using ORCID, institution, and country"""
    # Priority 1: ORCID (most reliable)
    if author.get('orcid'):
        return f"orcid:{author['orcid']}"
    
    # Priority 2: Institution + Country + Normalized name
    institution = author.get('institution', '')
    country = author.get('country', '')
    compare_name = author.get('compare_name', '')
    
    if institution and country:
        return f"inst:{institution}|country:{country}|name:{compare_name}"
    elif institution:
        return f"inst:{institution}|name:{compare_name}"
    elif country:
        return f"country:{country}|name:{compare_name}"
    
    # Fallback: just normalized name
    return f"name:{compare_name}"

def extract_authors_from_crossref(data: Dict) -> List[Dict]:
    """Extract authors from Crossref"""
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
                    'given': given,
                    'institution': '',  # Crossref doesn't always provide institution
                    'country': ''
                })
            elif family:
                compare_name, display_name = normalize_author_name(family)
                authors.append({
                    'compare_name': compare_name,
                    'display_name': display_name,
                    'raw_name': family,
                    'orcid': orcid,
                    'family': family,
                    'given': '',
                    'institution': '',
                    'country': ''
                })
    return authors

def extract_authors_from_openalex(data: Dict) -> List[Dict]:
    """Extract authors from OpenAlex with institution and country"""
    authors = []
    if 'authorships' in data and data['authorships']:
        for authorship in data['authorships']:
            author = authorship.get('author', {})
            display_name_raw = author.get('display_name', '')
            orcid = author.get('orcid', None)
            institutions = authorship.get('institutions', [])
            country = institutions[0].get('country_code', '') if institutions else ''
            institution_name = institutions[0].get('display_name', '') if institutions else ''
            
            if display_name_raw:
                compare_name, display_name = normalize_author_name(display_name_raw)
                authors.append({
                    'compare_name': compare_name,
                    'display_name': display_name,
                    'raw_name': display_name_raw,
                    'orcid': orcid,
                    'country': country,
                    'institution': institution_name,
                    'family': display_name_raw.split()[-1] if display_name_raw.split() else '',
                    'given': display_name_raw.split()[0] if display_name_raw.split() else ''
                })
    return authors

def merge_authors(authors_list: List[Dict]) -> List[Dict]:
    """Merge duplicate authors using ORCID and disambiguation keys"""
    merged = {}
    for author in authors_list:
        key = get_author_disambiguation_key(author)
        if key and key in merged:
            existing = merged[key]
            # Merge additional metadata
            if not existing.get('orcid') and author.get('orcid'):
                existing['orcid'] = author['orcid']
            if not existing.get('institution') and author.get('institution'):
                existing['institution'] = author['institution']
            if not existing.get('country') and author.get('country'):
                existing['country'] = author['country']
            if len(author.get('display_name', '')) > len(existing.get('display_name', '')):
                existing['display_name'] = author['display_name']
        elif key:
            merged[key] = author.copy()
    return list(merged.values())

# ======================== DUPLICATE DETECTION ========================
def find_duplicate_references(references: List[str], threshold: float = 0.85) -> List[Dict]:
    """Find duplicate references in literature list"""
    duplicates = []
    seen_dois = {}
    seen_texts = {}
    
    for i, ref1 in enumerate(references):
        doi1 = extract_doi_from_text(ref1)
        
        if doi1:
            # Check if DOI already seen (exact match including suffix)
            if doi1 in seen_dois:
                j = seen_dois[doi1]
                # Only consider duplicate if DOIs are EXACTLY the same (including suffix)
                duplicates.append({
                    'index1': j,
                    'index2': i,
                    'ref1': references[j][:200],
                    'ref2': ref1[:200],
                    'reason': f'Full DOI match: {doi1}'
                })
                continue
            else:
                seen_dois[doi1] = i
        
        clean1 = re.sub(r'\s+', ' ', ref1).lower()
        clean1 = re.sub(r'[^\w\s]', '', clean1)
        
        for j, ref2 in enumerate(references[i+1:], i+1):
            doi2 = extract_doi_from_text(ref2)
            
            # Skip if both have DOI and they are exactly the same (already handled above)
            if doi1 and doi2 and doi1 == doi2:
                continue
            
            # Only perform text similarity for references without exact DOI match
            clean2 = re.sub(r'\s+', ' ', ref2).lower()
            clean2 = re.sub(r'[^\w\s]', '', clean2)
            
            similarity = difflib.SequenceMatcher(None, clean1, clean2).ratio()
            
            if similarity > threshold:
                duplicates.append({
                    'index1': i,
                    'index2': j,
                    'ref1': ref1[:200],
                    'ref2': ref2[:200],
                    'reason': f'High text similarity: {similarity:.1%}'
                })
    
    unique_duplicates = []
    seen_pairs = set()
    for dup in duplicates:
        pair = tuple(sorted([dup['index1'], dup['index2']]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_duplicates.append(dup)
    
    return unique_duplicates

# ======================== NEW ANALYSIS FUNCTIONS ========================

def extract_concepts_from_references(results: List[Dict]) -> Dict:
    """Analyze concepts from OpenAlex"""
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
    
    for concept in concept_details:
        concept_details[concept]['avg_score'] = concept_details[concept]['score_sum'] / concept_details[concept]['count']
    
    return {
        'concepts': concept_counter.most_common(20),
        'details': concept_details,
        'unique_concepts': len(concept_counter)
    }

def analyze_geographic_distribution(results: List[Dict]) -> Dict:
    """Geographic analysis by author country"""
    country_counter = Counter()
    institution_counter = Counter()
    
    for result in results:
        for author in result.get('authors', []):
            if author.get('country'):
                country_counter[author['country']] += 1
            if author.get('institution'):
                institution_counter[author['institution']] += 1
    
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
    """Co-authorship network analysis"""
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
    
    top_collaborations = []
    for (a1, a2), count in author_pairs.most_common(20):
        name1 = next((a['display_name'] for r in results for a in r.get('authors', []) 
                     if a.get('compare_name') == a1), a1)
        name2 = next((a['display_name'] for r in results for a in r.get('authors', []) 
                     if a.get('compare_name') == a2), a2)
        top_collaborations.append({'author1': name1, 'author2': name2, 'count': count})
    
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
    """Temporal analysis of citations (without Sleeping Beauties)"""
    yearly_citations = defaultdict(int)
    paper_ages = []
    
    for result in results:
        if result.get('year'):
            year = result['year']
            if isinstance(year, (int, float)) and 1900 < year <= datetime.now().year:
                yearly_citations[year] += 1
                age = datetime.now().year - year
                paper_ages.append(age)
    
    cumulative = {}
    sorted_years = sorted(yearly_citations.keys())
    running_total = 0
    for year in sorted_years:
        running_total += yearly_citations[year]
        cumulative[year] = running_total
    
    median_age = sorted(paper_ages)[len(paper_ages)//2] if paper_ages else 0
    
    return {
        'yearly_distribution': dict(sorted(yearly_citations.items())),
        'cumulative_citations': cumulative,
        'median_age': median_age,
        'average_age': sum(paper_ages) / len(paper_ages) if paper_ages else 0
    }

def analyze_yearly_statistics(results: List[Dict]) -> Dict:
    """Analyze yearly statistics with 3/5/10 year lookback"""
    current_year = datetime.now().year
    year_counts = {}
    year_percentages = {}
    
    # Count references by year
    for result in results:
        year = result.get('year')
        if year and isinstance(year, (int, float)) and 1900 < year <= current_year:
            year_counts[year] = year_counts.get(year, 0) + 1
    
    total_refs = sum(year_counts.values())
    
    # Calculate percentages
    for year in year_counts:
        year_percentages[year] = (year_counts[year] / total_refs * 100) if total_refs > 0 else 0
    
    # Calculate cumulative percentage
    sorted_years = sorted(year_counts.keys(), reverse=True)
    cumulative = {}
    running_total = 0
    for year in sorted_years:
        running_total += year_counts[year]
        cumulative[year] = (running_total / total_refs * 100) if total_refs > 0 else 0
    
    # Calculate last N years statistics
    last_3_years = sum(year_counts.get(y, 0) for y in range(current_year - 2, current_year + 1))
    last_5_years = sum(year_counts.get(y, 0) for y in range(current_year - 4, current_year + 1))
    last_10_years = sum(year_counts.get(y, 0) for y in range(current_year - 9, current_year + 1))
    
    return {
        'yearly_counts': year_counts,
        'yearly_percentages': year_percentages,
        'cumulative_percentages': cumulative,
        'last_3_years': last_3_years,
        'last_3_years_percent': (last_3_years / total_refs * 100) if total_refs > 0 else 0,
        'last_5_years': last_5_years,
        'last_5_years_percent': (last_5_years / total_refs * 100) if total_refs > 0 else 0,
        'last_10_years': last_10_years,
        'last_10_years_percent': (last_10_years / total_refs * 100) if total_refs > 0 else 0,
        'total_with_year': total_refs,
        'unknown_year': len([r for r in results if not r.get('year')])
    }

def analyze_identifier_coverage(results: List[Dict]) -> Dict:
    """Analyze what types of identifiers each reference has"""
    identifier_stats = {
        'has_doi': 0,
        'has_url': 0,
        'has_arxiv': 0,
        'has_pmid': 0,
        'has_isbn': 0,
        'has_none': 0,
        'multiple': 0
    }
    
    references_without_any = []
    references_with_only_url = []
    references_without_doi = []
    
    for result in results:
        text = result.get('original_text', '')
        identifiers = extract_identifiers(text)
        
        has_any = False
        count = 0
        
        if identifiers['doi']:
            identifier_stats['has_doi'] += 1
            has_any = True
            count += 1
        else:
            references_without_doi.append(text[:200])
        
        if identifiers['url']:
            identifier_stats['has_url'] += 1
            has_any = True
            count += 1
            if not identifiers['doi']:
                references_with_only_url.append(text[:200])
        if identifiers['arxiv']:
            identifier_stats['has_arxiv'] += 1
            has_any = True
            count += 1
        if identifiers['pmid']:
            identifier_stats['has_pmid'] += 1
            has_any = True
            count += 1
        if identifiers['isbn']:
            identifier_stats['has_isbn'] += 1
            has_any = True
            count += 1
        
        if not has_any:
            identifier_stats['has_none'] += 1
        
        if count > 1:
            identifier_stats['multiple'] += 1
    
    return {
        'stats': identifier_stats,
        'references_without_any': references_without_any[:20],
        'references_with_only_url': references_with_only_url[:20],
        'references_without_doi': references_without_doi[:20],
        'total_references': len(results)
    }

def analyze_publisher_frequency(results: List[Dict]) -> Dict:
    """Analyze publisher frequency - теперь корректно работает с OpenAlex данными"""
    publisher_counter = Counter()
    
    for result in results:
        # Try to get publisher from result first (already merged)
        publisher = result.get('publisher')
        
        # If not found, try to extract from OpenAlex data directly
        if not publisher and result.get('openalex_data'):
            openalex_data = result['openalex_data']
            
            # Try multiple sources in OpenAlex
            if openalex_data.get('host_venue') and isinstance(openalex_data['host_venue'], dict):
                publisher = openalex_data['host_venue'].get('publisher') or openalex_data['host_venue'].get('publisher_name')
            
            if not publisher and openalex_data.get('primary_location'):
                primary = openalex_data['primary_location']
                if isinstance(primary, dict) and primary.get('source'):
                    source = primary['source']
                    if isinstance(source, dict):
                        publisher = source.get('publisher') or source.get('publisher_name')
            
            if not publisher and openalex_data.get('locations'):
                for loc in openalex_data['locations']:
                    if isinstance(loc, dict) and loc.get('source'):
                        source = loc['source']
                        if isinstance(source, dict):
                            publisher = source.get('publisher') or source.get('publisher_name')
                            if publisher:
                                break
            
            if not publisher and openalex_data.get('host_organization'):
                host_org = openalex_data['host_organization']
                if isinstance(host_org, dict):
                    publisher = host_org.get('display_name') or host_org.get('name')
                elif isinstance(host_org, str):
                    publisher = host_org
            
            if not publisher and openalex_data.get('host_organization_name'):
                publisher = openalex_data['host_organization_name']
        
        # If still not found, try Crossref
        if not publisher and result.get('crossref_data'):
            publisher = result['crossref_data'].get('publisher')
        
        if publisher and isinstance(publisher, str):
            publisher = publisher.strip()
            if publisher:
                publisher_counter[publisher] += 1
    
    total_pubs = sum(publisher_counter.values())
    
    # Prepare full list with percentages
    publisher_list = []
    for publisher, count in publisher_counter.most_common():
        percentage = (count / total_pubs * 100) if total_pubs > 0 else 0
        publisher_list.append({
            'publisher': publisher,
            'count': count,
            'percentage': percentage
        })
    
    return {
        'all_publishers': publisher_list,
        'unique_publishers': len(publisher_counter),
        'top_10': publisher_list[:10]
    }

def analyze_journal_frequency_all(results: List[Dict]) -> Dict:
    """Analyze journal frequency (all journals, not just top)"""
    journal_counter = Counter()
    
    for result in results:
        if result.get('journal'):
            journal_counter[result['journal']] += 1
    
    total_journals = sum(journal_counter.values())
    
    # Prepare full list with percentages
    journal_list = []
    for journal, count in journal_counter.most_common():
        percentage = (count / total_journals * 100) if total_journals > 0 else 0
        journal_list.append({
            'journal': journal,
            'count': count,
            'percentage': percentage
        })
    
    return {
        'all_journals': journal_list,
        'unique_journals': len(journal_counter),
        'top_10': journal_list[:10]
    }

def analyze_author_frequency_all(results: List[Dict]) -> Dict:
    """Analyze author frequency with enhanced cross-reference merging using ORCID-name mapping"""
    # Step 1: First pass - collect all author records and build ORCID to name mapping
    all_author_records = []
    orcid_to_names = defaultdict(set)  # Maps ORCID to all compare_names
    name_to_orcid = {}  # Maps compare_name to ORCID (if any record has ORCID)
    
    for result in results:
        for author in result.get('authors', []):
            key = get_author_disambiguation_key(author)
            compare_name = author.get('compare_name', '')
            orcid = author.get('orcid')
            display_name = author.get('display_name', 'Unknown')
            institution = author.get('institution', '')
            country = author.get('country', '')
            
            # Store all records for later processing
            all_author_records.append({
                'key': key,
                'compare_name': compare_name,
                'orcid': orcid,
                'display_name': display_name,
                'institution': institution,
                'country': country
            })
            
            # Build mapping: if we have ORCID, record all names associated with it
            if orcid:
                orcid_to_names[orcid].add(compare_name)
            
            # If we have a compare_name and it has ORCID in at least one record, remember that
            if compare_name and orcid:
                # This name is definitively linked to this ORCID
                name_to_orcid[compare_name] = orcid
    
    # Step 2: Propagate ORCID links through name relationships
    # If two different names are linked to the same ORCID, they represent the same person
    name_clusters = defaultdict(set)  # Maps root name to all names in cluster
    
    # First, group by ORCID
    for orcid, names in orcid_to_names.items():
        # For each ORCID, all associated names belong together
        root_name = min(names) if names else ''  # Use smallest name as cluster key
        for name in names:
            name_clusters[root_name].add(name)
            # Also record that this name maps to this ORCID for reverse lookup
            name_to_orcid[name] = orcid
    
    # Step 3: Second pass - merge records using ORCID as primary key, fallback to name clusters
    merged_authors = {}  # Key: final_identifier, Value: author details
    
    for record in all_author_records:
        original_key = record['key']
        compare_name = record['compare_name']
        orcid = record['orcid']
        display_name = record['display_name']
        institution = record['institution']
        country = record['country']
        
        # Determine the canonical identifier for this author
        canonical_id = None
        
        # Priority 1: Use ORCID if available (most reliable)
        if orcid:
            canonical_id = f"orcid:{orcid}"
        else:
            # Priority 2: Check if this compare_name is linked to an ORCID via name_to_orcid
            if compare_name in name_to_orcid:
                linked_orcid = name_to_orcid[compare_name]
                canonical_id = f"orcid:{linked_orcid}"
            else:
                # Priority 3: Check if this name belongs to a cluster with other names
                found_cluster = False
                for root_name, cluster_names in name_clusters.items():
                    if compare_name in cluster_names:
                        # Use the root of the cluster as canonical identifier
                        canonical_id = f"cluster:{root_name}"
                        found_cluster = True
                        break
                
                # Priority 4: Use original key as last resort
                if not found_cluster:
                    canonical_id = original_key
        
        # Now merge using the canonical identifier
        if canonical_id not in merged_authors:
            merged_authors[canonical_id] = {
                'display_name': display_name,
                'orcid': orcid if orcid else (name_to_orcid.get(compare_name) if compare_name in name_to_orcid else None),
                'institution': institution,
                'country': country,
                'count': 0,
                'all_names': set(),
                'all_institutions': set(),
                'all_countries': set(),
                'latin_name': None  # New field for storing Latin (English) name
            }
        
        # Aggregate data
        merged_authors[canonical_id]['count'] += 1
        merged_authors[canonical_id]['all_names'].add(display_name)
        
        # Store Latin name if available (prefer OpenAlex Latin names)
        if author.get('raw_name') and re.match(r'^[A-Za-z\s\.]+$', author.get('raw_name', '')):
            if not merged_authors[canonical_id]['latin_name'] or len(author.get('raw_name', '')) > len(merged_authors[canonical_id]['latin_name'] or ''):
                merged_authors[canonical_id]['latin_name'] = author.get('raw_name')
        
        if institution:
            merged_authors[canonical_id]['all_institutions'].add(institution)
        if country:
            merged_authors[canonical_id]['all_countries'].add(country)
        
        # Update to best available display name (prefer longer, more complete names)
        current_display = merged_authors[canonical_id]['display_name']
        if len(display_name) > len(current_display):
            merged_authors[canonical_id]['display_name'] = display_name
        
        # Update ORCID if we have it and it's missing
        if orcid and not merged_authors[canonical_id]['orcid']:
            merged_authors[canonical_id]['orcid'] = orcid
        elif compare_name in name_to_orcid and not merged_authors[canonical_id]['orcid']:
            merged_authors[canonical_id]['orcid'] = name_to_orcid[compare_name]
    
    # Step 4: Build final author list with best available information
    author_list = []
    for canonical_id, details in merged_authors.items():
        # Determine the best institution (prefer non-empty, then most common if multiple)
        best_institution = ''
        if details['all_institutions']:
            # Count frequency of institutions
            inst_counter = Counter()
            for inst in details['all_institutions']:
                if inst:
                    inst_counter[inst] += 1
            if inst_counter:
                best_institution = inst_counter.most_common(1)[0][0]
        
        # Determine the best country
        best_country = ''
        if details['all_countries']:
            country_counter = Counter()
            for ctry in details['all_countries']:
                if ctry:
                    country_counter[ctry] += 1
            if country_counter:
                best_country = country_counter.most_common(1)[0][0]
        
        # Determine best display name: prefer Latin (English) name over Cyrillic
        best_display_name = details['display_name']
        if details.get('latin_name') and re.match(r'^[A-Za-z\s\.]+$', details['latin_name']):
            # Check if current name contains Cyrillic characters
            if any(ord(char) > 0x0400 and ord(char) < 0x0600 for char in best_display_name):
                best_display_name = details['latin_name']
        
        author_list.append({
            'display_name': best_display_name,
            'orcid': details['orcid'],
            'institution': best_institution,
            'country': best_country,
            'count': details['count']
        })
    
    # Sort by citation count descending
    author_list.sort(key=lambda x: x['count'], reverse=True)
    
    # Step 5: Post-process to merge any remaining duplicates by name similarity
    # (handle cases where ORCID is missing everywhere but names are very similar)
    final_author_list = []
    used_indices = set()
    
    for i, author in enumerate(author_list):
        if i in used_indices:
            continue
        
        # Extract base name without ORCID for comparison
        base_name = author['display_name'].lower()
        # Extract just the last name + first initial for comparison
        name_parts = base_name.split()
        if len(name_parts) >= 2:
            last_name = name_parts[0]
            first_initial = name_parts[1][0] if len(name_parts[1]) > 0 else ''
            comparison_key = f"{last_name} {first_initial}"
        else:
            comparison_key = base_name
        
        # Find all authors with the same comparison_key
        merged_count = author['count']
        merged_orcid = author['orcid']
        merged_institution = author['institution']
        merged_country = author['country']
        merged_names = [author['display_name']]
        
        for j, other in enumerate(author_list[i+1:], i+1):
            if j in used_indices:
                continue
            
            other_base = other['display_name'].lower()
            other_parts = other_base.split()
            if len(other_parts) >= 2:
                other_last = other_parts[0]
                other_initial = other_parts[1][0] if len(other_parts[1]) > 0 else ''
                other_key = f"{other_last} {other_initial}"
            else:
                other_key = other_base
            
            if other_key == comparison_key:
                # Same person!
                used_indices.add(j)
                merged_count += other['count']
                merged_names.append(other['display_name'])
                
                # Prefer any available ORCID
                if other['orcid'] and not merged_orcid:
                    merged_orcid = other['orcid']
                
                # Prefer institution if current is empty
                if other['institution'] and not merged_institution:
                    merged_institution = other['institution']
                elif other['institution'] and merged_institution and len(other['institution']) > len(merged_institution):
                    merged_institution = other['institution']
                
                # Prefer country if current is empty
                if other['country'] and not merged_country:
                    merged_country = other['country']
        
        # Choose best display name (longest, most complete, prefer Latin)
        best_name = max(merged_names, key=len)
        # Check if best_name contains Cyrillic and if there's a Latin alternative
        if any(ord(char) > 0x0400 and ord(char) < 0x0600 for char in best_name):
            for name in merged_names:
                if re.match(r'^[A-Za-z\s\.]+$', name):
                    best_name = name
                    break
        
        final_author_list.append({
            'display_name': best_name,
            'orcid': merged_orcid,
            'institution': merged_institution,
            'country': merged_country,
            'count': merged_count
        })
    
    # Final sort by count
    final_author_list.sort(key=lambda x: x['count'], reverse=True)
    
    return {
        'all_authors': final_author_list,
        'unique_authors': len(final_author_list),
        'top_20': final_author_list[:20]
    }

def analyze_orcid_coverage(results: List[Dict]) -> Dict:
    """Analyze ORCID coverage"""
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
    """Analyze language distribution of titles"""
    if not LANG_DETECT_AVAILABLE:
        return {'available': False, 'message': 'Install langdetect: pip install langdetect'}
    
    language_counter = Counter()
    
    for result in results:
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
    """Detect potentially predatory journals (warning signs)"""
    predatory_signs = []
    
    suspicious_publishers = ['OMICS', 'WASET', 'Scientific & Academic Publishing', 'Ashdin Publishing']
    
    for result in results:
        signs = []
        if result.get('publisher'):
            for sp in suspicious_publishers:
                if sp.lower() in result['publisher'].lower():
                    signs.append(f"Publisher {result['publisher']} in suspicious list")
        
        if not result.get('doi') and result.get('journal'):
            signs.append("No DOI for journal article")
        
        if result.get('crossref_data'):
            posted = result['crossref_data'].get('posted', {})
            issued = result['crossref_data'].get('issued', {})
            if posted and issued:
                signs.append("Possible very rapid publication")
        
        if signs:
            predatory_signs.append({
                'reference': result['original_text'][:200],
                'signs': signs,
                'journal': result.get('journal', 'Unknown')
            })
    
    return predatory_signs[:20]

def calculate_shannon_diversity(results: List[Dict], field: str = 'authors') -> float:
    """Shannon diversity index for authors, journals, or publishers"""
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
    """Identify citation classics (articles with abnormally high citation count)"""
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
            doi = result.get('doi', '')
            classics.append({
                'title': title,
                'citations': citations,
                'year': result.get('year', 'Unknown'),
                'journal': result.get('journal', 'Unknown'),
                'doi': doi
            })
    
    return sorted(classics, key=lambda x: x['citations'], reverse=True)[:10]

# ======================== MAIN ANALYSIS LOGIC ========================
def parse_reference_list(references_text: str) -> List[str]:
    """Split reference list into individual references (support multiple formats)
    
    Supports:
    - Numbered references: "1. Reference text"
    - Bracketed: "[1] Reference text"
    - Parenthesized: "(1) Reference text"
    - Plain DOI list: one DOI per line
    - Mixed formats
    """
    lines = references_text.strip().split('\n')
    references = []
    current_ref = []
    
    # Pattern for numbered/bracketed references
    patterns = [
        r'^\d+\.',      # "1. Text"
        r'^\[\d+\]',    # "[1] Text"
        r'^\(\d+\)',    # "(1) Text"
        r'^\d+\)',      # "1) Text"
        r'^\d+\s+[A-Z]' # "1 Text" (if Text starts with capital letter)
    ]
    
    # Pattern for detecting if a line looks like a standalone DOI or URL
    doi_url_pattern = r'^(https?://doi\.org/|https?://dx\.doi\.org/|10\.\d{4,9}/)'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        is_new_ref = False
        
        # Check if line starts with a reference marker
        for pattern in patterns:
            if re.match(pattern, line):
                is_new_ref = True
                break
        
        # SPECIAL CASE: If line starts with DOI/URL pattern AND previous line
        # was also a DOI/URL, treat as separate reference even without marker
        if not is_new_ref and re.match(doi_url_pattern, line):
            # Check if current_ref is not empty and contains a DOI/URL pattern
            if current_ref:
                # Join current_ref to see if it looks like it contains DOIs
                current_text = ' '.join(current_ref)
                # If current_text already has a DOI and this is another DOI on new line,
                # it should be a separate reference
                if re.search(doi_url_pattern, current_text):
                    # Save current reference and start new one
                    if current_ref:
                        references.append(' '.join(current_ref))
                        current_ref = []
                    is_new_ref = True
        
        if is_new_ref:
            if current_ref:
                references.append(' '.join(current_ref))
            
            # Clean the line from the marker
            cleaned_line = line
            for pattern in patterns:
                cleaned_line = re.sub(pattern, '', cleaned_line, count=1)
            cleaned_line = cleaned_line.strip()
            current_ref = [cleaned_line]
        else:
            if current_ref:
                current_ref.append(line)
            else:
                current_ref = [line]
    
    # Don't forget the last reference
    if current_ref:
        references.append(' '.join(current_ref))
    
    # Post-processing: split any reference that contains multiple DOIs on the same line
    final_references = []
    for ref in references:
        # Check if this reference contains multiple DOI patterns separated by spaces or newlines
        # Find all DOIs/URLs in this reference
        doi_matches = re.findall(r'(https?://doi\.org/10\.\d{4,9}/[^\s]+|10\.\d{4,9}/[^\s]+)', ref)
        
        if len(doi_matches) > 1:
            # Split into separate references, one per DOI
            for doi_match in doi_matches:
                final_references.append(doi_match.strip())
        else:
            final_references.append(ref)
    
    return final_references

def analyze_all_references(references: List[str], batch_size: int = 50, paper_authors: Set[str] = None) -> List[Dict]:
    """Analyze all references with batching - NOW USING OPTIMIZED VERSION"""
    # Use the optimized version for better performance
    return analyze_all_references_optimized(references, batch_size, paper_authors)

# ======================== PARSE PAPER AUTHORS INPUT ========================
def parse_paper_authors(authors_input: str) -> Set[str]:
    """Parse paper authors input with format validation {First Initial} {Last Name}"""
    if not authors_input:
        return set()
    
    authors = set()
    # Split by comma, tab, or newline
    parts = re.split(r'[,\t\n]+', authors_input)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Validate format: should start with letter (initial) optionally followed by dot, then space, then last name
        # Examples: N. Fukatsu, N Fukatsu, Z. Wei
        pattern = r'^([A-Za-z]\.?\s+[A-Za-z]+)$'
        if re.match(pattern, part):
            authors.add(part)
        else:
            # Try to auto-correct common mistakes
            # If format is "LastName FirstInitial" -> convert to "FirstInitial LastName"
            parts_reverse = part.split()
            if len(parts_reverse) == 2:
                # Check if second part is single letter (likely initial)
                if len(parts_reverse[1]) == 1 or (len(parts_reverse[1]) == 2 and parts_reverse[1][1] == '.'):
                    corrected = f"{parts_reverse[1]} {parts_reverse[0]}"
                    if re.match(r'^([A-Za-z]\.?\s+[A-Za-z]+)$', corrected):
                        authors.add(corrected)
                        continue
            # If format is "First Last" without initial dot
            if len(parts_reverse) == 2:
                if len(parts_reverse[0]) == 1 or (len(parts_reverse[0]) == 2 and parts_reverse[0][1] == '.'):
                    authors.add(part)
                    continue
            st.warning(get_text('authors_warning_text').format(part))
    
    return authors

# ======================== ENHANCED STATISTICS ========================
def generate_advanced_statistics(results: List[Dict]) -> Dict:
    """Generate enhanced statistics with new metrics - FIXED for OpenAlex publishers"""
    
    doi_status = {'both': 0, 'crossref_only': 0, 'openalex_only': 0, 'none': 0}
    author_counter = Counter()
    journal_counter = Counter()
    type_counter = Counter()
    year_counter = Counter()
    publisher_counter = Counter()  # Теперь будет считать из обоих источников
    problematic_refs = []
    crossref_only_refs = []
    openalex_only_refs = []
    suspicious_doi_refs = []
    
    # Для отладки - счетчики источников издателей
    publisher_sources = {'crossref': 0, 'openalex': 0, 'both': 0}
    
    for result in results:
        # DOI Status analysis
        if result['doi']:
            if result['crossref_status'] and result['openalex_status']:
                doi_status['both'] += 1
            elif result['crossref_status']:
                doi_status['crossref_only'] += 1
                crossref_only_refs.append({
                    'text': result['original_text'],
                    'doi': result['doi']
                })
            elif result['openalex_status']:
                doi_status['openalex_only'] += 1
                openalex_only_refs.append({
                    'text': result['original_text'],
                    'doi': result['doi']
                })
            else:
                doi_status['none'] += 1
                if result.get('is_suspicious_doi'):
                    suspicious_doi_refs.append({
                        'text': result['original_text'],
                        'doi': result['doi']
                    })
        else:
            doi_status['none'] += 1
        
        # ========== JOURNAL COLLECTION (already fixed in analyze function) ==========
        if result.get('journal'):
            journal_counter[result['journal']] += 1
        
        # ========== PUBLISHER COLLECTION - FIXED: collect from BOTH sources ==========
        publisher = None
        publisher_source = None
        
        # Try to get publisher from result (already merged in analyze function)
        if result.get('publisher'):
            publisher = result['publisher']
            publisher_source = result.get('publisher_from', 'unknown')
            
            # Count by source for debugging
            if publisher_source == 'crossref':
                publisher_sources['crossref'] += 1
            elif publisher_source == 'openalex' or publisher_source == 'openalex_override':
                publisher_sources['openalex'] += 1
                publisher_sources['both'] += 1 if result.get('crossref_status') else 0
        
        # Fallback: try to extract publisher directly from OpenAlex data if not in result
        if not publisher and result.get('openalex_data'):
            openalex_data = result['openalex_data']
            
            # Method 1: host_venue publisher
            if openalex_data.get('host_venue'):
                host_venue = openalex_data['host_venue']
                if isinstance(host_venue, dict):
                    if host_venue.get('publisher'):
                        publisher = host_venue['publisher'].strip()
                        publisher_source = 'openalex_host_venue'
                    elif host_venue.get('publisher_name'):
                        publisher = host_venue['publisher_name'].strip()
                        publisher_source = 'openalex_host_venue'
            
            # Method 2: primary_location source publisher
            if not publisher and openalex_data.get('primary_location'):
                primary = openalex_data['primary_location']
                if isinstance(primary, dict) and primary.get('source'):
                    source = primary['source']
                    if isinstance(source, dict):
                        if source.get('publisher'):
                            publisher = source['publisher'].strip()
                            publisher_source = 'openalex_primary_location'
                        elif source.get('publisher_name'):
                            publisher = source['publisher_name'].strip()
                            publisher_source = 'openalex_primary_location'
            
            # Method 3: locations array
            if not publisher and openalex_data.get('locations'):
                for loc in openalex_data['locations']:
                    if isinstance(loc, dict) and loc.get('source'):
                        source = loc['source']
                        if isinstance(source, dict):
                            if source.get('publisher'):
                                publisher = source['publisher'].strip()
                                publisher_source = 'openalex_locations'
                                break
                            elif source.get('publisher_name'):
                                publisher = source['publisher_name'].strip()
                                publisher_source = 'openalex_locations'
                                break
            
            # Method 4: host_organization
            if not publisher and openalex_data.get('host_organization'):
                host_org = openalex_data['host_organization']
                if isinstance(host_org, dict):
                    if host_org.get('display_name'):
                        publisher = host_org['display_name'].strip()
                        publisher_source = 'openalex_host_organization'
                    elif host_org.get('name'):
                        publisher = host_org['name'].strip()
                        publisher_source = 'openalex_host_organization'
                elif isinstance(host_org, str):
                    publisher = host_org.strip()
                    publisher_source = 'openalex_host_organization'
            
            # Method 5: host_organization_name
            if not publisher and openalex_data.get('host_organization_name'):
                publisher = openalex_data['host_organization_name'].strip()
                publisher_source = 'openalex_host_organization_name'
            
            # Method 6: best_open_access
            if not publisher and openalex_data.get('best_open_access'):
                best_oa = openalex_data['best_open_access']
                if isinstance(best_oa, dict) and best_oa.get('host_venue'):
                    host = best_oa['host_venue']
                    if isinstance(host, dict):
                        if host.get('publisher'):
                            publisher = host['publisher'].strip()
                            publisher_source = 'openalex_best_oa'
            
            # If we found publisher from OpenAlex, update the result for future use
            if publisher:
                result['publisher'] = publisher
                result['publisher_from'] = publisher_source
                publisher_sources['openalex'] += 1
        
        # Fallback: try to extract publisher from Crossref data if not in result
        if not publisher and result.get('crossref_data'):
            crossref_data = result['crossref_data']
            if 'publisher' in crossref_data and crossref_data['publisher']:
                publisher = crossref_data['publisher'].strip()
                publisher_source = 'crossref'
                result['publisher'] = publisher
                result['publisher_from'] = publisher_source
                publisher_sources['crossref'] += 1
        
        # Add to counter if publisher found
        if publisher:
            publisher_counter[publisher] += 1
        
        # ========== OTHER STATISTICS ==========
        
        # Publication type
        if result.get('type'):
            type_name = result['type'].replace('journal-', '').replace('-', ' ')
            type_counter[type_name] += 1
        
        # Year
        if result.get('year') and isinstance(result['year'], (int, float)) and 1900 < result['year'] <= datetime.now().year:
            year_counter[int(result['year'])] += 1
        
        # Problematic references detection
        has_problem = False
        problems = []
        if result.get('is_retracted'):
            problems.append(get_text('retracted'))
            has_problem = True
        if result.get('is_preprint'):
            problems.append(get_text('preprint'))
            has_problem = True
        if result.get('crossmark_issues'):
            problems.extend(result['crossmark_issues'])
            has_problem = True
        if result.get('is_suspicious_doi'):
            problems.append('⚠️ ' + get_text('suspicious_doi_badge'))
            has_problem = True
        
        if has_problem:
            problematic_refs.append({'text': result['original_text'], 'problems': ', '.join(problems)})
    
    # ========== ENHANCED AUTHOR ANALYSIS WITH MERGING ==========
    author_details = {}
    for result in results:
        for author in result.get('authors', []):
            key = get_author_disambiguation_key(author)
            if key:
                if key not in author_details:
                    author_details[key] = {
                        'display_name': author.get('display_name', 'Unknown'),
                        'orcid': author.get('orcid'),
                        'count': 0,
                        'country': author.get('country', ''),
                        'institution': author.get('institution', '')
                    }
                author_details[key]['count'] += 1
    
    sorted_authors = sorted(author_details.values(), key=lambda x: x['count'], reverse=True)
    top_authors_formatted = []
    for author in sorted_authors[:20]:
        orcid_str = f" 🔗 ORCID: {author['orcid']}" if author.get('orcid') else ""
        inst_str = f" 🏛 {author['institution'][:30]}" if author.get('institution') else ""
        display = ' '.join([part.capitalize() for part in author['display_name'].split()])
        top_authors_formatted.append(f"{display}{orcid_str}{inst_str} — {author['count']} {get_text('html_citations_label')}")
    
    # ========== CITATION STACKING ANALYSIS ==========
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
    
    # ========== FREQUENTLY CITED AUTHORS ==========
    frequently_cited = [a for a in sorted_authors if a['count'] >= 5]
    
    # ========== BASIC METRICS ==========
    unique_doi_count = len([r for r in results if r['doi']])
    current_year = datetime.now().year
    years_last_5 = sum(count for year, count in year_counter.items() if year >= current_year - 5)
    
    # ========== NEW METRICS ==========
    concepts_data = extract_concepts_from_references(results)
    geo_data = analyze_geographic_distribution(results)
    collab_data = analyze_collaboration_network(results)
    temporal_data = analyze_temporal_citations(results)
    yearly_stats = analyze_yearly_statistics(results)
    identifier_data = analyze_identifier_coverage(results)
    publisher_freq = analyze_publisher_frequency(results)  # This now uses the fixed publisher_counter
    journal_freq_all = analyze_journal_frequency_all(results)
    author_freq_all = analyze_author_frequency_all(results)
    orcid_data = analyze_orcid_coverage(results)
    language_data = analyze_language_distribution(results)
    predatory = detect_predatory_journals(results)
    shannon_authors = calculate_shannon_diversity(results, 'authors')
    shannon_journals = calculate_shannon_diversity(results, 'journals')
    shannon_publishers = calculate_shannon_diversity(results, 'publishers')  # This now uses fixed publisher_counter
    citation_classics = identify_citation_classics(results)
    
    # Collect self-citations
    self_citation_refs = [r for r in results if r.get('is_self_citation', False)]
    
    # Debug info (can be removed in production)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Publisher Source Statistics")
    st.sidebar.markdown(f"Crossref only: {publisher_sources['crossref']}")
    st.sidebar.markdown(f"OpenAlex only: {publisher_sources['openalex']}")
    st.sidebar.markdown(f"Total unique publishers: {len(publisher_counter)}")
    
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
        'crossref_only_refs': crossref_only_refs[:20],
        'openalex_only_refs': openalex_only_refs[:20],
        'suspicious_doi_refs': suspicious_doi_refs[:20],
        'citation_stacking': citation_stacking[:10],
        'frequently_cited': [f"{a['display_name']} — {a['count']}" for a in frequently_cited[:10]],
        'self_citations_count': len([r for r in results if r.get('is_self_citation', False)]),
        'self_citations_percent': (len([r for r in results if r.get('is_self_citation', False)]) / len(results) * 100) if results else 0,
        'self_citation_refs': self_citation_refs,
        
        # Enhanced data
        'concepts': concepts_data,
        'geography': geo_data,
        'collaboration': collab_data,
        'temporal': temporal_data,
        'yearly_stats': yearly_stats,
        'identifier_coverage': identifier_data,
        'publisher_frequency': {
            'all_publishers': [{'publisher': p, 'count': c, 'percentage': (c / len(results) * 100) if len(results) > 0 else 0} 
                               for p, c in publisher_counter.most_common()],
            'unique_publishers': len(publisher_counter),
            'top_10': [{'publisher': p, 'count': c, 'percentage': (c / len(results) * 100) if len(results) > 0 else 0} 
                       for p, c in publisher_counter.most_common(10)]
        },
        'journal_frequency_all': journal_freq_all,
        'author_frequency_all': author_freq_all,
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
        'avg_citations': sum(r.get('citations_count', 0) for r in results) / len(results) if results else 0,
        
        # Debug info (optional)
        'publisher_sources': publisher_sources
    }

# ======================== HELPER FUNCTION FOR AUTHOR HIGHLIGHTING ========================
def format_authors_with_highlight(authors_list: List[str], highlight_authors_norm_set: Set[str], normalize_func) -> str:
    """Format authors list with highlighting for self-citation authors"""
    if not authors_list:
        return ""
    
    formatted_authors = []
    for author in authors_list:
        # Normalize the author name for comparison
        norm_author, _ = normalize_func(author)
        
        # Check if normalized author is in the pre-normalized highlight set
        if norm_author in highlight_authors_norm_set:
            escaped_author = html.escape(author)
            formatted_authors.append(f'<span class="self-citation-author">{escaped_author}</span>')
        else:
            formatted_authors.append(html.escape(author))
    
    return ', '.join(formatted_authors)

def get_color_for_author(index: int) -> str:
    """Get a color for highlighting author based on index"""
    colors = [
        "#d9534f",  # red
        "#5bc0de",  # blue
        "#5cb85c",  # green
        "#f0ad4e",  # orange
        "#9b59b6",  # purple
        "#e67e22",  # orange-dark
        "#1abc9c",  # teal
        "#e74c3c",  # red-dark
        "#3498db",  # blue-dark
        "#2ecc71"   # green-dark
    ]
    return colors[index % len(colors)]

# ======================== HTML REPORT (ENGLISH, UPDATED) ========================
def generate_html_report_advanced(results: List[Dict], stats: Dict, paper_authors: Set[str] = None, lang: str = 'en', journal_name: str = '', article_number: str = '') -> str:
    """Generate enhanced HTML report with custom PNG icons instead of emojis"""
    import base64
    
    # Function to encode icon to base64 for embedding directly in HTML
    def encode_icon_base64(icon_path: str) -> str:
        """Encode PNG icon to base64 data URI"""
        try:
            with open(icon_path, "rb") as f:
                icon_data = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{icon_data}"
        except FileNotFoundError:
            # Fallback to emoji if icon not found
            return None
    
    # Define icon mapping with relative paths
    icon_base_path = "icons"  # Folder containing icons
    icons = {
        'overview': f"{icon_base_path}/overview.png",
        'identifiers': f"{icon_base_path}/identifiers.png",
        'authors': f"{icon_base_path}/authors.png",
        'journals': f"{icon_base_path}/journals.png",
        'publishers': f"{icon_base_path}/publishers.png",
        'yearly': f"{icon_base_path}/yearly.png",
        'concepts': f"{icon_base_path}/concepts.png",
        'geography': f"{icon_base_path}/geography.png",
        'collaboration': f"{icon_base_path}/collaboration.png",
        'diversity': f"{icon_base_path}/diversity.png",
        'classics': f"{icon_base_path}/classics.png",
        'self_citations': f"{icon_base_path}/self_citations.png",
        'crossref_only': f"{icon_base_path}/crossref_only.png",
        'openalex_only': f"{icon_base_path}/openalex_only.png",
        'suspicious_doi': f"{icon_base_path}/suspicious_doi.png",
        'non_doi': f"{icon_base_path}/non_doi.png",
        'url_sources': f"{icon_base_path}/url_sources.png",
        'problems': f"{icon_base_path}/problems.png",
        'full_list': f"{icon_base_path}/full_list.png",
        'total_refs': f"{icon_base_path}/total_refs.png",
        'doi_found': f"{icon_base_path}/doi_found.png",
        'self_citations_alt': f"{icon_base_path}/self_citations_alt.png",
        'total_citations': f"{icon_base_path}/total_citations.png",
        'avg_citations': f"{icon_base_path}/avg_citations.png"
    }
    
    # Encode all icons to base64
    icon_data_uris = {}
    for key, path in icons.items():
        data_uri = encode_icon_base64(path)
        if data_uri:
            icon_data_uris[key] = data_uri
        else:
            # Provide emoji fallback
            emoji_fallbacks = {
                'overview': '📊',
                'identifiers': '🔍',
                'authors': '👨‍🎓',
                'journals': '📖',
                'publishers': '🏢',
                'yearly': '📅',
                'concepts': '🧠',
                'geography': '🌍',
                'collaboration': '🤝',
                'diversity': '🔄',
                'classics': '⭐',
                'self_citations': '📝',
                'crossref_only': '⚠️',
                'openalex_only': '⚠️',
                'suspicious_doi': '🔍',
                'non_doi': '📄',
                'url_sources': '🔗',
                'problems': '⚠️',
                'full_list': '📋',
                'total_refs': '📄',
                'doi_found': '🔗',
                'self_citations_alt': '🔄',
                'total_citations': '📊',
                'avg_citations': '⭐'
            }
            icon_data_uris[key] = emoji_fallbacks.get(key, '•')
    
    # Helper function to render icon or fallback
    def render_icon(icon_key: str, size: str = "24px") -> str:
        """Render icon as img or fallback emoji"""
        uri = icon_data_uris.get(icon_key)
        if uri and uri.startswith('data:image'):
            return f'<img src="{uri}" style="width: {size}; height: {size}; vertical-align: middle; margin-right: 8px;" alt="{icon_key}">'
        else:
            return f'<span style="font-size: {size}; margin-right: 8px;">{uri}</span>'
    
    # Load and encode logo
    logo_base64 = ""
    try:
        with open("logo.png", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        pass
    
    # Set default journal name
    if not journal_name or journal_name.strip() == '':
        journal_name_display = "Chimica Techno Acta"
    else:
        journal_name_display = html.escape(journal_name)
    
    article_number_display = html.escape(article_number) if article_number and article_number.strip() else ""
    
    # Determine if self-citations section should be shown
    show_self_citations_section = paper_authors and len(paper_authors) > 0
    
    # Helper functions for clickable links
    def make_clickable_doi(doi):
        if doi:
            return f'<a href="https://doi.org/{doi}" target="_blank" class="clickable-link">{html.escape(doi)}</a>'
        return get_text('html_not_found')
    
    def make_clickable_orcid(orcid):
        if orcid:
            return f'<a href="{orcid}" target="_blank" class="clickable-link">{html.escape(orcid)}</a>'
        return ''
    
    # Prepare self-citation authors highlighting
    paper_authors_set = set()
    paper_authors_colors = {}
    if show_self_citations_section and paper_authors:
        for idx, author in enumerate(paper_authors):
            paper_authors_set.add(author)
            paper_authors_colors[author] = get_color_for_author(idx)
    
    # Generate authors display for self-citation section header
    authors_header_html = ""
    if show_self_citations_section and paper_authors_set:
        authors_header_parts = []
        for author in paper_authors_set:
            escaped_author = html.escape(author)
            color = paper_authors_colors[author]
            authors_header_parts.append(f'<span style="color: {color}; font-weight: bold;">{escaped_author}</span>')
        authors_header_html = f'<div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;"><strong>{get_text("html_self_citation_authors_label")}:</strong> {", ".join(authors_header_parts)}</div>'
    
    # Generate self-citations section
    self_citations_html = ""
    if show_self_citations_section:
        if stats.get('self_citation_refs'):
            for ref in stats.get('self_citation_refs', []):
                authors_full_list = ref.get('authors_display', [])
                
                normalized_paper_authors = set()
                paper_author_display = {}
                
                for idx, author in enumerate(paper_authors_set):
                    norm, display = normalize_author_name(author)
                    normalized_paper_authors.add(norm)
                    color = get_color_for_author(idx)
                    paper_author_display[norm] = {'display': display, 'color': color}
                
                def format_authors_with_colors(authors_list, paper_norm_set, color_map):
                    if not authors_list:
                        return ""
                    
                    formatted_authors = []
                    for author in authors_list:
                        norm_author, _ = normalize_author_name(author)
                        
                        if norm_author in paper_norm_set:
                            escaped_author = html.escape(author)
                            color = color_map.get(norm_author, {}).get('color', '#d9534f')
                            formatted_authors.append(f'<span style="color: {color}; font-weight: bold; background-color: {color}20; padding: 2px 4px; border-radius: 3px;">{escaped_author}</span>')
                        else:
                            formatted_authors.append(html.escape(author))
                    
                    return ', '.join(formatted_authors)
                
                color_map = {}
                for idx, author in enumerate(paper_authors_set):
                    norm, display = normalize_author_name(author)
                    color = get_color_for_author(idx)
                    color_map[norm] = {'display': display, 'color': color}
                
                formatted_authors = format_authors_with_colors(authors_full_list, normalized_paper_authors, color_map)
                original_text_full = html.escape(ref.get('original_text', ''))
                doi_info = f'<div style="font-size: 13px; margin-top: 8px;">🔗 DOI: {make_clickable_doi(ref.get("doi"))}</div>' if ref.get('doi') else ''
                journal_info = f'<div style="font-size: 13px; margin-top: 5px;">📖 {get_text("journal")}: {html.escape(ref.get("journal", "Unknown"))}</div>' if ref.get('journal') else ''
                year_info = f'<div style="font-size: 13px; margin-top: 5px;">📅 {get_text("year")}: {ref.get("year", "Unknown")}</div>' if ref.get('year') else ''
                
                self_citations_html += f"""
                <div class="rank-item" style="margin-bottom: 15px;">
                    <div><strong>📄 Reference:</strong></div>
                    <div class="full-text-container">{original_text_full}</div>
                    <div style="font-size: 13px; margin-top: 8px;">👨‍🎓 {get_text("authors")}: {formatted_authors}</div>
                    {doi_info}
                    {journal_info}
                    {year_info}
                </div>
                """
        else:
            self_citations_html = f'<p>{get_text("no_problematic")}</p>'
    
    # Generate full reference list
    full_references_html = ""
    for idx, result in enumerate(results[:300]):
        authors_full_list = result.get('authors_display', [])
        normalized_paper_authors_full = set()
        for author in paper_authors_set:
            norm, _ = normalize_author_name(author)
            normalized_paper_authors_full.add(norm)
        
        if show_self_citations_section and result.get('is_self_citation'):
            formatted_authors = format_authors_with_highlight(authors_full_list, normalized_paper_authors_full, normalize_author_name)
        else:
            formatted_authors = ', '.join([html.escape(a) for a in authors_full_list]) if authors_full_list else ""
        
        original_text_full = html.escape(result.get('original_text', ''))
        doi_info = f'<div style="font-size: 13px; margin-top: 5px;">🔗 DOI: {make_clickable_doi(result.get("doi"))}</div>' if result.get('doi') else ''
        status_icon = "⚠️" if result.get('is_suspicious_doi') else ("✅" if result.get('doi') else "❌")
        
        full_references_html += f"""
        <div class="rank-item" style="margin-bottom: 15px;">
            <div><strong>{status_icon} Reference {idx + 1}:</strong></div>
            <div class="full-text-container">{original_text_full}</div>
            <div style="font-size: 13px; margin-top: 5px;">👨‍🎓 {get_text("authors")}: {formatted_authors}</div>
            {doi_info}
        </div>
        """
    
    # Build the complete HTML
    html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Reference List Analysis</title>
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
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
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
            display: flex;
            align-items: center;
        }}
        .sidebar a {{
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 8px;
            transition: all 0.3s;
            gap: 12px;
        }}
        .sidebar a:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }}
        .sidebar-icon {{
            width: 20px;
            height: 20px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .main-content {{
            margin-left: 280px;
            padding: 30px 40px;
        }}
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
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }}
        .header .date {{
            opacity: 0.9;
        }}
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
        .stat-card-icon {{
            width: 40px;
            height: 40px;
            margin: 0 auto 12px auto;
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
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }}
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
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .concept-icon {{
            width: 28px;
            height: 28px;
        }}
        .concept-name {{
            font-weight: 600;
            color: #667eea;
            flex: 1;
        }}
        .concept-score {{
            font-size: 12px;
            color: #666;
        }}
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
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .clickable-link {{
            color: #667eea;
            text-decoration: none;
            transition: all 0.3s;
        }}
        .clickable-link:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        .full-text-container {{
            max-height: 150px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 12px;
            background: #f5f5f5;
            padding: 8px;
            border-radius: 5px;
            margin-top: 5px;
        }}
        .self-citation-author {{
            color: #d9534f;
            font-weight: bold;
            background-color: #f8d7da;
            padding: 2px 4px;
            border-radius: 3px;
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
        <h3>{render_icon('overview', '22px')} {get_text('html_overview')}</h3>
        <a href="#overview">{render_icon('overview', '18px')} {get_text('html_overview')}</a>
        <a href="#identifiers">{render_icon('identifiers', '18px')} {get_text('html_identifier_coverage')}</a>
        <a href="#authors">{render_icon('authors', '18px')} {get_text('html_authors')}</a>
        <a href="#journals">{render_icon('journals', '18px')} {get_text('html_journals')}</a>
        <a href="#publishers">{render_icon('publishers', '18px')} {get_text('html_publishers')}</a>
        <a href="#yearly">{render_icon('yearly', '18px')} {get_text('html_yearly')}</a>
        <a href="#concepts">{render_icon('concepts', '18px')} {get_text('html_concepts')}</a>
        <a href="#geography">{render_icon('geography', '18px')} {get_text('html_geography')}</a>
        <a href="#collaboration">{render_icon('collaboration', '18px')} {get_text('html_collaborations')}</a>
        <a href="#diversity">{render_icon('diversity', '18px')} {get_text('html_diversity')}</a>
        <a href="#classics">{render_icon('classics', '18px')} {get_text('html_classics')}</a>
        {f'<a href="#selfcitations">{render_icon("self_citations", "18px")} {get_text("html_self_citations")}</a>' if show_self_citations_section else ''}
        <a href="#crossref_only">{render_icon('crossref_only', '18px')} {get_text('html_crossref_only')}</a>
        <a href="#openalex_only">{render_icon('openalex_only', '18px')} {get_text('html_openalex_only')}</a>
        <a href="#suspicious_doi">{render_icon('suspicious_doi', '18px')} {get_text('html_suspicious_doi')}</a>
        <a href="#non_doi">{render_icon('non_doi', '18px')} {get_text('html_non_doi')}</a>
        <a href="#url_sources">{render_icon('url_sources', '18px')} {get_text('html_url_sources')}</a>
        <a href="#problems">{render_icon('problems', '18px')} {get_text('html_problems')}</a>
        <a href="#full_reference_list">{render_icon('full_list', '18px')} 📋 Full Reference List</a>
    </div>
    
    <div class="main-content">
        <div class="header">
            <div style="display: flex; justify-content: center; margin-bottom: 15px;">
                <img src="data:image/png;base64,{logo_base64}" style="height: 150px; width: auto;">
            </div>
            <div style="margin-top: 10px;"><strong>{get_text('html_journal_label')}:</strong> {journal_name_display}</div>
            {f'<div><strong>{get_text("html_article_number_label")}:</strong> {article_number_display}</div>' if article_number_display else ''}
            <div class="date">{get_text('html_generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
            <div style="margin-top: 15px;">
                <span class="badge badge-success">✅ Crossref + OpenAlex</span>
                <span class="badge badge-info">📊 {stats['total_references']} {get_text('total_references')}</span>
            </div>
        </div>
        
        <div id="overview" class="section">
            <div class="section-title">{render_icon('overview', '28px')} {get_text('html_overview')}</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-card-icon">{render_icon('total_refs', '32px')}</div>
                    <div class="stat-number">{stats['total_references']}</div>
                    <div class="stat-label">{get_text('total_references')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon">{render_icon('doi_found', '32px')}</div>
                    <div class="stat-number">{stats['total_with_doi']}</div>
                    <div class="stat-label">{get_text('doi_found')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon">{render_icon('yearly', '32px')}</div>
                    <div class="stat-number">{stats['yearly_stats']['last_5_years']}</div>
                    <div class="stat-label">{get_text('last_5_years')}</div>
                </div>
                {f'''
                <div class="stat-card">
                    <div class="stat-card-icon">{render_icon('self_citations_alt', '32px')}</div>
                    <div class="stat-number">{stats['self_citations_count']}</div>
                    <div class="stat-label">{get_text('self_citations')}</div>
                </div>
                ''' if show_self_citations_section else ''}
                <div class="stat-card">
                    <div class="stat-card-icon">{render_icon('total_citations', '32px')}</div>
                    <div class="stat-number">{stats.get('total_citations_sum', 0)}</div>
                    <div class="stat-label">{get_text('total_citations')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon">{render_icon('avg_citations', '32px')}</div>
                    <div class="stat-number">{stats.get('avg_citations', 0):.1f}</div>
                    <div class="stat-label">{get_text('avg_citations')}</div>
                </div>
            </div>
        </div>
        
        <div id="identifiers" class="section">
            <div class="section-title">{render_icon('identifiers', '28px')} {get_text('html_identifier_coverage')}</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['identifier_coverage']['stats']['has_doi']}</div>
                    <div class="stat-label">{get_text('doi_found')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['identifier_coverage']['stats']['has_url']}</div>
                    <div class="stat-label">URL</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['identifier_coverage']['stats']['has_arxiv']}</div>
                    <div class="stat-label">arXiv</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['identifier_coverage']['stats']['has_pmid']}</div>
                    <div class="stat-label">PMID</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['identifier_coverage']['stats']['has_isbn']}</div>
                    <div class="stat-label">ISBN</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['identifier_coverage']['stats']['has_none']}</div>
                    <div class="stat-label">{get_text('no_identifier')}</div>
                </div>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['both']}</div>
                    <div class="stat-label">✅ Crossref + OpenAlex</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['crossref_only']}</div>
                    <div class="stat-label">{render_icon('crossref_only', '16px')} {get_text('only_crossref')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['openalex_only']}</div>
                    <div class="stat-label">{render_icon('openalex_only', '16px')} {get_text('only_openalex')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['none']}</div>
                    <div class="stat-label">❌ {get_text('status_none')}</div>
                </div>
            </div>
        </div>
        
        <div id="authors" class="section">
            <div class="section-title">{render_icon('authors', '28px')} {get_text('html_authors')}</div>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{html.escape(author["display_name"])}</span><span class="rank-count">{author["count"]} {get_text("html_citations_label")}</span>' + (f'<div style="font-size: 11px; color: #667eea;">🔗 ORCID: {make_clickable_orcid(author["orcid"])}</div>' if author.get("orcid") else '') + (f'<div style="font-size: 11px; color: #666;">🏛 {html.escape(author["institution"][:50])}</div>' if author.get("institution") else '') + '<div class="progress-bar"><div class="progress-fill" style="width: ' + str(min(100, author["count"] / stats["author_frequency_all"]["all_authors"][0]["count"] * 100 if stats["author_frequency_all"]["all_authors"] else 0)) + '%;"></div></div></div>' for i, author in enumerate(stats["author_frequency_all"]["all_authors"][:30])])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text('unique_authors')}: {stats['author_frequency_all']['unique_authors']}</span>
                <span class="badge badge-info">{get_text('shannon_authors')}: {stats['shannon_index']['authors']}</span>
                <span class="badge badge-info">{get_text('orcid_coverage')}: {stats['orcid_coverage']['with_orcid']} ({stats['orcid_coverage']['coverage_percent']:.1f}%)</span>
            </div>
        </div>
        
        <div id="journals" class="section">
            <div class="section-title">{render_icon('journals', '28px')} {get_text('html_journals')}</div>
            <table>
                <thead>
                    <tr><th>{get_text('html_rank')}</th><th>{get_text('journal')}</th><th>{get_text('html_count')}</th><th>{get_text('html_percentage')}</th></tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{i+1}</td><td>{html.escape(journal["journal"])}</td><td>{journal["count"]}</td><td>{journal["percentage"]:.1f}%</td></tr>' for i, journal in enumerate(stats["journal_frequency_all"]["all_journals"])])}
                </tbody>
            </table>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text('unique_journals')}: {stats['journal_frequency_all']['unique_journals']}</span>
                <span class="badge badge-info">{get_text('shannon_journals')}: {stats['shannon_index']['journals']}</span>
            </div>
        </div>
        
        <div id="publishers" class="section">
            <div class="section-title">{render_icon('publishers', '28px')} {get_text('html_publishers')}</div>
            <table>
                <thead>
                    <tr><th>{get_text('html_rank')}</th><th>{get_text('publisher')}</th><th>{get_text('html_count')}</th><th>{get_text('html_percentage')}</th></tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{i+1}</td><td>{html.escape(publisher["publisher"])}</td><td>{publisher["count"]}</td><td>{publisher["percentage"]:.1f}%</td></tr>' for i, publisher in enumerate(stats["publisher_frequency"]["all_publishers"])])}
                </tbody>
            </table>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text('unique_publishers_metric')}: {stats['publisher_frequency']['unique_publishers']}</span>
                <span class="badge badge-info">{get_text('shannon_publishers')}: {stats['shannon_index']['publishers']}</span>
            </div>
        </div>
        
        <div id="yearly" class="section">
            <div class="section-title">{render_icon('yearly', '28px')} {get_text('html_yearly')}</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['last_3_years']} ({stats['yearly_stats']['last_3_years_percent']:.1f}%)</div>
                    <div class="stat-label">{get_text('last_3_years')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['last_5_years']} ({stats['yearly_stats']['last_5_years_percent']:.1f}%)</div>
                    <div class="stat-label">{get_text('last_5_years_metric')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['last_10_years']} ({stats['yearly_stats']['last_10_years_percent']:.1f}%)</div>
                    <div class="stat-label">{get_text('last_10_years')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['unknown_year']}</div>
                    <div class="stat-label">{get_text('references_with_unknown_year')}</div>
                </div>
            </div>
            <div>
                <h4>{get_text('yearly_distribution')}</h4>
                {''.join([f'<div class="rank-item"><span class="rank-name">{year}</span><span class="rank-count">{stats["yearly_stats"]["yearly_counts"][year]} {get_text("references_count")} ({stats["yearly_stats"]["yearly_percentages"][year]:.1f}%)</span><div class="progress-bar"><div class="progress-fill" style="width: {stats["yearly_stats"]["yearly_percentages"][year]}%;"></div></div></div>' for year in sorted(stats["yearly_stats"]["yearly_counts"].keys(), reverse=True)])}
            </div>
            <div style="margin-top: 15px;">
                <h4>{get_text('cumulative_percentage')}</h4>
                {''.join([f'<div class="rank-item"><span class="rank-name">{year}</span><span class="rank-count">{stats["yearly_stats"]["cumulative_percentages"][year]:.1f}% {get_text("cumulative")}</span><div class="progress-bar"><div class="progress-fill" style="width: {stats["yearly_stats"]["cumulative_percentages"][year]}%;"></div></div></div>' for year in sorted(stats["yearly_stats"]["yearly_counts"].keys(), reverse=True)])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text('median_age')}: {stats['temporal']['median_age']} {get_text('years')}</span>
                <span class="badge badge-info">{get_text('average_age')}: {stats['temporal']['average_age']:.1f} {get_text('years')}</span>
            </div>
        </div>
        
        <div id="concepts" class="section">
            <div class="section-title">{render_icon('concepts', '28px')} {get_text('html_concepts')}</div>
            <div class="concepts-grid">
                {''.join([f'<div class="concept-card"><div class="concept-icon">{render_icon("concepts", "24px")}</div><div class="concept-name">{html.escape(concept[0])}</div><div class="concept-score">{get_text("html_frequency")}: {concept[1]}</div></div>' for concept in stats['concepts']['concepts'][:12]])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text('unique_concepts')}: {stats['concepts']['unique_concepts']}</span>
            </div>
        </div>
        
        <div id="geography" class="section">
            <div class="section-title">{render_icon('geography', '28px')} {get_text('html_geography')}</div>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-name">{html.escape(country)}</span><span class="rank-count">{count} {get_text("html_authors_count")}</span><div class="progress-bar"><div class="progress-fill" style="width: {count / max(stats["geography"]["countries"].values()) * 100 if stats["geography"]["countries"] else 0}%;"></div></div></div>' for country, count in list(stats['geography']['countries'].items())[:10]])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text('total_countries')}: {stats['geography']['total_countries']}</span>
                <span class="badge badge-info">{get_text('international_collaboration')}: {stats['geography']['international_percent']:.1f}%</span>
            </div>
        </div>
        
        <div id="collaboration" class="section">
            <div class="section-title">{render_icon('collaboration', '28px')} {get_text('html_collaborations')}</div>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{html.escape(collab["author1"])} + {html.escape(collab["author2"])}</span><span class="rank-count">{collab["count"]} {get_text("html_works")}</span></div>' for i, collab in enumerate(stats["collaboration"]["top_collaborations"][:8])])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text('core_authors_label')}: {', '.join([f"{html.escape(author[0])} ({author[1]} {get_text('html_connections')})" for author in stats['collaboration']['core_authors'][:5]])}</span>
            </div>
        </div>
        
        <div id="diversity" class="section">
            <div class="section-title">{render_icon('diversity', '28px')} {get_text('html_diversity')}</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['shannon_index']['authors']}</div>
                    <div class="stat-label">{get_text('shannon_authors')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['shannon_index']['journals']}</div>
                    <div class="stat-label">{get_text('shannon_journals')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['shannon_index']['publishers']}</div>
                    <div class="stat-label">{get_text('shannon_publishers')}</div>
                </div>
            </div>
        </div>
        
        <div id="classics" class="section">
            <div class="section-title">{render_icon('classics', '28px')} {get_text('html_classics')}</div>
            {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{html.escape(classic["title"] if classic["title"] else "Unknown")}</span><span class="rank-count">📊 {classic["citations"]} {get_text("html_citations_label")}</span><div style="font-size: 12px; color: #666; margin-top: 5px;">{html.escape(classic["journal"] if classic["journal"] else "Unknown")} ({classic["year"] if classic["year"] else "Unknown"})</div>' + (f'<div style="font-size: 11px; margin-top: 5px;">🔗 DOI: {make_clickable_doi(classic["doi"])}</div>' if classic.get("doi") else '') + '</div>' for i, classic in enumerate(stats['citation_classics'][:8])]) if stats['citation_classics'] else f'<p>{get_text("no_citation_classics")}</p>'}
        </div>
        
        {f'''
        <div id="selfcitations" class="section">
            <div class="section-title">{render_icon('self_citations', '28px')} {get_text('html_self_citations')}</div>
            {authors_header_html}
            {self_citations_html}
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text('html_total_self_citations')}: {stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)</span>
            </div>
        </div>
        ''' if show_self_citations_section else ''}
        
        <div id="crossref_only" class="section">
            <div class="section-title">{render_icon('crossref_only', '28px')} {get_text('html_crossref_only')}</div>
            {''.join([f'<div class="rank-item"><div>📄 {html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">🔗 DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('crossref_only_refs', [])[:20]]) if stats.get('crossref_only_refs') else f'<p>{get_text("no_crossref_only")}</p>'}
        </div>
        
        <div id="openalex_only" class="section">
            <div class="section-title">{render_icon('openalex_only', '28px')} {get_text('html_openalex_only')}</div>
            {''.join([f'<div class="rank-item"><div>📄 {html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">🔗 DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('openalex_only_refs', [])[:20]]) if stats.get('openalex_only_refs') else f'<p>{get_text("no_openalex_only")}</p>'}
        </div>
        
        <div id="suspicious_doi" class="section">
            <div class="section-title">{render_icon('suspicious_doi', '28px')} {get_text('html_suspicious_dois')}</div>
            {''.join([f'<div class="rank-item"><div class="badge badge-danger">{get_text("html_attention")}</div><div>📄 {html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">🔗 DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('suspicious_doi_refs', [])[:20]]) if stats.get('suspicious_doi_refs') else f'<p>{get_text("no_suspicious_dois")}</p>'}
        </div>
        
        <div id="non_doi" class="section">
            <div class="section-title">{render_icon('non_doi', '28px')} {get_text('html_non_doi')}</div>
            {''.join([f'<div class="rank-item">📄 {html.escape(ref)}</div>' for ref in stats['identifier_coverage']['references_without_doi'][:20]]) if stats['identifier_coverage']['references_without_doi'] else f'<p>{get_text("all_have_doi")}</p>'}
        </div>
        
        <div id="url_sources" class="section">
            <div class="section-title">{render_icon('url_sources', '28px')} {get_text('html_url_sources')}</div>
            {''.join([f'<div class="rank-item">🔗 {html.escape(ref)}</div>' for ref in stats['identifier_coverage']['references_with_only_url'][:20]]) if stats['identifier_coverage']['references_with_only_url'] else f'<p>{get_text("no_url_only")}</p>'}
        </div>
        
        <div id="problems" class="section">
            <div class="section-title">{render_icon('problems', '28px')} {get_text('html_problems')}</div>
            {''.join([f'<div class="rank-item"><span class="badge badge-danger">⚠️ {html.escape(ref["problems"])}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div></div>' for ref in stats['problematic_refs'][:10]]) if stats['problematic_refs'] else f'<p>{get_text("no_problematic")}</p>'}
            {f'<div style="margin-top: 15px;"><h4>{get_text("predatory_journals")}:</h4>{"".join([f"<div class=rank-item>📕 {html.escape(pred['journal'])}<br><span style=font-size:12px;color:#666;>{', '.join([html.escape(s) for s in pred['signs']])}</span></div>" for pred in stats['predatory_journals'][:5]])}</div>' if stats['predatory_journals'] else ''}
        </div>
        
        <div id="full_reference_list" class="section">
            <div class="section-title">{render_icon('full_list', '28px')} 📋 Full Reference List</div>
            {full_references_html}
            {f'<p style="margin-top: 15px; color: #666;">Showing first 300 of {len(results)} references</p>' if len(results) > 300 else ''}
        </div>
        
        <div class="footer">
            Report automatically generated.<br>
            © Comprehensive Reference List Analysis / Created by daM / Chimica Techno Acta <a href="https://chimicatechnoacta.ru" target="_blank">https://chimicatechnoacta.ru</a>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

# ======================== UI INTERFACE (ENGLISH, UPDATED) ========================
def main():
    # Language selector in sidebar (before anything else)
    with st.sidebar:
        st.markdown(f"## {get_text('language')}")
        lang_option = st.selectbox(
            "",
            options=['en', 'ru'],
            format_func=lambda x: get_text('language_english') if x == 'en' else get_text('language_russian'),
            index=0 if st.session_state.language == 'en' else 1
        )
        if lang_option != st.session_state.language:
            st.session_state.language = lang_option
            st.rerun()
        st.markdown("---")
    
    st.image("logo.png", width=250)
    st.markdown("---")
    st.markdown(f"### {get_text('app_subtitle')}")
    st.markdown("---")
    
    with st.sidebar:
        st.markdown(f"## {get_text('settings')}")
        batch_size = st.slider(get_text('batch_size'), 10, 100, 50, help=get_text('batch_size_help'))
        
        st.markdown("---")
        st.markdown(f"## {get_text('paper_authors')}")
        st.markdown(f"*{get_text('paper_authors_help')}*")
        st.markdown(get_text('format_hint'))
        st.markdown(get_text('separator_hint'))
        
        authors_input = st.text_area(
            get_text('paper_authors'),
            placeholder=get_text('authors_placeholder'),
            help=get_text('paper_authors_help')
        )
        
        paper_authors = set()
        if authors_input:
            paper_authors = parse_paper_authors(authors_input)
            if paper_authors:
                st.success(get_text('authors_added').format(len(paper_authors)))
            else:
                st.warning(get_text('authors_warning'))
        
        st.markdown("---")
        st.markdown(f"## {get_text('journal_name_label')}")
        journal_name_input = st.text_input(
            get_text('journal_name_label'),
            placeholder="Chimica Techno Acta",
            help=get_text('journal_name_help'),
            key="journal_name_input"
        )
        if journal_name_input:
            st.session_state.journal_name = journal_name_input
        else:
            st.session_state.journal_name = ""
        
        st.markdown(f"## {get_text('article_number_label')}")
        article_number_input = st.text_input(
            get_text('article_number_label'),
            placeholder="1224, CTA-1234, CTA/1224",
            help=get_text('article_number_help'),
            key="article_number_input"
        )
        if article_number_input:
            st.session_state.article_number = article_number_input
        else:
            st.session_state.article_number = ""
        
        st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs([get_text('tab_upload'), get_text('tab_analytics'), get_text('tab_report')])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.header(get_text('upload_header'))
        
        input_method = st.radio(get_text('input_method'), [get_text('text_paste'), get_text('file_upload')])
        
        references_text = ""
        
        if input_method == get_text('text_paste'):
            references_text = st.text_area(
                get_text('text_paste'),
                height=400,
                placeholder=get_text('paste_placeholder')
            )
        else:
            uploaded_file = st.file_uploader(get_text('file_upload'), type=['txt'])
            if uploaded_file:
                references_text = uploaded_file.read().decode('utf-8')
                st.success(get_text('upload_success').format(len(references_text)))
        
        if st.button(get_text('start_analysis'), type="primary", disabled=not references_text.strip()):
            if references_text.strip():
                with st.spinner(get_text('parsing')):
                    references = parse_reference_list(references_text)
                    st.info(get_text('found_refs').format(len(references)))
                    
                    with st.expander(get_text('preview')):
                        for i, ref in enumerate(references[:3]):
                            st.text(f"{i+1}. {ref[:200]}...")
                
                if len(references) > 2000:
                    st.error(get_text('limit_exceeded').format(len(references)))
                else:
                    with st.spinner(get_text('searching_duplicates')):
                        duplicates = find_duplicate_references(references)
                        if duplicates:
                            st.warning(get_text('found_duplicates').format(len(duplicates)))
                            with st.expander(get_text('view_duplicates')):
                                for dup in duplicates[:10]:
                                    st.text(f"Reference {dup['index1']+1} and {dup['index2']+1}")
                                    st.text(f"{get_text('reason')}: {dup['reason']}")
                                    st.markdown("---")
                    
                    st.session_state['references'] = references
                    st.session_state['paper_authors'] = paper_authors
                    st.session_state['batch_size'] = batch_size
                    st.session_state['analysis_started'] = True
                    
                    with st.spinner(get_text('analysis_started')):
                        # Use the optimized analysis function
                        results = analyze_all_references(references, batch_size, paper_authors if paper_authors else None)
                        st.session_state['results'] = results
                        st.session_state['analysis_complete'] = True
                    
                    st.success(get_text('analysis_complete').format(len([r for r in results if r['doi']]), len(results)))
                    st.balloons()
                    st.info(get_text('go_to_analytics'))
            else:
                st.warning(get_text('enter_reference_list'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
            results = st.session_state['results']
            paper_authors = st.session_state.get('paper_authors', set())
            
            with st.spinner(get_text('analysis_started')):
                stats = generate_advanced_statistics(results)
            
            st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['total_references']}</div>
                    <div class="metric-label">{get_text('total_references')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['total_with_doi']} ({stats['total_with_doi']/stats['total_references']*100 if stats['total_references'] > 0 else 0:.0f}%)</div>
                    <div class="metric-label">{get_text('doi_found')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['yearly_stats']['last_5_years']}</div>
                    <div class="metric-label">{get_text('last_5_years')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)</div>
                    <div class="metric-label">{get_text('self_citations')}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats.get('total_citations_sum', 0)}</div>
                    <div class="metric-label">{get_text('total_citations')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col6:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats.get('avg_citations', 0):.1f}</div>
                    <div class="metric-label">{get_text('avg_citations')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col7:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['orcid_coverage']['coverage_percent']:.1f}%</div>
                    <div class="metric-label">{get_text('orcid_coverage')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col8:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{stats['publisher_frequency']['unique_publishers']}</div>
                    <div class="metric-label">{get_text('unique_publishers')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Custom tabs implementation with buttons
            st.markdown(f"### {get_text('analysis_sections')}")
            
            # Initialize session state for active tab if not exists
            if 'active_tab' not in st.session_state:
                st.session_state.active_tab = "metrics"
            
            # Define tabs configuration
            tabs_config = [
                {"id": "metrics", "icon": "📊", "title": get_text('total_references'), "subtitle": get_text('html_overview')},
                {"id": "identifiers", "icon": "🔍", "title": get_text('identifier_coverage'), "subtitle": get_text('html_identifier_coverage')},
                {"id": "authors", "icon": "👨‍🎓", "title": get_text('authors'), "subtitle": get_text('html_authors')},
                {"id": "journals", "icon": "📖", "title": get_text('journal'), "subtitle": get_text('html_journals')},
                {"id": "publishers", "icon": "🏢", "title": get_text('publisher'), "subtitle": get_text('html_publishers')},
                {"id": "yearly", "icon": "📅", "title": get_text('yearly_stats'), "subtitle": get_text('html_yearly')},
                {"id": "concepts", "icon": "🧠", "title": get_text('key_concepts'), "subtitle": get_text('html_concepts')},
                {"id": "geography", "icon": "🌍", "title": get_text('geographic_distribution'), "subtitle": get_text('html_geography')},
                {"id": "collaboration", "icon": "🤝", "title": get_text('collaboration_networks'), "subtitle": get_text('html_collaborations')},
                {"id": "diversity", "icon": "🔄", "title": get_text('diversity_analysis'), "subtitle": get_text('html_diversity')},
                {"id": "classics", "icon": "⭐", "title": get_text('citation_classics'), "subtitle": get_text('html_classics')},
                {"id": "crossref_only", "icon": "⚠️", "title": get_text('crossref_only'), "subtitle": get_text('html_crossref_only')},
                {"id": "openalex_only", "icon": "⚠️", "title": get_text('openalex_only'), "subtitle": get_text('html_openalex_only')},
                {"id": "suspicious", "icon": "🔍", "title": get_text('suspicious_dois'), "subtitle": get_text('html_suspicious_doi')},
                {"id": "non_doi", "icon": "📄", "title": get_text('non_doi_sources'), "subtitle": get_text('html_non_doi')},
                {"id": "url_sources", "icon": "🔗", "title": get_text('url_sources'), "subtitle": get_text('html_url_sources')},
                {"id": "problems", "icon": "⚠️", "title": get_text('problematic_refs'), "subtitle": get_text('html_problems')}
            ]
            
            # Create buttons in rows of 6
            cols_per_row = 6
            for i in range(0, len(tabs_config), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(tabs_config):
                        tab = tabs_config[i + j]
                        if col.button(
                            f"{tab['icon']}\n{tab['title']}\n{tab['subtitle']}",
                            key=f"tab_{tab['id']}",
                            use_container_width=True
                        ):
                            st.session_state.active_tab = tab["id"]
                            st.rerun()
            
            st.markdown("---")
            
            # Display content based on active tab
            active_tab = st.session_state.active_tab
            
            if active_tab == "metrics":
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {get_text('doi_status')}")
                    doi_data = pd.DataFrame([
                        {"Status": get_text('status_both'), "Count": stats['doi_status']['both']},
                        {"Status": get_text('status_crossref_only'), "Count": stats['doi_status']['crossref_only']},
                        {"Status": get_text('status_openalex_only'), "Count": stats['doi_status']['openalex_only']},
                        {"Status": get_text('status_none'), "Count": stats['doi_status']['none']}
                    ])
                    st.dataframe(doi_data, use_container_width=True)
                
                with col2:
                    st.markdown(f"### {get_text('citation_metrics')}")
                    st.metric(get_text('total_citations'), stats.get('total_citations_sum', 0))
                    st.metric(get_text('avg_citations'), f"{stats.get('avg_citations', 0):.1f}")
                    st.metric(get_text('self_citations'), f"{stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)")
            
            elif active_tab == "identifiers":
                st.markdown(f"### {get_text('identifier_coverage')}")
                id_df = pd.DataFrame([
                    {"Identifier type": "DOI", "Count": stats['identifier_coverage']['stats']['has_doi'], "Percentage": f"{stats['identifier_coverage']['stats']['has_doi']/stats['total_references']*100:.1f}%"},
                    {"Identifier type": "URL", "Count": stats['identifier_coverage']['stats']['has_url'], "Percentage": f"{stats['identifier_coverage']['stats']['has_url']/stats['total_references']*100:.1f}%"},
                    {"Identifier type": "arXiv", "Count": stats['identifier_coverage']['stats']['has_arxiv'], "Percentage": f"{stats['identifier_coverage']['stats']['has_arxiv']/stats['total_references']*100:.1f}%"},
                    {"Identifier type": "PMID", "Count": stats['identifier_coverage']['stats']['has_pmid'], "Percentage": f"{stats['identifier_coverage']['stats']['has_pmid']/stats['total_references']*100:.1f}%"},
                    {"Identifier type": "ISBN", "Count": stats['identifier_coverage']['stats']['has_isbn'], "Percentage": f"{stats['identifier_coverage']['stats']['has_isbn']/stats['total_references']*100:.1f}%"},
                    {"Identifier type": "No identifier", "Count": stats['identifier_coverage']['stats']['has_none'], "Percentage": f"{stats['identifier_coverage']['stats']['has_none']/stats['total_references']*100:.1f}%"},
                    {"Identifier type": "Multiple identifiers", "Count": stats['identifier_coverage']['stats']['multiple'], "Percentage": f"{stats['identifier_coverage']['stats']['multiple']/stats['total_references']*100:.1f}%"}
                ])
                st.dataframe(id_df, use_container_width=True)
                
                if stats['identifier_coverage']['references_without_any']:
                    st.markdown(f"### {get_text('references_without_any')}")
                    for ref in stats['identifier_coverage']['references_without_any'][:10]:
                        st.text(ref)
            
            elif active_tab == "authors":
                st.markdown(f"### {get_text('top_authors')}")
                for i, author in enumerate(stats['author_frequency_all']['all_authors'][:30], 1):
                    orcid_text = f" 🔗 ORCID: {author['orcid']}" if author.get('orcid') else ""
                    inst_text = f" 🏛 {author['institution'][:50]}" if author.get('institution') else ""
                    st.markdown(f"""
                    <div class="rank-item">
                        <span class="rank-number">{i}.</span>
                        <span class="rank-name">{author['display_name']}{orcid_text}{inst_text}</span>
                        <span class="rank-count">{author['count']} {get_text('html_citations_label')}</span>
                        <div class="progress-bar-custom">
                            <div class="progress-fill" style="width: {author['count'] / stats['author_frequency_all']['all_authors'][0]['count'] * 100 if stats['author_frequency_all']['all_authors'] else 0}%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"**{get_text('unique_authors')}:** {stats['author_frequency_all']['unique_authors']}")
            
            elif active_tab == "journals":
                st.markdown(f"### {get_text('all_journals')}")
                journals_df = pd.DataFrame(stats['journal_frequency_all']['all_journals'])
                st.dataframe(journals_df, use_container_width=True)
                st.markdown(f"**{get_text('unique_journals')}:** {stats['journal_frequency_all']['unique_journals']}")
            
            elif active_tab == "publishers":
                st.markdown(f"### {get_text('all_publishers')}")
                publishers_df = pd.DataFrame(stats['publisher_frequency']['all_publishers'])
                st.dataframe(publishers_df, use_container_width=True)
                st.markdown(f"**{get_text('unique_publishers_metric')}:** {stats['publisher_frequency']['unique_publishers']}")
            
            elif active_tab == "yearly":
                st.markdown(f"### {get_text('yearly_stats')}")
                st.markdown(f"**{get_text('references_with_known_year')}:** {stats['yearly_stats']['total_with_year']}")
                st.markdown(f"**{get_text('references_with_unknown_year')}:** {stats['yearly_stats']['unknown_year']}")
                
                st.markdown(f"#### {get_text('recent_years_summary')}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(get_text('last_3_years'), f"{stats['yearly_stats']['last_3_years']} ({stats['yearly_stats']['last_3_years_percent']:.1f}%)")
                with col2:
                    st.metric(get_text('last_5_years_metric'), f"{stats['yearly_stats']['last_5_years']} ({stats['yearly_stats']['last_5_years_percent']:.1f}%)")
                with col3:
                    st.metric(get_text('last_10_years'), f"{stats['yearly_stats']['last_10_years']} ({stats['yearly_stats']['last_10_years_percent']:.1f}%)")
                
                st.markdown(f"#### {get_text('distribution_by_year')}")
                years_df = pd.DataFrame(list(stats['yearly_stats']['yearly_counts'].items()), columns=["Year", "Count"])
                years_df = years_df.sort_values("Year", ascending=False)
                st.bar_chart(years_df.set_index("Year"))
                
                st.markdown(f"#### {get_text('detailed_yearly_data')}")
                yearly_data = []
                for year in sorted(stats['yearly_stats']['yearly_counts'].keys(), reverse=True):
                    yearly_data.append({
                        "Year": year,
                        "Count": stats['yearly_stats']['yearly_counts'][year],
                        "Percentage": f"{stats['yearly_stats']['yearly_percentages'][year]:.1f}%",
                        "Cumulative %": f"{stats['yearly_stats']['cumulative_percentages'][year]:.1f}%"
                    })
                st.dataframe(pd.DataFrame(yearly_data), use_container_width=True)
            
            elif active_tab == "concepts":
                st.markdown(f"### {get_text('key_concepts')}")
                concepts_df = pd.DataFrame(stats['concepts']['concepts'][:15], columns=["Concept", "Frequency"])
                st.dataframe(concepts_df, use_container_width=True)
            
            elif active_tab == "geography":
                st.markdown(f"### {get_text('geographic_distribution')}")
                if stats['geography']['countries']:
                    geo_df = pd.DataFrame(list(stats['geography']['countries'].items()), columns=["Country", "Author count"])
                    st.dataframe(geo_df, use_container_width=True)
                    st.markdown(f"**{get_text('total_countries')}:** {stats['geography']['total_countries']}")
                    st.markdown(f"**{get_text('international_collaboration')}:** {stats['geography']['international_percent']:.1f}%")
            
            elif active_tab == "collaboration":
                st.markdown(f"### {get_text('collaboration_networks')}")
                if stats['collaboration']['top_collaborations']:
                    st.markdown(f"#### {get_text('top_author_pairs')}")
                    for i, collab in enumerate(stats['collaboration']['top_collaborations'][:10], 1):
                        st.markdown(f"{i}. **{collab['author1']}** + **{collab['author2']}** — {collab['count']} {get_text('html_joint_works')}")
                    
                    st.markdown(f"#### {get_text('core_authors')}")
                    for author, connections in stats['collaboration']['core_authors'][:10]:
                        st.markdown(f"• **{author}** — {connections} {get_text('html_connections')}")
            
            elif active_tab == "diversity":
                st.markdown(f"### {get_text('diversity_analysis')}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(get_text('shannon_authors'), stats['shannon_index']['authors'])
                with col2:
                    st.metric(get_text('shannon_journals'), stats['shannon_index']['journals'])
                with col3:
                    st.metric(get_text('shannon_publishers'), stats['shannon_index']['publishers'])
            
            elif active_tab == "classics":
                st.markdown(f"### {get_text('citation_classics')}")
                if stats['citation_classics']:
                    for classic in stats['citation_classics'][:10]:
                        with st.expander(f"{classic['title'][:100]}..."):
                            st.markdown(f"**{get_text('citations')}:** {classic['citations']}")
                            st.markdown(f"**{get_text('journal')}:** {classic['journal']}")
                            st.markdown(f"**{get_text('year')}:** {classic['year']}")
                            if classic.get('doi'):
                                st.markdown(f"**DOI:** [{classic['doi']}](https://doi.org/{classic['doi']})")
                else:
                    st.info(get_text('no_citation_classics'))
            
            elif active_tab == "crossref_only":
                st.markdown(f"### {get_text('crossref_only')}")
                if stats.get('crossref_only_refs'):
                    for ref in stats['crossref_only_refs'][:20]:
                        st.warning(f"📄 {ref['text']}\n\nDOI: {ref['doi']}")
                else:
                    st.success(get_text('no_crossref_only'))
            
            elif active_tab == "openalex_only":
                st.markdown(f"### {get_text('openalex_only')}")
                if stats.get('openalex_only_refs'):
                    for ref in stats['openalex_only_refs'][:20]:
                        st.info(f"📄 {ref['text']}\n\nDOI: {ref['doi']}")
                else:
                    st.success(get_text('no_openalex_only'))
            
            elif active_tab == "suspicious":
                st.markdown(f"### {get_text('suspicious_dois')}")
                st.markdown(get_text('suspicious_dois_hint'))
                if stats.get('suspicious_doi_refs'):
                    for ref in stats['suspicious_doi_refs'][:20]:
                        st.error(f"⚠️ {ref['text']}\n\nDOI: {ref['doi']}")
                else:
                    st.success(get_text('no_suspicious_dois'))
            
            elif active_tab == "non_doi":
                st.markdown(f"### {get_text('non_doi_sources')}")
                if stats['identifier_coverage']['references_without_doi']:
                    for ref in stats['identifier_coverage']['references_without_doi'][:20]:
                        st.text(ref)
                else:
                    st.success(get_text('all_have_doi'))
            
            elif active_tab == "url_sources":
                st.markdown(f"### {get_text('url_sources')}")
                if stats['identifier_coverage']['references_with_only_url']:
                    for ref in stats['identifier_coverage']['references_with_only_url'][:20]:
                        st.text(ref)
                else:
                    st.success(get_text('no_url_only'))
            
            elif active_tab == "problems":
                st.markdown(f"### {get_text('problematic_refs')}")
                if stats['problematic_refs']:
                    for ref in stats['problematic_refs'][:15]:
                        st.warning(f"**{ref['problems']}**\n\n{ref['text']}")
                else:
                    st.success(get_text('no_problematic'))
                
                if stats['predatory_journals']:
                    st.markdown(f"### {get_text('predatory_journals')}")
                    for pred in stats['predatory_journals'][:10]:
                        with st.expander(f"📕 {pred['journal']}"):
                            st.markdown(f"**{get_text('issues')}:** {', '.join(pred['signs'])}")
                            st.markdown(f"**{get_text('reference')}:** {pred['reference']}")
            
            st.markdown("---")
            st.markdown(f"### {get_text('full_reference_list')}")
            
            # Initialize filter states in session state if not exists
            if 'filter_states' not in st.session_state:
                st.session_state.filter_states = {
                    'doi_only': False,
                    'non_doi_only': False,
                    'url_only': False,
                    'crossref_only': False,
                    'openalex_only': False,
                    'problematic_only': False,
                    'self_cited_only': False
                }
            
            # Function to handle filter changes
            def toggle_filter(filter_name, is_checked):
                if is_checked:
                    # Disable all other filters
                    for key in st.session_state.filter_states:
                        st.session_state.filter_states[key] = False
                    st.session_state.filter_states[filter_name] = True
                else:
                    st.session_state.filter_states[filter_name] = False
            
            col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
            with col_filter1:
                doi_only = st.checkbox(
                    get_text('only_with_doi'),
                    value=st.session_state.filter_states['doi_only'],
                    key="filter_doi_only",
                    on_change=lambda: toggle_filter('doi_only', st.session_state.filter_doi_only)
                )
            with col_filter2:
                non_doi_only = st.checkbox(
                    get_text('only_non_doi'),
                    value=st.session_state.filter_states['non_doi_only'],
                    key="filter_non_doi_only",
                    on_change=lambda: toggle_filter('non_doi_only', st.session_state.filter_non_doi_only)
                )
            with col_filter3:
                url_only = st.checkbox(
                    get_text('url_links'),
                    value=st.session_state.filter_states['url_only'],
                    key="filter_url_only",
                    on_change=lambda: toggle_filter('url_only', st.session_state.filter_url_only)
                )
            with col_filter4:
                crossref_only = st.checkbox(
                    get_text('only_crossref'),
                    value=st.session_state.filter_states['crossref_only'],
                    key="filter_crossref_only",
                    on_change=lambda: toggle_filter('crossref_only', st.session_state.filter_crossref_only)
                )
            
            col_filter5, col_filter6, col_filter7, col_filter8 = st.columns(4)
            with col_filter5:
                openalex_only = st.checkbox(
                    get_text('only_openalex'),
                    value=st.session_state.filter_states['openalex_only'],
                    key="filter_openalex_only",
                    on_change=lambda: toggle_filter('openalex_only', st.session_state.filter_openalex_only)
                )
            with col_filter6:
                problematic_only = st.checkbox(
                    get_text('problematic_only'),
                    value=st.session_state.filter_states['problematic_only'],
                    key="filter_problematic_only",
                    on_change=lambda: toggle_filter('problematic_only', st.session_state.filter_problematic_only)
                )
            with col_filter7:
                self_cited_only = st.checkbox(
                    get_text('self_cited_only'),
                    value=st.session_state.filter_states['self_cited_only'],
                    key="filter_self_cited_only",
                    on_change=lambda: toggle_filter('self_cited_only', st.session_state.filter_self_cited_only)
                )
            with col_filter8:
                search_term = st.text_input(get_text('search_in_text'), placeholder=get_text('search_placeholder'))
            
            filtered_results = results
            
            # Apply filters based on session state
            if st.session_state.filter_states['doi_only']:
                filtered_results = [r for r in filtered_results if r['doi']]
            if st.session_state.filter_states['non_doi_only']:
                filtered_results = [r for r in filtered_results if not r['doi']]
            if st.session_state.filter_states['url_only']:
                filtered_results = [r for r in filtered_results if r.get('identifiers', {}).get('url') and not r.get('doi')]
            if st.session_state.filter_states['crossref_only']:
                filtered_results = [r for r in filtered_results if r['doi'] and r['crossref_status'] and not r['openalex_status']]
            if st.session_state.filter_states['openalex_only']:
                filtered_results = [r for r in filtered_results if r['doi'] and r['openalex_status'] and not r['crossref_status']]
            if st.session_state.filter_states['problematic_only']:
                filtered_results = [r for r in filtered_results if r['is_retracted'] or r['is_preprint'] or r['crossmark_issues'] or r.get('is_suspicious_doi')]
            if st.session_state.filter_states['self_cited_only']:
                filtered_results = [r for r in filtered_results if r['is_self_citation']]
            if search_term:
                filtered_results = [r for r in filtered_results if search_term.lower() in r['original_text'].lower()]
            
            st.markdown(get_text('showing').format(len(filtered_results), len(results)))
            
            for i, result in enumerate(filtered_results[:50]):
                if result.get('is_suspicious_doi'):
                    status_icon = "⚠️"
                elif result['doi']:
                    status_icon = "✅"
                else:
                    status_icon = "❌"
                
                problems_badges = []
                if result['is_retracted']:
                    problems_badges.append(f'<span class="badge-danger">{get_text("retracted")}</span>')
                if result['is_preprint']:
                    problems_badges.append(f'<span class="badge-warning">{get_text("preprint")}</span>')
                if result['is_self_citation']:
                    problems_badges.append(f'<span class="badge-info">{get_text("self_citation")}</span>')
                if result.get('is_suspicious_doi'):
                    problems_badges.append(f'<span class="badge-danger">{get_text("suspicious_doi_badge")}</span>')
                
                badges_html = ' '.join(problems_badges)
                
                with st.expander(f"{status_icon} {result['original_text'][:150]}..."):
                    st.markdown(f"**DOI:** {result['doi'] if result['doi'] else get_text('not_found')}")
                    identifiers = result.get('identifiers', {})
                    if identifiers.get('url'):
                        st.markdown(f"**URL:** {identifiers['url']}")
                    if identifiers.get('arxiv'):
                        st.markdown(f"**arXiv:** {identifiers['arxiv']}")
                    st.markdown(f"**{get_text('status')}:** Crossref: {'✅' if result['crossref_status'] else '❌'} | OpenAlex: {'✅' if result['openalex_status'] else '❌'}")
                    if result['journal']:
                        st.markdown(f"**{get_text('journal')}:** {result['journal']}")
                    if result['year']:
                        st.markdown(f"**{get_text('year')}:** {result['year']}")
                    if result['authors_display']:
                        st.markdown(f"**{get_text('authors')}:** {', '.join(result['authors_display'][:5])}")
                    if result.get('citations_count', 0) > 0:
                        st.markdown(f"**{get_text('citations')}:** {result['citations_count']}")
                    if badges_html:
                        st.markdown(f"**{get_text('issues')}:** {badges_html}", unsafe_allow_html=True)
                    st.markdown(f"**{get_text('full_text')}:**")
                    st.text(result['original_text'])
            
            if len(filtered_results) > 50:
                st.info(get_text('showing_first').format(50, len(filtered_results)))
            
        else:
            st.info(get_text('upload_first'))
    
    with tab3:
        if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
            results = st.session_state['results']
            paper_authors = st.session_state.get('paper_authors', set())
            journal_name = st.session_state.get('journal_name', '')
            article_number = st.session_state.get('article_number', '')
            stats = generate_advanced_statistics(results)
            
            st.markdown(f"### {get_text('export_report')}")
            st.markdown(get_text('download_html'))
            
            html_report = generate_html_report_advanced(results, stats, paper_authors, st.session_state.language, journal_name, article_number)
            
            # Generate filename from journal abbreviation and article number (no datetime)
            def get_journal_abbreviation(journal_name: str) -> str:
                """Get journal abbreviation from full name"""
                abbreviations = {
                    'chimica techno acta': 'CTA',
                    'materials reports energy': 'MRE',
                    # Add more abbreviations as needed
                }
                journal_lower = journal_name.lower().strip()
                for full, abbr in abbreviations.items():
                    if full in journal_lower:
                        return abbr
                # Fallback: take first letters of each word (max 3-4 letters)
                words = re.findall(r'[A-Za-z][a-z]*', journal_name)
                if words:
                    abbr = ''.join(word[0].upper() for word in words[:3])
                    return abbr if abbr else "JRNL"
                return "JRNL"
            
            def sanitize_filename(s: str) -> str:
                # Remove special characters, replace spaces and punctuation with underscores
                s = re.sub(r'[^a-z0-9]+', '_', s.lower().strip())
                # Remove leading/trailing underscores
                s = s.strip('_')
                return s if s else "report"
            
            # Get journal abbreviation
            if journal_name and journal_name.strip():
                journal_abbr = get_journal_abbreviation(journal_name)
            else:
                journal_abbr = "CTA"  # default
            
            # Sanitize article number for filename
            if article_number and article_number.strip():
                num_part = sanitize_filename(article_number)
                # Keep only alphanumeric and dash for article number
                num_part = re.sub(r'[^a-z0-9\-]', '', num_part)
                file_name = f"{journal_abbr}_{num_part}.html"
            else:
                file_name = f"{journal_abbr}.html"
            
            st.download_button(
                label=get_text('download_html'),
                data=html_report.encode('utf-8'),
                file_name=file_name,
                mime="text/html"
            )
            
            st.markdown("---")
            st.markdown(f"### {get_text('text_export')}")
            
            copy_text = f"""
=== COMPREHENSIVE REFERENCE LIST ANALYSIS ===
Journal: {journal_name if journal_name else 'Chimica Techno Acta'}
Article number: {article_number if article_number else '—'}
Date: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

=== OVERVIEW STATISTICS ===
Total references: {stats['total_references']}
DOI found: {stats['total_with_doi']} ({stats['total_with_doi']/stats['total_references']*100 if stats['total_references'] > 0 else 0:.1f}%)
References last 5 years: {stats['yearly_stats']['last_5_years']}
Self-citations: {stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)
Total citations: {stats.get('total_citations_sum', 0)}
Average citations: {stats.get('avg_citations', 0):.1f}

=== IDENTIFIER COVERAGE ===
DOI: {stats['identifier_coverage']['stats']['has_doi']}
URL: {stats['identifier_coverage']['stats']['has_url']}
arXiv: {stats['identifier_coverage']['stats']['has_arxiv']}
PMID: {stats['identifier_coverage']['stats']['has_pmid']}
ISBN: {stats['identifier_coverage']['stats']['has_isbn']}
No identifier: {stats['identifier_coverage']['stats']['has_none']}

=== DOI STATUS ===
Crossref + OpenAlex: {stats['doi_status']['both']}
Only Crossref: {stats['doi_status']['crossref_only']}
Only OpenAlex: {stats['doi_status']['openalex_only']}
No data: {stats['doi_status']['none']}
Suspicious DOIs: {len(stats.get('suspicious_doi_refs', []))}

=== TOP AUTHORS (MERGED) ===
{chr(10).join([f"{a['display_name']}: {a['count']} citations" + (f" (ORCID: {a['orcid']})" if a.get('orcid') else "") for a in stats['author_frequency_all']['all_authors'][:20]])}

=== ORCID COVERAGE ===
Total authors: {stats['orcid_coverage']['total_authors']}
With ORCID: {stats['orcid_coverage']['with_orcid']} ({stats['orcid_coverage']['coverage_percent']:.1f}%)

=== YEARLY STATISTICS ===
Last 3 years: {stats['yearly_stats']['last_3_years']} ({stats['yearly_stats']['last_3_years_percent']:.1f}%)
Last 5 years: {stats['yearly_stats']['last_5_years']} ({stats['yearly_stats']['last_5_years_percent']:.1f}%)
Last 10 years: {stats['yearly_stats']['last_10_years']} ({stats['yearly_stats']['last_10_years_percent']:.1f}%)
Unknown year: {stats['yearly_stats']['unknown_year']}

=== KEY CONCEPTS ===
{chr(10).join([f"{c[0]}: {c[1]}" for c in stats['concepts']['concepts'][:10]])}

=== DIVERSITY INDICES ===
Authors (Shannon): {stats['shannon_index']['authors']}
Journals (Shannon): {stats['shannon_index']['journals']}
Publishers (Shannon): {stats['shannon_index']['publishers']}
"""
            
            st.text_area(get_text('text_export'), copy_text, height=400)
            
            if st.button(get_text('copy_to_clipboard')):
                st.write(get_text('copied'))
        else:
            st.info(get_text('run_analysis_first'))

if __name__ == "__main__":
    main()
