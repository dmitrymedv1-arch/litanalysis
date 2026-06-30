# ============================================================
# STYLES.PY - 10 УНИКАЛЬНЫХ СТИЛЕЙ ДЛЯ HTML ОТЧЕТА
# ============================================================

from datetime import datetime
import html

def get_date():
    """Get current date for footer"""
    return datetime.now().strftime('%d.%m.%Y')

def get_footer_text():
    """Get footer text for all styles"""
    return f'© Chimica Techno Acta / Created by daM / {get_date()}'

# ============================================================
# СТИЛЬ 1: GLASSMORPHISM (Стеклянный эффект)
# ============================================================
def generate_style_glassmorphism(data, lang='en', journal_name='', article_number=''):
    """Стиль 1: Glassmorphism — стеклянный эффект с размытием"""
    date_str = get_date()
    footer = get_footer_text()
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Glassmorphism Report</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{min-height:100vh;background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);padding:30px;font-family:'Segoe UI',sans-serif;}}
.container{{max-width:1200px;margin:0 auto;}}
.glass{{background:rgba(255,255,255,0.15);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-radius:20px;padding:30px;border:1px solid rgba(255,255,255,0.2);margin-bottom:20px;box-shadow:0 8px 32px rgba(0,0,0,0.1);}}
h1{{color:#fff;font-size:32px;font-weight:300;letter-spacing:2px;}}
.subtitle{{color:rgba(255,255,255,0.7);font-size:14px;}}
.glass-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:15px;}}
.glass-stat{{background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:16px;padding:20px;text-align:center;border:1px solid rgba(255,255,255,0.1);}}
.stat-number{{font-size:28px;font-weight:700;color:#fff;}}
.stat-label{{font-size:11px;color:rgba(255,255,255,0.6);margin-top:5px;text-transform:uppercase;letter-spacing:1px;}}
.tag-glass{{display:inline-block;padding:6px 16px;background:rgba(255,255,255,0.12);border-radius:20px;margin:4px;color:#fff;font-size:13px;backdrop-filter:blur(5px);border:1px solid rgba(255,255,255,0.08);}}
.section-title{{color:#fff;font-weight:600;margin-bottom:12px;font-size:16px;letter-spacing:1px;}}
.footer{{text-align:center;color:rgba(255,255,255,0.4);font-size:11px;padding:20px;}}
</style>
</head>
<body>
<div class="container">
    <div class="glass"><h1>✦ Glassmorphism Report</h1><div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div></div>
    <div class="glass">
        <div class="glass-grid">
            <div class="glass-stat"><div class="stat-number">{data.get('total_references', 0)}</div><div class="stat-label">Total</div></div>
            <div class="glass-stat"><div class="stat-number">{data.get('total_with_doi', 0)}</div><div class="stat-label">DOI</div></div>
            <div class="glass-stat"><div class="stat-number">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="stat-label">5 Years</div></div>
            <div class="glass-stat"><div class="stat-number">{data.get('self_citations_count', 0)}</div><div class="stat-label">Self-Cit</div></div>
            <div class="glass-stat"><div class="stat-number">{data.get('total_citations_sum', 0)}</div><div class="stat-label">Citations</div></div>
        </div>
    </div>
    <div class="glass">
        <div class="section-title">👨‍🎓 Authors</div>
        {''.join([f'<span class="tag-glass">{a.get("display_name", "Unknown")} ({a.get("mention_count", 0)})</span>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:6]])}
    </div>
    <div class="glass">
        <div class="section-title">📖 Journals</div>
        {''.join([f'<span class="tag-glass">{j.get("journal", "Unknown")} ({j.get("count", 0)})</span>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:5]])}
    </div>
    <div class="glass">
        <div class="section-title">🌍 Geography</div>
        {''.join([f'<span class="tag-glass">{c}: {count}</span>' for c, count in list(data.get('geography', {}).get('type1_unique_countries_per_reference', {}).items())[:5]])}
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 2: NEON CYBER (Неоновое свечение)
# ============================================================
def generate_style_neon_cyber(data, lang='en', journal_name='', article_number=''):
    """Стиль 2: Neon Cyber — неоновое свечение на темном фоне"""
    date_str = get_date()
    footer = get_footer_text()
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Neon Cyber Report</title>
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
.section-title{{color:#00ffff;margin-bottom:10px;font-size:14px;letter-spacing:2px;}}
.footer{{text-align:center;color:rgba(255,255,255,0.2);font-size:11px;padding:15px;}}
</style>
</head>
<body>
<div class="container">
    <div class="neon-box"><h1>◈ NEON CYBER</h1><div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div></div>
    <div class="neon-box">
        <div class="neon-grid">
            <div class="neon-stat"><div class="neon-number">{data.get('total_references', 0)}</div><div class="neon-label">Total</div></div>
            <div class="neon-stat"><div class="neon-number">{data.get('total_with_doi', 0)}</div><div class="neon-label">DOI</div></div>
            <div class="neon-stat"><div class="neon-number">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="neon-label">5Y</div></div>
            <div class="neon-stat"><div class="neon-number">{data.get('self_citations_count', 0)}</div><div class="neon-label">SELF</div></div>
            <div class="neon-stat"><div class="neon-number">{data.get('total_citations_sum', 0)}</div><div class="neon-label">CIT</div></div>
        </div>
    </div>
    <div class="neon-box">
        <div class="section-title">▶ AUTHORS</div>
        {''.join([f'<span class="neon-tag">{a.get("display_name", "Unknown")} [{a.get("mention_count", 0)}]</span>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:6]])}
    </div>
    <div class="neon-box">
        <div class="section-title">▶ JOURNALS</div>
        {''.join([f'<span class="neon-tag neon-tag-cyan">{j.get("journal", "Unknown")} {j.get("count", 0)}</span>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:5]])}
    </div>
    <div class="neon-box">
        <div class="section-title">▶ GEOGRAPHY</div>
        {''.join([f'<span class="neon-tag neon-tag-cyan">{c}: {count}</span>' for c, count in list(data.get('geography', {}).get('type1_unique_countries_per_reference', {}).items())[:4]])}
    </div>
    <div class="footer">✦ {date_str} • {footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 3: GLASS ENHANCED (Улучшенное стекло)
# ============================================================
def generate_style_glass_enhanced(data, lang='en', journal_name='', article_number=''):
    """Стиль 3: Glassmorphism Enhanced — улучшенный стеклянный эффект с градиентами"""
    date_str = get_date()
    footer = get_footer_text()
    
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
.section-title{{color:rgba(255,255,255,0.6);margin-bottom:12px;font-weight:600;}}
.footer{{text-align:center;color:rgba(255,255,255,0.2);font-size:11px;padding:15px;}}
</style>
</head>
<body>
<div class="container">
    <div class="glass"><h1>✦ Glass Enhanced</h1><div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div></div>
    <div class="glass">
        <div class="grid">
            <div class="stat"><div class="num">{data.get('total_references', 0)}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{data.get('total_with_doi', 0)}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{data.get('self_citations_count', 0)}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{data.get('total_citations_sum', 0)}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div class="glass">
        <div class="section-title">✦ Authors</div>
        {''.join([f'<span class="tag">{a.get("display_name", "Unknown")} ({a.get("mention_count", 0)})</span>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:6]])}
    </div>
    <div class="glass">
        <div class="section-title">✦ Journals</div>
        {''.join([f'<span class="tag tag-gold">{j.get("journal", "Unknown")} ({j.get("count", 0)})</span>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:5]])}
    </div>
    <div class="glass">
        <div class="section-title">✦ Geography</div>
        {''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(data.get('geography', {}).get('type1_unique_countries_per_reference', {}).items())[:5]])}
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 4: SMART GLOW (Умное свечение)
# ============================================================
def generate_style_smart_glow(data, lang='en', journal_name='', article_number=''):
    """Стиль 4: Smart Glow — умная аналитика с подсветкой"""
    date_str = get_date()
    footer = get_footer_text()
    
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
.section-title{{color:#c9d1d9;margin-bottom:12px;font-weight:600;}}
.footer{{text-align:center;color:#8b949e;font-size:11px;padding:15px;}}
</style>
</head>
<body>
<div class="container">
    <div class="glow-card"><h1>✦ Smart Glow</h1><div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div></div>
    <div class="glow-card">
        <div class="grid">
            <div class="stat"><div class="num">{data.get('total_references', 0)}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{data.get('total_with_doi', 0)}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{data.get('self_citations_count', 0)}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{data.get('total_citations_sum', 0)}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div class="glow-card">
        <div class="section-title">👨‍🎓 Authors</div>
        {''.join([f'<span class="tag">{a.get("display_name", "Unknown")} ({a.get("mention_count", 0)})</span>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:6]])}
    </div>
    <div class="glow-card">
        <div class="section-title">📖 Journals</div>
        {''.join([f'<span class="tag tag-blue">{j.get("journal", "Unknown")} ({j.get("count", 0)})</span>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:5]])}
    </div>
    <div class="glow-card">
        <div class="section-title">🌍 Geography</div>
        {''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(data.get('geography', {}).get('type1_unique_countries_per_reference', {}).items())[:5]])}
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 5: AURORA (Северное сияние)
# ============================================================
def generate_style_aurora(data, lang='en', journal_name='', article_number=''):
    """Стиль 5: Aurora — северное сияние с плавными градиентами"""
    date_str = get_date()
    footer = get_footer_text()
    
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
.section-title{{color:rgba(255,255,255,0.6);margin-bottom:12px;position:relative;z-index:1;}}
.footer{{text-align:center;color:rgba(255,255,255,0.2);font-size:11px;padding:15px;position:relative;z-index:1;}}
</style>
</head>
<body>
<div class="container">
    <div class="aurora-card"><h1>✦ Aurora</h1><div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div></div>
    <div class="aurora-card">
        <div class="grid">
            <div class="stat"><div class="num">{data.get('total_references', 0)}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{data.get('total_with_doi', 0)}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{data.get('self_citations_count', 0)}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{data.get('total_citations_sum', 0)}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div class="aurora-card">
        <div class="section-title">👨‍🎓 Authors</div>
        {''.join([f'<span class="tag">{a.get("display_name", "Unknown")} ({a.get("mention_count", 0)})</span>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:6]])}
    </div>
    <div class="aurora-card">
        <div class="section-title">📖 Journals</div>
        {''.join([f'<span class="tag">{j.get("journal", "Unknown")} ({j.get("count", 0)})</span>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:5]])}
    </div>
    <div class="aurora-card">
        <div class="section-title">🌍 Geography</div>
        {''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(data.get('geography', {}).get('type1_unique_countries_per_reference', {}).items())[:5]])}
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 6: TIMELINE WAVE (Волна времени)
# ============================================================
def generate_style_timeline_wave(data, lang='en', journal_name='', article_number=''):
    """Стиль 6: Timeline Wave — волновая визуализация годов"""
    date_str = get_date()
    footer = get_footer_text()
    
    yearly_counts = data.get('yearly_stats', {}).get('yearly_counts', {})
    max_val = max(yearly_counts.values()) if yearly_counts else 1
    
    bars = ''.join([f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;"><div style="height:{count/max_val*150}px;width:30px;background:linear-gradient(180deg,#667eea,#764ba2);border-radius:4px 4px 0 0;transition:height 0.5s;box-shadow:0 0 20px rgba(102,126,234,0.3);"></div><div style="font-size:11px;color:#666;margin-top:5px;">{year}</div><div style="font-size:10px;color:#999;">{count}</div></div>' for year,count in sorted(yearly_counts.items())])
    
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
.section-title{{font-weight:600;margin-bottom:8px;}}
.footer{{text-align:center;color:#ccc;font-size:11px;padding:15px;border-top:1px solid #eee;margin-top:20px;}}
</style>
</head>
<body>
<div class="container">
    <h1>📊 Timeline Wave</h1>
    <div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div>
    <div class="grid">
        <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_year', 0)}</div><div class="lbl">Last Year</div></div>
        <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_3_years', 0)}</div><div class="lbl">3 Years</div></div>
        <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="lbl">5 Years</div></div>
        <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_10_years', 0)}</div><div class="lbl">10 Years</div></div>
        <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('unknown_year', 0)}</div><div class="lbl">Unknown</div></div>
    </div>
    <div class="timeline">{bars}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px;">
        <div style="background:#f8f9fa;border-radius:12px;padding:15px;">
            <div class="section-title">👨‍🎓 Authors</div>
            {''.join([f'<div style="font-size:13px;padding:3px 0;border-bottom:1px solid #eee;">{a.get("display_name", "Unknown")} ({a.get("mention_count", 0)})</div>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:5]])}
        </div>
        <div style="background:#f8f9fa;border-radius:12px;padding:15px;">
            <div class="section-title">📖 Journals</div>
            {''.join([f'<div style="font-size:13px;padding:3px 0;border-bottom:1px solid #eee;">{j.get("journal", "Unknown")} ({j.get("count", 0)})</div>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:5]])}
        </div>
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 7: MASONRY (Плиточный)
# ============================================================
def generate_style_masonry(data, lang='en', journal_name='', article_number=''):
    """Стиль 7: Masonry — плиточная раскладка как Pinterest"""
    date_str = get_date()
    footer = get_footer_text()
    
    author_cards = ''.join([f'<div style="background:#fff;border-radius:12px;padding:15px;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:4px solid #667eea;margin-bottom:10px;"><div style="font-weight:600;">{a.get("display_name", "Unknown")}</div><div style="font-size:12px;color:#666;">{a.get("mention_count", 0)} citations</div></div>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:6]])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Masonry</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#f5f7fa;padding:30px;font-family:'Segoe UI',sans-serif;}}
.container{{max-width:1200px;margin:0 auto;}}
h1{{font-size:28px;font-weight:700;color:#1a1a2e;}}
.subtitle{{color:#999;font-size:14px;}}
.masonry-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin:20px 0;}}
.masonry-item{{background:#fff;border-radius:16px;padding:20px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);transition:transform 0.2s;}}
.masonry-item:hover{{transform:translateY(-4px);box-shadow:0 4px 16px rgba(0,0,0,0.08);}}
.num{{font-size:28px;font-weight:700;color:#667eea;}}
.lbl{{font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px;margin-top:4px;}}
.row{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;}}
.tag{{display:inline-block;padding:4px 14px;background:#f0f2f5;border-radius:16px;font-size:12px;color:#333;}}
.section-title{{font-weight:600;margin-bottom:12px;}}
.footer{{text-align:center;color:#ccc;font-size:11px;padding:15px;margin-top:20px;border-top:1px solid #eee;}}
</style>
</head>
<body>
<div class="container">
    <h1>✦ Masonry Dashboard</h1>
    <div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div>
    <div class="masonry-grid">
        <div class="masonry-item"><div class="num">{data.get('total_references', 0)}</div><div class="lbl">Total</div></div>
        <div class="masonry-item"><div class="num">{data.get('total_with_doi', 0)}</div><div class="lbl">DOI</div></div>
        <div class="masonry-item"><div class="num">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="lbl">5 Years</div></div>
        <div class="masonry-item"><div class="num">{data.get('self_citations_count', 0)}</div><div class="lbl">Self-Cit</div></div>
        <div class="masonry-item"><div class="num">{data.get('total_citations_sum', 0)}</div><div class="lbl">Citations</div></div>
        <div class="masonry-item"><div class="num">{data.get('avg_citations', 0):.1f}</div><div class="lbl">Avg Cit</div></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div style="background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div class="section-title">👨‍🎓 Authors</div>
            {author_cards}
        </div>
        <div style="background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div class="section-title">📖 Journals</div>
            {''.join([f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0f0f0;font-size:13px;"><span>{j.get("journal", "Unknown")}</span><span style="font-weight:600;color:#667eea;">{j.get("count", 0)}</span></div>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:6]])}
        </div>
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 8: HOLOGRAPHIC (Голографический)
# ============================================================
def generate_style_holographic(data, lang='en', journal_name='', article_number=''):
    """Стиль 8: Holographic — голографический эффект с переливами"""
    date_str = get_date()
    footer = get_footer_text()
    
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
.section-title{{color:rgba(255,255,255,0.6);margin-bottom:12px;}}
.footer{{text-align:center;color:rgba(255,255,255,0.2);font-size:11px;padding:15px;}}
</style>
</head>
<body>
<div class="container">
    <div class="holo"><h1>✦ HOLOGRAPHIC</h1><div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div></div>
    <div class="holo">
        <div class="grid">
            <div class="stat"><div class="num">{data.get('total_references', 0)}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{data.get('total_with_doi', 0)}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{data.get('self_citations_count', 0)}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{data.get('total_citations_sum', 0)}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div class="holo">
        <div class="section-title">👨‍🎓 Authors</div>
        {''.join([f'<span class="tag">{a.get("display_name", "Unknown")} ({a.get("mention_count", 0)})</span>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:6]])}
    </div>
    <div class="holo">
        <div class="section-title">📖 Journals</div>
        {''.join([f'<span class="tag">{j.get("journal", "Unknown")} ({j.get("count", 0)})</span>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:5]])}
    </div>
    <div class="holo">
        <div class="section-title">🌍 Geography</div>
        {''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(data.get('geography', {}).get('type1_unique_countries_per_reference', {}).items())[:5]])}
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 9: GEO BUBBLES (Гео-пузырьки)
# ============================================================
def generate_style_geo_bubbles(data, lang='en', journal_name='', article_number=''):
    """Стиль 9: Geo Bubbles — географические пузырьки"""
    date_str = get_date()
    footer = get_footer_text()
    
    countries = list(data.get('geography', {}).get('type1_unique_countries_per_reference', {}).items())
    max_val = max([count for _, count in countries]) if countries else 1
    
    bubbles = ''.join([f'<div style="display:flex;align-items:center;margin:6px 0;"><div style="width:100px;font-size:14px;">{c}</div><div style="flex:1;height:24px;background:#e9ecef;border-radius:12px;overflow:hidden;"><div style="height:100%;width:{count/max_val*100}%;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:12px;transition:width 0.5s;"></div></div><div style="width:40px;text-align:right;font-size:14px;font-weight:600;color:#667eea;">{count}</div></div>' for c,count in countries])
    
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
.footer{{text-align:center;color:#ccc;font-size:11px;padding:15px;border-top:1px solid #eee;margin-top:20px;}}
</style>
</head>
<body>
<div class="container">
    <h1>🌍 Geo Bubbles</h1>
    <div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div>
    <div class="grid">
        <div class="stat"><div class="num">{data.get('total_references', 0)}</div><div class="lbl">Total</div></div>
        <div class="stat"><div class="num">{data.get('geography', {}).get('single_country_count', 0)}</div><div class="lbl">Single</div></div>
        <div class="stat"><div class="num">{data.get('geography', {}).get('international_count', 0)}</div><div class="lbl">International</div></div>
        <div class="stat"><div class="num">{data.get('geography', {}).get('total_references_with_country', 0)}</div><div class="lbl">With Country</div></div>
    </div>
    <div class="section">
        <div class="section-title">🌐 Countries Distribution</div>
        {bubbles}
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div class="section">
            <div class="section-title">👨‍🎓 Authors</div>
            {''.join([f'<div style="font-size:13px;padding:4px 0;border-bottom:1px solid #eee;">{a.get("display_name", "Unknown")} ({a.get("mention_count", 0)})</div>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:5]])}
        </div>
        <div class="section">
            <div class="section-title">🤝 Collaborations</div>
            {''.join([f'<div style="font-size:13px;padding:4px 0;border-bottom:1px solid #eee;">{c.get("country1", "Unknown")} + {c.get("country2", "Unknown")} ({c.get("count", 0)})</div>' for c in data.get('geography', {}).get('collaboration_matrix', [])[:4]])}
        </div>
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# СТИЛЬ 10: PARTICLES (Космический)
# ============================================================
def generate_style_particles(data, lang='en', journal_name='', article_number=''):
    """Стиль 10: Particles — частицы и космическая тема"""
    date_str = get_date()
    footer = get_footer_text()
    
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
.section-title{{color:rgba(255,255,255,0.4);margin-bottom:12px;letter-spacing:2px;}}
.footer{{text-align:center;color:rgba(255,255,255,0.1);font-size:11px;padding:15px;letter-spacing:2px;}}
</style>
</head>
<body>
<div class="container">
    <div class="particle-card"><h1>✦ PARTICLES</h1><div class="subtitle">{html.escape(journal_name) if journal_name else 'Chimica Techno Acta'} • {date_str}</div></div>
    <div class="particle-card">
        <div class="grid">
            <div class="stat"><div class="num">{data.get('total_references', 0)}</div><div class="lbl">Total</div></div>
            <div class="stat"><div class="num">{data.get('total_with_doi', 0)}</div><div class="lbl">DOI</div></div>
            <div class="stat"><div class="num">{data.get('yearly_stats', {}).get('last_5_years', 0)}</div><div class="lbl">5 Years</div></div>
            <div class="stat"><div class="num">{data.get('self_citations_count', 0)}</div><div class="lbl">Self-Cit</div></div>
            <div class="stat"><div class="num">{data.get('total_citations_sum', 0)}</div><div class="lbl">Citations</div></div>
        </div>
    </div>
    <div class="particle-card">
        <div class="section-title">◈ AUTHORS</div>
        {''.join([f'<span class="tag">{a.get("display_name", "Unknown")} ({a.get("mention_count", 0)})</span>' for a in data.get('author_frequency_all', {}).get('all_authors', [])[:6]])}
    </div>
    <div class="particle-card">
        <div class="section-title">◈ JOURNALS</div>
        {''.join([f'<span class="tag">{j.get("journal", "Unknown")} ({j.get("count", 0)})</span>' for j in data.get('journal_frequency_all', {}).get('all_journals', [])[:5]])}
    </div>
    <div class="particle-card">
        <div class="section-title">◈ GEOGRAPHY</div>
        {''.join([f'<span class="tag">{c}: {count}</span>' for c, count in list(data.get('geography', {}).get('type1_unique_countries_per_reference', {}).items())[:5]])}
    </div>
    <div class="footer">{footer}</div>
</div>
</body></html>'''

# ============================================================
# РЕГИСТРАЦИЯ ВСЕХ СТИЛЕЙ ДЛЯ ИСПОЛЬЗОВАНИЯ В APP.PY
# ============================================================

STYLE_GENERATORS = {
    "classic": {
        "name": "Классический (исходный)",
        "generator": None,  # Будет использоваться generate_html_report_advanced из app.py
        "show_color_theme": True
    },
    "glassmorphism": {
        "name": "Glassmorphism (Стекло)",
        "generator": generate_style_glassmorphism,
        "show_color_theme": False
    },
    "neon_cyber": {
        "name": "Neon Cyber (Неон)",
        "generator": generate_style_neon_cyber,
        "show_color_theme": False
    },
    "glass_enhanced": {
        "name": "Glass Enhanced (Улучшенное стекло)",
        "generator": generate_style_glass_enhanced,
        "show_color_theme": False
    },
    "smart_glow": {
        "name": "Smart Glow (Умное свечение)",
        "generator": generate_style_smart_glow,
        "show_color_theme": False
    },
    "aurora": {
        "name": "Aurora (Северное сияние)",
        "generator": generate_style_aurora,
        "show_color_theme": False
    },
    "timeline_wave": {
        "name": "Timeline Wave (Волна времени)",
        "generator": generate_style_timeline_wave,
        "show_color_theme": False
    },
    "masonry": {
        "name": "Masonry (Плиточный)",
        "generator": generate_style_masonry,
        "show_color_theme": False
    },
    "holographic": {
        "name": "Holographic (Голографический)",
        "generator": generate_style_holographic,
        "show_color_theme": False
    },
    "geo_bubbles": {
        "name": "Geo Bubbles (Гео-пузырьки)",
        "generator": generate_style_geo_bubbles,
        "show_color_theme": False
    },
    "particles": {
        "name": "Particles (Космический)",
        "generator": generate_style_particles,
        "show_color_theme": False
    }
}
