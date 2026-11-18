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
     const choices=page.locator('[data-theme-pick]');
     if(await choices.count()>1){
       const theme=choices.nth(Math.min(2,(await choices.count())-1));
       const palette=await theme.getAttribute('data-palette');
       const screenshot=page.locator('img[data-theme-img]').first();
       const oldSrc=await screenshot.count()?await screenshot.getAttribute('src'):null;
       const expected=await theme.getAttribute('data-theme-pick');
       await theme.click();
       if((await theme.getAttribute('aria-pressed'))!=='true')failures.push('Theme button did not become selected');
       const phone=page.locator('.phone[data-themable]').first();
       if(await phone.count()){
         const actual=await phone.getAttribute('data-theme');
         if(actual!==expected)failures.push('Theme click did not update themable phone');
       }
       if(palette&&oldSrc!==null&&(await screenshot.getAttribute('src'))===oldSrc)
         failures.push('Theme click did not change screenshot image palette');
     }
   }
   if((route==='es/'||route==='fr/'||route==='de/')&&(width===375||width===1536)){
      if(width===375)await page.locator('.burger').click();
      const featureTrigger=page.locator('.top .menu .drop').first().locator('button').first();
      await featureTrigger.click();
      const featurePanel=page.locator('#mega-features');
      if(!await featurePanel.isVisible())failures.push(route+' '+width+': Features menu not visible');
      const details=await page.evaluate(()=>{
        const panel=document.querySelector('#mega-features'),trigger=document.querySelector('.top .menu .drop button');
        const label=panel?.querySelector('.mega-link b');
        const intro=panel?.querySelector('.mega-intro-title');
        const size=node=>node?parseFloat(getComputedStyle(node).fontSize):0;
        const rect=panel?.getBoundingClientRect();
        return {parentSize:size(trigger),childSize:size(label),introSize:size(intro),
          iconCount:panel?.querySelectorAll('.e, .card, [class*="icon"], img').length??-1,
          linkCount:panel?.querySelectorAll('.mega-link').length??0,
          panelX:rect?.x??-999,panelRight:rect?.right??9999};
      });
      if(details.childSize>details.parentSize+0.5)failures.push(route+' '+width+': mega link font larger than parent navigation');
      if(details.introSize>details.parentSize+0.5)failures.push(route+' '+width+': mega introduction font larger than parent navigation');
      if(details.iconCount!==0)failures.push(route+' '+width+': old emoji/card/icon navigation remains');
      if(details.linkCount<8)failures.push(route+' '+width+': lost feature destinations');
      if(width===1536&&(details.panelX< -1||details.panelRight>1537))
        failures.push(route+' '+width+': panel exceeds horizontal viewport');
      await page.locator('.top .menu .drop').nth(1).locator('button').first().click();
      if(await featurePanel.isVisible())failures.push(route+' '+width+': Features menu did not close when Couples opened');
      if(!await page.locator('#mega-couples').isVisible())failures.push(route+' '+width+': Couples menu not visible');
      await page.keyboard.press('Escape');
      if(await page.locator('#mega-couples').isVisible())failures.push(route+' '+width+': Escape did not close menu');
      console.log('MEGA',route,width,JSON.stringify(details));
   }
   console.log('CHECK',route,width,JSON.stringify(stats));
  }catch(e){failures.push(route+' '+width+': '+e.message.slice(0,250));}
  finally{await page.close();}
 }
}
await browser.close();
if(failures.length){console.error('VISUAL/INTERACTION QA FAILED\n'+failures.join('\n'));process.exit(1);}
console.log('PASS: translated header/button geometry, page widths, theme interaction, and JS on 20 locale/viewport combinations.');
