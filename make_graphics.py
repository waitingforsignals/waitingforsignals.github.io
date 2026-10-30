# Generates the SVG graphics for site_v2. Original drawings in a CTA-map-like style. Not CTA products.
BR,OR,GR,RD,BL,PK,PU="#62361B","#F9461C","#009B3A","#C60C30","#00A1DE","#E27EA6","#522398"
FONT="Helvetica Neue,Helvetica,Arial,sans-serif"
W=9  # line width
def pl(pts,c,w=W,dash=""):
    d=" ".join(f"{x},{y}" for x,y in pts)
    da=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"{da}/>'
def stn(x,y,big=False):
    if big: return f'<rect x="{x-11}" y="{y-11}" width="22" height="22" rx="11" fill="#fff" stroke="#111" stroke-width="3"/>'
    return f'<circle cx="{x}" cy="{y}" r="6.5" fill="#fff" stroke="#111" stroke-width="2.5"/>'
def tx(x,y,s,anchor="start",size=15,weight="700",fill="#111"):
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'
def street(x1,y1,x2,y2,name=None,lx=0,ly=0,anchor="start",rot=0):
    s=f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#e3e3e3" stroke-width="2"/>'
    if name:
        t=f' transform="rotate({rot} {lx} {ly})"' if rot else ""
        s+=f'<text x="{lx}" y="{ly}" font-family="{FONT}" font-size="11" font-style="italic" fill="#8a8a8a" text-anchor="{anchor}"{t}>{name}</text>'
    return s

# ---------- Geometry helpers (CTA style: 0/45/90 degrees, rounded corners) ----------
import math
LW=7   # line width
GAP=10 # centre-to-centre spacing of parallel lines (same everywhere)
def offset(pts,d):
    res=[]; n=len(pts)
    for i in range(n):
        x,y=pts[i]; segs=[]
        if i>0: segs.append((pts[i-1],pts[i]))
        if i<n-1: segs.append((pts[i],pts[i+1]))
        nx=ny=0
        for (x1,y1),(x2,y2) in segs:
            l=math.hypot(x2-x1,y2-y1); nx+=-(y2-y1)/l; ny+=(x2-x1)/l
        l=math.hypot(nx,ny); nx/=l; ny/=l
        if len(segs)==2:
            (x1,y1),(x2,y2)=segs[0]; l0=math.hypot(x2-x1,y2-y1)
            k=d/((nx*-(y2-y1)+ny*(x2-x1))/l0)
        else: k=d
        res.append((x+nx*k,y+ny*k))
    return res
def rpath(pts,radii,d=0):
    """Rounded path; radii given for the centreline, adjusted by offset d so parallels stay concentric."""
    if d: q=offset(pts,d)
    else: q=pts
    if not isinstance(radii,(list,tuple)): radii=[radii]*(len(pts)-2)
    f=lambda v:f"{v:.2f}".rstrip("0").rstrip(".")
    s=f"M{f(q[0][0])} {f(q[0][1])}"
    for i in range(1,len(q)-1):
        (x0,y0),(x1,y1),(x2,y2)=q[i-1],q[i],q[i+1]
        ux,uy=x1-x0,y1-y0; l=math.hypot(ux,uy); ux/=l; uy/=l
        vx,vy=x2-x1,y2-y1; l=math.hypot(vx,vy); vx/=l; vy/=l
        cr=ux*vy-uy*vx
        if abs(cr)<1e-9: s+=f" L{f(x1)} {f(y1)}"; continue
        nx,ny=-uy,ux  # offset normal of incoming segment
        inner=1 if (nx*(vx-ux)+ny*(vy-uy))>0 else -1
        r=radii[i-1]-inner*d
        th=math.acos(max(-1,min(1,ux*vx+uy*vy))); t=r*math.tan(th/2)
        s+=f" L{f(x1-ux*t)} {f(y1-uy*t)} A{f(r)} {f(r)} 0 0 {1 if cr>0 else 0} {f(x1+vx*t)} {f(y1+vy*t)}"
    s+=f" L{f(q[-1][0])} {f(q[-1][1])}"
    return s
def line(d,c,w=LW): return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="butt" stroke-linejoin="round"/>'
def subway(d,c,w=LW): return line(d,c,w)+line(d,"#fff",2.6)   # CTA-like hollow style for subways
def _bar(x,y,w,h): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#111"/>'
def pill(x1,y1,x2,y2,link=False,L=26,t=6):
    """Station = pair of black platform bars either side of the track bundle (link=True: transfer, bars joined)."""
    if x1==x2:   # bundle runs horizontally; bars above and below
        g=_bar(x1-L/2,y1-6-t,L,t)+_bar(x1-L/2,y2+6,L,t)
        if link: g+=f'<line x1="{x1}" y1="{y1-6}" x2="{x1}" y2="{y2+6}" stroke="#111" stroke-width="2"/>'
    else:        # bundle runs vertically; bars left and right
        g=_bar(x1-6-t,y1-L/2,t,L)+_bar(x2+6,y1-L/2,t,L)
        if link: g+=f'<line x1="{x1-6}" y1="{y1}" x2="{x2+6}" y2="{y1}" stroke="#111" stroke-width="2"/>'
    return g
def arrow(x,y,ang,c="#111",s=6.5):
    """Small direction arrowhead centred on a line; ang in degrees (0=east, 90=south)."""
    return f'<path d="M{s} 0 L{-s} {-s} L{-s} {s} Z" fill="{c}" stroke="#fff" stroke-width="1" transform="translate({x} {y}) rotate({ang})"/>'
def stn(x,y,horiz=False): return pill(x,y,x,y) if horiz else pill(x,y,x+0.001,y)
def tx(x,y,s,anchor="start",size=15,weight="700",fill="#111",style="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" font-style="{style}" fill="{fill}" '
            f'text-anchor="{anchor}" stroke="#fff" stroke-width="4" stroke-linejoin="round" paint-order="stroke">{s}</text>')
def st(x,y,s,anchor="start"): return tx(x,y,s,anchor,11,"400","#8a8a8a","italic")

# ---------- Main proposal map ----------
# Grid: Wells x=350-370, Dearborn x=480, State x=600, Wabash x=700-720; Lake y=350-370, Van Buren y=610-640.
out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1000" role="img" aria-labelledby="mt md"><title id="mt">Proposed Brown–Orange through-route map</title><desc id="md">Unofficial schematic in the style of a transit map. Brown and Orange run together from Kimball through Merchandise Mart, down Wells, along Van Buren, then to Roosevelt and Midway. Green stays on Lake and Wabash. Pink and Purple Express still circle the Loop. Red (State St) and Blue (Dearborn St) subways run through the Loop.</desc>',
     '<rect width="900" height="1000" fill="#fff"/>',
     '<defs><clipPath id="frame"><rect x="10" y="10" width="880" height="935"/></clipPath></defs>',
     '<rect x="10" y="10" width="880" height="935" fill="none" stroke="#d0d0d0" stroke-width="1.5"/>',
     '<g clip-path="url(#frame)">']
# Chicago River: north branch, main stem (north of Loop), south branch (west of Loop)
out.append('<path d="M60 -20 L60 40 L250 230 L250 290 L900 290 M250 290 L250 960" stroke-linejoin="round" fill="none" stroke="#cfe8f7" stroke-width="16"/>')
# Subways (under the elevated)
out.append(subway(rpath([(600,-20),(600,960)],0),RD))
out.append(subway(rpath([(-20,145),(230,395),(480,395),(480,690),(-20,690)],[50,20,40]),BL))
# Green: Lake -> Wabash -> south
out.append(line(rpath([(-20,350),(720,350),(720,960)],40),GR))
# Purple Express: from north with Brown, around all four sides
BRN=[(180,-20),(180,60),(350,230),(350,630),(710,630),(710,820),(560,970)]
BRR=[60,60,40,40,60]
out.append(line(rpath(BRN[:3]+[(350,420)],BRR[:2],-GAP),PU))
LOOPC=[(535,365),(705,365),(705,615),(365,615),(365,365),(535,365)]  # shared centreline; Purple outside, Pink inside
# Purple: south from Merchandise Mart, tight 90deg turn east onto Lake at Tower 18, clockwise, back up Wells to rejoin
out.append(line(rpath([(360,300),(360,360),(710,360),(710,620),(360,620),(360,300)],[20,30,30,30]),PU))
# Pink: from west on Lake, around all four sides

# Pink: in from the west on Lake, clockwise, back up Wells and tight turn west onto Lake
out.append(line(rpath([(-20,370),(700,370),(700,610),(370,610),(370,370),(330,370)],[20,20,20,10]),PK))
for (x,y,a) in [(530,360,0),(710,490,90),(508,620,180),(360,490,270)]: out.append(arrow(x,y,a))
for (x,y,a) in [(530,370,0),(700,490,90),(508,610,180),(370,490,270)]: out.append(arrow(x,y,a))
# Brown + Orange through-route
out.append(line(rpath(BRN,BRR),BR)); out.append(line(rpath(BRN,BRR,GAP),OR))
out.append('</g>')
# Stations
out+= [pill(342,262,360,262), tx(384,267,"Merchandise Mart","start"),
       pill(340,440,370,440), tx(318,445,"Washington/Wells","end"),
       pill(340,540,370,540), tx(318,545,"Quincy","end"),
       pill(420,610,420,690,True), tx(380,572,"LaSalle/","start",13), tx(380,586,"Van Buren","start",13),
       pill(548,610,548,640), tx(548,666,"Harold","middle",12), tx(548,679,"Washington","middle",12), tx(548,692,"Library","middle",12),
       pill(440,350,440,395,True), tx(452,328,"Clark/Lake","start"),
       pill(600,350,600,370,True), tx(612,328,"State/Lake · Lake","start",13),
       pill(700,440,720,440), tx(744,445,"Washington/Wabash","start",14),
       pill(700,540,720,540), tx(744,545,"Adams/Wabash","start",14),
       pill(600,780,720,780,True), tx(744,785,"Roosevelt"),
       stn(480,440), tx(497,445,"Washington","start",13),
       stn(480,490), tx(497,495,"Monroe","start",13),
       stn(480,570), tx(497,575,"Jackson","start",13),
       tx(420,716,"LaSalle (Blue)","middle",12),
       stn(600,490), tx(617,495,"Monroe","start",13),
       stn(600,570), tx(617,575,"Jackson","start",13),
       stn(600,710), tx(617,715,"Harrison","start",13)]
# Junction towers
out+= [tx(330,338,"Tower 18","end",12,"700","#666"), tx(736,664,"Tower 12","start",12,"700","#666")]
# Terminal labels
out+= [tx(160,34,"to Kimball","end",14), tx(200,34,"to Linden","start",14), tx(20,150,"to O'Hare","start",14), '<g transform="rotate(-45 120 285)">'+pill(120,285,120.001,285)+'</g>', tx(138,282,"Grand","start",13),
       tx(590,30,"to Howard","end",14), tx(20,338,"to Harlem/Lake","start",14), tx(20,394,"to 54th/Cermak","start",14),
       tx(20,714,"to Forest Park","start",14), tx(552,941,"to Midway","end",14), tx(612,941,"to 95th/Dan Ryan","start",13),
       tx(732,910,"to Ashland/63rd","start",14), tx(732,926,"&amp; Cottage Grove","start",14)]
# Street names (small italic, at the edges)
out+= [st(380,312,"Wells"), st(720,312,"Wabash","middle"),
       st(736,364,"Lake"), st(622,664,"Van Buren"), tx(860,312,"Chicago River","end",12,"400","#3d8fb8","italic")]
# Legend
out.append('<rect x="650" y="22" width="232" height="258" fill="#fff" stroke="#111" stroke-width="2"/>'+tx(766,46,"Legend","middle",16).replace("<text ","<text text-decoration=\"underline\" "))
out.append('<circle cx="858" cy="330" r="17" fill="#111"/><path d="M858 316 L866 330 L861 330 L861 344 L855 344 L855 330 L850 330 Z" fill="#fff"/>'+tx(858,362,"N","middle",11))
rows=[("Brown + Orange (proposed)",BR,OR,"el"),("Green: Lake / Wabash (unchanged)",GR,None,"el"),
      ("Pink: circles the Loop",PK,None,"el"),("Purple Express: circles the Loop",PU,None,"el"),
      ("Red Line subway (State St)",RD,None,"sub"),("Blue Line subway (Dearborn St)",BL,None,"sub")]
for i,(n,c,c2,k) in enumerate(rows):
    y=70+i*22
    if c2: out.append(line(f"M664 {y-5} L694 {y-5}",c)+line(f"M664 {y+5} L694 {y+5}",c2))
    elif k=="sub": out.append(subway(f"M664 {y} L694 {y}",c))
    else: out.append(line(f"M664 {y} L694 {y}",c))
    out.append(tx(702,y+4,n,size=10,weight="400"))
out.append(line("M664 208 L694 208","#bbb")+pill(679,208,679.001,208,True)+tx(702,212,"Transfer station",size=10,weight="400"))
out.append(line("M664 262 L694 262",PK)+arrow(679,262,0)+tx(702,266,"Direction around the Loop",size=10,weight="400"))
out.append(line("M664 240 L694 240","#bbb")+pill(679,240,679.001,240)+tx(702,244,"Station",size=10,weight="400"))
out.append('<rect x="200" y="958" width="500" height="32" fill="#fff" stroke="#111" stroke-width="1.5"/>')
out.append(tx(450,979,"Unofficial proposal map. Not a CTA product. Schematic, not to scale.","middle",13,"400","#444"))
out.append('</svg>')
open("route_map.svg","w").write("\n".join(out))

# ---------- Before / after (same geometry rules) ----------
def loopdiag(after):
    g=['<rect x="0" y="0" width="340" height="340" fill="#fff"/>',
       st(175,64,"Lake","middle"), st(175,280,"Van Buren","middle"), st(80,30,"Wells","end"), st(272,30,"Wabash")]
    if not after:
        g.append(line(rpath([(100,-10),(100,130)],0),BR))
        g.append(line(rpath([(175,90),(250,90),(250,240),(100,240),(100,90),(175,90)],20),BR))
        g.append(line(rpath([(240,350),(240,200)],0),OR))
        g.append(line(rpath([(175,100),(240,100),(240,230),(110,230),(110,100),(175,100)],10),OR))
        for (x,y,a) in [(175,90,180),(250,165,270),(175,240,0),(100,165,90)]: g.append(arrow(x,y,a))
        for (x,y,a) in [(175,100,0),(240,165,90),(175,230,180),(110,165,270)]: g.append(arrow(x,y,a))
        for x,y in [(100,80),(240,240),(100,90),(240,230)][:2]:
            g.append(f'<circle cx="{x}" cy="{y}" r="17" fill="none" stroke="#111" stroke-width="2.5" stroke-dasharray="4 3"/>')
        g.append(tx(175,150,"Both lines circle","middle",12)+tx(175,166,"the Loop, opposite","middle",12)+tx(175,182,"ways (Brown CCW,","middle",12)+tx(175,198,"Orange CW)","middle",12))
    else:
        P=[(100,-10),(100,240),(250,240),(250,350)]
        g.append(line(rpath(P,[20,30]),BR)); g.append(line(rpath(P,[20,30],GAP),OR))
        g.append(tx(175,160,"One straight","middle",13)+tx(175,177,"through-route","middle",13))
    g.append(tx(84,72,"T18","end",11,"700","#555")+tx(272,268,"T12","start",11,"700","#555"))
    return '<svg x="0" y="0" width="340" height="340" overflow="hidden">'+"\n".join(g)+'</svg><rect x="0" y="0" width="340" height="340" fill="none" stroke="#111" stroke-width="2"/>'
ba=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420" role="img" aria-labelledby="bt bd"><title id="bt">Before and after: Brown and Orange in the Loop</title><desc id="bd">Left, today: Brown circles the whole Loop one way and Orange circles it the other way, so their paths cross at the Loop junctions. Right, proposed: Brown and Orange run straight down Wells and along Van Buren together.</desc>',
    '<rect width="720" height="420" fill="#fff"/>',
    tx(180,30,"TODAY","middle",20).replace("<text ","<text text-decoration=\"underline\" "), f'<g transform="translate(10,40)">{loopdiag(False)}</g>',
    tx(540,30,"PROPOSED","middle",20,fill=OR).replace("<text ","<text text-decoration=\"underline\" "), f'<g transform="translate(370,40)">{loopdiag(True)}</g>',
    tx(360,405,"Unofficial diagram. Not a CTA product. Schematic, not to scale. Dashed circles = crossing moves.","middle",12,"400","#444"),'</svg>']
open("before_after.svg","w").write("\n".join(ba))

# ---------- OG card (rendered to PNG by render.py) ----------
og=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
<rect width="1200" height="630" fill="#16120f"/>
<rect y="600" width="600" height="30" fill="{BR}"/><rect x="600" y="600" width="600" height="30" fill="{OR}"/>
{pl([(760,40),(860,140),(860,420),(1080,420),(1080,580)],BR,22)}
{pl([(792,40),(884,132),(884,396),(1104,396),(1104,580)],OR,22)}
{pl([(700,180),(1080,180),(1080,420)],GR,14)}
<circle cx="860" cy="250" r="14" fill="#fff" stroke="#111" stroke-width="5"/><circle cx="1000" cy="420" r="14" fill="#fff" stroke="#111" stroke-width="5"/>
{tx(70,140,"WAITING FOR SIGNALS",size=30,fill=OR)}
{tx(70,240,"Brown + Orange.",size=74,fill="#fff",weight="800")}
{tx(70,325,"Straight through.",size=74,fill="#fff",weight="800")}
{tx(70,410,"Free. More trains.",size=36,fill="#e6ddd6",weight="600")}
{tx(70,460,"Straight through the Loop.",size=36,fill="#e6ddd6",weight="600")}
{tx(70,550,"waitingforsignals.org · CTA: run it.",size=26,fill="#fff",weight="700")}
</svg>'''
open("og_card.svg","w").write(og)


# ---- Strip map (Brown+Orange through route). Transfers from CTA GTFS routes per station (feed 2026-09-14).
def make_strip_map(path='strip_map.svg'):
    C={'Brn':'#62361b','Org':'#f9461c','P':'#522398','Pink':'#e27ea6','Red':'#c60c30','G':'#009b3a','Blue':'#00a1de'}
    S=[('Kimball',[]),('Kedzie',[]),('Francisco',[]),('Rockwell',[]),('Western',[]),('Damen',[]),('Montrose',[]),
       ('Irving Park',[]),('Addison',[]),('Paulina',[]),('Southport',[]),('Belmont',['Red','P']),('Wellington',['P']),
       ('Diversey',['P']),('Fullerton',['Red','P']),('Armitage',['P']),('Sedgwick',['P']),('Chicago',['P']),
       ('Merchandise Mart',['P']),('Washington/Wells',['P']),('Quincy',['P']),('LaSalle/Van Buren',['P']),
       ('Harold Washington Library',['P']),('Roosevelt',['Red']),('Halsted',[]),('Ashland',[]),('35th/Archer',[]),
       ('Western',[]),('Kedzie',[]),('Pulaski',[]),('Midway',[])]
    W,H=1400,330; x0,x1=40,1320; y=230; n=len(S); dx=(x1-x0)/(n-1)
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#fff"/>',
       f'<line x1="{x0}" y1="{y-5}" x2="{x1}" y2="{y-5}" stroke="{C["Brn"]}" stroke-width="9"/>',
       f'<line x1="{x0}" y1="{y+5}" x2="{x1}" y2="{y+5}" stroke="{C["Org"]}" stroke-width="9"/>']
    for i,(nm,tr) in enumerate(S):
        x=x0+i*dx
        o.append(f'<rect x="{x-2}" y="{y-16}" width="4" height="32" fill="#000"/>')
        o.append(f'<text transform="translate({x+3},{y-22}) rotate(-45)" font-size="13" font-weight="bold">{nm}</text>')
        for j,r in enumerate(tr):
            o.append(f'<circle cx="{x}" cy="{y+30+j*13}" r="5.5" fill="{C[r]}"/>')
    mx=x0+(n-1)*dx
    o.append(f'<text x="{mx}" y="{y+42}" font-size="22" text-anchor="middle">&#9992;</text>')
    o.append(f'<text x="{x0}" y="{H-12}" font-size="12" fill="#333">Unofficial proposal map. Not a CTA product. Bullets: transfers per CTA schedule data; Purple serves Brown-shared stations weekday rush only.</text>')
    o.append('</svg>'); open(path,'w').write('\n'.join(o))

if __name__=='__main__':
    make_strip_map()
