const DAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'];
const DAYS_SHORT = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
const MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
const ROOT = document.body.dataset.root || '';
const DEPT_COLOR = { fussball: 'var(--pitch)', turnen: 'var(--coral)', fitness: 'var(--berry)' };

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const icon = (name) => `<svg class="i" aria-hidden="true"><use href="${ROOT}assets/img/icons.svg#${name}"/></svg>`;
const art = (name) => `<img class="art" src="${ROOT}assets/img/iconsflat/${name}.svg" alt="" width="96" height="96" loading="lazy">`;
const mins = (t) => { const [h, m] = t.split(':').map(Number); return h * 60 + m; };
const weekday = (d) => (d.getDay() + 6) % 7;
const inSeason = (g, d) => !g.months || g.months.includes(d.getMonth() + 1);
const placeName = (g) => (g.place ? PLACES[g.place].name : 'Ort nach Absprache');
const mapUrl = (key) => 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(PLACES[key].q);

function sessionsOn(day, date, dept) {
  const out = [];
  for (const g of GROUPS) {
    if (dept && g.dept !== dept) continue;
    if (date && !inSeason(g, date)) continue;
    for (const [d, start, end] of g.slots) if (d === day) out.push({ g, start, end });
  }
  return out.sort((a, b) => mins(a.start) - mins(b.start) || a.g.title.localeCompare(b.g.title));
}

/* ---------- Heute beim SVO ---------- */
function renderToday(el) {
  const now = new Date();
  const nowMin = now.getHours() * 60 + now.getMinutes();
  let date = now;
  let list = sessionsOn(weekday(now), now);
  let label = 'Heute';
  const pending = list.filter((s) => mins(s.end) > nowMin);

  // Heute nichts mehr los: nächsten Trainingstag zeigen
  if (!pending.length) {
    for (let i = 1; i <= 7; i++) {
      const d = new Date(now); d.setDate(now.getDate() + i);
      const l = sessionsOn(weekday(d), d);
      if (l.length) { date = d; list = l; label = i === 1 ? 'Morgen' : DAYS[weekday(d)]; break; }
    }
  }
  const isToday = date === now;
  const MAX = 6;
  if (isToday && list.length > MAX) {
    const done = list.filter((s) => mins(s.end) <= nowMin);
    list = done.slice(Math.max(0, done.length - Math.max(0, MAX - pending.length))).concat(pending);
  }
  const extra = Math.max(0, list.length - MAX);
  list = list.slice(0, MAX);

  const rows = list.map(({ g, start, end }) => {
    const live = isToday && mins(start) <= nowMin && nowMin < mins(end);
    const done = isToday && mins(end) <= nowMin;
    return `<li class="board__row${live ? ' is-live' : ''}${done ? ' is-done' : ''}" style="--c:${DEPT_COLOR[g.dept]}">
      <span class="board__time">${start}</span>
      <span class="board__what"><strong>${esc(g.title)}</strong><small>${esc(g.who)}</small></span>
      <span class="board__where">${live ? '<em class="live">Läuft</em>' : esc(placeName(g))}</span>
    </li>`;
  }).join('');

  el.innerHTML = `
    <header class="board__head">
      <span class="board__label"><i class="dot" aria-hidden="true"></i>${label} beim SVO</span>
      <span class="board__date">${DAYS[weekday(date)]}, ${date.getDate()}. ${MONTHS[date.getMonth()]}</span>
    </header>
    <ol class="board__list">${rows}</ol>
    <a class="board__more" href="#woche">${extra ? `+${extra} weitere · ` : ''}Ganze Woche ansehen ${icon('arrow')}</a>`;
}

/* ---------- Wochenplan ---------- */
function renderWeek(el, fixedDept, filter) {
  const today = new Date();
  const todayIdx = weekday(today);
  let dept = fixedDept || '';

  const draw = () => {
    let shown = 0;
    const cols = DAYS.map((name, i) => {
      let list = sessionsOn(i, today, dept);
      if (filter) list = list.filter((s) => filter(s.g));
      if (fixedDept && !list.length) return '';
      shown++;
      const items = list.map(({ g, start, end }) => `
        <li class="slot slot--${g.dept}">
          <span class="slot__time">${start}–${end}</span>
          <strong class="slot__title">${esc(g.title)}</strong>
          <span class="slot__meta">${esc(g.who)}</span>
          <span class="slot__meta">${esc(placeName(g))}</span>
        </li>`).join('');
      return `<section class="day${i === todayIdx ? ' is-today' : ''}${list.length ? '' : ' is-empty'}" aria-label="${name}">
        <h3 class="day__name"><span class="day__short">${DAYS_SHORT[i]}</span><span class="day__long">${name}</span>${i === todayIdx ? '<em>Heute</em>' : ''}</h3>
        <ul>${items || '<li class="day__none">Kein Training</li>'}</ul>
      </section>`;
    }).join('');
    const grid = el.querySelector('.week__grid');
    grid.innerHTML = cols;
    if (fixedDept) grid.style.setProperty('--days', shown);
  };

  el.innerHTML = (fixedDept ? '' : `
    <div class="chips" role="group" aria-label="Abteilung filtern">
      <button type="button" class="chip" aria-pressed="true" data-dept="">Alle</button>
      ${Object.entries(DEPTS).map(([k, d]) => `<button type="button" class="chip" aria-pressed="false" data-dept="${k}" style="--c:${DEPT_COLOR[k]}"><i></i>${d.name}</button>`).join('')}
    </div>`) + '<div class="week__grid"></div>';

  el.querySelectorAll('.chip').forEach((b) => b.addEventListener('click', () => {
    dept = b.dataset.dept;
    el.querySelectorAll('.chip').forEach((c) => c.setAttribute('aria-pressed', String(c === b)));
    draw();
  }));
  draw();
}

const timesList = (g) => `<ul class="times">${g.slots.map(([d, s, e]) => `<li><b>${DAYS_SHORT[d]}</b> ${s}–${e}</li>`).join('')}</ul>`;
const placeLine = (g) => `<p class="meta-line">${icon('pin')}<span>${g.place ? `<a href="${mapUrl(g.place)}" target="_blank" rel="noopener">${esc(PLACES[g.place].name)}</a>` : 'Ort nach Absprache'}${g.note ? ` · ${esc(g.note)}` : ''}</span></p>`;
const seasonTag = (g) => (g.months ? `<span class="season">Nur ${MONTHS[g.months[0] - 1]} bis ${MONTHS[g.months[g.months.length - 1] - 1]}</span>` : '');

/* ---------- Fußball-Teams: 3D-Trikot mit Mannschafts-Kürzel ---------- */
const jersey = (code) => `<span class="jersey">${art('jersey')}<b class="jersey__code">${esc(code)}</b></span>`;
function renderTeams(el) {
  el.innerHTML = GROUPS.filter((g) => g.dept === 'fussball').map((g) => `
    <article class="team${/^\d$/.test(g.code) ? ' team--senior' : ''}">
      ${jersey(g.code)}
      <div>
        <h3>${esc(g.title)}</h3>
        <p class="team__who">${esc(g.who)}</p>
        ${timesList(g)}
        ${placeLine(g)}
        <p class="coaches"><span>Trainer</span>${esc(g.coaches)}</p>
      </div>
    </article>`).join('');
}

/* ---------- Gruppenkarten mit Icon oder Foto ---------- */
function renderGroups(el, dept, age) {
  el.innerHTML = GROUPS.filter((g) => g.dept === dept && (!age || g.age === age)).map((g) => `
    <article class="group">
      ${g.img ? `<img class="group__img" src="${ROOT}assets/img/${g.img}" alt="" loading="lazy">` : ''}
      <div class="group__body">
        ${g.img ? '' : `<span class="group__icon">${art(g.icon || 'trophy')}</span>`}
        <h3>${esc(g.title)}</h3>
        <p class="group__who">${esc(g.who)}</p>
        ${g.desc ? `<p class="group__desc">${esc(g.desc)}</p>` : ''}
        ${timesList(g)}
        ${placeLine(g)}
        ${seasonTag(g)}
      </div>
    </article>`).join('');
}

function fillCounts() {
  document.querySelectorAll('[data-count]').forEach((el) => {
    el.textContent = GROUPS.filter((g) => g.dept === el.dataset.count).length;
  });
}

/* ---------- Navigation ---------- */
function initNav() {
  const btn = document.querySelector('.nav-toggle');
  const nav = document.getElementById('site-nav');
  if (!btn || !nav) return;
  const set = (open) => {
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
    document.body.classList.toggle('nav-open', open);
  };
  btn.addEventListener('click', () => set(btn.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', (e) => { if (e.target.closest('a')) set(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
}

/* ---------- Slider mit Vereinsstreifen-Übergang ---------- */
function initSlider(root) {
  const slides = [...root.querySelectorAll('.slide')];
  const dotsEl = root.querySelector('.slider__dots');
  const bars = root.querySelector('.slider__bars');
  const toggle = root.querySelector('[data-slider="toggle"]');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const DUR = 7000;
  let idx = 0; let timer = null; let paused = reduce; let busy = false;

  dotsEl.innerHTML = slides.map((s, i) => `<button type="button" aria-label="Bild ${i + 1}: ${esc(s.dataset.title || '')}"></button>`).join('');
  const dots = [...dotsEl.children];
  root.style.setProperty('--dur', DUR + 'ms');

  const mark = () => {
    slides.forEach((s, i) => { s.classList.toggle('is-active', i === idx); s.setAttribute('aria-hidden', String(i !== idx)); s.inert = i !== idx; });
    dots.forEach((d, i) => { d.removeAttribute('aria-current'); if (i === idx) { void d.offsetWidth; d.setAttribute('aria-current', 'true'); } });
  };
  const schedule = () => { clearTimeout(timer); if (!paused) timer = setTimeout(() => go(idx + 1), DUR); };
  const go = (n) => {
    if (busy) return;
    const next = (n + slides.length) % slides.length;
    if (next === idx) return;
    if (reduce) { idx = next; mark(); return; }
    busy = true;
    bars.style.setProperty('--c', slides[next].style.getPropertyValue('--c') || 'var(--crest)');
    root.classList.remove('is-wiping'); void root.offsetWidth; root.classList.add('is-wiping');
    setTimeout(() => { idx = next; mark(); }, 430);
    setTimeout(() => { root.classList.remove('is-wiping'); busy = false; schedule(); }, 1250);
  };
  const setPaused = (p) => {
    paused = p; root.classList.toggle('is-paused', p);
    if (toggle) { toggle.setAttribute('aria-label', p ? 'Automatisch abspielen' : 'Anhalten'); toggle.innerHTML = icon(p ? 'play' : 'pause'); }
    p ? clearTimeout(timer) : schedule();
  };

  root.querySelector('[data-slider="prev"]').addEventListener('click', () => go(idx - 1));
  root.querySelector('[data-slider="next"]').addEventListener('click', () => go(idx + 1));
  dots.forEach((d, i) => d.addEventListener('click', () => go(i)));
  toggle?.addEventListener('click', () => setPaused(!paused));
  root.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') go(idx - 1); if (e.key === 'ArrowRight') go(idx + 1); });
  let x0 = null;
  root.addEventListener('pointerdown', (e) => { x0 = e.clientX; });
  root.addEventListener('pointerup', (e) => { if (x0 !== null && Math.abs(e.clientX - x0) > 50) go(idx + (e.clientX < x0 ? 1 : -1)); x0 = null; });
  document.addEventListener('visibilitychange', () => (document.hidden ? clearTimeout(timer) : schedule()));

  mark(); setPaused(paused);
}

/* ---------- Beitragsfilter ---------- */
function initNewsFilter(el) {
  const cards = [...document.querySelectorAll('[data-news-list] .news-card')];
  const apply = (cat) => {
    el.querySelectorAll('.chip').forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.cat === cat)));
    cards.forEach((c) => { c.hidden = !!cat && !c.dataset.cats.split(' ').includes(cat); });
  };
  el.addEventListener('click', (e) => {
    const b = e.target.closest('.chip'); if (!b) return;
    apply(b.dataset.cat);
    history.replaceState(null, '', b.dataset.cat ? '#' + b.dataset.cat : location.pathname);
  });
  apply(location.hash.slice(1));
}

/* ---------- Kontaktformular: E-Mail vorbereiten ---------- */
function initContactForm(form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const d = new FormData(form);
    const body = `${d.get('message')}\n\n—\n${d.get('name')}\n${d.get('email')}${d.get('phone') ? '\n' + d.get('phone') : ''}`;
    location.href = `mailto:${d.get('to')}?subject=${encodeURIComponent(d.get('subject') || 'Anfrage über die Website')}&body=${encodeURIComponent(body)}`;
    form.querySelector('[data-sent]').hidden = false;
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initNav();
  fillCounts();
  const board = document.querySelector('[data-today]');
  if (board) renderToday(board);
  document.querySelectorAll('[data-week]').forEach((el) => renderWeek(el, el.dataset.week || '',
    el.dataset.age ? (g) => g.age === el.dataset.age : null));
  document.querySelectorAll('[data-teams]').forEach(renderTeams);
  document.querySelectorAll('[data-groups]').forEach((el) => renderGroups(el, el.dataset.groups, el.dataset.age));
  document.querySelectorAll('.slider').forEach(initSlider);
  document.querySelectorAll('[data-news-filter]').forEach(initNewsFilter);
  document.querySelectorAll('[data-contact-form]').forEach(initContactForm);
  // Logo-Band für die Endlosschleife verdoppeln (Kopie ohne Alt-Text)
  document.querySelectorAll('.sponsor-band__track').forEach((t) => {
    [...t.children].forEach((n) => { const c = n.cloneNode(); c.alt = ''; t.appendChild(c); });
  });
});
