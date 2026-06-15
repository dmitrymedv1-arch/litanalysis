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
import html 
from urllib.parse import urlparse

# ======================== COLOR UTILITIES FOR DYNAMIC THEMES ========================
import colorsys

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_complementary_color(hex_color: str) -> str:
    """
    Generate complementary color by rotating hue by 180 degrees
    Returns a color that pairs well with the base color
    """
    rgb = hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    # Rotate hue by 0.5 (180 degrees)
    complementary_hue = (h + 0.5) % 1.0
    complementary_rgb = colorsys.hsv_to_rgb(complementary_hue, s, v)
    return rgb_to_hex(tuple(int(c * 255) for c in complementary_rgb))

def show_color_preview():
    """Display interactive color preview in sidebar"""
    primary = st.session_state.get('primary_color', '#667eea')
    secondary = st.session_state.get('secondary_color', get_complementary_color(primary))
    analogous = get_analogous_colors(primary, 2)
    
    st.markdown("### 🎨 Color Preview")
    
    # Create a visual palette
    palette_html = f"""
    <div style="display: flex; gap: 10px; margin: 15px 0; flex-wrap: wrap;">
        <div style="flex: 1; text-align: center;">
            <div style="background: {primary}; height: 60px; border-radius: 10px 10px 0 0;"></div>
            <div style="background: {secondary}; height: 60px; border-radius: 0 0 10px 10px;"></div>
            <div style="font-size: 11px; margin-top: 5px;">Primary → Complementary</div>
        </div>
        <div style="flex: 1; text-align: center;">
            <div style="background: {analogous[0] if analogous else primary}; height: 60px; border-radius: 10px;"></div>
            <div style="font-size: 11px; margin-top: 5px;">Analogous 1</div>
        </div>
        <div style="flex: 1; text-align: center;">
            <div style="background: {analogous[1] if len(analogous) > 1 else secondary}; height: 60px; border-radius: 10px;"></div>
            <div style="font-size: 11px; margin-top: 5px;">Analogous 2</div>
        </div>
    </div>
    
    <div style="display: flex; gap: 10px; margin: 10px 0;">
        <div style="flex: 1; background: linear-gradient(135deg, {primary}, {secondary}); height: 30px; border-radius: 15px;"></div>
        <div style="flex: 1; background: linear-gradient(90deg, {primary}, {secondary}); height: 30px; border-radius: 15px;"></div>
    </div>
    """
    st.markdown(palette_html, unsafe_allow_html=True)
    
    # Button to reset to default
    if st.button("Reset to Default Theme", use_container_width=True):
        st.session_state.primary_color = '#667eea'
        st.rerun()

def get_analogous_colors(hex_color: str, count: int = 2) -> List[str]:
    """
    Generate analogous colors (colors adjacent on color wheel)
    Useful for gradients and accents
    """
    rgb = hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    
    colors = []
    step = 30 / 360.0  # 30 degrees in hue space
    
    for i in range(count):
        offset = (i + 1) * step
        new_hue = (h + offset) % 1.0
        new_rgb = colorsys.hsv_to_rgb(new_hue, s, v)
        colors.append(rgb_to_hex(tuple(int(c * 255) for c in new_rgb)))
    
    return colors

def get_gradient_colors(hex_color: str, steps: int = 5) -> List[str]:
    """
    Generate gradient colors from base color to lighter shades
    """
    rgb = hex_to_rgb(hex_color)
    colors = []
    
    for i in range(steps):
        factor = 0.3 + (i * 0.14)  # 0.3 to 0.86
        new_rgb = tuple(min(255, int(c * (1 + factor * 0.5))) for c in rgb)
        colors.append(rgb_to_hex(new_rgb))
    
    return colors

def get_contrast_color(hex_color: str) -> str:
    """
    Get contrasting color (black or white) for text on a colored background
    Uses luminance calculation for optimal readability
    """
    rgb = hex_to_rgb(hex_color)
    # Calculate relative luminance (WCAG formula)
    luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
    return '#FFFFFF' if luminance < 0.5 else '#000000'

def generate_css_variables(base_color: str, accent_color: str = None) -> Dict[str, str]:
    """
    Generate complete CSS variable set for the theme
    """
    if accent_color is None:
        accent_color = get_complementary_color(base_color)
    
    # Generate gradient colors
    gradient_start = base_color
    gradient_end = accent_color
    
    # Generate lighter shades for backgrounds
    lighter_base = get_gradient_colors(base_color, 1)[0]
    lighter_accent = get_gradient_colors(accent_color, 1)[0]
    
    # Get contrast colors for text
    base_contrast = get_contrast_color(base_color)
    accent_contrast = get_contrast_color(accent_color)
    
    # Generate analogous colors for accents
    analogous = get_analogous_colors(base_color, 2)
    
    return {
        '--primary-color': base_color,
        '--secondary-color': accent_color,
        '--primary-light': lighter_base,
        '--secondary-light': lighter_accent,
        '--primary-contrast': base_contrast,
        '--secondary-contrast': accent_contrast,
        '--gradient-start': gradient_start,
        '--gradient-end': gradient_end,
        '--accent-1': analogous[0] if len(analogous) > 0 else accent_color,
        '--accent-2': analogous[1] if len(analogous) > 1 else accent_color,
        '--hover-light': f"{base_color}20",
    }

def apply_theme_css(base_color: str, accent_color: str = None):
    """
    Apply dynamic CSS theme based on selected colors
    """
    if accent_color is None:
        accent_color = get_complementary_color(base_color)
    
    css_vars = generate_css_variables(base_color, accent_color)
    
    theme_css = f"""
    <style>
        :root {{
            --primary: {css_vars['--primary-color']};
            --secondary: {css_vars['--secondary-color']};
            --primary-light: {css_vars['--primary-light']};
            --secondary-light: {css_vars['--secondary-light']};
            --primary-contrast: {css_vars['--primary-contrast']};
            --secondary-contrast: {css_vars['--secondary-contrast']};
            --gradient-start: {css_vars['--gradient-start']};
            --gradient-end: {css_vars['--gradient-end']};
            --accent-1: {css_vars['--accent-1']};
            --accent-2: {css_vars['--accent-2']};
            --hover-light: {css_vars['--hover-light']};
        }}
        
        /* Update all gradient backgrounds */
        .stApp {{
            background: linear-gradient(135deg, 
                rgba({int(hex_to_rgb(css_vars['--gradient-start'])[0])}, {int(hex_to_rgb(css_vars['--gradient-start'])[1])}, {int(hex_to_rgb(css_vars['--gradient-start'])[2])}, 0.05) 0%,
                rgba({int(hex_to_rgb(css_vars['--gradient-end'])[0])}, {int(hex_to_rgb(css_vars['--gradient-end'])[1])}, {int(hex_to_rgb(css_vars['--gradient-end'])[2])}, 0.08) 100%);
        }}
        
        .metric-number {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .section-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }}
        
        .rank-item {{
            border-left: 3px solid var(--primary);
        }}
        
        .rank-number {{
            color: var(--primary);
        }}
        
        .progress-fill {{
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }}
        
        .custom-tab-button.active {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }}
        
        .custom-tab-button:hover {{
            background: linear-gradient(135deg, var(--primary-light) 0%, var(--secondary-light) 100%);
        }}
        
        .colored-progress-bar {{
            background: linear-gradient(90deg, 
                var(--primary) 0%, 
                var(--secondary) 50%,
                var(--primary) 100%);
        }}
        
        .section-title {{
            border-bottom: 3px solid var(--primary);
        }}
        
        .concept-card {{
            background: linear-gradient(135deg, var(--hover-light) 0%, var(--secondary-light) 100%);
            border: 1px solid var(--primary-light);
        }}
        
        .concept-name {{
            color: var(--primary);
        }}
        
        .clickable-link {{
            color: var(--primary);
        }}
        
        .clickable-link:hover {{
            color: var(--secondary);
        }}
        
        .badge-success {{
            background: var(--primary-light);
            color: var(--primary-contrast);
        }}
        
        .custom-tab-button .custom-tab-title {{
            color: inherit;
        }}
        
        /* Additional hover effects */
        .metric-card:hover {{
            box-shadow: 0 6px 12px rgba({int(hex_to_rgb(css_vars['--primary-color'])[0])}, {int(hex_to_rgb(css_vars['--primary-color'])[1])}, {int(hex_to_rgb(css_vars['--primary-color'])[2])}, 0.15);
        }}
        
        /* Smooth color transitions */
        * {{
            transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }}
        
        /* Custom color picker preview */
        .color-preview {{
            display: inline-block;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-left: 10px;
            vertical-align: middle;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .color-preview:hover {{
            transform: scale(1.1);
        }}
        
        /* Complementary color indicator */
        .complementary-preview {{
            display: inline-block;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-left: 10px;
            vertical-align: middle;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* Theme info panel */
        .theme-info {{
            background: var(--hover-light);
            border-radius: 10px;
            padding: 12px;
            margin-top: 15px;
            font-size: 12px;
            text-align: center;
        }}
        
        /* Reviewer card styles */
        .reviewer-card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid var(--primary);
            transition: transform 0.2s;
        }}
        
        .reviewer-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .reviewer-name {{
            font-size: 18px;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 8px;
        }}
        
        .reviewer-orcid {{
            font-family: monospace;
            font-size: 12px;
            margin-bottom: 8px;
        }}
        
        .reviewer-section-title {{
            font-weight: 600;
            margin-top: 12px;
            margin-bottom: 6px;
            font-size: 13px;
            color: #555;
        }}
        
        .external-id-link {{
            display: inline-block;
            background: #f0f0f0;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            margin: 3px;
            text-decoration: none;
            color: #333;
            transition: all 0.2s;
        }}
        
        .external-id-link:hover {{
            background: var(--primary);
            color: white;
        }}
        
        .confidential-banner {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 4px solid #dc3545;
            padding: 12px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            font-weight: 500;
            color: #856404;
        }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

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
        'journal_name_label': "📝 Journal name",
        'journal_name_help': "If not specified, 'Chimica Techno Acta' will be used",
        'article_number_label': "🔢 Article number",
        'article_number_help': "Example: 1224, CTA-1234, CTA/1224",
        'duplicate_references_title': "Duplicate References (Full DOI Match)",
        'full_doi_match': "Full DOI Match",
        'and': "and",
        'references': "References",
        'reference': "Reference",
        'navigation': "Navigation",
        'full_reference_list_title': "Full Reference List",
        'last_year': "Last Year",
        'years': "years",
        'no_identifier': "No identifier",
        'propose_reviewers': "🔍 Propose potential reviewers",
        'propose_reviewers_help': "Identify qualified reviewers from cited authors (max 30, max 3 per affiliation)",
        'potential_reviewers': "👥 Potential Reviewers",
        'reviewer_confidential_banner': "CONFIDENTIAL: This report is intended for editorial use only and must not be shared with reviewers or authors.",
        'fetching_orcid_profiles': "🔍 Fetching ORCID profiles for potential reviewers...",
        'orcid_profile_not_public': "ORCID profile is not public or not found",
        'orcid_other_ids': "Other identifiers",
        'orcid_websites': "Websites & social links",
        'orcid_country': "Country",
        'reviewer_affiliations': "Affiliations",
        'reviewer_from_reference': "Cited in reference",
        'reviewer_year': "Publication year",
        'reviewer_no_orcid': "No ORCID available",
        'reviewer_no_affiliation': "Affiliation not specified",
        
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
        'non_journal_sources_with_doi': "📚 Non-journal Sources with DOI",
        'non_journal_sources_with_doi_desc': "Preprints, repositories, conference proceedings, and e-books that have valid DOIs",
        'url_sources': "🔗 URL Sources (Web links without DOI)",
        'problematic_refs': "⚠️ Problematic References",
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
        'only_preprint_repository': "📚 Preprint/Repository only",
        'only_books': "📖 Books only",
        'only_proceedings': "📊 Proceedings only",
        'only_retracted': "⚠️ Retracted only",
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
        'repository': "Repository",
        'ebook': "Electronic book",
        'proceedings': "Conference proceedings",
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
        
        # New identifier coverage strings
        'preprint_repository_count': "📚 Preprint/Repository",
        'books_count': "📖 Books",
        'proceedings_count': "📊 Proceedings",
        'retracted_count': "⚠️ Retracted",
        
        # Export
        'export_report': "📄 Export Enhanced Report",
        'download_html': "💾 Download HTML Report (Expert Edition)",
        'text_export': "📋 Text Export",
        'copy_to_clipboard': "📋 Copy to clipboard",
        'copied': "✅ Data copied! (use Ctrl+C)",
        'run_analysis_first': "👈 Please run analysis in 'Data Upload' tab first",
        'upload_first': "👈 Please upload a reference list in the 'Data Upload' tab and click 'Start Enhanced Analysis'",
        
        # HTML Report
        'html_overview': "Overview",
        'html_identifier_coverage': "Identifier Coverage",
        'html_authors': "Authors",
        'html_journals': "Journals",
        'html_publishers': "Publishers",
        'html_yearly': "Yearly Statistics",
        'html_concepts': "Concepts",
        'html_geography': "Geography",
        'html_collaborations': "Collaborations",
        'html_diversity': "Diversity",
        'html_classics': "Citation Classics",
        'html_self_citations': "Self-Citations",
        'html_crossref_only': "Only Crossref",
        'html_openalex_only': "Only OpenAlex",
        'html_suspicious_doi': "Suspicious DOIs",
        'html_non_doi': "Non-DOI Sources",
        'html_non_journal_sources_with_doi': "Non-journal Sources with DOI",
        'html_url_sources': "URL Sources",
        'html_problems': "Problems",
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
        'html_citations_label': "references",
        'html_total_self_citations': "Total self-citations",
        'html_attention': "⚠️ Attention: invalid/suspicious DOI",
        'html_not_found': "Not found",
        'html_works': "works",
        'html_journal_label': "Journal",
        'html_article_number_label': "Article number",
        'html_self_citation_authors_label': "Paper authors for self-citation analysis",
        'html_repository_note': "📚 Repository source (not invalid)",
        'html_proceedings_note': "📊 Conference proceedings (not invalid)",
        'html_ebook_note': "📖 Electronic book",
        
        # Geography section strings
        'geography_type_1': "Type 1: Unique Countries per Reference (Collaboration Level)",
        'geography_type_1_desc': "Each reference counted once per unique country (e.g., 4 authors from RU → 1 RU; 2 CN + 2 RU → 1 CN, 1 RU)",
        'geography_type_2': "Type 2: Authors per Country (Individual Distribution)",
        'geography_type_2_desc': "Each author counted separately (e.g., 4 authors from RU → 4 RU; 2 CN + 2 RU → 2 CN, 2 RU)",
        'geography_type_3': "Type 3: Collaboration Patterns",
        'geography_type_3_desc': "Distribution of single-country vs international collaborations",
        'single_country': "Single country",
        'international_collab': "International collaboration",
        'collaboration_matrix': "Collaboration matrix (country pairs)",
        'all_authors_affiliations': "All Author Affiliations",
        'all_affiliations': "All affiliations",
        'all_countries': "All countries",
        'num_affiliations': "Number of affiliations",
        'num_countries': "Number of countries",
        'affiliation': "Affiliation",
        
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
        'journal_name_label': "📝 Название журнала",
        'journal_name_help': "Если не указано, будет использовано 'Chimica Techno Acta'",
        'article_number_label': "🔢 Номер статьи",
        'article_number_help': "Пример: 1224, CTA-1234, CTA/1224",
        'duplicate_references_title': "Дублирующиеся ссылки (полное совпадение DOI)",
        'full_doi_match': "Полное совпадение DOI",
        'and': "и",
        'references': "Ссылки",
        'reference': "Ссылка",
        'navigation': "Навигация",
        'full_reference_list_title': "Полный список литературы",
        'last_year': "Последний год",
        'years': "лет",
        'no_identifier': "Нет идентификатора",
        'propose_reviewers': "🔍 Предложить потенциальных рецензентов",
        'propose_reviewers_help': "Выявить квалифицированных рецензентов из цитируемых авторов (макс. 30, не более 3 от одной аффилиации)",
        'potential_reviewers': "👥 Потенциальные рецензенты",
        'reviewer_confidential_banner': "КОНФИДЕНЦИАЛЬНО: Этот отчет предназначен только для редакционного использования и не подлежит распространению среди рецензентов или авторов.",
        'fetching_orcid_profiles': "🔍 Загрузка профилей ORCID для потенциальных рецензентов...",
        'orcid_profile_not_public': "Профиль ORCID не публичен или не найден",
        'orcid_other_ids': "Другие идентификаторы",
        'orcid_websites': "Веб-сайты и профили",
        'orcid_country': "Страна",
        'reviewer_affiliations': "Аффилиации",
        'reviewer_from_reference': "Цитируется в ссылке",
        'reviewer_year': "Год публикации",
        'reviewer_no_orcid': "ORCID не указан",
        'reviewer_no_affiliation': "Аффилиация не указана",
        
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
        'non_journal_sources_with_doi': "📚 Источники не из журналов с DOI",
        'non_journal_sources_with_doi_desc': "Препринты, репозитории, материалы конференций и электронные книги, имеющие валидные DOI",
        'url_sources': "🔗 Источники с URL (веб-ссылки без DOI)",
        'problematic_refs': "⚠️ Проблемные ссылки",
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
        'only_preprint_repository': "📚 Только препринты/репозитории",
        'only_books': "📖 Только книги",
        'only_proceedings': "📊 Только материалы конференций",
        'only_retracted': "⚠️ Только отозванные",
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
        'repository': "Репозиторий",
        'ebook': "Электронная книга",
        'proceedings': "Материалы конференций",
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
        
        # New identifier coverage strings
        'preprint_repository_count': "📚 Препринты/Репозитории",
        'books_count': "📖 Книги",
        'proceedings_count': "📊 Материалы конференций",
        'retracted_count': "⚠️ Отозванные",
        
        # Export
        'export_report': "📄 Экспорт расширенного отчета",
        'download_html': "💾 Скачать HTML отчет (Expert Edition)",
        'text_export': "📋 Текстовый экспорт",
        'copy_to_clipboard': "📋 Копировать в буфер",
        'copied': "✅ Данные скопированы! (используйте Ctrl+C)",
        'run_analysis_first': "👈 Сначала запустите анализ на вкладке 'Загрузка данных'",
        'upload_first': "👈 Загрузите список литературы на вкладке 'Загрузка данных' и нажмите 'Запустить расширенный анализ'",
        
        # HTML Report
        'html_overview': "Обзор",
        'html_identifier_coverage': "Покрытие идентификаторами",
        'html_authors': "Авторы",
        'html_journals': "Журналы",
        'html_publishers': "Издательства",
        'html_yearly': "Годовая статистика",
        'html_concepts': "Концепции",
        'html_geography': "География",
        'html_collaborations': "Сотрудничество",
        'html_diversity': "Разнообразие",
        'html_classics': "Классики цитирования",
        'html_self_citations': "Самоцитирования",
        'html_crossref_only': "Только Crossref",
        'html_openalex_only': "Только OpenAlex",
        'html_suspicious_doi': "Подозрительные DOI",
        'html_non_doi': "Источники без DOI",
        'html_non_journal_sources_with_doi': "Источники не из журналов с DOI",
        'html_url_sources': "URL-источники",
        'html_problems': "Проблемы",
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
        'html_citations_label': "ссылок",
        'html_total_self_citations': "Всего самоцитирований",
        'html_attention': "⚠️ Внимание: недействительный/подозрительный DOI",
        'html_not_found': "Не найден",
        'html_works': "работ",
        'html_journal_label': "Журнал",
        'html_article_number_label': "Номер статьи",
        'html_self_citation_authors_label': "Авторы статьи для анализа самоцитирований",
        'html_repository_note': "📚 Источник из репозитория (не невалидный)",
        'html_proceedings_note': "📊 Материалы конференции (не невалидные)",
        'html_ebook_note': "📖 Электронная книга",
        
        # Geography section strings
        'geography_type_1': "Тип 1: Уникальные страны по ссылке (уровень коллаборации)",
        'geography_type_1_desc': "Каждая ссылка учитывается один раз на уникальную страну (например, 4 автора из RU → 1 RU; 2 CN + 2 RU → 1 CN, 1 RU)",
        'geography_type_2': "Тип 2: Авторы по странам (индивидуальное распределение)",
        'geography_type_2_desc': "Каждый автор учитывается отдельно (например, 4 автора из RU → 4 RU; 2 CN + 2 RU → 2 CN, 2 RU)",
        'geography_type_3': "Тип 3: Паттерны коллабораций",
        'geography_type_3_desc': "Распределение внутристрановых и международных коллабораций",
        'single_country': "Одна страна",
        'international_collab': "Международная коллаборация",
        'collaboration_matrix': "Матрица коллабораций (пары стран)",
        'all_authors_affiliations': "Все аффилиации авторов",
        'all_affiliations': "Все аффилиации",
        'all_countries': "Все страны",
        'num_affiliations': "Количество аффилиаций",
        'num_countries': "Количество стран",
        'affiliation': "Аффилиация",
        
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

# Initialize ORCID cache in session state
if 'orcid_cache' not in st.session_state:
    st.session_state.orcid_cache = {}

# Initialize show reviewers flag
if 'show_reviewers' not in st.session_state:
    st.session_state.show_reviewers = False

# ======================== COUNTRY CODES MAPPING ========================
COUNTRY_CODES = {
    'USA': 'US', 'United States': 'US', 'US': 'US',
    'United Kingdom': 'GB', 'UK': 'GB', 'Great Britain': 'GB',
    'Germany': 'DE', 'Deutschland': 'DE',
    'France': 'FR', 'France': 'FR',
    'China': 'CN', "People's Republic of China": 'CN', 'PR China': 'CN',
    'Japan': 'JP', 'Japan': 'JP',
    'Canada': 'CA', 'Canada': 'CA',
    'Australia': 'AU', 'Australia': 'AU',
    'Italy': 'IT', 'Italia': 'IT',
    'Spain': 'ES', 'España': 'ES',
    'Russia': 'RU', 'Russian Federation': 'RU', 'Россия': 'RU', 'Russian': 'RU',
    'India': 'IN', 'India': 'IN',
    'Brazil': 'BR', 'Brasil': 'BR',
    'South Korea': 'KR', 'Korea, Republic of': 'KR', 'Korea': 'KR',
    'Netherlands': 'NL', 'The Netherlands': 'NL',
    'Switzerland': 'CH', 'Switzerland': 'CH',
    'Sweden': 'SE', 'Sweden': 'SE',
    'Norway': 'NO', 'Norway': 'NO',
    'Denmark': 'DK', 'Denmark': 'DK',
    'Finland': 'FI', 'Finland': 'FI',
    'Austria': 'AT', 'Austria': 'AT',
    'Belgium': 'BE', 'Belgium': 'BE',
    'Poland': 'PL', 'Poland': 'PL',
    'Portugal': 'PT', 'Portugal': 'PT',
    'Greece': 'GR', 'Greece': 'GR',
    'Turkey': 'TR', 'Türkiye': 'TR',
    'Israel': 'IL', 'Israel': 'IL',
    'Singapore': 'SG', 'Singapore': 'SG',
    'Taiwan': 'TW', 'Taiwan, Province of China': 'TW',
    'Hong Kong': 'HK', 'Hong Kong SAR': 'HK',
    'Mexico': 'MX', 'Mexico': 'MX',
    'Argentina': 'AR', 'Argentina': 'AR',
    'Chile': 'CL', 'Chile': 'CL',
    'Colombia': 'CO', 'Colombia': 'CO',
    'Ukraine': 'UA', 'Ukraine': 'UA',
    'Czech Republic': 'CZ', 'Czechia': 'CZ',
    'Hungary': 'HU', 'Hungary': 'HU',
    'Romania': 'RO', 'Romania': 'RO',
    'Bulgaria': 'BG', 'Bulgaria': 'BG',
    'Serbia': 'RS', 'Serbia': 'RS',
    'Croatia': 'HR', 'Croatia': 'HR',
    'Slovakia': 'SK', 'Slovakia': 'SK',
    'Slovenia': 'SI', 'Slovenia': 'SI',
    'Lithuania': 'LT', 'Lithuania': 'LT',
    'Latvia': 'LV', 'Latvia': 'LV',
    'Estonia': 'EE', 'Estonia': 'EE',
    'Ireland': 'IE', 'Ireland': 'IE',
    'New Zealand': 'NZ', 'New Zealand': 'NZ',
    'South Africa': 'ZA', 'South Africa': 'ZA',
    'Egypt': 'EG', 'Egypt': 'EG',
    'Saudi Arabia': 'SA', 'Saudi Arabia': 'SA',
    'United Arab Emirates': 'AE', 'UAE': 'AE',
    'Qatar': 'QA', 'Qatar': 'QA',
    'Iran': 'IR', 'Iran, Islamic Republic of': 'IR',
    'Pakistan': 'PK', 'Pakistan': 'PK',
    'Bangladesh': 'BD', 'Bangladesh': 'BD',
    'Vietnam': 'VN', 'Viet Nam': 'VN',
    'Thailand': 'TH', 'Thailand': 'TH',
    'Malaysia': 'MY', 'Malaysia': 'MY',
    'Indonesia': 'ID', 'Indonesia': 'ID',
    'Philippines': 'PH', 'Philippines': 'PH',
    'Kazakhstan': 'KZ', 'Kazakhstan': 'KZ',
    'Belarus': 'BY', 'Belarus': 'BY',
    'Uzbekistan': 'UZ', 'Uzbekistan': 'UZ',
    'Azerbaijan': 'AZ', 'Azerbaijan': 'AZ',
    'Georgia': 'GE', 'Georgia': 'GE',
    'Armenia': 'AM', 'Armenia': 'AM',
    'Moldova': 'MD', 'Moldova': 'MD',
    'Kyrgyzstan': 'KG', 'Kyrgyzstan': 'KG',
    'Tajikistan': 'TJ', 'Tajikistan': 'TJ',
    'Turkmenistan': 'TM', 'Turkmenistan': 'TM',
    'Mongolia': 'MN', 'Mongolia': 'MN',
}

# ======================== COLORED PROGRESS BAR ========================
def update_colored_progress(progress_percent: float, success_rate: float = None, data_density: float = None):
    """Update progress bar with theme colors"""
    
    primary_color = st.session_state.get('primary_color', '#667eea')
    secondary_color = st.session_state.get('secondary_color', get_complementary_color(primary_color))
    
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
            {primary_color} 0%, 
            {secondary_color} 50%,
            {primary_color} 100%);
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
    .badge-repository {
        background: #e2d5f8;
        color: #5e2a9e;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-book {
        background: #d4f1e9;
        color: #0e6b5e;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-proceedings {
        background: #fff2c9;
        color: #b26b00;
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
    
    /* Ebook highlight (non-gray background) */
    .ebook-reference {
        background: #d4f1e9 !important;
        border-left: 3px solid #0e6b5e !important;
    }
    
    /* Repository reference styling */
    .repository-reference {
        background: #e2d5f8 !important;
        border-left: 3px solid #5e2a9e !important;
    }
    
    /* Proceedings reference styling */
    .proceedings-reference {
        background: #fff2c9 !important;
        border-left: 3px solid #b26b00 !important;
    }
    
    /* Reviewer card styles */
    .reviewer-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
    .reviewer-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .reviewer-name {
        font-size: 18px;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 8px;
    }
    .reviewer-orcid {
        font-family: monospace;
        font-size: 12px;
        margin-bottom: 8px;
    }
    .reviewer-section-title {
        font-weight: 600;
        margin-top: 12px;
        margin-bottom: 6px;
        font-size: 13px;
        color: #555;
    }
    .external-id-link {
        display: inline-block;
        background: #f0f0f0;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        margin: 3px;
        text-decoration: none;
        color: #333;
        transition: all 0.2s;
    }
    .external-id-link:hover {
        background: #667eea;
        color: white;
    }
    .confidential-banner {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #dc3545;
        padding: 12px 20px;
        margin-bottom: 20px;
        border-radius: 8px;
        font-weight: 500;
        color: #856404;
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

# ======================== NEW: ORCID API FUNCTIONS ========================

def clean_orcid_id(orcid_input: str) -> Optional[str]:
    """Clean and format ORCID ID"""
    if not orcid_input:
        return None
    
    orcid_clean = orcid_input.strip().replace("https://orcid.org/", "").replace("http://orcid.org/", "")
    parts = orcid_clean.split('-')
    if len(parts) == 4 and all(len(part) == 4 for part in parts):
        return orcid_clean
    # Also accept format without dashes
    if len(orcid_clean) == 16 and orcid_clean[:4].isdigit() and orcid_clean[4:8].isdigit():
        return f"{orcid_clean[:4]}-{orcid_clean[4:8]}-{orcid_clean[8:12]}-{orcid_clean[12:16]}"
    return None

def fetch_orcid_profile_data(orcid_id: str) -> Optional[Dict]:
    """Fetch ORCID profile data from public API"""
    if not orcid_id:
        return None
    
    # Check cache first
    if orcid_id in st.session_state.orcid_cache:
        return st.session_state.orcid_cache[orcid_id]
    
    clean_id = clean_orcid_id(orcid_id)
    if not clean_id:
        return None
    
    url = f"https://pub.orcid.org/v3.0/{clean_id}"
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Cache the result
        st.session_state.orcid_cache[orcid_id] = data
        return data
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None

def extract_personal_info_from_orcid(profile_data: Dict) -> Dict:
    """Extract personal information from ORCID profile"""
    if not profile_data or 'person' not in profile_data:
        return {}
    
    person = profile_data.get('person', {})
    if person is None:
        return {}
    
    info = {}
    
    # Name section
    name = person.get('name')
    if name and isinstance(name, dict):
        given_names = name.get('given-names')
        info['given_names'] = given_names.get('value', '') if given_names and isinstance(given_names, dict) else ''
        
        family_name = name.get('family-name')
        info['family_name'] = family_name.get('value', '') if family_name and isinstance(family_name, dict) else ''
        
        credit_name = name.get('credit-name')
        info['credit_name'] = credit_name.get('value', '') if credit_name and isinstance(credit_name, dict) else ''
    else:
        info['given_names'] = ''
        info['family_name'] = ''
        info['credit_name'] = ''
    
    # Biography
    bio = person.get('biography')
    info['biography'] = bio.get('value', '') if bio and isinstance(bio, dict) else ''
    
    # Country
    addresses = person.get('addresses')
    if addresses and isinstance(addresses, dict):
        address_list = addresses.get('address', [])
        if address_list and len(address_list) > 0:
            first_address = address_list[0]
            if isinstance(first_address, dict):
                country = first_address.get('country')
                info['country'] = country.get('value', '') if country and isinstance(country, dict) else ''
            else:
                info['country'] = ''
        else:
            info['country'] = ''
    else:
        info['country'] = ''
    
    # Keywords
    keywords = person.get('keywords')
    if keywords and isinstance(keywords, dict):
        keyword_list = keywords.get('keyword', [])
        info['keywords'] = [k.get('content', '') for k in keyword_list if isinstance(k, dict)] if keyword_list else []
    else:
        info['keywords'] = []
    
    # Researcher URLs
    researcher_urls = person.get('researcher-urls')
    if researcher_urls and isinstance(researcher_urls, dict):
        url_list = researcher_urls.get('researcher-url', [])
        info['researcher_urls'] = []
        for url_item in url_list:
            if isinstance(url_item, dict):
                url_name = url_item.get('url-name', '')
                url_value = url_item.get('url', {}).get('value', '')
                if url_value:
                    info['researcher_urls'].append({'name': url_name, 'url': url_value})
    else:
        info['researcher_urls'] = []
    
    # External identifiers with hyperlinks
    external_ids = person.get('external-identifiers')
    info['external_ids'] = {}
    
    id_url_patterns = {
        'scopus-author-id': 'https://www.scopus.com/authid/detail.uri?authorId={}',
        'researcher-id': 'http://www.researcherid.com/rid/{}',
        'publons': 'https://publons.com/researcher/{}',
        'loop': 'https://loop.frontiersin.org/people/{}',
        'linkedin': 'https://www.linkedin.com/in/{}/',
        'researchgate': 'https://www.researchgate.net/profile/{}',
        'google-scholar': 'https://scholar.google.com/citations?user={}',
        'wos-researcherid': 'https://www.webofscience.com/wos/author/rid/{}',
        'arxiv': 'https://arxiv.org/a/{}',
        'ssrn': 'https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id={}',
        'orcid': 'https://orcid.org/{}',
    }
    
    if external_ids and isinstance(external_ids, dict):
        ext_id_list = external_ids.get('external-identifier', [])
        for ext_id in ext_id_list:
            if isinstance(ext_id, dict):
                id_type = ext_id.get('external-id-type', '').lower()
                id_value = ext_id.get('external-id-value', '')
                id_url = ext_id.get('external-id-url', {}).get('value', '')
                
                if id_type and id_value:
                    if id_url:
                        info['external_ids'][id_type] = {'value': id_value, 'url': id_url}
                    elif id_type in id_url_patterns:
                        url = id_url_patterns[id_type].format(id_value)
                        info['external_ids'][id_type] = {'value': id_value, 'url': url}
                    else:
                        info['external_ids'][id_type] = {'value': id_value, 'url': None}
    
    return info

# ======================== NEW: AFFILIATION AND AUTHOR EXTRACTION (FROM YOUR CODE) ========================

def extract_country_from_affiliation_string(affiliation_string: str) -> str:
    """
    Extract country from affiliation string (fallback method)
    This is the SAME function from your working code
    """
    if not affiliation_string:
        return "N/A"
    
    affiliation_string = affiliation_string.strip()
    
    known_countries = [
        'USA', 'UK', 'China', 'Germany', 'France', 'Japan', 'Canada', 'Australia',
        'Russia', 'India', 'Brazil', 'Italy', 'Spain', 'South Korea', 'Netherlands',
        'Switzerland', 'Sweden', 'Belgium', 'Norway', 'Denmark', 'Finland',
        'United States', 'United Kingdom', 'Китай', 'США', 'Великобритания', 'Германия', 'Франция'
    ]
    
    parts = [p.strip() for p in affiliation_string.split(',')]
    
    for part in reversed(parts):
        for country in known_countries:
            if country.lower() in part.lower():
                return part
    
    if len(parts) > 1:
        potential_country = parts[-1]
        if len(potential_country) > 2 and not potential_country.isdigit():
            return potential_country
    
    return "Не определена"

def get_authors_with_all_affiliations_from_openalex(openalex_data: Dict) -> List[Dict]:
    """
    Extracts authors with ALL their affiliations from OpenAlex API data.
    This is ADAPTED from your get_authors_with_all_affiliations function.
    Returns list of authors with full affiliation details.
    """
    authors_data = []
    
    if not openalex_data or 'authorships' not in openalex_data:
        return authors_data
    
    for authorship in openalex_data.get('authorships', []):
        author_info = authorship.get('author', {})
        author_name = author_info.get('display_name', 'Unknown')
        orcid = author_info.get('orcid', '')
        
        if not author_name or author_name == 'Unknown':
            continue
        
        institutions = authorship.get('institutions', [])
        
        affiliations_list = []
        countries_set = set()
        
        for inst in institutions:
            affiliation_name = inst.get('display_name', 'Не указана')
            country_code = inst.get('country_code', '')
            
            if not country_code or country_code == 'XX':
                country = extract_country_from_affiliation_string(affiliation_name)
            else:
                # Map country codes to full names (or keep as is)
                country_names = {
                    'US': 'USA', 'GB': 'UK', 'CN': 'China', 'DE': 'Germany',
                    'FR': 'France', 'JP': 'Japan', 'CA': 'Canada', 'AU': 'Australia',
                    'RU': 'Russia', 'IN': 'India', 'BR': 'Brazil', 'IT': 'Italy',
                    'ES': 'Spain', 'KR': 'South Korea', 'NL': 'Netherlands',
                    'CH': 'Switzerland', 'SE': 'Sweden', 'BE': 'Belgium',
                    'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland'
                }
                country = country_names.get(country_code, country_code)
            
            if affiliation_name and affiliation_name != 'Не указана':
                affiliations_list.append({
                    'name': affiliation_name,
                    'country': country
                })
                if country and country not in ['N/A', 'Не указана', 'Не определена']:
                    countries_set.add(country)
        
        # Normalize author name
        compare_name, display_name = normalize_author_name(author_name)
        
        # Format ORCID
        formatted_orcid = format_orcid_id(orcid) if orcid else ''
        
        authors_data.append({
            'author': display_name,
            'compare_name': compare_name,
            'orcid': formatted_orcid,
            'affiliations': affiliations_list,
            'countries': list(countries_set) if countries_set else ['Не указана'],
            'raw_affiliations': [aff['name'] for aff in affiliations_list]
        })
    
    return authors_data

def get_authors_from_crossref_simple(crossref_data: Dict) -> List[Dict]:
    """
    Simple extraction from Crossref WITHOUT aggressive cleaning.
    Used as fallback when OpenAlex returns no data.
    """
    authors_data = []
    
    if not crossref_data or 'author' not in crossref_data:
        return authors_data
    
    for author in crossref_data.get('author', []):
        given = author.get('given', '')
        family = author.get('family', '')
        orcid = author.get('ORCID', None)
        
        if not family:
            continue
        
        raw_name = f"{given} {family}".strip() if given else family
        compare_name, display_name = normalize_author_name(raw_name)
        
        # Extract affiliations from Crossref (without aggressive cleaning)
        affiliations_list = []
        countries_set = set()
        
        if 'affiliation' in author and author['affiliation']:
            for aff in author['affiliation']:
                aff_name = aff.get('name', '')
                if aff_name:
                    country = extract_country_from_affiliation_string(aff_name)
                    affiliations_list.append({
                        'name': aff_name,
                        'country': country
                    })
                    if country and country not in ['N/A', 'Не указана', 'Не определена']:
                        countries_set.add(country)
        
        # Format ORCID
        formatted_orcid = format_orcid_id(orcid) if orcid else ''
        
        authors_data.append({
            'author': display_name,
            'compare_name': compare_name,
            'orcid': formatted_orcid,
            'affiliations': affiliations_list,
            'countries': list(countries_set) if countries_set else ['Не указана']
        })
    
    return authors_data

def merge_authors_with_all_affiliations(all_authors_data: List[Dict]) -> List[Dict]:
    """
    Merge duplicate authors from all references.
    Collects ALL unique affiliations and countries.
    This is ADAPTED from your merge_authors function.
    """
    merged_authors = defaultdict(lambda: {
        'affiliations': set(),
        'countries': set(),
        'mention_count': 0,
        'articles': set(),
        'all_affiliations_details': [],
        'orcid': ''
    })
    
    for article_data in all_authors_data:
        doi = article_data.get('doi', 'unknown')
        for author in article_data.get('authors', []):
            author_name = author.get('author', '')
            if not author_name:
                continue
            
            # Add affiliations (use tuple for set)
            for aff in author.get('affiliations', []):
                aff_tuple = (aff.get('name', ''), aff.get('country', ''))
                merged_authors[author_name]['affiliations'].add(aff_tuple)
                if aff.get('country'):
                    merged_authors[author_name]['countries'].add(aff.get('country'))
                merged_authors[author_name]['all_affiliations_details'].append({
                    'doi': doi,
                    'affiliation': aff.get('name', ''),
                    'country': aff.get('country', '')
                })
            
            merged_authors[author_name]['mention_count'] += 1
            merged_authors[author_name]['articles'].add(doi)
            
            # Store ORCID if available and not already set
            if author.get('orcid') and not merged_authors[author_name]['orcid']:
                merged_authors[author_name]['orcid'] = author['orcid']
    
    # Convert sets back to lists
    result = []
    for author_name, data in merged_authors.items():
        # Find the best display name (most complete)
        display_name = author_name
        # Try to get a better display name from affiliations details
        for detail in data['all_affiliations_details']:
            # This is where we could extract full name, but for now keep as is
            pass
        
        result.append({
            'author': display_name,
            'compare_name': normalize_author_name(display_name)[0],
            'orcid': data['orcid'],
            'mention_count': data['mention_count'],
            'num_articles': len(data['articles']),
            'articles': list(data['articles']),
            'countries': sorted(list(data['countries'])) if data['countries'] else [],
            'num_countries': len(data['countries']),
            'num_affiliations': len(data['affiliations']),
            'affiliations': [{'name': aff[0], 'country': aff[1]} for aff in data['affiliations']],
            'affiliations_details': data['all_affiliations_details']
        })
    
    # Sort by mention count descending
    result.sort(key=lambda x: x['mention_count'], reverse=True)
    return result

# ======================== HELPER FUNCTIONS FOR AUTHOR PROCESSING (UPDATED) ========================

def normalize_author_name(name: str) -> Tuple[str, str]:
    """
    Normalize author name to format {Lastname} {FirstInitial}.
    Returns (compare_name, display_name)
    Example: "Danil E. Matkin" -> ("matkin d.", "Matkin D.")
    Example: "Matkin, Danil E." -> ("matkin d.", "Matkin D.")
    Example: "Medvedev D." -> ("medvedev d.", "Medvedev D.")
    """
    if not name or not isinstance(name, str):
        return "", ""
    
    name = name.strip()
    
    # Handle comma-separated format: "Matkin, Danil E." -> "Matkin D."
    if ',' in name:
        last, first = name.split(',', 1)
        last = last.strip()
        first = first.strip()
        
        # Extract first initial from first name part
        first_initial = ''
        if first:
            # Handle "Danil E." -> take 'D'
            first_parts = first.split()
            for part in first_parts:
                if part and part[0].isalpha():
                    first_initial = part[0].upper()
                    break
        
        display_name = f"{last} {first_initial}." if first_initial else last
        compare_name = f"{last.lower()} {first_initial.lower()}."
        return compare_name, display_name
    
    # Handle "First Last" format: "Danil E. Matkin" -> "Matkin D."
    parts = name.split()
    if len(parts) >= 2:
        last = parts[-1]
        
        # Extract first initial from first part(s)
        first_initial = ''
        for part in parts[:-1]:
            if part and part[0].isalpha():
                first_initial = part[0].upper()
                break
        
        display_name = f"{last} {first_initial}." if first_initial else last
        compare_name = f"{last.lower()} {first_initial.lower()}."
        return compare_name, display_name
    
    # Handle single word (unlikely, but possible)
    if len(parts) == 1:
        display_name = parts[0]
        compare_name = parts[0].lower()
        return compare_name, display_name
    
    # Fallback: return original as-is
    return name.lower(), name

def format_orcid_id(orcid: str) -> str:
    """Format ORCID ID to full URL"""
    if not orcid or not isinstance(orcid, str):
        return ""
    
    if orcid.startswith('https://orcid.org/'):
        return orcid
    
    # Clean ORCID from non-alphanumeric characters except dash
    clean_id = re.sub(r'[^\dXx-]', '', orcid.strip())
    
    if '-' in clean_id:
        # Already has dashes in correct format
        if re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$', clean_id, re.IGNORECASE):
            return f"https://orcid.org/{clean_id}"
    
    # Format without dashes
    if len(clean_id) == 16:
        formatted = f"{clean_id[:4]}-{clean_id[4:8]}-{clean_id[8:12]}-{clean_id[12:]}"
        return f"https://orcid.org/{formatted}"
    elif len(clean_id) == 15 and clean_id[15] in ['X', 'x']:
        formatted = f"{clean_id[:4]}-{clean_id[4:8]}-{clean_id[8:12]}-{clean_id[12:15]}X"
        return f"https://orcid.org/{formatted}"
    else:
        return f"https://orcid.org/{clean_id}"

# ======================== DUPLICATE DETECTION ========================
def find_duplicate_references(references: List[str], threshold: float = 0.85) -> List[Dict]:
    """Find duplicate references in literature list - ONLY Full DOI match"""
    duplicates = []
    seen_dois = {}  # Maps DOI -> index of first occurrence
    
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
                    'doi': doi1,
                    'reason': f'Full DOI match: {doi1}'
                })
            else:
                seen_dois[doi1] = i
    
    # Remove duplicates (same pair might appear multiple times if DOI appears more than twice)
    unique_duplicates = []
    seen_pairs = set()
    for dup in duplicates:
        pair = tuple(sorted([dup['index1'], dup['index2']]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_duplicates.append(dup)
    
    return unique_duplicates

# ======================== NEW: POTENTIAL REVIEWERS LOGIC ========================

def extract_all_authors_from_results(results: List[Dict]) -> List[Dict]:
    """
    Extract all unique authors from results with their affiliations and publication years.
    Returns list of candidate reviewers.
    """
    candidates = []
    seen_authors = set()
    
    for result in results:
        year = result.get('year')
        # Only consider references with valid year within last 4 years
        if year and isinstance(year, (int, float)):
            current_year = datetime.now().year
            if year < current_year - 4:
                continue
        
        for author in result.get('authors', []):
            # Get the normalized name for deduplication
            author_name = author.get('display_name', '')
            compare_name = author.get('compare_name', '')
            
            if not compare_name:
                continue
            
            # Skip if already seen
            if compare_name in seen_authors:
                continue
            
            seen_authors.add(compare_name)
            
            # Get primary affiliation (first one)
            affiliations = author.get('affiliations', [])
            primary_affiliation = affiliations[0]['name'] if affiliations else ''
            primary_country = affiliations[0]['country'] if affiliations else ''
            
            # Get all affiliations as list of names
            all_affiliation_names = [aff['name'] for aff in affiliations]
            all_countries = [aff['country'] for aff in affiliations if aff.get('country')]
            
            candidates.append({
                'name': author_name,
                'compare_name': compare_name,
                'orcid': author.get('orcid', ''),
                'primary_affiliation': primary_affiliation,
                'affiliations': all_affiliation_names,
                'all_affiliation_details': affiliations,
                'countries': list(set(all_countries)),
                'publication_year': year,
                'doi': result.get('doi', ''),
                'reference_text': result.get('original_text', '')[:200]
            })
    
    return candidates

def filter_candidates_by_affiliation(candidates: List[Dict], paper_author_affiliations: Set[str]) -> List[Dict]:
    """
    Filter out candidates who share ANY affiliation with paper authors.
    """
    filtered = []
    for candidate in candidates:
        # Check if candidate has any affiliation that matches paper authors' affiliations
        has_common_affiliation = False
        for aff in candidate.get('affiliations', []):
            if aff in paper_author_affiliations:
                has_common_affiliation = True
                break
        
        if not has_common_affiliation:
            filtered.append(candidate)
    
    return filtered

def filter_candidates_by_self_citation(candidates: List[Dict], paper_authors_norm_set: Set[str]) -> List[Dict]:
    """
    Filter out candidates who are in the paper authors list.
    """
    filtered = []
    for candidate in candidates:
        if candidate['compare_name'] not in paper_authors_norm_set:
            filtered.append(candidate)
    
    return filtered

def limit_candidates_by_affiliation(candidates: List[Dict], max_per_affiliation: int = 3) -> List[Dict]:
    """
    Limit to maximum max_per_affiliation candidates per primary affiliation.
    Prioritize those with ORCID.
    """
    # Group by primary affiliation
    by_affiliation = defaultdict(list)
    for candidate in candidates:
        aff_key = candidate.get('primary_affiliation', 'Unknown')
        by_affiliation[aff_key].append(candidate)
    
    # Sort each group: those with ORCID first
    for aff_key in by_affiliation:
        by_affiliation[aff_key].sort(key=lambda x: (0 if x.get('orcid') else 1, -x.get('publication_year', 0)))
        # Keep only top max_per_affiliation
        by_affiliation[aff_key] = by_affiliation[aff_key][:max_per_affiliation]
    
    # Flatten back to list
    result = []
    for aff_key, candidates_list in by_affiliation.items():
        result.extend(candidates_list)
    
    # Sort final list by publication year (newest first) and then by ORCID presence
    result.sort(key=lambda x: (0 if x.get('orcid') else 1, -x.get('publication_year', 0)))
    
    return result[:30]  # Return top 30

def get_potential_reviewers(results: List[Dict], paper_authors: Set[str], paper_author_affiliations: Set[str]) -> List[Dict]:
    """
    Main function to get potential reviewers based on:
    1. Not self-citation
    2. Different affiliation from paper authors
    3. Publication within last 4 years
    4. Max 30 reviewers, max 3 per affiliation
    """
    # Normalize paper authors for comparison
    paper_authors_norm = set()
    for author in paper_authors:
        norm, _ = normalize_author_name(author)
        paper_authors_norm.add(norm)
    
    # Extract all candidates from results
    all_candidates = extract_all_authors_from_results(results)
    
    # Filter by self-citation
    candidates_no_self = filter_candidates_by_self_citation(all_candidates, paper_authors_norm)
    
    # Filter by affiliation
    candidates_no_affiliation_overlap = filter_candidates_by_affiliation(candidates_no_self, paper_author_affiliations)
    
    # Limit by affiliation (max 3 per affiliation)
    final_candidates = limit_candidates_by_affiliation(candidates_no_affiliation_overlap, max_per_affiliation=3)
    
    return final_candidates

def fetch_orcid_profiles_for_reviewers(reviewers: List[Dict]) -> List[Dict]:
    """
    Fetch ORCID profiles for reviewers in parallel with progress bar.
    """
    if not reviewers:
        return reviewers
    
    # Filter reviewers who have ORCID
    reviewers_with_orcid = [r for r in reviewers if r.get('orcid')]
    
    if not reviewers_with_orcid:
        return reviewers
    
    # Progress bar placeholder
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    status_placeholder.markdown(f"🔍 {get_text('fetching_orcid_profiles')}")
    
    # Process in parallel
    enriched_reviewers = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for i, reviewer in enumerate(reviewers):
            if reviewer.get('orcid'):
                orcid_clean = clean_orcid_id(reviewer['orcid'])
                if orcid_clean:
                    future = executor.submit(fetch_orcid_profile_data, orcid_clean)
                    futures[future] = i
        
        # Update progress
        total = len(futures)
        completed = 0
        
        for future in as_completed(futures):
            idx = futures[future]
            orcid_data = future.result()
            completed += 1
            
            # Update progress bar
            progress_percent = (completed / total) * 100 if total > 0 else 0
            progress_placeholder.progress(progress_percent / 100)
            
            if orcid_data:
                personal_info = extract_personal_info_from_orcid(orcid_data)
                reviewers[idx]['orcid_profile'] = personal_info
            else:
                reviewers[idx]['orcid_profile'] = None
    
    # Clear progress placeholders
    progress_placeholder.empty()
    status_placeholder.empty()
    
    return reviewers

def display_reviewer_card(reviewer: Dict, index: int):
    """
    Display a reviewer card with ORCID profile information.
    """
    primary_color = st.session_state.get('primary_color', '#667eea')
    
    # Get ORCID profile data
    orcid_profile = reviewer.get('orcid_profile', {})
    orcid_id = reviewer.get('orcid', '')
    
    # Build name
    given_names = orcid_profile.get('given_names', '')
    family_name = orcid_profile.get('family_name', '')
    credit_name = orcid_profile.get('credit_name', '')
    
    if given_names and family_name:
        full_name = f"{given_names} {family_name}"
    elif credit_name:
        full_name = credit_name
    else:
        full_name = reviewer.get('name', 'Unknown')
    
    # ORCID link
    orcid_html = ""
    if orcid_id:
        orcid_url = format_orcid_id(orcid_id) if not orcid_id.startswith('http') else orcid_id
        orcid_html = f'<div class="reviewer-orcid"><strong>ORCID:</strong> <a href="{orcid_url}" target="_blank" style="color: {primary_color};">{orcid_id}</a></div>'
    else:
        orcid_html = f'<div class="reviewer-orcid"><em>{get_text("reviewer_no_orcid")}</em></div>'
    
    # Country from ORCID
    country = orcid_profile.get('country', '')
    if not country and reviewer.get('countries'):
        country = ', '.join(reviewer['countries'][:3])
    
    country_html = f'<div><strong>{get_text("orcid_country")}:</strong> {country}</div>' if country else ''
    
    # Affiliations
    affiliations = reviewer.get('affiliations', [])
    affiliations_html = ""
    if affiliations:
        aff_list = []
        for aff in affiliations[:3]:
            if isinstance(aff, dict):
                aff_list.append(aff.get('name', ''))
            else:
                aff_list.append(aff)
        affiliations_html = f'<div><strong>{get_text("reviewer_affiliations")}:</strong><br>{", ".join(aff_list)}</div>'
    else:
        affiliations_html = f'<div><em>{get_text("reviewer_no_affiliation")}</em></div>'
    
    # External IDs (Other IDs)
    external_ids = orcid_profile.get('external_ids', {})
    external_ids_html = ""
    if external_ids:
        friendly_names = {
            'scopus-author-id': 'Scopus Author ID',
            'researcher-id': 'ResearcherID (WoS)',
            'wos-researcherid': 'Web of Science ResearcherID',
            'publons': 'Publons',
            'loop': 'Loop',
            'linkedin': 'LinkedIn',
            'researchgate': 'ResearchGate',
            'google-scholar': 'Google Scholar',
            'arxiv': 'arXiv',
            'ssrn': 'SSRN',
        }
        id_links = []
        for id_type, id_info in external_ids.items():
            display_name = friendly_names.get(id_type, id_type.replace('-', ' ').title())
            id_value = id_info.get('value', '')
            id_url = id_info.get('url', '')
            if id_url:
                display_value = id_value[:30] + '...' if len(id_value) > 30 else id_value
                id_links.append(f'<a href="{id_url}" target="_blank" class="external-id-link">{display_name}</a>')
            elif id_value:
                id_links.append(f'<span class="external-id-link">{display_name}: {id_value[:20]}</span>')
        
        if id_links:
            external_ids_html = f'<div class="reviewer-section-title">{get_text("orcid_other_ids")}:</div><div>{" ".join(id_links)}</div>'
    
    # Websites
    researcher_urls = orcid_profile.get('researcher_urls', [])
    websites_html = ""
    if researcher_urls:
        url_links = []
        for url_info in researcher_urls[:5]:
            url_name = url_info.get('name', 'Website')
            url_value = url_info.get('url', '')
            if url_value:
                url_links.append(f'<a href="{url_value}" target="_blank" class="external-id-link">{url_name}</a>')
        if url_links:
            websites_html = f'<div class="reviewer-section-title">{get_text("orcid_websites")}:</div><div>{" ".join(url_links)}</div>'
    
    # Publication info
    pub_html = f'<div style="margin-top: 12px; font-size: 12px; color: #666;"><strong>{get_text("reviewer_from_reference")}:</strong> {reviewer.get("doi", "N/A")}<br><strong>{get_text("year")}:</strong> {reviewer.get("publication_year", "Unknown")}</div>'
    
    # Keywords/Research interests
    keywords = orcid_profile.get('keywords', [])
    keywords_html = ""
    if keywords:
        keywords_str = ', '.join(keywords[:5])
        keywords_html = f'<div><strong>Research interests:</strong> {keywords_str}</div>'
    
    # Biography (truncated)
    bio = orcid_profile.get('biography', '')
    bio_html = ""
    if bio:
        bio_truncated = bio[:200] + '...' if len(bio) > 200 else bio
        bio_html = f'<div style="margin-top: 8px; font-size: 12px; color: #555;"><em>{bio_truncated}</em></div>'
    
    # Render card
    st.markdown(f"""
    <div class="reviewer-card">
        <div class="reviewer-name">{index}. {full_name}</div>
        {orcid_html}
        {country_html}
        {affiliations_html}
        {keywords_html}
        {external_ids_html}
        {websites_html}
        {pub_html}
        {bio_html}
    </div>
    """, unsafe_allow_html=True)

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
    """
    Geographic analysis with THREE types using CORRECT country extraction.
    Uses structured data from OpenAlex API as the PRIMARY source.
    This matches the working reference code logic.
    """
    
    # Type 1: Unique countries per reference (collaboration level)
    country_single_counter = Counter()  # Each reference counted once per unique country
    country_combined_counter = Counter()  # Country combinations for collaboration analysis
    
    # Type 2: Authors per country (individual distribution)
    author_country_counter = Counter()
    
    # Track per-reference data
    reference_countries = []  # List of country sets per reference
    
    for result in results:
        # Collect all countries from authors in this reference
        ref_countries_set = set()
        
        # Get authors from result (already processed with new affiliation logic)
        for author in result.get('authors', []):
            # Try author.get('countries') - from the new extraction
            countries = author.get('countries', [])
            
            for country in countries:
                if country and country not in ['N/A', 'Не указана', 'Не определена']:
                    ref_countries_set.add(country)
                    # Type 2: Count each author by their country
                    author_country_counter[country] += 1
        
        if ref_countries_set:
            # Type 1: Count each reference once per unique country
            for country in ref_countries_set:
                country_single_counter[country] += 1
            
            # Type 3: Track collaboration patterns
            sorted_countries = sorted(ref_countries_set)
            if len(sorted_countries) == 1:
                # Single country collaboration
                country_combined_counter[sorted_countries[0]] += 1
            else:
                # International collaboration
                combination = ';'.join(sorted_countries)
                country_combined_counter[combination] += 1
            
            reference_countries.append(ref_countries_set)
        else:
            reference_countries.append(set())
    
    # Prepare Type 1 results (single country counts per reference)
    type1_data = []
    for country, count in country_single_counter.most_common():
        type1_data.append({'Country': country, 'Type': 'single', 'Count': count})
    
    # Prepare Type 2 results (authors per country)
    type2_data = []
    for country, count in author_country_counter.most_common():
        type2_data.append({'Country': country, 'Type': 'authors', 'Count': count})
    
    # Prepare Type 3 results (collaboration patterns)
    type3_data = []
    for pattern, count in country_combined_counter.most_common():
        if ';' in pattern:
            type3_data.append({'Country': pattern, 'Type': 'combined', 'Count': count})
    
    # Calculate collaboration statistics
    single_country_count = 0
    international_count = 0
    
    for pattern, count in country_combined_counter.items():
        if ';' not in pattern:
            single_country_count += count
        else:
            international_count += count
    
    # Prepare collaboration matrix (country pairs)
    country_pair_counter = Counter()
    for ref_countries in reference_countries:
        if len(ref_countries) > 1:
            sorted_countries = sorted(ref_countries)
            for i in range(len(sorted_countries)):
                for j in range(i + 1, len(sorted_countries)):
                    pair = tuple(sorted([sorted_countries[i], sorted_countries[j]]))
                    country_pair_counter[pair] += 1
    
    collaboration_matrix = []
    for (c1, c2), count in country_pair_counter.most_common(20):
        collaboration_matrix.append({
            'country1': c1,
            'country2': c2,
            'count': count
        })
    
    return {
        'geographic_data': type1_data + type3_data,
        'type1_unique_countries_per_reference': dict(country_single_counter.most_common()),
        'type2_authors_per_country': dict(author_country_counter.most_common()),
        'type3_collaboration_patterns': dict(country_combined_counter.most_common()),
        'single_country_count': single_country_count,
        'international_count': international_count,
        'collaboration_matrix': collaboration_matrix,
        'total_references_with_country': len([rc for rc in reference_countries if rc]),
        'total_references': len(results),
        'total_authors_with_country': sum(author_country_counter.values())
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
    """Analyze yearly statistics with 3/5/10 year lookback and LAST YEAR (completed full year)"""
    current_year = datetime.now().year
    # Last completed full year (e.g., 2025 if we are in 2026)
    last_completed_year = current_year - 1
    
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
    
    # Calculate last completed year statistics
    last_year_count = year_counts.get(last_completed_year, 0)
    last_year_percent = (last_year_count / total_refs * 100) if total_refs > 0 else 0
    
    # Calculate last N years statistics
    last_3_years = sum(year_counts.get(y, 0) for y in range(current_year - 2, current_year + 1))
    last_5_years = sum(year_counts.get(y, 0) for y in range(current_year - 4, current_year + 1))
    last_10_years = sum(year_counts.get(y, 0) for y in range(current_year - 9, current_year + 1))
    
    return {
        'yearly_counts': year_counts,
        'yearly_percentages': year_percentages,
        'cumulative_percentages': cumulative,
        'last_year': last_year_count,
        'last_year_percent': last_year_percent,
        'last_completed_year': last_completed_year,
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
    """Analyze what types of identifiers each reference has - IMPROVED VERSION with independent checks"""
    identifier_stats = {
        'has_doi': 0,
        'has_url': 0,
        'has_arxiv': 0,
        'has_pmid': 0,
        'has_isbn': 0,
        'has_none': 0,
        'multiple': 0,
        
        # NEW: Separate counters for different source types
        'is_preprint_repository': 0,    # OpenAlex type 'repository' or 'posted_content' OR arXiv ID
        'is_ebook_platform': 0,          # OpenAlex type 'ebook platform' OR raw_type 'book-chapter'
        'is_proceedings': 0,              # OpenAlex raw_type 'proceedings-article'
        'is_retracted': 0,               # OpenAlex is_retracted == True
        'is_book_no_doi': 0              # ISBN present but no DOI
    }
    
    references_without_any = []
    references_with_only_url = []
    references_without_doi = []
    
    for result in results:
        text = result.get('original_text', '')
        identifiers = extract_identifiers(text)
        
        has_any = False
        count = 0
        
        # ========== REPOSITORY / PREPRINT DETECTION - INDEPENDENT CHECK ==========
        # Check is_repository flag OR arXiv ID in text
        if result.get('is_repository', False) or identifiers.get('arxiv'):
            identifier_stats['is_preprint_repository'] += 1
        
        # ========== EBOOK PLATFORM DETECTION - INDEPENDENT CHECK ==========
        if result.get('is_ebook', False):
            identifier_stats['is_ebook_platform'] += 1
        
        # ========== PROCEEDINGS DETECTION - INDEPENDENT CHECK ==========
        if result.get('is_proceedings', False):
            identifier_stats['is_proceedings'] += 1
        
        # ========== RETRACTION DETECTION - INDEPENDENT CHECK ==========
        if result.get('is_retracted', False):
            identifier_stats['is_retracted'] += 1
        
        # ========== BOOK WITH ISBN BUT NO DOI - INDEPENDENT CHECK ==========
        if identifiers.get('isbn') and not identifiers.get('doi'):
            identifier_stats['is_book_no_doi'] += 1
        
        # ========== STANDARD IDENTIFIERS ==========
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
            references_without_any.append(text[:200])
        
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
    """Analyze publisher frequency - now works correctly with OpenAlex data"""
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
    """
    Analyze author frequency with PROPER merging using the new affiliation logic.
    Uses the merged authors from the new system.
    """
    # Collect all author occurrences with full affiliation data
    all_authors_data = []
    
    for result in results:
        doi = result.get('doi', 'unknown')
        authors = result.get('authors', [])
        
        all_authors_data.append({
            'doi': doi,
            'authors': authors
        })
    
    # Merge using the new merge function
    merged_authors = merge_authors_with_all_affiliations(all_authors_data)
    
    # Convert to the format expected by the UI
    author_list = []
    for author in merged_authors:
        # Get primary institution (first affiliation)
        primary_institution = author['affiliations'][0]['name'] if author['affiliations'] else ''
        primary_country = author['countries'][0] if author['countries'] else ''
        
        author_list.append({
            'display_name': author['author'],
            'compare_name': author['compare_name'],
            'orcid': author.get('orcid', ''),
            'count': author['mention_count'],
            'country': primary_country,
            'countries': author['countries'],
            'institution': primary_institution,
            'institutions': [aff['name'] for aff in author['affiliations']],
            'affiliations': author['affiliations']
        })
    
    return {
        'all_authors': author_list,
        'unique_authors': len(author_list),
        'top_20': author_list[:20]
    }

def analyze_orcid_coverage(results: List[Dict]) -> Dict:
    """Analyze ORCID coverage using the new author data"""
    total_authors = 0
    authors_with_orcid = 0
    orcid_by_country = Counter()
    
    for result in results:
        for author in result.get('authors', []):
            total_authors += 1
            if author.get('orcid'):
                authors_with_orcid += 1
                # Get countries from author
                countries = author.get('countries', [])
                if not countries and author.get('country'):
                    countries = [author['country']]
                for country in countries:
                    if country:
                        orcid_by_country[country] += 1
    
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
    """Identify citation classics (articles with > 300 citations) - NO LIMIT"""
    citation_counts = []
    
    for result in results:
        citations = 0
        if result.get('openalex_data') and 'cited_by_count' in result['openalex_data']:
            citations = result['openalex_data']['cited_by_count']
        elif result.get('crossref_data') and 'is-referenced-by-count' in result['crossref_data']:
            citations = result['crossref_data']['is-referenced-by-count']
        
        if citations > 0:
            citation_counts.append(citations)
    
    # Simple threshold: 300 citations
    threshold = 300
    
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
    
    return sorted(classics, key=lambda x: x['citations'], reverse=True)

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
    """Analyze all references with batching - USING NEW AFFILIATION LOGIC"""
    # Use the optimized version with new author extraction
    return analyze_all_references_with_new_affiliations(references, batch_size, paper_authors)

# ======================== OPTIMIZED BATCH PROCESSING WITH NEW AFFILIATION LOGIC ========================

def analyze_reference_batch_with_new_affiliations(references: List[str], progress_callback=None, paper_authors: Set[str] = None, batch_num: int = 0, total_batches: int = 1) -> List[Dict]:
    """Analyze batch of references using NEW affiliation extraction logic (based on your working code)"""
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
    
    # Step 2: Fetch data using ThreadPoolExecutor
    crossref_results = {}
    openalex_results = {}
    
    if dois_with_indices:
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {}
            for idx, doi in dois_with_indices:
                if doi in st.session_state.bad_dois:
                    futures[(idx, 'crossref')] = None
                    futures[(idx, 'openalex')] = None
                else:
                    futures[(idx, 'crossref')] = executor.submit(fetch_crossref, doi)
                    futures[(idx, 'openalex')] = executor.submit(fetch_openalex, doi)
            
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
            
            for idx, doi in dois_with_indices:
                if crossref_results.get(idx) is None and openalex_results.get(idx) is None:
                    st.session_state.bad_dois.add(doi)
    
    # Step 3: Build results for each reference with NEW AFFILIATION LOGIC
    for idx, ref in enumerate(references):
        identifiers = ref_doi_map[idx]
        doi = identifiers['doi']
        
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
            'journal_from': None,
            'year': None,
            'type': None,
            'raw_type': None,
            'publisher': None,
            'publisher_from': None,
            'crossmark_issues': [],
            'is_preprint': False,
            'has_erratum': False,
            'is_retracted': False,
            'is_self_citation': False,
            'issn': None,
            'license': None,
            'references_count': 0,
            'citations_count': 0,
            'is_suspicious_doi': False,
            'is_repository': False,
            'is_ebook': False,
            'is_proceedings': False,
            'openalex_type': None,
            'openalex_raw_type': None
        }
        
        if doi:
            if crossref_data is None and openalex_data is None:
                result['is_suspicious_doi'] = True
                result['crossmark_issues'].append('⚠️ Attention: invalid/suspicious DOI (not found in Crossref or OpenAlex)')
            
            # ==================== PROCESS OPENALEX DATA FIRST (NEW AFFILIATION LOGIC) ====================
            if openalex_data:
                result['openalex_data'] = openalex_data
                result['openalex_status'] = True
                
                # Extract authors using NEW function (from your working code)
                authors_data = get_authors_with_all_affiliations_from_openalex(openalex_data)
                result['authors'].extend(authors_data)
                
                for auth in authors_data:
                    result['authors_display'].append(auth['author'])
                
                # Extract OpenAlex type and raw_type
                openalex_type = openalex_data.get('type', '') or ''
                raw_type = openalex_data.get('raw_type', '') or openalex_data.get('primary_location', {}).get('raw_type', '') or ''
                
                result['openalex_type'] = openalex_type
                result['openalex_raw_type'] = raw_type
                result['type'] = openalex_type
                result['raw_type'] = raw_type
                
                # Type detection
                primary_location = openalex_data.get('primary_location', {})
                source = primary_location.get('source', {})
                source_type = source.get('type', '') or ''
                
                if raw_type == 'proceedings-article':
                    result['is_proceedings'] = True
                    result['crossmark_issues'].append('📊 Conference proceedings')
                elif raw_type == 'book-chapter' and source_type == 'ebook platform':
                    result['is_ebook'] = True
                    result['crossmark_issues'].append('📖 Electronic book')
                
                if not result['is_ebook'] and openalex_data.get('host_venue'):
                    host_venue = openalex_data['host_venue']
                    if isinstance(host_venue, dict):
                        venue_type = host_venue.get('type', '') or ''
                        if venue_type == 'ebook platform':
                            result['is_ebook'] = True
                            result['crossmark_issues'].append('📖 Electronic book (from series)')
                
                repository_raw_types = ['posted-content', 'posted_content', 'preprint']
                repository_source_types = ['repository']
                
                if raw_type.lower() in repository_raw_types:
                    result['is_repository'] = True
                    result['is_preprint'] = True
                    result['crossmark_issues'].append('📚 Repository / Preprint')
                elif source_type.lower() in repository_source_types:
                    result['is_repository'] = True
                    result['is_preprint'] = True
                    result['crossmark_issues'].append('📚 Repository / Preprint')
                
                if openalex_data.get('is_retracted') is True:
                    result['is_retracted'] = True
                    result['crossmark_issues'].append('⚠️ This article has been RETRACTED')
                
                # Extract year
                if 'publication_year' in openalex_data:
                    result['year'] = openalex_data['publication_year']
                
                # Extract journal
                journal_from_openalex = None
                
                if openalex_data.get('host_venue'):
                    host_venue = openalex_data['host_venue']
                    if isinstance(host_venue, dict):
                        if host_venue.get('display_name'):
                            journal_from_openalex = host_venue['display_name'].strip()
                
                if not journal_from_openalex and openalex_data.get('primary_location'):
                    primary = openalex_data['primary_location']
                    if isinstance(primary, dict):
                        if primary.get('source') and isinstance(primary['source'], dict):
                            if primary['source'].get('display_name'):
                                journal_from_openalex = primary['source']['display_name'].strip()
                
                if journal_from_openalex and journal_from_openalex.strip():
                    result['journal'] = journal_from_openalex
                    result['journal_from'] = 'openalex'
                
                # Extract publisher
                publisher_from_openalex = None
                
                if openalex_data.get('host_venue'):
                    host_venue = openalex_data['host_venue']
                    if isinstance(host_venue, dict):
                        if host_venue.get('publisher'):
                            publisher_from_openalex = host_venue['publisher'].strip()
                
                if not publisher_from_openalex and openalex_data.get('primary_location'):
                    primary = openalex_data['primary_location']
                    if isinstance(primary, dict) and primary.get('source'):
                        source_obj = primary['source']
                        if isinstance(source_obj, dict):
                            if source_obj.get('publisher'):
                                publisher_from_openalex = source_obj['publisher'].strip()
                
                if publisher_from_openalex and publisher_from_openalex.strip():
                    result['publisher'] = publisher_from_openalex
                    result['publisher_from'] = 'openalex'
                
                # Extract citation and reference counts
                if 'referenced_works_count' in openalex_data:
                    result['references_count'] = openalex_data['referenced_works_count']
                if 'cited_by_count' in openalex_data:
                    result['citations_count'] = openalex_data['cited_by_count']
            
            # ==================== FALLBACK: PROCESS CROSSREF DATA (if OpenAlex returned no authors) ====================
            if crossref_data and not result['authors']:
                result['crossref_data'] = crossref_data
                result['crossref_status'] = True
                
                # Use SIMPLE Crossref extraction (without aggressive cleaning)
                authors_data = get_authors_from_crossref_simple(crossref_data)
                result['authors'].extend(authors_data)
                
                for auth in authors_data:
                    result['authors_display'].append(auth['author'])
                
                # Extract journal
                if 'container-title' in crossref_data and crossref_data['container-title']:
                    journal_name = crossref_data['container-title'][0]
                    if journal_name and journal_name.strip():
                        result['journal'] = journal_name.strip()
                        result['journal_from'] = 'crossref'
                
                # Extract ISSN
                if 'ISSN' in crossref_data and crossref_data['ISSN']:
                    result['issn'] = crossref_data['ISSN'][0]
                
                # Extract year
                if 'issued' in crossref_data and 'date-parts' in crossref_data['issued']:
                    date_parts = crossref_data['issued']['date-parts']
                    if date_parts and date_parts[0] and len(date_parts[0]) > 0:
                        result['year'] = date_parts[0][0]
                
                # Extract publication type
                if 'type' in crossref_data:
                    result['type'] = crossref_data['type']
                
                # Extract publisher
                if 'publisher' in crossref_data and crossref_data['publisher']:
                    publisher_name = crossref_data['publisher']
                    if publisher_name and publisher_name.strip():
                        result['publisher'] = publisher_name.strip()
                        result['publisher_from'] = 'crossref'
                
                # Extract citation count
                if 'is-referenced-by-count' in crossref_data:
                    result['citations_count'] = max(result['citations_count'], crossref_data['is-referenced-by-count'])
        
        # ========== FALLBACK: arXiv ID AS REPOSITORY ==========
        if identifiers.get('arxiv') and not result['is_repository']:
            result['is_repository'] = True
            result['is_preprint'] = True
            result['crossmark_issues'].append('📚 arXiv preprint')
        
        # ========== SELF-CITATION DETECTION ==========
        if paper_authors and result['authors']:
            for author in result['authors']:
                compare_name = author.get('compare_name', '')
                for paper_author in paper_authors:
                    paper_norm, _ = normalize_author_name(paper_author)
                    if compare_name == paper_norm:
                        result['is_self_citation'] = True
                        break
        
        # Merge authors (deduplicate within the same reference)
        if result['authors']:
            # Use the new merge function for consistency
            temp_list = [{'doi': result.get('doi', 'unknown'), 'authors': result['authors']}]
            merged = merge_authors_with_all_affiliations(temp_list)
            # Convert back to expected format
            new_authors = []
            for author in merged:
                new_authors.append({
                    'display_name': author['author'],
                    'compare_name': author['compare_name'],
                    'orcid': author.get('orcid', ''),
                    'affiliations': author['affiliations'],
                    'countries': author['countries'],
                    'institutions': [aff['name'] for aff in author['affiliations']],
                    'country': author['countries'][0] if author['countries'] else '',
                    'institution': author['affiliations'][0]['name'] if author['affiliations'] else ''
                })
            result['authors'] = new_authors
            result['authors_display'] = [a['display_name'] for a in new_authors]
        
        results.append(result)
        
        # Update progress less frequently
        if progress_callback and idx % 10 == 0:
            progress_callback(batch_num, idx, batch_size, total_batches)
    
    return results

def analyze_all_references_with_new_affiliations(references: List[str], batch_size: int = 50, paper_authors: Set[str] = None) -> List[Dict]:
    """Analyze all references with optimized batching and NEW AFFILIATION LOGIC"""
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
    
    status_container = st.status(f"📊 Analyzing {len(references)} references...", expanded=True)
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(references))
        batch = references[start_idx:end_idx]
        
        status_container.update(
            label=f"📊 Analyzing batch {batch_num + 1} of {total_batches} (references {start_idx + 1}-{end_idx} of {len(references)})",
            state="running"
        )
        
        batch_results = analyze_reference_batch_with_new_affiliations(
            batch, 
            progress_callback=None,
            paper_authors=paper_authors,
            batch_num=batch_num,
            total_batches=total_batches
        )
        
        for result in batch_results:
            processed_refs += 1
            if result.get('doi'):
                total_dois_found += 1
            if result.get('crossref_status') or result.get('openalex_status'):
                total_api_success += 1
        
        all_results.extend(batch_results)
        
        progress_percent = (processed_refs / len(references)) * 100
        current_data_density = total_dois_found / processed_refs if processed_refs > 0 else 0
        api_success_rate = total_api_success / processed_refs if processed_refs > 0 else 0
        
        color, badge_text, badge_class = get_progress_color_by_metrics(
            total_dois_found, 
            processed_refs,
            total_api_success
        )
        
        shimmer_speed = "2s" if progress_percent < 50 else "1s"
        
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
        st.progress(progress_percent / 100)
    
    status_container.update(label="✅ Analysis completed!", state="complete")
    
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

# ======================== IDENTIFIER EXTRACTION ========================
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
                doi_raw = re.sub(r'[.,;:!?)]+$', '', doi_raw)
                if '(' in doi_raw and doi_raw.count('(') > doi_raw.count(')'):
                    open_count = doi_raw.count('(')
                    close_needed = open_count - doi_raw.count(')')
                    remaining_text = text[text.find(doi_raw) + len(doi_raw):]
                    for _ in range(close_needed):
                        match_close = re.search(r'\)', remaining_text)
                        if match_close:
                            doi_raw += ')'
                            remaining_text = remaining_text[match_close.start() + 1:]
                        else:
                            break
                
                if re.match(r'10\.\d{4,9}/.+', doi_raw):
                    if not re.search(r'[.,;:!?]$', doi_raw):
                        result['doi'] = doi_raw
                        break
            if result['doi']:
                break
    
    if not result['doi']:
        simple_pattern = r'(10\.\d{4,9}/[^\s]+)'
        matches = re.findall(simple_pattern, text)
        for match in matches:
            doi_clean = re.sub(r'[.,;:!?)]+$', '', match)
            if '(' in doi_clean and ')' not in doi_clean:
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

def parse_paper_authors(authors_text: str) -> Set[str]:
    """Parse paper authors from text input into normalized format"""
    authors = set()
    
    text = authors_text.replace('\t', '\n').replace(',', '\n')
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        match = re.match(r'^([A-Z]\.?)\s+([A-Za-z\-]+)', line)
        if match:
            initial = match.group(1).rstrip('.')
            lastname = match.group(2)
            authors.add(f"{initial}. {lastname}")
            continue
        
        match = re.match(r'^([A-Z][a-z]+)\s+([A-Za-z\-]+)', line)
        if match:
            firstname = match.group(1)
            lastname = match.group(2)
            initial = firstname[0]
            authors.add(f"{initial}. {lastname}")
            continue
        
        match = re.match(r'^([A-Za-z\-]+),\s*([A-Z]\.?)', line)
        if match:
            lastname = match.group(1)
            initial = match.group(2).rstrip('.')
            authors.add(f"{initial}. {lastname}")
            continue
        
        match = re.match(r'^([A-Za-z\-]+)\s+([A-Z]\.?)', line)
        if match:
            lastname = match.group(1)
            initial = match.group(2).rstrip('.')
            authors.add(f"{initial}. {lastname}")
            continue
        
        st.warning(get_text('authors_warning_text').format(line))
    
    return authors

# ======================== ENHANCED STATISTICS (UPDATED) ========================
def generate_advanced_statistics(results: List[Dict]) -> Dict:
    """Generate enhanced statistics with new metrics - USING NEW AFFILIATION LOGIC"""
    
    total_references = len(results)
    
    doi_status = {'both': 0, 'crossref_only': 0, 'openalex_only': 0, 'none': 0}
    author_counter = Counter()
    journal_counter = Counter()
    type_counter = Counter()
    year_counter = Counter()
    publisher_counter = Counter()
    problematic_refs = []
    crossref_only_refs = []
    openalex_only_refs = []
    suspicious_doi_refs = []
    
    repository_refs = []
    ebook_refs = []
    proceedings_refs = []
    retracted_refs = []
    books_with_isbn_no_doi = []
    non_journal_sources_with_doi = []
    
    publisher_sources = {'crossref': 0, 'openalex': 0, 'both': 0}
    
    # Collect all paper author affiliations for reviewer filtering
    paper_author_affiliations = set()
    
    for result in results:
        if result.get('is_repository', False):
            repository_refs.append({
                'text': result['original_text'],
                'doi': result.get('doi', ''),
                'note': get_text('repository')
            })
            if result.get('doi'):
                non_journal_sources_with_doi.append({
                    'text': result['original_text'],
                    'doi': result.get('doi', ''),
                    'type': 'repository',
                    'note': get_text('repository')
                })
        
        if result.get('is_ebook', False):
            ebook_refs.append({
                'text': result['original_text'],
                'doi': result.get('doi', ''),
                'note': get_text('ebook')
            })
            if result.get('doi'):
                non_journal_sources_with_doi.append({
                    'text': result['original_text'],
                    'doi': result.get('doi', ''),
                    'type': 'ebook',
                    'note': get_text('ebook')
                })
        
        if result.get('is_proceedings', False):
            proceedings_refs.append({
                'text': result['original_text'],
                'doi': result.get('doi', ''),
                'note': get_text('proceedings')
            })
            if result.get('doi'):
                non_journal_sources_with_doi.append({
                    'text': result['original_text'],
                    'doi': result.get('doi', ''),
                    'type': 'proceedings',
                    'note': get_text('proceedings')
                })
        
        if result.get('is_retracted', False):
            retracted_refs.append({
                'text': result['original_text'],
                'doi': result.get('doi', ''),
                'note': get_text('retracted')
            })
        
        if result.get('identifiers', {}).get('isbn') and not result.get('doi'):
            books_with_isbn_no_doi.append(result['original_text'])
        
        # Collect paper author affiliations from the target paper
        # This will be used for reviewer filtering later
        # We need to get affiliations of authors from the target paper (paper_authors)
        # This will be done separately using the paper_authors_set
        
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
        
        if result.get('journal'):
            journal_counter[result['journal']] += 1
        
        publisher = None
        publisher_source = None
        
        if result.get('publisher'):
            publisher = result['publisher']
            publisher_source = result.get('publisher_from', 'unknown')
            
            if publisher_source == 'crossref':
                publisher_sources['crossref'] += 1
            elif publisher_source == 'openalex' or publisher_source == 'openalex_override':
                publisher_sources['openalex'] += 1
                publisher_sources['both'] += 1 if result.get('crossref_status') else 0
        
        if publisher:
            publisher_counter[publisher] += 1
        
        if result.get('type'):
            type_name = result['type'].replace('journal-', '').replace('-', ' ')
            type_counter[type_name] += 1
        
        if result.get('year') and isinstance(result['year'], (int, float)) and 1900 < result['year'] <= datetime.now().year:
            year_counter[int(result['year'])] += 1
        
        has_problem = False
        problems = []
        if result.get('is_retracted'):
            problems.append(get_text('retracted'))
            has_problem = True
        if result.get('is_preprint'):
            problems.append(get_text('preprint'))
            has_problem = True
        if result.get('crossmark_issues'):
            for issue in result['crossmark_issues']:
                if not any(note in issue for note in ['Repository source', 'Electronic book', 'Conference proceedings']):
                    problems.append(issue)
                    has_problem = True
        
        if has_problem:
            problematic_refs.append({'text': result['original_text'], 'problems': ', '.join(problems)})
    
    author_data = analyze_author_frequency_all(results)
    sorted_authors = author_data['all_authors']
    
    top_authors_formatted = []
    for author in sorted_authors[:20]:
        orcid_str = f" 🔗 ORCID: {author['orcid']}" if author.get('orcid') else ""
        inst_str = f" 🏛 {author['institution'][:30]}" if author.get('institution') else ""
        country_str = f" 🌍 {author['country']}" if author.get('country') else ""
        display = author['display_name']
        top_authors_formatted.append(f"{display}{orcid_str}{inst_str}{country_str} — {author['count']} {get_text('html_citations_label')}")
    
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
    
    frequently_cited = [a for a in sorted_authors if a['count'] >= 5]
    
    unique_doi_count = len([r for r in results if r['doi']])
    current_year = datetime.now().year
    years_last_5 = sum(count for year, count in year_counter.items() if year >= current_year - 5)
    
    concepts_data = extract_concepts_from_references(results)
    geo_data = analyze_geographic_distribution(results)
    collab_data = analyze_collaboration_network(results)
    temporal_data = analyze_temporal_citations(results)
    yearly_stats = analyze_yearly_statistics(results)
    identifier_data = analyze_identifier_coverage(results)
    publisher_freq = analyze_publisher_frequency(results)
    journal_freq_all = analyze_journal_frequency_all(results)
    author_freq_all = author_data
    orcid_data = analyze_orcid_coverage(results)
    language_data = analyze_language_distribution(results)
    shannon_authors = calculate_shannon_diversity(results, 'authors')
    shannon_journals = calculate_shannon_diversity(results, 'journals')
    shannon_publishers = calculate_shannon_diversity(results, 'publishers')
    citation_classics = identify_citation_classics(results)
    
    self_citation_refs = [r for r in results if r.get('is_self_citation', False)]
    
    def calc_percent(count):
        return (count / total_references * 100) if total_references > 0 else 0
    
    return {
        'total_references': total_references,
        'total_with_doi': unique_doi_count,
        'total_with_doi_percent': calc_percent(unique_doi_count),
        'doi_status': doi_status,
        'doi_status_percents': {
            'both': calc_percent(doi_status['both']),
            'crossref_only': calc_percent(doi_status['crossref_only']),
            'openalex_only': calc_percent(doi_status['openalex_only']),
            'none': calc_percent(doi_status['none'])
        },
        'top_authors': top_authors_formatted,
        'top_journals': [f"{journal} — {count}" for journal, count in journal_counter.most_common(15)],
        'top_types': [f"{type_name} — {count}" for type_name, count in type_counter.most_common()],
        'year_distribution': dict(sorted(year_counter.items())),
        'years_last_5': years_last_5,
        'years_last_5_percent': calc_percent(years_last_5),
        'top_publishers': [f"{publisher} — {count}" for publisher, count in publisher_counter.most_common(10)],
        'problematic_refs': problematic_refs[:20],
        'crossref_only_refs': crossref_only_refs[:20],
        'openalex_only_refs': openalex_only_refs[:20],
        'suspicious_doi_refs': suspicious_doi_refs[:20],
        'citation_stacking': citation_stacking[:10],
        'frequently_cited': [f"{a['display_name']} — {a['count']}" for a in frequently_cited[:10]],
        'self_citations_count': len([r for r in results if r.get('is_self_citation', False)]),
        'self_citations_percent': calc_percent(len([r for r in results if r.get('is_self_citation', False)])),
        'self_citation_refs': self_citation_refs,
        'repository_refs': repository_refs[:20],
        'ebook_refs': ebook_refs[:20],
        'proceedings_refs': proceedings_refs[:20],
        'retracted_refs': retracted_refs[:20],
        'books_with_isbn_no_doi': books_with_isbn_no_doi[:20],
        'non_journal_sources_with_doi': non_journal_sources_with_doi[:50],
        'concepts': concepts_data,
        'geography': geo_data,
        'collaboration': collab_data,
        'temporal': temporal_data,
        'yearly_stats': yearly_stats,
        'identifier_coverage': identifier_data,
        'identifier_coverage_percents': {
            'has_doi': calc_percent(identifier_data['stats']['has_doi']),
            'has_url': calc_percent(identifier_data['stats']['has_url']),
            'has_arxiv': calc_percent(identifier_data['stats']['has_arxiv']),
            'has_pmid': calc_percent(identifier_data['stats']['has_pmid']),
            'has_isbn': calc_percent(identifier_data['stats']['has_isbn']),
            'has_none': calc_percent(identifier_data['stats']['has_none']),
            'multiple': calc_percent(identifier_data['stats']['multiple']),
            'preprint_repository': calc_percent(identifier_data['stats']['is_preprint_repository']),
            'ebook_platform': calc_percent(identifier_data['stats']['is_ebook_platform']),
            'proceedings': calc_percent(identifier_data['stats']['is_proceedings']),
            'retracted': calc_percent(identifier_data['stats']['is_retracted']),
            'book_no_doi': calc_percent(identifier_data['stats']['is_book_no_doi'])
        },
        'publisher_frequency': publisher_freq,
        'journal_frequency_all': journal_freq_all,
        'author_frequency_all': author_freq_all,
        'orcid_coverage': orcid_data,
        'language': language_data,
        'shannon_index': {
            'authors': shannon_authors,
            'journals': shannon_journals,
            'publishers': shannon_publishers
        },
        'citation_classics': citation_classics,
        'total_citations_sum': sum(r.get('citations_count', 0) for r in results),
        'avg_citations': sum(r.get('citations_count', 0) for r in results) / total_references if total_references else 0,
        'publisher_sources': publisher_sources
    }

def display_top_authors(stats: Dict):
    """Display top authors with proper ORCID and ALL affiliation information"""
    st.markdown(f"### {get_text('top_authors')}")
    
    for i, author in enumerate(stats['author_frequency_all']['all_authors'][:30], 1):
        orcid_html = ""
        if author.get('orcid'):
            orcid_url = author['orcid']
            if not orcid_url.startswith('http'):
                orcid_url = f"https://orcid.org/{orcid_url}"
            orcid_html = f' 🔗 <a href="{orcid_url}" target="_blank" style="color: #667eea; text-decoration: none;">ORCID</a>'
        
        inst_text = f" 🏛 {author['institution'][:50]}" if author.get('institution') else ""
        country_text = f" 🌍 {author['country']}" if author.get('country') else ""
        
        # Show ALL affiliations
        affiliations_text = ""
        if author.get('affiliations'):
            aff_list = author['affiliations'][:5]  # Show up to 5 affiliations
            affiliations_html = []
            for aff in aff_list:
                if isinstance(aff, dict):
                    aff_name = aff.get('name', '')
                    aff_country = aff.get('country', '')
                    if aff_country and aff_country not in ['N/A', 'Не указана', 'Не определена']:
                        affiliations_html.append(f'{html.escape(aff_name)} ({aff_country})')
                    else:
                        affiliations_html.append(html.escape(aff_name))
                else:
                    affiliations_html.append(html.escape(aff))
            
            if affiliations_html:
                affiliations_text = f"""
                <div style='font-size: 11px; color: #666; margin-top: 5px;'>
                    <strong>{get_text('all_affiliations')}:</strong><br>
                    {'<br>'.join(affiliations_html)}
                </div>
                """
        
        # Show ALL countries
        countries_text = ""
        if author.get('countries') and len(author.get('countries', [])) > 1:
            countries_text = f"<div style='font-size: 11px; color: #666; margin-top: 3px;'><strong>{get_text('all_countries')}:</strong> {', '.join(author['countries'])}</div>"
        
        st.markdown(f"""
        <div class="rank-item">
            <span class="rank-number">{i}.</span>
            <span class="rank-name">{author['display_name']}{orcid_html}{inst_text}{country_text}</span>
            <span class="rank-count">{author['count']} {get_text('html_citations_label')}</span>
            <div class="progress-bar-custom">
                <div class="progress-fill" style="width: {author['count'] / stats['author_frequency_all']['all_authors'][0]['count'] * 100 if stats['author_frequency_all']['all_authors'] else 0}%;"></div>
            </div>
            {affiliations_text}
            {countries_text}
        </div>
        """, unsafe_allow_html=True)

def display_geography_section(stats: Dict):
    """Display geography section with three types of statistics"""
    
    st.markdown(f"### {get_text('geographic_distribution')}")
    
    st.markdown(f"#### {get_text('geography_type_1')}")
    st.caption(get_text('geography_type_1_desc'))
    
    if stats['geography'].get('type1_unique_countries_per_reference'):
        type1_df = pd.DataFrame(
            list(stats['geography']['type1_unique_countries_per_reference'].items()),
            columns=["Country", "References count"]
        )
        st.dataframe(type1_df, use_container_width=True)
    
    st.markdown(f"#### {get_text('geography_type_2')}")
    st.caption(get_text('geography_type_2_desc'))
    
    if stats['geography'].get('type2_authors_per_country'):
        type2_df = pd.DataFrame(
            list(stats['geography']['type2_authors_per_country'].items()),
            columns=["Country", "Authors count"]
        )
        st.dataframe(type2_df, use_container_width=True)
    
    st.markdown(f"#### {get_text('geography_type_3')}")
    st.caption(get_text('geography_type_3_desc'))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(get_text('single_country'), stats['geography'].get('single_country_count', 0))
    with col2:
        st.metric(get_text('international_collab'), stats['geography'].get('international_count', 0))
    with col3:
        st.metric(
            get_text('total_references_with_country'),
            stats['geography'].get('total_references_with_country', 0)
        )
    
    if stats['geography'].get('collaboration_matrix'):
        st.markdown(f"#### {get_text('collaboration_matrix')}")
        collab_df = pd.DataFrame(stats['geography']['collaboration_matrix'][:15])
        st.dataframe(collab_df, use_container_width=True)

# ======================== HELPER FUNCTION FOR AUTHOR HIGHLIGHTING ========================
def format_authors_with_highlight(authors_list: List[str], highlight_authors_norm_set: Set[str], normalize_func) -> str:
    """Format authors list with highlighting for self-citation authors"""
    if not authors_list:
        return ""
    
    formatted_authors = []
    for author in authors_list:
        norm_author, _ = normalize_func(author)
        
        if norm_author in highlight_authors_norm_set:
            escaped_author = html.escape(author)
            formatted_authors.append(f'<span class="self-citation-author">{escaped_author}</span>')
        else:
            formatted_authors.append(html.escape(author))
    
    return ', '.join(formatted_authors)

def get_color_for_author(index: int) -> str:
    """Get a color for highlighting author based on index"""
    colors = [
        "#d9534f", "#5bc0de", "#5cb85c", "#f0ad4e", "#9b59b6",
        "#e67e22", "#1abc9c", "#e74c3c", "#3498db", "#2ecc71"
    ]
    return colors[index % len(colors)]

# ======================== HTML REPORT GENERATION (UPDATED WITH REVIEWERS AND AFFILIATIONS) ========================
def generate_html_report_advanced(results: List[Dict], stats: Dict, paper_authors: Set[str] = None, lang: str = 'en', journal_name: str = '', article_number: str = '', duplicates: List[Dict] = None, primary_color: str = '#667eea', secondary_color: str = '#f39c12', show_reviewers: bool = False, reviewers: List[Dict] = None) -> str:
    """Generate enhanced HTML report with PNG icons (no emojis) and professional design"""
    
    analogous = get_analogous_colors(primary_color, 2)
    
    css_vars = generate_css_variables(primary_color, secondary_color)
    
    primary_rgb = hex_to_rgb(primary_color)
    secondary_rgb = hex_to_rgb(secondary_color)
    
    import base64
    import os
    
    def get_text_local(key: str) -> str:
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        else:
            return key
    
    logo_base64 = ""
    try:
        with open("logo.png", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        pass
    
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
        ("url", "icon_url.png"), ("problems", "icon_problems.png"), ("list", "icon_list.png"),
        ("reviewers", "icon_reviewers.png")
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
    
    if not journal_name or journal_name.strip() == '':
        journal_name_display = get_text_local('journal_name_label') + ": Chimica Techno Acta"
    else:
        journal_name_display = get_text_local('journal_name_label') + ": " + html.escape(journal_name)
    
    article_number_display = ""
    if article_number and article_number.strip():
        article_number_display = f'<div><strong>{get_text_local("article_number_label")}:</strong> {html.escape(article_number)}</div>'
    
    show_self_citations_section = paper_authors and len(paper_authors) > 0
    
    def make_clickable_doi(doi):
        if doi:
            not_found_text = get_text_local('not_found')
            return f'<a href="https://doi.org/{doi}" target="_blank" class="clickable-link">{html.escape(doi)}</a>'
        return not_found_text
    
    def make_clickable_orcid(orcid):
        if orcid:
            return f'<a href="{orcid}" target="_blank" class="clickable-link">{html.escape(orcid)}</a>'
        return ''
    
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
    
    def format_authors_with_colors_for_selfcitations(authors_list, paper_norm_map):
        if not authors_list:
            return ""
        formatted_authors = []
        for author in authors_list:
            norm_author, _ = normalize_author_name(author)
            if norm_author in paper_norm_map:
                escaped_author = html.escape(author)
                color = paper_norm_map[norm_author]['color']
                formatted_authors.append(f'<span style="color: {color}; font-weight: bold; background-color: {color}20; padding: 2px 4px; border-radius: 3px;">{escaped_author}</span>')
            else:
                formatted_authors.append(html.escape(author))
        return ', '.join(formatted_authors)
    
    self_citations_html = ""
    if show_self_citations_section:
        if stats.get('self_citation_refs'):
            for ref in stats.get('self_citation_refs', []):
                authors_full_list = ref.get('authors_display', [])
                formatted_authors = format_authors_with_colors_for_selfcitations(authors_full_list, normalized_paper_authors_map)
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
    
    # Potential Reviewers section HTML
    reviewers_html = ""
    if show_reviewers and reviewers:
        reviewers_html = f"""
        <div id="reviewers" class="section">
            {make_section_title("reviewers", "potential_reviewers")}
        """
        for i, reviewer in enumerate(reviewers[:30], 1):
            orcid_profile = reviewer.get('orcid_profile', {})
            orcid_id = reviewer.get('orcid', '')
            
            given_names = orcid_profile.get('given_names', '')
            family_name = orcid_profile.get('family_name', '')
            credit_name = orcid_profile.get('credit_name', '')
            
            if given_names and family_name:
                full_name = f"{given_names} {family_name}"
            elif credit_name:
                full_name = credit_name
            else:
                full_name = reviewer.get('name', 'Unknown')
            
            orcid_link = ""
            if orcid_id:
                orcid_url = format_orcid_id(orcid_id) if not orcid_id.startswith('http') else orcid_id
                orcid_link = f'<div class="reviewer-orcid"><strong>ORCID:</strong> <a href="{orcid_url}" target="_blank" style="color: {primary_color};">{orcid_id}</a></div>'
            
            country = orcid_profile.get('country', '')
            if not country and reviewer.get('countries'):
                country = ', '.join(reviewer['countries'][:3])
            
            country_html = f'<div><strong>{get_text_local("orcid_country")}:</strong> {country}</div>' if country else ''
            
            affiliations = reviewer.get('affiliations', [])
            affiliations_html = ""
            if affiliations:
                aff_list = []
                for aff in affiliations[:3]:
                    if isinstance(aff, dict):
                        aff_list.append(aff.get('name', ''))
                    else:
                        aff_list.append(aff)
                affiliations_html = f'<div><strong>{get_text_local("reviewer_affiliations")}:</strong><br>{"<br>".join([html.escape(a) for a in aff_list])}</div>'
            
            external_ids = orcid_profile.get('external_ids', {})
            external_ids_html = ""
            if external_ids:
                friendly_names = {
                    'scopus-author-id': 'Scopus Author ID',
                    'researcher-id': 'ResearcherID (WoS)',
                    'wos-researcherid': 'Web of Science ResearcherID',
                    'publons': 'Publons',
                    'linkedin': 'LinkedIn',
                    'researchgate': 'ResearchGate',
                    'google-scholar': 'Google Scholar',
                }
                id_links = []
                for id_type, id_info in external_ids.items():
                    display_name = friendly_names.get(id_type, id_type.replace('-', ' ').title())
                    id_url = id_info.get('url', '')
                    if id_url:
                        id_links.append(f'<a href="{id_url}" target="_blank" class="external-id-link">{display_name}</a>')
                if id_links:
                    external_ids_html = f'<div class="reviewer-section-title">{get_text_local("orcid_other_ids")}:</div><div>{" ".join(id_links)}</div>'
            
            researcher_urls = orcid_profile.get('researcher_urls', [])
            websites_html = ""
            if researcher_urls:
                url_links = []
                for url_info in researcher_urls[:5]:
                    url_name = url_info.get('name', 'Website')
                    url_value = url_info.get('url', '')
                    if url_value:
                        url_links.append(f'<a href="{url_value}" target="_blank" class="external-id-link">{url_name}</a>')
                if url_links:
                    websites_html = f'<div class="reviewer-section-title">{get_text_local("orcid_websites")}:</div><div>{" ".join(url_links)}</div>'
            
            pub_html = f'<div style="margin-top: 12px; font-size: 12px; color: #666;"><strong>{get_text_local("reviewer_from_reference")}:</strong> {reviewer.get("doi", "N/A")}<br><strong>{get_text_local("year")}:</strong> {reviewer.get("publication_year", "Unknown")}</div>'
            
            keywords = orcid_profile.get('keywords', [])
            keywords_html = ""
            if keywords:
                keywords_str = ', '.join(keywords[:5])
                keywords_html = f'<div><strong>Research interests:</strong> {keywords_str}</div>'
            
            reviewers_html += f"""
            <div class="reviewer-card">
                <div class="reviewer-name">{i}. {full_name}</div>
                {orcid_link}
                {country_html}
                {affiliations_html}
                {keywords_html}
                {external_ids_html}
                {websites_html}
                {pub_html}
            </div>
            """
        reviewers_html += "</div>"
    
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
    
    full_references_html = ""
    duplicate_indices = set()
    if duplicates:
        for dup in duplicates:
            duplicate_indices.add(dup['index1'])
            duplicate_indices.add(dup['index2'])
    
    for idx, result in enumerate(results[:300]):
        authors_full_list = result.get('authors_display', [])
        formatted_authors = ', '.join([html.escape(a) for a in authors_full_list]) if authors_full_list else get_text_local("not_found")
        original_text_full = html.escape(result.get('original_text', ''))
        doi_info = f'<div style="font-size: 13px; margin-top: 5px;"><strong>{get_text_local("doi_found")}:</strong> {make_clickable_doi(result.get("doi"))}</div>' if result.get('doi') else ''
        status_icon = "⚠" if result.get('is_suspicious_doi') else ("✓" if result.get('doi') else "✗")
        
        color_class = ""
        if result.get('is_retracted', False):
            color_class = "retracted-reference"
        elif result.get('is_suspicious_doi', False):
            color_class = "suspicious-reference"
        elif idx in duplicate_indices:
            color_class = "duplicate-reference"
        elif result.get('is_ebook', False):
            color_class = "ebook-reference"
        elif result.get('is_proceedings', False):
            color_class = "proceedings-reference"
        elif result.get('is_repository', False):
            color_class = "repository-reference"
        elif result.get('is_preprint', False):
            color_class = "preprint-reference"
        elif not result.get('doi') and not result.get('crossref_status') and not result.get('openalex_status'):
            color_class = "notfound-reference"
        else:
            color_class = "normal-article"
        
        special_badge = ""
        if result.get('is_retracted', False):
            special_badge = f'<span class="badge-danger" style="margin-left: 10px;">{get_text_local("retracted")}</span>'
        elif result.get('is_ebook', False):
            special_badge = f'<span class="badge-book" style="margin-left: 10px;">{get_text_local("ebook")}</span>'
        elif result.get('is_repository', False):
            special_badge = f'<span class="badge-repository" style="margin-left: 10px;">{get_text_local("repository")}</span>'
        elif result.get('is_preprint', False):
            special_badge = f'<span class="badge-repository" style="margin-left: 10px;">{get_text_local("preprint")}</span>'
        elif result.get('is_proceedings', False):
            special_badge = f'<span class="badge-proceedings" style="margin-left: 10px;">{get_text_local("proceedings")}</span>'
        elif result.get('is_suspicious_doi', False):
            special_badge = f'<span class="badge-danger" style="margin-left: 10px;">{get_text_local("suspicious_doi_badge")}</span>'
        elif idx in duplicate_indices:
            special_badge = f'<span class="badge-warning" style="margin-left: 10px;">{get_text_local("full_doi_match")}</span>'
        
        full_references_html += f"""
        <div class="rank-item {color_class}" style="margin-bottom: 15px;">
            <div><strong>{status_icon} {get_text_local("reference")} {idx + 1}:</strong>{special_badge}</div>
            <div class="full-text-container">{original_text_full}</div>
            <div style="font-size: 13px; margin-top: 5px;"><strong>{get_text_local("authors")}:</strong> {formatted_authors}</div>
            {doi_info}
        </div>
        """
    
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
    
    if show_reviewers and reviewers:
        sidebar_items.append(("reviewers", "potential_reviewers", icons.get("reviewers", "")))
    
    if duplicates and len(duplicates) > 0:
        sidebar_items.append(("duplicates", "duplicate_references_title", icons.get("duplicates", icons["list"])))
    
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
    
    total_references = stats['total_references']
    total_with_doi = stats['total_with_doi']
    total_with_doi_percent = stats.get('total_with_doi_percent', 0)
    last_5_years = stats['yearly_stats']['last_5_years']
    last_5_years_percent = stats['yearly_stats']['last_5_years_percent']
    self_citations_count = stats['self_citations_count']
    self_citations_percent = stats['self_citations_percent']
    total_citations_sum = stats.get('total_citations_sum', 0)
    avg_citations = stats.get('avg_citations', 0)
    
    identifier_stats = stats['identifier_coverage']['stats']
    identifier_percents = stats['identifier_coverage_percents']
    
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
    
    current_date = datetime.now().strftime('%d.%m.%Y')
    
    confidential_banner_html = ""
    if show_reviewers:
        banner_text = get_text_local('reviewer_confidential_banner')
        confidential_banner_html = f'<div class="confidential-banner">⚠️ {banner_text}</div>'
    
    html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{get_text_local('app_title')}</title>
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
        
        .normal-article {{ background: #e8f5e9 !important; border-left: 3px solid #4caf50 !important; }}
        .notfound-reference {{ background: #e9ecef !important; border-left: 3px solid #6c757d !important; }}
        .suspicious-reference {{ background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }}
        .duplicate-reference {{ background: #ffe5cc !important; border-left: 3px solid #fd7e14 !important; }}
        .ebook-reference {{ background: #d4f1e9 !important; border-left: 3px solid #0e6b5e !important; }}
        .repository-reference {{ background: #e2d5f8 !important; border-left: 3px solid #5e2a9e !important; }}
        .preprint-reference {{ background: #e2d5f8 !important; border-left: 3px solid #5e2a9e !important; }}
        .proceedings-reference {{ background: #fff2c9 !important; border-left: 3px solid #b26b00 !important; }}
        .retracted-reference {{ background: #f8d7da !important; border-left: 3px solid #dc3545 !important; }}
        
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
        
        .reviewer-card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid {primary_color};
            transition: transform 0.2s;
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
        .reviewer-section-title {{
            font-weight: 600;
            margin-top: 12px;
            margin-bottom: 6px;
            font-size: 13px;
            color: #555;
        }}
        .external-id-link {{
            display: inline-block;
            background: #f0f0f0;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            margin: 3px;
            text-decoration: none;
            color: #333;
            transition: all 0.2s;
        }}
        .external-id-link:hover {{
            background: {primary_color};
            color: white;
        }}
        .confidential-banner {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 4px solid #dc3545;
            padding: 12px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            font-weight: 500;
            color: #856404;
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
        
        {confidential_banner_html}
        
        <div id="overview" class="section">
            {make_section_title("overview", "html_overview")}
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-number">{total_references}</div><div class="stat-percent">(100.0%)</div><div class="stat-label">{get_text_local('total_references')}</div></div>
                <div class="stat-card"><div class="stat-number">{total_with_doi}</div><div class="stat-percent">({total_with_doi_percent:.1f}%)</div><div class="stat-label">{get_text_local('doi_found')}</div></div>
                <div class="stat-card"><div class="stat-number">{last_5_years}</div><div class="stat-percent">({last_5_years_percent:.1f}%)</div><div class="stat-label">{get_text_local('last_5_years_metric')}</div></div>
                <div class="stat-card"><div class="stat-number">{self_citations_count}</div><div class="stat-percent">({self_citations_percent:.1f}%)</div><div class="stat-label">{get_text_local('self_citations')}</div></div>
                <div class="stat-card"><div class="stat-number">{total_citations_sum}</div><div class="stat-label">{get_text_local('total_citations')}</div></div>
                <div class="stat-card"><div class="stat-number">{avg_citations:.1f}</div><div class="stat-label">{get_text_local('avg_citations')}</div></div>
            </div>
        </div>
        
        <div id="identifiers" class="section">
            {make_section_title("identifier", "html_identifier_coverage")}
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-number">{identifier_stats['has_doi']}</div><div class="stat-percent">({identifier_percents['has_doi']:.1f}%)</div><div class="stat-label">{get_text_local('doi_found')}</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['has_url']}</div><div class="stat-percent">({identifier_percents['has_url']:.1f}%)</div><div class="stat-label">URL</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['is_preprint_repository']}</div><div class="stat-percent">({identifier_percents['preprint_repository']:.1f}%)</div><div class="stat-label">{get_text_local('preprint_repository_count')}</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['has_pmid']}</div><div class="stat-percent">({identifier_percents['has_pmid']:.1f}%)</div><div class="stat-label">PMID</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['is_ebook_platform']}</div><div class="stat-percent">({identifier_percents['ebook_platform']:.1f}%)</div><div class="stat-label">{get_text_local('ebook')} (with DOI)</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['is_book_no_doi']}</div><div class="stat-percent">({identifier_percents['book_no_doi']:.1f}%)</div><div class="stat-label">{get_text_local('books_count')} (ISBN only)</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['is_proceedings']}</div><div class="stat-percent">({identifier_percents['proceedings']:.1f}%)</div><div class="stat-label">{get_text_local('proceedings_count')}</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['is_retracted']}</div><div class="stat-percent">({identifier_percents['retracted']:.1f}%)</div><div class="stat-label">{get_text_local('retracted_count')}</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['has_none']}</div><div class="stat-percent">({identifier_percents['has_none']:.1f}%)</div><div class="stat-label">{get_text_local('no_identifier')}</div></div>
                <div class="stat-card"><div class="stat-number">{identifier_stats['multiple']}</div><div class="stat-percent">({identifier_percents['multiple']:.1f}%)</div><div class="stat-label">Multiple identifiers</div></div>
            </div>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-number">{stats['doi_status']['both']}</div><div class="stat-percent">({stats['doi_status_percents']['both']:.1f}%)</div><div class="stat-label">{get_text_local('status_both')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['doi_status']['crossref_only']}</div><div class="stat-percent">({stats['doi_status_percents']['crossref_only']:.1f}%)</div><div class="stat-label">{get_text_local('status_crossref_only')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['doi_status']['openalex_only']}</div><div class="stat-percent">({stats['doi_status_percents']['openalex_only']:.1f}%)</div><div class="stat-label">{get_text_local('status_openalex_only')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['doi_status']['none']}</div><div class="stat-percent">({stats['doi_status_percents']['none']:.1f}%)</div><div class="stat-label">{get_text_local('status_none')}</div></div>
            </div>
        </div>
        
        <div id="authors" class="section">
            {make_section_title("authors", "html_authors")}
            <div>
                {''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{html.escape(author["display_name"])}</span><span class="rank-count">{author["count"]} {get_text_local("html_citations_label")}</span>' + (f'<div style="font-size: 11px; color: #667eea;">{get_text_local("orcid_label")}: {make_clickable_orcid(author["orcid"])}</div>' if author.get("orcid") else '') + (f'<div style="font-size: 11px; color: #666;"><strong>{get_text_local("institution_label")}:</strong> {html.escape(author["institution"][:50])}</div>' if author.get("institution") else '') + (f'<div style="font-size: 11px; color: #666;"><strong>{get_text_local("country_label")}:</strong> {", ".join(author["countries"])}</div>' if author.get("countries") else '') + (f'<div style="font-size: 11px; color: #666; margin-top: 5px;"><strong>{get_text_local("all_affiliations")}:</strong><br>' + '<br>'.join([html.escape(aff["name"]) for aff in author.get("affiliations", [])[:3]]) + '</div>' if author.get("affiliations") else '') + '<div class="progress-bar"><div class="progress-fill" style="width: ' + str(min(100, author["count"] / stats["author_frequency_all"]["all_authors"][0]["count"] * 100 if stats["author_frequency_all"]["all_authors"] else 0)) + '%;"></div></div></div>' for i, author in enumerate(stats["author_frequency_all"]["all_authors"][:30])])}
            </div>
            <div style="margin-top: 15px;">
                <span class="badge badge-info">{get_text_local('unique_authors')}: {stats['author_frequency_all']['unique_authors']}</span>
                <span class="badge badge-info">{get_text_local('shannon_authors')}: {stats['shannon_index']['authors']}</span>
                <span class="badge badge-info">{get_text_local('orcid_coverage')}: {stats['orcid_coverage']['with_orcid']} ({stats['orcid_coverage']['coverage_percent']:.1f}%)</span>
            </div>
        </div>
        
        <div id="journals" class="section">
            {make_section_title("journals", "html_journals")}
            <table><thead><tr><th>{get_text_local('html_rank')}</th><th>{get_text_local('journal')}</th><th>{get_text_local('html_count')}</th><th>{get_text_local('html_percentage')}</th></tr></thead>
            <tbody>{''.join([f'<tr><td>{i+1}</td><td>{html.escape(journal["journal"])}</td><td>{journal["count"]}</td><td>{journal["percentage"]:.1f}%</td></tr>' for i, journal in enumerate(stats["journal_frequency_all"]["all_journals"])])}</tbody></table>
            <div style="margin-top: 15px;"><span class="badge badge-info">{get_text_local('unique_journals')}: {stats['journal_frequency_all']['unique_journals']}</span><span class="badge badge-info">{get_text_local('shannon_journals')}: {stats['shannon_index']['journals']}</span></div>
        </div>
        
        <div id="publishers" class="section">
            {make_section_title("publishers", "html_publishers")}
            <table><thead><tr><th>{get_text_local('html_rank')}</th><th>{get_text_local('publisher')}</th><th>{get_text_local('html_count')}</th><th>{get_text_local('html_percentage')}</th></tr></thead>
            <tbody>{''.join([f'<tr><td>{i+1}</td><td>{html.escape(publisher["publisher"])}</td><td>{publisher["count"]}</td><td>{publisher["percentage"]:.1f}%</td></tr>' for i, publisher in enumerate(stats["publisher_frequency"]["all_publishers"])])}</tbody></table>
            <div style="margin-top: 15px;"><span class="badge badge-info">{get_text_local('unique_publishers_metric')}: {stats['publisher_frequency']['unique_publishers']}</span><span class="badge badge-info">{get_text_local('shannon_publishers')}: {stats['shannon_index']['publishers']}</span></div>
        </div>
        
        <div id="yearly" class="section">
            {make_section_title("yearly", "html_yearly")}
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-number">{stats['yearly_stats']['last_year']}</div><div class="stat-percent">({stats['yearly_stats']['last_year_percent']:.1f}%)</div><div class="stat-label">{get_text_local('last_year')} ({stats['yearly_stats']['last_completed_year']})</div></div>
                <div class="stat-card"><div class="stat-number">{stats['yearly_stats']['last_3_years']}</div><div class="stat-percent">({stats['yearly_stats']['last_3_years_percent']:.1f}%)</div><div class="stat-label">{get_text_local('last_3_years')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['yearly_stats']['last_5_years']}</div><div class="stat-percent">({stats['yearly_stats']['last_5_years_percent']:.1f}%)</div><div class="stat-label">{get_text_local('last_5_years_metric')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['yearly_stats']['last_10_years']}</div><div class="stat-percent">({stats['yearly_stats']['last_10_years_percent']:.1f}%)</div><div class="stat-label">{get_text_local('last_10_years')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['yearly_stats']['unknown_year']}</div><div class="stat-label">{get_text_local('references_with_unknown_year')}</div></div>
            </div>
            <div><h4>{get_text_local('distribution_by_year')}:</h4>{''.join([f'<div class="rank-item"><span class="rank-name">{year}</span><span class="rank-count">{stats["yearly_stats"]["yearly_counts"][year]} {get_text_local("references_count")} ({stats["yearly_stats"]["yearly_percentages"][year]:.1f}%)</span><div class="progress-bar"><div class="progress-fill" style="width: {stats["yearly_stats"]["yearly_percentages"][year]}%;"></div></div></div>' for year in sorted(stats["yearly_stats"]["yearly_counts"].keys(), reverse=True)])}</div>
            <div style="margin-top: 15px;"><h4>{get_text_local('cumulative_percentage')}:</h4>{''.join([f'<div class="rank-item"><span class="rank-name">{year}</span><span class="rank-count">{stats["yearly_stats"]["cumulative_percentages"][year]:.1f}% {get_text_local("cumulative")}</span><div class="progress-bar"><div class="progress-fill" style="width: {stats["yearly_stats"]["cumulative_percentages"][year]}%;"></div></div></div>' for year in sorted(stats["yearly_stats"]["yearly_counts"].keys(), reverse=True)])}</div>
            <div style="margin-top: 15px;"><span class="badge badge-info">{get_text_local('median_age')}: {stats['temporal']['median_age']} {get_text_local('years')}</span><span class="badge badge-info">{get_text_local('average_age')}: {stats['temporal']['average_age']:.1f} {get_text_local('years')}</span></div>
        </div>
        
        <div id="concepts" class="section">
            {make_section_title("concepts", "html_concepts")}
            <div class="concepts-grid">{''.join([f'<div class="concept-card"><div class="concept-name">{html.escape(concept[0])}</div><div class="concept-score">{get_text_local("html_frequency")}: {concept[1]}</div></div>' for concept in stats['concepts']['concepts'][:12]])}</div>
            <div style="margin-top: 15px;"><span class="badge badge-info">{get_text_local('unique_concepts')}: {stats['concepts']['unique_concepts']}</span></div>
        </div>
        
        <div id="geography" class="section">
            {make_section_title("geography", "html_geography")}
            <h4>{get_text_local('geography_type_1')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_1_desc')}</p>
            <div>{''.join([f'<div class="rank-item"><span class="rank-name">{html.escape(country)}</span><span class="rank-count">{count} {get_text_local("references_count")}</span><div class="progress-bar"><div class="progress-fill" style="width: {count / max(stats["geography"]["type1_unique_countries_per_reference"].values()) * 100 if stats["geography"]["type1_unique_countries_per_reference"] else 0}%;"></div></div></div>' for country, count in list(stats['geography']['type1_unique_countries_per_reference'].items())[:15]])}</div>
            <h4 style="margin-top: 25px;">{get_text_local('geography_type_2')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_2_desc')}</p>
            <div>{''.join([f'<div class="rank-item"><span class="rank-name">{html.escape(country)}</span><span class="rank-count">{count} {get_text_local("html_authors_count")}</span><div class="progress-bar"><div class="progress-fill" style="width: {count / max(stats["geography"]["type2_authors_per_country"].values()) * 100 if stats["geography"]["type2_authors_per_country"] else 0}%;"></div></div></div>' for country, count in list(stats['geography']['type2_authors_per_country'].items())[:15]])}</div>
            <h4 style="margin-top: 25px;">{get_text_local('geography_type_3')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_3_desc')}</p>
            <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
                <div class="stat-card"><div class="stat-number">{stats['geography']['single_country_count']}</div><div class="stat-label">{get_text_local('single_country')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['geography']['international_count']}</div><div class="stat-label">{get_text_local('international_collab')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['geography']['total_references_with_country']}</div><div class="stat-label">{get_text_local('total_references')} (with country)</div></div>
            </div>
            <h5 style="margin-top: 20px;">{get_text_local('collaboration_matrix')}:</h5>
            <div>{''.join([f'<div class="rank-item"><span class="rank-name">{collab["country1"]} + {collab["country2"]}</span><span class="rank-count">{collab["count"]} {get_text_local("references_count")}</span><div class="progress-bar"><div class="progress-fill" style="width: {collab["count"] / max([c["count"] for c in stats["geography"]["collaboration_matrix"]]) * 100 if stats["geography"]["collaboration_matrix"] else 0}%;"></div></div></div>' for collab in stats['geography']['collaboration_matrix'][:15]])}</div>
        </div>
        
        <div id="collaboration" class="section">
            {make_section_title("collaborations", "html_collaborations")}
            <div>{''.join([f'<div class="rank-item"><span class="rank-number">{i+1}.</span><span class="rank-name">{html.escape(collab["author1"])} + {html.escape(collab["author2"])}</span><span class="rank-count">{collab["count"]} {get_text_local("html_joint_works")}</span></div>' for i, collab in enumerate(stats["collaboration"]["top_collaborations"][:8])])}</div>
            <div style="margin-top: 15px;"><span class="badge badge-info">{get_text_local('core_authors_label')}: {', '.join([f"{html.escape(author[0])} ({author[1]} {get_text_local('html_connections')})" for author in stats['collaboration']['core_authors'][:5]])}</span></div>
        </div>
        
        <div id="diversity" class="section">
            {make_section_title("diversity", "html_diversity")}
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-number">{stats['shannon_index']['authors']}</div><div class="stat-label">{get_text_local('shannon_authors')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['shannon_index']['journals']}</div><div class="stat-label">{get_text_local('shannon_journals')}</div></div>
                <div class="stat-card"><div class="stat-number">{stats['shannon_index']['publishers']}</div><div class="stat-label">{get_text_local('shannon_publishers')}</div></div>
            </div>
        </div>
        
        <div id="classics" class="section">
            {make_section_title("classics", "html_classics")}
            {citation_classics_html}
        </div>
        
        {f'''
        <div id="selfcitations" class="section">
            {make_section_title("selfcitation", "html_self_citations")}
            {authors_header_html}
            {self_citations_html}
            <div style="margin-top: 15px;"><span class="badge badge-info">{get_text_local('html_total_self_citations')}: {self_citations_count} ({self_citations_percent:.1f}%)</span></div>
        </div>
        ''' if show_self_citations_section else ''}
        
        {reviewers_html}
        
        {duplicates_html}
        
        <div id="crossref_only" class="section">
            {make_section_title("crossref", "html_crossref_only")}
            {''.join([f'<div class="rank-item"><div>{html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('crossref_only_refs', [])[:20]]) if stats.get('crossref_only_refs') else f'<p>{get_text_local("no_crossref_only")}</p>'}
        </div>
        
        <div id="openalex_only" class="section">
            {make_section_title("openalex", "html_openalex_only")}
            {''.join([f'<div class="rank-item"><div>{html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('openalex_only_refs', [])[:20]]) if stats.get('openalex_only_refs') else f'<p>{get_text_local("no_openalex_only")}</p>'}
        </div>
        
        <div id="suspicious_doi" class="section">
            {make_section_title("suspicious", "html_suspicious_doi")}
            <div style="margin-bottom: 15px; font-size: 13px; color: #666;">{get_text_local('suspicious_dois_hint')}</div>
            {f'''
            <div style="margin-top: 10px; margin-bottom: 15px;"><h4>{get_text_local("repository")} {get_text_local("references")}:</h4><div style="font-size: 12px; color: #5e2a9e; margin-bottom: 10px;">{get_text_local("html_repository_note")}</div>{''.join([f'<div class="rank-item repository-reference"><span class="badge-repository">{get_text_local("repository")}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div>' + (f'<div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div>' if ref.get("doi") else '') + '</div>' for ref in stats.get('repository_refs', [])[:20]])}</div>
            ''' if stats.get('repository_refs') else ''}
            {f'''
            <div style="margin-top: 10px; margin-bottom: 15px;"><h4>{get_text_local("proceedings")} {get_text_local("references")}:</h4><div style="font-size: 12px; color: #b26b00; margin-bottom: 10px;">{get_text_local("html_proceedings_note")}</div>{''.join([f'<div class="rank-item proceedings-reference"><span class="badge-proceedings">{get_text_local("proceedings")}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div>' + (f'<div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div>' if ref.get("doi") else '') + '</div>' for ref in stats.get('proceedings_refs', [])[:20]])}</div>
            ''' if stats.get('proceedings_refs') else ''}
            <div style="margin-top: 10px;"><h4>{get_text_local("suspicious_dois")}:</h4>{''.join([f'<div class="rank-item suspicious-reference"><div class="badge badge-danger">{get_text_local("html_attention")}</div><div>{html.escape(ref["text"])}</div><div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div></div>' for ref in stats.get('suspicious_doi_refs', [])[:20]]) if stats.get('suspicious_doi_refs') else f'<p>{get_text_local("no_suspicious_dois")}</p>'}</div>
        </div>
        
        <div id="non_doi" class="section">
            {make_section_title("nondoi", "html_non_doi")}
            {f'''
            <div style="margin-bottom: 15px;"><h4>{get_text_local("books_count")} (ISBN without DOI):</h4>{''.join([f'<div class="rank-item book-reference"><span class="badge-book">{get_text_local("ebook")}</span><div style="margin-top: 8px;">{html.escape(ref)}</div></div>' for ref in stats.get('books_with_isbn_no_doi', [])[:20]])}</div>
            ''' if stats.get('books_with_isbn_no_doi') else ''}
            <div><h4>{get_text_local("other")} {get_text_local("non_doi_sources")}:</h4>{''.join([f'<div class="rank-item notfound-reference">{html.escape(ref)}</div>' for ref in stats['identifier_coverage']['references_without_doi'][:20]]) if stats['identifier_coverage']['references_without_doi'] else f'<p>{get_text_local("all_have_doi")}</p>'}</div>
        </div>
        
        {non_journal_sources_html}
        
        <div id="url_sources" class="section">
            {make_section_title("url", "html_url_sources")}
            {''.join([f'<div class="rank-item">{html.escape(ref)}</div>' for ref in stats['identifier_coverage']['references_with_only_url'][:20]]) if stats['identifier_coverage']['references_with_only_url'] else f'<p>{get_text_local("no_url_only")}</p>'}
        </div>
        
        <div id="problems" class="section">
            {make_section_title("problems", "html_problems")}
            {f'''
            <div style="margin-bottom: 20px;"><h4>{get_text_local("retracted_count")}:</h4>{''.join([f'<div class="rank-item retracted-reference"><span class="badge-danger" style="background: #f8d7da; color: #721c24;">{get_text_local("retracted")}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div>' + (f'<div style="font-size: 11px; margin-top: 5px;">DOI: {make_clickable_doi(ref["doi"])}</div>' if ref.get("doi") else '') + '</div>' for ref in stats.get('retracted_refs', [])[:20]]) if stats.get('retracted_refs') else f'<p>{get_text_local("none_detected")}</p>'}</div>
            ''' if stats.get('retracted_refs') else ''}
            <div><h4>{get_text_local("other")} {get_text_local("problematic_refs")}:</h4>{''.join([f'<div class="rank-item"><span class="badge badge-warning">{html.escape(ref["problems"])}</span><div style="margin-top: 8px;">{html.escape(ref["text"])}</div></div>' for ref in stats['problematic_refs'][:10]]) if stats['problematic_refs'] else f'<p>{get_text_local("no_problematic")}</p>'}</div>
        </div>
        
        <div id="full_reference_list" class="section">
            {make_section_title("list", "full_reference_list_title")}
            {full_references_html}
            {f'<p style="margin-top: 15px; color: #666;">{get_text_local("showing_first").format(300, len(results))}</p>' if len(results) > 300 else ''}
        </div>
        
        <div class="footer">
            {get_text_local('html_footer')}<br>
            {get_text_local('html_copyright')}
        </div>
    </div>
</body>
</html>"""
    
    return html_content

# ======================== UI INTERFACE (UPDATED LAYOUT) ========================
def main():
    # Language selector in sidebar (first)
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
        
        # Paper authors (second)
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
        
        # Journal name (third)
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
        
        st.markdown("---")
        
        # Article number (fourth)
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
        
        # Propose potential reviewers (fifth)
        st.markdown(f"## {get_text('propose_reviewers')}")
        show_reviewers = st.checkbox(
            get_text('propose_reviewers'),
            value=st.session_state.get('show_reviewers', False),
            help=get_text('propose_reviewers_help')
        )
        st.session_state.show_reviewers = show_reviewers
        
        st.markdown("---")
        
        # Color Theme (sixth)
        st.markdown(f"## 🎨 Color Theme")
        
        if 'primary_color' not in st.session_state:
            st.session_state.primary_color = '#667eea'
        if 'secondary_color' not in st.session_state:
            st.session_state.secondary_color = '#f39c12'
        
        preset_themes = {
            "Default (Blue-Purple)": {"primary": "#667eea", "secondary": "#9b59b6"},
            "Emerald (Green-Teal)": {"primary": "#2ecc71", "secondary": "#27ae60"},
            "Sunset (Orange-Coral)": {"primary": "#e74c3c", "secondary": "#c0392b"},
            "Ocean (Deep Blue)": {"primary": "#3498db", "secondary": "#2980b9"},
            "Royal (Purple-Pink)": {"primary": "#9b59b6", "secondary": "#e84393"},
            "Forest (Dark Green)": {"primary": "#27ae60", "secondary": "#2ecc71"},
            "Cherry (Red-Pink)": {"primary": "#e84393", "secondary": "#9b59b6"},
            "Amber (Yellow-Orange)": {"primary": "#f39c12", "secondary": "#e67e22"},
        }
        
        theme_option = st.selectbox("🎨 Preset themes", options=list(preset_themes.keys()), index=0)
        use_preset = st.checkbox("Use preset theme", value=True)
        
        if use_preset:
            selected_theme = preset_themes[theme_option]
            st.session_state.primary_color = selected_theme["primary"]
            st.session_state.secondary_color = selected_theme["secondary"]
        else:
            selected_color = st.color_picker("🎨 Pick your primary color", value=st.session_state.primary_color)
            st.session_state.primary_color = selected_color
            st.session_state.secondary_color = get_complementary_color(selected_color)
        
        complementary = st.session_state.secondary_color
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div style="text-align: center;"><div class="color-preview" style="background: {st.session_state.primary_color};"></div><div style="font-size: 11px; margin-top: 5px;">Primary</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="text-align: center;"><div class="color-preview" style="background: {complementary};"></div><div style="font-size: 11px; margin-top: 5px;">Complementary</div></div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="complementary-preview" style="height: 8px; width: 100%; margin: 10px 0;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="theme-info">✨ Complementary color automatically selected<br>🎨 Gradient: Primary → Complementary</div>', unsafe_allow_html=True)
        
        secondary = st.session_state.get('secondary_color', get_complementary_color(st.session_state.primary_color))
        apply_theme_css(st.session_state.primary_color, secondary)
        
        st.markdown("---")
        
        # Settings (seventh)
        st.markdown(f"## {get_text('settings')}")
        batch_size = st.slider(get_text('batch_size'), 10, 100, 50, help=get_text('batch_size_help'))
        
        st.markdown("---")
    
    # Main content
    st.image("logo.png", width=250)
    st.markdown("---")
    st.markdown(f"### {get_text('app_subtitle')}")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs([get_text('tab_upload'), get_text('tab_analytics'), get_text('tab_report')])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.header(get_text('upload_header'))
        
        input_method = st.radio(get_text('input_method'), [get_text('text_paste'), get_text('file_upload')])
        
        references_text = ""
        
        if input_method == get_text('text_paste'):
            references_text = st.text_area(get_text('text_paste'), height=400, placeholder=get_text('paste_placeholder'))
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
                            st.session_state['duplicates'] = duplicates
                        else:
                            st.session_state['duplicates'] = []
                    
                    st.session_state['references'] = references
                    st.session_state['paper_authors'] = paper_authors
                    st.session_state['batch_size'] = batch_size
                    st.session_state['analysis_started'] = True
                    
                    with st.spinner(get_text('analysis_started')):
                        results = analyze_all_references_with_new_affiliations(references, batch_size, paper_authors if paper_authors else None)
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
                
                # Get potential reviewers if enabled
                reviewers = []
                paper_author_affiliations = set()
                
                # First, collect affiliations of paper authors
                # We need to get this from somewhere - the paper authors themselves
                # Since we don't have the target paper's data, we'll use the affiliations
                # from the paper_authors set (which are just names, not affiliations)
                # For now, we'll use a placeholder - this should be handled differently
                # In a real scenario, you would have the target paper's data
                # For the purpose of this code, we'll assume we need to get affiliations from
                # somewhere else, but since we don't have that, we'll use the paper_authors set
                # as a fallback for name-based filtering only
                
                if st.session_state.get('show_reviewers', False) and paper_authors:
                    # Get potential reviewers
                    reviewers = get_potential_reviewers(results, paper_authors, set())
                    # Fetch ORCID profiles
                    reviewers = fetch_orcid_profiles_for_reviewers(reviewers)
            
            st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_percent = 100.0
                st.markdown(f'<div class="metric-card"><div class="metric-number">{stats["total_references"]}</div><div class="metric-label">{get_text("total_references")}</div><div style="font-size: 11px; color: #155724; background-color: #d4edda; padding: 2px 8px; border-radius: 12px; margin-top: 5px; display: inline-block;">({total_percent:.1f}%)</div></div>', unsafe_allow_html=True)
            with col2:
                doi_percent = stats.get('total_with_doi_percent', 0)
                st.markdown(f'<div class="metric-card"><div class="metric-number">{stats["total_with_doi"]} ({stats["total_with_doi"]/stats["total_references"]*100 if stats["total_references"] > 0 else 0:.0f}%)</div><div class="metric-label">{get_text("doi_found")}</div><div style="font-size: 11px; color: #155724; background-color: #d4edda; padding: 2px 8px; border-radius: 12px; margin-top: 5px; display: inline-block;">({doi_percent:.1f}%)</div></div>', unsafe_allow_html=True)
            with col3:
                last5_percent = stats['yearly_stats']['last_5_years_percent']
                st.markdown(f'<div class="metric-card"><div class="metric-number">{stats["yearly_stats"]["last_5_years"]}</div><div class="metric-label">{get_text("last_5_years")}</div><div style="font-size: 11px; color: #155724; background-color: #d4edda; padding: 2px 8px; border-radius: 12px; margin-top: 5px; display: inline-block;">({last5_percent:.1f}%)</div></div>', unsafe_allow_html=True)
            with col4:
                self_cit_percent = stats['self_citations_percent']
                st.markdown(f'<div class="metric-card"><div class="metric-number">{stats["self_citations_count"]}</div><div class="metric-label">{get_text("self_citations")}</div><div style="font-size: 11px; color: #155724; background-color: #d4edda; padding: 2px 8px; border-radius: 12px; margin-top: 5px; display: inline-block;">({self_cit_percent:.1f}%)</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.markdown(f'<div class="metric-card"><div class="metric-number">{stats.get("total_citations_sum", 0)}</div><div class="metric-label">{get_text("total_citations")}</div></div>', unsafe_allow_html=True)
            with col6:
                st.markdown(f'<div class="metric-card"><div class="metric-number">{stats.get("avg_citations", 0):.1f}</div><div class="metric-label">{get_text("avg_citations")}</div></div>', unsafe_allow_html=True)
            with col7:
                st.markdown(f'<div class="metric-card"><div class="metric-number">{stats["orcid_coverage"]["coverage_percent"]:.1f}%</div><div class="metric-label">{get_text("orcid_coverage")}</div></div>', unsafe_allow_html=True)
            with col8:
                st.markdown(f'<div class="metric-card"><div class="metric-number">{stats["publisher_frequency"]["unique_publishers"]}</div><div class="metric-label">{get_text("unique_publishers")}</div></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"### {get_text('analysis_sections')}")
            
            if 'active_tab' not in st.session_state:
                st.session_state.active_tab = "metrics"
            
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
                {"id": "problems", "icon": "⚠️", "title": get_text('problematic_refs'), "subtitle": get_text('html_problems')},
            ]
            
            if st.session_state.get('show_reviewers', False):
                tabs_config.insert(11, {"id": "reviewers", "icon": "👥", "title": get_text('potential_reviewers'), "subtitle": "Potential reviewers"})
            
            cols_per_row = 6
            for i in range(0, len(tabs_config), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(tabs_config):
                        tab = tabs_config[i + j]
                        if col.button(f"{tab['icon']}\n{tab['title']}\n{tab['subtitle']}", key=f"tab_{tab['id']}", use_container_width=True):
                            st.session_state.active_tab = tab["id"]
                            st.rerun()
            
            st.markdown("---")
            
            active_tab = st.session_state.active_tab
            
            if active_tab == "metrics":
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {get_text('doi_status')}")
                    doi_data = pd.DataFrame([
                        {"Status": get_text('status_both'), "Count": stats['doi_status']['both'], "Percentage": f"{stats['doi_status_percents']['both']:.1f}%"},
                        {"Status": get_text('status_crossref_only'), "Count": stats['doi_status']['crossref_only'], "Percentage": f"{stats['doi_status_percents']['crossref_only']:.1f}%"},
                        {"Status": get_text('status_openalex_only'), "Count": stats['doi_status']['openalex_only'], "Percentage": f"{stats['doi_status_percents']['openalex_only']:.1f}%"},
                        {"Status": get_text('status_none'), "Count": stats['doi_status']['none'], "Percentage": f"{stats['doi_status_percents']['none']:.1f}%"}
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
                    {"Identifier type": "DOI", "Count": stats['identifier_coverage']['stats']['has_doi'], "Percentage": f"{stats['identifier_coverage_percents']['has_doi']:.1f}%"},
                    {"Identifier type": "URL", "Count": stats['identifier_coverage']['stats']['has_url'], "Percentage": f"{stats['identifier_coverage_percents']['has_url']:.1f}%"},
                    {"Identifier type": get_text('preprint_repository_count'), "Count": stats['identifier_coverage']['stats']['has_arxiv'], "Percentage": f"{stats['identifier_coverage_percents']['has_arxiv']:.1f}%"},
                    {"Identifier type": "PMID", "Count": stats['identifier_coverage']['stats']['has_pmid'], "Percentage": f"{stats['identifier_coverage_percents']['has_pmid']:.1f}%"},
                    {"Identifier type": get_text('preprint_repository_count') + " (from API)", "Count": stats['identifier_coverage']['stats']['is_preprint_repository'], "Percentage": f"{stats['identifier_coverage_percents']['preprint_repository']:.1f}%"},
                    {"Identifier type": get_text('proceedings_count'), "Count": stats['identifier_coverage']['stats']['is_proceedings'], "Percentage": f"{stats['identifier_coverage_percents']['proceedings']:.1f}%"},
                    {"Identifier type": get_text('retracted_count'), "Count": stats['identifier_coverage']['stats']['is_retracted'], "Percentage": f"{stats['identifier_coverage_percents']['retracted']:.1f}%"},
                    {"Identifier type": get_text('no_identifier'), "Count": stats['identifier_coverage']['stats']['has_none'], "Percentage": f"{stats['identifier_coverage_percents']['has_none']:.1f}%"},
                    {"Identifier type": "Multiple identifiers", "Count": stats['identifier_coverage']['stats']['multiple'], "Percentage": f"{stats['identifier_coverage_percents']['multiple']:.1f}%"}
                ])
                st.dataframe(id_df, use_container_width=True)
                
                if stats['identifier_coverage']['references_without_any']:
                    st.markdown(f"### {get_text('references_without_any')}")
                    for ref in stats['identifier_coverage']['references_without_any'][:10]:
                        st.text(ref)
            
            elif active_tab == "authors":
                display_top_authors(stats)
            
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
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric(f"Last Year ({stats['yearly_stats']['last_completed_year']})", f"{stats['yearly_stats']['last_year']} ({stats['yearly_stats']['last_year_percent']:.1f}%)")
                with col2:
                    st.metric(get_text('last_3_years'), f"{stats['yearly_stats']['last_3_years']} ({stats['yearly_stats']['last_3_years_percent']:.1f}%)")
                with col3:
                    st.metric(get_text('last_5_years_metric'), f"{stats['yearly_stats']['last_5_years']} ({stats['yearly_stats']['last_5_years_percent']:.1f}%)")
                with col4:
                    st.metric(get_text('last_10_years'), f"{stats['yearly_stats']['last_10_years']} ({stats['yearly_stats']['last_10_years_percent']:.1f}%)")
                with col5:
                    st.metric(get_text('references_with_unknown_year'), stats['yearly_stats']['unknown_year'])
                
                st.markdown(f"#### {get_text('distribution_by_year')}")
                years_df = pd.DataFrame(list(stats['yearly_stats']['yearly_counts'].items()), columns=["Year", "Count"])
                years_df = years_df.sort_values("Year", ascending=False)
                st.bar_chart(years_df.set_index("Year"))
                
                st.markdown(f"#### {get_text('detailed_yearly_data')}")
                yearly_data = []
                for year in sorted(stats['yearly_stats']['yearly_counts'].keys(), reverse=True):
                    yearly_data.append({"Year": year, "Count": stats['yearly_stats']['yearly_counts'][year], "Percentage": f"{stats['yearly_stats']['yearly_percentages'][year]:.1f}%", "Cumulative %": f"{stats['yearly_stats']['cumulative_percentages'][year]:.1f}%"})
                st.dataframe(pd.DataFrame(yearly_data), use_container_width=True)
                st.markdown(f"**{get_text('references_with_known_year')}:** {stats['yearly_stats']['total_with_year']}")
            
            elif active_tab == "concepts":
                st.markdown(f"### {get_text('key_concepts')}")
                concepts_df = pd.DataFrame(stats['concepts']['concepts'][:15], columns=["Concept", "Frequency"])
                st.dataframe(concepts_df, use_container_width=True)
            
            elif active_tab == "geography":
                display_geography_section(stats)
            
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
                    for classic in stats['citation_classics']:
                        with st.expander(f"{classic['title'][:100]}..."):
                            st.markdown(f"**{get_text('citations')}:** {classic['citations']}")
                            st.markdown(f"**{get_text('journal')}:** {classic['journal']}")
                            st.markdown(f"**{get_text('year')}:** {classic['year']}")
                            if classic.get('doi'):
                                st.markdown(f"**DOI:** <a href='https://doi.org/{classic['doi']}' target='_blank' style='color: #667eea; text-decoration: none;'>{classic['doi']}</a>", unsafe_allow_html=True)
                else:
                    st.info(get_text('no_citation_classics'))
            
            elif active_tab == "reviewers" and st.session_state.get('show_reviewers', False):
                st.markdown(f"### {get_text('potential_reviewers')}")
                if reviewers:
                    for i, reviewer in enumerate(reviewers[:30], 1):
                        display_reviewer_card(reviewer, i)
                    st.info(f"Showing {min(len(reviewers), 30)} potential reviewers (max 30, max 3 per affiliation)")
                else:
                    st.info("No potential reviewers found matching the criteria (not self-cited, different affiliation, recent publication)")
            
            elif active_tab == "crossref_only":
                st.markdown(f"### {get_text('crossref_only')}")
                if stats.get('crossref_only_refs'):
                    for ref in stats['crossref_only_refs'][:20]:
                        doi_link = f"<a href='https://doi.org/{ref['doi']}' target='_blank' style='color: #667eea; text-decoration: none;'>{ref['doi']}</a>"
                        st.warning(f"📄 {ref['text']}\n\nDOI: {doi_link}", unsafe_allow_html=True)
                else:
                    st.success(get_text('no_crossref_only'))
            
            elif active_tab == "openalex_only":
                st.markdown(f"### {get_text('openalex_only')}")
                if stats.get('openalex_only_refs'):
                    for ref in stats['openalex_only_refs'][:20]:
                        doi_link = f"<a href='https://doi.org/{ref['doi']}' target='_blank' style='color: #667eea; text-decoration: none;'>{ref['doi']}</a>"
                        st.info(f"📄 {ref['text']}\n\nDOI: {doi_link}", unsafe_allow_html=True)
                else:
                    st.success(get_text('no_openalex_only'))
            
            elif active_tab == "suspicious":
                st.markdown(f"### {get_text('suspicious_dois')}")
                st.markdown(get_text('suspicious_dois_hint'))
                if stats.get('repository_refs'):
                    st.markdown(f"#### {get_text('repository')} {get_text('references')}")
                    st.caption(get_text('html_repository_note'))
                    for ref in stats['repository_refs'][:20]:
                        doi_link = f"<a href='https://doi.org/{ref['doi']}' target='_blank' style='color: #667eea; text-decoration: none;'>{ref['doi']}</a>" if ref.get('doi') else get_text('not_found')
                        st.info(f"📚 {ref['text']}\n\nDOI: {doi_link}", unsafe_allow_html=True)
                if stats.get('proceedings_refs'):
                    st.markdown(f"#### {get_text('proceedings')} {get_text('references')}")
                    st.caption(get_text('html_proceedings_note'))
                    for ref in stats['proceedings_refs'][:20]:
                        doi_link = f"<a href='https://doi.org/{ref['doi']}' target='_blank' style='color: #667eea; text-decoration: none;'>{ref['doi']}</a>" if ref.get('doi') else get_text('not_found')
                        st.warning(f"📊 {ref['text']}\n\nDOI: {doi_link}", unsafe_allow_html=True)
                if stats.get('suspicious_doi_refs'):
                    st.markdown(f"#### {get_text('suspicious_dois')}")
                    for ref in stats['suspicious_doi_refs'][:20]:
                        doi_link = f"<a href='https://doi.org/{ref['doi']}' target='_blank' style='color: #667eea; text-decoration: none;'>{ref['doi']}</a>"
                        st.error(f"⚠️ {ref['text']}\n\nDOI: {doi_link}", unsafe_allow_html=True)
                elif not stats.get('repository_refs') and not stats.get('proceedings_refs'):
                    st.success(get_text('no_suspicious_dois'))
            
            elif active_tab == "non_doi":
                st.markdown(f"### {get_text('non_doi_sources')}")
                if stats.get('books_with_isbn_no_doi'):
                    st.markdown(f"#### {get_text('books_count')} (ISBN without DOI)")
                    for ref in stats['books_with_isbn_no_doi'][:20]:
                        st.markdown(f"<div class='rank-item book-reference'><span class='badge-book'>{get_text('ebook')}</span><div style='margin-top: 8px;'>{html.escape(ref)}</div></div>", unsafe_allow_html=True)
                if stats['identifier_coverage']['references_without_doi']:
                    st.markdown(f"#### {get_text('other')} {get_text('non_doi_sources')}")
                    for ref in stats['identifier_coverage']['references_without_doi'][:20]:
                        if not any(book_ref == ref for book_ref in stats.get('books_with_isbn_no_doi', [])):
                            st.text(ref)
                elif not stats.get('books_with_isbn_no_doi'):
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
                if stats.get('retracted_refs'):
                    st.markdown(f"#### {get_text('retracted_count')}")
                    for ref in stats['retracted_refs'][:20]:
                        doi_link = f"<a href='https://doi.org/{ref['doi']}' target='_blank' style='color: #667eea; text-decoration: none;'>{ref['doi']}</a>" if ref.get('doi') else get_text('not_found')
                        st.error(f"⚠️ {get_text('retracted')}: {ref['text']}\n\nDOI: {doi_link}", unsafe_allow_html=True)
                if stats['problematic_refs']:
                    st.markdown(f"#### {get_text('other')} {get_text('problematic_refs')}")
                    for ref in stats['problematic_refs'][:15]:
                        st.warning(f"**{ref['problems']}**\n\n{ref['text']}")
                if not stats['problematic_refs'] and not stats.get('retracted_refs'):
                    st.success(get_text('no_problematic'))
            
            st.markdown("---")
            st.markdown(f"### {get_text('full_reference_list')}")
            
            if 'filter_states' not in st.session_state:
                st.session_state.filter_states = {
                    'doi_only': False, 'non_doi_only': False, 'url_only': False,
                    'crossref_only': False, 'openalex_only': False, 'problematic_only': False,
                    'self_cited_only': False, 'preprint_repository_only': False,
                    'books_only': False, 'proceedings_only': False, 'retracted_only': False
                }
            
            def toggle_filter(filter_name, is_checked):
                if is_checked:
                    for key in st.session_state.filter_states:
                        st.session_state.filter_states[key] = False
                    st.session_state.filter_states[filter_name] = True
                else:
                    st.session_state.filter_states[filter_name] = False
            
            has_preprint_repository = any(r.get('is_repository', False) for r in results)
            has_books = any(r.get('is_ebook', False) or (r.get('identifiers', {}).get('isbn') and not r.get('doi')) for r in results)
            has_proceedings = any(r.get('is_proceedings', False) for r in results)
            has_retracted = any(r.get('is_retracted', False) for r in results)
            
            col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
            with col_filter1:
                doi_only = st.checkbox(get_text('only_with_doi'), value=st.session_state.filter_states['doi_only'], key="filter_doi_only", on_change=lambda: toggle_filter('doi_only', st.session_state.filter_doi_only))
            with col_filter2:
                non_doi_only = st.checkbox(get_text('only_non_doi'), value=st.session_state.filter_states['non_doi_only'], key="filter_non_doi_only", on_change=lambda: toggle_filter('non_doi_only', st.session_state.filter_non_doi_only))
            with col_filter3:
                url_only = st.checkbox(get_text('url_links'), value=st.session_state.filter_states['url_only'], key="filter_url_only", on_change=lambda: toggle_filter('url_only', st.session_state.filter_url_only))
            with col_filter4:
                crossref_only = st.checkbox(get_text('only_crossref'), value=st.session_state.filter_states['crossref_only'], key="filter_crossref_only", on_change=lambda: toggle_filter('crossref_only', st.session_state.filter_crossref_only))
            
            col_filter5, col_filter6, col_filter7, col_filter8 = st.columns(4)
            with col_filter5:
                openalex_only = st.checkbox(get_text('only_openalex'), value=st.session_state.filter_states['openalex_only'], key="filter_openalex_only", on_change=lambda: toggle_filter('openalex_only', st.session_state.filter_openalex_only))
            with col_filter6:
                problematic_only = st.checkbox(get_text('problematic_only'), value=st.session_state.filter_states['problematic_only'], key="filter_problematic_only", on_change=lambda: toggle_filter('problematic_only', st.session_state.filter_problematic_only))
            with col_filter7:
                self_cited_only = st.checkbox(get_text('self_cited_only'), value=st.session_state.filter_states['self_cited_only'], key="filter_self_cited_only", on_change=lambda: toggle_filter('self_cited_only', st.session_state.filter_self_cited_only))
            with col_filter8:
                search_term = st.text_input(get_text('search_in_text'), placeholder=get_text('search_placeholder'))
            
            col_filter9, col_filter10, col_filter11, col_filter12 = st.columns(4)
            with col_filter9:
                if has_preprint_repository:
                    preprint_repo_only = st.checkbox(get_text('only_preprint_repository'), value=st.session_state.filter_states['preprint_repository_only'], key="filter_preprint_repo_only", on_change=lambda: toggle_filter('preprint_repository_only', st.session_state.filter_preprint_repo_only))
            with col_filter10:
                if has_books:
                    books_only = st.checkbox(get_text('only_books'), value=st.session_state.filter_states['books_only'], key="filter_books_only", on_change=lambda: toggle_filter('books_only', st.session_state.filter_books_only))
            with col_filter11:
                if has_proceedings:
                    proceedings_only = st.checkbox(get_text('only_proceedings'), value=st.session_state.filter_states['proceedings_only'], key="filter_proceedings_only", on_change=lambda: toggle_filter('proceedings_only', st.session_state.filter_proceedings_only))
            with col_filter12:
                if has_retracted:
                    retracted_only = st.checkbox(get_text('only_retracted'), value=st.session_state.filter_states['retracted_only'], key="filter_retracted_only", on_change=lambda: toggle_filter('retracted_only', st.session_state.filter_retracted_only))
            
            filtered_results = results
            
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
            if st.session_state.filter_states['preprint_repository_only']:
                filtered_results = [r for r in filtered_results if r.get('is_repository', False) or r.get('type') == 'posted_content']
            if st.session_state.filter_states['books_only']:
                filtered_results = [r for r in filtered_results if r.get('is_ebook', False) or (r.get('identifiers', {}).get('isbn') and not r.get('doi'))]
            if st.session_state.filter_states['proceedings_only']:
                filtered_results = [r for r in filtered_results if r.get('is_proceedings', False)]
            if st.session_state.filter_states['retracted_only']:
                filtered_results = [r for r in filtered_results if r.get('is_retracted', False)]
            if search_term:
                filtered_results = [r for r in filtered_results if search_term.lower() in r['original_text'].lower()]
            
            st.markdown(get_text('showing').format(len(filtered_results), len(results)))
            
            paper_authors_set = set()
            normalized_paper_authors = set()
            if paper_authors:
                for author in paper_authors:
                    paper_authors_set.add(author)
                    norm, _ = normalize_author_name(author)
                    normalized_paper_authors.add(norm)
            
            def format_authors_with_highlight_streamlit(authors_list, highlight_set, normalize_func):
                if not authors_list:
                    return ""
                formatted_authors = []
                for author in authors_list:
                    norm_author, _ = normalize_func(author)
                    if norm_author in highlight_set:
                        formatted_authors.append(f'<span style="color: #d9534f; font-weight: bold; background-color: #f8d7da; padding: 2px 4px; border-radius: 3px;">{html.escape(author)}</span>')
                    else:
                        formatted_authors.append(html.escape(author))
                return ', '.join(formatted_authors)
            
            for i, result in enumerate(filtered_results[:50]):
                if result.get('is_suspicious_doi'):
                    status_icon = "⚠️"
                elif result['doi']:
                    status_icon = "✅"
                else:
                    status_icon = "❌"
                
                problems_badges = []
                if result.get('is_retracted'):
                    problems_badges.append(f'<span class="badge-danger">{get_text("retracted")}</span>')
                if result.get('is_preprint'):
                    problems_badges.append(f'<span class="badge-warning">{get_text("preprint")}</span>')
                if result.get('is_repository'):
                    problems_badges.append(f'<span class="badge-repository">{get_text("repository")}</span>')
                if result.get('is_ebook'):
                    problems_badges.append(f'<span class="badge-book">{get_text("ebook")}</span>')
                if result.get('is_proceedings'):
                    problems_badges.append(f'<span class="badge-proceedings">{get_text("proceedings")}</span>')
                if result.get('is_self_citation'):
                    problems_badges.append(f'<span class="badge-info">{get_text("self_citation")}</span>')
                if result.get('is_suspicious_doi'):
                    problems_badges.append(f'<span class="badge-danger">{get_text("suspicious_doi_badge")}</span>')
                
                badges_html = ' '.join(problems_badges)
                
                special_class = ""
                if result.get('is_ebook', False):
                    special_class = "ebook-reference"
                elif result.get('is_repository', False):
                    special_class = "repository-reference"
                elif result.get('is_proceedings', False):
                    special_class = "proceedings-reference"
                
                if result['is_self_citation'] and normalized_paper_authors:
                    authors_display_html = format_authors_with_highlight_streamlit(result['authors_display'], normalized_paper_authors, normalize_author_name)
                else:
                    authors_display_html = ', '.join([html.escape(a) for a in result['authors_display'][:5]]) if result['authors_display'] else ""
                
                doi_display = ""
                if result['doi']:
                    doi_display = f'<a href="https://doi.org/{result["doi"]}" target="_blank" style="color: #667eea; text-decoration: none;">{result["doi"]}</a>'
                else:
                    doi_display = get_text('not_found')
                
                expander_label = f"{status_icon} {result['original_text'][:150]}..."
                if special_class:
                    expander_label = f"{status_icon} <span class='{special_class}' style='display: inline-block; padding: 2px 8px; border-radius: 12px;'>{result['original_text'][:130]}...</span>"
                
                with st.expander(expander_label):
                    st.markdown(f"**DOI:** {doi_display}", unsafe_allow_html=True)
                    identifiers = result.get('identifiers', {})
                    if identifiers.get('url'):
                        st.markdown(f"**URL:** {identifiers['url']}")
                    if identifiers.get('arxiv'):
                        st.markdown(f"**arXiv:** {identifiers['arxiv']}")
                    if identifiers.get('isbn'):
                        st.markdown(f"**ISBN:** {identifiers['isbn']}")
                    st.markdown(f"**{get_text('status')}:** Crossref: {'✅' if result['crossref_status'] else '❌'} | OpenAlex: {'✅' if result['openalex_status'] else '❌'}")
                    if result.get('openalex_type'):
                        st.markdown(f"**OpenAlex type:** {result['openalex_type']}")
                    if result['journal']:
                        st.markdown(f"**{get_text('journal')}:** {result['journal']}")
                    if result['year']:
                        st.markdown(f"**{get_text('year')}:** {result['year']}")
                    if authors_display_html:
                        st.markdown(f"**{get_text('authors')}:** {authors_display_html}", unsafe_allow_html=True)
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
            duplicates = st.session_state.get('duplicates', [])
            show_reviewers_flag = st.session_state.get('show_reviewers', False)
            
            stats = generate_advanced_statistics(results)
            
            reviewers = []
            if show_reviewers_flag and paper_authors:
                reviewers = get_potential_reviewers(results, paper_authors, set())
                reviewers = fetch_orcid_profiles_for_reviewers(reviewers)
            
            st.markdown(f"### {get_text('export_report')}")
            st.markdown(get_text('download_html'))
            
            primary_color = st.session_state.get('primary_color', '#667eea')
            secondary_color = st.session_state.get('secondary_color', get_complementary_color(primary_color))
            
            html_report = generate_html_report_advanced(
                results, stats, paper_authors, st.session_state.language,
                journal_name, article_number, duplicates, primary_color, secondary_color,
                show_reviewers_flag, reviewers
            )
            
            def get_journal_abbreviation(journal_name: str) -> str:
                abbreviations = {'chimica techno acta': 'CTA', 'materials reports energy': 'MRE'}
                journal_lower = journal_name.lower().strip()
                for full, abbr in abbreviations.items():
                    if full in journal_lower:
                        return abbr
                words = re.findall(r'[A-Za-z][a-z]*', journal_name)
                if words:
                    abbr = ''.join(word[0].upper() for word in words[:3])
                    return abbr if abbr else "JRNL"
                return "JRNL"
            
            def sanitize_filename(s: str) -> str:
                s = re.sub(r'[^a-z0-9]+', '_', s.lower().strip())
                s = s.strip('_')
                return s if s else "report"
            
            if journal_name and journal_name.strip():
                journal_abbr = get_journal_abbreviation(journal_name)
            else:
                journal_abbr = "CTA"
            
            if article_number and article_number.strip():
                num_part = sanitize_filename(article_number)
                num_part = re.sub(r'[^a-z0-9\-]', '', num_part)
                file_name = f"{journal_abbr}_{num_part}.html"
            else:
                file_name = f"{journal_abbr}.html"
            
            st.download_button(label=get_text('download_html'), data=html_report.encode('utf-8'), file_name=file_name, mime="text/html")
            
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
    References last 5 years: {stats['yearly_stats']['last_5_years']} ({stats['yearly_stats']['last_5_years_percent']:.1f}%)
    Self-citations: {stats['self_citations_count']} ({stats['self_citations_percent']:.1f}%)
    Total citations: {stats.get('total_citations_sum', 0)}
    Average citations: {stats.get('avg_citations', 0):.1f}
    
    === IDENTIFIER COVERAGE ===
    DOI: {stats['identifier_coverage']['stats']['has_doi']} ({stats['identifier_coverage_percents']['has_doi']:.1f}%)
    URL: {stats['identifier_coverage']['stats']['has_url']} ({stats['identifier_coverage_percents']['has_url']:.1f}%)
    PMID: {stats['identifier_coverage']['stats']['has_pmid']} ({stats['identifier_coverage_percents']['has_pmid']:.1f}%)
    Preprint/Repository: {stats['identifier_coverage']['stats']['is_preprint_repository']} ({stats['identifier_coverage_percents']['preprint_repository']:.1f}%)
    Ebook Platform (with DOI): {stats['identifier_coverage']['stats']['is_ebook_platform']} ({stats['identifier_coverage_percents']['ebook_platform']:.1f}%)
    Books (ISBN only): {stats['identifier_coverage']['stats']['is_book_no_doi']} ({stats['identifier_coverage_percents']['book_no_doi']:.1f}%)
    Proceedings: {stats['identifier_coverage']['stats']['is_proceedings']} ({stats['identifier_coverage_percents']['proceedings']:.1f}%)
    Retracted: {stats['identifier_coverage']['stats']['is_retracted']} ({stats['identifier_coverage_percents']['retracted']:.1f}%)
    No identifier: {stats['identifier_coverage']['stats']['has_none']} ({stats['identifier_coverage_percents']['has_none']:.1f}%)
    Multiple identifiers: {stats['identifier_coverage']['stats']['multiple']} ({stats['identifier_coverage_percents']['multiple']:.1f}%)
    
    === DOI STATUS ===
    Crossref + OpenAlex: {stats['doi_status']['both']} ({stats['doi_status_percents']['both']:.1f}%)
    Only Crossref: {stats['doi_status']['crossref_only']} ({stats['doi_status_percents']['crossref_only']:.1f}%)
    Only OpenAlex: {stats['doi_status']['openalex_only']} ({stats['doi_status_percents']['openalex_only']:.1f}%)
    No data: {stats['doi_status']['none']} ({stats['doi_status_percents']['none']:.1f}%)
    Suspicious DOIs: {len(stats.get('suspicious_doi_refs', []))}
    Repository sources: {len(stats.get('repository_refs', []))}
    Proceedings sources: {len(stats.get('proceedings_refs', []))}
    
    === DUPLICATES ===
    Full DOI matches found: {len(duplicates) if duplicates else 0}
    {chr(10).join([f"References {dup['index1']+1} and {dup['index2']+1}: {dup['doi']}" for dup in (duplicates if duplicates else [])]) if duplicates else "No full DOI duplicates found"}
    
    === TOP AUTHORS (MERGED) ===
    {chr(10).join([f"{i+1}. {a['display_name']}: {a['count']} citations" + (f" (ORCID: {a['orcid']})" if a.get('orcid') else "") for i, a in enumerate(stats['author_frequency_all']['all_authors'][:20])])}
    
    === ORCID COVERAGE ===
    Total authors: {stats['orcid_coverage']['total_authors']}
    With ORCID: {stats['orcid_coverage']['with_orcid']} ({stats['orcid_coverage']['coverage_percent']:.1f}%)
    
    === YEARLY STATISTICS ===
    Last year ({stats['yearly_stats']['last_completed_year']}): {stats['yearly_stats']['last_year']} ({stats['yearly_stats']['last_year_percent']:.1f}%)
    Last 3 years: {stats['yearly_stats']['last_3_years']} ({stats['yearly_stats']['last_3_years_percent']:.1f}%)
    Last 5 years: {stats['yearly_stats']['last_5_years']} ({stats['yearly_stats']['last_5_years_percent']:.1f}%)
    Last 10 years: {stats['yearly_stats']['last_10_years']} ({stats['yearly_stats']['last_10_years_percent']:.1f}%)
    Unknown year: {stats['yearly_stats']['unknown_year']}
    
    === YEARLY DISTRIBUTION ===
    {chr(10).join([f"{year}: {stats['yearly_stats']['yearly_counts'][year]} ({stats['yearly_stats']['yearly_percentages'][year]:.1f}%)" for year in sorted(stats['yearly_stats']['yearly_counts'].keys(), reverse=True)[:15]])}
    
    === KEY CONCEPTS ===
    {chr(10).join([f"{c[0]}: {c[1]}" for c in stats['concepts']['concepts'][:10]])}
    
    === TOP JOURNALS ===
    {chr(10).join([f"{j['journal']}: {j['count']} ({j['percentage']:.1f}%)" for j in stats['journal_frequency_all']['all_journals'][:15]])}
    
    === TOP PUBLISHERS ===
    {chr(10).join([f"{p['publisher']}: {p['count']} ({p['percentage']:.1f}%)" for p in stats['publisher_frequency']['all_publishers'][:15]])}
    
    === DIVERSITY INDICES ===
    Authors (Shannon): {stats['shannon_index']['authors']}
    Journals (Shannon): {stats['shannon_index']['journals']}
    Publishers (Shannon): {stats['shannon_index']['publishers']}
    
    === CITATION CLASSICS ===
    {chr(10).join([f"{i+1}. {c['title'][:100] if c['title'] else 'Unknown'}: {c['citations']} citations" for i, c in enumerate(stats['citation_classics'])]) if stats['citation_classics'] else "No citation classics detected (threshold: >300 citations)"}
    
    === RETRACTED ARTICLES ===
    {chr(10).join([f"- {ref['text'][:100]}... DOI: {ref.get('doi', 'N/A')}" for ref in stats.get('retracted_refs', [])[:5]]) if stats.get('retracted_refs') else "No retracted articles detected"}
    
    === REPOSITORY SOURCES ===
    {chr(10).join([f"- {ref['text'][:100]}... DOI: {ref.get('doi', 'N/A')}" for ref in stats.get('repository_refs', [])[:5]]) if stats.get('repository_refs') else "No repository sources detected"}
    
    === PROCEEDINGS SOURCES ===
    {chr(10).join([f"- {ref['text'][:100]}... DOI: {ref.get('doi', 'N/A')}" for ref in stats.get('proceedings_refs', [])[:5]]) if stats.get('proceedings_refs') else "No proceedings sources detected"}
    
    === BOOKS (ISBN without DOI) ===
    {chr(10).join([f"- {ref[:100]}..." for ref in stats.get('books_with_isbn_no_doi', [])[:5]]) if stats.get('books_with_isbn_no_doi') else "No books with ISBN without DOI detected"}
    
    === PROBLEMATIC REFERENCES ===
    {chr(10).join([f"- {ref['problems']}: {ref['text'][:100]}..." for ref in stats['problematic_refs'][:5]]) if stats['problematic_refs'] else "No problematic references detected"}
    """
            
            if show_reviewers_flag and reviewers:
                copy_text += "\n\n=== POTENTIAL REVIEWERS ===\n"
                for i, reviewer in enumerate(reviewers[:30], 1):
                    orcid_info = f" (ORCID: {reviewer.get('orcid', 'N/A')})" if reviewer.get('orcid') else ""
                    copy_text += f"{i}. {reviewer.get('name', 'Unknown')}{orcid_info}\n"
                    copy_text += f"   Publication: {reviewer.get('doi', 'N/A')} ({reviewer.get('publication_year', 'Unknown')})\n"
                    if reviewer.get('affiliations'):
                        aff_list = [aff if isinstance(aff, str) else aff.get('name', '') for aff in reviewer['affiliations'][:3]]
                        copy_text += f"   Affiliations: {', '.join(aff_list)}\n"
                    if reviewer.get('countries'):
                        copy_text += f"   Countries: {', '.join(reviewer['countries'][:3])}\n"
                    copy_text += "\n"
            
            st.text_area(get_text('text_export'), copy_text, height=400)
            
            if st.button(get_text('copy_to_clipboard')):
                st.write(get_text('copied'))
        else:
            st.info(get_text('run_analysis_first'))

if __name__ == "__main__":
    main()
