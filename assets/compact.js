// OneSpace compact site — accessible demos, color preview and consented interest intake.
// UI demonstrations use fictional sample data; no tracking services or app data are accessed.
(()=>{'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const safeGet=k=>{try{return localStorage.getItem(k)}catch(_){return null}};
const safeSet=(k,v)=>{try{localStorage.setItem(k,v)}catch(_){}};
const nav=$('#mainNav'),menu=$('#menuToggle');
if(menu&&nav){menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.dataset.open=String(open)});$$('.nav a').forEach(a=>a.addEventListener('click',()=>{menu.setAttribute('aria-expanded','false');nav.dataset.open='false'}));}
const themes=['midnight','mono','clean','rose'];
function setTheme(theme){if(!themes.includes(theme))theme='clean';document.body.dataset.theme=theme;
['#heroApp','#tourApp'].forEach(s=>{const el=$(s);if(el)el.dataset.appTheme=theme});
$$('.swatch').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.theme===theme)));safeSet('onespace-web-theme',theme);
}
$$('.swatch').forEach(b=>b.addEventListener('click',()=>setTheme(b.dataset.theme)));
setTheme(safeGet('onespace-web-theme')||'clean');
const steps=[
{title:'Start with your day',body:"See what needs attention, what’s happening together, and the details you don't want to forget.",chips:['☑ Needs attention','📅 Coming up','♡ Stay close'],app:'Today',sub:'Your space, at a glance',cards:[['Since you were away',"You're all caught up."],['Needs your attention',"Friday · Choose our plans"],['Coming up together','Friday · Movie night']]},
{title:'Remember the little things',body:"Keep a calendar, to-do lists, reminders, notes, and the people and places that matter. Choose Shared or Only me when you add something.",chips:['📅 Shared calendar','☑ To-do lists','📝 Notes'],app:'Remember',sub:'A home for everything coming up',cards:[['Shared calendar','Our plans in one place'],['To-do lists','Things we want to get done'],['Notes','Details worth keeping']]},
{title:'Make the plan together',body:"Collect options in a shared activity, discuss the details, and save the decision without losing the conversation. You can plan journeys here too.",chips:['🧭 Shared activities','✓ Decisions','✈ Trips'],app:'Coordinate',sub:'Plans and decisions',cards:[['Activities','Friday dinner · Exploring'],['Options','Dinner out or movie at home'],['Trips','Our next visit · Planning']]},
{title:'Keep the connection',body:"Send a thoughtful gesture when you choose, write a letter, and save the memories that make your shared life feel like yours.",chips:['💌 Love letters','♡ Little gestures','📷 Memories'],app:'Connect',sub:'The meaningful moments',cards:[['A little love','Send a warm hug'],['Memories','Our best weekend yet'],['Daily connection',"What's on your mind?"]]}
];
let current=0;
function showStep(n){current=((n%steps.length)+steps.length)%steps.length;const step=steps[current];
if($('#stepIndex'))$('#stepIndex').textContent=String(current+1).padStart(2,'0')+' / 04';
if($('#stepTitle'))$('#stepTitle').textContent=step.title;
if($('#stepBody'))$('#stepBody').textContent=step.body;
if($('#stepHint'))$('#stepHint').textContent=step.app.toUpperCase();
if($('#tourAppHeading'))$('#tourAppHeading').textContent=step.app;
if($('#tourAppSub'))$('#tourAppSub').textContent=step.sub;
const chips=$('#stepChips');if(chips){chips.replaceChildren();step.chips.forEach(x=>{const el=document.createElement('span');el.className='tour-chip';el.textContent=x;chips.append(el)})}
const cards=$('#tourAppCards');if(cards){cards.replaceChildren();step.cards.forEach(([label,value])=>{const card=document.createElement('div');card.className='app-card';const heading=document.createElement('div');heading.className='cardhead';heading.textContent=label;const content=document.createElement('div');content.className='app-row';content.textContent=value;card.append(heading,content);cards.append(card)})}
$$('.tour-tab').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.step)===current)));
if($('#tourNext'))$('#tourNext').textContent=current===steps.length-1?'Start again ↻':'Next step →';
if($('#tourAppCurrent'))$('#tourAppCurrent').textContent=step.app;
}
$$('.tour-tab').forEach(b=>b.addEventListener('click',()=>showStep(Number(b.dataset.step))));
if($('#tourNext'))$('#tourNext').addEventListener('click',()=>showStep(current+1));
showStep(0);
const form=$('#waitlistForm');
if(form)form.addEventListener('submit',async e=>{e.preventDefault();const status=$('#waitStatus'),button=form.querySelector('button[type=submit]');
const say=(s,kind)=>{status.textContent=s;status.className='status '+kind};
if(form.elements.company&&form.elements.company.value)return;
const email=String(form.elements.email.value||'').trim();const platform=String(form.elements.platform.value||'').trim();
if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email))return say('Please enter a valid email address.','error');
if(!['Android','iOS','Both','Undecided'].includes(platform))return say('Please select a phone platform.','error');
if(!form.elements.consent.checked)return say('Please consent to launch updates first.','error');
button.disabled=true;say('Sending your request…','');
try{const url='https://ugwrpeduzyzrujkizqfo.supabase.co/rest/v1/rpc/submit_public_support';
const key='sb_publishable_TtW_uUboFxD4adF5o7FSfA_cpjojMCe';
const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json',apikey:key,Authorization:'Bearer '+key},body:JSON.stringify({p_kind:'contact',p_subject:'OneSpace early-interest · '+platform,p_message:'Opted in on the website for testing/launch updates. Phone platform: '+platform+'. No founder membership number assigned.',p_reply_email:email,p_app_version:'website',p_platform:'other',p_locale:document.documentElement.lang==='ar'?'ar':'en',p_diagnostics:'website early-interest form; no automated tracking'})});
if(!response.ok){const body=await response.text();throw new Error(body.includes('Too many')?'rate':'network')}
form.reset();say('Received! Thank you for your interest. We’ll reach out with updates.','ok');
}catch(ex){say(ex.message==='rate'?'Too many requests right now. Please try later.':'Could not send. Please try again or contact support.','error')}finally{button.disabled=false}
});
const arabic={
'c.nav.features':'المميزات','c.nav.tour':'جرّب التطبيق','c.nav.themes':'المظاهر','c.nav.faq':'الأسئلة الشائعة','c.nav.support':'الدعم','c.nav.join':'انضم مبكرًا ↗',
'c.hero.kicker':'للأزواج، معًا أو عن بُعد','c.hero.title':'حياتكما معًا.<br><em>في مساحة جميلة واحدة.</em>',
'c.hero.desc':'بيت خاص لخططكما وتقويمكما المشترك والتذكيرات والذكريات واللفتات اللطيفة. تفاصيل أقل تشغل البال، ووقت أكثر يجمعكما.',
'c.hero.primary':'سجّل اهتمامك ↗','c.hero.secondary':'استكشف OneSpace ▶','c.hero.proof':'<strong>نحن الاثنان. مساحة واحدة.</strong> بلا إعلانات. خاص أو مشترك، باختيارك.',
'c.visual.top':'ابقيا قريبين حتى من بعيد','c.visual.bottom':'خططا لأدق التفاصيل',
'c.value.a':'<i>♡</i> خصوصية لشخصين','c.value.as':'أنت من يحدد الخاص والمشترك','c.value.b':'<i>☑</i> خططا معًا','c.value.bs':'مواعيد وقرارات وتذكيرات ورحلات','c.value.c':'<i>✦</i> تذكّرا أكثر','c.value.cs':'الأشخاص والملاحظات والأماكن والذكريات',
'c.tour.kicker':'جرّب رحلة بسيطة','c.tour.title':'اكتشف OneSpace بأربع نقرات.','c.tour.desc':'اكتشف كيف يجمع يومكما وخططكما والتواصل بينكما. اختر قسمًا أو اتبع الجولة القصيرة.',
'c.tour.mock':'عرض توضيحي · بيانات خيالية',
'c.theme.title':'مساحتكما بطريقتكما.','c.theme.desc':'جرّب الألوان المستوحاة من التطبيق. يمكن لكل شريك اختيار مظهره.',
'c.more.features':'جميع المميزات ←','c.more.tutorials':'الدليل الكامل ←','c.more.ldr':'للعلاقات عن بُعد ←',
'c.early.kicker':'مجتمع البداية','c.early.title':'كن من أوائل من يعرفون.','c.early.body':'ندعو الأزواج للمساعدة في تشكيل OneSpace. أخبرنا بنوع هاتفك لنرسل لك أخبار التجربة والإطلاق.',
'c.early.founder':'✦ الداعمون الأوائل · نخطط لتقدير أول 500 مؤسس',
'c.form.email':'البريد الإلكتروني','c.form.platform':'نوع هاتفك','c.form.button':'انضم ↗',
'c.form.consent':'أوافق على استقبال أخبار تجربة OneSpace وإطلاقه. سيُرسل بريدي ونوع هاتفي إلى صندوق دعم OneSpace. <a href="privacy.html">الخصوصية</a>.'
};
const originals=new Map();
function translate(){const ar=document.documentElement.lang==='ar';$$('[data-i18n^="c."]').forEach(el=>{if(!originals.has(el))originals.set(el,el.innerHTML);el.innerHTML=ar&&arabic[el.dataset.i18n]?arabic[el.dataset.i18n]:originals.get(el)});
}
translate();$$('.lang').forEach(b=>b.addEventListener('click',translate));
})();
