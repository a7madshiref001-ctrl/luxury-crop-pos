/* DARJ — Barista screen (KDS): used by kds.html and the "الباريستا" tab inside the app */
(function () {
  'use strict';
  const D = window.DARJ;
  const K = (window.DARJ_KDS = {});
  const T = {
    ar: { new: 'جديد', make: 'قيد التحضير', ready: 'جاهز للتسليم', start: 'ابدأ التحضير', done: 'جاهز', picked: 'تم التسليم', empty: 'لا توجد طلبات', allday: 'المطلوب الآن' },
    en: { new: 'New', make: 'Making', ready: 'Ready', start: 'Start', done: 'Ready', picked: 'Picked up', empty: 'Nothing here', allday: 'All-day' },
  };
  const isMaking = (o, now) => o.started || (o.sim && now - (o.tsAcc || o.ts) > 50000);
  const age = (o, now) => now - (o.status === 'ready' ? o.tsReady : (o.tsAcc || o.ts));

  function ticket(o, now, lang) {
    const t = T[lang];
    const col = o.status === 'ready' ? 'ready' : isMaking(o, now) ? 'make' : 'new';
    const a = age(o, now);
    const cls = col === 'ready' ? 'ready' : a > 7 * 60000 ? 'late' : a > 4 * 60000 ? 'warn' : '';
    const ch = D.CH[o.ch];
    const where = o.ch === 'table' ? (lang === 'en' ? `Table ${o.table}` : `طاولة ${o.table}`) : o.ch === 'pickup' ? (lang === 'en' ? 'Web pickup' : 'استلام من الموقع') : (lang === 'en' ? D.TYPES[o.type].en : D.TYPES[o.type].ar);
    const lines = o.lines.map((l, i) => {
      const p = D.prod(l.pid);
      if (!D.isDrink(p)) return '';
      const chips = D.modList(l).filter(({ o: op }) => op.k).map(({ o: op, g }) => `<span class="${g === 'size' ? 'soft' : ''}">${op.k}</span>`).join('');
      const done = (o.lineDone || []).includes(i);
      const v = (o.voided && o.voided[i]) || 0;
      const left = l.qty - v;
      if (v) return `<div class="kt__l done void"><b>${left || l.qty}</b><div><div class="nm">${D.esc(lang === 'en' ? p.en : p.ar)}</div><div class="mods"><span class="void">${lang === 'en' ? 'VOID' : 'ملغي'} −${v}</span></div></div></div>` + (left ? `<div class="kt__l" data-line="${i}" data-id="${o.id}"><b>${left}</b><div><div class="nm">${D.esc(lang === 'en' ? p.en : p.ar)}</div>${chips ? `<div class="mods">${chips}</div>` : ''}</div></div>` : '');
      return `<div class="kt__l${done ? ' done' : ''}" data-line="${i}" data-id="${o.id}"><b>${l.qty}</b><div><div class="nm">${D.esc(lang === 'en' ? p.en : p.ar)}</div><div class="ar">${D.esc(lang === 'en' ? p.ar : p.en)}</div>${chips ? `<div class="mods">${chips}</div>` : ''}${l.note ? `<div class="note">${D.esc(l.note)}</div>` : ''}</div></div>`;
    }).join('');
    const food = o.lines.filter((l) => !D.isDrink(D.prod(l.pid))).map((l) => `${l.qty}× ${D.esc(lang === 'en' ? D.prod(l.pid).en : D.prod(l.pid).ar)}`).join(' · ');
    const btn = col === 'new' ? t.start : col === 'make' ? t.done : t.picked;
    return `<article class="kt ${cls}${o._in ? ' in' : ''}" data-id="${o.id}" data-col="${col}">
      <div class="kt__h" data-adv="${o.id}"><div><b>#${o.no}</b><span class="kt__ch">${D.icon(ch.ic, 'sm')}${D.esc(where)}${o.name ? ' · ' + D.esc(o.name) : ''}</span></div><span class="kt__time" data-t="${o.id}">${D.mmss(a)}</span></div>
      <div class="kt__lines">${lines}${food ? `<div class="kt__l"><b></b><div class="ar">${food}</div></div>` : ''}</div>
      <div class="kt__f"><button class="btn ${col === 'make' ? 'btn--go' : col === 'ready' ? 'btn--ghost' : 'btn--ink'} btn--sm" data-adv="${o.id}">${btn}</button></div>
    </article>`;
  }

  K.mount = (el, opt) => {
    opt = opt || {};
    let lang = opt.lang || 'en';
    const seen = new Set();
    let first = true;
    function draw() {
      const S = D.state();
      const now = Date.now();
      const t = T[lang];
      const act = S.orders.filter((o) => (o.status === 'prep' || o.status === 'ready') && o.lines.some((l) => D.isDrink(D.prod(l.pid))));
      const cols = { new: [], make: [], ready: [] };
      act.forEach((o) => { cols[o.status === 'ready' ? 'ready' : isMaking(o, now) ? 'make' : 'new'].push(o); });
      cols.new.sort((a, b) => a.ts - b.ts); cols.make.sort((a, b) => a.ts - b.ts); cols.ready.sort((a, b) => b.tsReady - a.tsReady);
      // صوت لما يوصل طلب جديد
      let fresh = false;
      act.forEach((o) => { o._in = false; if (!seen.has(o.id)) { seen.add(o.id); if (!first) { fresh = true; o._in = true; } } });
      if (fresh && opt.sound !== false) D.sound('new');
      first = false;
      const allday = {};
      [...cols.new, ...cols.make].forEach((o) => o.lines.forEach((l, i) => { const p = D.prod(l.pid); const n = l.qty - ((o.voided && o.voided[i]) || 0); if (D.isDrink(p) && n > 0) allday[p.id] = (allday[p.id] || 0) + n; }));
      const ad = Object.entries(allday).sort((a, b) => b[1] - a[1]).map(([id, n]) => `<span><b>${n}</b> ${D.esc(lang === 'en' ? D.prod(id).en : D.prod(id).ar)}</span>`).join('');
      const col = (k, title) => `<section class="kds__col"><div class="kds__h"><b>${title}</b><span>${cols[k].length}</span></div>${cols[k].map((o) => ticket(o, now, lang)).join('') || `<div class="empty">${D.icon('cup')}<span>${t.empty}</span></div>`}</section>`;
      el.innerHTML = `${ad ? `<div class="allday"><span class="label" style="border:0;background:none;padding:0">${t.allday}</span>${ad}</div>` : ''}<div class="kds">${col('new', t.new)}${col('make', t.make)}${col('ready', t.ready)}</div>`;
    }
    el.addEventListener('click', (e) => {
      const ln = e.target.closest('[data-line]');
      if (ln && !e.target.closest('[data-adv]')) {
        const i = +ln.dataset.line;
        D.mutate((s) => { const o = s.orders.find((x) => x.id === ln.dataset.id); if (!o) return; o.lineDone = o.lineDone || []; o.lineDone = o.lineDone.includes(i) ? o.lineDone.filter((x) => x !== i) : [...o.lineDone, i]; }, 'kds');
        return;
      }
      const b = e.target.closest('[data-adv]');
      if (!b) return;
      const id = b.dataset.adv;
      const card = el.querySelector(`.kt[data-id="${id}"]`);
      const colName = card && card.dataset.col;
      if (colName === 'new') D.mutate((s) => { const o = s.orders.find((x) => x.id === id); if (o) o.started = Date.now(); }, 'kds');
      else if (colName === 'make') { D.setStatus(id, 'ready'); D.sound('ready'); }
      else if (colName === 'ready') D.setStatus(id, 'done');
    });
    const off = D.on((why) => { if (why !== 'cart') draw(); });
    const timer = setInterval(() => {
      const now = Date.now(); const S = D.state();
      el.querySelectorAll('[data-t]').forEach((n) => { const o = S.orders.find((x) => x.id === n.dataset.t); if (o) n.textContent = D.mmss(age(o, now)); });
    }, 1000);
    const slow = setInterval(draw, 15000);
    draw();
    return { setLang(l) { lang = l; draw(); }, destroy() { off(); clearInterval(timer); clearInterval(slow); } };
  };
})();
