# ============================================================
# styles.py - Все стили HTML отчетов (ПОЛНАЯ ВЕРСИЯ)
# ============================================================

from datetime import datetime
import html
import re
from typing import Dict, List, Optional

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ СТИЛЕЙ
# ============================================================

def get_date() -> str:
    """Возвращает текущую дату в формате ДД.ММ.ГГГГ"""
    return datetime.now().strftime('%d.%m.%Y')

def get_footer(journal_name: str = "Chimica Techno Acta") -> str:
    """Возвращает подвал для отчетов"""
    return f'© {journal_name} / Created by daM / {get_date()}'

def make_clickable_doi(doi: str) -> str:
    """Создает кликабельную ссылку для DOI"""
    if doi:
        return f'<a href="https://doi.org/{doi}" target="_blank" style="color: #667eea; text-decoration: none;">{html.escape(str(doi))}</a>'
    return "Not found"

def safe_str(value) -> str:
    """Безопасное преобразование в строку с защитой от None"""
    if value is None:
        return ""
    return str(value)

def safe_escape(value) -> str:
    """Безопасное экранирование HTML с защитой от None"""
    if value is None:
        return ""
    return html.escape(str(value))

# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ ГЕНЕРАЦИИ КЛАССИЧЕСКОГО ОТЧЕТА (ПОЛНАЯ ВЕРСИЯ)
# ============================================================

def generate_full_report_html(data: Dict, custom_css: str = None, custom_header: str = None) -> str:
    """
    Генерирует полный HTML отчет со всеми разделами.
    Параметры:
    - data: словарь со всеми данными
    - custom_css: пользовательский CSS (для новых стилей)
    - custom_header: пользовательский заголовок (для новых стилей)
    """
    
    # ========== РАСПАКОВКА ДАННЫХ С ЗАЩИТОЙ ОТ None ==========
    total_references = data.get('total_references', 0)
    total_with_doi = data.get('total_with_doi', 0)
    total_with_doi_percent = data.get('total_with_doi_percent', 0)
    last_5_years = data.get('yearly_stats', {}).get('last_5_years', 0)
    last_5_years_percent = data.get('yearly_stats', {}).get('last_5_years_percent', 0)
    self_citations_count = data.get('self_citations_count', 0)
    self_citations_percent = data.get('self_citations_percent', 0)
    total_citations_sum = data.get('total_citations_sum', 0)
    avg_citations = data.get('avg_citations', 0)
    
    journal_name = data.get('journal_name', 'Chimica Techno Acta')
    article_number = data.get('article_number', '')
    
    # DOI статус
    doi_status = data.get('doi_status', {'both': 0, 'crossref_only': 0, 'openalex_only': 0, 'none': 0})
    doi_status_percents = data.get('doi_status_percents', {'both': 0, 'crossref_only': 0, 'openalex_only': 0, 'none': 0})
    
    # Identifier coverage
    identifier_stats = data.get('identifier_coverage', {}).get('stats', {})
    identifier_percents = data.get('identifier_coverage_percents', {})
    
    # Authors
    all_authors = data.get('author_frequency_all', {}).get('all_authors', [])
    unique_authors = data.get('author_frequency_all', {}).get('unique_authors', 0)
    
    # Journals
    all_journals = data.get('journal_frequency_all', {}).get('all_journals', [])
    unique_journals = data.get('journal_frequency_all', {}).get('unique_journals', 0)
    
    # Publishers
    all_publishers = data.get('publisher_frequency', {}).get('all_publishers', [])
    unique_publishers = data.get('publisher_frequency', {}).get('unique_publishers', 0)
    
    # Yearly stats
    yearly_stats = data.get('yearly_stats', {})
    yearly_counts = yearly_stats.get('yearly_counts', {})
    yearly_percentages = yearly_stats.get('yearly_percentages', {})
    cumulative_percentages = yearly_stats.get('cumulative_percentages', {})
    
    # Concepts
    concepts = data.get('concepts', {}).get('concepts', [])
    unique_concepts = data.get('concepts', {}).get('unique_concepts', 0)
    
    # Geography
    geography = data.get('geography', {})
    type1_countries = geography.get('type1_unique_countries_per_reference', {})
    type2_countries = geography.get('type2_authors_per_country', {})
    collaboration_matrix = geography.get('collaboration_matrix', [])
    
    # Collaboration
    collaboration = data.get('collaboration', {})
    top_collaborations = collaboration.get('top_collaborations', [])
    core_authors = collaboration.get('core_authors', [])
    
    # Shannon index
    shannon_index = data.get('shannon_index', {'authors': 0, 'journals': 0, 'publishers': 0})
    
    # ORCID coverage
    orcid_coverage = data.get('orcid_coverage', {'total_authors': 0, 'with_orcid': 0, 'coverage_percent': 0})
    
    # Citation classics
    citation_classics = data.get('citation_classics', [])
    
    # Temporal
    temporal = data.get('temporal', {'median_age': 0, 'average_age': 0})
    
    # Problematic refs
    problematic_refs = data.get('problematic_refs', [])
    crossref_only_refs = data.get('crossref_only_refs', [])
    openalex_only_refs = data.get('openalex_only_refs', [])
    suspicious_doi_refs = data.get('suspicious_doi_refs', [])
    repository_refs = data.get('repository_refs', [])
    proceedings_refs = data.get('proceedings_refs', [])
    retracted_refs = data.get('retracted_refs', [])
    books_with_isbn_no_doi = data.get('books_with_isbn_no_doi', [])
    non_journal_sources_with_doi = data.get('non_journal_sources_with_doi', [])
    
    # Self citations
    self_citation_refs = data.get('self_citation_refs', [])
    
    # Duplicates
    duplicates = data.get('duplicates', [])
    
    # Results for full reference list
    results = data.get('results', [])
    references_without_doi = data.get('references_without_doi', [])
    references_with_only_url = data.get('references_with_only_url', [])
    
    # ========== ПОСТРОЕНИЕ НАВИГАЦИОННОГО МЕНЮ ==========
    sidebar_items = [
        ("overview", "Overview"),
        ("identifiers", "Identifier Coverage"),
        ("authors", "Authors"),
        ("journals", "Journals"),
        ("publishers", "Publishers"),
        ("yearly", "Yearly Statistics"),
        ("concepts", "Concepts"),
        ("geography", "Geography"),
        ("collaboration", "Collaborations"),
        ("diversity", "Diversity"),
        ("classics", "Citation Classics")
    ]
    
    if self_citation_refs:
        sidebar_items.append(("selfcitations", "Self-Citations"))
    
    if duplicates:
        sidebar_items.append(("duplicates", "Duplicates"))
    
    sidebar_items.extend([
        ("crossref_only", "Only Crossref"),
        ("openalex_only", "Only OpenAlex"),
        ("suspicious_doi", "Suspicious DOIs"),
        ("non_doi", "Non-DOI Sources"),
        ("nonjournal", "Non-journal Sources with DOI"),
        ("url_sources", "URL Sources"),
        ("problems", "Problems"),
        ("full_reference_list", "Full Reference List")
    ])
    
    sidebar_html = '<div class="sidebar">\n'
    sidebar_html += '<h3>Navigation</h3>\n'
    for item_id, title in sidebar_items:
        sidebar_html += f'<a href="#{item_id}"><span>{safe_escape(title)}</span></a>\n'
    sidebar_html += '</div>\n'
    
    # ========== ПОСТРОЕНИЕ МЕТРИК ==========
    metrics_html = f'''
    <div class="stats-grid">
        <div class="metric-card">
            <div class="metric-number">{total_references}</div>
            <div class="metric-percent">(100.0%)</div>
            <div class="metric-label">Total references</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{total_with_doi}</div>
            <div class="metric-percent">({total_with_doi_percent:.1f}%)</div>
            <div class="metric-label">DOI found</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{last_5_years}</div>
            <div class="metric-percent">({last_5_years_percent:.1f}%)</div>
            <div class="metric-label">References (last 5 years)</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{self_citations_count}</div>
            <div class="metric-percent">({self_citations_percent:.1f}%)</div>
            <div class="metric-label">Self-citations</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{total_citations_sum}</div>
            <div class="metric-label">Total citations</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{avg_citations:.1f}</div>
            <div class="metric-label">Average citations</div>
        </div>
    </div>
    '''
    
    # ========== IDENTIFIER COVERAGE ==========
    identifier_html = f'''
    <div class="stats-grid">
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('has_doi', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('has_doi', 0):.1f}%)</div>
            <div class="metric-label">DOI found</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('has_url', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('has_url', 0):.1f}%)</div>
            <div class="metric-label">URL</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('is_preprint_repository', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('preprint_repository', 0):.1f}%)</div>
            <div class="metric-label">Preprint/Repository</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('has_pmid', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('has_pmid', 0):.1f}%)</div>
            <div class="metric-label">PMID</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('is_ebook_platform', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('ebook_platform', 0):.1f}%)</div>
            <div class="metric-label">Ebook (with DOI)</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('is_book_no_doi', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('book_no_doi', 0):.1f}%)</div>
            <div class="metric-label">Books (ISBN only)</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('is_proceedings', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('proceedings', 0):.1f}%)</div>
            <div class="metric-label">Proceedings</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('is_retracted', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('retracted', 0):.1f}%)</div>
            <div class="metric-label">Retracted</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('has_none', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('has_none', 0):.1f}%)</div>
            <div class="metric-label">No identifier</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{identifier_stats.get('multiple', 0)}</div>
            <div class="metric-percent">({identifier_percents.get('multiple', 0):.1f}%)</div>
            <div class="metric-label">Multiple identifiers</div>
        </div>
    </div>
    <div class="stats-grid">
        <div class="metric-card">
            <div class="metric-number">{doi_status.get('both', 0)}</div>
            <div class="metric-percent">({doi_status_percents.get('both', 0):.1f}%)</div>
            <div class="metric-label">Crossref + OpenAlex</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{doi_status.get('crossref_only', 0)}</div>
            <div class="metric-percent">({doi_status_percents.get('crossref_only', 0):.1f}%)</div>
            <div class="metric-label">Only Crossref</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{doi_status.get('openalex_only', 0)}</div>
            <div class="metric-percent">({doi_status_percents.get('openalex_only', 0):.1f}%)</div>
            <div class="metric-label">Only OpenAlex</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{doi_status.get('none', 0)}</div>
            <div class="metric-percent">({doi_status_percents.get('none', 0):.1f}%)</div>
            <div class="metric-label">No data</div>
        </div>
    </div>
    '''
    
    # ========== AUTHORS SECTION ==========
    authors_html = ''
    if all_authors:
        max_count = all_authors[0].get('mention_count', 1) if all_authors else 1
        for i, author in enumerate(all_authors[:30], 1):
            author_name = safe_escape(author.get('display_name', 'Unknown'))
            mention_count = author.get('mention_count', 0)
            orcid = author.get('orcid', '')
            primary_institution = safe_escape(author.get('primary_institution', ''))
            countries = author.get('countries', [])
            
            orcid_html = f'<div style="font-size: 11px; color: #667eea;">ORCID: <a href="{safe_escape(orcid)}" target="_blank" style="color: #667eea; text-decoration: none;">{safe_escape(orcid)}</a></div>' if orcid else ''
            inst_html = f'<div style="font-size: 11px; color: #666;">Institution: {primary_institution[:50]}</div>' if primary_institution else ''
            country_html = f'<div style="font-size: 11px; color: #666;">Country: {", ".join([safe_escape(c) for c in countries])}</div>' if countries else ''
            
            affiliations_html = ''
            if author.get('affiliations'):
                aff_list = author.get('affiliations', [])[:3]
                aff_names = [safe_escape(aff.get('name', '')[:80]) for aff in aff_list]
                affiliations_html = f'<div style="font-size: 11px; color: #666;">All affiliations:<br>{", ".join(aff_names)}</div>'
            
            progress_width = min(100, (mention_count / max_count * 100)) if max_count > 0 else 0
            
            authors_html += f'''
            <div class="rank-item">
                <span class="rank-number">{i}.</span>
                <span class="rank-name">{author_name}</span>
                <span class="rank-count">{mention_count} citations</span>
                {orcid_html}
                {inst_html}
                {country_html}
                {affiliations_html}
                <div class="progress-bar-custom">
                    <div class="progress-fill" style="width: {progress_width}%;"></div>
                </div>
            </div>
            '''
    
    # ========== JOURNALS SECTION ==========
    journals_html = ''
    for i, journal in enumerate(all_journals, 1):
        journal_name_safe = safe_escape(journal.get('journal', 'Unknown'))
        count = journal.get('count', 0)
        percentage = journal.get('percentage', 0)
        journals_html += f'''
        <tr>
            <td>{i}</td>
            <td>{journal_name_safe}</td>
            <td>{count}</td>
            <td>{percentage:.1f}%</td>
        </tr>
        '''
    
    # ========== PUBLISHERS SECTION ==========
    publishers_html = ''
    for i, publisher in enumerate(all_publishers, 1):
        publisher_name_safe = safe_escape(publisher.get('publisher', 'Unknown'))
        count = publisher.get('count', 0)
        percentage = publisher.get('percentage', 0)
        publishers_html += f'''
        <tr>
            <td>{i}</td>
            <td>{publisher_name_safe}</td>
            <td>{count}</td>
            <td>{percentage:.1f}%</td>
        </tr>
        '''
    
    # ========== YEARLY SECTION ==========
    yearly_html = f'''
    <div class="stats-grid">
        <div class="metric-card">
            <div class="metric-number">{yearly_stats.get('last_year', 0)}</div>
            <div class="metric-percent">({yearly_stats.get('last_year_percent', 0):.1f}%)</div>
            <div class="metric-label">Last Year ({yearly_stats.get('last_completed_year', 'N/A')})</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{yearly_stats.get('last_3_years', 0)}</div>
            <div class="metric-percent">({yearly_stats.get('last_3_years_percent', 0):.1f}%)</div>
            <div class="metric-label">Last 3 years</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{yearly_stats.get('last_5_years', 0)}</div>
            <div class="metric-percent">({yearly_stats.get('last_5_years_percent', 0):.1f}%)</div>
            <div class="metric-label">Last 5 years</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{yearly_stats.get('last_10_years', 0)}</div>
            <div class="metric-percent">({yearly_stats.get('last_10_years_percent', 0):.1f}%)</div>
            <div class="metric-label">Last 10 years</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{yearly_stats.get('unknown_year', 0)}</div>
            <div class="metric-label">Unknown year</div>
        </div>
    </div>
    <div>
        <h4>Distribution by year:</h4>
    '''
    
    for year in sorted(yearly_counts.keys(), reverse=True):
        count = yearly_counts.get(year, 0)
        percent = yearly_percentages.get(year, 0)
        yearly_html += f'''
        <div class="rank-item">
            <span class="rank-name">{year}</span>
            <span class="rank-count">{count} references ({percent:.1f}%)</span>
            <div class="progress-bar-custom">
                <div class="progress-fill" style="width: {percent}%;"></div>
            </div>
        </div>
        '''
    
    yearly_html += '''
    </div>
    <div style="margin-top: 15px;">
        <h4>Cumulative percentage:</h4>
    '''
    
    for year in sorted(cumulative_percentages.keys(), reverse=True):
        cum_percent = cumulative_percentages.get(year, 0)
        yearly_html += f'''
        <div class="rank-item">
            <span class="rank-name">{year}</span>
            <span class="rank-count">{cum_percent:.1f}% cumulative</span>
            <div class="progress-bar-custom">
                <div class="progress-fill" style="width: {cum_percent}%;"></div>
            </div>
        </div>
        '''
    
    yearly_html += f'''
    </div>
    <div style="margin-top: 15px;">
        <span class="badge badge-info">Median age: {temporal.get('median_age', 0)} years</span>
        <span class="badge badge-info">Average age: {temporal.get('average_age', 0):.1f} years</span>
    </div>
    '''
    
    # ========== CONCEPTS SECTION ==========
    concepts_html = '<div class="concepts-grid">'
    for concept, count in concepts[:12]:
        concepts_html += f'''
        <div class="concept-card">
            <div class="concept-name">{safe_escape(concept)}</div>
            <div class="concept-score">Frequency: {count}</div>
        </div>
        '''
    concepts_html += f'''
    </div>
    <div style="margin-top: 15px;">
        <span class="badge badge-info">Unique concepts: {unique_concepts}</span>
    </div>
    '''
    
    # ========== GEOGRAPHY SECTION ==========
    geography_html = f'''
    <h4>Type 1: Unique Countries per Reference</h4>
    <p style="font-size: 12px; color: #666; margin-bottom: 10px;">Each reference counted once per unique country</p>
    <div>
    '''
    
    max_geo_count = max(type1_countries.values()) if type1_countries else 1
    for country, count in list(type1_countries.items())[:15]:
        geo_width = (count / max_geo_count * 100) if max_geo_count > 0 else 0
        geography_html += f'''
        <div class="rank-item">
            <span class="rank-name">{safe_escape(country)}</span>
            <span class="rank-count">{count} references</span>
            <div class="progress-bar-custom">
                <div class="progress-fill" style="width: {geo_width}%;"></div>
            </div>
        </div>
        '''
    
    geography_html += '''
    </div>
    <h4 style="margin-top: 25px;">Type 2: Authors per Country</h4>
    <p style="font-size: 12px; color: #666; margin-bottom: 10px;">Each author counted separately</p>
    <div>
    '''
    
    max_geo_authors = max(type2_countries.values()) if type2_countries else 1
    for country, count in list(type2_countries.items())[:15]:
        geo_width = (count / max_geo_authors * 100) if max_geo_authors > 0 else 0
        geography_html += f'''
        <div class="rank-item">
            <span class="rank-name">{safe_escape(country)}</span>
            <span class="rank-count">{count} authors</span>
            <div class="progress-bar-custom">
                <div class="progress-fill" style="width: {geo_width}%;"></div>
            </div>
        </div>
        '''
    
    geography_html += f'''
    </div>
    <h4 style="margin-top: 25px;">Type 3: Collaboration Patterns</h4>
    <p style="font-size: 12px; color: #666; margin-bottom: 10px;">Distribution of single-country vs international collaborations</p>
    <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
        <div class="metric-card">
            <div class="metric-number">{geography.get('single_country_count', 0)}</div>
            <div class="metric-label">Single country</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{geography.get('international_count', 0)}</div>
            <div class="metric-label">International collaboration</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{geography.get('total_references_with_country', 0)}</div>
            <div class="metric-label">References (with country)</div>
        </div>
    </div>
    <h5 style="margin-top: 20px;">Collaboration matrix:</h5>
    <div>
    '''
    
    max_collab = max([c.get('count', 0) for c in collaboration_matrix]) if collaboration_matrix else 1
    for collab in collaboration_matrix[:15]:
        collab_width = (collab.get('count', 0) / max_collab * 100) if max_collab > 0 else 0
        geography_html += f'''
        <div class="rank-item">
            <span class="rank-name">{safe_escape(collab.get('country1', ''))} + {safe_escape(collab.get('country2', ''))}</span>
            <span class="rank-count">{collab.get('count', 0)} references</span>
            <div class="progress-bar-custom">
                <div class="progress-fill" style="width: {collab_width}%;"></div>
            </div>
        </div>
        '''
    
    geography_html += '</div>'
    
    # ========== COLLABORATION SECTION ==========
    collaboration_html = ''
    for i, collab in enumerate(top_collaborations[:8], 1):
        collaboration_html += f'''
        <div class="rank-item">
            <span class="rank-number">{i}.</span>
            <span class="rank-name">{safe_escape(collab.get('author1', ''))} + {safe_escape(collab.get('author2', ''))}</span>
            <span class="rank-count">{collab.get('count', 0)} joint works</span>
        </div>
        '''
    
    core_authors_html = ', '.join([f"{safe_escape(author[0])} ({author[1]} connections)" for author in core_authors[:5]])
    
    # ========== DIVERSITY SECTION ==========
    diversity_html = f'''
    <div class="stats-grid">
        <div class="metric-card">
            <div class="metric-number">{shannon_index.get('authors', 0)}</div>
            <div class="metric-label">Authors Shannon index</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{shannon_index.get('journals', 0)}</div>
            <div class="metric-label">Journals Shannon index</div>
        </div>
        <div class="metric-card">
            <div class="metric-number">{shannon_index.get('publishers', 0)}</div>
            <div class="metric-label">Publishers Shannon index</div>
        </div>
    </div>
    '''
    
    # ========== CITATION CLASSICS ==========
    classics_html = ''
    if citation_classics:
        for i, classic in enumerate(citation_classics, 1):
            title = safe_escape(classic.get('title', 'Unknown'))
            journal = safe_escape(classic.get('journal', 'Unknown'))
            year = classic.get('year', 'N/A')
            citations = classic.get('citations', 0)
            doi = classic.get('doi', '')
            
            classics_html += f'''
            <div class="rank-item">
                <span class="rank-number">{i}.</span>
                <span class="rank-name">{title}</span>
                <span class="rank-count">Citations: {citations}</span>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">{journal} ({year})</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(doi)}</div>
            </div>
            '''
    else:
        classics_html = '<p>No citation classics detected</p>'
    
    # ========== SELF-CITATIONS SECTION ==========
    self_citations_html = ''
    if self_citation_refs:
        for ref in self_citation_refs:
            authors_display = ', '.join([safe_escape(a) for a in ref.get('authors_display', [])])
            original_text = safe_escape(ref.get('original_text', ''))
            doi = ref.get('doi', '')
            journal = safe_escape(ref.get('journal', 'Not found'))
            year = ref.get('year', 'Not found')
            
            self_citations_html += f'''
            <div class="rank-item" style="margin-bottom: 15px;">
                <div><strong>Reference:</strong></div>
                <div class="full-text-container">{original_text}</div>
                <div style="font-size: 13px; margin-top: 8px;"><strong>Authors:</strong> {authors_display}</div>
                <div style="font-size: 13px; margin-top: 5px;"><strong>DOI found:</strong> {make_clickable_doi(doi)}</div>
                <div style="font-size: 13px; margin-top: 5px;"><strong>Journal:</strong> {journal}</div>
                <div style="font-size: 13px; margin-top: 5px;"><strong>Year:</strong> {year}</div>
            </div>
            '''
    else:
        self_citations_html = '<p>None detected</p>'
    
    # ========== DUPLICATES SECTION ==========
    duplicates_html = ''
    if duplicates:
        for dup in duplicates:
            ref1 = safe_escape(dup.get('ref1', '')[:200])
            ref2 = safe_escape(dup.get('ref2', '')[:200])
            doi = dup.get('doi', 'Not found')
            duplicates_html += f'''
            <div class="rank-item duplicate-reference" style="margin-bottom: 10px;">
                <span class="badge badge-warning">Full DOI Match</span>
                <div style="margin-top: 8px;"><strong>References {dup.get('index1', 0) + 1} and {dup.get('index2', 0) + 1}</strong> — DOI found: {make_clickable_doi(doi)}</div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">Reference {dup.get('index1', 0) + 1}: {ref1}...</div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">Reference {dup.get('index2', 0) + 1}: {ref2}...</div>
            </div>
            '''
    
    # ========== CROSSREF ONLY ==========
    crossref_only_html = ''
    if crossref_only_refs:
        for ref in crossref_only_refs[:20]:
            crossref_only_html += f'''
            <div class="rank-item">
                <div>{safe_escape(ref.get('text', ''))}</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref.get('doi', ''))}</div>
            </div>
            '''
    else:
        crossref_only_html = '<p>No references with only Crossref data</p>'
    
    # ========== OPENALEX ONLY ==========
    openalex_only_html = ''
    if openalex_only_refs:
        for ref in openalex_only_refs[:20]:
            openalex_only_html += f'''
            <div class="rank-item">
                <div>{safe_escape(ref.get('text', ''))}</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref.get('doi', ''))}</div>
            </div>
            '''
    else:
        openalex_only_html = '<p>No references with only OpenAlex data</p>'
    
    # ========== SUSPICIOUS DOIS ==========
    suspicious_doi_html = ''
    if suspicious_doi_refs:
        for ref in suspicious_doi_refs[:20]:
            suspicious_doi_html += f'''
            <div class="rank-item suspicious-reference">
                <div class="badge badge-danger">⚠️ Attention: invalid/suspicious DOI</div>
                <div>{safe_escape(ref.get('text', ''))}</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref.get('doi', ''))}</div>
            </div>
            '''
    else:
        suspicious_doi_html = '<p>No suspicious DOIs detected</p>'
    
    # ========== REPOSITORY REFS ==========
    repository_html = ''
    if repository_refs:
        for ref in repository_refs[:20]:
            repository_html += f'''
            <div class="rank-item repository-reference">
                <span class="badge-repository">Repository</span>
                <div style="margin-top: 8px;">{safe_escape(ref.get('text', ''))}</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref.get('doi', ''))}</div>
            </div>
            '''
    
    # ========== PROCEEDINGS REFS ==========
    proceedings_html = ''
    if proceedings_refs:
        for ref in proceedings_refs[:20]:
            proceedings_html += f'''
            <div class="rank-item proceedings-reference">
                <span class="badge-proceedings">Proceedings</span>
                <div style="margin-top: 8px;">{safe_escape(ref.get('text', ''))}</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref.get('doi', ''))}</div>
            </div>
            '''
    
    # ========== RETRACTED REFS ==========
    retracted_html = ''
    if retracted_refs:
        for ref in retracted_refs[:20]:
            retracted_html += f'''
            <div class="rank-item retracted-reference">
                <span class="badge-danger">Retracted</span>
                <div style="margin-top: 8px;">{safe_escape(ref.get('text', ''))}</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref.get('doi', ''))}</div>
            </div>
            '''
    
    # ========== BOOKS WITH ISBN ==========
    books_html = ''
    if books_with_isbn_no_doi:
        for ref in books_with_isbn_no_doi[:20]:
            books_html += f'''
            <div class="rank-item book-reference">
                <span class="badge-book">Ebook</span>
                <div style="margin-top: 8px;">{safe_escape(ref)}</div>
            </div>
            '''
    
    # ========== NON-JOURNAL SOURCES ==========
    nonjournal_html = ''
    if non_journal_sources_with_doi:
        for source in non_journal_sources_with_doi[:20]:
            badge_class = "badge-repository" if source.get('type') == 'repository' else ("badge-book" if source.get('type') == 'ebook' else "badge-proceedings")
            badge_text = source.get('type', 'Source').capitalize()
            nonjournal_html += f'''
            <div class="rank-item">
                <span class="{badge_class}">{badge_text}</span>
                <div style="margin-top: 8px;">{safe_escape(source.get('text', ''))}</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(source.get('doi', ''))}</div>
            </div>
            '''
    
    # ========== URL SOURCES ==========
    url_html = ''
    if references_with_only_url:
        for ref in references_with_only_url[:20]:
            url_html += f'''
            <div class="rank-item">{safe_escape(ref)}</div>
            '''
    else:
        url_html = '<p>No URL-only references found</p>'
    
    # ========== PROBLEMS SECTION ==========
    problems_html = ''
    if retracted_refs:
        problems_html += f'''
        <div style="margin-bottom: 20px;">
            <h4>Retracted:</h4>
            {retracted_html if retracted_html else '<p>None detected</p>'}
        </div>
        '''
    
    if problematic_refs:
        problems_html += f'''
        <div>
            <h4>Other problematic references:</h4>
        '''
        for ref in problematic_refs[:10]:
            problems_html += f'''
            <div class="rank-item">
                <span class="badge badge-warning">{safe_escape(ref.get('problems', ''))}</span>
                <div style="margin-top: 8px;">{safe_escape(ref.get('text', ''))}</div>
            </div>
            '''
        problems_html += '</div>'
    
    if not problems_html:
        problems_html = '<p>No problematic references detected</p>'
    
    # ========== FULL REFERENCE LIST ==========
    full_refs_html = ''
    for idx, result in enumerate(results[:500]):
        original_text = safe_escape(result.get('original_text', ''))
        authors_display = ', '.join([safe_escape(a) for a in result.get('authors_display', [])])
        doi = result.get('doi', '')
        
        status_icon = "⚠️" if result.get('is_suspicious_doi') else ("✅" if doi else "❌")
        
        special_badge = ""
        if result.get('is_retracted', False):
            special_badge = f'<span class="badge-danger" style="margin-left: 10px;">Retracted</span>'
        elif result.get('is_ebook', False):
            special_badge = f'<span class="badge-book" style="margin-left: 10px;">Ebook</span>'
        elif result.get('is_repository', False):
            special_badge = f'<span class="badge-repository" style="margin-left: 10px;">Repository</span>'
        elif result.get('is_proceedings', False):
            special_badge = f'<span class="badge-proceedings" style="margin-left: 10px;">Proceedings</span>'
        elif result.get('is_suspicious_doi', False):
            special_badge = f'<span class="badge-danger" style="margin-left: 10px;">⚠️ Suspicious DOI</span>'
        
        color_class = ""
        if result.get('is_retracted', False):
            color_class = "retracted-reference"
        elif result.get('is_suspicious_doi', False):
            color_class = "suspicious-reference"
        elif result.get('is_ebook', False):
            color_class = "ebook-reference"
        elif result.get('is_repository', False):
            color_class = "repository-reference"
        elif result.get('is_proceedings', False):
            color_class = "proceedings-reference"
        elif not doi:
            color_class = "notfound-reference"
        else:
            color_class = "normal-article"
        
        full_refs_html += f'''
        <div class="rank-item {color_class}" style="margin-bottom: 15px;">
            <div><strong>{status_icon} Reference {idx + 1}:</strong>{special_badge}</div>
            <div class="full-text-container">{original_text}</div>
            <div style="font-size: 13px; margin-top: 5px;"><strong>Authors:</strong> {authors_display}</div>
            <div style="font-size: 13px; margin-top: 5px;"><strong>DOI found:</strong> {make_clickable_doi(doi)}</div>
        </div>
        '''
    
    # ========== CSS ==========
    if custom_css:
        css_to_use = custom_css
    else:
        css_to_use = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 0;
            margin: 0;
        }
        .report-wrapper {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .sidebar {
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
        }
        .sidebar h3 {
            margin-bottom: 20px;
            font-size: 18px;
            font-weight: 600;
        }
        .sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 8px;
            transition: all 0.3s;
            font-size: 14px;
        }
        .sidebar a:hover {
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }
        .main-content {
            margin-left: 260px;
            padding: 30px 40px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header .date {
            opacity: 0.9;
            margin-top: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
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
        .metric-percent {
            font-size: 12px;
            color: #155724;
            background-color: #d4edda;
            padding: 3px 10px;
            border-radius: 20px;
            margin-top: 8px;
            display: inline-block;
        }
        .metric-label {
            color: #666;
            font-size: 14px;
            margin-top: 8px;
        }
        .section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .section-title {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
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
            width: 300px;
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
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        .badge-repository { background: #e2d5f8; color: #5e2a9e; }
        .badge-book { background: #d4f1e9; color: #0e6b5e; }
        .badge-proceedings { background: #fff2c9; color: #b26b00; }
        
        .concepts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .concept-card {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-radius: 10px;
            padding: 12px;
            text-align: center;
            border: 1px solid #667eea30;
        }
        .concept-name {
            font-weight: 600;
            color: #667eea;
        }
        .concept-score {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
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
        
        .normal-article { background: #e8f5e9 !important; border-left: 3px solid #4caf50 !important; }
        .notfound-reference { background: #e9ecef !important; border-left: 3px solid #6c757d !important; }
        .suspicious-reference { background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }
        .duplicate-reference { background: #ffe5cc !important; border-left: 3px solid #fd7e14 !important; }
        .ebook-reference { background: #d4f1e9 !important; border-left: 3px solid #0e6b5e !important; }
        .repository-reference { background: #e2d5f8 !important; border-left: 3px solid #5e2a9e !important; }
        .proceedings-reference { background: #fff2c9 !important; border-left: 3px solid #b26b00 !important; }
        .retracted-reference { background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
            margin-top: 30px;
        }
        .clickable-link {
            color: #667eea;
            text-decoration: none;
            transition: all 0.3s;
        }
        .clickable-link:hover {
            color: #764ba2;
            text-decoration: underline;
        }
        
        @media print {
            .sidebar { display: none; }
            .main-content { margin-left: 0; }
            .metric-card, .section { break-inside: avoid; }
        }
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .main-content { margin-left: 0; padding: 20px; }
        }
        """
    
    # ========== ЗАГОЛОВОК ==========
    if custom_header:
        header_html = custom_header
    else:
        header_html = f'''
        <div class="header">
            <h1>Comprehensive Reference List Analysis</h1>
            <div>Journal: {safe_escape(journal_name)}</div>
            {f'<div>Article number: {safe_escape(article_number)}</div>' if article_number else ''}
            <div class="date">Generated: {get_date()}</div>
        </div>
        '''
    
    # ========== СБОРКА HTML ==========
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Reference List Analysis</title>
    <style>
        {css_to_use}
    </style>
</head>
<body>
    {sidebar_html}
    
    <div class="main-content">
        {header_html}
        
        <!-- OVERVIEW SECTION -->
        <div id="overview" class="section">
            <div class="section-title">Overview</div>
            {metrics_html}
        </div>
        
        <!-- IDENTIFIER COVERAGE SECTION -->
        <div id="identifiers" class="section">
            <div class="section-title">Identifier Coverage Analysis</div>
            {identifier_html}
        </div>
        
        <!-- AUTHORS SECTION -->
        <div id="authors" class="section">
            <div class="section-title">Top Authors (with intelligent merging)</div>
            {authors_html}
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Unique authors: {unique_authors}</span>
                <span class="badge badge-info">Shannon index: {shannon_index.get('authors', 0)}</span>
                <span class="badge badge-info">ORCID coverage: {orcid_coverage.get('with_orcid', 0)} ({orcid_coverage.get('coverage_percent', 0):.1f}%)</span>
            </div>
        </div>
        
        <!-- JOURNALS SECTION -->
        <div id="journals" class="section">
            <div class="section-title">All Journals (sorted by frequency)</div>
            <table>
                <thead>
                    <tr><th>Rank</th><th>Journal</th><th>Count</th><th>Percentage</th></tr>
                </thead>
                <tbody>
                    {journals_html}
                </tbody>
            </table>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Unique journals: {unique_journals}</span>
                <span class="badge badge-info">Shannon index: {shannon_index.get('journals', 0)}</span>
            </div>
        </div>
        
        <!-- PUBLISHERS SECTION -->
        <div id="publishers" class="section">
            <div class="section-title">All Publishers (sorted by frequency)</div>
            <table>
                <thead>
                    <tr><th>Rank</th><th>Publisher</th><th>Count</th><th>Percentage</th></tr>
                </thead>
                <tbody>
                    {publishers_html}
                </tbody>
            </table>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Unique publishers: {unique_publishers}</span>
                <span class="badge badge-info">Shannon index: {shannon_index.get('publishers', 0)}</span>
            </div>
        </div>
        
        <!-- YEARLY SECTION -->
        <div id="yearly" class="section">
            <div class="section-title">Yearly Statistics</div>
            {yearly_html}
        </div>
        
        <!-- CONCEPTS SECTION -->
        <div id="concepts" class="section">
            <div class="section-title">Key Scientific Concepts</div>
            {concepts_html}
        </div>
        
        <!-- GEOGRAPHY SECTION -->
        <div id="geography" class="section">
            <div class="section-title">Geographic Distribution</div>
            {geography_html}
        </div>
        
        <!-- COLLABORATION SECTION -->
        <div id="collaboration" class="section">
            <div class="section-title">Collaboration Networks</div>
            <div>
                {collaboration_html}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Core authors: {core_authors_html}</span>
            </div>
        </div>
        
        <!-- DIVERSITY SECTION -->
        <div id="diversity" class="section">
            <div class="section-title">Diversity Analysis</div>
            {diversity_html}
        </div>
        
        <!-- CITATION CLASSICS SECTION -->
        <div id="classics" class="section">
            <div class="section-title">Citation Classics</div>
            {classics_html}
        </div>
        
        <!-- SELF-CITATIONS SECTION -->
        {f'''
        <div id="selfcitations" class="section">
            <div class="section-title">Self-Citations</div>
            {self_citations_html}
            <div style="margin-top: 15px;">
                <span class="badge badge-info">Total self-citations: {self_citations_count} ({self_citations_percent:.1f}%)</span>
            </div>
        </div>
        ''' if self_citation_refs else ''}
        
        <!-- DUPLICATES SECTION -->
        {f'''
        <div id="duplicates" class="section">
            <div class="section-title">Duplicate References (Full DOI Match)</div>
            {duplicates_html}
        </div>
        ''' if duplicates else ''}
        
        <!-- ONLY CROSSREF SECTION -->
        <div id="crossref_only" class="section">
            <div class="section-title">References with Only Crossref (OpenAlex missing)</div>
            {crossref_only_html}
        </div>
        
        <!-- ONLY OPENALEX SECTION -->
        <div id="openalex_only" class="section">
            <div class="section-title">References with Only OpenAlex (Crossref missing)</div>
            {openalex_only_html}
        </div>
        
        <!-- SUSPICIOUS DOIS SECTION -->
        <div id="suspicious_doi" class="section">
            <div class="section-title">Suspicious DOIs</div>
            <div style="margin-bottom: 15px; font-size: 13px; color: #666;">These DOIs were extracted from references but returned no data from Crossref or OpenAlex. May be invalid, typo, or AI-generated.</div>
            
            {f'''
            <div style="margin-top: 10px; margin-bottom: 15px;">
                <h4>Repository references:</h4>
                <div style="font-size: 12px; color: #5e2a9e; margin-bottom: 10px;">📚 Repository source (not invalid)</div>
                {repository_html}
            </div>
            ''' if repository_refs else ''}
            
            {f'''
            <div style="margin-top: 10px; margin-bottom: 15px;">
                <h4>Proceedings references:</h4>
                <div style="font-size: 12px; color: #b26b00; margin-bottom: 10px;">📊 Conference proceedings (not invalid)</div>
                {proceedings_html}
            </div>
            ''' if proceedings_refs else ''}
            
            <div style="margin-top: 10px;">
                <h4>Suspicious DOIs:</h4>
                {suspicious_doi_html}
            </div>
        </div>
        
        <!-- NON-DOI SOURCES SECTION -->
        <div id="non_doi" class="section">
            <div class="section-title">Non-DOI Sources (Books, Theses, Conference Papers, etc.)</div>
            
            {f'''
            <div style="margin-bottom: 15px;">
                <h4>Books (ISBN without DOI):</h4>
                {books_html}
            </div>
            ''' if books_with_isbn_no_doi else ''}
            
            <div>
                <h4>Other non-DOI sources:</h4>
                {''.join([f'<div class="rank-item notfound-reference">{safe_escape(ref)}</div>' for ref in references_without_doi[:20]]) if references_without_doi else '<p>All references have DOI identifiers</p>'}
            </div>
        </div>
        
        <!-- NON-JOURNAL SOURCES WITH DOI SECTION -->
        {f'''
        <div id="nonjournal" class="section">
            <div class="section-title">Non-journal Sources with DOI</div>
            <div style="margin-bottom: 15px; font-size: 13px; color: #666;">Preprints, repositories, conference proceedings, and e-books that have valid DOIs</div>
            {nonjournal_html}
        </div>
        ''' if non_journal_sources_with_doi else ''}
        
        <!-- URL SOURCES SECTION -->
        <div id="url_sources" class="section">
            <div class="section-title">URL Sources (Web links without DOI)</div>
            {url_html}
        </div>
        
        <!-- PROBLEMS SECTION -->
        <div id="problems" class="section">
            <div class="section-title">Problematic References</div>
            {problems_html}
        </div>
        
        <!-- FULL REFERENCE LIST SECTION -->
        <div id="full_reference_list" class="section">
            <div class="section-title">Full Reference List</div>
            {full_refs_html}
            {f'<p style="margin-top: 15px; color: #666;">Showing first 500 of {len(results)} references</p>' if len(results) > 500 else ''}
        </div>
        
        <div class="footer">
            {get_footer(journal_name)}
        </div>
    </div>
</body>
</html>'''
    
    return html_content

# ============================================================
# СТИЛЬ 0: КЛАССИЧЕСКИЙ (ИСХОДНЫЙ)
# ============================================================

def generate_style_0_classic(data: Dict) -> str:
    """Стиль 0: Классический (исходный дизайн)"""
    return generate_full_report_html(data)

# ============================================================
# СТИЛЬ 1: GLASSMORPHISM
# ============================================================

def generate_style_1_glassmorphism(data: Dict) -> str:
    """Стиль 1: Glassmorphism — стеклянный эффект с размытием"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 30px; font-family: 'Segoe UI', sans-serif; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: rgba(255,255,255,0.12); backdrop-filter: blur(20px);
        color: white; padding: 30px 20px; overflow-y: auto; z-index: 1000;
        border-right: 1px solid rgba(255,255,255,0.15);
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; }
    .sidebar a {
        color: white; text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
        background: rgba(255,255,255,0.05);
    }
    .sidebar a:hover { background: rgba(255,255,255,0.2); transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 30px 40px; }
    .header {
        background: rgba(255,255,255,0.12); backdrop-filter: blur(20px);
        border-radius: 20px; padding: 40px; margin-bottom: 30px; text-align: center;
        border: 1px solid rgba(255,255,255,0.15);
        color: white;
    }
    .header h1 { font-size: 32px; margin-bottom: 10px; }
    .header .date { opacity: 0.8; margin-top: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: rgba(255,255,255,0.08); backdrop-filter: blur(10px);
        border-radius: 16px; padding: 20px; text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s;
        color: white;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-number { font-size: 36px; font-weight: bold; color: white; }
    .metric-percent { font-size: 12px; background: rgba(255,255,255,0.15); padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; color: rgba(255,255,255,0.8); }
    .metric-label { color: rgba(255,255,255,0.7); font-size: 14px; margin-top: 8px; }
    .section {
        background: rgba(255,255,255,0.08); backdrop-filter: blur(10px);
        border-radius: 16px; padding: 25px; margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid rgba(255,255,255,0.15); color: white; }
    .rank-item {
        background: rgba(255,255,255,0.06); border-radius: 10px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid rgba(255,255,255,0.3);
        color: white;
    }
    .rank-item:hover { transform: translateX(5px); background: rgba(255,255,255,0.1); }
    .rank-number { font-weight: bold; color: white; font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: white; }
    .rank-count { float: right; color: rgba(255,255,255,0.7); }
    .progress-bar-custom { background: rgba(255,255,255,0.15); border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, rgba(255,255,255,0.5), rgba(255,255,255,0.8)); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: rgba(255,255,255,0.15); color: white; }
    .badge-success { background: rgba(46, 204, 113, 0.3); color: #2ecc71; }
    .badge-warning { background: rgba(241, 196, 15, 0.3); color: #f1c40f; }
    .badge-danger { background: rgba(231, 76, 60, 0.3); color: #e74c3c; }
    .badge-info { background: rgba(52, 152, 219, 0.3); color: #3498db; }
    .badge-repository { background: rgba(155, 89, 182, 0.3); color: #9b59b6; }
    .badge-book { background: rgba(26, 188, 156, 0.3); color: #1abc9c; }
    .badge-proceedings { background: rgba(241, 196, 15, 0.3); color: #f1c40f; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: rgba(255,255,255,0.06); border-radius: 10px; padding: 12px; text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .concept-name { font-weight: 600; color: white; }
    .concept-score { font-size: 12px; color: rgba(255,255,255,0.6); margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: rgba(0,0,0,0.15); padding: 8px; border-radius: 5px; margin-top: 5px;
        color: rgba(255,255,255,0.8);
    }
    
    .normal-article { background: rgba(46, 204, 113, 0.15) !important; border-left: 3px solid #2ecc71 !important; }
    .notfound-reference { background: rgba(149, 165, 166, 0.15) !important; border-left: 3px solid #95a5a6 !important; }
    .suspicious-reference { background: rgba(231, 76, 60, 0.15) !important; border-left: 3px solid #e74c3c !important; }
    .duplicate-reference { background: rgba(241, 196, 15, 0.15) !important; border-left: 3px solid #f1c40f !important; }
    .ebook-reference { background: rgba(26, 188, 156, 0.15) !important; border-left: 3px solid #1abc9c !important; }
    .repository-reference { background: rgba(155, 89, 182, 0.15) !important; border-left: 3px solid #9b59b6 !important; }
    .proceedings-reference { background: rgba(241, 196, 15, 0.15) !important; border-left: 3px solid #f1c40f !important; }
    .retracted-reference { background: rgba(231, 76, 60, 0.15) !important; border-left: 3px solid #e74c3c !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.08); color: white; }
    th { background: rgba(255,255,255,0.1); }
    tr:hover { background: rgba(255,255,255,0.05); }
    .footer { text-align: center; padding: 20px; color: rgba(255,255,255,0.4); font-size: 12px; border-top: 1px solid rgba(255,255,255,0.08); margin-top: 30px; }
    .clickable-link { color: rgba(255,255,255,0.8); text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: white; text-decoration: underline; }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } .metric-card, .section { break-inside: avoid; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 2: NEON CYBER
# ============================================================

def generate_style_2_neon_cyber(data: Dict) -> str:
    """Стиль 2: Neon Cyber — неоновое свечение на темном фоне"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #0a0a0f; padding: 30px; font-family: 'Courier New', monospace; color: #fff; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: rgba(0,255,255,0.03); border-right: 1px solid rgba(0,255,255,0.1);
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
    }
    .sidebar h3 { color: #00ffff; text-shadow: 0 0 20px rgba(0,255,255,0.2); margin-bottom: 20px; font-size: 18px; }
    .sidebar a {
        color: rgba(0,255,255,0.6); text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
        border: 1px solid transparent;
    }
    .sidebar a:hover { color: #00ffff; border-color: rgba(0,255,255,0.2); text-shadow: 0 0 20px rgba(0,255,255,0.1); }
    .main-content { margin-left: 260px; padding: 30px 40px; }
    .header {
        background: rgba(0,255,255,0.03); border: 1px solid rgba(0,255,255,0.15);
        border-radius: 12px; padding: 40px; margin-bottom: 30px; text-align: center;
        box-shadow: 0 0 40px rgba(0,255,255,0.05);
    }
    .header h1 { font-size: 32px; color: #00ffff; text-shadow: 0 0 30px rgba(0,255,255,0.3); }
    .header .date { color: rgba(0,255,255,0.4); margin-top: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: rgba(0,255,255,0.03); border: 1px solid rgba(0,255,255,0.1);
        border-radius: 12px; padding: 20px; text-align: center;
        transition: all 0.3s;
    }
    .metric-card:hover { border-color: #00ffff; box-shadow: 0 0 30px rgba(0,255,255,0.05); }
    .metric-number { font-size: 36px; font-weight: bold; color: #00ffff; text-shadow: 0 0 30px rgba(0,255,255,0.2); }
    .metric-percent { font-size: 12px; color: rgba(0,255,255,0.5); background: rgba(0,255,255,0.05); padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: rgba(0,255,255,0.5); font-size: 14px; margin-top: 8px; }
    .section {
        background: rgba(0,255,255,0.02); border: 1px solid rgba(0,255,255,0.06);
        border-radius: 12px; padding: 25px; margin-bottom: 30px;
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(0,255,255,0.1); color: #00ffff; text-shadow: 0 0 20px rgba(0,255,255,0.1); }
    .rank-item {
        background: rgba(0,255,255,0.02); border: 1px solid rgba(0,255,255,0.04);
        border-radius: 8px; padding: 12px; margin-bottom: 8px;
        transition: all 0.3s;
    }
    .rank-item:hover { border-color: rgba(0,255,255,0.2); transform: translateX(5px); }
    .rank-number { font-weight: bold; color: #ff00ff; font-size: 18px; display: inline-block; width: 40px; text-shadow: 0 0 20px rgba(255,0,255,0.2); }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: rgba(255,255,255,0.8); }
    .rank-count { float: right; color: rgba(0,255,255,0.5); }
    .progress-bar-custom { background: rgba(0,255,255,0.05); border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #00ffff, #ff00ff); height: 100%; border-radius: 10px; box-shadow: 0 0 20px rgba(0,255,255,0.2); }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid rgba(0,255,255,0.2); color: #00ffff; background: rgba(0,255,255,0.05); }
    .badge-success { border-color: rgba(46, 204, 113, 0.3); color: #2ecc71; }
    .badge-warning { border-color: rgba(241, 196, 15, 0.3); color: #f1c40f; }
    .badge-danger { border-color: rgba(231, 76, 60, 0.3); color: #e74c3c; }
    .badge-info { border-color: rgba(52, 152, 219, 0.3); color: #3498db; }
    .badge-repository { border-color: rgba(155, 89, 182, 0.3); color: #9b59b6; }
    .badge-book { border-color: rgba(26, 188, 156, 0.3); color: #1abc9c; }
    .badge-proceedings { border-color: rgba(241, 196, 15, 0.3); color: #f1c40f; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: rgba(0,255,255,0.02); border: 1px solid rgba(0,255,255,0.06);
        border-radius: 8px; padding: 12px; text-align: center;
    }
    .concept-name { font-weight: 600; color: #00ffff; }
    .concept-score { font-size: 12px; color: rgba(0,255,255,0.4); margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: rgba(0,0,0,0.3); padding: 8px; border-radius: 5px; margin-top: 5px;
        color: rgba(255,255,255,0.6);
    }
    
    .normal-article { border-left: 3px solid #00ff00 !important; }
    .notfound-reference { border-left: 3px solid #666 !important; }
    .suspicious-reference { border-left: 3px solid #ff0000 !important; }
    .duplicate-reference { border-left: 3px solid #ffff00 !important; }
    .ebook-reference { border-left: 3px solid #00ffff !important; }
    .repository-reference { border-left: 3px solid #ff00ff !important; }
    .proceedings-reference { border-left: 3px solid #ffff00 !important; }
    .retracted-reference { border-left: 3px solid #ff0000 !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(0,255,255,0.06); color: rgba(255,255,255,0.7); }
    th { background: rgba(0,255,255,0.05); color: #00ffff; }
    tr:hover { background: rgba(0,255,255,0.02); }
    .footer { text-align: center; padding: 20px; color: rgba(0,255,255,0.2); font-size: 12px; border-top: 1px solid rgba(0,255,255,0.06); margin-top: 30px; }
    .clickable-link { color: #00ffff; text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: #ff00ff; text-shadow: 0 0 20px rgba(255,0,255,0.2); }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 3: GLASS ENHANCED
# ============================================================

def generate_style_3_glass_enhanced(data: Dict) -> str:
    """Стиль 3: Glassmorphism Enhanced — улучшенный стеклянный эффект"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { min-height: 100vh; background: linear-gradient(135deg, #0c0c1e 0%, #1a1a3e 50%, #2d1b69 100%); padding: 30px; font-family: 'Segoe UI', sans-serif; color: #fff; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: rgba(255,255,255,0.04); backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; background: linear-gradient(135deg, #f7971e, #ffd200); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sidebar a {
        color: rgba(255,255,255,0.5); text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
    }
    .sidebar a:hover { background: rgba(255,255,255,0.05); color: #fff; transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 30px 40px; }
    .header {
        background: rgba(255,255,255,0.04); backdrop-filter: blur(20px);
        border-radius: 20px; padding: 40px; margin-bottom: 30px; text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .header h1 { font-size: 32px; font-weight: 700; background: linear-gradient(135deg, #f7971e, #ffd200); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .header .date { color: rgba(255,255,255,0.3); margin-top: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: rgba(255,255,255,0.03); backdrop-filter: blur(10px);
        border-radius: 16px; padding: 20px; text-align: center;
        border: 1px solid rgba(255,255,255,0.04);
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: rgba(247,151,30,0.2); }
    .metric-number { font-size: 36px; font-weight: bold; background: linear-gradient(135deg, #f7971e, #ffd200); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-percent { font-size: 12px; color: rgba(255,255,255,0.5); background: rgba(255,255,255,0.04); padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: rgba(255,255,255,0.5); font-size: 14px; margin-top: 8px; }
    .section {
        background: rgba(255,255,255,0.03); backdrop-filter: blur(10px);
        border-radius: 16px; padding: 25px; margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.06); color: rgba(255,255,255,0.8); }
    .rank-item {
        background: rgba(255,255,255,0.02); border-radius: 10px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid rgba(247,151,30,0.3);
        transition: all 0.3s;
    }
    .rank-item:hover { background: rgba(255,255,255,0.04); transform: translateX(5px); }
    .rank-number { font-weight: bold; color: #f7971e; font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: rgba(255,255,255,0.8); }
    .rank-count { float: right; color: rgba(255,255,255,0.4); }
    .progress-bar-custom { background: rgba(255,255,255,0.04); border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #f7971e, #ffd200); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.04); }
    .badge-success { border-color: rgba(46, 204, 113, 0.2); color: #2ecc71; }
    .badge-warning { border-color: rgba(241, 196, 15, 0.2); color: #f1c40f; }
    .badge-danger { border-color: rgba(231, 76, 60, 0.2); color: #e74c3c; }
    .badge-info { border-color: rgba(52, 152, 219, 0.2); color: #3498db; }
    .badge-repository { border-color: rgba(155, 89, 182, 0.2); color: #9b59b6; }
    .badge-book { border-color: rgba(26, 188, 156, 0.2); color: #1abc9c; }
    .badge-proceedings { border-color: rgba(241, 196, 15, 0.2); color: #f1c40f; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: rgba(255,255,255,0.02); border-radius: 10px; padding: 12px; text-align: center;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .concept-name { font-weight: 600; color: #f7971e; }
    .concept-score { font-size: 12px; color: rgba(255,255,255,0.3); margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: rgba(0,0,0,0.2); padding: 8px; border-radius: 5px; margin-top: 5px;
        color: rgba(255,255,255,0.5);
    }
    
    .normal-article { border-left: 3px solid #2ecc71 !important; }
    .notfound-reference { border-left: 3px solid #666 !important; }
    .suspicious-reference { border-left: 3px solid #e74c3c !important; }
    .duplicate-reference { border-left: 3px solid #f1c40f !important; }
    .ebook-reference { border-left: 3px solid #1abc9c !important; }
    .repository-reference { border-left: 3px solid #9b59b6 !important; }
    .proceedings-reference { border-left: 3px solid #f1c40f !important; }
    .retracted-reference { border-left: 3px solid #e74c3c !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.04); color: rgba(255,255,255,0.6); }
    th { background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.8); }
    tr:hover { background: rgba(255,255,255,0.02); }
    .footer { text-align: center; padding: 20px; color: rgba(255,255,255,0.2); font-size: 12px; border-top: 1px solid rgba(255,255,255,0.04); margin-top: 30px; }
    .clickable-link { color: #f7971e; text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: #ffd200; }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 4: SMART GLOW
# ============================================================

def generate_style_4_smart_glow(data: Dict) -> str:
    """Стиль 4: Smart Glow — умная аналитика с подсветкой"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #0d1117; padding: 30px; font-family: 'Inter', sans-serif; color: #e6edf3; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: #161b22; border-right: 1px solid #30363d;
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; color: #58a6ff; }
    .sidebar a {
        color: #8b949e; text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
    }
    .sidebar a:hover { background: #21262d; color: #c9d1d9; transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 30px 40px; }
    .header {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d; border-radius: 16px; padding: 40px; margin-bottom: 30px; text-align: center;
        box-shadow: 0 4px 30px rgba(0,0,0,0.3);
    }
    .header h1 { font-size: 32px; font-weight: 700; background: linear-gradient(135deg, #58a6ff, #f0883e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .header .date { color: #8b949e; margin-top: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: #0d1117; border: 1px solid #30363d; border-radius: 14px; padding: 20px; text-align: center;
        transition: all 0.3s;
    }
    .metric-card:hover { border-color: #58a6ff; box-shadow: 0 0 30px rgba(88,166,255,0.05); }
    .metric-number { font-size: 36px; font-weight: bold; color: #58a6ff; }
    .metric-percent { font-size: 12px; color: #8b949e; background: #161b22; padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: #8b949e; font-size: 14px; margin-top: 8px; }
    .section {
        background: #0d1117; border: 1px solid #30363d; border-radius: 14px; padding: 25px; margin-bottom: 30px;
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #30363d; color: #c9d1d9; }
    .rank-item {
        background: #0d1117; border: 1px solid #21262d; border-radius: 10px; padding: 12px; margin-bottom: 8px;
        transition: all 0.3s;
    }
    .rank-item:hover { border-color: #58a6ff; transform: translateX(5px); }
    .rank-number { font-weight: bold; color: #58a6ff; font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: #c9d1d9; }
    .rank-count { float: right; color: #8b949e; }
    .progress-bar-custom { background: #21262d; border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #58a6ff, #f0883e); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .badge-success { border-color: rgba(46, 204, 113, 0.3); color: #2ecc71; }
    .badge-warning { border-color: rgba(241, 196, 15, 0.3); color: #f1c40f; }
    .badge-danger { border-color: rgba(231, 76, 60, 0.3); color: #e74c3c; }
    .badge-info { border-color: rgba(52, 152, 219, 0.3); color: #3498db; }
    .badge-repository { border-color: rgba(155, 89, 182, 0.3); color: #9b59b6; }
    .badge-book { border-color: rgba(26, 188, 156, 0.3); color: #1abc9c; }
    .badge-proceedings { border-color: rgba(241, 196, 15, 0.3); color: #f1c40f; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: #0d1117; border: 1px solid #21262d; border-radius: 10px; padding: 12px; text-align: center;
    }
    .concept-name { font-weight: 600; color: #58a6ff; }
    .concept-score { font-size: 12px; color: #8b949e; margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: #0d1117; padding: 8px; border-radius: 5px; margin-top: 5px;
        color: #8b949e; border: 1px solid #21262d;
    }
    
    .normal-article { border-left: 3px solid #2ecc71 !important; }
    .notfound-reference { border-left: 3px solid #666 !important; }
    .suspicious-reference { border-left: 3px solid #e74c3c !important; }
    .duplicate-reference { border-left: 3px solid #f1c40f !important; }
    .ebook-reference { border-left: 3px solid #1abc9c !important; }
    .repository-reference { border-left: 3px solid #9b59b6 !important; }
    .proceedings-reference { border-left: 3px solid #f1c40f !important; }
    .retracted-reference { border-left: 3px solid #e74c3c !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #21262d; color: #8b949e; }
    th { background: #161b22; color: #c9d1d9; }
    tr:hover { background: #161b22; }
    .footer { text-align: center; padding: 20px; color: #21262d; font-size: 12px; border-top: 1px solid #21262d; margin-top: 30px; }
    .clickable-link { color: #58a6ff; text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: #f0883e; }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 5: AURORA
# ============================================================

def generate_style_5_aurora(data: Dict) -> str:
    """Стиль 5: Aurora — северное сияние с плавными градиентами"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { min-height: 100vh; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); padding: 30px; font-family: 'Segoe UI', sans-serif; color: #fff; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: rgba(255,255,255,0.02); border-right: 1px solid rgba(255,255,255,0.03);
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
        backdrop-filter: blur(10px);
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; color: rgba(255,255,255,0.6); letter-spacing: 2px; }
    .sidebar a {
        color: rgba(255,255,255,0.3); text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
        letter-spacing: 1px;
    }
    .sidebar a:hover { background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.8); transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 30px 40px; }
    .header {
        background: rgba(255,255,255,0.02); border-radius: 20px; padding: 40px; margin-bottom: 30px; text-align: center;
        border: 1px solid rgba(255,255,255,0.03);
        position: relative; overflow: hidden;
    }
    .header::before {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(0,255,200,0.03), transparent, rgba(200,0,255,0.03), transparent);
        animation: rotate_aurora 20s linear infinite; pointer-events: none;
    }
    @keyframes rotate_aurora { 100% { transform: rotate(360deg); } }
    .header h1 { font-size: 32px; font-weight: 300; background: linear-gradient(90deg, #00ff87, #60efff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; position: relative; z-index: 1; }
    .header .date { color: rgba(255,255,255,0.2); margin-top: 10px; position: relative; z-index: 1; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: rgba(255,255,255,0.02); border-radius: 16px; padding: 20px; text-align: center;
        border: 1px solid rgba(255,255,255,0.03);
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: rgba(0,255,200,0.1); }
    .metric-number { font-size: 36px; font-weight: bold; background: linear-gradient(135deg, #00ff87, #60efff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-percent { font-size: 12px; color: rgba(255,255,255,0.3); background: rgba(255,255,255,0.02); padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: rgba(255,255,255,0.3); font-size: 14px; margin-top: 8px; letter-spacing: 1px; }
    .section {
        background: rgba(255,255,255,0.02); border-radius: 16px; padding: 25px; margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.03);
        position: relative; overflow: hidden;
    }
    .section::before {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(0,255,200,0.02), transparent, rgba(200,0,255,0.02), transparent);
        animation: rotate_aurora 25s linear infinite; pointer-events: none;
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.03); color: rgba(255,255,255,0.6); letter-spacing: 2px; position: relative; z-index: 1; }
    .rank-item {
        background: rgba(255,255,255,0.01); border-radius: 10px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid rgba(0,255,200,0.2);
        transition: all 0.3s; position: relative; z-index: 1;
    }
    .rank-item:hover { background: rgba(255,255,255,0.02); transform: translateX(5px); border-left-color: rgba(0,255,200,0.5); }
    .rank-number { font-weight: bold; color: #60efff; font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: rgba(255,255,255,0.7); }
    .rank-count { float: right; color: rgba(255,255,255,0.3); }
    .progress-bar-custom { background: rgba(255,255,255,0.03); border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #00ff87, #60efff, #a78bfa); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.4); border: 1px solid rgba(255,255,255,0.03); }
    .badge-success { border-color: rgba(0,255,135,0.2); color: #00ff87; }
    .badge-warning { border-color: rgba(255,215,0,0.2); color: #ffd700; }
    .badge-danger { border-color: rgba(255,100,100,0.2); color: #ff6b6b; }
    .badge-info { border-color: rgba(96,239,255,0.2); color: #60efff; }
    .badge-repository { border-color: rgba(167,139,250,0.2); color: #a78bfa; }
    .badge-book { border-color: rgba(0,255,200,0.2); color: #00ffc8; }
    .badge-proceedings { border-color: rgba(255,215,0,0.2); color: #ffd700; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: rgba(255,255,255,0.01); border-radius: 10px; padding: 12px; text-align: center;
        border: 1px solid rgba(255,255,255,0.03);
    }
    .concept-name { font-weight: 600; color: #60efff; }
    .concept-score { font-size: 12px; color: rgba(255,255,255,0.2); margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: rgba(0,0,0,0.2); padding: 8px; border-radius: 5px; margin-top: 5px;
        color: rgba(255,255,255,0.3);
    }
    
    .normal-article { border-left: 3px solid #00ff87 !important; }
    .notfound-reference { border-left: 3px solid #666 !important; }
    .suspicious-reference { border-left: 3px solid #ff6b6b !important; }
    .duplicate-reference { border-left: 3px solid #ffd700 !important; }
    .ebook-reference { border-left: 3px solid #00ffc8 !important; }
    .repository-reference { border-left: 3px solid #a78bfa !important; }
    .proceedings-reference { border-left: 3px solid #ffd700 !important; }
    .retracted-reference { border-left: 3px solid #ff6b6b !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.02); color: rgba(255,255,255,0.3); }
    th { background: rgba(255,255,255,0.01); color: rgba(255,255,255,0.5); }
    tr:hover { background: rgba(255,255,255,0.01); }
    .footer { text-align: center; padding: 20px; color: rgba(255,255,255,0.1); font-size: 12px; border-top: 1px solid rgba(255,255,255,0.02); margin-top: 30px; letter-spacing: 2px; }
    .clickable-link { color: #60efff; text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: #a78bfa; }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 6: TIMELINE WAVE
# ============================================================

def generate_style_6_timeline_wave(data: Dict) -> str:
    """Стиль 6: Timeline Wave — волновая визуализация годов"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #f8f9fa; padding: 30px; font-family: 'Segoe UI', sans-serif; color: #1a1a2e; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; background: #fff; border-radius: 20px; padding: 30px; box-shadow: 0 4px 30px rgba(0,0,0,0.06); }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: #fff; border-right: 1px solid #eee;
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; color: #1a1a2e; }
    .sidebar a {
        color: #666; text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
    }
    .sidebar a:hover { background: #f0f2f5; color: #1a1a2e; transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 0 20px; }
    .header {
        background: #fff; border-radius: 16px; padding: 40px; margin-bottom: 30px; text-align: center;
        border: 1px solid #f0f2f5;
    }
    .header h1 { font-size: 32px; font-weight: 700; color: #1a1a2e; }
    .header .date { color: #999; margin-top: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: #f8f9fa; border-radius: 14px; padding: 20px; text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-number { font-size: 36px; font-weight: bold; color: #667eea; }
    .metric-percent { font-size: 12px; color: #155724; background: #d4edda; padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: #666; font-size: 14px; margin-top: 8px; }
    .section {
        background: #fff; border: 1px solid #f0f2f5; border-radius: 16px; padding: 25px; margin-bottom: 30px;
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea; color: #1a1a2e; }
    .rank-item {
        background: #f8f9fa; border-radius: 10px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid #667eea;
        transition: all 0.3s;
    }
    .rank-item:hover { background: #f0f2f5; transform: translateX(5px); }
    .rank-number { font-weight: bold; color: #667eea; font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: #1a1a2e; }
    .rank-count { float: right; color: #666; }
    .progress-bar-custom { background: #e9ecef; border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-success { background: #d4edda; color: #155724; }
    .badge-warning { background: #fff3cd; color: #856404; }
    .badge-danger { background: #f8d7da; color: #721c24; }
    .badge-info { background: #d1ecf1; color: #0c5460; }
    .badge-repository { background: #e2d5f8; color: #5e2a9e; }
    .badge-book { background: #d4f1e9; color: #0e6b5e; }
    .badge-proceedings { background: #fff2c9; color: #b26b00; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 10px; padding: 12px; text-align: center;
        border: 1px solid #667eea30;
    }
    .concept-name { font-weight: 600; color: #667eea; }
    .concept-score { font-size: 12px; color: #666; margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: #f5f5f5; padding: 8px; border-radius: 5px; margin-top: 5px;
    }
    
    .normal-article { background: #e8f5e9 !important; border-left: 3px solid #4caf50 !important; }
    .notfound-reference { background: #e9ecef !important; border-left: 3px solid #6c757d !important; }
    .suspicious-reference { background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }
    .duplicate-reference { background: #ffe5cc !important; border-left: 3px solid #fd7e14 !important; }
    .ebook-reference { background: #d4f1e9 !important; border-left: 3px solid #0e6b5e !important; }
    .repository-reference { background: #e2d5f8 !important; border-left: 3px solid #5e2a9e !important; }
    .proceedings-reference { background: #fff2c9 !important; border-left: 3px solid #b26b00 !important; }
    .retracted-reference { background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #e0e0e0; }
    th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    tr:hover { background: #f5f5f5; }
    .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; border-top: 1px solid #eee; margin-top: 30px; }
    .clickable-link { color: #667eea; text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: #764ba2; text-decoration: underline; }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 7: MASONRY
# ============================================================

def generate_style_7_masonry(data: Dict) -> str:
    """Стиль 7: Masonry — плиточная раскладка как Pinterest"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #f5f7fa; padding: 30px; font-family: 'Segoe UI', sans-serif; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: #fff; border-right: 1px solid #e8ecf1;
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; color: #1a1a2e; }
    .sidebar a {
        color: #666; text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
    }
    .sidebar a:hover { background: #f0f2f5; color: #1a1a2e; transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 30px 40px; }
    .header {
        background: #fff; border-radius: 20px; padding: 40px; margin-bottom: 30px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .header h1 { font-size: 32px; font-weight: 700; color: #1a1a2e; }
    .header .date { color: #999; margin-top: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: #fff; border-radius: 16px; padding: 20px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
    .metric-number { font-size: 36px; font-weight: bold; color: #667eea; }
    .metric-percent { font-size: 12px; color: #155724; background: #d4edda; padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: #666; font-size: 14px; margin-top: 8px; }
    .section {
        background: #fff; border-radius: 16px; padding: 25px; margin-bottom: 30px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea; color: #1a1a2e; }
    .rank-item {
        background: #f8f9fa; border-radius: 12px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid #667eea;
        transition: all 0.3s;
    }
    .rank-item:hover { transform: translateX(5px); box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .rank-number { font-weight: bold; color: #667eea; font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: #1a1a2e; }
    .rank-count { float: right; color: #666; }
    .progress-bar-custom { background: #e9ecef; border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-success { background: #d4edda; color: #155724; }
    .badge-warning { background: #fff3cd; color: #856404; }
    .badge-danger { background: #f8d7da; color: #721c24; }
    .badge-info { background: #d1ecf1; color: #0c5460; }
    .badge-repository { background: #e2d5f8; color: #5e2a9e; }
    .badge-book { background: #d4f1e9; color: #0e6b5e; }
    .badge-proceedings { background: #fff2c9; color: #b26b00; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 12px; padding: 12px; text-align: center;
        border: 1px solid #667eea30;
    }
    .concept-name { font-weight: 600; color: #667eea; }
    .concept-score { font-size: 12px; color: #666; margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: #f5f5f5; padding: 8px; border-radius: 5px; margin-top: 5px;
    }
    
    .normal-article { background: #e8f5e9 !important; border-left: 3px solid #4caf50 !important; }
    .notfound-reference { background: #e9ecef !important; border-left: 3px solid #6c757d !important; }
    .suspicious-reference { background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }
    .duplicate-reference { background: #ffe5cc !important; border-left: 3px solid #fd7e14 !important; }
    .ebook-reference { background: #d4f1e9 !important; border-left: 3px solid #0e6b5e !important; }
    .repository-reference { background: #e2d5f8 !important; border-left: 3px solid #5e2a9e !important; }
    .proceedings-reference { background: #fff2c9 !important; border-left: 3px solid #b26b00 !important; }
    .retracted-reference { background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #e0e0e0; }
    th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    tr:hover { background: #f5f5f5; }
    .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; border-top: 1px solid #eee; margin-top: 30px; }
    .clickable-link { color: #667eea; text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: #764ba2; text-decoration: underline; }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 8: HOLOGRAPHIC
# ============================================================

def generate_style_8_holographic(data: Dict) -> str:
    """Стиль 8: Holographic — голографический эффект с переливами"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { min-height: 100vh; background: linear-gradient(135deg, #0a0a1a, #1a0a2e, #0a1a2e); padding: 30px; font-family: 'Segoe UI', sans-serif; color: #fff; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        backdrop-filter: blur(10px); border-right: 1px solid rgba(255,255,255,0.03);
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #ff6b6b); background-size: 300% 100%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer_holo 3s linear infinite; }
    @keyframes shimmer_holo { 0% { background-position: 0% 50%; } 100% { background-position: 300% 50%; } }
    .sidebar a {
        color: rgba(255,255,255,0.3); text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
    }
    .sidebar a:hover { background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.8); transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 30px 40px; }
    .header {
        background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
        backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; margin-bottom: 30px; text-align: center;
        border: 1px solid rgba(255,255,255,0.03); position: relative; overflow: hidden;
    }
    .header::before {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(from 0deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #ff6b6b);
        animation: spin_holo 8s linear infinite; opacity: 0.05; pointer-events: none;
    }
    @keyframes spin_holo { 100% { transform: rotate(360deg); } }
    .header h1 { font-size: 32px; font-weight: 700; background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #ff6b6b); background-size: 300% 100%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer_holo 3s linear infinite; position: relative; z-index: 1; }
    .header .date { color: rgba(255,255,255,0.2); margin-top: 10px; position: relative; z-index: 1; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: rgba(255,255,255,0.02); backdrop-filter: blur(10px);
        border-radius: 16px; padding: 20px; text-align: center;
        border: 1px solid rgba(255,255,255,0.03); transition: all 0.3s;
    }
    .metric-card:hover { border-color: rgba(255,255,255,0.1); }
    .metric-number { font-size: 36px; font-weight: bold; background: linear-gradient(90deg, #ff6b6b, #ffd93d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-percent { font-size: 12px; color: rgba(255,255,255,0.3); background: rgba(255,255,255,0.02); padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: rgba(255,255,255,0.3); font-size: 14px; margin-top: 8px; }
    .section {
        background: rgba(255,255,255,0.02); backdrop-filter: blur(10px);
        border-radius: 16px; padding: 25px; margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.03); position: relative; overflow: hidden;
    }
    .section::before {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(from 0deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #ff6b6b);
        animation: spin_holo 10s linear infinite; opacity: 0.02; pointer-events: none;
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.04); color: rgba(255,255,255,0.6); position: relative; z-index: 1; }
    .rank-item {
        background: rgba(255,255,255,0.01); border-radius: 10px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid rgba(255,255,255,0.05); transition: all 0.3s; position: relative; z-index: 1;
    }
    .rank-item:hover { background: rgba(255,255,255,0.02); transform: translateX(5px); }
    .rank-number { font-weight: bold; color: #ffd93d; font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: rgba(255,255,255,0.6); }
    .rank-count { float: right; color: rgba(255,255,255,0.2); }
    .progress-bar-custom { background: rgba(255,255,255,0.02); border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.3); border: 1px solid rgba(255,255,255,0.03); }
    .badge-success { border-color: rgba(107,203,119,0.2); color: #6bcb77; }
    .badge-warning { border-color: rgba(255,217,61,0.2); color: #ffd93d; }
    .badge-danger { border-color: rgba(255,107,107,0.2); color: #ff6b6b; }
    .badge-info { border-color: rgba(77,150,255,0.2); color: #4d96ff; }
    .badge-repository { border-color: rgba(155,89,182,0.2); color: #9b59b6; }
    .badge-book { border-color: rgba(26,188,156,0.2); color: #1abc9c; }
    .badge-proceedings { border-color: rgba(255,217,61,0.2); color: #ffd93d; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: rgba(255,255,255,0.01); border-radius: 10px; padding: 12px; text-align: center;
        border: 1px solid rgba(255,255,255,0.03);
    }
    .concept-name { font-weight: 600; color: #ffd93d; }
    .concept-score { font-size: 12px; color: rgba(255,255,255,0.2); margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: rgba(0,0,0,0.2); padding: 8px; border-radius: 5px; margin-top: 5px;
        color: rgba(255,255,255,0.2);
    }
    
    .normal-article { border-left: 3px solid #6bcb77 !important; }
    .notfound-reference { border-left: 3px solid #666 !important; }
    .suspicious-reference { border-left: 3px solid #ff6b6b !important; }
    .duplicate-reference { border-left: 3px solid #ffd93d !important; }
    .ebook-reference { border-left: 3px solid #1abc9c !important; }
    .repository-reference { border-left: 3px solid #9b59b6 !important; }
    .proceedings-reference { border-left: 3px solid #ffd93d !important; }
    .retracted-reference { border-left: 3px solid #ff6b6b !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.02); color: rgba(255,255,255,0.3); }
    th { background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.5); }
    tr:hover { background: rgba(255,255,255,0.01); }
    .footer { text-align: center; padding: 20px; color: rgba(255,255,255,0.1); font-size: 12px; border-top: 1px solid rgba(255,255,255,0.02); margin-top: 30px; }
    .clickable-link { color: rgba(255,255,255,0.4); text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: #ffd93d; }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 9: GEO BUBBLES
# ============================================================

def generate_style_9_geo_bubbles(data: Dict) -> str:
    """Стиль 9: Geo Bubbles — географические пузырьки"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #f0f4f8; padding: 30px; font-family: 'Segoe UI', sans-serif; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; background: #fff; border-radius: 20px; padding: 30px; box-shadow: 0 4px 30px rgba(0,0,0,0.06); }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: #fff; border-right: 1px solid #e8ecf1;
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; color: #1a1a2e; }
    .sidebar a {
        color: #666; text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
    }
    .sidebar a:hover { background: #f0f2f5; color: #1a1a2e; transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 0 20px; }
    .header {
        background: #fff; border-radius: 16px; padding: 40px; margin-bottom: 30px; text-align: center;
        border: 1px solid #f0f2f5;
    }
    .header h1 { font-size: 32px; font-weight: 700; color: #1a1a2e; }
    .header .date { color: #999; margin-top: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: #f8f9fa; border-radius: 14px; padding: 20px; text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-number { font-size: 36px; font-weight: bold; color: #667eea; }
    .metric-percent { font-size: 12px; color: #155724; background: #d4edda; padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: #666; font-size: 14px; margin-top: 8px; }
    .section {
        background: #fff; border: 1px solid #f0f2f5; border-radius: 16px; padding: 25px; margin-bottom: 30px;
    }
    .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea; color: #1a1a2e; }
    .rank-item {
        background: #f8f9fa; border-radius: 10px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid #667eea;
        transition: all 0.3s;
    }
    .rank-item:hover { background: #f0f2f5; transform: translateX(5px); }
    .rank-number { font-weight: bold; color: #667eea; font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: #1a1a2e; }
    .rank-count { float: right; color: #666; }
    .progress-bar-custom { background: #e9ecef; border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-success { background: #d4edda; color: #155724; }
    .badge-warning { background: #fff3cd; color: #856404; }
    .badge-danger { background: #f8d7da; color: #721c24; }
    .badge-info { background: #d1ecf1; color: #0c5460; }
    .badge-repository { background: #e2d5f8; color: #5e2a9e; }
    .badge-book { background: #d4f1e9; color: #0e6b5e; }
    .badge-proceedings { background: #fff2c9; color: #b26b00; }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 10px; padding: 12px; text-align: center;
        border: 1px solid #667eea30;
    }
    .concept-name { font-weight: 600; color: #667eea; }
    .concept-score { font-size: 12px; color: #666; margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: #f5f5f5; padding: 8px; border-radius: 5px; margin-top: 5px;
    }
    
    .normal-article { background: #e8f5e9 !important; border-left: 3px solid #4caf50 !important; }
    .notfound-reference { background: #e9ecef !important; border-left: 3px solid #6c757d !important; }
    .suspicious-reference { background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }
    .duplicate-reference { background: #ffe5cc !important; border-left: 3px solid #fd7e14 !important; }
    .ebook-reference { background: #d4f1e9 !important; border-left: 3px solid #0e6b5e !important; }
    .repository-reference { background: #e2d5f8 !important; border-left: 3px solid #5e2a9e !important; }
    .proceedings-reference { background: #fff2c9 !important; border-left: 3px solid #b26b00 !important; }
    .retracted-reference { background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #e0e0e0; }
    th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    tr:hover { background: #f5f5f5; }
    .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; border-top: 1px solid #eee; margin-top: 30px; }
    .clickable-link { color: #667eea; text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: #764ba2; text-decoration: underline; }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# СТИЛЬ 10: PARTICLES (SPACE)
# ============================================================

def generate_style_10_particles(data: Dict) -> str:
    """Стиль 10: Particles — космическая тема с частицами"""
    
    custom_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { min-height: 100vh; background: radial-gradient(ellipse at center, #1a1a2e, #0a0a1a); padding: 30px; font-family: 'Segoe UI', sans-serif; color: #fff; }
    .report-wrapper { max-width: 1400px; margin: 0 auto; }
    .sidebar {
        position: fixed; left: 0; top: 0; width: 260px; height: 100vh;
        background: rgba(255,255,255,0.01); border-right: 1px solid rgba(255,255,255,0.02);
        padding: 30px 20px; overflow-y: auto; z-index: 1000;
    }
    .sidebar h3 { margin-bottom: 20px; font-size: 18px; font-weight: 600; color: rgba(255,255,255,0.3); letter-spacing: 4px; }
    .sidebar a {
        color: rgba(255,255,255,0.15); text-decoration: none; display: block; padding: 10px 15px;
        margin: 5px 0; border-radius: 8px; transition: all 0.3s; font-size: 14px;
        letter-spacing: 1px;
    }
    .sidebar a:hover { background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.6); transform: translateX(5px); }
    .main-content { margin-left: 260px; padding: 30px 40px; }
    .header {
        background: rgba(255,255,255,0.01); border-radius: 20px; padding: 40px; margin-bottom: 30px; text-align: center;
        border: 1px solid rgba(255,255,255,0.02);
        position: relative; overflow: hidden;
    }
    .header::after {
        content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 20% 50%, rgba(100,100,255,0.03), transparent 70%), radial-gradient(circle at 80% 50%, rgba(255,100,100,0.03), transparent 70%);
        pointer-events: none; border-radius: 20px;
    }
    .header h1 { font-size: 32px; font-weight: 300; letter-spacing: 8px; background: linear-gradient(90deg, #a78bfa, #60efff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; position: relative; z-index: 1; }
    .header .date { color: rgba(255,255,255,0.1); margin-top: 10px; letter-spacing: 3px; position: relative; z-index: 1; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .metric-card {
        background: rgba(255,255,255,0.01); border-radius: 16px; padding: 20px; text-align: center;
        border: 1px solid rgba(255,255,255,0.01); transition: all 0.3s;
    }
    .metric-card:hover { border-color: rgba(255,255,255,0.03); }
    .metric-number { font-size: 36px; font-weight: bold; background: linear-gradient(135deg, #a78bfa, #60efff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-percent { font-size: 12px; color: rgba(255,255,255,0.15); background: rgba(255,255,255,0.01); padding: 3px 10px; border-radius: 20px; margin-top: 8px; display: inline-block; }
    .metric-label { color: rgba(255,255,255,0.15); font-size: 14px; margin-top: 8px; letter-spacing: 2px; }
    .section {
        background: rgba(255,255,255,0.01); border-radius: 16px; padding: 25px; margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.01); position: relative; overflow: hidden;
    }
    .section::after {
        content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 20% 50%, rgba(100,100,255,0.02), transparent 70%), radial-gradient(circle at 80% 50%, rgba(255,100,100,0.02), transparent 70%);
        pointer-events: none; border-radius: 16px;
    }
    .section-title { font-size: 24px; font-weight: 300; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.02); color: rgba(255,255,255,0.3); letter-spacing: 4px; position: relative; z-index: 1; }
    .rank-item {
        background: rgba(255,255,255,0.005); border-radius: 10px; padding: 12px; margin-bottom: 8px;
        border-left: 1px solid rgba(255,255,255,0.02); transition: all 0.3s; position: relative; z-index: 1;
    }
    .rank-item:hover { background: rgba(255,255,255,0.01); transform: translateX(5px); }
    .rank-number { font-weight: bold; color: rgba(167,139,250,0.5); font-size: 18px; display: inline-block; width: 40px; }
    .rank-name { display: inline-block; width: 300px; font-weight: 500; color: rgba(255,255,255,0.3); letter-spacing: 1px; }
    .rank-count { float: right; color: rgba(255,255,255,0.1); }
    .progress-bar-custom { background: rgba(255,255,255,0.01); border-radius: 10px; height: 8px; margin-top: 8px; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, rgba(167,139,250,0.5), rgba(96,239,255,0.5)); height: 100%; border-radius: 10px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: rgba(255,255,255,0.01); color: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.01); letter-spacing: 1px; }
    .badge-success { border-color: rgba(46, 204, 113, 0.1); color: rgba(46, 204, 113, 0.4); }
    .badge-warning { border-color: rgba(241, 196, 15, 0.1); color: rgba(241, 196, 15, 0.4); }
    .badge-danger { border-color: rgba(231, 76, 60, 0.1); color: rgba(231, 76, 60, 0.4); }
    .badge-info { border-color: rgba(52, 152, 219, 0.1); color: rgba(52, 152, 219, 0.4); }
    .badge-repository { border-color: rgba(155, 89, 182, 0.1); color: rgba(155, 89, 182, 0.4); }
    .badge-book { border-color: rgba(26, 188, 156, 0.1); color: rgba(26, 188, 156, 0.4); }
    .badge-proceedings { border-color: rgba(241, 196, 15, 0.1); color: rgba(241, 196, 15, 0.4); }
    
    .concepts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
    .concept-card {
        background: rgba(255,255,255,0.005); border-radius: 10px; padding: 12px; text-align: center;
        border: 1px solid rgba(255,255,255,0.005);
    }
    .concept-name { font-weight: 600; color: rgba(167,139,250,0.5); }
    .concept-score { font-size: 12px; color: rgba(255,255,255,0.08); margin-top: 5px; }
    
    .full-text-container {
        max-height: 150px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;
        background: rgba(0,0,0,0.2); padding: 8px; border-radius: 5px; margin-top: 5px;
        color: rgba(255,255,255,0.1);
    }
    
    .normal-article { border-left: 1px solid rgba(46, 204, 113, 0.2) !important; }
    .notfound-reference { border-left: 1px solid rgba(255,255,255,0.02) !important; }
    .suspicious-reference { border-left: 1px solid rgba(231, 76, 60, 0.2) !important; }
    .duplicate-reference { border-left: 1px solid rgba(241, 196, 15, 0.2) !important; }
    .ebook-reference { border-left: 1px solid rgba(26, 188, 156, 0.2) !important; }
    .repository-reference { border-left: 1px solid rgba(155, 89, 182, 0.2) !important; }
    .proceedings-reference { border-left: 1px solid rgba(241, 196, 15, 0.2) !important; }
    .retracted-reference { border-left: 1px solid rgba(231, 76, 60, 0.2) !important; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.01); color: rgba(255,255,255,0.15); }
    th { background: rgba(255,255,255,0.005); color: rgba(255,255,255,0.3); letter-spacing: 2px; }
    tr:hover { background: rgba(255,255,255,0.005); }
    .footer { text-align: center; padding: 20px; color: rgba(255,255,255,0.03); font-size: 12px; border-top: 1px solid rgba(255,255,255,0.01); margin-top: 30px; letter-spacing: 4px; }
    .clickable-link { color: rgba(167,139,250,0.3); text-decoration: none; transition: all 0.3s; }
    .clickable-link:hover { color: rgba(96,239,255,0.5); }
    
    @media print { .sidebar { display: none; } .main-content { margin-left: 0; } }
    @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; padding: 20px; } }
    """
    
    return generate_full_report_html(data, custom_css)

# ============================================================
# РЕГИСТРАЦИЯ ВСЕХ СТИЛЕЙ
# ============================================================

STYLE_GENERATORS = {
    "0": {
        "name": "Classic (Original)",
        "generator": generate_style_0_classic
    },
    "1": {
        "name": "Glassmorphism (Glass)",
        "generator": generate_style_1_glassmorphism
    },
    "2": {
        "name": "Neon Cyber (Neon)",
        "generator": generate_style_2_neon_cyber
    },
    "3": {
        "name": "Glass Enhanced",
        "generator": generate_style_3_glass_enhanced
    },
    "4": {
        "name": "Smart Glow",
        "generator": generate_style_4_smart_glow
    },
    "5": {
        "name": "Aurora (Northern Lights)",
        "generator": generate_style_5_aurora
    },
    "6": {
        "name": "Timeline Wave",
        "generator": generate_style_6_timeline_wave
    },
    "7": {
        "name": "Masonry (Pinterest Style)",
        "generator": generate_style_7_masonry
    },
    "8": {
        "name": "Holographic",
        "generator": generate_style_8_holographic
    },
    "9": {
        "name": "Geo Bubbles",
        "generator": generate_style_9_geo_bubbles
    },
    "10": {
        "name": "Particles (Space)",
        "generator": generate_style_10_particles
    }
}

def get_style_names() -> Dict[str, str]:
    """Возвращает словарь с названиями стилей"""
    return {key: info["name"] for key, info in STYLE_GENERATORS.items()}

def generate_report(style_key: str, data: Dict) -> str:
    """Генерирует HTML отчет в выбранном стиле"""
    if style_key in STYLE_GENERATORS:
        return STYLE_GENERATORS[style_key]["generator"](data)
    return STYLE_GENERATORS["0"]["generator"](data)
