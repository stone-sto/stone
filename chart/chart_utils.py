# -*- encoding:utf-8 -*-

from pychartdir import *

# 默认的存储目录
default_path = '/Users/wgx/workspace/python/stone/1v_stone/result'

# 不同颜色, 画线的时候直接用就行, 先准备5个, 以后不够再加
default_colors = [0xff0000, 0x008800, 0x3333ff, 0x1ad145, 0xff9500]

# 买入和卖出标记的颜色, 买入, 蓝色, 卖出, 红色
buy_color = 0x478fe0
sell_color = 0xff5656


def draw_line_chart(horizontal_grid_name, values, line_names, line_colors, title, horizontal_name='', vertical_name='',
                    output_dir=None, opt_points=None):
    """
    画折线图
    :param opt_points: 操作的位置, 买入画B, 卖出画S, 坐标单位必须是horizontal_grid_name, values[0], type
    :type opt_points: list[tuple[str|float]]
    :param output_dir: 输出的目录
    :type output_dir: str
    :param line_colors: 折线的颜色, 必须与len(values)相等
    :type line_colors: list[int]
    :param line_names: 折线的名称, 长度必须与len(values)相等
    :type line_names: list[str]
    :param horizontal_grid_name: 水平方向的分割单元的名称, 长度必须len(values[i])相等
    :type horizontal_grid_name: list
    :param values: 数据, 格式list[list[float]]
    :type values:list[list[float]]
    :param horizontal_name: 水平坐标轴的名称
    :type horizontal_name: str
    :param vertical_name:垂直坐标轴的名称
    :type vertical_name:str
    :param title:图的标题
    :type title:str
    :return:图的存放路径
    :rtype:str
    """

    # Create an XYChart object of size 600 x 300 pixels, with a light blue (EEEEFF) background, black
    # border, 1 pxiel 3D border effect and rounded corners
    c = XYChart(1200, 600, 0xeeeeff, 0x000000, 1)
    c.setRoundedFrame()

    # Set the plotarea at (55, 58) and of size 520 x 195 pixels, with white background. Turn on both
    # horizontal and vertical grid lines with light grey color (0xcccccc)
    c.setPlotArea(55, 58, 1100, 490, 0xffffff, -1, -1, 0xcccccc, 0xcccccc)

    # Add a legend box at (50, 30) (top of the chart) with horizontal layout. Use 9pt Arial Bold font.
    # Set the background and border color to Transparent.
    c.addLegend(50, 30, 0, "arialbd.ttf", 9).setBackground(Transparent)

    # Add a title box to the chart using 15pt Times Bold Italic font, on a light blue (CCCCFF)
    # background with glass effect. white (0xffffff) on a dark red (0x800000) background, with a 1 pixel
    # 3D border.
    c.addTitle(title, "timesbi.ttf", 15).setBackground(0xccccff, 0x000000,
                                                       glassEffect())

    # Add a title to the y axis
    c.yAxis().setTitle(vertical_name)

    # Set the labels on the x axis.
    c.xAxis().setLabels(horizontal_grid_name)

    # Display 1 out of 3 labels on the x-axis.
    c.xAxis().setLabelStep(len(values[0]) / 40)

    # Add a title to the x axis
    c.xAxis().setTitle(horizontal_name)

    # Add a line layer to the chart
    layer = c.addLineLayer2()

    # Set the default line width to 2 pixels
    layer.setLineWidth(2)

    # Add the three data sets to the line layer. For demo purpose, we use a dash line color for the last
    # line
    for index in range(0, len(values)):
        # layer.addDataSet(data2, c.dashLineColor(0x3333ff, DashLine), "Server #3")
        layer.addDataSet(values[index], line_colors[index], line_names[index])

    if output_dir:
        output_path = os.path.join(os.path.join(output_dir, title.replace(' ', '_') + '.png'))
    else:
        output_path = os.path.join(os.path.join(default_path, title.replace(' ', '_') + '.png'))

    c.makeChart(output_path)

    # 加上opt点位
    if opt_points:
        for opt_point in opt_points:
            if opt_point[2] == 0:
                c.addText(c.getXCoor(opt_point[0]), c.getYCoor(opt_point[1]), 'B', "timesbi.ttf", 9, buy_color)
            elif opt_point[2] == 1:
                c.addText(c.getXCoor(opt_point[0]), c.getYCoor(opt_point[1]), 'S', "timesbi.ttf", 9, sell_color)

    c.makeChart(output_path)


if __name__ == '__main__':
    # The data for the line chart
    data0 = [42, 49, 33, 38, 51, 46, 29, 41, 44, 57, 59, 52, 37, 34, 51, 56, 56, 60, 70, 76, 63, 67, 75,
             64, 51]
    data1 = [50, 55, 47, 34, 42, 49, 63, 62, 73, 59, 56, 50, 64, 60, 67, 67, 58, 59, 73, 77, 84, 82, 80,
             84, 98]
    data2 = [36, 28, 25, 33, 38, 20, 22, 30, 25, 33, 30, 24, 28, 15, 21, 26, 46, 42, 48, 45, 43, 52, 64,
             60, 70]

    labels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
              "16", "17", "18", "19", "20", "21", "22", "23", "24"]
    draw_line_chart(labels, [data0, data1, data2], ['1', '2', '3'], default_colors[0:3], 'test',
                    opt_points=[('5', 33, 0), ])
