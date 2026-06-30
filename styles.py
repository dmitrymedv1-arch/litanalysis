"""
STYLES.PY - Все стили HTML отчетов для Comprehensive Reference List Analysis
Содержит классический стиль и 10 новых дизайнов
"""

import html
import re
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
import base64
import os

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ СТИЛЕЙ
# ============================================================

def get_date() -> str:
    """Возвращает текущую дату в формате DD.MM.YYYY"""
    return datetime.now().strftime('%d.%m.%Y')

def get_footer() -> str:
    """Возвращает подвал для отчетов"""
    return f'© Chimica Techno Acta / Created by daM / {get_date()}'

def make_clickable_doi(doi: str) -> str:
    """Создает HTML ссылку для DOI"""
    if doi:
        return f'<a href="https://doi.org/{doi}" target="_blank" class="clickable-link">{html.escape(doi)}</a>'
    return 'Not found'

def make_clickable_orcid(orcid: str) -> str:
    """Создает HTML ссылку для ORCID"""
    if orcid:
        return f'<a href="{orcid}" target="_blank" class="clickable-link">{html.escape(orcid)}</a>'
    return ''

def normalize_author_name(name: str) -> Tuple[str, str]:
    """
    Normalize author name to format {Lastname} {FirstInitial}.
    Returns (compare_name, display_name)
    """
    if not name or not isinstance(name, str):
        return "", ""
    
    name = name.strip()
    
    if ',' in name:
        last, first = name.split(',', 1)
        last = last.strip()
        first = first.strip()
        first_initial = ''
        if first:
            first_parts = first.split()
            for part in first_parts:
                if part and part[0].isalpha():
                    first_initial = part[0].upper()
                    break
        display_name = f"{last} {first_initial}." if first_initial else last
        compare_name = f"{last.lower()} {first_initial.lower()}."
        return compare_name, display_name
    
    parts = name.split()
    if len(parts) >= 2:
        last = parts[-1]
        first_initial = ''
        for part in parts[:-1]:
            if part and part[0].isalpha():
                first_initial = part[0].upper()
                break
        display_name = f"{last} {first_initial}." if first_initial else last
        compare_name = f"{last.lower()} {first_initial.lower()}."
        return compare_name, display_name
    
    if len(parts) == 1:
        display_name = parts[0]
        compare_name = parts[0].lower()
        return compare_name, display_name
    
    return name.lower(), name

def get_color_for_author(index: int) -> str:
    """Get a color for highlighting author based on index"""
    colors = [
        "#d9534f", "#5bc0de", "#5cb85c", "#f0ad4e", "#9b59b6",
        "#e67e22", "#1abc9c", "#e74c3c", "#3498db", "#2ecc71"
    ]
    return colors[index % len(colors)]

def format_authors_with_colors(authors_list, paper_norm_map):
    """Format authors with colors for self-citation highlighting"""
    if not authors_list:
        return ""
    formatted_authors = []
    for author in authors_list:
        norm_author, _ = normalize_author_name(author)
        if norm_author in paper_norm_map:
            escaped_author = html.escape(author)
            color = paper_norm_map[norm_author]['color']
            formatted_authors.append(
                f'<span style="color: {color}; font-weight: bold; background-color: {color}20; padding: 2px 4px; border-radius: 3px;">{escaped_author}</span>'
            )
        else:
            formatted_authors.append(html.escape(author))
    return ', '.join(formatted_authors)

# ============================================================
# КЛАССИЧЕСКИЙ СТИЛЬ (ОРИГИНАЛЬНЫЙ)
# ============================================================

def generate_classic_report(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#f39c12',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Generate enhanced HTML report with PNG icons and professional design"""
    
    # Localization
    def get_text_local(key: str) -> str:
        from app import TEXTS  # Import here to avoid circular import
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    # Load icons as base64
    icons = {}
    icon_files = [
        ("overview", "icon_overview.png"), ("identifier", "icon_identifier.png"),
        ("authors", "icon_authors.png"), ("journals", "icon_journals.png"),
        ("publishers", "icon_publishers.png"), ("yearly", "icon_yearly.png"),
        ("concepts", "icon_concepts.png"), ("geography", "icon_geography.png"),
        ("collaborations", "icon_collaborations.png"), ("diversity", "icon_diversity.png"),
        ("classics", "icon_classics.png"), ("selfcitation", "icon_selfcitation.png"),
        ("crossref", "icon_crossref.png"), ("openalex", "icon_openalex.png"),
        ("suspicious", "icon_suspicious.png"), ("nondoi", "icon_nondoi.png"),
        ("duplicates", "duplicates.png"), ("nonjournal", "icon_nonjournal.png"),
        ("url", "icon_url.png"), ("problems", "icon_problems.png"),
        ("list", "icon_list.png"), ("reviewers", "icon_reviewers.png"),
    ]
    
    for key, filename in icon_files:
        try:
            with open(f"icons/{filename}", "rb") as f:
                icons[key] = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        except FileNotFoundError:
            icons[key] = ""
    
    def make_section_title(icon_key, title_key):
        icon_src = icons.get(icon_key, "")
        title_text = get_text_local(title_key)
        if icon_src:
            return f'<div class="section-title"><img src="{icon_src}" class="section-icon" alt=""> {title_text}</div>'
        else:
            return f'<div class="section-title">{title_text}</div>'
    
    # Set default journal name if not provided
    if not journal_name or journal_name.strip() == '':
        journal_name_display = get_text_local('journal_name_label') + ": Chimica Techno Acta"
    else:
        journal_name_display = get_text_local('journal_name_label') + ": " + html.escape(journal_name)
    
    article_number_display = ""
    if article_number and article_number.strip():
        article_number_display = f'<div><strong>{get_text_local("article_number_label")}:</strong> {html.escape(article_number)}</div>'
    
    show_self_citations_section = paper_authors and len(paper_authors) > 0
    
    # Prepare self-citation authors highlighting with colors
    paper_authors_set = set()
    paper_authors_colors = {}
    normalized_paper_authors_map = {}
    
    if show_self_citations_section and paper_authors:
        for idx, author in enumerate(paper_authors):
            paper_authors_set.add(author)
            paper_authors_colors[author] = get_color_for_author(idx)
            norm, display = normalize_author_name(author)
            normalized_paper_authors_map[norm] = {'display': display, 'color': get_color_for_author(idx)}
    
    authors_header_html = ""
    if show_self_citations_section and paper_authors_set:
        authors_header_parts = []
        for author in paper_authors_set:
            escaped_author = html.escape(author)
            color = paper_authors_colors[author]
            authors_header_parts.append(f'<span style="color: {color}; font-weight: bold;">{escaped_author}</span>')
        authors_header_html = f'<div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;"><strong>{get_text_local("html_self_citation_authors_label")}:</strong> {", ".join(authors_header_parts)}</div>'
    
    # Generate self-citations section
    self_citations_html = ""
    if show_self_citations_section:
        if stats.get('self_citation_refs'):
            for ref in stats.get('self_citation_refs', []):
                authors_full_list = ref.get('authors_display', [])
                formatted_authors = format_authors_with_colors(authors_full_list, normalized_paper_authors_map)
                original_text_full = html.escape(ref.get('original_text', ''))
                doi_info = f'<div style="font-size: 13px; margin-top: 8px;"><strong>{get_text_local("doi_found")}:</strong> {make_clickable_doi(ref.get("doi"))}</div>' if ref.get('doi') else ''
                journal_info = f'<div style="font-size: 13px; margin-top: 5px;"><strong>{get_text_local("journal")}:</strong> {html.escape(ref.get("journal", get_text_local("not_found")))}</div>' if ref.get('journal') else ''
                year_info = f'<div style="font-size: 13px; margin-top: 5px;"><strong>{get_text_local("year")}:</strong> {ref.get("year", get_text_local("not_found"))}</div>' if ref.get('year') else ''
                
                special_class = ""
                if ref.get('is_retracted', False):
                    special_class = "retracted-reference"
                elif ref.get('is_ebook', False):
                    special_class = "ebook-reference"
                elif ref.get('is_repository', False):
                    special_class = "repository-reference"
                elif ref.get('is_proceedings', False):
                    special_class = "proceedings-reference"
                
                self_citations_html += f"""
                <div class="rank-item {special_class}" style="margin-bottom: 15px;">
                    <div><strong>{get_text_local("reference")}:</strong></div>
                    <div class="full-text-container">{original_text_full}</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>{get_text_local("authors")}:</strong> {formatted_authors}</div>
                    {doi_info}
                    {journal_info}
                    {year_info}
                </div>
                """
        else:
            self_citations_html = f'<p>{get_text_local("none_detected")}</p>'
    
    # Generate duplicates section
    duplicates_html = ""
    if duplicates and len(duplicates) > 0:
        duplicates_html = f"""
        <div id="duplicates" class="section">
            {make_section_title("duplicates", "duplicate_references_title")}
        """
        for dup in duplicates:
            ref_num_1 = dup['index1'] + 1
            ref_num_2 = dup['index2'] + 1
            doi = dup.get('doi', get_text_local('not_found'))
            duplicates_html += f"""
            <div class="rank-item duplicate-reference" style="margin-bottom: 10px;">
                <span class="badge badge-warning">{get_text_local("full_doi_match")}</span>
                <div style="margin-top: 8px;"><strong>{get_text_local("references")} {ref_num_1} {get_text_local("and")} {ref_num_2}</strong> — {get_text_local("doi_found")}: {make_clickable_doi(doi)}</div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">{get_text_local("reference")} {ref_num_1}: {html.escape(dup['ref1'])}...</div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">{get_text_local("reference")} {ref_num_2}: {html.escape(dup['ref2'])}...</div>
            </div>
            """
        duplicates_html += "</div>"
    
    # Generate Non-journal Sources with DOI section
    non_journal_sources_html = ""
    if stats.get('non_journal_sources_with_doi'):
        non_journal_sources_html = f"""
        <div id="nonjournal" class="section">
            {make_section_title("nonjournal", "html_non_journal_sources_with_doi")}
            <div style="margin-bottom: 15px; font-size: 13px; color: #666;">{get_text_local("non_journal_sources_with_doi_desc")}</div>
        """
        for source in stats.get('non_journal_sources_with_doi', []):
            badge_class = ""
            badge_text = ""
            if source.get('type') == 'repository':
                badge_class = "badge-repository"
                badge_text = get_text_local("repository")
            elif source.get('type') == 'ebook':
                badge_class = "badge-book"
                badge_text = get_text_local("ebook")
            elif source.get('type') == 'proceedings':
                badge_class = "badge-proceedings"
                badge_text = get_text_local("proceedings")
            else:
                badge_class = "badge-info"
                badge_text = source.get('type', get_text_local("reference"))
            
            non_journal_sources_html += f"""
            <div class="rank-item">
                <span class="{badge_class}">{badge_text}</span>
                <div style="margin-top: 8px;">{html.escape(source['text'])}</div>
                <div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(source.get('doi'))}</div>
            </div>
            """
        non_journal_sources_html += "</div>"
    
    # Generate Potential Reviewers section (if enabled)
    potential_reviewers_html = ""
    if show_reviewers and potential_reviewers:
        reviewers_content = ""
        for i, reviewer in enumerate(potential_reviewers, 1):
            reviewer_name = reviewer.get('display_name', 'Unknown')
            orcid = reviewer.get('orcid', '')
            latest_year = reviewer.get('latest_year', 'N/A')
            citation_count = reviewer.get('citation_count', 0)
            affiliations = reviewer.get('affiliations', [])
            countries = reviewer.get('countries', [])
            orcid_profile = reviewer.get('orcid_profile', {})
            
            orcid_link = f'<div class="reviewer-orcid">🔗 <a href="{orcid}" target="_blank" class="clickable-link">ORCID: {orcid.replace("https://orcid.org/", "")}</a></div>' if orcid else ''
            
            countries_str = ', '.join(countries[:3]) if countries else ''
            
            aff_str = ', '.join(affiliations[:3])
            if len(affiliations) > 3:
                aff_str += f' +{len(affiliations)-3} more'
            
            profile_html = ""
            if orcid_profile:
                if orcid_profile.get('country'):
                    profile_html += f'<div><strong>{get_text_local("orcid_country")}:</strong> {orcid_profile["country"]}</div>'
                if orcid_profile.get('keywords'):
                    keywords_str = ', '.join(orcid_profile['keywords'][:5])
                    profile_html += f'<div><strong>{get_text_local("orcid_keywords")}:</strong> {keywords_str}</div>'
                if orcid_profile.get('external_ids'):
                    profile_html += f'<div class="reviewer-section"><div class="reviewer-section-title">{get_text_local("orcid_other_ids")}:</div>'
                    for id_type, id_info in orcid_profile['external_ids'].items():
                        id_url = id_info['url']
                        friendly_name = id_type.replace('-', ' ').title()
                        if id_url:
                            profile_html += f'<a href="{id_url}" target="_blank" class="external-id-link">{friendly_name}</a>'
                        else:
                            profile_html += f'<span class="external-id-link">{friendly_name}</span>'
                    profile_html += '</div>'
                if orcid_profile.get('researcher_urls'):
                    profile_html += f'<div class="reviewer-section"><div class="reviewer-section-title">{get_text_local("orcid_websites")}:</div>'
                    for url_info in orcid_profile['researcher_urls']:
                        url_name = url_info.get('name', 'Website')
                        url_value = url_info.get('url', '')
                        if url_value:
                            profile_html += f'<a href="{url_value}" target="_blank" class="reviewer-website">{url_name}</a>'
                    profile_html += '</div>'
            
            reviewers_content += f"""
            <div class="reviewer-card">
                <div class="reviewer-name">{i}. {reviewer_name}</div>
                {orcid_link}
                <div style="display: flex; gap: 20px; margin: 10px 0;">
                    <div><strong>{get_text_local("reviewer_article_year")}:</strong> {latest_year}</div>
                    <div><strong>{get_text_local("reviewer_citations")}:</strong> {citation_count}</div>
                    {f'<div><strong>{get_text_local("orcid_country")}:</strong> {countries_str}</div>' if countries_str else ''}
                </div>
                {profile_html}
                <div><strong>{get_text_local("affiliation")}:</strong> {aff_str}</div>
            </div>
            """
        
        potential_reviewers_html = f"""
        <div id="reviewers" class="section">
            {make_section_title("reviewers", "potential_reviewers")}
            {reviewers_content}
        </div>
        """
    
    # Generate full reference list with color coding for different types
    full_references_html = ""
    duplicate_indices = set()
    if duplicates:
        for dup in duplicates:
            duplicate_indices.add(dup['index1'])
            duplicate_indices.add(dup['index2'])
    
    results = stats.get('_results', [])  # Need to pass results separately
    # For now, we'll generate a placeholder
    # In the actual implementation, results are passed separately
    full_references_html = "<p>Full reference list will be generated from actual data.</p>"
    
    # Build sidebar navigation with PNG icons
    sidebar_items = [
        ("overview", "html_overview", icons["overview"]),
        ("identifiers", "html_identifier_coverage", icons["identifier"]),
        ("authors", "html_authors", icons["authors"]),
        ("journals", "html_journals", icons["journals"]),
        ("publishers", "html_publishers", icons["publishers"]),
        ("yearly", "html_yearly", icons["yearly"]),
        ("concepts", "html_concepts", icons["concepts"]),
        ("geography", "html_geography", icons["geography"]),
        ("collaboration", "html_collaborations", icons["collaborations"]),
        ("diversity", "html_diversity", icons["diversity"]),
        ("classics", "html_classics", icons["classics"]),
    ]
    
    if show_self_citations_section:
        sidebar_items.append(("selfcitations", "html_self_citations", icons["selfcitation"]))
    
    if duplicates and len(duplicates) > 0:
        sidebar_items.append(("duplicates", "duplicate_references_title", icons.get("duplicates", icons["list"])))
    
    if show_reviewers and potential_reviewers:
        sidebar_items.append(("reviewers", "potential_reviewers", icons.get("reviewers", icons["list"])))
    
    sidebar_items.extend([
        ("crossref_only", "html_crossref_only", icons["crossref"]),
        ("openalex_only", "html_openalex_only", icons["openalex"]),
        ("suspicious_doi", "html_suspicious_doi", icons["suspicious"]),
        ("non_doi", "html_non_doi", icons["nondoi"]),
        ("nonjournal", "html_non_journal_sources_with_doi", icons.get("nonjournal", "")),
        ("url_sources", "html_url_sources", icons["url"]),
        ("problems", "html_problems", icons["problems"]),
        ("full_reference_list", "full_reference_list_title", icons["list"]),
    ])
    
    sidebar_html = '<div class="sidebar">\n'
    sidebar_html += f'<h3>{get_text_local("navigation")}</h3>\n'
    for item_id, title_key, icon_src in sidebar_items:
        title_text = get_text_local(title_key)
        if icon_src:
            sidebar_html += f'''
            <a href="#{item_id}">
                <img src="{icon_src}" class="sidebar-icon" alt="{title_text}">
                <span>{title_text}</span>
            </a>
            '''
        else:
            sidebar_html += f'''
            <a href="#{item_id}">
                <span>{title_text}</span>
            </a>
            '''
    sidebar_html += '</div>\n'
    
    # Confidential banner for reviewers mode
    confidential_banner = ""
    if show_reviewers:
        confidential_text = get_text_local('confidential_banner')
        confidential_banner = f'''
        <div class="confidential-banner">
            ⚠️ {confidential_text}
        </div>
        '''
    
    # Format metrics for overview section
    total_references = stats['total_references']
    total_with_doi = stats['total_with_doi']
    total_with_doi_percent = stats.get('total_with_doi_percent', 0)
    last_5_years = stats['yearly_stats']['last_5_years']
    last_5_years_percent = stats['yearly_stats']['last_5_years_percent']
    self_citations_count = stats['self_citations_count']
    self_citations_percent = stats['self_citations_percent']
    total_citations_sum = stats.get('total_citations_sum', 0)
    avg_citations = stats.get('avg_citations', 0)
    
    # Get identifier coverage stats
    identifier_stats = stats['identifier_coverage']['stats']
    identifier_percents = stats['identifier_coverage_percents']
    
    # Format citation classics
    citation_classics_html = ""
    if stats['citation_classics']:
        for i, classic in enumerate(stats['citation_classics']):
            citation_classics_html += f"""
            <div class="rank-item">
                <span class="rank-number">{i+1}.</span>
                <span class="rank-name">{html.escape(classic["title"] if classic["title"] else get_text_local("not_found"))}</span>
                <span class="rank-count">{get_text_local("html_citations_count")}: {classic["citations"]}</span>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">{html.escape(classic["journal"] if classic["journal"] else get_text_local("not_found"))} ({classic["year"] if classic["year"] else get_text_local("not_found")})</div>
                {f'<div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(classic["doi"])}</div>' if classic.get("doi") else ''}
            </div>
            """
    else:
        citation_classics_html = f'<p>{get_text_local("no_citation_classics")}</p>'
    
    current_date = get_date()
    
    # Load logo
    logo_base64 = ""
    try:
        with open("logo.png", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        pass

    # Build HTML content (truncated for brevity - full version in original code)
    html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{get_text_local('app_title')}</title>
    <style>
        /* CSS styles - full version from original code */
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
            width: 260px;
            height: 100vh;
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
            padding: 30px 20px;
            overflow-y: auto;
            z-index: 1000;
        }}
        .sidebar h3 {{
            margin-bottom: 20px;
            font-size: 18px;
            font-weight: 600;
        }}
        .sidebar a {{
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 8px;
            transition: all 0.3s;
        }}
        .sidebar a:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }}
        .sidebar-icon {{
            width: 22px;
            height: 22px;
            background: transparent;
            display: inline-block;
            vertical-align: middle;
        }}
        .main-content {{
            margin-left: 260px;
            padding: 30px 40px;
        }}
        .header {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
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
            margin-top: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
            font-size: 32px;
            font-weight: bold;
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stat-label {{
            color: #666;
            margin-top: 10px;
            font-size: 14px;
        }}
        .stat-percent {{
            font-size: 12px;
            color: #155724;
            background-color: #d4edda;
            padding: 3px 10px;
            border-radius: 20px;
            margin-top: 8px;
            display: inline-block;
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
            border-bottom: 3px solid {primary_color};
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .section-icon {{
            width: 28px;
            height: 28px;
            vertical-align: middle;
            display: inline-block;
            background: transparent;
        }}
        .rank-item {{
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
            transition: all 0.3s;
        }}
        .rank-number {{
            font-weight: bold;
            color: {primary_color};
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
            background: linear-gradient(90deg, {primary_color}, {secondary_color});
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
            background: linear-gradient(135deg, {primary_color}15 0%, {secondary_color}15 100%);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid {primary_color}30;
        }}
        .concept-name {{
            font-weight: 600;
            color: {primary_color};
        }}
        .concept-score {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
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
        .badge-repository {{ background: #e2d5f8; color: #5e2a9e; }}
        .badge-book {{ background: #bbecde; color: #0e6b5e; }}
        .badge-proceedings {{ background: #fff2c9; color: #b26b00; }}
        
        /* Color coding for different reference types */
        .normal-article {{ background: #e8f5e9 !important; border-left: 3px solid #4caf50 !important; }}
        .notfound-reference {{ background: #e9ecef !important; border-left: 3px solid #6c757d !important; }}
        .suspicious-reference {{ background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }}
        .duplicate-reference {{ background: #ffe5cc !important; border-left: 3px solid #fd7e14 !important; }}
        .ebook-reference {{ background: #d4f1e9 !important; border-left: 3px solid #0e6b5e !important; }}
        .repository-reference {{ background: #e2d5f8 !important; border-left: 3px solid #5e2a9e !important; }}
        .preprint-reference {{ background: #e2d5f8 !important; border-left: 3px solid #5e2a9e !important; }}
        .proceedings-reference {{ background: #fff2c9 !important; border-left: 3px solid #b26b00 !important; }}
        .retracted-reference {{ background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }}
        
        .reviewer-card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid {primary_color};
        }}
        .reviewer-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .reviewer-name {{
            font-size: 18px;
            font-weight: 600;
            color: {primary_color};
            margin-bottom: 8px;
        }}
        .reviewer-orcid {{
            font-family: monospace;
            font-size: 12px;
            margin-bottom: 8px;
        }}
        .reviewer-section {{
            margin-top: 12px;
            padding-top: 8px;
            border-top: 1px solid #e0e0e0;
        }}
        .reviewer-section-title {{
            font-weight: 600;
            font-size: 13px;
            margin-bottom: 8px;
            color: #555;
        }}
        .external-id-link {{
            display: inline-block;
            background: #f0f0f0;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 11px;
            margin: 3px;
            text-decoration: none;
            color: #333;
            transition: background 0.2s;
        }}
        .external-id-link:hover {{
            background: {primary_color};
            color: white;
        }}
        .reviewer-website {{
            display: inline-block;
            margin: 3px 6px 3px 0;
            font-size: 12px;
        }}
        .confidential-banner {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffe69e 100%);
            border-left: 4px solid #dc3545;
            padding: 12px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            font-weight: 500;
            text-align: center;
        }}
        
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
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .clickable-link {{
            color: {primary_color};
            text-decoration: none;
            transition: all 0.3s;
        }}
        .clickable-link:hover {{
            color: {secondary_color};
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
    {sidebar_html}
    
    <div class="main-content">
        <div class="header">
            <div style="display: flex; justify-content: center; margin-bottom: 15px;">
                <img src="data:image/png;base64,{logo_base64}" style="height: 150px; width: auto;" alt="Logo">
            </div>
            <div style="margin-top: 10px;">{journal_name_display}</div>
            {article_number_display}
            <div class="date">{get_text_local('html_generated')}: {current_date}</div>
            <div style="margin-top: 15px;">
                <span class="badge badge-success">{get_text_local('status_both')}</span>
                <span class="badge badge-info">{get_text_local('total_references')}: {stats['total_references']}</span>
            </div>
        </div>
        
        {confidential_banner}
        
        <!-- OVERVIEW SECTION -->
        <div id="overview" class="section">
            {make_section_title("overview", "html_overview")}
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_references}</div>
                    <div class="stat-percent">(100.0%)</div>
                    <div class="stat-label">{get_text_local('total_references')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_with_doi}</div>
                    <div class="stat-percent">({total_with_doi_percent:.1f}%)</div>
                    <div class="stat-label">{get_text_local('doi_found')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{last_5_years}</div>
                    <div class="stat-percent">({last_5_years_percent:.1f}%)</div>
                    <div class="stat-label">{get_text_local('last_5_years_metric')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{self_citations_count}</div>
                    <div class="stat-percent">({self_citations_percent:.1f}%)</div>
                    <div class="stat-label">{get_text_local('self_citations')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_citations_sum}</div>
                    <div class="stat-label">{get_text_local('total_citations')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_citations:.1f}</div>
                    <div class="stat-label">{get_text_local('avg_citations')}</div>
                </div>
            </div>
        </div>
        
        <!-- IDENTIFIER COVERAGE SECTION -->
        <div id="identifiers" class="section">
            {make_section_title("identifier", "html_identifier_coverage")}
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['has_doi']}</div>
                    <div class="stat-percent">({identifier_percents['has_doi']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('doi_found')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['has_url']}</div>
                    <div class="stat-percent">({identifier_percents['has_url']:.1f}%)</div>
                    <div class="stat-label">URL</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['is_preprint_repository']}</div>
                    <div class="stat-percent">({identifier_percents['preprint_repository']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('preprint_repository_count')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['has_pmid']}</div>
                    <div class="stat-percent">({identifier_percents['has_pmid']:.1f}%)</div>
                    <div class="stat-label">PMID</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['is_ebook_platform']}</div>
                    <div class="stat-percent">({identifier_percents['ebook_platform']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('ebook')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['is_book_no_doi']}</div>
                    <div class="stat-percent">({identifier_percents['book_no_doi']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('books_count')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['is_proceedings']}</div>
                    <div class="stat-percent">({identifier_percents['proceedings']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('proceedings_count')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['is_retracted']}</div>
                    <div class="stat-percent">({identifier_percents['retracted']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('retracted_count')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['has_none']}</div>
                    <div class="stat-percent">({identifier_percents['has_none']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('no_identifier')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{identifier_stats['multiple']}</div>
                    <div class="stat-percent">({identifier_percents['multiple']:.1f}%)</div>
                    <div class="stat-label">Multiple identifiers</div>
                </div>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['both']}</div>
                    <div class="stat-percent">({stats['doi_status_percents']['both']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('status_both')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['crossref_only']}</div>
                    <div class="stat-percent">({stats['doi_status_percents']['crossref_only']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('status_crossref_only')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['openalex_only']}</div>
                    <div class="stat-percent">({stats['doi_status_percents']['openalex_only']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('status_openalex_only')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['doi_status']['none']}</div>
                    <div class="stat-percent">({stats['doi_status_percents']['none']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('status_none')}</div>
                </div>
            </div>
        </div>
        
        <!-- AUTHORS SECTION -->
        <div id="authors" class="section">
            {make_section_title("authors", "html_authors")}
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{html.escape(author["display_name"])}</span><span class="rank-count">{author["mention_count"]} {get_text_local("html_citations_label")}</span>' + (f'<div style="font-size: 11px; color: #667eea;">{get_text_local("orcid_label")}: {make_clickable_orcid(author["orcid"])}</div>' if author.get("orcid") else '') + (f'<div style="font-size: 11px; color: #666;"><strong>{get_text_local("institution_label")}:</strong> {html.escape(author["primary_institution"][:50])}</div>' if author.get("primary_institution") else '') + (f'<div style="font-size: 11px; color: #666;"><strong>{get_text_local("country_label")}:</strong> {", ".join(author["countries"])}</div>' if author.get("countries") else '') + (f'<div style="font-size: 11px; color: #666;"><strong>{get_text_local("all_affiliations")}:</strong><br>' + '<br>'.join([html.escape(aff["name"][:80]) for aff in author.get("affiliations", [])[:3]]) + '</div>' if author.get("affiliations") else '') + '<div class="progress-bar"><div class="progress-fill" style="width: ' + str(min(100, author["mention_count"] / stats["author_frequency_all"]["all_authors"][0]["mention_count"] * 100 if stats["author_frequency_all"]["all_authors"] else 0)) + '%;"></div></div></div>' for i, author in enumerate(stats["author_frequency_all"]["all_authors"][:30])])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text_local('unique_authors')}: {stats['author_frequency_all']['unique_authors']}</span>
                <span class="badge badge-info">{get_text_local('shannon_authors')}: {stats['shannon_index']['authors']}</span>
                <span class="badge badge-info">{get_text_local('orcid_coverage')}: {stats['orcid_coverage']['with_orcid']} ({stats['orcid_coverage']['coverage_percent']:.1f}%)</span>
            </div>
        </div>
        
        <!-- JOURNALS SECTION -->
        <div id="journals" class="section">
            {make_section_title("journals", "html_journals")}
            <table>
                <thead>
                    <tr><th>{get_text_local('html_rank')}</th><th>{get_text_local('journal')}</th><th>{get_text_local('html_count')}</th><th>{get_text_local('html_percentage')}</th></tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{i+1}</td><td>{html.escape(journal["journal"])}</td><td>{journal["count"]}</td><td>{journal["percentage"]:.1f}%</td></tr>' for i, journal in enumerate(stats["journal_frequency_all"]["all_journals"])])}
                </tbody>
            </table>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text_local('unique_journals')}: {stats['journal_frequency_all']['unique_journals']}</span>
                <span class="badge badge-info">{get_text_local('shannon_journals')}: {stats['shannon_index']['journals']}</span>
            </div>
        </div>
        
        <!-- PUBLISHERS SECTION -->
        <div id="publishers" class="section">
            {make_section_title("publishers", "html_publishers")}
            <table>
                <thead>
                    <tr><th>{get_text_local('html_rank')}</th><th>{get_text_local('publisher')}</th><th>{get_text_local('html_count')}</th><th>{get_text_local('html_percentage')}</th></tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{i+1}</td><td>{html.escape(publisher["publisher"])}</td><td>{publisher["count"]}</td><td>{publisher["percentage"]:.1f}%</td></tr>' for i, publisher in enumerate(stats["publisher_frequency"]["all_publishers"])])}
                </tbody>
            </table>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text_local('unique_publishers_metric')}: {stats['publisher_frequency']['unique_publishers']}</span>
                <span class="badge badge-info">{get_text_local('shannon_publishers')}: {stats['shannon_index']['publishers']}</span>
            </div>
        </div>
        
        <!-- YEARLY STATISTICS -->
        <div id="yearly" class="section">
            {make_section_title("yearly", "html_yearly")}
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['last_year']}</div>
                    <div class="stat-percent">({stats['yearly_stats']['last_year_percent']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('last_year')} ({stats['yearly_stats']['last_completed_year']})</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['last_3_years']}</div>
                    <div class="stat-percent">({stats['yearly_stats']['last_3_years_percent']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('last_3_years')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['last_5_years']}</div>
                    <div class="stat-percent">({stats['yearly_stats']['last_5_years_percent']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('last_5_years_metric')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['last_10_years']}</div>
                    <div class="stat-percent">({stats['yearly_stats']['last_10_years_percent']:.1f}%)</div>
                    <div class="stat-label">{get_text_local('last_10_years')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['yearly_stats']['unknown_year']}</div>
                    <div class="stat-label">{get_text_local('references_with_unknown_year')}</div>
                </div>
            </div>
            <div>
                <h4>{get_text_local('distribution_by_year')}:</h4>
                {''.join([f'<div class="rank-item"><span class="rank-name">{year}</span><span class="rank-count">{stats["yearly_stats"]["yearly_counts"][year]} {get_text_local("references_count")} ({stats["yearly_stats"]["yearly_percentages"][year]:.1f}%)</span><div class="progress-bar"><div class="progress-fill" style="width: {stats["yearly_stats"]["yearly_percentages"][year]}%;"></div></div></div>' for year in sorted(stats["yearly_stats"]["yearly_counts"].keys(), reverse=True)])}
            </div>
            <div style="margin-top: 15px;">
                <h4>{get_text_local('cumulative_percentage')}:</h4>
                {''.join([f'<div class="rank-item"><span class="rank-name">{year}</span><span class="rank-count">{stats["yearly_stats"]["cumulative_percentages"][year]:.1f}% {get_text_local("cumulative")}</span><div class="progress-bar"><div class="progress-fill" style="width: {stats["yearly_stats"]["cumulative_percentages"][year]}%;"></div></div></div>' for year in sorted(stats["yearly_stats"]["yearly_counts"].keys(), reverse=True)])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text_local('median_age')}: {stats['temporal']['median_age']} {get_text_local('years')}</span>
                <span class="badge badge-info">{get_text_local('average_age')}: {stats['temporal']['average_age']:.1f} {get_text_local('years')}</span>
            </div>
        </div>
        
        <!-- CONCEPTS SECTION -->
        <div id="concepts" class="section">
            {make_section_title("concepts", "html_concepts")}
            <div class="concepts-grid">
                {''.join([f'<div class="concept-card"><div class="concept-name">{html.escape(concept[0])}</div><div class="concept-score">{get_text_local("html_frequency")}: {concept[1]}</div></div>' for concept in stats['concepts']['concepts'][:12]])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text_local('unique_concepts')}: {stats['concepts']['unique_concepts']}</span>
            </div>
        </div>
        
        <!-- GEOGRAPHY SECTION -->
        <div id="geography" class="section">
            {make_section_title("geography", "html_geography")}
            <h4>{get_text_local('geography_type_1')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_1_desc')}</p>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-name">{html.escape(country)}</span><span class="rank-count">{count} {get_text_local("references_count")}</span><div class="progress-bar"><div class="progress-fill" style="width: {count / max(stats["geography"]["type1_unique_countries_per_reference"].values()) * 100 if stats["geography"]["type1_unique_countries_per_reference"] else 0}%;"></div></div></div>' for country, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:15]])}
            </div>
            <h4 style="margin-top: 25px;">{get_text_local('geography_type_2')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_2_desc')}</p>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-name">{html.escape(country)}</span><span class="rank-count">{count} {get_text_local("html_authors_count")}</span><div class="progress-bar"><div class="progress-fill" style="width: {count / max(stats["geography"]["type2_authors_per_country"].values()) * 100 if stats["geography"]["type2_authors_per_country"] else 0}%;"></div></div></div>' for country, count in list(stats['geography']['type2_authors_per_country'].items())[:15]])}
            </div>
            <h4 style="margin-top: 25px;">{get_text_local('geography_type_3')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_3_desc')}</p>
            <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
                <div class="stat-card">
                    <div class="stat-number">{stats['geography']['single_country_count']}</div>
                    <div class="stat-label">{get_text_local('single_country')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['geography']['international_count']}</div>
                    <div class="stat-label">{get_text_local('international_collab')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['geography']['total_references_with_country']}</div>
                    <div class="stat-label">{get_text_local('total_references')}</div>
                </div>
            </div>
            <h5 style="margin-top: 20px;">{get_text_local('collaboration_matrix')}:</h5>
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-name">{collab["country1"]} + {collab["country2"]}</span><span class="rank-count">{collab["count"]} {get_text_local("references_count")}</span><div class="progress-bar"><div class="progress-fill" style="width: {collab["count"] / max([c["count"] for c in stats["geography"]["collaboration_matrix"]]) * 100 if stats["geography"]["collaboration_matrix"] else 0}%;"></div></div></div>' for collab in stats['geography']['collaboration_matrix'][:15]])}
            </div>
        </div>
        
        <!-- COLLABORATION SECTION -->
        <div id="collaboration" class="section">
            {make_section_title("collaborations", "html_collaborations")}
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{html.escape(collab["author1"])} + {html.escape(collab["author2"])}</span><span class="rank-count">{collab["count"]} {get_text_local("html_joint_works")}</span></div>' for i, collab in enumerate(stats["collaboration"]["top_collaborations"][:8])])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text_local('core_authors_label')}: {', '.join([f"{html.escape(author[0])} ({author[1]} {get_text_local('html_connections')})" for author in stats['collaboration']['core_authors'][:5]])}</span>
            </div>
        </div>
        
        <!-- DIVERSITY SECTION -->
        <div id="diversity" class="section">
            {make_section_title("diversity", "html_diversity")}
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['shannon_index']['authors']}</div>
                    <div class="stat-label">{get_text_local('shannon_authors')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['shannon_index']['journals']}</div>
                    <div class="stat-label">{get_text_local('shannon_journals')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['shannon_index']['publishers']}</div>
                    <div class="stat-label">{get_text_local('shannon_publishers')}</div>
                </div>
            </div>
        </div>
        
        <!-- CITATION CLASSICS SECTION -->
        <div id="classics" class="section">
            {make_section_title("classics", "html_classics")}
            {citation_classics_html}
        </div>
        
        <!-- SELF-CITATIONS SECTION -->
        {f'''
        <div id="selfcitations" class="section">
            {make_section_title("selfcitation", "html_self_citations")}
            {authors_header_html}
            {self_citations_html}
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text_local('html_total_self_citations')}: {self_citations_count} ({self_citations_percent:.1f}%)</span>
            </div>
        </div>
        ''' if show_self_citations_section else ''}
        
        <!-- DUPLICATES SECTION -->
        {duplicates_html}
        
        <!-- POTENTIAL REVIEWERS SECTION -->
        {potential_reviewers_html}
        
        <!-- ONLY CROSSREF SECTION -->
        <div id="crossref_only" class="section">
            {make_section_title("crossref", "html_crossref_only")}
            {''.join([f'<div class="rank-item"><div>{html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('crossref_only_refs', [])[:20]]) if stats.get('crossref_only_refs') else f'<p>{get_text_local("no_crossref_only")}</p>'}
        </div>
        
        <!-- ONLY OPENALEX SECTION -->
        <div id="openalex_only" class="section">
            {make_section_title("openalex", "html_openalex_only")}
            {''.join([f'<div class="rank-item"><div>{html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('openalex_only_refs', [])[:20]]) if stats.get('openalex_only_refs') else f'<p>{get_text_local("no_openalex_only")}</p>'}
        </div>
        
        <!-- SUSPICIOUS DOIS SECTION -->
        <div id="suspicious_doi" class="section">
            {make_section_title("suspicious", "html_suspicious_doi")}
            <div style="margin-bottom: 15px; font-size: 13px; color: #666;">{get_text_local('suspicious_dois_hint')}</div>
            
            {f'''
            <div style="margin-top: 10px; margin-bottom: 15px;">
                <h4>{get_text_local("repository")} {get_text_local("references")}:</h4>
                <div style="font-size: 12px; color: #5e2a9e; margin-bottom: 10px;">{get_text_local("html_repository_note")}</div>
                {''.join([f'<div class="rank-item repository-reference"><span class="badge-repository">{get_text_local("repository")}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div>' + (f'<div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div>' if ref.get("doi") else '') + '</div>' for ref in stats.get('repository_refs', [])[:20]])}
            </div>
            ''' if stats.get('repository_refs') else ''}
            
            {f'''
            <div style="margin-top: 10px; margin-bottom: 15px;">
                <h4>{get_text_local("proceedings")} {get_text_local("references")}:</h4>
                <div style="font-size: 12px; color: #b26b00; margin-bottom: 10px;">{get_text_local("html_proceedings_note")}</div>
                {''.join([f'<div class="rank-item proceedings-reference"><span class="badge-proceedings">{get_text_local("proceedings")}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div>' + (f'<div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div>' if ref.get("doi") else '') + '</div>' for ref in stats.get('proceedings_refs', [])[:20]])}
            </div>
            ''' if stats.get('proceedings_refs') else ''}
            
            <div style="margin-top: 10px;">
                <h4>{get_text_local("suspicious_dois")}:</h4>
                {''.join([f'<div class="rank-item suspicious-reference"><div class="badge badge-danger">{get_text_local("html_attention")}</div><div>{html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('suspicious_doi_refs', [])[:20]]) if stats.get('suspicious_doi_refs') else f'<p>{get_text_local("no_suspicious_dois")}</p>'}
            </div>
        </div>
        
        <!-- NON-DOI SOURCES SECTION -->
        <div id="non_doi" class="section">
            {make_section_title("nondoi", "html_non_doi")}
            
            {f'''
            <div style="margin-bottom: 15px;">
                <h4>{get_text_local("books_count")} (ISBN without DOI):</h4>
                {''.join([f'<div class="rank-item book-reference"><span class="badge-book">{get_text_local("ebook")}</span><div style="margin-top: 8px;">{html.escape(ref)}</div></div>' for ref in stats.get('books_with_isbn_no_doi', [])[:20]])}
            </div>
            ''' if stats.get('books_with_isbn_no_doi') else ''}
            
            <div>
                <h4>{get_text_local("other")} {get_text_local("non_doi_sources")}:</h4>
                {''.join([f'<div class="rank-item notfound-reference">{html.escape(ref)}</div>' for ref in stats['identifier_coverage']['references_without_doi'][:20]]) if stats['identifier_coverage']['references_without_doi'] else f'<p>{get_text_local("all_have_doi")}</p>'}
            </div>
        </div>
        
        <!-- NON-JOURNAL SOURCES WITH DOI SECTION -->
        {non_journal_sources_html}
        
        <!-- URL SOURCES SECTION -->
        <div id="url_sources" class="section">
            {make_section_title("url", "html_url_sources")}
            {''.join([f'<div class="rank-item">{html.escape(ref)}</div>' for ref in stats['identifier_coverage']['references_with_only_url'][:20]]) if stats['identifier_coverage']['references_with_only_url'] else f'<p>{get_text_local("no_url_only")}</p>'}
        </div>
        
        <!-- PROBLEMS SECTION -->
        <div id="problems" class="section">
            {make_section_title("problems", "html_problems")}
            
            {f'''
            <div style="margin-bottom: 20px;">
                <h4>{get_text_local("retracted_count")}:</h4>
                {''.join([f'<div class="rank-item retracted-reference"><span class="badge-danger" style="background: #f8d7da; color: #721c24;">{get_text_local("retracted")}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div>' + (f'<div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div>' if ref.get("doi") else '') + '</div>' for ref in stats.get('retracted_refs', [])[:20]]) if stats.get('retracted_refs') else f'<p>{get_text_local("none_detected")}</p>'}
            </div>
            ''' if stats.get('retracted_refs') else ''}
            
            <div>
                <h4>{get_text_local("other")} {get_text_local("problematic_refs")}:</h4>
                {''.join([f'<div class="rank-item"><span class="badge badge-warning">{html.escape(ref["problems"])}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div></div>' for ref in stats['problematic_refs'][:10]]) if stats['problematic_refs'] else f'<p>{get_text_local("no_problematic")}</p>'}
            </div>
        </div>
        
        <!-- FULL REFERENCE LIST SECTION -->
        <div id="full_reference_list" class="section">
            {make_section_title("list", "full_reference_list_title")}
            {full_references_html}
        </div>
        
        <div class="footer">
            {get_text_local('html_footer')}<br>
            {get_text_local('html_copyright')}
        </div>
    </div>
</body>
</html>"""
    
    return html_content

# ============================================================
# НОВЫЕ СТИЛИ (10 УНИКАЛЬНЫХ ДИЗАЙНОВ)
# ============================================================

def generate_style_glassmorphism(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 1: Glassmorphism — стеклянный эффект с размытием"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    
    authors_html = ''.join([f'<span class="tag-glass">{a["display_name"]} ({a["mention_count"]})</span>' for a in stats['author_frequency_all']['all_authors'][:8]])
    journals_html = ''.join([f'<span class="tag-glass">{j["journal"]} ({j["count"]})</span>' for j in stats['journal_frequency_all']['all_journals'][:6]])
    geo_html = ''.join([f'<span class="tag-glass">{c}: {count}</span>' for c, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:5]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Glassmorphism Report</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{min-height:100vh;background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);padding:30px;font-family:'Segoe UI',sans-serif;}}
.container{{max-width:1200px;margin:0 auto;}}
.glass{{background:rgba(255,255,255,0.15);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-radius:20px;padding:28px;margin-bottom:20px;border:1px solid rgba(255,255,255,0.2);box-shadow:0 8px 32px rgba(0,0,0,0.1);}}
h1{{color:#fff;font-size:32px;font-weight:300;letter-spacing:2px;}}
.subtitle{{color:rgba(255,255,255,0.7);font-size:14px;}}
.glass-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:15px;}}
.glass-stat{{background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:16px;padding:20px;text-align:center;border:1px solid rgba(255,255,255,0.1);}}
.stat-number{{font-size:28px;font-weight:700;color:#fff;}}
.stat-label{{font-size:11px;color:rgba(255,255,255,0.6);margin-top:5px;text-transform:uppercase;letter-spacing:1px;}}
.tag-glass{{display:inline-block;padding:6px 16px;background:rgba(255,255,255,0.12);border-radius:20px;margin:4px;color:#fff;font-size:13px;backdrop-filter:blur(5px);border:1px solid rgba(255,255,255,0.08);}}
.sidebar-glass{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);border-radius:16px;padding:15px;border:1px solid rgba(255,255,255,0.1);z-index:100;}}
.sidebar-glass a{{display:block;color:rgba(255,255,255,0.7);text-decoration:none;padding:8px 12px;font-size:12px;border-radius:8px;transition:all 0.3s;}}
.sidebar-glass a:hover{{background:rgba(255,255,255,0.15);color:#fff;}}
.footer{{text-align:center;color:rgba(255,255,255,0.4);font-size:11px;padding:20px;}}
</style>
</head>
<body>
<div class="sidebar-glass">
    <a href="#overview">Overview</a>
    <a href="#authors">Authors</a>
    <a href="#journals">Journals</a>
    <a href="#geo">Geography</a>
</div>
<div class="container" style="margin-left:100px;">
    <div class="glass"><h1>✦ Glassmorphism Report</h1><div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div></div>
    <div class="glass">
        <div class="glass-grid">
            <div class="glass-stat"><div class="stat-number">{total}</div><div class="stat-label">Total</div></div>
            <div class="glass-stat"><div class="stat-number">{doi}</div><div class="stat-label">DOI</div></div>
            <div class="glass-stat"><div class="stat-number">{last5}</div><div class="stat-label">5 Years</div></div>
            <div class="glass-stat"><div class="stat-number">{self_cit}</div><div class="stat-label">Self-Cit</div></div>
            <div class="glass-stat"><div class="stat-number">{citations}</div><div class="stat-label">Citations</div></div>
        </div>
    </div>
    <div id="authors" class="glass"><div style="color:#fff;font-weight:600;margin-bottom:12px;">👨‍🎓 Authors</div>{authors_html}</div>
    <div id="journals" class="glass"><div style="color:#fff;font-weight:600;margin-bottom:12px;">📖 Journals</div>{journals_html}</div>
    <div id="geo" class="glass"><div style="color:#fff;font-weight:600;margin-bottom:12px;">🌍 Geography</div>{geo_html}</div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_neon_cyber(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 2: Neon Cyber — неоновое свечение на темном фоне"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    
    authors_html = ''.join([f'<span class="neon-tag">{a["display_name"]} [{a["mention_count"]}]</span>' for a in stats['author_frequency_all']['all_authors'][:8]])
    journals_html = ''.join([f'<span class="neon-tag neon-tag-cyan">{j["journal"]} {j["count"]}</span>' for j in stats['journal_frequency_all']['all_journals'][:6]])
    geo_html = ''.join([f'<span class="neon-tag">{c}:{count}</span>' for c, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:5]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Neon Cyber</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0a0a0f;padding:30px;font-family:'Courier New',monospace;color:#fff;}}
.container{{max-width:1200px;margin:0 auto;}}
.neon-box{{background:rgba(255,255,255,0.03);border:1px solid rgba(0,255,255,0.2);border-radius:12px;padding:25px;margin-bottom:20px;position:relative;box-shadow:0 0 30px rgba(0,255,255,0.05);}}
.neon-box::before{{content:'';position:absolute;top:-1px;left:50%;transform:translateX(-50%);width:60%;height:2px;background:linear-gradient(90deg,transparent,#00ffff,transparent);}}
h1{{font-size:32px;color:#00ffff;text-shadow:0 0 30px rgba(0,255,255,0.3);letter-spacing:4px;}}
.subtitle{{color:rgba(255,255,255,0.4);font-size:13px;}}
.neon-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;}}
.neon-stat{{background:rgba(0,255,255,0.05);border:1px solid rgba(0,255,255,0.1);border-radius:10px;padding:15px;text-align:center;}}
.neon-number{{font-size:28px;font-weight:700;color:#00ffff;text-shadow:0 0 20px rgba(0,255,255,0.2);}}
.neon-label{{font-size:10px;color:rgba(0,255,255,0.5);text-transform:uppercase;letter-spacing:2px;margin-top:4px;}}
.neon-tag{{display:inline-block;padding:4px 14px;margin:3px;border:1px solid rgba(255,0,255,0.3);border-radius:4px;font-size:12px;color:#ff00ff;background:rgba(255,0,255,0.05);}}
.neon-tag-cyan{{border-color:rgba(0,255,255,0.3);color:#00ffff;}}
.sidebar-neon{{position:fixed;right:20px;top:50%;transform:translateY(-50%);background:rgba(0,0,0,0.8);border:1px solid rgba(0,255,255,0.2);border-radius:10px;padding:12px;z-index:100;}}
.sidebar-neon a{{display:block;color:rgba(255,255,255,0.5);text-decoration:none;padding:6px 10px;font-size:11px;transition:all 0.3s;}}
.sidebar-neon a:hover{{color:#00ffff;text-shadow:0 0 10px rgba(0,255,255,0.5);}}
.footer{{text-align:center;color:rgba(255,255,255,0.2);font-size:11px;padding:15px;}}
</style>
</head>
<body>
<div class="sidebar-neon">
    <a href="#overview">▶ OVERVIEW</a>
    <a href="#authors">▶ AUTHORS</a>
    <a href="#journals">▶ JOURNALS</a>
    <a href="#geo">▶ GEO</a>
</div>
<div class="container" style="margin-right:120px;">
    <div class="neon-box"><h1>◈ NEON CYBER</h1><div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div></div>
    <div id="overview" class="neon-box">
        <div class="neon-grid">
            <div class="neon-stat"><div class="neon-number">{total}</div><div class="neon-label">Total</div></div>
            <div class="neon-stat"><div class="neon-number">{doi}</div><div class="neon-label">DOI</div></div>
            <div class="neon-stat"><div class="neon-number">{last5}</div><div class="neon-label">5Y</div></div>
            <div class="neon-stat"><div class="neon-number">{self_cit}</div><div class="neon-label">SELF</div></div>
            <div class="neon-stat"><div class="neon-number">{citations}</div><div class="neon-label">CIT</div></div>
        </div>
    </div>
    <div id="authors" class="neon-box"><div style="color:#00ffff;margin-bottom:10px;">▶ AUTHORS</div>{authors_html}</div>
    <div id="journals" class="neon-box"><div style="color:#00ffff;margin-bottom:10px;">▶ JOURNALS</div>{journals_html}</div>
    <div id="geo" class="neon-box"><div style="color:#00ffff;margin-bottom:10px;">▶ GEOGRAPHY</div>{geo_html}</div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_glass_enhanced(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 3: Glass Enhanced — улучшенный стеклянный эффект"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    
    authors_html = ''.join([f'<span class="tag">{a["display_name"]} ({a["mention_count"]})</span>' for a in stats['author_frequency_all']['all_authors'][:8]])
    journals_html = ''.join([f'<span class="tag tag-gold">{j["journal"]} ({j["count"]})</span>' for j in stats['journal_frequency_all']['all_journals'][:6]])
    geo_html = ''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:5]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Glass Enhanced</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{min-height:100vh;background:linear-gradient(135deg,#0c0c1e 0%,#1a1a3e 50%,#2d1b69 100%);padding:30px;font-family:'Segoe UI',sans-serif;}}
.container{{max-width:1200px;margin:0 auto;}}
.glass{{background:rgba(255,255,255,0.06);backdrop-filter:blur(30px);-webkit-backdrop-filter:blur(30px);border-radius:24px;padding:28px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.08);box-shadow:0 8px 40px rgba(0,0,0,0.3);}}
h1{{background:linear-gradient(135deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:34px;font-weight:700;}}
.subtitle{{color:rgba(255,255,255,0.5);font-size:14px;}}
.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;}}
.stat{{background:rgba(255,255,255,0.04);border-radius:16px;padding:18px;text-align:center;border:1px solid rgba(255,255,255,0.04);}}
.num{{font-size:30px;font-weight:700;background:linear-gradient(135deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.lbl{{font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-top:5px;}}
.tag{{display:inline-block;padding:5px 16px;margin:3px;border-radius:20px;font-size:13px;background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.8);border:1px solid rgba(255,255,255,0.06);}}
.tag-gold{{background:rgba(247,151,30,0.15);border-color:rgba(247,151,30,0.2);color:#f7971e;}}
.sidebar-glass{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.04);backdrop-filter:blur(20px);border-radius:16px;padding:12px;border:1px solid rgba(255,255,255,0.04);z-index:100;}}
.sidebar-glass a{{display:block;color:rgba(255,255,255,0.4);text-decoration:none;padding:6px 12px;font-size:11px;border-radius:6px;transition:all 0.3s;}}
.sidebar-glass a:hover{{background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.8);}}
.footer{{text-align:center;color:rgba(255,255,255,0.2);font-size:11px;padding:15px;}}
</style>
</head>
<body>
<div class="sidebar-glass">
    <a href="#overview">✦ Overview</a>
    <a href="#authors">✦ Authors</a>
    <a href="#journals">✦ Journals</a>
    <a href="#geo">✦ Geography</a>
</div>
<div class="container" style="margin-left:100px;">
    <div class="glass"><h1>✦ Glass Enhanced</h1><div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div></div>
    <div id="overview" class="glass">
        <div class="grid">
            <div class="stat"><div class="num">{total}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{doi}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{last5}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{self_cit}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{citations}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div id="authors" class="glass"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;font-weight:600;">✦ Authors</div>{authors_html}</div>
    <div id="journals" class="glass"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;font-weight:600;">✦ Journals</div>{journals_html}</div>
    <div id="geo" class="glass"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;font-weight:600;">✦ Geography</div>{geo_html}</div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_smart_glow(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 4: Smart Glow — умная аналитика с подсветкой"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    avg = stats.get('avg_citations', 0)
    
    authors_html = ''.join([f'<span class="tag">{a["display_name"]} ({a["mention_count"]})</span>' for a in stats['author_frequency_all']['all_authors'][:8]])
    journals_html = ''.join([f'<span class="tag tag-blue">{j["journal"]} ({j["count"]})</span>' for j in stats['journal_frequency_all']['all_journals'][:6]])
    geo_html = ''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:5]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Smart Glow</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d1117;padding:30px;font-family:'Inter',sans-serif;color:#e6edf3;}}
.container{{max-width:1200px;margin:0 auto;}}
.glow-card{{background:linear-gradient(145deg,#161b22,#0d1117);border-radius:20px;padding:25px;margin-bottom:18px;border:1px solid #30363d;box-shadow:0 4px 30px rgba(0,0,0,0.3);}}
h1{{font-size:32px;font-weight:700;background:linear-gradient(135deg,#58a6ff,#f0883e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.subtitle{{color:#8b949e;font-size:14px;}}
.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;}}
.stat{{background:#0d1117;border-radius:14px;padding:18px;text-align:center;border:1px solid #30363d;transition:all 0.3s;}}
.stat:hover{{border-color:#58a6ff;box-shadow:0 0 30px rgba(88,166,255,0.1);}}
.num{{font-size:28px;font-weight:700;color:#58a6ff;}}
.lbl{{font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:1px;margin-top:4px;}}
.tag{{display:inline-block;padding:4px 14px;margin:3px;border-radius:16px;font-size:12px;background:#161b22;border:1px solid #30363d;color:#c9d1d9;}}
.tag-blue{{border-color:#58a6ff;color:#58a6ff;}}
.sidebar-glow{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:#161b22;border-radius:12px;padding:12px;border:1px solid #30363d;z-index:100;}}
.sidebar-glow a{{display:block;color:#8b949e;text-decoration:none;padding:6px 12px;font-size:11px;border-radius:6px;transition:all 0.3s;}}
.sidebar-glow a:hover{{color:#58a6ff;background:#0d1117;}}
.footer{{text-align:center;color:#8b949e;font-size:11px;padding:15px;}}
</style>
</head>
<body>
<div class="sidebar-glow">
    <a href="#overview">✦ Overview</a>
    <a href="#authors">✦ Authors</a>
    <a href="#journals">✦ Journals</a>
    <a href="#geo">✦ Geography</a>
</div>
<div class="container" style="margin-left:100px;">
    <div class="glow-card"><h1>✦ Smart Glow</h1><div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div></div>
    <div id="overview" class="glow-card">
        <div class="grid">
            <div class="stat"><div class="num">{total}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{doi}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{last5}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{self_cit}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{citations}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div id="authors" class="glow-card"><div style="color:#c9d1d9;margin-bottom:12px;font-weight:600;">👨‍🎓 Authors</div>{authors_html}</div>
    <div id="journals" class="glow-card"><div style="color:#c9d1d9;margin-bottom:12px;font-weight:600;">📖 Journals</div>{journals_html}</div>
    <div id="geo" class="glow-card"><div style="color:#c9d1d9;margin-bottom:12px;font-weight:600;">🌍 Geography</div>{geo_html}</div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_aurora(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 5: Aurora — северное сияние"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    
    authors_html = ''.join([f'<span class="tag">{a["display_name"]} ({a["mention_count"]})</span>' for a in stats['author_frequency_all']['all_authors'][:8]])
    journals_html = ''.join([f'<span class="tag">{j["journal"]} ({j["count"]})</span>' for j in stats['journal_frequency_all']['all_journals'][:6]])
    geo_html = ''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:5]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Aurora</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{min-height:100vh;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);padding:30px;font-family:'Segoe UI',sans-serif;color:#fff;}}
.container{{max-width:1200px;margin:0 auto;}}
.aurora-card{{background:rgba(255,255,255,0.04);border-radius:20px;padding:25px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.06);position:relative;overflow:hidden;}}
.aurora-card::before{{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:conic-gradient(from 0deg,transparent,rgba(0,255,200,0.03),transparent,rgba(200,0,255,0.03),transparent);animation:rotate 20s linear infinite;pointer-events:none;}}
@keyframes rotate{{100%{{transform:rotate(360deg);}}}}
h1{{font-size:32px;font-weight:300;background:linear-gradient(90deg,#00ff87,#60efff,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;position:relative;z-index:1;}}
.subtitle{{color:rgba(255,255,255,0.4);font-size:14px;position:relative;z-index:1;}}
.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;position:relative;z-index:1;}}
.stat{{background:rgba(255,255,255,0.03);border-radius:14px;padding:18px;text-align:center;}}
.num{{font-size:28px;font-weight:700;background:linear-gradient(135deg,#00ff87,#60efff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.lbl{{font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-top:4px;}}
.tag{{display:inline-block;padding:4px 14px;margin:3px;border-radius:16px;font-size:12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.06);color:rgba(255,255,255,0.7);position:relative;z-index:1;}}
.sidebar-aurora{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.04);backdrop-filter:blur(10px);border-radius:16px;padding:12px;border:1px solid rgba(255,255,255,0.04);z-index:100;}}
.sidebar-aurora a{{display:block;color:rgba(255,255,255,0.3);text-decoration:none;padding:6px 12px;font-size:11px;border-radius:6px;transition:all 0.3s;}}
.sidebar-aurora a:hover{{color:#60efff;background:rgba(255,255,255,0.04);}}
.footer{{text-align:center;color:rgba(255,255,255,0.2);font-size:11px;padding:15px;position:relative;z-index:1;}}
</style>
</head>
<body>
<div class="sidebar-aurora">
    <a href="#overview">✦ Overview</a>
    <a href="#authors">✦ Authors</a>
    <a href="#journals">✦ Journals</a>
    <a href="#geo">✦ Geography</a>
</div>
<div class="container" style="margin-left:100px;">
    <div class="aurora-card"><h1>✦ Aurora</h1><div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div></div>
    <div id="overview" class="aurora-card">
        <div class="grid">
            <div class="stat"><div class="num">{total}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{doi}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{last5}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{self_cit}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{citations}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div id="authors" class="aurora-card"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;">👨‍🎓 Authors</div>{authors_html}</div>
    <div id="journals" class="aurora-card"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;">📖 Journals</div>{journals_html}</div>
    <div id="geo" class="aurora-card"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;">🌍 Geography</div>{geo_html}</div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_timeline_wave(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 6: Timeline Wave — волновая визуализация годов"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    years = sorted(stats['yearly_stats']['yearly_counts'].keys())
    max_val = max(stats['yearly_stats']['yearly_counts'].values()) if years else 1
    bars = ''.join([f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;"><div style="height:{count/max_val*150}px;width:30px;background:linear-gradient(180deg,#667eea,#764ba2);border-radius:4px 4px 0 0;transition:height 0.5s;box-shadow:0 0 20px rgba(102,126,234,0.3);"></div><div style="font-size:11px;color:#666;margin-top:5px;">{year}</div><div style="font-size:10px;color:#999;">{count}</div></div>' for year,count in sorted(stats['yearly_stats']['yearly_counts'].items())])
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    
    authors_html = ''.join([f'<div style="font-size:13px;padding:3px 0;border-bottom:1px solid #eee;">{a["display_name"]} ({a["mention_count"]})</div>' for a in stats['author_frequency_all']['all_authors'][:5]])
    journals_html = ''.join([f'<div style="font-size:13px;padding:3px 0;border-bottom:1px solid #eee;">{j["journal"]} ({j["count"]})</div>' for j in stats['journal_frequency_all']['all_journals'][:5]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Timeline Wave</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#f8f9fa;padding:30px;font-family:'Segoe UI',sans-serif;}}
.container{{max-width:1200px;margin:0 auto;background:#fff;border-radius:20px;padding:30px;box-shadow:0 4px 30px rgba(0,0,0,0.06);}}
h1{{font-size:28px;font-weight:700;color:#1a1a2e;}}
.subtitle{{color:#999;font-size:14px;}}
.timeline{{display:flex;justify-content:space-around;align-items:flex-end;height:200px;padding:20px;background:#f8f9fa;border-radius:12px;margin:20px 0;}}
.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:20px 0;}}
.stat{{background:#f8f9fa;border-radius:12px;padding:15px;text-align:center;}}
.num{{font-size:24px;font-weight:700;color:#667eea;}}
.lbl{{font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px;margin-top:4px;}}
.tag{{display:inline-block;padding:4px 14px;margin:3px;border-radius:16px;font-size:12px;background:#f0f2f5;color:#333;}}
.sidebar-wave{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:#fff;border-radius:12px;padding:12px;box-shadow:0 2px 12px rgba(0,0,0,0.06);z-index:100;}}
.sidebar-wave a{{display:block;color:#999;text-decoration:none;padding:6px 12px;font-size:11px;border-radius:6px;transition:all 0.3s;}}
.sidebar-wave a:hover{{color:#667eea;background:#f8f9fa;}}
.footer{{text-align:center;color:#ccc;font-size:11px;padding:15px;border-top:1px solid #eee;margin-top:20px;}}
</style>
</head>
<body>
<div class="sidebar-wave">
    <a href="#overview">📊 Overview</a>
    <a href="#timeline">📈 Timeline</a>
    <a href="#authors">👤 Authors</a>
    <a href="#journals">📖 Journals</a>
</div>
<div class="container" style="margin-left:80px;">
    <h1>📊 Timeline Wave</h1>
    <div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div>
    <div id="overview" class="grid">
        <div class="stat"><div class="num">{total}</div><div class="lbl">Total</div></div>
        <div class="stat"><div class="num">{doi}</div><div class="lbl">DOI</div></div>
        <div class="stat"><div class="num">{last5}</div><div class="lbl">5 Years</div></div>
        <div class="stat"><div class="num">{self_cit}</div><div class="lbl">Self-Cit</div></div>
        <div class="stat"><div class="num">{citations}</div><div class="lbl">Citations</div></div>
    </div>
    <div id="timeline" class="timeline">{bars}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px;">
        <div id="authors" style="background:#f8f9fa;border-radius:12px;padding:15px;">
            <div style="font-weight:600;margin-bottom:8px;">👨‍🎓 Authors</div>
            {authors_html}
        </div>
        <div id="journals" style="background:#f8f9fa;border-radius:12px;padding:15px;">
            <div style="font-weight:600;margin-bottom:8px;">📖 Journals</div>
            {journals_html}
        </div>
    </div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_masonry(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 7: Masonry — плиточная раскладка"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    avg = stats.get('avg_citations', 0)
    
    author_cards = ''.join([f'<div style="background:#fff;border-radius:12px;padding:15px;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:4px solid #667eea;margin-bottom:10px;"><div style="font-weight:600;">{a["display_name"]}</div><div style="font-size:12px;color:#666;">{a["mention_count"]} citations</div></div>' for a in stats['author_frequency_all']['all_authors'][:6]])
    journal_items = ''.join([f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0f0f0;font-size:13px;"><span>{j["journal"]}</span><span style="font-weight:600;color:#667eea;">{j["count"]}</span></div>' for j in stats['journal_frequency_all']['all_journals'][:6]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Masonry</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#f5f7fa;padding:30px;font-family:'Segoe UI',sans-serif;}}
.container{{max-width:1200px;margin:0 auto;}}
h1{{font-size:28px;font-weight:700;color:#1a1a2e;}}
.subtitle{{color:#999;font-size:14px;}}
.masonry-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin:20px 0;}}
.masonry-item{{background:#fff;border-radius:16px;padding:20px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);transition:transform 0.2s;}}
.masonry-item:hover{{transform:translateY(-4px);box-shadow:0 4px 16px rgba(0,0,0,0.08);}}
.num{{font-size:28px;font-weight:700;color:#667eea;}}
.lbl{{font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px;margin-top:4px;}}
.row{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;}}
.tag{{display:inline-block;padding:4px 14px;background:#f0f2f5;border-radius:16px;font-size:12px;color:#333;}}
.sidebar-masonry{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:#fff;border-radius:12px;padding:12px;box-shadow:0 2px 12px rgba(0,0,0,0.06);z-index:100;}}
.sidebar-masonry a{{display:block;color:#999;text-decoration:none;padding:6px 12px;font-size:11px;border-radius:6px;transition:all 0.3s;}}
.sidebar-masonry a:hover{{color:#667eea;background:#f5f7fa;}}
.footer{{text-align:center;color:#ccc;font-size:11px;padding:15px;border-top:1px solid #eee;margin-top:20px;}}
</style>
</head>
<body>
<div class="sidebar-masonry">
    <a href="#overview">✦ Overview</a>
    <a href="#authors">✦ Authors</a>
    <a href="#journals">✦ Journals</a>
</div>
<div class="container" style="margin-left:80px;">
    <h1>✦ Masonry Dashboard</h1>
    <div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div>
    <div id="overview" class="masonry-grid">
        <div class="masonry-item"><div class="num">{total}</div><div class="lbl">Total</div></div>
        <div class="masonry-item"><div class="num">{doi}</div><div class="lbl">DOI</div></div>
        <div class="masonry-item"><div class="num">{last5}</div><div class="lbl">5 Years</div></div>
        <div class="masonry-item"><div class="num">{self_cit}</div><div class="lbl">Self-Cit</div></div>
        <div class="masonry-item"><div class="num">{citations}</div><div class="lbl">Citations</div></div>
        <div class="masonry-item"><div class="num">{avg:.1f}</div><div class="lbl">Avg Cit</div></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div id="authors" style="background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="font-weight:600;margin-bottom:12px;">👨‍🎓 Authors</div>
            {author_cards}
        </div>
        <div id="journals" style="background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="font-weight:600;margin-bottom:12px;">📖 Journals</div>
            {journal_items}
        </div>
    </div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_holographic(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 8: Holographic — голографический эффект"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    
    authors_html = ''.join([f'<span class="tag">{a["display_name"]} ({a["mention_count"]})</span>' for a in stats['author_frequency_all']['all_authors'][:8]])
    journals_html = ''.join([f'<span class="tag">{j["journal"]} ({j["count"]})</span>' for j in stats['journal_frequency_all']['all_journals'][:6]])
    geo_html = ''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:5]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Holographic</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{min-height:100vh;background:linear-gradient(135deg,#0a0a1a,#1a0a2e,#0a1a2e);padding:30px;font-family:'Segoe UI',sans-serif;color:#fff;}}
.container{{max-width:1200px;margin:0 auto;}}
.holo{{background:linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));border-radius:20px;padding:25px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(10px);position:relative;overflow:hidden;}}
.holo::before{{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:conic-gradient(from 0deg,#ff6b6b,#ffd93d,#6bcb77,#4d96ff,#ff6b6b);animation:spin 8s linear infinite;opacity:0.05;pointer-events:none;}}
@keyframes spin{{100%{{transform:rotate(360deg);}}}}
h1{{font-size:32px;font-weight:700;background:linear-gradient(90deg,#ff6b6b,#ffd93d,#6bcb77,#4d96ff,#ff6b6b);background-size:300% 100%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 4s linear infinite;}}
@keyframes shimmer{{0%{{background-position:0% 50%}}100%{{background-position:300% 50%}}}}
.subtitle{{color:rgba(255,255,255,0.4);font-size:14px;}}
.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;position:relative;z-index:1;}}
.stat{{background:rgba(255,255,255,0.03);border-radius:14px;padding:18px;text-align:center;border:1px solid rgba(255,255,255,0.04);}}
.num{{font-size:28px;font-weight:700;background:linear-gradient(90deg,#ff6b6b,#ffd93d);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.lbl{{font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-top:4px;}}
.tag{{display:inline-block;padding:4px 14px;margin:3px;border-radius:16px;font-size:12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);color:rgba(255,255,255,0.7);}}
.sidebar-holo{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.02);backdrop-filter:blur(10px);border-radius:12px;padding:12px;border:1px solid rgba(255,255,255,0.04);z-index:100;}}
.sidebar-holo a{{display:block;color:rgba(255,255,255,0.3);text-decoration:none;padding:6px 12px;font-size:11px;border-radius:6px;transition:all 0.3s;}}
.sidebar-holo a:hover{{color:#ffd93d;background:rgba(255,255,255,0.04);}}
.footer{{text-align:center;color:rgba(255,255,255,0.2);font-size:11px;padding:15px;}}
</style>
</head>
<body>
<div class="sidebar-holo">
    <a href="#overview">✦ Overview</a>
    <a href="#authors">✦ Authors</a>
    <a href="#journals">✦ Journals</a>
    <a href="#geo">✦ Geography</a>
</div>
<div class="container" style="margin-left:100px;">
    <div class="holo"><h1>✦ HOLOGRAPHIC</h1><div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div></div>
    <div id="overview" class="holo">
        <div class="grid">
            <div class="stat"><div class="num">{total}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{doi}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{last5}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{self_cit}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{citations}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div id="authors" class="holo"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;">👨‍🎓 Authors</div>{authors_html}</div>
    <div id="journals" class="holo"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;">📖 Journals</div>{journals_html}</div>
    <div id="geo" class="holo"><div style="color:rgba(255,255,255,0.6);margin-bottom:12px;">🌍 Geography</div>{geo_html}</div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_geo_bubbles(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 9: Geo Bubbles — географические пузырьки"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    
    countries = list(stats['geography']['type1_unique_countries_per_reference'].items())
    max_count = max([c[1] for c in countries]) if countries else 1
    bubbles = ''.join([f'<div style="display:flex;align-items:center;margin:6px 0;"><div style="width:100px;font-size:14px;">{c}</div><div style="flex:1;height:24px;background:#e9ecef;border-radius:12px;overflow:hidden;"><div style="height:100%;width:{count/max_count*100}%;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:12px;transition:width 0.5s;"></div></div><div style="width:40px;text-align:right;font-size:14px;font-weight:600;color:#667eea;">{count}</div></div>' for c,count in countries])
    
    authors_html = ''.join([f'<div style="font-size:13px;padding:4px 0;border-bottom:1px solid #eee;">{a["display_name"]} ({a["mention_count"]})</div>' for a in stats['author_frequency_all']['all_authors'][:5]])
    collab_html = ''.join([f'<div style="font-size:13px;padding:4px 0;border-bottom:1px solid #eee;">{c["country1"]} + {c["country2"]} ({c["count"]})</div>' for c in stats['geography']['collaboration_matrix'][:4]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Geo Bubbles</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#f0f4f8;padding:30px;font-family:'Segoe UI',sans-serif;}}
.container{{max-width:1200px;margin:0 auto;background:#fff;border-radius:20px;padding:30px;box-shadow:0 4px 30px rgba(0,0,0,0.06);}}
h1{{font-size:28px;font-weight:700;color:#1a1a2e;}}
.subtitle{{color:#999;font-size:14px;}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0;}}
.stat{{background:#f8f9fa;border-radius:12px;padding:15px;text-align:center;}}
.num{{font-size:24px;font-weight:700;color:#667eea;}}
.lbl{{font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px;margin-top:4px;}}
.section{{background:#f8f9fa;border-radius:12px;padding:20px;margin:15px 0;}}
.section-title{{font-weight:600;margin-bottom:12px;font-size:16px;}}
.tag{{display:inline-block;padding:4px 14px;margin:3px;border-radius:16px;font-size:12px;background:#e8f0fe;color:#1a73e8;}}
.sidebar-geo{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:#fff;border-radius:12px;padding:12px;box-shadow:0 2px 12px rgba(0,0,0,0.06);z-index:100;}}
.sidebar-geo a{{display:block;color:#999;text-decoration:none;padding:6px 12px;font-size:11px;border-radius:6px;transition:all 0.3s;}}
.sidebar-geo a:hover{{color:#667eea;background:#f8f9fa;}}
.footer{{text-align:center;color:#ccc;font-size:11px;padding:15px;border-top:1px solid #eee;margin-top:20px;}}
</style>
</head>
<body>
<div class="sidebar-geo">
    <a href="#overview">🌍 Overview</a>
    <a href="#geo">🌐 Countries</a>
    <a href="#authors">👤 Authors</a>
    <a href="#collab">🤝 Collaborations</a>
</div>
<div class="container" style="margin-left:80px;">
    <h1>🌍 Geo Bubbles</h1>
    <div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div>
    <div id="overview" class="grid">
        <div class="stat"><div class="num">{total}</div><div class="lbl">Total</div></div>
        <div class="stat"><div class="num">{doi}</div><div class="lbl">DOI</div></div>
        <div class="stat"><div class="num">{last5}</div><div class="lbl">5 Years</div></div>
        <div class="stat"><div class="num">{self_cit}</div><div class="lbl">Self-Cit</div></div>
    </div>
    <div id="geo" class="section">
        <div class="section-title">🌐 Countries Distribution</div>
        {bubbles}
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div id="authors" class="section">
            <div class="section-title">👨‍🎓 Authors</div>
            {authors_html}
        </div>
        <div id="collab" class="section">
            <div class="section-title">🤝 Collaborations</div>
            {collab_html}
        </div>
    </div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

def generate_style_particles(
    stats: Dict,
    paper_authors: Set[str],
    lang: str = 'en',
    journal_name: str = '',
    article_number: str = '',
    duplicates: List[Dict] = None,
    primary_color: str = '#667eea',
    secondary_color: str = '#764ba2',
    potential_reviewers: List[Dict] = None,
    show_reviewers: bool = False
) -> str:
    """Стиль 10: Particles — космическая тема"""
    
    def get_text_local(key: str) -> str:
        from app import TEXTS
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        return key
    
    total = stats['total_references']
    doi = stats['total_with_doi']
    last5 = stats['yearly_stats']['last_5_years']
    self_cit = stats['self_citations_count']
    citations = stats.get('total_citations_sum', 0)
    
    authors_html = ''.join([f'<span class="tag">{a["display_name"]} ({a["mention_count"]})</span>' for a in stats['author_frequency_all']['all_authors'][:8]])
    journals_html = ''.join([f'<span class="tag">{j["journal"]} ({j["count"]})</span>' for j in stats['journal_frequency_all']['all_journals'][:6]])
    geo_html = ''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:5]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Particles</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{min-height:100vh;background:radial-gradient(ellipse at center,#1a1a2e,#0a0a1a);padding:30px;font-family:'Segoe UI',sans-serif;color:#fff;}}
.container{{max-width:1200px;margin:0 auto;}}
.particle-card{{background:rgba(255,255,255,0.02);border-radius:20px;padding:25px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.03);box-shadow:0 8px 40px rgba(0,0,0,0.3);position:relative;}}
.particle-card::after{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(circle at 20% 50%,rgba(100,100,255,0.05),transparent 70%),radial-gradient(circle at 80% 50%,rgba(255,100,100,0.05),transparent 70%);pointer-events:none;border-radius:20px;}}
h1{{font-size:32px;font-weight:300;letter-spacing:4px;background:linear-gradient(90deg,#a78bfa,#60efff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;position:relative;z-index:1;}}
.subtitle{{color:rgba(255,255,255,0.3);font-size:14px;position:relative;z-index:1;letter-spacing:2px;}}
.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;position:relative;z-index:1;}}
.stat{{background:rgba(255,255,255,0.02);border-radius:14px;padding:18px;text-align:center;border:1px solid rgba(255,255,255,0.02);}}
.num{{font-size:28px;font-weight:700;background:linear-gradient(135deg,#a78bfa,#60efff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.lbl{{font-size:11px;color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:2px;margin-top:4px;}}
.tag{{display:inline-block;padding:4px 14px;margin:3px;border-radius:16px;font-size:12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);color:rgba(255,255,255,0.5);position:relative;z-index:1;}}
.sidebar-particles{{position:fixed;left:20px;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.02);backdrop-filter:blur(10px);border-radius:12px;padding:12px;border:1px solid rgba(255,255,255,0.02);z-index:100;}}
.sidebar-particles a{{display:block;color:rgba(255,255,255,0.2);text-decoration:none;padding:6px 12px;font-size:11px;border-radius:6px;transition:all 0.3s;letter-spacing:2px;}}
.sidebar-particles a:hover{{color:#a78bfa;background:rgba(255,255,255,0.02);}}
.footer{{text-align:center;color:rgba(255,255,255,0.1);font-size:11px;padding:15px;letter-spacing:2px;}}
</style>
</head>
<body>
<div class="sidebar-particles">
    <a href="#overview">◈ OVERVIEW</a>
    <a href="#authors">◈ AUTHORS</a>
    <a href="#journals">◈ JOURNALS</a>
    <a href="#geo">◈ GEO</a>
</div>
<div class="container" style="margin-left:100px;">
    <div class="particle-card"><h1>✦ PARTICLES</h1><div class="subtitle">{journal_name or 'Chimica Techno Acta'} • {get_date()}</div></div>
    <div id="overview" class="particle-card">
        <div class="grid">
            <div class="stat"><div class="num">{total}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{doi}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{last5}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{self_cit}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{citations}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div id="authors" class="particle-card"><div style="color:rgba(255,255,255,0.4);margin-bottom:12px;letter-spacing:2px;">◈ AUTHORS</div>{authors_html}</div>
    <div id="journals" class="particle-card"><div style="color:rgba(255,255,255,0.4);margin-bottom:12px;letter-spacing:2px;">◈ JOURNALS</div>{journals_html}</div>
    <div id="geo" class="particle-card"><div style="color:rgba(255,255,255,0.4);margin-bottom:12px;letter-spacing:2px;">◈ GEOGRAPHY</div>{geo_html}</div>
    <div class="footer">{get_footer()}</div>
</div>
</body></html>'''

# ============================================================
# РЕГИСТРАЦИЯ ВСЕХ СТИЛЕЙ
# ============================================================

STYLE_GENERATORS = {
    'classic': generate_classic_report,
    'glassmorphism': generate_style_glassmorphism,
    'neon_cyber': generate_style_neon_cyber,
    'glass_enhanced': generate_style_glass_enhanced,
    'smart_glow': generate_style_smart_glow,
    'aurora': generate_style_aurora,
    'timeline_wave': generate_style_timeline_wave,
    'masonry': generate_style_masonry,
    'holographic': generate_style_holographic,
    'geo_bubbles': generate_style_geo_bubbles,
    'particles': generate_style_particles
}

STYLE_NAMES = {
    'classic': 'Classic',
    'glassmorphism': 'Glassmorphism',
    'neon_cyber': 'Neon Cyber',
    'glass_enhanced': 'Glass Enhanced',
    'smart_glow': 'Smart Glow',
    'aurora': 'Aurora',
    'timeline_wave': 'Timeline Wave',
    'masonry': 'Masonry',
    'holographic': 'Holographic',
    'geo_bubbles': 'Geo Bubbles',
    'particles': 'Particles'
}

def get_style_generator(style_name: str):
    """Возвращает функцию-генератор для указанного стиля"""
    return STYLE_GENERATORS.get(style_name, generate_classic_report)
