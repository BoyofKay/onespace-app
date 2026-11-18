import { chromium } from 'playwright';
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-sandbox']});
const failures=[];
const paths=['es/','fr/','de/','de/features.html','es/how-it-works.html'];
const widths=[375,810,1120,1536];
for(const route of paths){
 for(const width of widths){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  const errs=[];
  page.on('pageerror',e=>errs.push(e.message));
  try{
   await page.goto('http://127.0.0.1:8765/'+route,{waitUntil:'domcontentloaded',timeout:25000});
   await page.waitForTimeout(200);
   const stats=await page.evaluate(()=>{
    const rect=(selector)=>document.querySelector(selector)?.getBoundingClientRect();
    const header=rect('.top');
    const join=rect('.top .nav-join');
    const storeButton=rect('.store-arrival-card > .btn');
    const card=rect('.store-arrival-card');
    const bodyWidth=document.documentElement.scrollWidth;
    const viewport=document.documentElement.clientWidth;
    const wall=document.querySelector('.wall');
    return {header:header?.height??0,join:join?.width??0,joinVisible:join?.width>0,
     storeButton:storeButton?.width??0,storeCard:card?.width??0,
     documentWidth:bodyWidth,viewport,
     themedScroll:wall?getComputedStyle(wall).scrollbarColor:'none',
     themeCount:document.querySelectorAll('[data-theme-pick]').length,
     screenshots:document.querySelectorAll('.device img').length,
     topText:document.body.textContent.trim().slice(0,20)};
   });
   if(stats.header>105)failures.push(route+' '+width+': header height '+stats.header);
   if(stats.documentWidth>stats.viewport+5)failures.push(route+' '+width+': horizontal document overflow '+(stats.documentWidth-stats.viewport));
   if(stats.joinVisible&&stats.join>210)failures.push(route+' '+width+': oversized nav join '+stats.join);
   if(stats.storeButton&&stats.storeButton>stats.storeCard-20)failures.push(route+' '+width+': store CTA extends beyond card');
   if(stats.topText==='HTML')failures.push(route+' '+width+': raw HTML text visible');
   if(errs.length)failures.push(route+' '+width+': JS errors '+errs.join('; ').slice(0,200));
   if(route==='de/'&&width===1536){
     const theme=page.locator('[data-theme-pick]').first();
     if(await theme.count()){
       const value=await theme.getAttribute('data-theme-pick');
       await theme.click();
       const selected=await page.locator('.phone[data-themable]').first().getAttribute('data-theme');
       if(selected!==value)failures.push('Theme click did not update phone theme');
     }
   }
   console.log('CHECK',route,width,JSON.stringify(stats));
  }catch(e){failures.push(route+' '+width+': '+e.message.slice(0,250));}
  finally{await page.close();}
 }
}
await browser.close();
if(failures.length){console.error('VISUAL/INTERACTION QA FAILED\n'+failures.join('\n'));process.exit(1);}
console.log('PASS: translated header/button geometry, page widths, theme interaction, and JS on 20 locale/viewport combinations.');
