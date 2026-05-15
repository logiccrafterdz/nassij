import re

html_path = "web/static/index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

replacements = [
    (
        r'<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="square" stroke-linejoin="miter"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>',
        r'<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="miter"><rect x="5" y="5" width="14" height="14" transform="rotate(45 12 12)" /><rect x="5" y="5" width="14" height="14" /><circle cx="12" cy="12" r="2" fill="currentColor"/></svg>'
    ),
    (
        r'<svg class="w-16 h-16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="square" stroke-linejoin="miter"><path d="M12 2v14M7 11l5 5 5-5M4 20h16"/></svg>',
        r'<svg class="w-20 h-20 drop-shadow-[0_0_15px_rgba(212,175,55,0.2)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="0.8" stroke-linejoin="miter"><path d="M12 2L22 12L12 22L2 12Z" /><path d="M12 6L18 12L12 18L6 12Z" opacity="0.6"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/><path d="M12 2v20 M2 12h20" stroke-dasharray="1 3" opacity="0.4"/></svg>'
    ),
    (
        r'<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="square" stroke-linejoin="miter"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>',
        r'<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 12H4m0 0l6-6m-6 6l6 6" /><path d="M16 6s-4 6 4 12" stroke-width="0.8" opacity="0.4"/></svg>'
    ),
    (
        r'<svg class="w-8 h-8 text-copper" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="square" stroke-linejoin="miter"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 12 12 17 22 12"/><polyline points="2 17 12 22 22 17"/></svg>',
        r'<svg class="w-10 h-10 text-copper group-hover:scale-110 transition-transform duration-500 drop-shadow-[0_0_10px_rgba(212,175,55,0.3)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><circle cx="12" cy="12" r="10" opacity="0.2"/><rect x="7" y="7" width="10" height="10" transform="rotate(45 12 12)" /><rect x="7" y="7" width="10" height="10" /><circle cx="12" cy="12" r="2" fill="currentColor"/></svg>'
    ),
    (
        r'<svg class="w-8 h-8 text-white/30 transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="square" stroke-linejoin="miter"><rect x="3" y="3" width="18" height="18"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/></svg>',
        r'<svg class="w-10 h-10 text-white/30 transition-all duration-500 group-hover:text-teal group-hover:scale-110 group-hover:drop-shadow-[0_0_10px_rgba(0,242,254,0.3)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M12 2L22 7V17L12 22L2 17V7L12 2Z" /><path d="M12 2v20 M2 7l10 5l10-5 M2 17l10-5l10 5" opacity="0.3"/><circle cx="12" cy="12" r="2.5" fill="currentColor" opacity="0.8"/></svg>'
    ),
    (
        r'<svg class="w-8 h-8 text-white/30 transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="square" stroke-linejoin="miter"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
        r'<svg class="w-10 h-10 text-white/30 transition-all duration-500 group-hover:text-copper group-hover:scale-110 group-hover:drop-shadow-[0_0_10px_rgba(212,175,55,0.3)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M12 2 C18 2, 22 6, 22 12 C22 18, 18 22, 12 22 C6 22, 2 18, 2 12 C2 6, 6 2, 12 2 Z" stroke-dasharray="3 3" opacity="0.5"/><path d="M12 6 C15.3 6, 18 8.7, 18 12 C18 15.3, 15.3 18, 12 18 C8.7 18, 6 15.3, 6 12 C6 8.7, 8.7 6, 12 6 Z" /><polygon points="12 9, 14 14, 10 14" fill="currentColor"/></svg>'
    )
]

for old, new in replacements:
    if old in html:
        html = html.replace(old, new)
        print(f"Replaced {old[:30]}...")
    else:
        print(f"Could not find {old[:30]}...")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Done!")
