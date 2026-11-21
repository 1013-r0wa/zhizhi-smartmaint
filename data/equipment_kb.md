# 智维知识库（模拟数据，仅供原型演示与评测）

## KB-001 主轴电机温度过高
- 案例编号：KB-001
- 标题EN：Spindle motor overheating
- 报警代码：ALM-2041
- 设备：M-003 数控车床
- 设备EN：M-003 CNC lathe
- 现象：主轴电机温度持续升高，超过报警阈值后触发 ALM-2041，加工中断
- 现象EN：Spindle motor temperature keeps rising and exceeds the alarm threshold, triggering ALM-2041 and interrupting machining
- 可能原因：1）冷却风扇故障或滤网堵塞，散热不足（概率 60%）；2）主轴轴承润滑不良或磨损（概率 25%）；3）温度传感器漂移误报（概率 15%）
- 可能原因EN：1) Cooling fan failure or clogged filter causing insufficient heat dissipation (probability 60%)；2) Poor spindle bearing lubrication or bearing wear (probability 25%)；3) Temperature sensor drift causing false alarms (probability 15%)
- 现场确认项：检查冷却风扇是否运转、滤网是否堵塞；查看轴承温升曲线；核对温度传感器数值是否合理
- 现场确认项EN：Check whether the cooling fan runs and the filter is clogged；Review the bearing temperature-rise curve；Verify the temperature sensor reading is reasonable
- 关联备件：FAN-2041
- 来源：《M-003 数控车床使用手册》第 4.2 节
- 来源EN：M-003 CNC Lathe Operation Manual, Section 4.2
- 高危：否

## KB-002 主轴伺服报警
- 案例编号：KB-002
- 标题EN：Spindle servo alarm
- 报警代码：ALM-1023
- 设备：M-003 数控车床
- 设备EN：M-003 CNC lathe
- 现象：主轴启动即报 ALM-1023，主轴无法旋转，重启后偶发复现
- 现象EN：ALM-1023 occurs immediately after spindle start, the spindle cannot rotate, and the alarm reappears occasionally after restart
- 可能原因：1）编码器反馈线缆松动或屏蔽层破损（概率 65%）；2）伺服驱动器过流保护误触发（概率 25%）；3）主轴电机编码器故障（概率 10%）
- 可能原因EN：1) Encoder feedback cable loose or shield damaged (probability 65%)；2) Servo drive over-current protection falsely triggered (probability 25%)；3) Spindle motor encoder failure (probability 10%)
- 现场确认项：检查编码器插头是否锁紧；检查线缆有无破损；观察驱动器面板电流显示值
- 现场确认项EN：Check whether the encoder connector is locked；Inspect the cable for damage；Observe the current reading on the drive panel
- 关联备件：ENC-1023
- 来源：《M-003 数控车床使用手册》第 4.2 节
- 来源EN：M-003 CNC Lathe Operation Manual, Section 4.2
- 高危：否

## KB-003 液压压力低
- 案例编号：KB-003
- 标题EN：Low hydraulic pressure
- 报警代码：ALM-3105
- 设备：M-008 液压站
- 设备EN：M-008 hydraulic station
- 现象：液压系统压力低于设定值，报警 ALM-3105，油压无法上升
- 现象EN：Hydraulic system pressure is below the set value with alarm ALM-3105, and the oil pressure cannot build up
- 可能原因：1）液压油位不足或油质劣化（概率 55%）；2）液压泵磨损，输出流量下降（概率 30%）；3）溢流阀卡滞或调定值漂移（概率 15%）
- 可能原因EN：1) Insufficient hydraulic oil level or degraded oil quality (probability 55%)；2) Worn hydraulic pump with reduced output flow (probability 30%)；3) Relief valve stuck or setpoint drift (probability 15%)
- 现场确认项：检查油箱油位与油质；听泵运转有无异响；检查压力表读数与溢流阀状态
- 现场确认项EN：Check oil tank level and oil quality；Listen for abnormal pump noise；Check the pressure gauge reading and relief valve status
- 关联备件：HP-3105、RV-3105
- 来源：《M-008 液压站维护手册》第 3.1 节
- 来源EN：M-008 Hydraulic Station Maintenance Manual, Section 3.1
- 高危：否

## KB-004 刀库换刀超时
- 案例编号：KB-004
- 标题EN：Tool change timeout
- 报警代码：ALM-4102
- 设备：M-011 加工中心
- 设备EN：M-011 machining center
- 现象：自动换刀超过设定时间，报警 ALM-4102，刀库停在中途位置
- 现象EN：Automatic tool change exceeds the set time with alarm ALM-4102, and the tool magazine stops midway
- 可能原因：1）刀套定位销磨损或卡滞（概率 70%）；2）换刀臂原点信号异常（概率 20%）；3）气源压力不足（概率 10%）
- 可能原因EN：1) Tool sleeve locating pin worn or stuck (probability 70%)；2) Tool change arm home signal abnormal (probability 20%)；3) Insufficient air supply pressure (probability 10%)
- 现场确认项：检查刀套定位销磨损情况；核对换刀臂原点信号；检查气源压力是否达到要求
- 现场确认项EN：Inspect the tool sleeve locating pin for wear；Verify the tool change arm home signal；Check whether the air supply pressure meets the requirement
- 关联备件：PIN-4102
- 来源：《M-011 加工中心维护手册》第 5.4 节
- 来源EN：M-011 Machining Center Maintenance Manual, Section 5.4
- 高危：否

## KB-005 进给轴伺服过载
- 案例编号：KB-005
- 标题EN：Feed axis servo overload
- 报警代码：ALM-5207
- 设备：M-015 立式加工中心
- 设备EN：M-015 vertical machining center
- 现象：进给轴运行中出现伺服过载报警 ALM-5207，轴停止运动
- 现象EN：Servo overload alarm ALM-5207 occurs while the feed axis is running, and the axis stops moving
- 可能原因：1）导轨润滑不足，摩擦阻力增大（概率 60%）；2）切削参数不当，负载超限（概率 25%）；3）丝杠预紧异常（概率 15%）
- 可能原因EN：1) Insufficient guideway lubrication increasing friction (probability 60%)；2) Improper cutting parameters causing excessive load (probability 25%)；3) Abnormal ball screw preload (probability 15%)
- 现场确认项：检查导轨润滑状态；复核切削参数；检查丝杠温升与预紧
- 现场确认项EN：Check guideway lubrication status；Review cutting parameters；Check ball screw temperature rise and preload
- 关联备件：LUB-5207
- 来源：《M-015 立式加工中心使用手册》第 6.1 节
- 来源EN：M-015 Vertical Machining Center Operation Manual, Section 6.1
- 高危：否

## KB-006 主轴异响与剧烈振动
- 案例编号：KB-006
- 标题EN：Spindle abnormal noise and severe vibration
- 报警代码：无
- 设备：M-003 数控车床
- 设备EN：M-003 CNC lathe
- 现象：主轴高速运转时剧烈抖动并伴随金属异响，振动值异常升高
- 现象EN：Severe vibration with metallic abnormal noise at high spindle speed, and the vibration value rises abnormally
- 可能原因：1）主轴轴承失效或保持架断裂（概率 50%）；2）刀具动平衡严重破坏（概率 30%）；3）主轴装配连接松动（概率 20%）
- 可能原因EN：1) Spindle bearing failure or cage fracture (probability 50%)；2) Severe tool dynamic imbalance (probability 30%)；3) Loose spindle assembly connection (probability 20%)
- 现场确认项：立即停机并上报，由具备资质的维修人员检查，严禁带病运行
- 现场确认项EN：Stop the machine immediately and report；Inspection must be performed by qualified maintenance personnel；Never run the machine with the fault
- 关联备件：待检查后确认
- 关联备件EN：To be confirmed after inspection
- 来源：《车间安全操作规程》第 2.3 节
- 来源EN：Workshop Safety Operating Procedures, Section 2.3
- 高危：是

## KB-007 电柜焦糊味与打火痕迹
- 案例编号：KB-007
- 标题EN：Burning smell and arcing marks in the electrical cabinet
- 报警代码：无
- 设备：车间配电柜
- 设备EN：Workshop distribution cabinet
- 现象：电柜内有焦糊味，可见打火痕迹，局部绝缘变色
- 现象EN：Burning smell inside the cabinet with visible arcing marks and locally discolored insulation
- 可能原因：1）接线端子松动过热（概率 55%）；2）接触器触头烧蚀（概率 30%）；3）电缆绝缘老化击穿（概率 15%）
- 可能原因EN：1) Loose terminal overheating (probability 55%)；2) Burnt contactor contacts (probability 30%)；3) Aged and punctured cable insulation (probability 15%)
- 现场确认项：立即断电挂牌，由持证电工检查，禁止带电作业
- 现场确认项EN：Power off immediately and attach a lockout tag；Inspection by a certified electrician；No live work
- 关联备件：待检查后确认
- 关联备件EN：To be confirmed after inspection
- 来源：《电气安全操作规程》第 3.2 节
- 来源EN：Electrical Safety Operating Procedures, Section 3.2
- 高危：是
