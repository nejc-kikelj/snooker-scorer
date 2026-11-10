# Test cases derived from the WPBSA Rules of Snooker (May 2022 edition), Section 3. Expected values come from the rule text.
import json
from ui import new
c=new()
c.eval("D.players=[{id:'a',name:'Ann'},{id:'b',name:'Bob'}];render();")
c.eval(r"""
var run=(acts,br=0)=>{const S=newFrame(br);acts.forEach(a=>applyAction(S,a));return S};
var clearance=(ci,sc)=>{const S=newFrame(0);S.reds=0;S.phase='clear';S.ci=ci;S.cols=COL.map((_,i)=>i>=ci);S.sc=sc||[0,0];return S};
var foul=(S,o)=>{applyAction(S,Object.assign({k:'foul',pots:[],hit:null,potted:[],type:'wrong'},o));return S};
var lastFoulPts=S=>S.st[1-S.turn].foulPtsRecv; // before turn flips: use st directly in each test
var T=[];function t(rule,desc,fn){let ok=false,info='';try{const r=fn();ok=(r===true);if(r!==true)info=String(r)}catch(e){info='EXC '+e.message}T.push([rule,desc,ok,info])}
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b)||('got '+JSON.stringify(a)+' want '+JSON.stringify(b));

// ---- Rule 1 / 3: scoring ----
t('3.1(a)','values: red 1, yellow 2 ... black 7',()=>eq(BALLS.map(b=>VAL[b]),[1,2,3,4,5,6,7]));
t('3.1(f)(i)','maximum break 147 wins the frame',()=>{const p=[];for(let i=0;i<15;i++)p.push({b:'red'},{b:'black'});COL.forEach(b=>p.push({b}));const S=run([{k:'turn',pots:p}]);return eq([S.sc,S.over,S.winner],[[147,0],true,0])});
t('3.3(g)','each red potted in the same stroke is scored',()=>{const S=run([{k:'turn',pots:[{b:'red'},{b:'red'},{b:'red'},{b:'blue'}]}]);return eq([S.sc[0],S.reds],[8,12])});
t('3.3(g)','a free ball nominated as a red and a red in the same stroke score 1 each',()=>{const S=newFrame(0);S.free=true;applyPot(S,{b:'green',f:true});applyPot(S,{b:'red'});return eq([S.sc[0],S.reds],[2,14])});
t('3.3(h)(i)','after a red the next ball on is a colour; red is not allowed',()=>{const S=newFrame(0);applyPot(S,{b:'red'});const e1=applyPot(clone(S),{b:'yellow'});const S2=clone(S);S2.brk=[];const e2=applyPot(S2,{b:'red'});return eq([e1,!!e2],[null,true])});
t('3.3(h)(i)','a potted colour is spotted again while reds remain',()=>{const S=run([{k:'turn',pots:[{b:'red'},{b:'pink'}]}]);return eq([S.cols.every(Boolean),S.reds],[true,14])});
t('3.3(h)(ii)(iii)','after the last red a colour is played, then yellow..black in order',()=>{const S=newFrame(0);S.reds=1;applyPot(S,{b:'red'});applyPot(S,{b:'black'});const bad=applyPot(clone(S),{b:'green'});const ok=applyPot(S,{b:'yellow'});return eq([S.phase,S.ci,!!bad,ok],['clear',1,true,null])});
t('3.3(j)/3.3(h)','a miss ends the turn; incoming player is on a red',()=>{const S=run([{k:'turn',pots:[{b:'red'}]}]);return eq([S.turn,S.phase],[1,'red'])});
t('3.3(h)(ii)','missing the colour after the last red: opponent starts on yellow',()=>{const S=newFrame(0);S.reds=1;applyAction(S,{k:'turn',pots:[{b:'red'}]});return eq([S.turn,S.phase,S.ci],[1,'clear',0])});

// ---- Rule 4: end of frame ----
t('3.4(a)','last black potted ends the frame, higher score wins',()=>{const S=clearance(5,[10,20]);applyAction(S,{k:'turn',pots:[{b:'black'}]});return eq([S.over,S.winner,S.sc],[true,0,[17,20]].map((x,i)=>i==1?1:x)) });
t('3.4(a)(b)','level scores after the black: black spotted, lots drawn, nobody wins yet',()=>{const S=clearance(5,[0,7]);applyAction(S,{k:'turn',pots:[{b:'black'}]});return eq([S.over,S.phase,S.needToss],[false,'rsblack',true])});
t('3.4(a)','a foul on the last black ends the frame (fouler behind)',()=>{const S=clearance(5,[40,50]);foul(S,{type:'miss'});return eq([S.over,S.winner],[true,1])});
t('3.4(a)','a foul on the last black ends the frame (fouler still ahead)',()=>{const S=clearance(5,[60,20]);foul(S,{type:'miss'});return eq([S.over,S.winner],[true,0])});
t('3.4(a)(i)','a foul that levels the scores on the last black: respotted black',()=>{const S=clearance(5,[53,46]);S.turn=0;foul(S,{type:'miss'});return eq([S.over,S.phase,S.needToss],[false,'rsblack',true])});
t('3.4(b)(iv)','respotted black: first pot ends the frame',()=>{const S=clearance(5,[10,10]);S.phase='rsblack';S.needToss=true;applyAction(S,{k:'toss',p:1});applyAction(S,{k:'turn',pots:[{b:'black'}]});return eq([S.over,S.winner],[true,1])});
t('3.4(b)(iv)','respotted black: first infringement ends the frame',()=>{const S=clearance(5,[10,10]);S.phase='rsblack';S.needToss=true;applyAction(S,{k:'toss',p:1});foul(S,{type:'miss'});return eq([S.over,S.winner],[true,0])});
t('3.4(b)(iv)','respotted black: replace/play again does not keep the frame going',()=>{const S=clearance(5,[10,10]);S.phase='rsblack';S.needToss=true;applyAction(S,{k:'toss',p:1});foul(S,{type:'miss',again:true});return eq([S.over,S.winner],[true,0])});

// ---- Rule 10: fouls ----
t('3.10(e)','points scored in the break before a foul count',()=>{const S=run([{k:'foul',pots:[{b:'red'},{b:'blue'}],hit:null,potted:[],type:'miss'}]);return eq(S.sc,[6,4]) });
t('3.10(e)','no points for a ball pocketed in the foul stroke; red stays off, colour respotted',()=>{const S=run([{k:'foul',pots:[],hit:'red',potted:['red','yellow'],type:'inoff'}]);return eq([S.sc,S.reds,S.cols.every(Boolean)],[[0,4],14,true])});
t('3.10(g)','several fouls in one stroke: highest penalty only',()=>{const S=run([{k:'foul',pots:[],hit:'pink',potted:['blue'],type:'wrong'}]);return eq(S.sc,[0,6])});
t('3.10(i)','after a foul the ball on is a red (or yellow when all reds are gone)',()=>{const S=run([{k:'foul',pots:[],type:'miss'}]);const T2=newFrame(0);T2.reds=0;T2.phase='clear';T2.ci=2;T2.cols=[false,false,true,true,true,true];foul(T2,{});return eq([S.phase,T2.phase,T2.ci],['red','clear',2])});
t('3.10(f)','a foul on the colour after the last red: opponent starts at yellow',()=>{const S=newFrame(0);S.reds=1;foul(S,{pots:[{b:'red'}],type:'miss'});return eq([S.phase,S.ci,S.turn],['clear',0,1])});

// ---- Rule 11: penalty values ----
const FV=(S,hit,potted,nom,fb,seven)=>foulValue(S,hit,potted||[],nom||null,fb||null,!!seven);
t('3.11','base penalty is 4 (cue-ball pocketed, red on)',()=>eq(FV(newFrame(0),'red'),4));
t('3.11(a)(vi)','ball on blue, no ball hit = value of the ball on (5)',()=>eq(FV(clearance(3),null),5));
t('3.11(a)','clearance: yellow 4 (minimum), green 4, brown 4, blue 5, pink 6, black 7',()=>eq([0,1,2,3,4,5].map(i=>FV(clearance(i),null)),[4,4,4,5,6,7]));
t('3.11(b)(iv)','red on, blue hit first = 5; black hit first = 7',()=>eq([FV(newFrame(0),'blue'),FV(newFrame(0),'black')],[5,7]));
t('3.11(b)(iii)','ball not on pocketed: red on, pink potted = 6',()=>eq(FV(newFrame(0),'red',['pink']),6));
t('3.11(c)','two balls hit together: the higher value counts (blue+black = 7)',()=>eq(FV(newFrame(0),'black',['blue']),7));
t('3.11(d)(vi)','after a red, foul before a colour is nominated = 7',()=>{const S=newFrame(0);applyPot(S,{b:'red'});return eq(FV(S,null),7)});
t('3.11(a)/(b)','after a red, colour nominated: yellow = 4 (minimum), blue = 5, black = 7',()=>{const S=newFrame(0);applyPot(S,{b:'red'});return eq([FV(S,null,[],'yellow'),FV(S,null,[],'blue'),FV(S,null,[],'black')],[4,5,7])});
t('3.11(d)(iii)','playing at reds in successive strokes = 7',()=>{const S=newFrame(0);applyPot(S,{b:'red'});return eq(FV(S,'red',[],'yellow'),7)});
t('3.11(d)','other seven-point fouls (measuring, ball off the table...) = 7',()=>eq(FV(newFrame(0),null,[],null,null,true),7));
t('3.11','penalty points go to the opponent, not into the striker break',()=>{const S=run([{k:'foul',pots:[{b:'red'},{b:'black'}],hit:null,potted:[],type:'miss'}]);return eq([S.sc,S.st[0].hb],[[8,4],8])});

// ---- Rule 12: free ball ----
t('3.12(a)(ii)(c)','free ball potted with red on: scores the value of the ball on (1), next ball on is a colour',()=>{const S=newFrame(0);S.free=true;applyPot(S,{b:'pink',f:true});return eq([S.sc[0],S.phase,S.reds],[1,'colour',15])});
t('3.12(c)','free ball potted with blue on: scores 5 and the ball on stays on the table',()=>{const S=clearance(3);S.free=true;applyPot(S,{b:'black',f:true});return eq([S.sc[0],S.ci],[5,3])});
t('3.12(d)','ball on potted instead of the free ball: scores its own value, free ball option ends',()=>{const S=newFrame(0);S.free=true;applyPot(S,{b:'red'});return eq([S.sc[0],S.free],[1,false])});
t('3.12(e)','free ball and a colour on both potted: only the ball on scores',()=>{const S=clearance(2);S.free=true;applyPot(S,{b:'black',f:true});applyPot(S,{b:'brown',w:1});return eq(S.sc[0],4)});
t('3.12(e)','free ball and a red both potted: each is scored',()=>{const S=newFrame(0);S.free=true;applyPot(S,{b:'black',f:true});applyPot(S,{b:'red'});return eq(S.sc[0],2)});
t('3.12','free ball awarded after a foul goes to the incoming player',()=>{const S=run([{k:'foul',pots:[],type:'miss',free:true}]);return eq([S.turn,S.free],[1,true])});
t('3.12(f)','free ball is void if the offender is asked to play again',()=>{const S=run([{k:'foul',pots:[],type:'wrong',free:true,again:true}]);return eq([S.turn,S.free],[0,false])});
t('3.12','no free ball possible when only the black is left',()=>{const S=clearance(5,[60,0]);S.turn=0;foul(S,{type:'miss',free:true});return eq(S.free,false)});

// ---- Rule 13 / 14: foul and a miss ----
t('3.14(b)','foul and a miss, balls replaced: offender plays again, reds potted on the stroke go back',()=>{const S=run([{k:'foul',pots:[],hit:null,potted:['red'],type:'miss',again:true}]);return eq([S.turn,S.reds,S.sc],[0,15,[0,4]])});
t('3.14(b)(iii)','replaced after a red: ball on stays a colour of the striker choice',()=>{const S=run([{k:'foul',pots:[{b:'red'}],hit:null,potted:[],type:'miss',again:true}]);return eq([S.phase,S.turn],['colour',0])});
t('3.14(d)(ii)','third failure from the original position (clear path) forfeits the frame; fewer does not',()=>{const m={k:'foul',pots:[],type:'miss',again:true,clear:true};const a=run([m,m]),b=run([m,m,m]);return eq([a.over,b.over,b.winner],[false,true,1])});
t('3.14(d)','misses without a clear path never forfeit',()=>{const m={k:'foul',pots:[],type:'miss',again:true,clear:false};const a=run([m,m,m,m,m]);return eq(a.over,false)});
t('3.14(d)(iii)','asked to play from the position left: the sequence ends',()=>{const m={k:'foul',pots:[],type:'miss',again:true,clear:true};const S=run([m,m,{k:'foul',pots:[],type:'miss',again:false},m]);return eq([S.over,S.missRun[0]+S.missRun[1]],[false,1])});

// ---- Rule 1(f), 17 ----
t('3.1(f)(ii)','conceded frame goes to the opponent, scores kept',()=>{const S=run([{k:'turn',pots:[{b:'red'}]},{k:'concede',p:1,pots:[]}]);return eq([S.over,S.winner,S.sc],[true,0,[1,0]])});
// ---- reds / points left ----
t('3.1(e)','points left: 147 at the start; after a red the player at the table has 7 more than the opponent',()=>{const S=newFrame(0);applyPot(S,{b:'red'});const Q=clone(S);fixPhase(Q);return eq([remaining(newFrame(0)),remaining(S),remaining(Q)],[147,146,139])});
t('3.1(e)','points left in the clearance = sum of the colours still on',()=>eq([remaining(clearance(0)),remaining(clearance(3)),remaining(clearance(5))],[27,18,7]));

// ---- Rule 7: spotting colours (UI helper) ----
const R=(balls,taken,placed)=>({balls,i:0,taken:taken||[],placed:placed||{},undo:false});
t('3.7','colour spotted on its own spot when free',()=>eq(respotOffer(R(['green'])),{spot:'green',own:true}));
t('3.7(e)','own spot occupied: highest value spot available',()=>eq(respotOffer(R(['green'],['green'])),{spot:'black'}));
t('3.7(e)','highest spot also taken: next highest',()=>eq(respotOffer(R(['green'],['green','black','pink'])),{spot:'blue'}));
t('3.7(f)','several colours: highest value is spotted first',()=>{startRespot(['yellow','black','green'],clone(newFrame(0)),'foul');return eq(ui.respot.balls,['black','green','yellow'])});
t('3.7(f)','second colour whose own spot was used by the first one is offered another spot',()=>eq(respotOffer({balls:['black','pink'],i:1,taken:['black'],placed:{black:'pink'},undo:false}),{spot:'blue'}));
t('3.7(g)(h)','all spots occupied: place as near to its own spot as possible',()=>eq(respotOffer(R(['yellow'],['yellow','green','brown','blue','pink','black'])),{close:true}));

// ---- breaks and stats ----
t('stats','break of 30+, 50+ counted once per break; fouls are not part of a break',()=>{const p=[];for(let i=0;i<4;i++)p.push({b:'red'},{b:'black'});const S=run([{k:'turn',pots:p},{k:'turn',pots:[]},{k:'foul',pots:[],type:'miss'}]);return eq([S.st[0].hb,S.st[0].b30,S.st[0].b50],[32,1,0])});
JSON.stringify(T)
""")
res=json.loads(c.eval("JSON.stringify(T)"))
bad=[r for r in res if not r[2]]
for r in res:print(('PASS' if r[2] else 'FAIL'),r[0].ljust(14),r[1],('' if r[2] else ' -> '+r[3]))
print(len(res)-len(bad),'passed,',len(bad),'failed')
print('errs',c.eval("JSON.stringify(errs)"))
