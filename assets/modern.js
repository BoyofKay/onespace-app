// OneSpace product website — visitor interactions only. No mobile-app changes.
(()=>{'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const safeStore={get(k){try{return localStorage.getItem(k)}catch(_){return null}},set(k,v){try{localStorage.setItem(k,v)}catch(_){}}};
const menu=$('#menuToggle'),nav=$('#mainNav');
if(menu&&nav){menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.dataset.open=String(open)});$$('#mainNav a').forEach(a=>a.addEventListener('click',()=>{menu.setAttribute('aria-expanded','false');nav.dataset.open='false'}))}
const themes=['midnight','clean','rose','mono'];
function themeChange(theme){if(!themes.includes(theme))return;document.body.dataset.siteTheme=theme;const p=$('#themePreview');if(p)p.dataset.theme=theme;$$('[data-theme-choice]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.themeChoice===theme)));safeStore.set('onespace-web-theme',theme);eventHook('theme_changed',{theme})}
$$('[data-theme-choice]').forEach(b=>b.addEventListener('click',()=>themeChange(b.dataset.themeChoice)));
themeChange(safeStore.get('onespace-web-theme')||'midnight');
const walk=[
{title:'Today · the day at a glance',subtitle:'Your little corner of the day, together.',items:[['☀️ Good morning, Alex','A calm start to your shared day'],['☑ Needs attention','Choose our Friday night plans'],['📅 Coming up','Friday · Movie night']]},
{title:'Remember · save the details',subtitle:'From fleeting thought to something you can find again.',items:[['📝 A note for both of us','A new Italian place to try'],['📅 Our shared calendar','Dinner idea · Friday'],['📍 Our places','Add it to our places to visit']]},
{title:'Coordinate · make a decision',subtitle:'Discuss a plan without losing the context.',items:[['🧭 Friday date night','Exploring · Shared activity'],['✨ Two options','Italian restaurant · Movie at home'],['✓ Decided together','Italian restaurant · Friday evening']]},
{title:'Connect · keep the moment',subtitle:'The day was lovely. Keep a little piece of it.',items:[['💌 A little love','Send a hug on purpose'],['📸 Our memory','Friday dinner · A moment worth keeping'],['♡ Shared experiences','A date to remember']]}
];
let step=0;
function renderDemo(n){step=(n+walk.length)%walk.length;const data=walk[step];if($('#demoTitle'))$('#demoTitle').textContent=data.title;if($('#demoSubtitle'))$('#demoSubtitle').textContent=data.subtitle;const root=$('#demoObjects');if(root){root.replaceChildren();data.items.forEach(([title,desc])=>{const box=document.createElement('div');box.className='demo-object';const strong=document.createElement('b');strong.textContent=title;const span=document.createElement('span');span.textContent=desc;box.append(strong,span);root.append(box)})}$$('[data-step]').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.step===step)));if($('#demoPrev'))$('#demoPrev').disabled=step===0;if($('#demoNext'))$('#demoNext').textContent=step===walk.length-1?'Start again ↻':'Next step →';eventHook('demo_step',{step:step+1})}
$$('[data-step]').forEach(b=>b.addEventListener('click',()=>renderDemo(Number(b.dataset.step))));
if($('#demoNext'))$('#demoNext').addEventListener('click',()=>renderDemo(step===walk.length-1?0:step+1));
if($('#demoPrev'))$('#demoPrev').addEventListener('click',()=>renderDemo(step-1));
renderDemo(0);
// Event names are deliberately internal hooks. No third-party analytics or tracking is enabled.
function eventHook(name,properties){if(typeof window.onespaceAnalytics==='function')window.onespaceAnalytics(name,properties)}
const form=$('#waitlistForm');
if(form)form.addEventListener('submit',async e=>{
 e.preventDefault();const status=$('#waitStatus'),button=form.querySelector('[type="submit"]');
 const say=(message,good)=>{status.textContent=message;status.className='status '+(good?'ok':'error')};
 if(form.elements.company?.value)return;
 const email=String(form.elements.email.value||'').trim(),platform=String(form.elements.platform.value||'').trim();
 if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){say('Please enter a valid email address.',false);return}
 if(!['Android','iOS','Both','Undecided'].includes(platform)){say('Please choose a phone platform.',false);return}
 if(!form.elements.consent.checked){say('Please agree to receive OneSpace updates before continuing.',false);return}
 button.disabled=true;say('Sending your request…',true);
 try{
 const supabaseUrl='https://ugwrpeduzyzrujkizqfo.supabase.co';
 const anonKey='sb_publishable_TtW_uUboFxD4adF5o7FSfA_cpjojMCe';
 const language=document.documentElement.lang==='ar'?'ar':'en';
 const message='Early-access interest request. Platform: '+platform+'. Opt-in: explicit launch/testing email consent. Source: public website. No founder number assigned.';
 const res=await fetch(supabaseUrl+'/rest/v1/rpc/submit_public_support',{method:'POST',headers:{'Content-Type':'application/json',apikey:anonKey,Authorization:'Bearer '+anonKey},body:JSON.stringify({p_kind:'contact',p_subject:'Website: OneSpace early-interest / '+platform,p_message:message,p_reply_email:email,p_app_version:'website',p_platform:'other',p_locale:language,p_diagnostics:'OneSpace website early-access form; '+location.pathname})});
 if(!res.ok){const details=await res.text();throw new Error(details.includes('Too many')?'rate':'send')}
 form.reset();say('Thank you! Your interest request was received. We’ll contact you if an early-access place is available.',true);eventHook('waitlist_submitted',{platform})
 }catch(err){say(err.message==='rate'?'We have received too many requests right now. Please try again later.':'Could not send the request. Please try again or contact support.',false)}
 finally{button.disabled=false}
});
const newAr={
'new.nav.features':'الميزات','new.nav.how':'كيف يعمل','new.nav.themes':'المظاهر','new.nav.faq':'الأسئلة الشائعة','new.nav.support':'الدعم','new.nav.access':'انضم للتجربة المبكرة ↗',
'new.hero.tag':'حياة مشتركة، ببساطة','new.hero.title':'أقرب قليلاً.<br><span>كل يوم.</span>','new.hero.lead':'بيت خاص لكل ما يجمعكما. خططا معًا، تذكّرا التفاصيل الصغيرة، وابقيا قريبين سواء كنتما في المنزل نفسه أو تفصل بينكما قارات.',
'new.hero.cta':'انضم إلى مجتمع المؤسسين ↗','new.hero.demo':'تعرّف على التطبيق ▶','new.hero.fine':'✦ لشخصين فقط · الخصوصية أولاً · مرحلة الاختبار المبكر',
'new.trust.intro':'صُمم للعلاقات الحقيقية','new.trust.a':'✦ لكما أنتما الاثنين','new.trust.b':'✦ خاص أو مشترك، حسب اختيارك','new.trust.c':'✦ بلا إعلانات أو بيع للبيانات',
'new.features.tag':'كل شيء في مكانه','new.features.title':'مساحة واحدة. وكل التفاصيل التي تصنع حياتكما.','new.features.lead':'ليس مجرد تطبيق رسائل، بل مكان للخطط والأشخاص والقرارات والذكريات التي تشكل علاقتكما.',
'new.today.title':'اليوم','new.today.copy':'اعرفا ما يحتاج الاهتمام، وما يقترب، والفرص الصغيرة للاهتمام ببعضكما.',
'new.remember.title':'تذكّر','new.remember.copy':'تقويم مشترك، مهام، ملاحظات، مناسبات، أشخاص وأماكن مهمة.',
'new.coordinate.title':'نسّق','new.coordinate.copy':'ناقشا الأفكار، قارنا الخيارات، اتخذا القرارات وخططا للرحلات معًا.',
'new.connect.title':'تواصل','new.connect.copy':'لفتات لطيفة، رسائل حب، تواصل يومي، ذكريات وتجارب مشتركة.',
'new.me.title':'أنا والتفضيلات','new.me.copy':'اللغة والمظهر والإشعارات والتحكم في بياناتك الشخصية والمساعدة.',
'new.why.tag':'لماذا OneSpace','new.why.title':'لأن الحب يسكن التفاصيل.','new.why.copy':'المطعم الذي تحدث عنه شريكك، وتاريخ مهم، وفكرة وعدتما بالعودة إليها. يساعدكما OneSpace على حفظ كل تلك التفاصيل معًا.',
'new.why.a':'تذكّرا ما يهم شريك حياتكما','new.why.b':'نظّما أموركما دون أن تبدو عبئًا','new.why.c':'احتفظا باللحظات إلى جوار الخطط اليومية','new.why.link':'استكشف كل الميزات ↗',
'new.theme.tag':'مساحتكما، بطريقتكما','new.theme.title':'غيّرا الأجواء.<br><em>واحتفظا بالسحر.</em>','new.theme.copy':'جرّب المظاهر المستوحاة من إعدادات OneSpace. ينبغي أن تشبهكما مساحتكما الخاصة.','new.theme.note':'يغيّر هذا العرض مظهر الموقع، وليس إعدادات تطبيقك.',
'new.demo.tag':'جرّب بنفسك','new.demo.title':'جولة صغيرة في مساحتكما المشتركة.','new.demo.copy':'انتقل بين خطوات مثال واقعي، من فكرة تتذكرانها إلى خطة وقرار وذكرى.',
'new.both.tag':'تطبيق واحد، بطرق مختلفة','new.both.title':'للمسافات بينكما، وللحظات التي تجمعكما.',
'new.both.ldr':'مكانان. حياة مشتركة واحدة.','new.both.ldrcopy':'المناطق الزمنية والزيارات المقبلة والتذكيرات والتواصل اليومي في مكان واحد.',
'new.both.home':'منزل واحد. ومساحتكما الخاصة.','new.both.homecopy':'روتين مشترك، مناسبات، أفكار لأوقاتكما وكل ما يستحق الاحتفاظ به.',
'new.faq.tag':'أسئلة مهمة','new.faq.title':'ربما تتساءل عن بعض الأمور.','new.faq.q1':'هل OneSpace للعلاقات عن بُعد فقط؟','new.faq.a1':'لا، يناسب الأزواج الذين يعيشون معًا أو بعيدًا في المنطقة الزمنية نفسها أو في مناطق مختلفة.',
'new.faq.q2':'هل يرى شريكي كل ملاحظاتي وخططي؟','new.faq.a2':'لا. يمكنك اختيار «مشترك» أو «أنا فقط» لكل عنصر وفقًا لإعداداته.',
'new.faq.q3':'هل التطبيق متاح للتنزيل؟','new.faq.a3':'OneSpace في مرحلة اختبار مبكر على أندرويد، وسيُعلن عن توفر iOS لاحقًا. سجّل اهتمامك لمعرفة المستجدات.',
'new.faq.q4':'هل تبيعون بياناتنا أو تعرضون الإعلانات؟','new.faq.a4':'لا. تنص سياسة خصوصية التطبيق على أنه لا يبيع بيانات المستخدمين أو يعرض إعلانات.',
'new.faq.q5':'هل يمكنني حذف بياناتي؟','new.faq.a5':'نعم، يوجد تصدير للبيانات وحذف للحساب. قد تبقى العناصر المشتركة مع الشريك الآخر وفقًا للسياسة.',
'new.faq.more':'جميع الأسئلة الشائعة ↗',
'new.early.tag':'ابدأ مبكرًا','new.early.title':'الأشياء الجميلة تبدأ بشخصين.<br>والمجتمعات الجميلة تبدأ صغيرة.','new.early.copy':'نصنع OneSpace مع الأزواج الحقيقيين. أخبرنا بهاتفك لتصلك أخبار فرص التجربة الجديدة.',
'new.early.disclaimer':'يُؤكد وضع الأعضاء المؤسسين بصورة فردية. التسجيل لا يضمن مقعدًا أو موعدًا للوصول.',
'new.form.title':'سجّل اهتمامك المبكر ♡','new.form.copy':'لا رسائل مزعجة. فقط أخبار التجربة والإطلاق.','new.form.email':'عنوان البريد الإلكتروني','new.form.platform':'ما نوع هاتفك؟',
'new.form.consent':'أوافق على استلام تحديثات OneSpace عبر البريد وأفهم أن هذا الطلب يُعالج عبر صندوق دعم OneSpace. <a href="privacy.html">سياسة الخصوصية</a>.',
'new.form.submit':'أريد الانضمام ↗','new.form.foot':'يُرسل بريدك ونوع هاتفك بشكل آمن إلى فريق OneSpace، دون أي دفع.',
'new.footer.tag':'نحن الاثنان. مساحة واحدة.<br>بيت خاص للحياة التي تتشاركانها.'
};
const original=new Map();
function translateNew(){const ar=document.documentElement.lang==='ar';$$('[data-i18n^="new."]').forEach(el=>{if(!original.has(el))original.set(el,el.innerHTML);el.innerHTML=ar&&newAr[el.dataset.i18n]?newAr[el.dataset.i18n]:original.get(el)});}
translateNew();$$('.lang').forEach(b=>b.addEventListener('click',()=>translateNew()));
})();