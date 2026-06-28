from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
import os

INPUT = '/mnt/data/qcc_ppt_v40_method_compliant_optimized.pptx'
OUTPUT = '/mnt/data/qcc_ppt_v41_format_hardened.pptx'
LOGO = '/mnt/data/ppt_unzip/ppt/media/image6.png'

prs = Presentation(INPUT)
W, H = prs.slide_width, prs.slide_height
FONT = 'Microsoft YaHei'
RED = RGBColor(210,8,45)
RED_DARK = RGBColor(159,0,1)
ORANGE = RGBColor(235,92,1)
BLUE = RGBColor(31,84,130)
GREEN = RGBColor(0,150,80)
BLACK = RGBColor(35,24,21)
GRAY = RGBColor(137,137,137)
MID_GRAY = RGBColor(221,221,221)
LIGHT_GRAY = RGBColor(246,246,246)
PINK = RGBColor(252,234,237)
WHITE = RGBColor(255,255,255)


def clear_slide(slide):
    spTree = slide.shapes._spTree
    for sp in list(spTree):
        if sp.tag.endswith('}nvGrpSpPr') or sp.tag.endswith('}grpSpPr'):
            continue
        spTree.remove(sp)


def set_run_font(run, size, bold=False, color=BLACK):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_text(slide, x,y,w,h,text,size=12,bold=False,color=BLACK,align=None,valign=None,margin=0.05):
    shp=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=shp.text_frame
    tf.word_wrap=True
    tf.margin_left=Inches(margin); tf.margin_right=Inches(margin)
    tf.margin_top=Inches(0.02); tf.margin_bottom=Inches(0.02)
    if valign: tf.vertical_anchor=valign
    tf.clear(); p=tf.paragraphs[0]
    p.text=text
    if align: p.alignment=align
    for r in p.runs: set_run_font(r,size,bold,color)
    return shp


def add_rect(slide,x,y,w,h,fill=WHITE,line=MID_GRAY,radius=True,width=0.8):
    shp=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    shp.fill.solid(); shp.fill.fore_color.rgb=fill
    shp.line.color.rgb=line; shp.line.width=Pt(width)
    return shp


def add_title(slide,title,subtitle,footer_no):
    bg=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,W,H)
    bg.fill.solid(); bg.fill.fore_color.rgb=WHITE; bg.line.fill.background()
    # v4.1: cap long titles to avoid full-width dominant title blocks
    add_text(slide,0.72,0.50,11.8,0.50,title,size=22,bold=True,color=BLACK)
    bar=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(0.72),Inches(1.18),Inches(0.95),Inches(0.035))
    bar.fill.solid(); bar.fill.fore_color.rgb=RED; bar.line.fill.background()
    if subtitle:
        add_text(slide,0.82,1.35,11.1,0.28,subtitle,size=10.5,color=GRAY)
    add_text(slide,0.58,6.95,0.45,0.2,str(footer_no),size=8.5,color=BLACK)
    add_text(slide,1.16,6.95,2.0,0.2,'Huawei Confidential',size=8.5,color=BLACK)
    if os.path.exists(LOGO):
        slide.shapes.add_picture(LOGO, Inches(11.2), Inches(6.86), width=Inches(1.42))


def add_callout(slide,label,text):
    y=6.05; x=0.72; w=12.0; h=0.58
    add_rect(slide,x,y,w,h,fill=WHITE,line=MID_GRAY,radius=True)
    lab=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(1.8),Inches(h))
    lab.fill.solid(); lab.fill.fore_color.rgb=RED; lab.line.fill.background()
    add_text(slide,x+0.08,y+0.17,1.6,0.21,label,size=11,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
    add_text(slide,x+2.08,y+0.17,w-2.35,0.24,text,size=10.8,color=BLACK)


def add_metric_card(slide,x,y,w,h,label,value,desc,color=RED):
    add_rect(slide,x,y,w,h,fill=WHITE,line=MID_GRAY,radius=True)
    strip=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(0.08),Inches(h))
    strip.fill.solid(); strip.fill.fore_color.rgb=color; strip.line.fill.background()
    add_text(slide,x+0.18,y+0.14,w-0.28,0.24,label,size=10.5,bold=True,color=color)
    add_text(slide,x+0.18,y+0.45,w-0.28,0.34,value,size=18,bold=True,color=BLACK)
    add_text(slide,x+0.18,y+0.88,w-0.28,h-0.95,desc,size=9.4,color=GRAY)


def set_cell(cell,text,size=10,bold=False,color=BLACK,fill=WHITE,align=PP_ALIGN.CENTER):
    cell.text=text
    cell.margin_left=Inches(0.04); cell.margin_right=Inches(0.04)
    cell.margin_top=Inches(0.03); cell.margin_bottom=Inches(0.03)
    cell.vertical_anchor=MSO_ANCHOR.MIDDLE
    cell.fill.solid(); cell.fill.fore_color.rgb=fill
    for p in cell.text_frame.paragraphs:
        p.alignment=align
        for r in p.runs:
            set_run_font(r,size,bold,color)


def add_simple_table(slide,x,y,w,h,data,col_widths=None,header_fill=PINK,font_size=10):
    rows,cols=len(data),len(data[0])
    shape=slide.shapes.add_table(rows,cols,Inches(x),Inches(y),Inches(w),Inches(h))
    table=shape.table
    if col_widths:
        for i,cw in enumerate(col_widths): table.columns[i].width=Inches(cw)
    for r in range(rows):
        for c in range(cols):
            fill=header_fill if r==0 else (WHITE if r%2 else LIGHT_GRAY)
            if r==0:
                set_cell(table.cell(r,c),data[r][c],size=font_size+0.5,bold=True,color=RED,fill=fill)
            else:
                align=PP_ALIGN.LEFT if c==0 else PP_ALIGN.CENTER
                set_cell(table.cell(r,c),data[r][c],size=font_size,bold=False,color=BLACK,fill=fill,align=align)
    return shape


def add_score_bar(slide,x,y,label,score,total=20,color=RED):
    add_text(slide,x,y,2.8,0.22,label,size=10.2,bold=True,color=BLACK)
    add_rect(slide,x,y+0.34,3.05,0.18,fill=LIGHT_GRAY,line=LIGHT_GRAY,radius=True)
    fill_w=3.05*score/total
    rect=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y+0.34),Inches(fill_w),Inches(0.18))
    rect.fill.solid(); rect.fill.fore_color.rgb=color; rect.line.fill.background()
    add_text(slide,x+3.15,y+0.24,0.5,0.28,str(score),size=13,bold=True,color=color,align=PP_ALIGN.CENTER)


def rebuild_slide13(slide):
    clear_slide(slide)
    add_title(slide,'价值闭环：问题、目标、对策、效果同屏对齐','保留业务地图逻辑，但压缩表格密度，突出四项可汇报证据。',13)
    metrics=[
        ('质量边界','0','典型负载拒绝 / 自动化失败 / 错误',GREEN),
        ('响应速度','168ms','闭环扩容响应，分钟级转毫秒级',RED),
        ('资源效率','32%','低峰平均线程占用降低',ORANGE),
        ('审计能力','100%','调整证据可追溯',BLUE),
    ]
    for i,(l,v,d,c) in enumerate(metrics):
        add_metric_card(slide,0.86+i*3.05,1.95,2.72,1.28,l,v,d,c)
    # PDCA cards
    items=[
        ('P 现状','峰谷不均、阻塞不可预测、人工处理滞后',RED),
        ('D 对策','闭环控制、SafetyGate、Evidence、重建重放',ORANGE),
        ('C 验证','自动化测试、实验场景、风险关闭台账',BLUE),
        ('A 标准','流程、数据、测试、运维和 AI 模板沉淀',GREEN),
    ]
    for i,(t,b,c) in enumerate(items):
        x=0.86+i*3.05
        add_rect(slide,x,3.65,2.72,1.38,fill=WHITE,line=c,radius=True,width=1.0)
        add_text(slide,x+0.18,3.88,2.36,0.25,t,size=12,bold=True,color=c,align=PP_ALIGN.CENTER)
        add_text(slide,x+0.32,4.25,2.08,0.45,b,size=9.8,color=BLACK,align=PP_ALIGN.CENTER)
        if i<3:
            add_text(slide,x+2.85,4.18,0.26,0.2,'→',size=16,bold=True,color=GRAY,align=PP_ALIGN.CENTER)
    add_callout(slide,'闭环结论','本页只保留“指标证据 + PDCA 链路”，避免在正式汇报页堆叠多张小表。')


def rebuild_slide15(slide):
    clear_slide(slide)
    add_title(slide,'根因分析｜矩阵图','矩阵页只保留关键少数要因；评分可读、结论明确，避免大表压缩。',15)
    # Left: simplified matrix table
    data=[
        ['疑似原因','影响','频度','可控','证据','总分'],
        ['缺少采样-诊断-决策闭环','5','5','5','5','20'],
        ['人工经验调参滞后','5','4','4','5','18'],
        ['缺少 SafetyGate 门控','5','4','5','4','18'],
        ['调整过程不可审计','4','4','5','5','18'],
    ]
    add_simple_table(slide,0.82,1.95,7.35,3.35,data,col_widths=[2.75,0.82,0.82,0.82,0.82,1.32],font_size=10.2)
    # Right: visual ranking bars
    add_rect(slide,8.55,1.95,3.85,3.35,fill=WHITE,line=MID_GRAY,radius=True)
    add_text(slide,8.82,2.18,3.25,0.28,'关键要因排序',size=13,bold=True,color=RED,align=PP_ALIGN.CENTER)
    bars=[('闭环缺失',20,RED),('人工滞后',18,ORANGE),('安全门缺失',18,BLUE),('审计缺失',18,GREEN)]
    y=2.68
    for label,score,c in bars:
        add_score_bar(slide,8.82,y,label,score,color=c)
        y+=0.58
    add_text(slide,8.9,4.95,3.15,0.18,'保留：总分≥18 且有工程对策',size=9.2,color=GRAY,align=PP_ALIGN.CENTER)
    add_callout(slide,'矩阵结论','优先保留四类可行动要因：闭环缺失、人工滞后、安全门缺失、审计缺失；队列不可热改作为工程约束单独处理。')


def add_action_tile(slide,x,y,w,h,idx,what,why,who,when,where,color=RED):
    add_rect(slide,x,y,w,h,fill=WHITE,line=MID_GRAY,radius=True)
    badge=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(0.55),Inches(0.42))
    badge.fill.solid(); badge.fill.fore_color.rgb=color; badge.line.fill.background()
    add_text(slide,x+0.06,y+0.11,0.42,0.16,str(idx),size=9.5,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
    add_text(slide,x+0.72,y+0.13,w-0.90,0.24,what,size=12.0,bold=True,color=color)
    fields=[('Why',why),('Who',who),('When',when),('Where',where)]
    positions=[(x+0.62,y+0.60),(x+w/2+0.10,y+0.60),(x+0.62,y+1.02),(x+w/2+0.10,y+1.02)]
    fw=w/2-0.85
    for (k,v),(fx,fy) in zip(fields,positions):
        add_text(slide,fx,fy,0.55,0.16,k,size=8.8,bold=True,color=GRAY,align=PP_ALIGN.RIGHT)
        add_text(slide,fx+0.65,fy,fw-0.65,0.22,v,size=9.8,color=BLACK)


def rebuild_slide17(slide):
    clear_slide(slide)
    add_title(slide,'拟定对策｜5W','以 2×2 对策卡承载 5W，保留方法形式，同时提高正式汇报可读性。',17)
    actions=[
        ('构建采样-诊断-决策-执行闭环','解决人工响应滞后','架构设计','P1','治理核心链路',RED),
        ('引入 SafetyGate 安全门','避免误调、振荡和过度扩容','实验验证','P1','策略准入与执行前',ORANGE),
        ('建立 Evidence 证据链','保证调整可审计、可复盘','报告沉淀','P1-P2','before / command / after / audit',BLUE),
        ('实现 Executor 重建与任务重放','处理队列容量不可热改','开发实现','P2','队列治理链路',GREEN),
    ]
    coords=[(0.86,1.95),(6.76,1.95),(0.86,3.65),(6.76,3.65)]
    for i,(a,(x,y)) in enumerate(zip(actions,coords),1):
        add_action_tile(slide,x,y,5.55,1.28,i,*a)
    # small explicit method strip to make 5W visible for auditors
    add_rect(slide,0.86,5.25,11.45,0.42,fill=PINK,line=RED,radius=True,width=0.8)
    add_text(slide,1.05,5.36,11.05,0.15,'5W 字段已覆盖：What 做什么 / Why 为什么 / Who 谁负责 / When 何时 / Where 范围',size=9.8,bold=True,color=RED,align=PP_ALIGN.CENTER)
    add_callout(slide,'对策结论','每项对策均绑定原因、责任人、时间边界和实施范围，避免措施清单化。')


def rebuild_slide19(slide):
    clear_slide(slide)
    add_title(slide,'实施跟踪｜5W','实施页突出状态和证据，保留 5W 跟踪结构，避免空白大表。',19)
    data=[
        ('闭环控制链路','架构设计','已完成','采样 / 诊断 / 策略 / 执行','扩容响应 168ms',RED),
        ('SafetyGate 门控','实验验证','已完成','冷却 / 限额 / 方向阻断','40步 0反转',ORANGE),
        ('Evidence 审计','报告沉淀','已完成','commandId + JSONL','100% 可追溯',BLUE),
        ('质量门禁','测试建设','已完成','自动化验证','646 passed / 0 failed',GREEN),
    ]
    # header
    add_rect(slide,0.86,1.92,11.85,0.42,fill=PINK,line=RED,radius=False,width=0.8)
    heads=['What 实施项','Who 责任','When 节点','Where 范围','Status / Evidence']
    colx=[0.95,3.25,5.28,7.25,9.35]; widths=[2.1,1.75,1.65,1.85,2.85]
    for x,w,h in zip(colx,widths,heads): add_text(slide,x,2.03,w,0.17,h,size=9.8,bold=True,color=RED,align=PP_ALIGN.CENTER)
    y=2.47
    for idx,(what,who,when,where,evi,c) in enumerate(data):
        add_rect(slide,0.86,y,11.85,0.72,fill=WHITE if idx%2==0 else LIGHT_GRAY,line=MID_GRAY,radius=False,width=0.5)
        vals=[what,who,when,where,evi]
        for x,w,v in zip(colx,widths,vals):
            add_text(slide,x,y+0.22,w,0.22,v,size=10.2,bold=(v==when or v==evi),color=(c if v==evi else BLACK),align=PP_ALIGN.CENTER)
        y+=0.78
    add_callout(slide,'实施结论','实施跟踪显示关键对策均已完成验证，具备进入影子模式的基础条件。')

# apply selected repairs
rebuild_slide13(prs.slides[12])
rebuild_slide15(prs.slides[14])
rebuild_slide17(prs.slides[16])
rebuild_slide19(prs.slides[18])

prs.save(OUTPUT)
print(OUTPUT)
