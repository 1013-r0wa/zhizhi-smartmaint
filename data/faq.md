# 智维问答库（模拟数据，仅供原型演示与评测）

## FAQ-001 冷却风扇多久需要清理一次？
- 所属案例：KB-001
- 问题EN：How often should the cooling fan be cleaned?
- 答案：建议每 500 运行小时或每月清理一次滤网，粉尘较大的车间缩短到每两周。清理时先断电挂牌，用低压压缩空气从内向外吹扫；滤网破损或风扇轴承异响时直接更换 FAN-2041。清理后空载运行 10 分钟，确认主轴温升回落。
- 答案EN：Clean the filter every 500 operating hours or monthly, and every two weeks in dusty workshops. Power off and lock out first, then blow with low-pressure compressed air from inside out. Replace FAN-2041 if the filter is damaged or the fan bearing is noisy. Run idle for 10 minutes after cleaning and confirm the spindle temperature rise drops.
- 依据：《M-003 数控车床使用手册》第 4.2 节
- 依据EN：M-003 CNC Lathe Operation Manual, Section 4.2

## FAQ-002 温度达到多少时需要立即停机？
- 所属案例：KB-001
- 问题EN：At what temperature should the machine be stopped immediately?
- 答案：知识库未给出统一温度数值，应以机床手册的报警设定值为准。一旦触发 ALM-2041，或在风扇与滤网确认正常后温度仍持续上升，就立即停机；不要通过调高报警阈值继续加工，停机后按 KB-001 的确认项检查轴承与温度传感器。
- 答案EN：The knowledge base does not define a universal temperature limit; use the alarm setpoint in the machine manual. Stop immediately once ALM-2041 is triggered, or if the temperature keeps rising after the fan and filter are verified. Do not raise the alarm threshold to keep machining; after stopping, check the bearing and sensor per KB-001.
- 依据：《M-003 数控车床使用手册》第 4.2 节
- 依据EN：M-003 CNC Lathe Operation Manual, Section 4.2

## FAQ-003 更换冷却风扇组件需要多长时间？
- 所属案例：KB-001
- 问题EN：How long does it take to replace the cooling fan assembly?
- 答案：备件 FAN-2041 当前库存 2 件，标准更换约 30 至 60 分钟，包含断电挂牌、拆装与试运行。若同时需要清理风道或更换滤网，建议预留 1 小时停机窗口，并由维修人员确认温升恢复正常后再开机。
- 答案EN：FAN-2041 has 2 units in stock. A standard replacement takes about 30-60 minutes, including lockout/tagout, removal and installation, and a test run. If the air duct or filter also needs cleaning, reserve a one-hour downtime window and restart only after maintenance personnel confirm the temperature rise is normal.
- 依据：《M-003 数控车床使用手册》第 4.2 节
- 依据EN：M-003 CNC Lathe Operation Manual, Section 4.2

## FAQ-004 如何判断是线缆松动还是编码器损坏？
- 所属案例：KB-002
- 问题EN：How can I tell whether the cable is loose or the encoder is faulty?
- 答案：先断电重新插拔并锁紧编码器插头，再轻轻弯折线缆，观察驱动器电流或报警是否跳变，跳变多为线缆或屏蔽层问题。若插头锁紧、线缆外观正常仍复现 ALM-1023，再用同型号备件替换编码器验证。线缆处理成本低，建议先查线缆。
- 答案EN：Power off, reseat and lock the encoder connector, then gently flex the cable while watching the drive current or alarm. A jump usually indicates a cable or shield problem. If ALM-1023 persists with the connector locked and the cable intact, swap in a known-good encoder to verify. Always check the cable first because it is the lower-cost fix.
- 依据：《M-003 数控车床使用手册》第 4.2 节
- 依据EN：M-003 CNC Lathe Operation Manual, Section 4.2

## FAQ-005 更换编码器线缆后需要重新校准吗？
- 所属案例：KB-002
- 问题EN：Is recalibration required after replacing the encoder cable?
- 答案：需要。更换编码器线缆后应执行回零与编码器偏置校准，并低速试运行确认主轴定位精度；校准完成前不要直接投入批量加工。具体步骤参照 M-003 手册的伺服调试章节，由电气维修人员执行。
- 答案EN：Yes. After replacing the encoder cable, perform homing and encoder offset calibration, then run at low speed to verify spindle positioning accuracy. Do not start batch machining before calibration. Follow the servo commissioning section of the M-003 manual and have an electrical technician perform it.
- 依据：《M-003 数控车床使用手册》第 4.2 节
- 依据EN：M-003 CNC Lathe Operation Manual, Section 4.2

## FAQ-006 报警重启后消失，可以继续加工吗？
- 所属案例：KB-002
- 问题EN：The alarm disappears after a restart. Can machining continue?
- 答案：不建议直接继续加工。偶发复现说明存在接触不良或干扰隐患，应按 KB-002 的确认项检查插头、线缆与驱动器面板电流，并记录复现条件。确认无异常后可低速试切一件，同时安排停机窗口更换 ENC-1023 备件。
- 答案EN：Continuing production directly is not recommended. An intermittent alarm indicates a loose connection or interference risk. Check the connector, cable and drive panel current per KB-002 and record the conditions that trigger it. After confirming no abnormality, run a single low-speed trial cut and schedule a downtime window to replace ENC-1023.
- 依据：《M-003 数控车床使用手册》第 4.2 节
- 依据EN：M-003 CNC Lathe Operation Manual, Section 4.2

## FAQ-007 液压油多久需要更换一次？
- 所属案例：KB-003
- 问题EN：How often should the hydraulic oil be changed?
- 答案：一般按 2000 运行小时或每年更换一次；油液出现乳化、明显变黑或含金属颗粒时立即更换。换油同时清洗吸油滤芯，并记录油位与油温。油质劣化正是 ALM-3105 的首要原因。
- 答案EN：Change the hydraulic oil every 2,000 operating hours or annually, and immediately if the oil is emulsified, visibly darkened or contains metal particles. Clean the suction filter during the change and record oil level and temperature. Degraded oil is the leading cause of ALM-3105.
- 依据：《M-008 液压站维护手册》第 3.1 节
- 依据EN：M-008 Hydraulic Station Maintenance Manual, Section 3.1

## FAQ-008 如何判断液压泵是否已经磨损？
- 所属案例：KB-003
- 问题EN：How can I tell whether the hydraulic pump is worn?
- 答案：结合三点判断：油位与油质正常但压力仍上不去；泵体有连续异响或温升明显；空载流量比出厂值下降超过 10%。满足两点即可怀疑泵磨损，可用压力表分段测压确认，必要时更换 HP-3105。
- 答案EN：Check three signs: pressure still will not build up with normal oil level and quality; continuous abnormal noise or obvious temperature rise at the pump; no-load flow more than 10% below the factory value. Two of these suggest pump wear. Confirm with sectional pressure tests and replace HP-3105 if necessary.
- 依据：《M-008 液压站维护手册》第 3.1 节
- 依据EN：M-008 Hydraulic Station Maintenance Manual, Section 3.1

## FAQ-009 关联备件库存为 0 时如何处理？
- 所属案例：KB-003
- 问题EN：What should I do when the related spare part is out of stock?
- 答案：系统显示 HP-3105 液压泵库存为 0，处于待采购状态，替代型号为 HP-3106。建议先按确认项排查油位、油质与溢流阀，避免误换泵；确需更换时提交紧急采购申请并走替代型号审批，工单标注缺件等待，不得虚报库存。
- 答案EN：HP-3105 is out of stock and marked for procurement; the substitute is HP-3106. First check oil level, oil quality and the relief valve per the checklist to avoid replacing the pump unnecessarily. If replacement is required, raise an urgent purchase request and approve the substitute model, and mark the work order as waiting for parts. Never report false stock.
- 依据：《M-008 液压站维护手册》第 3.1 节
- 依据EN：M-008 Hydraulic Station Maintenance Manual, Section 3.1

## FAQ-010 液压油添加方法
- 所属案例：KB-003
- 问题EN：How do I top up the hydraulic oil?
- 答案：停机泄压后清洁加油口周围，经滤油车或滤网加入同牌号液压油至油标中位，不要混用不同牌号。加注后空载运行 5 至 10 分钟排出空气，再复查油位与压力。油位不足是 ALM-3105 的常见诱因，加注前应先确认是否存在泄漏。
- 答案EN：Stop the machine and release pressure, clean around the filler port, then add the same grade of hydraulic oil through a filter cart or strainer up to the mid-level mark. Do not mix different oil grades. Run idle for 5-10 minutes to bleed air, then recheck oil level and pressure. Low oil level is a common cause of ALM-3105, so check for leaks before topping up.
- 依据：《M-008 液压站维护手册》第 3.1 节
- 依据EN：M-008 Hydraulic Station Maintenance Manual, Section 3.1

## FAQ-011 刀套定位销磨损后如何更换？
- 所属案例：KB-004
- 问题EN：How do I replace a worn tool sleeve locating pin?
- 答案：停机并切到手动模式，确认刀库停稳后手动盘车复位；拆下刀套固定螺栓，取出磨损定位销，检查销孔有无拉伤。更换 PIN-4102（库存 5 件）后按手册调整间隙，手动试换刀 3 至 5 次，自动运行前必须空刀试换。
- 答案EN：Stop the machine, switch to manual mode, and manually jog the magazine back into position. Remove the tool sleeve bolts, extract the worn pin and inspect the pin bore for scoring. Replace with PIN-4102 (5 in stock), adjust clearance per the manual, and manually test 3-5 tool changes. Always run an empty tool-change test before automatic operation.
- 依据：《M-011 加工中心维护手册》第 5.4 节
- 依据EN：M-011 Machining Center Maintenance Manual, Section 5.4

## FAQ-012 换刀臂原点信号异常如何排查？
- 所属案例：KB-004
- 问题EN：How do I troubleshoot an abnormal tool change arm home signal?
- 答案：在手动模式下观察换刀臂原点接近开关指示灯是否随动作变化；不变化时检查开关间隙、接线与铁屑遮挡，再用万用表测量信号通断。信号抖动多由间隙过大或线缆松动引起，调整后重新执行回原点。
- 答案EN：In manual mode, watch whether the tool change arm home proximity switch LED toggles with movement. If not, check the switch gap, wiring and chip contamination, then verify signal continuity with a multimeter. Signal chatter is usually caused by an excessive gap or loose wiring; re-home after adjustment.
- 依据：《M-011 加工中心维护手册》第 5.4 节
- 依据EN：M-011 Machining Center Maintenance Manual, Section 5.4

## FAQ-013 气源压力不足如何处理？
- 所属案例：KB-004
- 问题EN：How should insufficient air supply pressure be handled?
- 答案：先读气源压力表，确认是否低于机床要求；检查三联件滤杯积水、调压阀设定与管路快插是否漏气，排水并重新调压。压力恢复后手动试换刀，确认换刀时间回到正常范围，再恢复自动加工。
- 答案EN：Read the air pressure gauge and compare it with the machine requirement. Check the FRL unit bowl for water, the regulator setting and the quick couplings for leaks; drain water and reset the pressure. After recovery, test tool change manually and confirm the change time returns to normal before resuming automatic machining.
- 依据：《M-011 加工中心维护手册》第 5.4 节
- 依据EN：M-011 Machining Center Maintenance Manual, Section 5.4

## FAQ-014 导轨润滑油脂如何加注？
- 所属案例：KB-005
- 问题EN：How do I apply guideway lubricating grease?
- 答案：使用机床指定牌号的导轨润滑脂，先清洁油嘴，用黄油枪缓慢加注至旧脂被挤出为止，不要过量。加注后手动往复各轴 2 至 3 次并擦净多余油脂。润滑不足是 ALM-5207 的首要原因，建议按保养周期定检。
- 答案EN：Use the guideway grease specified for the machine. Clean the nipple, slowly pump grease until old grease is expelled, and avoid overfilling. Move each axis back and forth 2-3 times manually and wipe off excess grease. Insufficient lubrication is the leading cause of ALM-5207, so follow the maintenance interval.
- 依据：《M-015 立式加工中心使用手册》第 6.1 节
- 依据EN：M-015 Vertical Machining Center Operation Manual, Section 6.1

## FAQ-015 切削参数如何调整才能避免过载？
- 所属案例：KB-005
- 问题EN：How should cutting parameters be adjusted to avoid overload?
- 答案：优先降低进给速度或切深，单次调整不超过 20%，观察主轴负载表是否回落到 70% 以下，避免同时加大切深与进给。参数调整属于工艺范畴，须由工艺人员确认后执行，本系统不会直接写入机床参数。
- 答案EN：Reduce feed rate or depth of cut first, by no more than 20% per step, and check that spindle load falls below 70%. Do not increase depth of cut and feed at the same time. Parameter changes belong to process engineering and must be approved by process staff; this system never writes machine parameters.
- 依据：《M-015 立式加工中心使用手册》第 6.1 节
- 依据EN：M-015 Vertical Machining Center Operation Manual, Section 6.1

## FAQ-016 丝杠预紧异常需要返厂维修吗？
- 所属案例：KB-005
- 问题EN：Does abnormal ball screw preload require factory repair?
- 答案：不一定。先检查丝杠两端支撑轴承温升、联轴器同轴度与预紧螺母，若仅预紧力下降，可在现场按手册重新预紧；出现丝杠弯曲、滚道剥落或反向间隙超差时，才需要返厂或更换丝杠组件。
- 答案EN：Not necessarily. Check bearing temperature rise at both screw ends, coupling alignment and the preload nut. If only the preload has dropped, re-preload on site per the manual. Return to the factory or replace the screw assembly only when the screw is bent, the raceway spalls, or backlash exceeds tolerance.
- 依据：《M-015 立式加工中心使用手册》第 6.1 节
- 依据EN：M-015 Vertical Machining Center Operation Manual, Section 6.1

## FAQ-017 主轴剧烈振动时还能继续加工吗？
- 所属案例：KB-006
- 问题EN：Can machining continue during severe spindle vibration?
- 答案：不能。剧烈振动伴随金属异响可能意味着轴承失效或保持架断裂，继续运行存在崩裂与飞溅风险。应立即停机、设置警示标识并上报班组长，由具备资质的维修人员检查后再决定处置方案。
- 答案EN：No. Severe vibration with metallic noise may indicate bearing failure or cage fracture; continued operation risks fracture and flying debris. Stop immediately, set warning signs and report to the team leader, and let qualified maintenance personnel inspect before deciding on repairs.
- 依据：《车间安全操作规程》第 2.3 节
- 依据EN：Workshop Safety Operating Procedures, Section 2.3

## FAQ-018 主轴轴承失效有哪些早期征兆？
- 所属案例：KB-006
- 问题EN：What are the early warning signs of spindle bearing failure?
- 答案：常见征兆包括振动值缓慢上升、主轴温升变快、加工表面出现规律振纹、低速运转有周期性异响。发现上述现象应记录振动与温升趋势并安排停机检查，不要等到剧烈抖动才处理。
- 答案EN：Early signs include slowly rising vibration, faster spindle temperature rise, regular chatter marks on the machined surface, and periodic noise at low speed. Record vibration and temperature trends and schedule an inspection instead of waiting for severe vibration.
- 依据：《车间安全操作规程》第 2.3 节
- 依据EN：Workshop Safety Operating Procedures, Section 2.3

## FAQ-019 电柜有焦糊味应该先做什么？
- 所属案例：KB-007
- 问题EN：What should I do first when there is a burning smell in the electrical cabinet?
- 答案：立即断电并挂牌上锁，禁止合闸与带电检查；疏散无关人员，确认无明火后由持证电工开柜检查接线端子、接触器触头与电缆绝缘，必要时用红外测温定位过热点。处理完成并复测绝缘合格后方可送电。
- 答案EN：Cut power immediately and apply a lockout tag. Do not re-energize or inspect live. Keep bystanders away; after confirming there is no open flame, a certified electrician should inspect terminals, contactor contacts and cable insulation, using infrared thermography to locate hot spots if needed. Re-energize only after repair and insulation tests pass.
- 依据：《电气安全操作规程》第 3.2 节
- 依据EN：Electrical Safety Operating Procedures, Section 3.2

## FAQ-020 带电作业有什么风险？
- 所属案例：KB-007
- 问题EN：What are the risks of live electrical work?
- 答案：带电作业存在触电、电弧灼伤与短路引爆风险，本系统明确不支持带电检修。所有电柜检查必须先断电、验电、挂牌上锁，并由持证电工按电气安全操作规程执行。
- 答案EN：Live work carries risks of electric shock, arc burns and short-circuit ignition. This system does not support live maintenance. All cabinet inspections require power-off, voltage verification and lockout/tagout, performed by a certified electrician under the electrical safety procedures.
- 依据：《电气安全操作规程》第 3.2 节
- 依据EN：Electrical Safety Operating Procedures, Section 3.2
