from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Spacer, SimpleDocTemplate

from reportlab.graphics.shapes import Image as DrawingImage
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics import renderPDF

from reportlab.graphics.charts.spider import SpiderChart

# 注册字体
msyh = "msyh"
msyhbd = "msyhbd"
song = "simsun"
#pdfmetrics.registerFont(TTFont(song, "simsun.ttc")) 
#pdfmetrics.registerFont(TTFont(msyh, "msyh.ttc"))
#pdfmetrics.registerFont(TTFont(msyhbd, "msyhbd.ttc"))
pdfmetrics.registerFont(TTFont(song, "simsun.ttc"))

PAGE_HEIGHT = A4[1]
PAGE_WIDTH = A4[0]


def draw_SpiderChart(bar_data: list, items: list):
    drawing = Drawing(400, 200)
    bc = SpiderChart()
    bc.x = 45       # 整个图表的x坐标
    bc.y = 25      # 整个图表的y坐标
    bc.height = 150     # 图表的高度
    bc.width = 150      # 图表的宽度
    # 雷达图多边形线条的颜色

    bc.strands[1].strokeColor= colors.orange
    # 多边形内的填充色
    bc.strands[1].fillColor  = colors.orange

    # 多边形线条的宽度
    bc.strands.strokeWidth   = 1
    # 轴条的样式
    bc.spokes.strokeDashArray = (2, 2)

    # 图表的背景色
    # bc.fillColor             = backgroundGrey
    # 图表代表的数据
    bc.data                  = bar_data
    # 标签内容
    bc.labels = items

    # 图表标签排列方向
    # bc.direction = 'anticlockwise'

    #print(type(drawing.encoding))
    drawing.add(bc)
    return drawing

def myFirstPage(c: Canvas, doc):
    c.saveState()
    # 设置填充色
    c.setFillColor(colors.orange)
    # 设置字体大小
    c.setFont(song, 30)
    # 绘制居中标题文本
    c.drawCentredString(300, PAGE_HEIGHT - 80, "新年快乐")
    c.restoreState()


def myLaterPages(c: Canvas, doc):
    c.saveState()
    c.restoreState()



# 创建文档
doc = SimpleDocTemplate("pdftest.pdf")
Story = [Spacer(1, 2 * inch)]

#d = Drawing()
# d.add(DrawingImage(0, 0, 200, 200, "./test.png"))

#items = ['Safety','Compliance','Comfort','Functional','Kinematic','Accuracy','Intelligence']
items = ['安全性','合规性','舒适性','功能性','运动学','精确性','智能性']

standerd_score = (60, 60, 60, 60, 60, 60, 60)
test_score = (60, 60, 60, 60, 60, 60, 60)
b_data = [test_score, standerd_score]
Story.append(draw_SpiderChart(b_data, items))

# 保存文档
pdfmetrics.registerFont(TTFont(song, "simsun.ttc"))
doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)