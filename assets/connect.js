/* محصول فاخر — الربط مع المنيو الأونلاين (Supabase بتاع luxurycrop.site)
   متوقف لحد ما DARJ_CONFIG.connect.enabled = true. ساعتها:
   1) المدير يدخل بحساب الإدارة بتاع المنيو (نفس إيميل لوحة الإدارة) من Settings → Online menu.
   2) طلبات الطاولة الجديدة بتنزل في Orders كـ«بانتظار الدفع»، والتحصيل عند الكاشير.
   3) أي تغيير حالة في الكاشير/الباريستا بيتبعت للمنيو: preparing · ready · completed · cancelled.
   4) الأسعار والأصناف الخالصة (sold out) بتتسحب من المنيو عند الربط، عشان الكاشير والمنيو يبقوا نفس الأرقام.
   مفيش كلمة سر ولا مفتاح إداري محفوظ في الملفات — الجلسة بتتحفظ في المتصفح بعد الدخول. */
(function () {
  'use strict';
  const D = window.DARJ;
  const C = (D.CFG && D.CFG.connect) || {};
  const STATUS_OUT = { prep: 'preparing', ready: 'ready', done: 'completed', rejected: 'cancelled', cancelled: 'cancelled' };
  let client = null, started = false, timer = null, channel = null;

  function sdk() {
    return new Promise((res, rej) => {
      if (window.supabase) { res(window.supabase); return; }
      const sc = document.createElement('script');
      sc.src = 'assets/vendor/supabase-2.116.0.js';
      sc.onload = () => res(window.supabase); sc.onerror = () => rej(new Error('supabase sdk'));
      document.head.appendChild(sc);
    });
  }
  async function init() {
    if (client) return client;
    const lib = await sdk();
    client = lib.createClient(C.url, C.key, { auth: { persistSession: true, storageKey: 'luxurycrop-pos-auth' } });
    return client;
  }
  async function isAdmin(c, uid) {
    const r = await c.from('admin_users').select('user_id').eq('user_id', uid).maybeSingle();
    return !r.error && !!r.data;
  }

  // سطر الإضافة بيتركّب على آخر صنف قبله في نفس الطلب
  function groupOf(optId) {
    const id = (D.ALIAS && D.ALIAS[optId]) || optId;
    for (const [g, G] of Object.entries(D.MODS)) if ((G.opts || []).some((o) => o.id === id)) return [g, id];
    return [null, id];
  }
  function mapOrder(o) {
    const lines = [], missing = [];
    (o.order_items || []).forEach((it) => {
      if (it.item_type === 'addon') {
        const [g, id] = groupOf(it.item_id);
        const last = lines[lines.length - 1];
        if (last && g && D.prod(last.pid).mods.includes(g)) { last.mods[g] = (last.mods[g] || []).concat(Array(it.quantity).fill(id).slice(0, 1)); return; }
        missing.push(`${it.quantity}× ${it.item_name}`); return;
      }
      const p = D.prod(it.item_id);
      if (!p) { missing.push(`${it.quantity}× ${it.item_name}`); return; }
      lines.push({ pid: p.id, qty: it.quantity, mods: D.defMods(p), note: it.note || '' });
    });
    if (missing.length && lines.length) lines[lines.length - 1].note = [lines[lines.length - 1].note, 'غير معروف: ' + missing.join('، ')].filter(Boolean).join(' · ');
    return {
      ext: o.id, extNo: o.order_number, ch: 'table', type: 'table', table: o.table_no, ts: new Date(o.created_at).getTime(),
      name: o.customer_name || '', phone: o.customer_phone || '', label: o.service_label || '', lines,
    };
  }

  async function pull() {
    const c = await init();
    const since = new Date(Date.now() - 6 * 3600e3).toISOString();
    const r = await c.from('orders')
      .select('id,order_number,table_no,service_label,customer_name,customer_phone,status,total,created_at,order_items(item_type,item_id,item_name,quantity,unit_price,note)')
      .in('status', ['new', 'preparing']).gte('created_at', since).order('created_at');
    if (r.error) throw r.error;
    const known = new Set(D.state().orders.map((x) => x.ext).filter(Boolean));
    r.data.filter((o) => !known.has(o.id)).forEach((o) => { const m = mapOrder(o); if (m.lines.length) D.addOnline(m); });
  }
  async function syncCatalog() {
    const c = await init();
    const r = await c.from('products').select('id,price,sold_out,is_active');
    if (r.error) return;
    D.mutate((s) => {
      let n = 0;
      r.data.forEach((p) => {
        const mine = D.prod(p.id); if (!mine) return;
        const price = Number(p.price);
        if (price && price !== mine.price && s.prices[p.id] !== price) { s.prices[p.id] = price; n++; }
        const on = !p.sold_out && p.is_active !== false;
        if ((s.avail[p.id] !== false) !== on) { s.avail[p.id] = on; n++; }
      });
      D.log(null, 'sync', `مزامنة المنيو الأونلاين — ${n} تحديث في الأسعار والتوفّر`);
    }, 'sync');
  }
  async function start() {
    if (started) return; started = true;
    const c = await init();
    D.hooks.status = (o, st) => { const out = STATUS_OUT[st]; if (out && o.ext) c.from('orders').update({ status: out, updated_at: new Date().toISOString() }).eq('id', o.ext).then(() => {}); };
    await syncCatalog();
    await pull();
    channel = c.channel('pos-orders').on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'orders' }, () => setTimeout(pull, 600)).subscribe();
    timer = setInterval(() => { if (navigator.onLine) pull().catch(() => {}); }, C.pollMs || 2500);
    D.toast('اتربط بالمنيو الأونلاين', 'طلبات الطاولة هتنزل في Orders', { ic: 'cloud' });
  }

  window.DARJ_CONNECT = {
    enabled: !!C.enabled,
    open(me) {
      if (!C.enabled) return;
      const m = D.modal(`${D.head('ربط المنيو الأونلاين', 'ادخل بحساب الإدارة بتاع المنيو (نفس لوحة الإدارة)')}
        <div class="modal__b grid" style="gap:12px"><label class="field"><span>البريد</span><input class="input mono" id="cxE" type="email" autocomplete="username"></label>
        <label class="field"><span>كلمة المرور</span><input class="input mono" id="cxP" type="password" autocomplete="current-password"></label><div id="cxErr"></div></div>
        <div class="modal__f"><button class="btn btn--ghost" data-close>إلغاء</button><button class="btn btn--ink" id="cxGo">دخول وربط</button></div>`, { cls: 'modal--sm' });
      m.querySelector('#cxGo').addEventListener('click', async () => {
        const err = (t) => { m.querySelector('#cxErr').innerHTML = `<div class="blind" style="color:var(--red)">${t}</div>`; };
        try {
          const c = await init();
          const out = await c.auth.signInWithPassword({ email: m.querySelector('#cxE').value.trim(), password: m.querySelector('#cxP').value });
          if (out.error) return err('البريد أو كلمة المرور غير صحيحة');
          if (!(await isAdmin(c, out.data.user.id))) { await c.auth.signOut(); return err('الحساب ده مش حساب إدارة'); }
          D.mutate(() => D.log(me, 'sync', 'تشغيل الربط مع المنيو الأونلاين'), 'sync');
          m.close(); start();
        } catch (e) { err('تعذّر الاتصال — تأكد من الإنترنت'); }
      });
    },
  };

  // لو فيه جلسة إدارة محفوظة، الربط بيرجع لوحده
  if (C.enabled && D.REAL) {
    init().then(async (c) => { const s = await c.auth.getSession(); const u = s && s.data && s.data.session && s.data.session.user; if (u && await isAdmin(c, u.id)) start(); }).catch(() => {});
  }
})();
