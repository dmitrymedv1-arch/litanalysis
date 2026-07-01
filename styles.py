"""
styles.py - Полная система стилей для HTML-отчета
Содержит все темы оформления, базовые стили и генераторы CSS
"""

import colorsys
import random
from typing import Dict, Optional, List, Tuple

# ======================== БАЗОВЫЕ УТИЛИТЫ ДЛЯ ЦВЕТОВ ========================

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
    complementary_hue = (h + 0.5) % 1.0
    complementary_rgb = colorsys.hsv_to_rgb(complementary_hue, s, v)
    return rgb_to_hex(tuple(int(c * 255) for c in complementary_rgb))

def get_contrast_color(hex_color: str) -> str:
    """
    Get contrasting color (black or white) for text on a colored background
    Uses luminance calculation for optimal readability
    """
    rgb = hex_to_rgb(hex_color)
    luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
    return '#FFFFFF' if luminance < 0.5 else '#000000'

def get_analogous_colors(hex_color: str, count: int = 2) -> List[str]:
    """
    Generate analogous colors (colors adjacent on color wheel)
    Useful for gradients and accents
    """
    rgb = hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    
    colors = []
    step = 30 / 360.0
    
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
        factor = 0.3 + (i * 0.14)
        new_rgb = tuple(min(255, int(c * (1 + factor * 0.5))) for c in rgb)
        colors.append(rgb_to_hex(new_rgb))
    
    return colors

def inject_color_placeholders(css: str, primary: str, secondary: str = None) -> str:
    """
    Заменяет плейсхолдеры {{PRIMARY}} и {{SECONDARY}} на фактические цвета
    """
    css = css.replace('{{PRIMARY}}', primary)
    if secondary:
        css = css.replace('{{SECONDARY}}', secondary)
    else:
        # Если secondary не передан, генерируем комплементарный цвет
        css = css.replace('{{SECONDARY}}', get_complementary_color(primary))
    return css

def get_random_neon_color() -> str:
    """Генерирует случайный неоновый цвет для киберпанк темы"""
    neon_colors = [
        '#00ff41', # Матричный зеленый
        '#ff00ff', # Розовый
        '#00ffff', # Голубой
        '#ff6600', # Оранжевый
        '#ff0044', # Красный
        '#ff00aa', # Пурпурный
        '#00ffaa', # Бирюзовый
        '#ffaa00'  # Желтый
    ]
    return random.choice(neon_colors)

# ======================== БАЗОВЫЕ СТИЛИ (НЕ ЗАВИСЯТ ОТ ТЕМЫ) ========================

BASE_CSS = """
/* ==================== БАЗОВАЯ СТРУКТУРА ==================== */
* { 
    margin: 0; 
    padding: 0; 
    box-sizing: border-box; 
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding: 0;
    margin: 0;
    min-height: 100vh;
}

.report-wrapper {
    max-width: 1400px;
    margin: 0 auto;
    background: transparent;
    position: relative;
}

/* ==================== САЙДБАР ==================== */
.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 260px;
    height: 100vh;
    padding: 30px 20px;
    overflow-y: auto;
    z-index: 1000;
    transition: all 0.3s ease;
}

.sidebar h3 {
    margin-bottom: 20px;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.sidebar a {
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 15px;
    margin: 5px 0;
    border-radius: 8px;
    transition: all 0.3s ease;
    font-size: 14px;
}

.sidebar a:hover {
    transform: translateX(5px);
}

.sidebar-icon {
    width: 22px;
    height: 22px;
    background: transparent;
    display: inline-block;
    vertical-align: middle;
    flex-shrink: 0;
}

/* ==================== ОСНОВНОЙ КОНТЕНТ ==================== */
.main-content {
    margin-left: 260px;
    padding: 30px 40px;
    min-height: 100vh;
}

/* ==================== ЗАГОЛОВОК ==================== */
.header {
    padding: 40px;
    border-radius: 15px;
    margin-bottom: 30px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.header h1 {
    font-size: 32px;
    margin-bottom: 10px;
    font-weight: 700;
}

.header .date {
    opacity: 0.9;
    margin-top: 10px;
    font-size: 14px;
}

.header .badge {
    margin: 5px;
}

/* ==================== СЕТКИ ==================== */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

/* ==================== КАРТОЧКИ ==================== */
.stat-card {
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.stat-card:hover {
    transform: translateY(-5px);
}

.stat-number {
    font-size: 36px;
    font-weight: bold;
    display: block;
    line-height: 1.2;
}

.stat-percent {
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 8px;
    display: inline-block;
    font-weight: 600;
}

.stat-label {
    margin-top: 10px;
    font-size: 14px;
    font-weight: 500;
}

/* ==================== СЕКЦИИ ==================== */
.section {
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 30px;
    transition: all 0.3s ease;
}

.section-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
    padding-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.section-icon {
    width: 28px;
    height: 28px;
    vertical-align: middle;
    display: inline-block;
    background: transparent;
    flex-shrink: 0;
}

/* ==================== СПИСКИ ==================== */
.rank-item {
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    transition: all 0.3s ease;
    position: relative;
}

.rank-item:hover {
    transform: translateX(5px);
}

.rank-number {
    font-weight: bold;
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
}

.progress-bar {
    border-radius: 10px;
    height: 8px;
    margin-top: 8px;
    overflow: hidden;
    background: rgba(0,0,0,0.06);
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.5s ease;
}

/* ==================== БЭЙДЖИ ==================== */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 2px;
}

.badge-success { background: #d4edda; color: #155724; }
.badge-warning { background: #fff3cd; color: #856404; }
.badge-danger { background: #f8d7da; color: #721c24; }
.badge-info { background: #d1ecf1; color: #0c5460; }
.badge-repository { background: #e2d5f8; color: #5e2a9e; }
.badge-book { background: #d4f1e9; color: #0e6b5e; }
.badge-proceedings { background: #fff2c9; color: #b26b00; }

/* ==================== ТАБЛИЦЫ ==================== */
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}

th, td {
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

th {
    font-weight: 600;
    font-size: 14px;
}

tr:hover {
    background: rgba(0,0,0,0.02);
}

/* ==================== КОНЦЕПТЫ ==================== */
.concepts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.concept-card {
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    transition: all 0.3s ease;
}

.concept-card:hover {
    transform: translateY(-3px);
}

.concept-name {
    font-weight: 600;
}

.concept-score {
    font-size: 12px;
    margin-top: 5px;
}

/* ==================== ССЫЛКИ ==================== */
.clickable-link {
    text-decoration: none;
    transition: all 0.3s ease;
}

.clickable-link:hover {
    text-decoration: underline;
}

/* ==================== ПОЛНЫЙ ТЕКСТ ==================== */
.full-text-container {
    max-height: 150px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: monospace;
    font-size: 12px;
    padding: 8px;
    border-radius: 5px;
    margin-top: 5px;
    background: rgba(0,0,0,0.03);
}

/* ==================== РЕЦЕНЗЕНТЫ ==================== */
.reviewer-card {
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
    border-left: 4px solid;
}

.reviewer-card:hover {
    transform: translateY(-2px);
}

.reviewer-name {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
}

.reviewer-orcid {
    font-family: monospace;
    font-size: 12px;
    margin-bottom: 8px;
}

.reviewer-section {
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1px solid rgba(0,0,0,0.06);
}

.reviewer-section-title {
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 8px;
}

.external-id-link {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 15px;
    font-size: 11px;
    margin: 3px;
    text-decoration: none;
    transition: all 0.2s ease;
    background: rgba(0,0,0,0.04);
    color: #333;
}

.external-id-link:hover {
    background: #667eea;
    color: white;
}

.reviewer-website {
    display: inline-block;
    margin: 3px 6px 3px 0;
    font-size: 12px;
}

/* ==================== КОНФИДЕНЦИАЛЬНО ==================== */
.confidential-banner {
    padding: 12px 20px;
    margin-bottom: 20px;
    border-radius: 8px;
    font-weight: 500;
    text-align: center;
    background: linear-gradient(135deg, #fff3cd 0%, #ffe69e 100%);
    border-left: 4px solid #dc3545;
}

/* ==================== ПОДВАЛ ==================== */
.footer {
    text-align: center;
    padding: 20px;
    font-size: 12px;
    border-top: 1px solid rgba(0,0,0,0.06);
    margin-top: 30px;
}

/* ==================== АДАПТИВНОСТЬ ==================== */
@media print {
    .sidebar { display: none; }
    .main-content { margin-left: 0; }
    .stat-card, .section { break-inside: avoid; }
}

@media (max-width: 1024px) {
    .sidebar { width: 220px; padding: 20px 15px; }
    .main-content { margin-left: 220px; padding: 20px; }
    .rank-name { width: 200px; }
}

@media (max-width: 768px) {
    .sidebar { display: none; }
    .main-content { margin-left: 0; padding: 15px; }
    .stats-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
    .rank-name { width: 150px; }
    .section-title { font-size: 20px; }
    .header h1 { font-size: 24px; }
    .header { padding: 25px; }
}

@media (max-width: 480px) {
    .stats-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
    .rank-name { width: 100px; font-size: 12px; }
    .rank-number { width: 30px; font-size: 14px; }
    .section { padding: 15px; }
    .concepts-grid { grid-template-columns: 1fr 1fr; }
}
"""

# ======================== ТЕМА 1: GRADIENT CLASSIC (ТЕКУЩИЙ ДИЗАЙН) ========================

GRADIENT_CLASSIC_CSS = """
/* ==================== ТЕМА: GRADIENT CLASSIC ==================== */
/* Использует {{PRIMARY}} и {{SECONDARY}} для градиентов */

body {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.sidebar {
    background: linear-gradient(135deg, {{PRIMARY}} 0%, {{SECONDARY}} 100%);
    color: white;
    box-shadow: 2px 0 15px rgba(0,0,0,0.1);
}

.sidebar a {
    color: white;
}

.sidebar a:hover {
    background: rgba(255,255,255,0.2);
}

.sidebar a.active {
    background: rgba(255,255,255,0.25);
}

.header {
    background: linear-gradient(135deg, {{PRIMARY}} 0%, {{SECONDARY}} 100%);
    color: white;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.stat-card {
    background: linear-gradient(135deg, white 0%, #f8f9fa 100%);
    box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    border: 1px solid rgba(255,255,255,0.2);
}

.stat-card:hover {
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.stat-number {
    background: linear-gradient(135deg, {{PRIMARY}} 0%, {{SECONDARY}} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-percent {
    background: #d4edda;
    color: #155724;
}

.section {
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.section-title {
    color: #2d3436;
    border-bottom: 3px solid {{PRIMARY}};
}

.rank-item {
    background: white;
    border-left: 3px solid {{PRIMARY}};
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.rank-item:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.rank-number {
    color: {{PRIMARY}};
}

.progress-fill {
    background: linear-gradient(90deg, {{PRIMARY}}, {{SECONDARY}});
}

.concept-card {
    background: linear-gradient(135deg, {{PRIMARY}}15 0%, {{SECONDARY}}15 100%);
    border: 1px solid {{PRIMARY}}30;
}

.concept-name {
    color: {{PRIMARY}};
}

.clickable-link {
    color: {{PRIMARY}};
}

.clickable-link:hover {
    color: {{SECONDARY}};
}

.reviewer-card {
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left-color: {{PRIMARY}};
}

.reviewer-name {
    color: {{PRIMARY}};
}

th {
    background: linear-gradient(135deg, {{PRIMARY}} 0%, {{SECONDARY}} 100%);
    color: white;
}

/* Цветная кодировка для ссылок в полном списке */
.normal-article {
    background: #e8f5e9 !important;
    border-left: 3px solid #4caf50 !important;
}

.notfound-reference {
    background: #e9ecef !important;
    border-left: 3px solid #6c757d !important;
}

.suspicious-reference {
    background: #f8d7da !important;
    border-left: 3px solid #dc3545 !important;
}

.duplicate-reference {
    background: #ffe5cc !important;
    border-left: 3px solid #fd7e14 !important;
}

.ebook-reference {
    background: #d4f1e9 !important;
    border-left: 3px solid #0e6b5e !important;
}

.repository-reference {
    background: #e2d5f8 !important;
    border-left: 3px solid #5e2a9e !important;
}

.preprint-reference {
    background: #e2d5f8 !important;
    border-left: 3px solid #5e2a9e !important;
}

.proceedings-reference {
    background: #fff2c9 !important;
    border-left: 3px solid #b26b00 !important;
}

.retracted-reference {
    background: #f8d7da !important;
    border-left: 3px solid #dc3545 !important;
}

/* Анимация появления */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.section {
    animation: fadeInUp 0.5s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.1s; }
.section:nth-child(3) { animation-delay: 0.2s; }
.section:nth-child(4) { animation-delay: 0.3s; }
.section:nth-child(5) { animation-delay: 0.4s; }
.section:nth-child(6) { animation-delay: 0.5s; }
.section:nth-child(7) { animation-delay: 0.6s; }
.section:nth-child(8) { animation-delay: 0.7s; }
.section:nth-child(9) { animation-delay: 0.8s; }
.section:nth-child(10) { animation-delay: 0.9s; }
"""

# ======================== ТЕМА 2: GLASSMORPHISM (МАТОВОЕ СТЕКЛО) ========================

GLASSMORPHISM_CSS = """
/* ==================== ТЕМА: GLASSMORPHISM ==================== */
/* Использует {{PRIMARY}} для акцентов */

body {
    background: linear-gradient(135deg, #667eea15 0%, #764ba215 30%, #f093fb15 60%, #f5576c15 100%);
    min-height: 100vh;
    position: relative;
}

body::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        radial-gradient(ellipse at 20% 30%, rgba(102,126,234,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 70%, rgba(245,87,108,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(240,147,251,0.05) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.report-wrapper {
    position: relative;
    z-index: 1;
}

.sidebar {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.15);
    color: white;
    box-shadow: 0 0 40px rgba(0,0,0,0.05);
}

.sidebar h3 {
    color: white;
    text-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.sidebar a {
    color: rgba(255,255,255,0.85);
}

.sidebar a:hover {
    background: rgba(255,255,255,0.15);
    color: white;
}

.sidebar a.active {
    background: rgba(255,255,255,0.2);
    color: white;
}

.header {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 8px 32px rgba(0,0,0,0.05);
    color: #2d3436;
}

.header h1 {
    color: #2d3436;
}

.stat-card {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 8px 32px rgba(0,0,0,0.04);
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.stat-card:hover {
    transform: translateY(-8px);
    background: rgba(255,255,255,0.18);
    box-shadow: 0 16px 48px rgba(0,0,0,0.08);
}

.stat-number {
    background: linear-gradient(135deg, {{PRIMARY}}, {{PRIMARY}}CC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
}

.stat-percent {
    background: rgba(255,255,255,0.2);
    color: #2d3436;
    backdrop-filter: blur(5px);
}

.stat-label {
    color: rgba(45,52,54,0.8);
}

.section {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.04);
}

.section-title {
    color: #2d3436;
    border-bottom: 2px solid {{PRIMARY}}40;
}

.rank-item {
    background: rgba(255,255,255,0.06);
    border-left: 3px solid {{PRIMARY}};
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    transition: all 0.3s ease;
}

.rank-item:hover {
    background: rgba(255,255,255,0.12);
    transform: translateX(8px);
}

.rank-number {
    color: {{PRIMARY}};
}

.progress-fill {
    background: linear-gradient(90deg, {{PRIMARY}}, {{PRIMARY}}CC);
}

.concept-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(5px);
}

.concept-card:hover {
    background: rgba(255,255,255,0.12);
    transform: translateY(-3px);
}

.concept-name {
    color: {{PRIMARY}};
}

.clickable-link {
    color: {{PRIMARY}};
    font-weight: 500;
}

.clickable-link:hover {
    color: {{PRIMARY}}CC;
    text-decoration: underline;
}

.reviewer-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-left: 4px solid {{PRIMARY}};
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
}

.reviewer-card:hover {
    background: rgba(255,255,255,0.14);
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}

.reviewer-name {
    color: {{PRIMARY}};
}

th {
    background: rgba(255,255,255,0.1);
    color: #2d3436;
    border-bottom: 2px solid {{PRIMARY}}40;
}

td {
    color: rgba(45,52,54,0.8);
}

tr:hover {
    background: rgba(255,255,255,0.05);
}

.normal-article {
    background: rgba(76,175,80,0.08) !important;
    border-left: 3px solid rgba(76,175,80,0.6) !important;
}

.notfound-reference {
    background: rgba(108,117,125,0.08) !important;
    border-left: 3px solid rgba(108,117,125,0.6) !important;
}

.suspicious-reference {
    background: rgba(220,53,69,0.08) !important;
    border-left: 3px solid rgba(220,53,69,0.6) !important;
}

.duplicate-reference {
    background: rgba(253,126,20,0.08) !important;
    border-left: 3px solid rgba(253,126,20,0.6) !important;
}

.ebook-reference {
    background: rgba(14,107,94,0.08) !important;
    border-left: 3px solid rgba(14,107,94,0.6) !important;
}

.repository-reference {
    background: rgba(94,42,158,0.08) !important;
    border-left: 3px solid rgba(94,42,158,0.6) !important;
}

.preprint-reference {
    background: rgba(94,42,158,0.08) !important;
    border-left: 3px solid rgba(94,42,158,0.6) !important;
}

.proceedings-reference {
    background: rgba(178,107,0,0.08) !important;
    border-left: 3px solid rgba(178,107,0,0.6) !important;
}

.retracted-reference {
    background: rgba(220,53,69,0.08) !important;
    border-left: 3px solid rgba(220,53,69,0.6) !important;
}

@keyframes glassIn {
    0% { opacity: 0; transform: translateY(30px) scale(0.96); backdrop-filter: blur(0px); }
    100% { opacity: 1; transform: translateY(0) scale(1); backdrop-filter: blur(15px); }
}

.section {
    animation: glassIn 0.6s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.08s; }
.section:nth-child(3) { animation-delay: 0.16s; }
.section:nth-child(4) { animation-delay: 0.24s; }
.section:nth-child(5) { animation-delay: 0.32s; }
.section:nth-child(6) { animation-delay: 0.40s; }
.section:nth-child(7) { animation-delay: 0.48s; }
.section:nth-child(8) { animation-delay: 0.56s; }
.section:nth-child(9) { animation-delay: 0.64s; }
.section:nth-child(10) { animation-delay: 0.72s; }

.stat-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 20%, rgba(255,255,255,0.1), transparent 50%);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.5s ease;
}

.stat-card:hover::after {
    opacity: 1;
}

.footer {
    color: rgba(45,52,54,0.6);
    border-top-color: rgba(255,255,255,0.1);
}
"""

# ======================== ТЕМА 3: NEON DARK (КИБЕРПАНК С НЕОНОВЫМИ КАРТОЧКАМИ) ========================

NEON_DARK_CSS = """
/* ==================== ТЕМА: NEON DARK - КИБЕРПАНК С ДИНАМИЧЕСКИМ НЕОНОМ ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: #0a0a0f;
    color: #e0e0e0;
    position: relative;
    font-family: 'Courier New', 'Segoe UI', monospace;
}

/* Киберпанк сетка на фоне */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        linear-gradient(rgba(0, 255, 65, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 65, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
    animation: gridPulse 8s ease-in-out infinite alternate;
}

@keyframes gridPulse {
    0% { opacity: 0.3; }
    100% { opacity: 0.7; }
}

body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(ellipse at 20% 30%, rgba(0,255,65,0.02) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 70%, rgba(255,0,255,0.02) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(0,255,255,0.01) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

.report-wrapper {
    position: relative;
    z-index: 1;
}

.sidebar {
    background: rgba(10,10,15,0.95);
    border-right: 1px solid rgba(0,255,65,0.15);
    box-shadow: 0 0 40px rgba(0,255,65,0.05);
    color: #e0e0e0;
    font-family: 'Courier New', monospace;
}

.sidebar h3 {
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.3), 0 0 40px rgba(0,255,65,0.1);
    border-bottom: 1px solid rgba(0,255,65,0.15);
    padding-bottom: 15px;
    font-family: 'Courier New', monospace;
    font-weight: 700;
    letter-spacing: 2px;
}

.sidebar a {
    color: rgba(224,224,224,0.7);
    transition: all 0.3s ease;
    font-family: 'Courier New', monospace;
    border-left: 2px solid transparent;
}

.sidebar a:hover {
    color: #00ff41;
    background: rgba(0,255,65,0.05);
    text-shadow: 0 0 20px rgba(0,255,65,0.2);
    transform: translateX(5px);
    border-left-color: #00ff41;
}

.sidebar a.active {
    color: #00ff41;
    background: rgba(0,255,65,0.08);
    text-shadow: 0 0 20px rgba(0,255,65,0.3);
    border-left-color: #00ff41;
}

.header {
    background: rgba(20,20,30,0.8);
    border: 1px solid rgba(0,255,65,0.08);
    box-shadow: 0 0 40px rgba(0,255,65,0.05);
    color: #e0e0e0;
}

.header h1 {
    color: #00ff41;
    text-shadow: 0 0 30px rgba(0,255,65,0.2), 0 0 60px rgba(0,255,65,0.1);
    font-family: 'Courier New', monospace;
    letter-spacing: 3px;
}

.header .date {
    color: rgba(224,224,224,0.6);
}

.stat-card {
    background: rgba(20,20,30,0.6);
    border: 1px solid rgba(0,255,65,0.05);
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
    transition: all 0.4s ease;
    position: relative;
    padding: 24px;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
}

/* Неоновая анимация для каждой карточки - случайный цвет из генератора */
.stat-card::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 8px;
    z-index: -1;
    animation: neonBorder 3s linear infinite;
    background: conic-gradient(from var(--angle), var(--neon-color1), var(--neon-color2), var(--neon-color3), var(--neon-color1));
    opacity: 0.7;
}

.stat-card::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 8px;
    z-index: -1;
    filter: blur(15px);
    animation: neonBorder 3s linear infinite;
    background: conic-gradient(from var(--angle), var(--neon-color1), var(--neon-color2), var(--neon-color3), var(--neon-color1));
    opacity: 0.3;
}

@property --angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}

@keyframes neonBorder {
    0% { --angle: 0deg; }
    100% { --angle: 360deg; }
}

/* Устанавливаем разные неоновые цвета для карточек через data-атрибуты */
.stat-card[data-type="doi"] { --neon-color1: #00ff41; --neon-color2: #00ffaa; --neon-color3: #00ffff; }
.stat-card[data-type="authors"] { --neon-color1: #ff00ff; --neon-color2: #ff00aa; --neon-color3: #aa00ff; }
.stat-card[data-type="citations"] { --neon-color1: #ff6600; --neon-color2: #ffaa00; --neon-color3: #ffff00; }
.stat-card[data-type="journals"] { --neon-color1: #00ffff; --neon-color2: #00aaff; --neon-color3: #0066ff; }
.stat-card[data-type="publishers"] { --neon-color1: #ff0044; --neon-color2: #ff0088; --neon-color3: #ff00aa; }
.stat-card[data-type="orcid"] { --neon-color1: #0088ff; --neon-color2: #00ccff; --neon-color3: #00ffff; }
.stat-card[data-type="selfcitations"] { --neon-color1: #ff0044; --neon-color2: #ff2200; --neon-color3: #ff6600; }

.stat-card:hover {
    transform: translateY(-5px) scale(1.02);
    border-color: rgba(0,255,65,0.15);
    box-shadow: 0 0 60px rgba(0,255,65,0.05);
}

.stat-card:hover::before {
    opacity: 1;
}

.stat-card:hover::after {
    opacity: 0.5;
}

.stat-number {
    color: #00ff41 !important;
    -webkit-text-fill-color: #00ff41 !important;
    background: none !important;
    text-shadow: 0 0 30px rgba(0,255,65,0.2), 0 0 60px rgba(0,255,65,0.1);
    font-family: 'Courier New', monospace;
}

.stat-percent {
    background: rgba(0,255,65,0.08);
    color: #00ff41;
    border: 1px solid rgba(0,255,65,0.15);
    font-family: 'Courier New', monospace;
}

.stat-label {
    color: rgba(224,224,224,0.7);
    letter-spacing: 1px;
}

.section {
    background: rgba(20,20,30,0.4);
    border: 1px solid rgba(0,255,65,0.03);
    box-shadow: 0 0 40px rgba(0,0,0,0.2);
    border-radius: 8px;
}

.section-title {
    color: #00ff41;
    border-bottom: 2px solid rgba(0,255,65,0.1);
    text-shadow: 0 0 30px rgba(0,255,65,0.1);
    font-family: 'Courier New', monospace;
    letter-spacing: 2px;
}

.rank-item {
    background: rgba(20,20,30,0.3);
    border-left: 2px solid rgba(0,255,65,0.1);
    transition: all 0.3s ease;
    font-family: 'Courier New', monospace;
}

.rank-item:hover {
    background: rgba(0,255,65,0.03);
    transform: translateX(8px);
    border-left-color: #00ff41;
    box-shadow: 0 0 30px rgba(0,255,65,0.02);
}

.rank-number {
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.1);
    font-family: 'Courier New', monospace;
}

.progress-bar {
    background: rgba(255,255,255,0.03);
    border-radius: 4px !important;
}

.progress-fill {
    background: linear-gradient(90deg, #00ff41, #00ffaa);
    box-shadow: 0 0 20px rgba(0,255,65,0.1);
    border-radius: 4px !important;
}

.concept-card {
    background: rgba(20,20,30,0.3);
    border: 1px solid rgba(0,255,65,0.05);
    transition: all 0.3s ease;
    border-radius: 8px;
}

.concept-card:hover {
    border-color: rgba(0,255,65,0.2);
    transform: translateY(-3px);
    box-shadow: 0 0 30px rgba(0,255,65,0.03);
}

.concept-name {
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.1);
    font-family: 'Courier New', monospace;
}

.concept-score {
    color: rgba(224,224,224,0.5);
}

.clickable-link {
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.1);
    font-family: 'Courier New', monospace;
}

.clickable-link:hover {
    color: #ffffff;
    text-shadow: 0 0 30px rgba(0,255,65,0.3);
}

.reviewer-card {
    background: rgba(20,20,30,0.4);
    border: 1px solid rgba(0,255,65,0.05);
    border-left: 4px solid #00ff41;
    box-shadow: 0 0 30px rgba(0,0,0,0.2);
    border-radius: 8px;
}

.reviewer-card:hover {
    background: rgba(0,255,65,0.03);
    box-shadow: 0 0 40px rgba(0,255,65,0.02);
}

.reviewer-name {
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.1);
    font-family: 'Courier New', monospace;
}

.reviewer-orcid {
    color: rgba(224,224,224,0.5);
}

.reviewer-orcid a {
    color: #00ff41;
}

.reviewer-section-title {
    color: rgba(224,224,224,0.6);
}

.external-id-link {
    background: rgba(0,255,65,0.05);
    color: #00ff41;
    border: 1px solid rgba(0,255,65,0.05);
    font-family: 'Courier New', monospace;
}

.external-id-link:hover {
    background: rgba(0,255,65,0.1);
    color: #ffffff;
}

th {
    background: rgba(0,255,65,0.05);
    color: #00ff41;
    border-bottom: 2px solid rgba(0,255,65,0.05);
    font-family: 'Courier New', monospace;
}

td {
    color: rgba(224,224,224,0.7);
}

tr:hover {
    background: rgba(0,255,65,0.02);
}

.normal-article {
    background: rgba(0,255,128,0.05) !important;
    border-left: 2px solid rgba(0,255,128,0.3) !important;
}

.notfound-reference {
    background: rgba(128,128,128,0.05) !important;
    border-left: 2px solid rgba(128,128,128,0.3) !important;
}

.suspicious-reference {
    background: rgba(255,0,0,0.05) !important;
    border-left: 2px solid rgba(255,0,0,0.3) !important;
}

.duplicate-reference {
    background: rgba(255,128,0,0.05) !important;
    border-left: 2px solid rgba(255,128,0,0.3) !important;
}

.ebook-reference {
    background: rgba(0,255,255,0.05) !important;
    border-left: 2px solid rgba(0,255,255,0.3) !important;
}

.repository-reference {
    background: rgba(128,0,255,0.05) !important;
    border-left: 2px solid rgba(128,0,255,0.3) !important;
}

.preprint-reference {
    background: rgba(128,0,255,0.05) !important;
    border-left: 2px solid rgba(128,0,255,0.3) !important;
}

.proceedings-reference {
    background: rgba(255,128,0,0.05) !important;
    border-left: 2px solid rgba(255,128,0,0.3) !important;
}

.retracted-reference {
    background: rgba(255,0,0,0.05) !important;
    border-left: 2px solid rgba(255,0,0,0.3) !important;
}

@keyframes neonPulse {
    0%, 100% { text-shadow: 0 0 20px rgba(0,255,65,0.1); }
    50% { text-shadow: 0 0 40px rgba(0,255,65,0.3), 0 0 80px rgba(0,255,65,0.1); }
}

.section-title {
    animation: neonPulse 4s ease-in-out infinite;
}

@keyframes neonIn {
    0% { opacity: 0; transform: translateY(30px); filter: blur(10px); }
    100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
}

.section {
    animation: neonIn 0.6s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.1s; }
.section:nth-child(3) { animation-delay: 0.2s; }
.section:nth-child(4) { animation-delay: 0.3s; }
.section:nth-child(5) { animation-delay: 0.4s; }
.section:nth-child(6) { animation-delay: 0.5s; }
.section:nth-child(7) { animation-delay: 0.6s; }
.section:nth-child(8) { animation-delay: 0.7s; }
.section:nth-child(9) { animation-delay: 0.8s; }
.section:nth-child(10) { animation-delay: 0.9s; }

.footer {
    color: rgba(224,224,224,0.3);
    border-top-color: rgba(0,255,65,0.03);
}

.confidential-banner {
    background: rgba(255,0,0,0.05);
    border-left: 4px solid #ff0044;
    color: #ff0044;
    text-shadow: 0 0 20px rgba(255,0,0,0.1);
    font-family: 'Courier New', monospace;
}

/* Дополнительные киберпанк элементы */
.badge {
    font-family: 'Courier New', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.badge-success { background: rgba(0,255,65,0.15); color: #00ff41; border: 1px solid rgba(0,255,65,0.2); }
.badge-warning { background: rgba(255,170,0,0.15); color: #ffaa00; border: 1px solid rgba(255,170,0,0.2); }
.badge-danger { background: rgba(255,0,68,0.15); color: #ff0044; border: 1px solid rgba(255,0,68,0.2); }
.badge-info { background: rgba(0,255,255,0.15); color: #00ffff; border: 1px solid rgba(0,255,255,0.2); }
.badge-repository { background: rgba(170,0,255,0.15); color: #aa00ff; border: 1px solid rgba(170,0,255,0.2); }
.badge-book { background: rgba(0,255,170,0.15); color: #00ffaa; border: 1px solid rgba(0,255,170,0.2); }
.badge-proceedings { background: rgba(255,170,0,0.15); color: #ffaa00; border: 1px solid rgba(255,170,0,0.2); }
"""

# ======================== ТЕМА 4: AURORA BOREALIS (ПОЛЯРНАЯ НОЧЬ/ЗИМНИЙ МОРОЗ) ========================

AURORA_CSS = """
/* ==================== ТЕМА: AURORA BOREALIS - АРКТИЧЕСКАЯ НОЧЬ С ЭФФЕКТОМ МОРОЗА ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: linear-gradient(180deg, #0a1520 0%, #0d1f2d 30%, #0a1a25 60%, #0d1f2d 80%, #0a1520 100%);
    color: #c8dce8;
    position: relative;
    overflow-x: hidden;
}

/* Снежная текстура - мелкие белые точки */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        radial-gradient(1px 1px at 5% 10%, rgba(255,255,255,0.15), transparent),
        radial-gradient(1px 1px at 15% 30%, rgba(255,255,255,0.10), transparent),
        radial-gradient(1.5px 1.5px at 25% 5%, rgba(255,255,255,0.20), transparent),
        radial-gradient(1px 1px at 35% 45%, rgba(255,255,255,0.08), transparent),
        radial-gradient(1px 1px at 45% 15%, rgba(255,255,255,0.12), transparent),
        radial-gradient(2px 2px at 55% 35%, rgba(255,255,255,0.18), transparent),
        radial-gradient(1px 1px at 65% 5%, rgba(255,255,255,0.10), transparent),
        radial-gradient(1px 1px at 75% 25%, rgba(255,255,255,0.15), transparent),
        radial-gradient(1.5px 1.5px at 85% 15%, rgba(255,255,255,0.12), transparent),
        radial-gradient(1px 1px at 95% 40%, rgba(255,255,255,0.08), transparent),
        radial-gradient(1px 1px at 10% 55%, rgba(255,255,255,0.10), transparent),
        radial-gradient(1px 1px at 20% 70%, rgba(255,255,255,0.15), transparent),
        radial-gradient(1.5px 1.5px at 30% 60%, rgba(255,255,255,0.12), transparent),
        radial-gradient(1px 1px at 40% 80%, rgba(255,255,255,0.08), transparent),
        radial-gradient(1px 1px at 50% 65%, rgba(255,255,255,0.18), transparent),
        radial-gradient(2px 2px at 60% 85%, rgba(255,255,255,0.10), transparent),
        radial-gradient(1px 1px at 70% 75%, rgba(255,255,255,0.15), transparent),
        radial-gradient(1px 1px at 80% 90%, rgba(255,255,255,0.12), transparent),
        radial-gradient(1.5px 1.5px at 90% 60%, rgba(255,255,255,0.18), transparent),
        radial-gradient(1px 1px at 95% 80%, rgba(255,255,255,0.08), transparent);
    background-size: 200px 200px;
    background-repeat: repeat;
    opacity: 0.3;
    pointer-events: none;
    z-index: 0;
    animation: snowfall 20s linear infinite;
}

@keyframes snowfall {
    0% { transform: translateY(0); }
    100% { transform: translateY(200px); }
}

/* Полярное сияние только в хедере и футере */
body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(ellipse at 30% 10%, rgba(168,216,234,0.03) 0%, transparent 20%),
        radial-gradient(ellipse at 70% 15%, rgba(192,192,192,0.02) 0%, transparent 20%),
        radial-gradient(ellipse at 50% 90%, rgba(168,216,234,0.02) 0%, transparent 20%);
    pointer-events: none;
    z-index: 0;
}

.report-wrapper {
    position: relative;
    z-index: 1;
}

.sidebar {
    background: rgba(10,21,32,0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(168,216,234,0.05);
    color: #c8dce8;
    box-shadow: 0 0 60px rgba(0,0,0,0.2);
}

.sidebar h3 {
    color: #a8d8ea;
    text-shadow: 0 0 30px rgba(168,216,234,0.05);
    border-bottom: 1px solid rgba(168,216,234,0.05);
    padding-bottom: 15px;
    font-weight: 300;
    letter-spacing: 2px;
}

.sidebar a {
    color: rgba(200,220,232,0.5);
    transition: all 0.3s ease;
    border-left: 2px solid transparent;
}

.sidebar a:hover {
    color: #a8d8ea;
    background: rgba(168,216,234,0.03);
    text-shadow: 0 0 20px rgba(168,216,234,0.05);
    border-left-color: #a8d8ea;
}

.sidebar a.active {
    color: #a8d8ea;
    background: rgba(168,216,234,0.05);
    text-shadow: 0 0 20px rgba(168,216,234,0.08);
    border-left-color: #a8d8ea;
}

.header {
    background: rgba(13,31,45,0.6);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(168,216,234,0.03);
    box-shadow: 0 0 60px rgba(0,0,0,0.1);
    color: #c8dce8;
    position: relative;
    overflow: hidden;
}

/* Эффект полярного сияния в хедере */
.header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 20%, rgba(168,216,234,0.03) 0%, transparent 30%),
                radial-gradient(ellipse at 70% 30%, rgba(192,192,192,0.02) 0%, transparent 30%);
    animation: auroraMoveHeader 15s ease-in-out infinite alternate;
    pointer-events: none;
}

@keyframes auroraMoveHeader {
    0% { transform: translateX(-10%) scale(1); }
    100% { transform: translateX(10%) scale(1.1); }
}

.header h1 {
    color: #a8d8ea;
    text-shadow: 0 0 40px rgba(168,216,234,0.05);
    font-weight: 300;
    letter-spacing: 3px;
}

.header .date {
    color: rgba(200,220,232,0.4);
}

.stat-card {
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(168,216,234,0.03);
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    transition: all 0.5s ease;
    position: relative;
}

/* Эффект инея на карточках */
.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.03), transparent);
    border-radius: inherit;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.5s ease;
}

.stat-card:hover {
    transform: translateY(-8px);
    border-color: rgba(168,216,234,0.08);
    box-shadow: 0 16px 48px rgba(0,0,0,0.2);
}

.stat-card:hover::before {
    opacity: 1;
}

.stat-number {
    color: #a8d8ea !important;
    -webkit-text-fill-color: #a8d8ea !important;
    background: none !important;
    text-shadow: 0 0 40px rgba(168,216,234,0.02);
    font-weight: 300;
}

.stat-percent {
    background: rgba(168,216,234,0.04);
    color: #a8d8ea;
    border: 1px solid rgba(168,216,234,0.02);
}

.stat-label {
    color: rgba(200,220,232,0.5);
    font-weight: 300;
}

.section {
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(168,216,234,0.02);
    box-shadow: 0 8px 32px rgba(0,0,0,0.05);
}

.section-title {
    color: #a8d8ea;
    border-bottom: 2px solid rgba(168,216,234,0.03);
    text-shadow: 0 0 30px rgba(168,216,234,0.02);
    font-weight: 300;
    letter-spacing: 2px;
}

.rank-item {
    background: rgba(255,255,255,0.01);
    border-left: 2px solid rgba(168,216,234,0.03);
    transition: all 0.4s ease;
}

.rank-item:hover {
    background: rgba(168,216,234,0.02);
    transform: translateX(8px);
    border-left-color: rgba(168,216,234,0.08);
}

.rank-number {
    color: #a8d8ea;
    font-weight: 300;
}

.progress-bar {
    background: rgba(255,255,255,0.02);
    border-radius: 4px !important;
}

.progress-fill {
    background: linear-gradient(90deg, #a8d8ea, #c8dce8);
    box-shadow: 0 0 20px rgba(168,216,234,0.02);
    border-radius: 4px !important;
}

.concept-card {
    background: rgba(255,255,255,0.01);
    border: 1px solid rgba(168,216,234,0.02);
    transition: all 0.4s ease;
}

.concept-card:hover {
    border-color: rgba(168,216,234,0.03);
    transform: translateY(-3px);
    box-shadow: 0 0 40px rgba(168,216,234,0.01);
}

.concept-name {
    color: #a8d8ea;
    font-weight: 300;
}

.concept-score {
    color: rgba(200,220,232,0.2);
}

.clickable-link {
    color: #a8d8ea;
}

.clickable-link:hover {
    color: #e0f0f8;
    text-shadow: 0 0 20px rgba(168,216,234,0.02);
}

.reviewer-card {
    background: rgba(13,31,45,0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(168,216,234,0.02);
    border-left: 4px solid rgba(168,216,234,0.03);
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.reviewer-card:hover {
    background: rgba(168,216,234,0.02);
}

.reviewer-name {
    color: #a8d8ea;
    font-weight: 300;
}

th {
    background: rgba(168,216,234,0.02);
    color: #a8d8ea;
    border-bottom: 2px solid rgba(168,216,234,0.02);
    font-weight: 300;
}

td {
    color: rgba(200,220,232,0.5);
}

tr:hover {
    background: rgba(168,216,234,0.01);
}

.normal-article {
    border-left: 2px solid rgba(168,216,234,0.05) !important;
    background: none !important;
}

.notfound-reference {
    border-left: 2px solid rgba(128,128,128,0.05) !important;
    background: none !important;
}

.suspicious-reference {
    border-left: 2px solid rgba(200,100,100,0.05) !important;
    background: none !important;
}

.duplicate-reference {
    border-left: 2px solid rgba(200,180,100,0.05) !important;
    background: none !important;
}

.ebook-reference {
    border-left: 2px solid rgba(168,216,234,0.05) !important;
    background: none !important;
}

.repository-reference {
    border-left: 2px solid rgba(180,160,220,0.05) !important;
    background: none !important;
}

.preprint-reference {
    border-left: 2px solid rgba(180,160,220,0.05) !important;
    background: none !important;
}

.proceedings-reference {
    border-left: 2px solid rgba(220,200,160,0.05) !important;
    background: none !important;
}

.retracted-reference {
    border-left: 2px solid rgba(200,100,100,0.05) !important;
    background: none !important;
}

@keyframes auroraIn {
    0% { opacity: 0; transform: translateY(30px); filter: blur(2px); }
    100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
}

.section {
    animation: auroraIn 0.7s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.1s; }
.section:nth-child(3) { animation-delay: 0.2s; }
.section:nth-child(4) { animation-delay: 0.3s; }
.section:nth-child(5) { animation-delay: 0.4s; }
.section:nth-child(6) { animation-delay: 0.5s; }
.section:nth-child(7) { animation-delay: 0.6s; }
.section:nth-child(8) { animation-delay: 0.7s; }
.section:nth-child(9) { animation-delay: 0.8s; }
.section:nth-child(10) { animation-delay: 0.9s; }

.footer {
    color: rgba(200,220,232,0.15);
    border-top-color: rgba(168,216,234,0.02);
}

.confidential-banner {
    background: rgba(200,100,100,0.02);
    border-left: 4px solid rgba(200,100,100,0.05);
    color: #b8a8a8;
    font-weight: 300;
}

/* Стили для бейджей в арктическом стиле */
.badge {
    font-weight: 300;
    letter-spacing: 0.5px;
}

.badge-success { background: rgba(168,216,234,0.05); color: #a8d8ea; border: 1px solid rgba(168,216,234,0.02); }
.badge-warning { background: rgba(200,200,180,0.05); color: #c8c8b8; border: 1px solid rgba(200,200,180,0.02); }
.badge-danger { background: rgba(200,100,100,0.05); color: #c8a8a8; border: 1px solid rgba(200,100,100,0.02); }
.badge-info { background: rgba(180,200,220,0.05); color: #a8b8c8; border: 1px solid rgba(180,200,220,0.02); }
"""

# ======================== ТЕМА 5: OCEAN DEEP (ГЛУБИНА ОКЕАНА / ЗАТОНУВШИЙ КОРАБЛЬ) ========================

OCEAN_DEEP_CSS = """
/* ==================== ТЕМА: OCEAN DEEP - ГЛУБИНА ОКЕАНА С ЭФФЕКТОМ ЗАТОНУВШЕГО КОРАБЛЯ ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: linear-gradient(180deg, #0a1628 0%, #0a1f1a 30%, #0a2a1a 50%, #0a1f1a 70%, #0a1628 100%);
    color: #8db5a8;
    min-height: 100vh;
    position: relative;
}

/* Подводные лучи света */
body::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        linear-gradient(135deg, rgba(0,180,200,0.02) 0%, transparent 30%),
        linear-gradient(225deg, rgba(0,150,180,0.01) 0%, transparent 30%),
        radial-gradient(ellipse at 30% 20%, rgba(0,200,180,0.02) 0%, transparent 20%),
        radial-gradient(ellipse at 70% 80%, rgba(0,150,200,0.01) 0%, transparent 20%);
    animation: lightBeams 15s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes lightBeams {
    0% { transform: rotate(-5deg) scale(1); }
    100% { transform: rotate(5deg) scale(1.05); }
}

/* Пузырьки */
body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        radial-gradient(2px 2px at 10% 20%, rgba(0,255,200,0.05), transparent),
        radial-gradient(2px 2px at 25% 40%, rgba(0,255,200,0.03), transparent),
        radial-gradient(3px 3px at 40% 60%, rgba(0,255,200,0.04), transparent),
        radial-gradient(2px 2px at 55% 80%, rgba(0,255,200,0.03), transparent),
        radial-gradient(2px 2px at 70% 30%, rgba(0,255,200,0.05), transparent),
        radial-gradient(3px 3px at 85% 50%, rgba(0,255,200,0.04), transparent),
        radial-gradient(2px 2px at 15% 70%, rgba(0,255,200,0.03), transparent),
        radial-gradient(2px 2px at 45% 20%, rgba(0,255,200,0.05), transparent),
        radial-gradient(3px 3px at 65% 90%, rgba(0,255,200,0.04), transparent),
        radial-gradient(2px 2px at 90% 10%, rgba(0,255,200,0.03), transparent);
    background-size: 300px 300px;
    background-repeat: repeat;
    opacity: 0.3;
    pointer-events: none;
    z-index: 0;
    animation: bubbles 12s ease-in-out infinite alternate;
}

@keyframes bubbles {
    0% { transform: translateY(0); }
    100% { transform: translateY(-200px); }
}

.report-wrapper {
    position: relative;
    z-index: 1;
}

.sidebar {
    background: rgba(10,30,26,0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(0,180,160,0.05);
    color: #8db5a8;
    box-shadow: 0 0 60px rgba(0,0,0,0.3);
}

.sidebar h3 {
    color: #00d4aa;
    text-shadow: 0 0 30px rgba(0,212,170,0.05);
    border-bottom: 1px solid rgba(0,180,160,0.05);
    padding-bottom: 15px;
    font-weight: 300;
    letter-spacing: 3px;
}

.sidebar a {
    color: rgba(141,181,168,0.5);
    transition: all 0.3s ease;
    clip-path: polygon(0 0, 100% 0, 95% 100%, 0% 100%);
}

.sidebar a:hover {
    color: #00d4aa;
    background: rgba(0,212,170,0.03);
    text-shadow: 0 0 20px rgba(0,212,170,0.05);
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%);
}

.sidebar a.active {
    color: #00d4aa;
    background: rgba(0,212,170,0.05);
    text-shadow: 0 0 20px rgba(0,212,170,0.08);
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%);
}

.header {
    background: rgba(10,31,26,0.6);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(0,180,160,0.03);
    box-shadow: 0 0 60px rgba(0,0,0,0.2);
    color: #8db5a8;
    clip-path: polygon(0 0, 100% 0, 98% 100%, 2% 100%);
}

.header h1 {
    color: #00d4aa;
    text-shadow: 0 0 40px rgba(0,212,170,0.02);
    font-weight: 300;
    letter-spacing: 4px;
}

.header .date {
    color: rgba(141,181,168,0.3);
}

.stat-card {
    background: rgba(10,31,26,0.5);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(0,180,160,0.02);
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    transition: all 0.5s ease;
    clip-path: polygon(0 0, 100% 0, 97% 100%, 3% 100%);
    position: relative;
}

/* Налет на карточках (эффект затонувшего корабля) */
.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(180deg, rgba(0,180,160,0.02), transparent 50%, rgba(0,180,160,0.01));
    border-radius: inherit;
    pointer-events: none;
}

.stat-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(0,212,170,0.05);
    box-shadow: 0 16px 48px rgba(0,0,0,0.3);
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%);
}

.stat-number {
    background: linear-gradient(135deg, #00d4aa, #00b894) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    text-shadow: 0 0 40px rgba(0,212,170,0.02);
    font-weight: 300;
}

.stat-percent {
    background: rgba(0,212,170,0.04);
    color: #00d4aa;
    border: 1px solid rgba(0,212,170,0.02);
}

.stat-label {
    color: rgba(141,181,168,0.5);
    font-weight: 300;
}

.section {
    background: rgba(10,31,26,0.3);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(0,180,160,0.01);
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.section-title {
    color: #00d4aa;
    border-bottom: 2px solid rgba(0,212,170,0.03);
    text-shadow: 0 0 30px rgba(0,212,170,0.01);
    font-weight: 300;
    letter-spacing: 3px;
}

.rank-item {
    background: rgba(255,255,255,0.01);
    border-left: 2px solid rgba(0,212,170,0.03);
    transition: all 0.4s ease;
    clip-path: polygon(0 0, 100% 0, 98% 100%, 2% 100%);
}

.rank-item:hover {
    background: rgba(0,212,170,0.01);
    transform: translateX(8px);
    border-left-color: rgba(0,212,170,0.05);
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%);
}

.rank-number {
    color: #00d4aa;
    font-weight: 300;
}

.progress-bar {
    background: rgba(255,255,255,0.01);
    border-radius: 4px !important;
}

.progress-fill {
    background: linear-gradient(90deg, #00b894, #00d4aa);
    box-shadow: 0 0 20px rgba(0,212,170,0.02);
    border-radius: 4px !important;
}

.concept-card {
    background: rgba(255,255,255,0.01);
    border: 1px solid rgba(0,180,160,0.01);
    transition: all 0.4s ease;
    clip-path: polygon(0 0, 100% 0, 95% 100%, 5% 100%);
}

.concept-card:hover {
    border-color: rgba(0,212,170,0.02);
    transform: translateY(-3px);
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%);
}

.concept-name {
    color: #00d4aa;
    font-weight: 300;
}

.concept-score {
    color: rgba(141,181,168,0.2);
}

.clickable-link {
    color: #00d4aa;
}

.clickable-link:hover {
    color: #00ffcc;
    text-shadow: 0 0 20px rgba(0,212,170,0.02);
}

.reviewer-card {
    background: rgba(10,31,26,0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0,180,160,0.01);
    border-left: 4px solid rgba(0,212,170,0.03);
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    clip-path: polygon(0 0, 100% 0, 98% 100%, 2% 100%);
}

.reviewer-card:hover {
    background: rgba(0,212,170,0.01);
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%);
}

.reviewer-name {
    color: #00d4aa;
    font-weight: 300;
}

th {
    background: rgba(0,212,170,0.02);
    color: #00d4aa;
    border-bottom: 2px solid rgba(0,212,170,0.02);
    font-weight: 300;
}

td {
    color: rgba(141,181,168,0.5);
}

tr:hover {
    background: rgba(0,212,170,0.01);
}

.normal-article {
    border-left: 2px solid rgba(0,200,180,0.03) !important;
    background: none !important;
}

.notfound-reference {
    border-left: 2px solid rgba(128,128,128,0.03) !important;
    background: none !important;
}

.suspicious-reference {
    border-left: 2px solid rgba(255,100,100,0.03) !important;
    background: none !important;
}

.duplicate-reference {
    border-left: 2px solid rgba(255,200,100,0.03) !important;
    background: none !important;
}

.ebook-reference {
    border-left: 2px solid rgba(0,212,170,0.03) !important;
    background: none !important;
}

.repository-reference {
    border-left: 2px solid rgba(150,100,200,0.03) !important;
    background: none !important;
}

.preprint-reference {
    border-left: 2px solid rgba(150,100,200,0.03) !important;
    background: none !important;
}

.proceedings-reference {
    border-left: 2px solid rgba(200,180,100,0.03) !important;
    background: none !important;
}

.retracted-reference {
    border-left: 2px solid rgba(255,100,100,0.03) !important;
    background: none !important;
}

@keyframes oceanIn {
    0% { opacity: 0; transform: translateY(30px) scale(0.98) rotateX(2deg); }
    100% { opacity: 1; transform: translateY(0) scale(1) rotateX(0deg); }
}

.section {
    animation: oceanIn 0.7s ease-out forwards;
    perspective: 1000px;
}

.section:nth-child(2) { animation-delay: 0.1s; }
.section:nth-child(3) { animation-delay: 0.2s; }
.section:nth-child(4) { animation-delay: 0.3s; }
.section:nth-child(5) { animation-delay: 0.4s; }
.section:nth-child(6) { animation-delay: 0.5s; }
.section:nth-child(7) { animation-delay: 0.6s; }
.section:nth-child(8) { animation-delay: 0.7s; }
.section:nth-child(9) { animation-delay: 0.8s; }
.section:nth-child(10) { animation-delay: 0.9s; }

.footer {
    color: rgba(141,181,168,0.1);
    border-top-color: rgba(0,212,170,0.01);
}

.confidential-banner {
    background: rgba(255,100,100,0.02);
    border-left: 4px solid rgba(255,100,100,0.05);
    color: #8db5a8;
    font-weight: 300;
}

.badge {
    font-weight: 300;
    letter-spacing: 0.5px;
}

.badge-success { background: rgba(0,212,170,0.05); color: #00d4aa; border: 1px solid rgba(0,212,170,0.02); }
.badge-warning { background: rgba(255,200,100,0.05); color: #c8b888; border: 1px solid rgba(255,200,100,0.02); }
.badge-danger { background: rgba(255,100,100,0.05); color: #c88888; border: 1px solid rgba(255,100,100,0.02); }
.badge-info { background: rgba(0,180,200,0.05); color: #00b8c8; border: 1px solid rgba(0,180,200,0.02); }
"""

# ======================== ТЕМА 6: COSMIC (РЕТРО-КОСМОС 70-Х) ========================

COSMIC_CSS = """
/* ==================== ТЕМА: COSMIC - РЕТРО-ФУТУРИСТИЧЕСКИЙ КОСМОС 70-Х ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: linear-gradient(180deg, #0a0a1a 0%, #0d0d2b 30%, #0f0f2d 50%, #0d0d2b 70%, #0a0a1a 100%);
    color: #c8c8d8;
    position: relative;
    overflow-x: hidden;
    font-family: 'Georgia', 'Times New Roman', serif;
}

/* Винтажная зернистость */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        radial-gradient(1px 1px at 10% 20%, rgba(255,255,200,0.06), transparent),
        radial-gradient(1px 1px at 30% 50%, rgba(255,255,200,0.04), transparent),
        radial-gradient(1.5px 1.5px at 50% 30%, rgba(255,255,200,0.08), transparent),
        radial-gradient(1px 1px at 70% 60%, rgba(255,255,200,0.05), transparent),
        radial-gradient(1px 1px at 90% 40%, rgba(255,255,200,0.07), transparent),
        radial-gradient(1px 1px at 20% 70%, rgba(255,255,200,0.04), transparent),
        radial-gradient(1.5px 1.5px at 40% 90%, rgba(255,255,200,0.06), transparent),
        radial-gradient(1px 1px at 60% 10%, rgba(255,255,200,0.08), transparent),
        radial-gradient(1px 1px at 80% 80%, rgba(255,255,200,0.05), transparent);
    background-size: 200px 200px;
    background-repeat: repeat;
    opacity: 0.2;
    pointer-events: none;
    z-index: 0;
}

/* Ретро-элементы (круги, орбиты) */
body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 30%, rgba(255,215,0,0.02) 0%, transparent 15%),
        radial-gradient(circle at 80% 70%, rgba(255,107,53,0.02) 0%, transparent 15%),
        radial-gradient(circle at 50% 50%, rgba(0,212,255,0.01) 0%, transparent 20%),
        radial-gradient(circle at 70% 20%, rgba(255,215,0,0.01) 0%, transparent 12%),
        radial-gradient(circle at 30% 80%, rgba(255,107,53,0.01) 0%, transparent 12%);
    pointer-events: none;
    z-index: 0;
}

.report-wrapper {
    position: relative;
    z-index: 1;
}

.sidebar {
    background: rgba(10,10,26,0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 2px solid rgba(255,215,0,0.03);
    color: #c8c8d8;
    box-shadow: 0 0 60px rgba(0,0,0,0.3);
}

.sidebar h3 {
    color: #ffd700;
    text-shadow: 0 0 30px rgba(255,215,0,0.05);
    border-bottom: 2px solid rgba(255,215,0,0.05);
    padding-bottom: 15px;
    font-family: 'Georgia', serif;
    font-weight: 700;
    letter-spacing: 4px;
}

.sidebar a {
    color: rgba(200,200,216,0.5);
    transition: all 0.3s ease;
    font-family: 'Georgia', serif;
    border: 1px solid transparent;
    padding: 10px 15px;
}

.sidebar a:hover {
    color: #ffd700;
    background: rgba(255,215,0,0.03);
    text-shadow: 0 0 20px rgba(255,215,0,0.05);
    border-color: rgba(255,215,0,0.05);
}

.sidebar a.active {
    color: #ffd700;
    background: rgba(255,215,0,0.05);
    text-shadow: 0 0 20px rgba(255,215,0,0.08);
    border-color: rgba(255,215,0,0.08);
}

.header {
    background: rgba(13,13,43,0.6);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 2px solid rgba(255,215,0,0.02);
    box-shadow: 0 0 60px rgba(0,0,0,0.2);
    color: #c8c8d8;
    position: relative;
    overflow: hidden;
}

/* Ретро-орбита в хедере */
.header::before {
    content: '✦ ✧ ✦';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 60px;
    color: rgba(255,215,0,0.02);
    letter-spacing: 100px;
    pointer-events: none;
    animation: orbitRotate 20s linear infinite;
}

@keyframes orbitRotate {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}

.header h1 {
    color: #ffd700;
    text-shadow: 0 0 40px rgba(255,215,0,0.02);
    font-family: 'Georgia', serif;
    font-weight: 700;
    letter-spacing: 5px;
}

.header .date {
    color: rgba(200,200,216,0.3);
}

.stat-card {
    background: rgba(20,20,50,0.4);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255,215,0,0.02);
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    transition: all 0.5s ease;
    border-radius: 0 !important;
    /* Винтажная рамка с уголками */
    position: relative;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    width: 30px;
    height: 30px;
    border-top: 2px solid rgba(255,215,0,0.05);
    border-left: 2px solid rgba(255,215,0,0.05);
}

.stat-card::after {
    content: '';
    position: absolute;
    bottom: -1px;
    right: -1px;
    width: 30px;
    height: 30px;
    border-bottom: 2px solid rgba(255,215,0,0.05);
    border-right: 2px solid rgba(255,215,0,0.05);
}

.stat-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(255,215,0,0.05);
    box-shadow: 0 0 60px rgba(255,215,0,0.02);
}

.stat-card:hover::before,
.stat-card:hover::after {
    border-color: rgba(255,215,0,0.1);
}

.stat-number {
    color: #ffd700 !important;
    -webkit-text-fill-color: #ffd700 !important;
    background: none !important;
    text-shadow: 0 0 40px rgba(255,215,0,0.02);
    font-family: 'Georgia', serif;
    font-weight: 700;
}

.stat-percent {
    background: rgba(255,215,0,0.04);
    color: #ffd700;
    border: 1px solid rgba(255,215,0,0.02);
    font-family: 'Georgia', serif;
}

.stat-label {
    color: rgba(200,200,216,0.5);
    font-family: 'Georgia', serif;
    font-weight: 300;
}

.section {
    background: rgba(20,20,50,0.2);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255,215,0,0.01);
    box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    border-radius: 0 !important;
    position: relative;
}

/* Уголки для секций */
.section::before {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    width: 40px;
    height: 40px;
    border-top: 2px solid rgba(255,215,0,0.02);
    border-left: 2px solid rgba(255,215,0,0.02);
}

.section::after {
    content: '';
    position: absolute;
    bottom: -1px;
    right: -1px;
    width: 40px;
    height: 40px;
    border-bottom: 2px solid rgba(255,215,0,0.02);
    border-right: 2px solid rgba(255,215,0,0.02);
}

.section-title {
    color: #ffd700;
    border-bottom: 2px solid rgba(255,215,0,0.02);
    text-shadow: 0 0 30px rgba(255,215,0,0.01);
    font-family: 'Georgia', serif;
    font-weight: 700;
    letter-spacing: 3px;
}

.rank-item {
    background: rgba(255,255,255,0.01);
    border-left: 3px solid rgba(255,215,0,0.02);
    transition: all 0.4s ease;
    font-family: 'Georgia', serif;
}

.rank-item:hover {
    background: rgba(255,215,0,0.01);
    transform: translateX(8px);
    border-left-color: rgba(255,215,0,0.05);
}

.rank-number {
    color: #ffd700;
    font-family: 'Georgia', serif;
}

.progress-bar {
    background: rgba(255,255,255,0.01);
    border-radius: 0 !important;
    height: 4px;
}

.progress-fill {
    background: linear-gradient(90deg, #ffd700, #ff6b35);
    border-radius: 0 !important;
}

.concept-card {
    background: rgba(255,255,255,0.01);
    border: 1px solid rgba(255,215,0,0.01);
    transition: all 0.4s ease;
    border-radius: 0 !important;
}

.concept-card:hover {
    border-color: rgba(255,215,0,0.02);
    transform: translateY(-3px);
}

.concept-name {
    color: #ffd700;
    font-family: 'Georgia', serif;
}

.concept-score {
    color: rgba(200,200,216,0.2);
}

.clickable-link {
    color: #ffd700;
    font-family: 'Georgia', serif;
    border-bottom: 1px dotted rgba(255,215,0,0.02);
}

.clickable-link:hover {
    color: #ff6b35;
    text-shadow: 0 0 20px rgba(255,215,0,0.02);
}

.reviewer-card {
    background: rgba(20,20,50,0.3);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,215,0,0.01);
    border-left: 4px solid rgba(255,215,0,0.02);
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-radius: 0 !important;
}

.reviewer-card:hover {
    background: rgba(255,215,0,0.01);
}

.reviewer-name {
    color: #ffd700;
    font-family: 'Georgia', serif;
}

th {
    background: rgba(255,215,0,0.02);
    color: #ffd700;
    border-bottom: 2px solid rgba(255,215,0,0.02);
    font-family: 'Georgia', serif;
}

td {
    color: rgba(200,200,216,0.5);
}

tr:hover {
    background: rgba(255,215,0,0.01);
}

.normal-article {
    border-left: 3px solid rgba(255,215,0,0.03) !important;
    background: none !important;
}

.notfound-reference {
    border-left: 3px solid rgba(128,128,128,0.03) !important;
    background: none !important;
}

.suspicious-reference {
    border-left: 3px solid rgba(255,100,100,0.03) !important;
    background: none !important;
}

.duplicate-reference {
    border-left: 3px solid rgba(255,200,100,0.03) !important;
    background: none !important;
}

.ebook-reference {
    border-left: 3px solid rgba(0,200,200,0.03) !important;
    background: none !important;
}

.repository-reference {
    border-left: 3px solid rgba(150,100,200,0.03) !important;
    background: none !important;
}

.preprint-reference {
    border-left: 3px solid rgba(150,100,200,0.03) !important;
    background: none !important;
}

.proceedings-reference {
    border-left: 3px solid rgba(200,180,100,0.03) !important;
    background: none !important;
}

.retracted-reference {
    border-left: 3px solid rgba(255,100,100,0.03) !important;
    background: none !important;
}

@keyframes cosmicIn {
    0% { opacity: 0; transform: translateY(20px) scale(0.98) rotateX(2deg); }
    100% { opacity: 1; transform: translateY(0) scale(1) rotateX(0deg); }
}

.section {
    animation: cosmicIn 0.8s ease-out forwards;
    perspective: 1000px;
}

.section:nth-child(2) { animation-delay: 0.1s; }
.section:nth-child(3) { animation-delay: 0.2s; }
.section:nth-child(4) { animation-delay: 0.3s; }
.section:nth-child(5) { animation-delay: 0.4s; }
.section:nth-child(6) { animation-delay: 0.5s; }
.section:nth-child(7) { animation-delay: 0.6s; }
.section:nth-child(8) { animation-delay: 0.7s; }
.section:nth-child(9) { animation-delay: 0.8s; }
.section:nth-child(10) { animation-delay: 0.9s; }

.footer {
    color: rgba(200,200,216,0.1);
    border-top: 2px solid rgba(255,215,0,0.01);
}

.confidential-banner {
    background: rgba(255,100,100,0.02);
    border-left: 4px solid rgba(255,100,100,0.03);
    color: #c8b8b8;
    font-family: 'Georgia', serif;
}

.badge {
    font-family: 'Georgia', serif;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.badge-success { background: rgba(255,215,0,0.05); color: #ffd700; border: 1px solid rgba(255,215,0,0.02); }
.badge-warning { background: rgba(255,200,100,0.05); color: #ffcc66; border: 1px solid rgba(255,200,100,0.02); }
.badge-danger { background: rgba(255,100,100,0.05); color: #ff8888; border: 1px solid rgba(255,100,100,0.02); }
.badge-info { background: rgba(0,200,200,0.05); color: #66cccc; border: 1px solid rgba(0,200,200,0.02); }
"""

# ======================== ТЕМА 7: BRUTALIST (БРУТАЛИСТ) ========================

BRUTALIST_CSS = """
/* ==================== ТЕМА: BRUTALIST ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: #f5f0eb;
    color: #1a1a1a;
    font-family: 'Courier New', Courier, monospace;
}

.sidebar {
    background: #1a1a1a;
    border-right: 4px solid #1a1a1a;
    color: #f5f0eb;
    box-shadow: none;
}

.sidebar h3 {
    color: #f5f0eb;
    font-weight: 900;
    letter-spacing: -1px;
    text-transform: uppercase;
    border-bottom: 4px solid #f5f0eb;
    padding-bottom: 12px;
}

.sidebar a {
    color: rgba(245,240,235,0.7);
    font-weight: 600;
    transition: all 0.05s ease;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 0.5px;
}

.sidebar a:hover {
    color: #f5f0eb;
    background: none;
    transform: translateX(4px);
    border-left: 4px solid #f5f0eb;
    padding-left: 12px;
}

.sidebar a.active {
    color: #f5f0eb;
    background: none;
    border-left: 4px solid #ff0000;
    padding-left: 12px;
}

.header {
    background: white;
    border: 4px solid #1a1a1a;
    border-radius: 0 !important;
    box-shadow: 8px 8px 0 rgba(0,0,0,0.1);
    color: #1a1a1a;
}

.header h1 {
    color: #1a1a1a;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -1px;
}

.header .date {
    color: #666;
    font-weight: 600;
}

.stat-card {
    background: white;
    border: 4px solid #1a1a1a;
    border-radius: 0 !important;
    box-shadow: 6px 6px 0 rgba(0,0,0,0.08);
    transition: all 0.05s ease;
    padding: 16px;
}

.stat-card:hover {
    transform: translate(-2px, -2px);
    box-shadow: 10px 10px 0 rgba(0,0,0,0.12);
}

.stat-number {
    font-size: 42px;
    font-weight: 900;
    background: none !important;
    -webkit-text-fill-color: #1a1a1a !important;
    color: #1a1a1a !important;
    font-family: 'Courier New', Courier, monospace;
}

.stat-percent {
    background: #1a1a1a !important;
    color: #f5f0eb !important;
    border-radius: 0 !important;
    font-weight: 900;
}

.stat-label {
    color: #666;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 1px;
}

.section {
    background: white;
    border: 4px solid #1a1a1a;
    border-radius: 0 !important;
    box-shadow: 6px 6px 0 rgba(0,0,0,0.06);
    padding: 20px;
}

.section-title {
    font-weight: 900;
    font-size: 28px;
    text-transform: uppercase;
    letter-spacing: -1px;
    border-bottom: 6px solid #1a1a1a;
    padding-bottom: 8px;
    color: #1a1a1a;
    font-family: 'Courier New', Courier, monospace;
}

.rank-item {
    background: #faf8f5;
    border: 2px solid #1a1a1a;
    border-radius: 0 !important;
    box-shadow: 4px 4px 0 rgba(0,0,0,0.04);
    transition: all 0.05s ease;
    padding: 12px 16px;
}

.rank-item:hover {
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0 rgba(0,0,0,0.08);
}

.rank-number {
    font-weight: 900;
    font-size: 18px;
    color: #1a1a1a;
}

.rank-name {
    font-weight: 700;
}

.rank-count {
    font-weight: 600;
    color: #666;
}

.progress-bar {
    background: #e0dcd8;
    border-radius: 0 !important;
    height: 6px;
}

.progress-fill {
    background: #1a1a1a !important;
    border-radius: 0 !important;
}

.concept-card {
    background: #faf8f5;
    border: 2px solid #1a1a1a;
    border-radius: 0 !important;
    box-shadow: 4px 4px 0 rgba(0,0,0,0.04);
}

.concept-card:hover {
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0 rgba(0,0,0,0.08);
}

.concept-name {
    color: #1a1a1a;
    font-weight: 900;
}

.concept-score {
    color: #666;
    font-weight: 600;
}

.clickable-link {
    color: #1a1a1a;
    font-weight: 700;
    border-bottom: 2px solid #1a1a1a;
    text-decoration: none;
}

.clickable-link:hover {
    color: #ff0000;
    border-bottom-color: #ff0000;
}

.reviewer-card {
    background: white;
    border: 4px solid #1a1a1a;
    border-radius: 0 !important;
    box-shadow: 6px 6px 0 rgba(0,0,0,0.04);
    padding: 16px;
}

.reviewer-card:hover {
    transform: translate(-2px, -2px);
    box-shadow: 8px 8px 0 rgba(0,0,0,0.08);
}

.reviewer-name {
    font-weight: 900;
    color: #1a1a1a;
    font-size: 20px;
}

.reviewer-orcid {
    font-weight: 600;
    color: #666;
}

.reviewer-section-title {
    font-weight: 900;
    color: #1a1a1a;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 1px;
}

.external-id-link {
    background: #f5f0eb;
    border: 2px solid #1a1a1a;
    border-radius: 0 !important;
    color: #1a1a1a;
    font-weight: 600;
    transition: all 0.05s ease;
}

.external-id-link:hover {
    background: #1a1a1a;
    color: #f5f0eb;
}

th {
    background: #1a1a1a !important;
    color: #f5f0eb !important;
    font-weight: 900;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 1px;
}

td {
    color: #1a1a1a;
    font-weight: 600;
    border-bottom: 2px solid #e0dcd8;
}

tr:hover {
    background: #faf8f5;
}

.normal-article {
    background: rgba(0,200,100,0.05) !important;
    border-left: 6px solid #00cc66 !important;
}

.notfound-reference {
    background: rgba(128,128,128,0.05) !important;
    border-left: 6px solid #999 !important;
}

.suspicious-reference {
    background: rgba(255,0,0,0.05) !important;
    border-left: 6px solid #cc0033 !important;
}

.duplicate-reference {
    background: rgba(255,100,0,0.05) !important;
    border-left: 6px solid #ff0000 !important;
}

.ebook-reference {
    background: rgba(0,200,200,0.05) !important;
    border-left: 6px solid #00cccc !important;
}

.repository-reference {
    background: rgba(100,0,200,0.05) !important;
    border-left: 6px solid #6600cc !important;
}

.preprint-reference {
    background: rgba(100,0,200,0.05) !important;
    border-left: 6px solid #6600cc !important;
}

.proceedings-reference {
    background: rgba(200,150,0,0.05) !important;
    border-left: 6px solid #cc9900 !important;
}

.retracted-reference {
    background: rgba(255,0,0,0.05) !important;
    border-left: 6px solid #cc0033 !important;
}

@keyframes brutalIn {
    0% { opacity: 0; transform: translateX(-20px); }
    100% { opacity: 1; transform: translateX(0); }
}

.section {
    animation: brutalIn 0.15s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.05s; }
.section:nth-child(3) { animation-delay: 0.10s; }
.section:nth-child(4) { animation-delay: 0.15s; }
.section:nth-child(5) { animation-delay: 0.20s; }
.section:nth-child(6) { animation-delay: 0.25s; }
.section:nth-child(7) { animation-delay: 0.30s; }
.section:nth-child(8) { animation-delay: 0.35s; }
.section:nth-child(9) { animation-delay: 0.40s; }
.section:nth-child(10) { animation-delay: 0.45s; }

.footer {
    color: #666;
    border-top: 4px solid #1a1a1a;
    font-weight: 600;
}

.confidential-banner {
    background: #1a1a1a;
    border-left: 6px solid #ff0000;
    color: #f5f0eb;
    border-radius: 0 !important;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 1px;
}
"""

# ======================== ТЕМА 8: MINIMALIST WHITE (МИНИМАЛИСТИЧНЫЙ БЕЛЫЙ) ========================

MINIMALIST_WHITE_CSS = """
/* ==================== ТЕМА: MINIMALIST WHITE ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: #ffffff;
    color: #1a1a1a;
    font-family: 'Georgia', 'Times New Roman', serif;
}

.sidebar {
    background: #f8f8f8;
    border-right: 1px solid #e0e0e0;
    color: #1a1a1a;
    box-shadow: none;
}

.sidebar h3 {
    color: #1a1a1a;
    font-weight: 400;
    font-size: 20px;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 15px;
    font-family: 'Georgia', serif;
}

.sidebar a {
    color: #666;
    transition: all 0.2s ease;
    font-family: 'Georgia', serif;
}

.sidebar a:hover {
    color: #1a1a1a;
    background: #f0f0f0;
    transform: none;
}

.sidebar a.active {
    color: #1a1a1a;
    background: #f0f0f0;
    font-weight: 600;
}

.header {
    background: #ffffff;
    border: none;
    border-bottom: 1px solid #e0e0e0;
    box-shadow: none;
    color: #1a1a1a;
    padding: 30px 20px;
}

.header h1 {
    color: #1a1a1a;
    font-weight: 400;
    font-size: 28px;
    font-family: 'Georgia', serif;
    letter-spacing: 0.5px;
}

.header .date {
    color: #999;
    font-size: 13px;
}

.stat-card {
    background: #fafafa;
    border: none;
    border-radius: 4px !important;
    box-shadow: none;
    padding: 24px;
    transition: background 0.2s ease;
}

.stat-card:hover {
    background: #f5f5f5;
    transform: none;
}

.stat-number {
    font-size: 38px;
    font-weight: 400;
    background: none !important;
    -webkit-text-fill-color: #1a1a1a !important;
    color: #1a1a1a !important;
    font-family: 'Georgia', serif;
}

.stat-percent {
    background: none !important;
    color: #999 !important;
    padding: 0 !important;
    font-weight: 400;
}

.stat-label {
    color: #666;
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 0.3px;
}

.section {
    background: #ffffff;
    border: none;
    border-radius: 0 !important;
    box-shadow: none;
    padding: 20px 0;
}

.section-title {
    font-weight: 400;
    font-size: 26px;
    font-family: 'Georgia', serif;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 12px;
    color: #1a1a1a;
}

.rank-item {
    background: #fafafa;
    border: none;
    border-left: 2px solid #1a1a1a !important;
    border-radius: 0 !important;
    box-shadow: none;
    padding: 12px 16px;
    transition: background 0.2s ease;
}

.rank-item:hover {
    background: #f5f5f5;
    transform: none;
}

.rank-number {
    font-weight: 400;
    font-size: 16px;
    color: #1a1a1a;
}

.rank-name {
    font-weight: 400;
}

.rank-count {
    color: #666;
}

.progress-bar {
    background: #f0f0f0;
    border-radius: 2px !important;
    height: 3px;
}

.progress-fill {
    background: #1a1a1a !important;
    border-radius: 2px !important;
}

.concept-card {
    background: #fafafa;
    border: none;
    border-radius: 4px !important;
    box-shadow: none;
    padding: 12px;
}

.concept-card:hover {
    background: #f5f5f5;
    transform: none;
}

.concept-name {
    color: #1a1a1a;
    font-weight: 400;
}

.concept-score {
    color: #999;
}

.clickable-link {
    color: #1a1a1a;
    text-decoration: underline;
    text-decoration-color: #e0e0e0;
    text-underline-offset: 3px;
}

.clickable-link:hover {
    color: #666;
    text-decoration-color: #666;
}

.reviewer-card {
    background: #fafafa;
    border: none;
    border-left: 2px solid #1a1a1a !important;
    border-radius: 0 !important;
    box-shadow: none;
    padding: 16px;
}

.reviewer-card:hover {
    background: #f5f5f5;
    transform: none;
}

.reviewer-name {
    color: #1a1a1a;
    font-weight: 400;
    font-size: 18px;
    font-family: 'Georgia', serif;
}

.reviewer-orcid {
    color: #999;
    font-family: monospace;
}

.reviewer-section-title {
    font-weight: 400;
    color: #666;
    font-size: 13px;
}

.external-id-link {
    background: #f0f0f0;
    border: none;
    border-radius: 2px !important;
    color: #1a1a1a;
    transition: background 0.2s ease;
}

.external-id-link:hover {
    background: #e0e0e0;
    color: #1a1a1a;
}

th {
    background: #f8f8f8 !important;
    color: #1a1a1a !important;
    font-weight: 400;
    border-bottom: 1px solid #e0e0e0;
}

td {
    color: #1a1a1a;
    border-bottom: 1px solid #f0f0f0;
}

tr:hover {
    background: #fafafa;
}

.normal-article {
    border-left: 3px solid #1a1a1a !important;
    background: none !important;
}

.notfound-reference {
    border-left: 3px solid #ccc !important;
    background: none !important;
}

.suspicious-reference {
    border-left: 3px solid #cc0033 !important;
    background: none !important;
}

.duplicate-reference {
    border-left: 3px solid #ff6600 !important;
    background: none !important;
}

.ebook-reference {
    border-left: 3px solid #008888 !important;
    background: none !important;
}

.repository-reference {
    border-left: 3px solid #6600cc !important;
    background: none !important;
}

.preprint-reference {
    border-left: 3px solid #6600cc !important;
    background: none !important;
}

.proceedings-reference {
    border-left: 3px solid #cc9900 !important;
    background: none !important;
}

.retracted-reference {
    border-left: 3px solid #cc0033 !important;
    background: none !important;
}

@keyframes minimalIn {
    0% { opacity: 0; }
    100% { opacity: 1; }
}

.section {
    animation: minimalIn 0.5s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.1s; }
.section:nth-child(3) { animation-delay: 0.2s; }
.section:nth-child(4) { animation-delay: 0.3s; }
.section:nth-child(5) { animation-delay: 0.4s; }
.section:nth-child(6) { animation-delay: 0.5s; }
.section:nth-child(7) { animation-delay: 0.6s; }
.section:nth-child(8) { animation-delay: 0.7s; }
.section:nth-child(9) { animation-delay: 0.8s; }
.section:nth-child(10) { animation-delay: 0.9s; }

.footer {
    color: #999;
    border-top: 1px solid #e0e0e0;
}

.confidential-banner {
    background: #fafafa;
    border-left: 4px solid #cc0033;
    color: #1a1a1a;
    border-radius: 0 !important;
}
"""

# ======================== ТЕМА 9: TERRAZZO (ТЕРРАЦЦО) ========================

TERRAZZO_CSS = """
/* ==================== ТЕМА: TERRAZZO ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: #f5f0eb;
    background-image: 
        radial-gradient(circle at 8% 15%, #e8d5c4 1px, transparent 1px),
        radial-gradient(circle at 22% 45%, #d4b8a8 1px, transparent 1px),
        radial-gradient(circle at 35% 8%, #c4a898 1px, transparent 1px),
        radial-gradient(circle at 48% 32%, #e8d5c4 1px, transparent 1px),
        radial-gradient(circle at 55% 68%, #d4b8a8 1px, transparent 1px),
        radial-gradient(circle at 70% 22%, #c4a898 1px, transparent 1px),
        radial-gradient(circle at 82% 55%, #e8d5c4 1px, transparent 1px),
        radial-gradient(circle at 92% 78%, #d4b8a8 1px, transparent 1px),
        radial-gradient(circle at 15% 85%, #c4a898 1px, transparent 1px),
        radial-gradient(circle at 45% 92%, #e8d5c4 1px, transparent 1px),
        radial-gradient(circle at 65% 88%, #d4b8a8 1px, transparent 1px),
        radial-gradient(circle at 85% 92%, #c4a898 1px, transparent 1px);
    background-size: 120px 120px;
    background-repeat: repeat;
    color: #4a3525;
}

.sidebar {
    background: rgba(255,248,240,0.95);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-right: 1px solid rgba(200,180,160,0.2);
    color: #4a3525;
    box-shadow: 0 0 40px rgba(0,0,0,0.02);
}

.sidebar h3 {
    color: #4a3525;
    font-weight: 600;
    border-bottom: 2px solid #c4a898;
    padding-bottom: 15px;
}

.sidebar a {
    color: rgba(74,53,37,0.6);
    transition: all 0.3s ease;
}

.sidebar a:hover {
    color: #4a3525;
    background: rgba(196,168,152,0.1);
}

.sidebar a.active {
    color: #4a3525;
    background: rgba(196,168,152,0.15);
    font-weight: 600;
}

.header {
    background: rgba(255,248,240,0.9);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(200,180,160,0.15);
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    color: #4a3525;
}

.header h1 {
    color: #4a3525;
    font-weight: 700;
}

.header .date {
    color: rgba(74,53,37,0.5);
}

.stat-card {
    background: rgba(255,248,240,0.7);
    border: 1px solid rgba(200,180,160,0.1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    transition: all 0.3s ease;
    padding: 20px;
}

.stat-card:nth-child(6n+1) { background: rgba(235,215,195,0.6); }
.stat-card:nth-child(6n+2) { background: rgba(245,225,210,0.6); }
.stat-card:nth-child(6n+3) { background: rgba(225,205,185,0.6); }
.stat-card:nth-child(6n+4) { background: rgba(240,220,200,0.6); }
.stat-card:nth-child(6n+5) { background: rgba(230,210,190,0.6); }
.stat-card:nth-child(6n+6) { background: rgba(250,230,215,0.6); }

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.04);
}

.stat-number {
    font-size: 38px;
    font-weight: 700;
    background: none !important;
    -webkit-text-fill-color: #4a3525 !important;
    color: #4a3525 !important;
}

.stat-percent {
    background: rgba(74,53,37,0.05);
    color: #4a3525;
}

.stat-label {
    color: rgba(74,53,37,0.7);
}

.section {
    background: rgba(255,248,240,0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(200,180,160,0.08);
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}

.section-title {
    color: #4a3525;
    border-bottom: 2px solid #c4a898;
    font-weight: 700;
}

.rank-item {
    background: rgba(255,248,240,0.5);
    border-left: 3px solid #c4a898 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    transition: all 0.3s ease;
}

.rank-item:hover {
    background: rgba(255,248,240,0.8);
    transform: translateX(6px);
}

.rank-number {
    color: #4a3525;
    font-weight: 700;
}

.progress-bar {
    background: rgba(196,168,152,0.15);
}

.progress-fill {
    background: #4a3525 !important;
}

.concept-card {
    background: rgba(255,248,240,0.5);
    border: 1px solid rgba(200,180,160,0.08);
    transition: all 0.3s ease;
}

.concept-card:hover {
    background: rgba(255,248,240,0.8);
    transform: translateY(-3px);
}

.concept-name {
    color: #4a3525;
    font-weight: 600;
}

.concept-score {
    color: rgba(74,53,37,0.5);
}

.clickable-link {
    color: #4a3525;
    border-bottom: 1px solid #c4a898;
    text-decoration: none;
}

.clickable-link:hover {
    color: #8a6a5a;
    border-bottom-color: #8a6a5a;
}

.reviewer-card {
    background: rgba(255,248,240,0.6);
    border: 1px solid rgba(200,180,160,0.08);
    border-left: 4px solid #c4a898;
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}

.reviewer-card:hover {
    background: rgba(255,248,240,0.8);
}

.reviewer-name {
    color: #4a3525;
    font-weight: 700;
}

th {
    background: rgba(196,168,152,0.15);
    color: #4a3525;
    border-bottom: 2px solid #c4a898;
}

td {
    color: rgba(74,53,37,0.7);
}

tr:hover {
    background: rgba(196,168,152,0.05);
}

.normal-article {
    background: rgba(100,200,150,0.05) !important;
    border-left: 3px solid rgba(100,200,150,0.3) !important;
}

.notfound-reference {
    background: rgba(128,128,128,0.05) !important;
    border-left: 3px solid rgba(128,128,128,0.3) !important;
}

.suspicious-reference {
    background: rgba(200,50,50,0.05) !important;
    border-left: 3px solid rgba(200,50,50,0.3) !important;
}

.duplicate-reference {
    background: rgba(200,150,50,0.05) !important;
    border-left: 3px solid rgba(200,150,50,0.3) !important;
}

.ebook-reference {
    background: rgba(50,150,200,0.05) !important;
    border-left: 3px solid rgba(50,150,200,0.3) !important;
}

.repository-reference {
    background: rgba(150,50,200,0.05) !important;
    border-left: 3px solid rgba(150,50,200,0.3) !important;
}

.preprint-reference {
    background: rgba(150,50,200,0.05) !important;
    border-left: 3px solid rgba(150,50,200,0.3) !important;
}

.proceedings-reference {
    background: rgba(200,150,50,0.05) !important;
    border-left: 3px solid rgba(200,150,50,0.3) !important;
}

.retracted-reference {
    background: rgba(200,50,50,0.05) !important;
    border-left: 3px solid rgba(200,50,50,0.3) !important;
}

@keyframes terrazzoIn {
    0% { opacity: 0; transform: scale(0.98); }
    100% { opacity: 1; transform: scale(1); }
}

.section {
    animation: terrazzoIn 0.5s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.05s; }
.section:nth-child(3) { animation-delay: 0.10s; }
.section:nth-child(4) { animation-delay: 0.15s; }
.section:nth-child(5) { animation-delay: 0.20s; }
.section:nth-child(6) { animation-delay: 0.25s; }
.section:nth-child(7) { animation-delay: 0.30s; }
.section:nth-child(8) { animation-delay: 0.35s; }
.section:nth-child(9) { animation-delay: 0.40s; }
.section:nth-child(10) { animation-delay: 0.45s; }

.footer {
    color: rgba(74,53,37,0.3);
    border-top-color: rgba(200,180,160,0.1);
}

.confidential-banner {
    background: rgba(200,50,50,0.03);
    border-left: 4px solid rgba(200,50,50,0.2);
    color: #8a4a4a;
}
"""

# ======================== ТЕМА 10: MODERN CARDS (СОВРЕМЕННЫЕ КАРТОЧКИ) ========================

MODERN_CARDS_CSS = """
/* ==================== ТЕМА: MODERN CARDS ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: #f0f2f5;
    color: #2d3436;
}

.sidebar {
    background: #ffffff;
    border-right: 1px solid rgba(0,0,0,0.04);
    color: #2d3436;
    box-shadow: 2px 0 20px rgba(0,0,0,0.02);
}

.sidebar h3 {
    color: #2d3436;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 0.5px;
    border-bottom: 2px solid #dfe6e9;
    padding-bottom: 15px;
}

.sidebar a {
    color: rgba(45,52,54,0.6);
    transition: all 0.3s ease;
    border-radius: 8px;
}

.sidebar a:hover {
    color: #2d3436;
    background: #f0f2f5;
    transform: translateX(4px);
}

.sidebar a.active {
    color: #2d3436;
    background: #f0f2f5;
    font-weight: 600;
}

.header {
    background: #ffffff;
    border: none;
    box-shadow: 0 2px 20px rgba(0,0,0,0.02);
    color: #2d3436;
    border-radius: 16px;
}

.header h1 {
    color: #2d3436;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.header .date {
    color: rgba(45,52,54,0.4);
}

.stat-card {
    background: #ffffff;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    padding: 24px;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    border: none;
    position: relative;
    overflow: hidden;
}

.stat-card:nth-child(6n+1) { transform: rotate(0.3deg) translateY(-2px); }
.stat-card:nth-child(6n+2) { transform: rotate(-0.2deg) translateY(1px); }
.stat-card:nth-child(6n+3) { transform: rotate(0.5deg) translateY(-1px); }
.stat-card:nth-child(6n+4) { transform: rotate(-0.4deg) translateY(2px); }
.stat-card:nth-child(6n+5) { transform: rotate(0.2deg) translateY(-1px); }
.stat-card:nth-child(6n+6) { transform: rotate(-0.3deg) translateY(1px); }

.stat-card:hover {
    transform: rotate(0deg) translateY(-8px) !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.08);
}

.stat-card[data-type="doi"] { border-top: 4px solid #00b894; }
.stat-card[data-type="authors"] { border-top: 4px solid #6c5ce7; }
.stat-card[data-type="citations"] { border-top: 4px solid #fdcb6e; }
.stat-card[data-type="journals"] { border-top: 4px solid #00cec9; }
.stat-card[data-type="publishers"] { border-top: 4px solid #fd79a8; }
.stat-card[data-type="orcid"] { border-top: 4px solid #0984e3; }
.stat-card[data-type="selfcitations"] { border-top: 4px solid #e17055; }

.stat-number {
    font-size: 38px;
    font-weight: 800;
    background: none !important;
    -webkit-text-fill-color: #2d3436 !important;
    color: #2d3436 !important;
}

.stat-percent {
    background: rgba(45,52,54,0.04);
    color: #2d3436;
    font-weight: 600;
}

.stat-label {
    color: rgba(45,52,54,0.6);
    font-weight: 500;
}

.section {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 20px 0;
}

.section-title {
    font-weight: 800;
    font-size: 28px;
    color: #2d3436;
    border-bottom: 3px solid #dfe6e9;
    padding-bottom: 12px;
    letter-spacing: -0.5px;
}

.rank-item {
    background: #ffffff;
    border-radius: 12px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.02);
    padding: 16px 20px;
    border-left: 4px solid #6c5ce7 !important;
    transition: all 0.3s ease;
}

.rank-item:hover {
    transform: translateX(8px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.rank-number {
    font-weight: 700;
    color: #6c5ce7;
    font-size: 16px;
}

.rank-name {
    font-weight: 600;
}

.rank-count {
    color: rgba(45,52,54,0.6);
}

.progress-bar {
    background: #f0f2f5;
    border-radius: 6px !important;
    height: 6px;
}

.progress-fill {
    background: #6c5ce7 !important;
    border-radius: 6px !important;
}

.concept-card {
    background: #ffffff;
    border-radius: 12px !important;
    border: none;
    box-shadow: 0 2px 12px rgba(0,0,0,0.02);
    padding: 16px;
    transition: all 0.3s ease;
}

.concept-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

.concept-name {
    color: #2d3436;
    font-weight: 700;
}

.concept-score {
    color: rgba(45,52,54,0.4);
}

.clickable-link {
    color: #6c5ce7;
    font-weight: 600;
    text-decoration: none;
    border-bottom: 2px solid rgba(108,92,231,0.1);
}

.clickable-link:hover {
    color: #5a4bd1;
    border-bottom-color: #6c5ce7;
}

.reviewer-card {
    background: #ffffff;
    border-radius: 12px !important;
    border: none;
    border-left: 4px solid #6c5ce7 !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.02);
    padding: 16px;
    transition: all 0.3s ease;
}

.reviewer-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

.reviewer-name {
    color: #2d3436;
    font-weight: 700;
    font-size: 18px;
}

.reviewer-orcid {
    color: rgba(45,52,54,0.5);
}

.reviewer-section-title {
    font-weight: 600;
    color: rgba(45,52,54,0.6);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.external-id-link {
    background: #f0f2f5;
    border-radius: 8px !important;
    color: #2d3436;
    font-weight: 500;
    transition: all 0.3s ease;
}

.external-id-link:hover {
    background: #6c5ce7;
    color: #ffffff;
}

th {
    background: #f8f9fa !important;
    color: #2d3436 !important;
    font-weight: 700;
    border-bottom: 2px solid #dfe6e9;
}

td {
    color: rgba(45,52,54,0.7);
    border-bottom: 1px solid #f0f2f5;
}

tr:hover {
    background: #f8f9fa;
}

.normal-article {
    background: rgba(0,184,148,0.04) !important;
    border-left: 4px solid #00b894 !important;
}

.notfound-reference {
    background: rgba(128,128,128,0.04) !important;
    border-left: 4px solid #b2bec3 !important;
}

.suspicious-reference {
    background: rgba(225,112,85,0.04) !important;
    border-left: 4px solid #e17055 !important;
}

.duplicate-reference {
    background: rgba(253,203,110,0.04) !important;
    border-left: 4px solid #fdcb6e !important;
}

.ebook-reference {
    background: rgba(0,206,201,0.04) !important;
    border-left: 4px solid #00cec9 !important;
}

.repository-reference {
    background: rgba(108,92,231,0.04) !important;
    border-left: 4px solid #6c5ce7 !important;
}

.preprint-reference {
    background: rgba(108,92,231,0.04) !important;
    border-left: 4px solid #6c5ce7 !important;
}

.proceedings-reference {
    background: rgba(253,121,168,0.04) !important;
    border-left: 4px solid #fd79a8 !important;
}

.retracted-reference {
    background: rgba(225,112,85,0.04) !important;
    border-left: 4px solid #e17055 !important;
}

@keyframes modernIn {
    0% { opacity: 0; transform: scale(0.96); }
    50% { transform: scale(1.01); }
    100% { opacity: 1; transform: scale(1); }
}

.section {
    animation: modernIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

.section:nth-child(2) { animation-delay: 0.05s; }
.section:nth-child(3) { animation-delay: 0.10s; }
.section:nth-child(4) { animation-delay: 0.15s; }
.section:nth-child(5) { animation-delay: 0.20s; }
.section:nth-child(6) { animation-delay: 0.25s; }
.section:nth-child(7) { animation-delay: 0.30s; }
.section:nth-child(8) { animation-delay: 0.35s; }
.section:nth-child(9) { animation-delay: 0.40s; }
.section:nth-child(10) { animation-delay: 0.45s; }

.footer {
    color: rgba(45,52,54,0.3);
    border-top: 2px solid #dfe6e9;
}

.confidential-banner {
    background: rgba(225,112,85,0.04);
    border-left: 4px solid #e17055;
    color: #2d3436;
    border-radius: 8px !important;
}
"""

# ======================== ТЕМА 11: DUOTONE (ДВУХЦВЕТНЫЙ) ========================

DUOTONE_CSS = """
/* ==================== ТЕМА: DUOTONE ==================== */
/* Полностью отключает пользовательские цвета */

body {
    background: #ffffff;
    color: #2d3436;
}

.sidebar {
    background: #fafafa;
    border-right: 1px solid #f0f0f0;
    color: #2d3436;
}

.sidebar h3 {
    color: #2d3436;
    font-weight: 700;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 15px;
}

.sidebar a {
    color: rgba(45,52,54,0.5);
    transition: all 0.3s ease;
}

.sidebar a:hover {
    color: #2d3436;
    background: #f5f5f5;
}

.sidebar a.active {
    color: #2d3436;
    background: #f5f5f5;
    font-weight: 600;
}

.header {
    background: #ffffff;
    border: none;
    border-bottom: 2px solid #f0f0f0;
    box-shadow: none;
    color: #2d3436;
}

.header h1 {
    color: #2d3436;
    font-weight: 800;
}

.header .date {
    color: rgba(45,52,54,0.3);
}

#overview .stat-card { background: linear-gradient(135deg, #667eea08, #764ba208); }
#overview .stat-number { background: linear-gradient(135deg, #667eea, #764ba2) !important; }
#overview .section-title { border-color: #667eea; }
#overview .stat-percent { background: #667eea10; color: #667eea; }

#identifiers .stat-card { background: linear-gradient(135deg, #f093fb08, #f5576c08); }
#identifiers .stat-number { background: linear-gradient(135deg, #f093fb, #f5576c) !important; }
#identifiers .section-title { border-color: #f5576c; }
#identifiers .stat-percent { background: #f5576c10; color: #f5576c; }

#authors .stat-card { background: linear-gradient(135deg, #4facfe08, #00f2fe08); }
#authors .stat-number { background: linear-gradient(135deg, #4facfe, #00f2fe) !important; }
#authors .section-title { border-color: #4facfe; }
#authors .stat-percent { background: #4facfe10; color: #4facfe; }

#journals .stat-card { background: linear-gradient(135deg, #43e97b08, #38f9d708); }
#journals .stat-number { background: linear-gradient(135deg, #43e97b, #38f9d7) !important; }
#journals .section-title { border-color: #43e97b; }
#journals .stat-percent { background: #43e97b10; color: #43e97b; }

#publishers .stat-card { background: linear-gradient(135deg, #fa709a08, #fee14008); }
#publishers .stat-number { background: linear-gradient(135deg, #fa709a, #fee140) !important; }
#publishers .section-title { border-color: #fa709a; }
#publishers .stat-percent { background: #fa709a10; color: #fa709a; }

#yearly .stat-card { background: linear-gradient(135deg, #f093fb08, #4facfe08); }
#yearly .stat-number { background: linear-gradient(135deg, #f093fb, #4facfe) !important; }
#yearly .section-title { border-color: #f093fb; }

#concepts .stat-card { background: linear-gradient(135deg, #43e97b08, #fa709a08); }
#concepts .stat-number { background: linear-gradient(135deg, #43e97b, #fa709a) !important; }
#concepts .section-title { border-color: #43e97b; }

#geography .stat-card { background: linear-gradient(135deg, #667eea08, #f093fb08); }
#geography .stat-number { background: linear-gradient(135deg, #667eea, #f093fb) !important; }
#geography .section-title { border-color: #667eea; }

#collaboration .stat-card { background: linear-gradient(135deg, #4facfe08, #43e97b08); }
#collaboration .stat-number { background: linear-gradient(135deg, #4facfe, #43e97b) !important; }
#collaboration .section-title { border-color: #4facfe; }

#diversity .stat-card { background: linear-gradient(135deg, #fa709a08, #fdcb6e08); }
#diversity .stat-number { background: linear-gradient(135deg, #fa709a, #fdcb6e) !important; }
#diversity .section-title { border-color: #fa709a; }

#classics .stat-card { background: linear-gradient(135deg, #f5576c08, #fdcb6e08); }
#classics .stat-number { background: linear-gradient(135deg, #f5576c, #fdcb6e) !important; }
#classics .section-title { border-color: #f5576c; }

.section {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 20px 0;
}

.section-title {
    font-weight: 700;
    font-size: 26px;
    border-bottom: 3px solid;
    padding-bottom: 12px;
}

.stat-card {
    border: none !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.02);
    border-radius: 12px !important;
    padding: 20px;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

.stat-number {
    font-weight: 800 !important;
    font-size: 36px;
}

.stat-percent {
    border: none !important;
}

.stat-label {
    color: rgba(45,52,54,0.6);
    font-weight: 500;
}

.rank-item {
    background: #fafafa;
    border: none !important;
    border-left: 4px solid #dfe6e9 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    padding: 12px 16px;
    transition: all 0.3s ease;
}

.rank-item:hover {
    transform: translateX(6px);
    background: #f5f5f5;
}

.rank-number {
    font-weight: 700;
    color: #2d3436;
}

.progress-bar {
    background: #f0f0f0;
    border-radius: 4px !important;
}

.progress-fill {
    background: #2d3436 !important;
    border-radius: 4px !important;
}

.concept-card {
    background: #fafafa;
    border: none;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    padding: 12px;
    transition: all 0.3s ease;
}

.concept-card:hover {
    background: #f5f5f5;
}

.concept-name {
    color: #2d3436;
    font-weight: 600;
}

.clickable-link {
    color: #2d3436;
    font-weight: 500;
    text-decoration: none;
    border-bottom: 2px solid #f0f0f0;
}

.clickable-link:hover {
    border-bottom-color: #2d3436;
}

.reviewer-card {
    background: #fafafa;
    border: none !important;
    border-left: 4px solid #dfe6e9 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.02);
}

.reviewer-card:hover {
    background: #f5f5f5;
}

.reviewer-name {
    color: #2d3436;
    font-weight: 700;
}

th {
    background: #f8f8f8 !important;
    color: #2d3436 !important;
    border-bottom: 2px solid #f0f0f0;
}

td {
    color: rgba(45,52,54,0.7);
    border-bottom: 1px solid #f5f5f5;
}

tr:hover {
    background: #fafafa;
}

.normal-article {
    border-left: 4px solid #00b894 !important;
    background: none !important;
}

.notfound-reference {
    border-left: 4px solid #b2bec3 !important;
    background: none !important;
}

.suspicious-reference {
    border-left: 4px solid #e17055 !important;
    background: none !important;
}

.duplicate-reference {
    border-left: 4px solid #fdcb6e !important;
    background: none !important;
}

.ebook-reference {
    border-left: 4px solid #00cec9 !important;
    background: none !important;
}

.repository-reference {
    border-left: 4px solid #6c5ce7 !important;
    background: none !important;
}

.preprint-reference {
    border-left: 4px solid #6c5ce7 !important;
    background: none !important;
}

.proceedings-reference {
    border-left: 4px solid #fd79a8 !important;
    background: none !important;
}

.retracted-reference {
    border-left: 4px solid #e17055 !important;
    background: none !important;
}

@keyframes duotoneIn {
    0% { opacity: 0; transform: translateY(15px); }
    100% { opacity: 1; transform: translateY(0); }
}

.section {
    animation: duotoneIn 0.5s ease-out forwards;
}

.section:nth-child(2) { animation-delay: 0.05s; }
.section:nth-child(3) { animation-delay: 0.10s; }
.section:nth-child(4) { animation-delay: 0.15s; }
.section:nth-child(5) { animation-delay: 0.20s; }
.section:nth-child(6) { animation-delay: 0.25s; }
.section:nth-child(7) { animation-delay: 0.30s; }
.section:nth-child(8) { animation-delay: 0.35s; }
.section:nth-child(9) { animation-delay: 0.40s; }
.section:nth-child(10) { animation-delay: 0.45s; }

.footer {
    color: rgba(45,52,54,0.2);
    border-top: 2px solid #f0f0f0;
}

.confidential-banner {
    background: #fafafa;
    border-left: 4px solid #e17055;
    color: #2d3436;
}
"""

# ======================== ТЕМА 12: MORPHING (МОРФИНГ) ========================

MORPHING_CSS = """
/* ==================== ТЕМА: MORPHING ==================== */
/* Использует {{PRIMARY}} и {{SECONDARY}} для градиентов */

body {
    background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    color: #2d3436;
}

.sidebar {
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.2);
    color: #2d3436;
    box-shadow: 0 0 40px rgba(0,0,0,0.02);
}

.sidebar h3 {
    color: #2d3436;
    font-weight: 700;
    border-bottom: 2px solid {{PRIMARY}}30;
    padding-bottom: 15px;
}

.sidebar a {
    color: rgba(45,52,54,0.6);
    transition: all 0.3s ease;
}

.sidebar a:hover {
    color: {{PRIMARY}};
    background: {{PRIMARY}}08;
}

.sidebar a.active {
    color: {{PRIMARY}};
    background: {{PRIMARY}}12;
    font-weight: 600;
}

.header {
    background: rgba(255,255,255,0.8);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.3);
    box-shadow: 0 8px 32px rgba(0,0,0,0.02);
    color: #2d3436;
}

.header h1 {
    background: linear-gradient(135deg, {{PRIMARY}}, {{SECONDARY}});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
}

.header .date {
    color: rgba(45,52,54,0.4);
}

#overview .stat-card { border-radius: 12px; background: rgba(255,255,255,0.9); }
#identifiers .stat-card { border-radius: 20px; background: rgba(255,255,255,0.85); box-shadow: 0 8px 32px rgba(0,0,0,0.02); }
#authors .stat-card { border-radius: 4px; background: white; box-shadow: 0 2px 12px rgba(0,0,0,0.02); }
#journals .stat-card { border-radius: 30px; background: rgba(255,255,255,0.7); backdrop-filter: blur(10px); }
#publishers .stat-card { border-radius: 0; background: white; box-shadow: 0 4px 16px rgba(0,0,0,0.01); }
#yearly .stat-card { border-radius: 16px; background: linear-gradient(135deg, {{PRIMARY}}08, {{SECONDARY}}08); }
#concepts .stat-card { border-radius: 8px; background: {{PRIMARY}}06; }
#geography .stat-card { border-radius: 24px; background: {{SECONDARY}}06; }
#collaboration .stat-card { border-radius: 12px; background: linear-gradient(135deg, {{PRIMARY}}04, {{SECONDARY}}04); }
#diversity .stat-card { border-radius: 4px; background: {{PRIMARY}}03; }
#classics .stat-card { border-radius: 20px; background: linear-gradient(135deg, {{SECONDARY}}06, {{PRIMARY}}06); }

.stat-card {
    border: none;
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    padding: 20px;
    transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.stat-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 48px rgba(0,0,0,0.06);
}

.stat-number {
    font-size: 38px;
    font-weight: 800;
    background: linear-gradient(135deg, {{PRIMARY}}, {{SECONDARY}});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-percent {
    background: rgba(0,0,0,0.03);
    color: #2d3436;
    font-weight: 600;
}

.stat-label {
    color: rgba(45,52,54,0.6);
    font-weight: 500;
}

.section {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 20px 0;
    opacity: 0;
    transform: translateY(30px);
    animation: morphIn 0.6s ease forwards;
}

.section:nth-child(2) { animation-delay: 0.05s; }
.section:nth-child(3) { animation-delay: 0.10s; }
.section:nth-child(4) { animation-delay: 0.15s; }
.section:nth-child(5) { animation-delay: 0.20s; }
.section:nth-child(6) { animation-delay: 0.25s; }
.section:nth-child(7) { animation-delay: 0.30s; }
.section:nth-child(8) { animation-delay: 0.35s; }
.section:nth-child(9) { animation-delay: 0.40s; }
.section:nth-child(10) { animation-delay: 0.45s; }

@keyframes morphIn {
    0% { opacity: 0; transform: translateY(30px) scale(0.95); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

.section-title {
    font-weight: 800;
    font-size: 28px;
    background: linear-gradient(135deg, {{PRIMARY}}, {{SECONDARY}});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    border-bottom: 3px solid {{PRIMARY}}30;
    padding-bottom: 12px;
}

#overview .rank-item { border-radius: 8px; }
#authors .rank-item { border-radius: 16px; border-left: 4px solid {{PRIMARY}} !important; }
#journals .rank-item { border-radius: 4px; border-left: 6px solid {{SECONDARY}} !important; }
#publishers .rank-item { border-radius: 20px; border-left: 3px solid {{PRIMARY}} !important; }
#yearly .rank-item { border-radius: 12px; background: {{PRIMARY}}04; }
#concepts .rank-item { border-radius: 0; border-left: none !important; }
#geography .rank-item { border-radius: 8px; background: {{SECONDARY}}04; }

.rank-item {
    background: rgba(255,255,255,0.5);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255,255,255,0.2);
    border-left: 4px solid {{PRIMARY}} !important;
    padding: 12px 16px;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.rank-item:hover {
    transform: translateX(8px) scale(1.01);
    background: rgba(255,255,255,0.8);
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

.rank-number {
    font-weight: 700;
    color: {{PRIMARY}};
}

.progress-bar {
    background: rgba(0,0,0,0.04);
    border-radius: 8px !important;
}

.progress-fill {
    background: linear-gradient(90deg, {{PRIMARY}}, {{SECONDARY}});
    border-radius: 8px !important;
}

.concept-card {
    background: rgba(255,255,255,0.5);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px !important;
    padding: 12px;
    transition: all 0.4s ease;
}

.concept-card:hover {
    transform: translateY(-4px);
    background: rgba(255,255,255,0.8);
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

.concept-name {
    font-weight: 600;
    background: linear-gradient(135deg, {{PRIMARY}}, {{SECONDARY}});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.clickable-link {
    color: {{PRIMARY}};
    font-weight: 600;
    text-decoration: none;
    border-bottom: 2px solid {{PRIMARY}}30;
    transition: all 0.3s ease;
}

.clickable-link:hover {
    color: {{SECONDARY}};
    border-bottom-color: {{SECONDARY}};
}

.reviewer-card {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    border-left: 4px solid {{PRIMARY}} !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    transition: all 0.4s ease;
}

.reviewer-card:hover {
    transform: translateY(-4px);
    background: rgba(255,255,255,0.8);
    box-shadow: 0 8px 30px rgba(0,0,0,0.04);
}

.reviewer-name {
    font-weight: 700;
    background: linear-gradient(135deg, {{PRIMARY}}, {{SECONDARY}});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 18px;
}

th {
    background: linear-gradient(135deg, {{PRIMARY}}08, {{SECONDARY}}08) !important;
    color: #2d3436 !important;
    font-weight: 700;
    border-bottom: 2px solid {{PRIMARY}}30;
}

td {
    color: rgba(45,52,54,0.7);
    border-bottom: 1px solid rgba(0,0,0,0.03);
}

tr:hover {
    background: {{PRIMARY}}04;
}

.normal-article {
    background: rgba(0,184,148,0.06) !important;
    border-left: 4px solid #00b894 !important;
}

.notfound-reference {
    background: rgba(128,128,128,0.06) !important;
    border-left: 4px solid #b2bec3 !important;
}

.suspicious-reference {
    background: rgba(225,112,85,0.06) !important;
    border-left: 4px solid #e17055 !important;
}

.duplicate-reference {
    background: rgba(253,203,110,0.06) !important;
    border-left: 4px solid #fdcb6e !important;
}

.ebook-reference {
    background: rgba(0,206,201,0.06) !important;
    border-left: 4px solid #00cec9 !important;
}

.repository-reference {
    background: rgba(108,92,231,0.06) !important;
    border-left: 4px solid #6c5ce7 !important;
}

.preprint-reference {
    background: rgba(108,92,231,0.06) !important;
    border-left: 4px solid #6c5ce7 !important;
}

.proceedings-reference {
    background: rgba(253,121,168,0.06) !important;
    border-left: 4px solid #fd79a8 !important;
}

.retracted-reference {
    background: rgba(225,112,85,0.06) !important;
    border-left: 4px solid #e17055 !important;
}

.footer {
    color: rgba(45,52,54,0.2);
    border-top: 2px solid {{PRIMARY}}20;
}

.confidential-banner {
    background: linear-gradient(135deg, {{PRIMARY}}06, {{SECONDARY}}06);
    border-left: 4px solid {{PRIMARY}};
    color: #2d3436;
}
"""

# ======================== ЦВЕТНАЯ КОДИРОВКА ДЛЯ СПИСКА ЛИТЕРАТУРЫ ========================

REFERENCE_COLORS_FULL = """
/* ==================== ЦВЕТНАЯ КОДИРОВКА - ПОЛНАЯ (ФОН + ГРАНИЦА) ==================== */
.normal-article {
    background: #e8f5e9 !important;
    border-left: 3px solid #4caf50 !important;
}
.notfound-reference {
    background: #e9ecef !important;
    border-left: 3px solid #6c757d !important;
}
.suspicious-reference {
    background: #f8d7da !important;
    border-left: 3px solid #dc3545 !important;
}
.duplicate-reference {
    background: #ffe5cc !important;
    border-left: 3px solid #fd7e14 !important;
}
.ebook-reference {
    background: #d4f1e9 !important;
    border-left: 3px solid #0e6b5e !important;
}
.repository-reference {
    background: #e2d5f8 !important;
    border-left: 3px solid #5e2a9e !important;
}
.preprint-reference {
    background: #e2d5f8 !important;
    border-left: 3px solid #5e2a9e !important;
}
.proceedings-reference {
    background: #fff2c9 !important;
    border-left: 3px solid #b26b00 !important;
}
.retracted-reference {
    background: #f8d7da !important;
    border-left: 3px solid #dc3545 !important;
}
"""

REFERENCE_COLORS_BORDER_ONLY = """
/* ==================== ЦВЕТНАЯ КОДИРОВКА - ТОЛЬКО ГРАНИЦА ==================== */
.normal-article {
    border-left: 4px solid #4caf50 !important;
}
.notfound-reference {
    border-left: 4px solid #6c757d !important;
}
.suspicious-reference {
    border-left: 4px solid #dc3545 !important;
}
.duplicate-reference {
    border-left: 4px solid #fd7e14 !important;
}
.ebook-reference {
    border-left: 4px solid #0e6b5e !important;
}
.repository-reference {
    border-left: 4px solid #5e2a9e !important;
}
.preprint-reference {
    border-left: 4px solid #5e2a9e !important;
}
.proceedings-reference {
    border-left: 4px solid #b26b00 !important;
}
.retracted-reference {
    border-left: 4px solid #dc3545 !important;
}
"""

REFERENCE_COLORS_ICONS = """
/* ==================== ЦВЕТНАЯ КОДИРОВКА - ТОЛЬКО БЭЙДЖИ ==================== */
.normal-article .badge { background: #4caf50; color: white; }
.notfound-reference .badge { background: #6c757d; color: white; }
.suspicious-reference .badge { background: #dc3545; color: white; }
.duplicate-reference .badge { background: #fd7e14; color: white; }
.ebook-reference .badge { background: #0e6b5e; color: white; }
.repository-reference .badge { background: #5e2a9e; color: white; }
.preprint-reference .badge { background: #5e2a9e; color: white; }
.proceedings-reference .badge { background: #b26b00; color: white; }
.retracted-reference .badge { background: #dc3545; color: white; }
"""

REFERENCE_COLORS_THEMED = """
/* ==================== ЦВЕТНАЯ КОДИРОВКА - СЛЕДУЕТ ТЕМЕ ==================== */
.normal-article { border-left: 4px solid {{PRIMARY}} !important; }
.notfound-reference { border-left: 4px solid {{SECONDARY}}40 !important; }
.suspicious-reference { border-left: 4px solid #dc3545 !important; }
.duplicate-reference { border-left: 4px solid #fd7e14 !important; }
.ebook-reference { border-left: 4px solid {{SECONDARY}} !important; }
.repository-reference { border-left: 4px solid {{PRIMARY}}80 !important; }
.preprint-reference { border-left: 4px solid {{PRIMARY}}80 !important; }
.proceedings-reference { border-left: 4px solid #b26b00 !important; }
.retracted-reference { border-left: 4px solid #dc3545 !important; }
"""

REFERENCE_COLORS_TEXT = """
/* ==================== ЦВЕТНАЯ КОДИРОВКА - ТОЛЬКО ТЕКСТ ==================== */
.normal-article .status-icon { color: #4caf50; }
.notfound-reference .status-icon { color: #6c757d; }
.suspicious-reference .status-icon { color: #dc3545; }
.duplicate-reference .status-icon { color: #fd7e14; }
.ebook-reference .status-icon { color: #0e6b5e; }
.repository-reference .status-icon { color: #5e2a9e; }
.preprint-reference .status-icon { color: #5e2a9e; }
.proceedings-reference .status-icon { color: #b26b00; }
.retracted-reference .status-icon { color: #dc3545; }
"""

# ======================== ИНФОРМАЦИЯ О ТЕМАХ ========================

THEMES_INFO = {
    'default': {
        'name': 'Gradient Classic',
        'description': 'Классический градиентный дизайн по умолчанию',
        'uses_primary': True,
        'uses_secondary': True,
        'css_generator': 'generate_default_css'
    },
    'glassmorphism': {
        'name': 'Glassmorphism',
        'description': 'Матовое стекло с размытием и прозрачностью',
        'uses_primary': True,
        'uses_secondary': False,
        'css_generator': 'generate_glassmorphism_css'
    },
    'neon_dark': {
        'name': 'Neon Dark - Cyberpunk',
        'description': 'Киберпанк с динамическими неоновыми карточками и бегущим свечением',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_neon_dark_css'
    },
    'aurora': {
        'name': 'Aurora Borealis - Arctic Night',
        'description': 'Арктическая ночь с эффектом инея и полярным сиянием в хедере',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_aurora_css'
    },
    'brutalist': {
        'name': 'Brutalist',
        'description': 'Брутальный архитектурный стиль с красными акцентами',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_brutalist_css'
    },
    'minimalist_white': {
        'name': 'Minimalist White',
        'description': 'Минималистичный белый с серифным шрифтом',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_minimalist_white_css'
    },
    'ocean_deep': {
        'name': 'Ocean Deep - Sunken Wreck',
        'description': 'Глубина океана с эффектом затонувшего корабля и пузырьками',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_ocean_deep_css'
    },
    'cosmic': {
        'name': 'Cosmic - Retro Space 70s',
        'description': 'Ретро-футуристический космос 70-х с винтажной эстетикой',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_cosmic_css'
    },
    'terrazzo': {
        'name': 'Terrazzo',
        'description': 'Терраццо с теплой текстурой и керамической плиткой',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_terrazzo_css'
    },
    'modern_cards': {
        'name': 'Modern Cards',
        'description': 'Современные карточки с наклоном и тенями нового поколения',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_modern_cards_css'
    },
    'duotone': {
        'name': 'Duotone',
        'description': 'Двухцветный дизайн для каждой секции с контрастными парами',
        'uses_primary': False,
        'uses_secondary': False,
        'css_generator': 'generate_duotone_css'
    },
    'morphing': {
        'name': 'Morphing',
        'description': 'Морфинг с разными стилями секций и плавными переходами',
        'uses_primary': True,
        'uses_secondary': True,
        'css_generator': 'generate_morphing_css'
    }
}

# ======================== ГЛАВНЫЙ ГЕНЕРАТОР ТЕМ ========================

def generate_theme_css(theme_name: str, primary_color: str = None, secondary_color: str = None) -> str:
    """
    Генерирует полный CSS для выбранной темы.
    Возвращает BASE_CSS + тематический CSS с подставленными цветами.
    """
    theme_name = theme_name or 'default'
    
    # Базовые стили всегда применяются
    css = BASE_CSS
    
    # Добавляем стили для цветной кодировки (по умолчанию полная)
    css += REFERENCE_COLORS_FULL
    
    # Получаем информацию о теме
    theme_info = THEMES_INFO.get(theme_name, THEMES_INFO['default'])
    
    # Генерируем CSS для выбранной темы
    if theme_name == 'default':
        theme_css = GRADIENT_CLASSIC_CSS
        if primary_color and secondary_color:
            theme_css = inject_color_placeholders(theme_css, primary_color, secondary_color)
        elif primary_color:
            theme_css = inject_color_placeholders(theme_css, primary_color)
    
    elif theme_name == 'glassmorphism':
        theme_css = GLASSMORPHISM_CSS
        if primary_color:
            theme_css = inject_color_placeholders(theme_css, primary_color)
    
    elif theme_name == 'neon_dark':
        theme_css = NEON_DARK_CSS
    
    elif theme_name == 'aurora':
        theme_css = AURORA_CSS
    
    elif theme_name == 'brutalist':
        theme_css = BRUTALIST_CSS
    
    elif theme_name == 'minimalist_white':
        theme_css = MINIMALIST_WHITE_CSS
    
    elif theme_name == 'ocean_deep':
        theme_css = OCEAN_DEEP_CSS
    
    elif theme_name == 'cosmic':
        theme_css = COSMIC_CSS
    
    elif theme_name == 'terrazzo':
        theme_css = TERRAZZO_CSS
    
    elif theme_name == 'modern_cards':
        theme_css = MODERN_CARDS_CSS
    
    elif theme_name == 'duotone':
        theme_css = DUOTONE_CSS
    
    elif theme_name == 'morphing':
        theme_css = MORPHING_CSS
        if primary_color and secondary_color:
            theme_css = inject_color_placeholders(theme_css, primary_color, secondary_color)
        elif primary_color:
            theme_css = inject_color_placeholders(theme_css, primary_color)
    
    else:
        theme_css = GRADIENT_CLASSIC_CSS
        if primary_color and secondary_color:
            theme_css = inject_color_placeholders(theme_css, primary_color, secondary_color)
        elif primary_color:
            theme_css = inject_color_placeholders(theme_css, primary_color)
    
    css += theme_css
    
    return css

def get_theme_info(theme_name: str) -> dict:
    """Возвращает информацию о теме"""
    return THEMES_INFO.get(theme_name, THEMES_INFO['default'])

def get_available_themes() -> List[str]:
    """Возвращает список доступных тем"""
    return list(THEMES_INFO.keys())

def get_theme_display_name(theme_name: str) -> str:
    """Возвращает отображаемое имя темы"""
    return THEMES_INFO.get(theme_name, THEMES_INFO['default'])['name']

def theme_uses_primary(theme_name: str) -> bool:
    """Проверяет, использует ли тема Primary цвет"""
    return THEMES_INFO.get(theme_name, THEMES_INFO['default'])['uses_primary']

def theme_uses_secondary(theme_name: str) -> bool:
    """Проверяет, использует ли тема Secondary цвет"""
    return THEMES_INFO.get(theme_name, THEMES_INFO['default'])['uses_secondary']

def get_reference_color_style(style_name: str = 'full') -> str:
    """
    Возвращает CSS для цветной кодировки ссылок.
    Доступные стили: 'full', 'border_only', 'icons', 'themed', 'text'
    """
    styles = {
        'full': REFERENCE_COLORS_FULL,
        'border_only': REFERENCE_COLORS_BORDER_ONLY,
        'icons': REFERENCE_COLORS_ICONS,
        'themed': REFERENCE_COLORS_THEMED,
        'text': REFERENCE_COLORS_TEXT
    }
    return styles.get(style_name, styles['full'])

# ======================== КОНЕЦ ФАЙЛА ========================
