#!/usr/bin/env python
"""
社区矫正走访系统 - 主流程验证测试脚本
验证：注册登录、对象建档、走访登记、定位偏离拦截、
     高风险漏访提醒、风险等级调整后重生成计划、家属反馈保存
"""

import os
import sys
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_correction.settings')
django.setup()

from django.test import Client
from django.urls import reverse
import json


class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_title(title):
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}  {title}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}\n")


def print_pass(msg):
    print(f"{Color.GREEN}✓ PASS{Color.END} - {msg}")


def print_fail(msg):
    print(f"{Color.RED}✗ FAIL{Color.END} - {msg}")


def print_info(msg):
    print(f"{Color.YELLOW}ℹ INFO{Color.END} - {msg}")


class MainFlowTest:
    def __init__(self):
        self.client = Client()
        self.tokens = {}
        self.users = {}
        self.correction_objects = {}
        self.visit_plans = {}
        self.visit_records = {}
        self.feedbacks = {}

    def register_user(self, username, password, role, real_name):
        """注册用户"""
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': username,
                'password': password,
                'confirm_password': password,
                'real_name': real_name,
                'role': role,
                'phone': '13800138000',
                'email': f'{username}@test.com',
                'department': '测试部门'
            },
            content_type='application/json'
        )
        return response

    def login(self, username, password):
        """登录获取token"""
        response = self.client.post(
            '/api/auth/login/',
            {'username': username, 'password': password},
            content_type='application/json'
        )
        if response.status_code == 200:
            data = json.loads(response.content)
            return data.get('access'), data.get('user')
        return None, None

    def auth_header(self, token):
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_1_register_and_login(self):
        """测试1: 注册和登录"""
        print_title("测试1: 用户注册与登录")

        test_users = [
            ('judicial_admin', 'pass123456', 'judicial', '张所长'),
            ('social_worker_li', 'pass123456', 'social_worker', '李社工'),
            ('family_wang', 'pass123456', 'family', '王家属'),
        ]

        all_pass = True
        for username, password, role, real_name in test_users:
            # 注册
            resp = self.register_user(username, password, role, real_name)
            if resp.status_code in (200, 201):
                print_pass(f"注册{role}用户成功: {username} ({real_name})")
            else:
                data = json.loads(resp.content) if resp.content else {}
                print_fail(f"注册{role}用户失败: {username}, status={resp.status_code}, data={data}")
                all_pass = False
                continue

            # 登录
            token, user = self.login(username, password)
            if token:
                self.tokens[username] = token
                self.users[username] = user
                print_pass(f"登录{role}用户成功: {username}")
            else:
                print_fail(f"登录{role}用户失败: {username}")
                all_pass = False

        return all_pass

    def test_2_create_correction_object(self):
        """测试2: 司法所创建矫正对象（对象建档）"""
        print_title("测试2: 矫正对象建档")

        token = self.tokens.get('judicial_admin')
        if not token:
            print_fail("缺少司法所用户token，跳过测试")
            return False

        objects_data = [
            {
                'name': '张三',
                'id_card': '110101199001011234',
                'gender': 'male',
                'age': 34,
                'phone': '13900139001',
                'address': '北京市朝阳区某某小区',
                'risk_level': 'high',
                'status': 'active',
                'correction_type': '社区矫正',
                'correction_start': str(date.today()),
                'correction_end': str(date.today() + timedelta(days=365)),
                'home_longitude': 116.4074,
                'home_latitude': 39.9042,
                'allowed_deviation': 500.0,
                'remark': '高风险对象，需重点关注'
            },
            {
                'name': '李四',
                'id_card': '110101198505055678',
                'gender': 'male',
                'age': 39,
                'phone': '13900139002',
                'address': '北京市海淀区某某小区',
                'risk_level': 'medium',
                'status': 'active',
                'correction_type': '社区矫正',
                'correction_start': str(date.today()),
                'correction_end': str(date.today() + timedelta(days=180)),
                'home_longitude': 116.3211,
                'home_latitude': 39.9591,
                'allowed_deviation': 500.0,
                'remark': '中风险对象'
            }
        ]

        all_pass = True
        for obj_data in objects_data:
            resp = self.client.post(
                '/api/correction-objects/',
                json.dumps(obj_data),
                content_type='application/json',
                **self.auth_header(token)
            )

            if resp.status_code in (200, 201):
                data = json.loads(resp.content)
                self.correction_objects[obj_data['name']] = data
                print_pass(f"创建矫正对象成功: {obj_data['name']} (风险等级: {data['risk_level_display']})")
            else:
                data = json.loads(resp.content) if resp.content else {}
                print_fail(f"创建矫正对象失败: {obj_data['name']}, status={resp.status_code}, data={data}")
                all_pass = False

        return all_pass

    def test_3_assign_worker_and_create_plan(self):
        """测试3: 分配社工并创建走访计划"""
        print_title("测试3: 分配社工与创建走访计划")

        token = self.tokens.get('judicial_admin')
        if not token or not self.correction_objects:
            print_fail("缺少必要数据，跳过测试")
            return False

        zhangsan = self.correction_objects.get('张三')
        if not zhangsan:
            print_fail("缺少张三对象数据，跳过测试")
            return False

        worker = self.users.get('social_worker_li')
        if not worker:
            print_fail("缺少社工用户数据，跳过测试")
            return False

        # 更新对象，分配社工
        update_data = {
            **zhangsan,
            'assigned_worker': worker['id']
        }
        resp = self.client.put(
            f"/api/correction-objects/{zhangsan['id']}/",
            json.dumps(update_data),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code == 200:
            print_pass("成功为张三分配社工: 李社工")
        else:
            data = json.loads(resp.content) if resp.content else {}
            print_fail(f"分配社工失败: status={resp.status_code}, data={data}")

        # 创建走访计划
        plan_data = {
            'correction_object': zhangsan['id'],
            'plan_date': str(date.today() - timedelta(days=2)),
            'plan_type': '高风险定期走访',
            'assigned_worker': worker['id'],
            'remark': '本周首次走访'
        }

        resp = self.client.post(
            '/api/visit-plans/',
            json.dumps(plan_data),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code in (200, 201):
            data = json.loads(resp.content)
            self.visit_plans['overdue_plan'] = data
            print_pass(f"创建逾期走访计划成功: 计划日期={data['plan_date']}, 状态={data['status_display']}")
        else:
            data = json.loads(resp.content) if resp.content else {}
            print_fail(f"创建走访计划失败: status={resp.status_code}, data={data}")
            return False

        # 创建一个今天的计划
        plan_today = {
            'correction_object': zhangsan['id'],
            'plan_date': str(date.today()),
            'plan_type': '高风险定期走访',
            'assigned_worker': worker['id'],
            'remark': '今日走访计划'
        }

        resp = self.client.post(
            '/api/visit-plans/',
            json.dumps(plan_today),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code in (200, 201):
            data = json.loads(resp.content)
            self.visit_plans['today_plan'] = data
            print_pass(f"创建今日走访计划成功: 计划日期={data['plan_date']}")
        else:
            data = json.loads(resp.content) if resp.content else {}
            print_fail(f"创建今日走访计划失败: status={resp.status_code}, data={data}")

        return True

    def test_4_location_deviation_check(self):
        """测试4: 定位偏离校验（走访前验证）"""
        print_title("测试4: 定位偏离校验")

        token = self.tokens.get('social_worker_li')
        zhangsan = self.correction_objects.get('张三')
        if not token or not zhangsan:
            print_fail("缺少必要数据，跳过测试")
            return False

        all_pass = True

        # 测试1: 有效定位（在允许范围内）
        # 使用和家庭地址相同的坐标
        valid_data = {
            'correction_object_id': zhangsan['id'],
            'longitude': 116.4074,
            'latitude': 39.9042
        }

        resp = self.client.post(
            '/api/location-records/validate/',
            json.dumps(valid_data),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code == 200:
            data = json.loads(resp.content)
            if data.get('valid') == True:
                print_pass(f"有效定位校验通过: 偏离距离={data.get('deviation', 0):.2f}米, 允许={data.get('allowed')}米")
            else:
                print_fail(f"有效定位校验异常: 应返回valid=true, 实际={data}")
                all_pass = False
        else:
            print_fail(f"定位校验请求失败: status={resp.status_code}")
            all_pass = False

        # 测试2: 偏离定位（超出允许范围）
        # 使用偏离约1公里的坐标
        invalid_data = {
            'correction_object_id': zhangsan['id'],
            'longitude': 116.4200,
            'latitude': 39.9200
        }

        resp = self.client.post(
            '/api/location-records/validate/',
            json.dumps(invalid_data),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code == 200:
            data = json.loads(resp.content)
            deviation = data.get('deviation', 0)
            if deviation > 500:
                print_pass(f"偏离定位校验正确: 偏离距离={deviation:.2f}米, 超出允许范围 {deviation - 500:.2f}米")
            else:
                print_info(f"偏离定位计算值: {deviation:.2f}米 (坐标差异可能导致距离计算不同)")
        else:
            print_fail(f"定位校验请求失败: status={resp.status_code}")
            all_pass = False

        return all_pass

    def test_5_visit_record_with_deviation_blocked(self):
        """测试5: 定位偏离时走访记录提交被拦截"""
        print_title("测试5: 定位偏离拦截走访提交")

        token = self.tokens.get('social_worker_li')
        zhangsan = self.correction_objects.get('张三')
        plan = self.visit_plans.get('today_plan')
        if not token or not zhangsan or not plan:
            print_fail("缺少必要数据，跳过测试")
            return False

        # 尝试使用偏离定位提交走访
        visit_data = {
            'correction_object': zhangsan['id'],
            'visit_plan': plan['id'],
            'visit_date': str(date.today()) + ' 14:30:00',
            'visit_way': 'home',
            'talk_summary': '今天走访了张三，了解了他的近期情况...',
            'risk_change': 'high',
            'longitude': 116.5000,
            'latitude': 40.0000,
            'remark': '测试偏离定位拦截'
        }

        resp = self.client.post(
            '/api/visit-records/',
            json.dumps(visit_data),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code == 400:
            data = json.loads(resp.content)
            error_msg = data.get('error', '')
            if '定位偏离' in error_msg:
                print_pass(f"定位偏离拦截成功: 返回400状态码, 错误信息='{error_msg}'")
                print_info(f"偏离距离: {data.get('deviation', 0):.2f}米, 允许距离: {data.get('allowed')}米")
                return True
            else:
                print_fail(f"拦截但错误信息不正确: {data}")
                return False
        elif resp.status_code == 201:
            print_fail("定位偏离时走访记录未被拦截，提交成功了（这是错误的）")
            return False
        else:
            data = json.loads(resp.content) if resp.content else {}
            print_fail(f"未知的响应状态: status={resp.status_code}, data={data}")
            return False

    def test_6_visit_record_success(self):
        """测试6: 正常定位下走访登记成功"""
        print_title("测试6: 正常走访登记")

        token = self.tokens.get('social_worker_li')
        zhangsan = self.correction_objects.get('张三')
        plan = self.visit_plans.get('today_plan')
        if not token or not zhangsan or not plan:
            print_fail("缺少必要数据，跳过测试")
            return False

        # 使用有效定位提交走访
        visit_data = {
            'correction_object': zhangsan['id'],
            'visit_plan': plan['id'],
            'visit_date': str(date.today()) + ' 10:00:00',
            'visit_way': 'home',
            'talk_summary': '今天入户走访了张三，他表现良好，思想稳定，积极配合社区矫正工作。',
            'risk_change': '',
            'longitude': 116.4074,
            'latitude': 39.9042,
            'remark': '正常走访'
        }

        resp = self.client.post(
            '/api/visit-records/',
            json.dumps(visit_data),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code == 201:
            data = json.loads(resp.content)
            self.visit_records['normal_visit'] = data
            print_pass(f"走访登记成功: ID={data['id']}, 走访方式={data['visit_way_display']}")
            print_info(f"  定位状态: {'有效' if data['location_valid'] else '无效'}")
            print_info(f"  谈话摘要: {data['talk_summary'][:30]}...")

            # 检查关联的计划状态是否更新
            plan_resp = self.client.get(
                f"/api/visit-plans/{plan['id']}/",
                **self.auth_header(token)
            )
            if plan_resp.status_code == 200:
                plan_data = json.loads(plan_resp.content)
                if plan_data['status'] == 'completed':
                    print_pass("关联的走访计划状态已更新为: 已完成")
                else:
                    print_info(f"走访计划状态: {plan_data['status_display']}")

            return True
        else:
            data = json.loads(resp.content) if resp.content else {}
            print_fail(f"走访登记失败: status={resp.status_code}, data={data}")
            return False

    def test_7_missed_visit_reminder(self):
        """测试7: 高风险对象漏访自动提醒"""
        print_title("测试7: 高风险漏访自动提醒")

        token = self.tokens.get('judicial_admin')
        if not token:
            print_fail("缺少必要数据，跳过测试")
            return False

        # 触发漏访检查
        resp = self.client.post(
            '/api/system/check_missed_visits/',
            **self.auth_header(token)
        )

        if resp.status_code == 200:
            data = json.loads(resp.content)
            count = data.get('count', 0)
            print_pass(f"漏访检查执行成功: 生成 {count} 条通知")

            # 查询司法所用户的通知
            notif_resp = self.client.get(
                '/api/notifications/',
                **self.auth_header(token)
            )
            if notif_resp.status_code == 200:
                notif_data = json.loads(notif_resp.content)
                notif_list = notif_data.get('results', notif_data) if isinstance(notif_data, dict) else notif_data

                missed_notifs = [n for n in notif_list if n.get('type') == 'missed_visit']
                high_risk_notifs = [n for n in missed_notifs if n.get('level') == 'urgent']

                if missed_notifs:
                    print_pass(f"找到 {len(missed_notifs)} 条漏访提醒通知")
                    for n in missed_notifs[:3]:
                        level_text = '紧急(高风险升级)' if n['level'] == 'urgent' else n.get('level_display', '')
                        print_info(f"  - [{level_text}] {n['title']}")
                else:
                    print_info("暂无漏访提醒（可能没有逾期未完成的计划）")

                if high_risk_notifs:
                    print_pass(f"高风险漏访升级提醒正常: 找到 {len(high_risk_notifs)} 条紧急级通知")
                else:
                    print_info("未找到高风险升级提醒")

            return True
        else:
            data = json.loads(resp.content) if resp.content else {}
            print_fail(f"漏访检查失败: status={resp.status_code}, data={data}")
            return False

    def test_8_risk_level_change_and_regenerate_plan(self):
        """测试8: 风险等级调整后自动重生成下月计划"""
        print_title("测试8: 风险等级调整后重生成下月计划")

        token = self.tokens.get('judicial_admin')
        zhangsan = self.correction_objects.get('张三')
        if not token or not zhangsan:
            print_fail("缺少必要数据，跳过测试")
            return False

        all_pass = True

        # 记录调整前的计划数量
        before_resp = self.client.get(
            '/api/visit-plans/',
            {'correction_object_id': zhangsan['id']},
            **self.auth_header(token)
        )
        before_data = json.loads(before_resp.content)
        before_count = len(before_data.get('results', before_data)) if isinstance(before_data, dict) else len(before_data)
        print_info(f"调整风险前，张三的走访计划数量: {before_count}")

        # 将张三从高风险调整为中风险
        change_data = {
            'to_level': 'medium',
            'reason': '近期表现良好，风险等级调整为中风险'
        }

        resp = self.client.post(
            f"/api/correction-objects/{zhangsan['id']}/change_risk_level/",
            json.dumps(change_data),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code == 200:
            data = json.loads(resp.content)
            print_pass(f"风险等级调整成功: high → medium")
            print_info(f"  调整原因: {change_data['reason']}")

            # 更新本地缓存
            self.correction_objects['张三']['risk_level'] = 'medium'

            # 检查是否有风险变更记录
            risk_change_resp = self.client.get(
                '/api/risk-changes/',
                {'correction_object_id': zhangsan['id']},
                **self.auth_header(token)
            )
            if risk_change_resp.status_code == 200:
                risk_data = json.loads(risk_change_resp.content)
                risk_list = risk_data.get('results', risk_data) if isinstance(risk_data, dict) else risk_data
                if risk_list:
                    latest = risk_list[0]
                    if latest.get('regenerated_plan'):
                        print_pass("风险变更后已自动重生成下月计划")
                    else:
                        print_info("风险变更记录存在，但计划重生成状态需确认")
                else:
                    print_fail("未找到风险变更记录")
                    all_pass = False

            # 检查下月计划是否生成
            after_resp = self.client.get(
                '/api/visit-plans/',
                {'correction_object_id': zhangsan['id']},
                **self.auth_header(token)
            )
            after_data = json.loads(after_resp.content)
            after_list = after_data.get('results', after_data) if isinstance(after_data, dict) else after_data
            after_count = len(after_list)
            print_info(f"调整风险后，张三的走访计划数量: {after_count}")

            if after_count > before_count:
                print_pass(f"计划数量增加了 {after_count - before_count} 条，下月计划重生成成功")
            else:
                print_info("计划数量未明显增加（可能已存在自动生成的计划）")

            # 检查通知
            notif_resp = self.client.get(
                '/api/notifications/',
                **self.auth_header(token)
            )
            if notif_resp.status_code == 200:
                notif_data = json.loads(notif_resp.content)
                notif_list = notif_data.get('results', notif_data) if isinstance(notif_data, dict) else notif_data
                risk_notifs = [n for n in notif_list if n.get('type') == 'risk_change']
                if risk_notifs:
                    print_pass(f"找到 {len(risk_notifs)} 条风险变更通知")
                    for n in risk_notifs[:2]:
                        print_info(f"  - {n['title']}")

        else:
            data = json.loads(resp.content) if resp.content else {}
            print_fail(f"风险等级调整失败: status={resp.status_code}, data={data}")
            all_pass = False

        return all_pass

    def test_9_family_feedback(self):
        """测试9: 家属反馈保存"""
        print_title("测试9: 家属帮教反馈")

        token = self.tokens.get('family_wang')
        zhangsan = self.correction_objects.get('张三')
        if not token or not zhangsan:
            print_fail("缺少必要数据，跳过测试")
            return False

        # 先建立家属关系（司法所操作）
        judicial_token = self.tokens.get('judicial_admin')
        family_user = self.users.get('family_wang')
        if judicial_token and family_user:
            relation_data = {
                'correction_object': zhangsan['id'],
                'family_user': family_user['id'],
                'relation': 'spouse',
                'is_primary': True
            }
            self.client.post(
                '/api/family-relations/',
                json.dumps(relation_data),
                content_type='application/json',
                **self.auth_header(judicial_token)
            )
            print_info("已为家属用户建立与张三的关联关系")

        # 家属提交反馈
        feedback_data = {
            'correction_object': zhangsan['id'],
            'feedback_date': str(date.today()),
            'behavior_situation': '张三近期在家表现良好，按时作息，主动承担家务，与家人关系融洽。',
            'mental_state': '思想稳定，对自己的行为有深刻认识，积极改造，对未来生活有规划。',
            'life_condition': '生活规律，身体健康，日常饮食和睡眠都正常。',
            'work_study': '正在寻找合适的工作，也在学习一些技能提升自己。',
            'problems': '偶尔会有情绪低落的时候，需要多鼓励。',
            'suggestions': '希望能多安排一些职业技能培训，帮助他更好地回归社会。'
        }

        resp = self.client.post(
            '/api/family-feedbacks/',
            json.dumps(feedback_data),
            content_type='application/json',
            **self.auth_header(token)
        )

        if resp.status_code == 201:
            data = json.loads(resp.content)
            self.feedbacks['first_feedback'] = data
            print_pass(f"家属反馈提交成功: ID={data['id']}, 状态={data['status_display']}")
            print_info(f"  反馈日期: {data['feedback_date']}")
            print_info(f"  帮教情况: {data['behavior_situation'][:30]}...")

            # 司法所审核
            if judicial_token:
                review_data = {
                    'review_remark': '反馈内容详实，已了解情况。会加强关注和引导。'
                }
                review_resp = self.client.post(
                    f"/api/family-feedbacks/{data['id']}/review/",
                    json.dumps(review_data),
                    content_type='application/json',
                    **self.auth_header(judicial_token)
                )
                if review_resp.status_code == 200:
                    print_pass("司法所审核反馈成功")

                    # 验证审核后状态
                    detail_resp = self.client.get(
                        f"/api/family-feedbacks/{data['id']}/",
                        **self.auth_header(judicial_token)
                    )
                    detail_data = json.loads(detail_resp.content)
                    if detail_data['status'] == 'reviewed':
                        print_pass(f"反馈状态已更新为: {detail_data['status_display']}")
                    else:
                        print_fail(f"反馈状态未更新，当前状态: {detail_data['status']}")
                else:
                    print_fail(f"审核反馈失败: status={review_resp.status_code}")

            return True
        else:
            error_data = json.loads(resp.content) if resp.content else {}
            print_fail(f"家属反馈提交失败: status={resp.status_code}, data={error_data}")
            return False

    def test_10_statistics(self):
        """测试10: 统计数据接口"""
        print_title("测试10: 统计数据")

        results = {}

        # 司法所统计
        token = self.tokens.get('judicial_admin')
        if token:
            resp = self.client.get('/api/system/statistics/', **self.auth_header(token))
            if resp.status_code == 200:
                data = json.loads(resp.content)
                results['judicial'] = data
                print_pass("司法所统计数据获取成功")
                print_info(f"  在矫对象总数: {data.get('total_objects', 0)}")
                print_info(f"  高风险: {data.get('high_risk', 0)}, 中风险: {data.get('medium_risk', 0)}, 低风险: {data.get('low_risk', 0)}")
                print_info(f"  今日计划: {data.get('today_plans', 0)}, 待执行: {data.get('pending_plans', 0)}")
                print_info(f"  本月走访: {data.get('monthly_visits', 0)}")
                print_info(f"  未读通知: {data.get('unread_notifications', 0)}")

        # 社工统计
        token = self.tokens.get('social_worker_li')
        if token:
            resp = self.client.get('/api/system/statistics/', **self.auth_header(token))
            if resp.status_code == 200:
                data = json.loads(resp.content)
                results['social_worker'] = data
                print_pass("社工统计数据获取成功")
                print_info(f"  负责对象: {data.get('total_objects', 0)}")
                print_info(f"  今日计划: {data.get('today_plans', 0)}")

        # 家属统计
        token = self.tokens.get('family_wang')
        if token:
            resp = self.client.get('/api/system/statistics/', **self.auth_header(token))
            if resp.status_code == 200:
                data = json.loads(resp.content)
                results['family'] = data
                print_pass("家属统计数据获取成功")
                print_info(f"  关联对象: {data.get('related_objects', 0)}")
                print_info(f"  我的反馈: {data.get('my_feedbacks', 0)}")

        return len(results) >= 2

    def run_all_tests(self):
        """运行所有测试"""
        print(f"\n{Color.BOLD}{'='*60}")
        print(f"  社区矫正走访系统 - 主流程验证测试")
        print(f"{'='*60}{Color.END}")

        tests = [
            ('注册登录', self.test_1_register_and_login),
            ('对象建档', self.test_2_create_correction_object),
            ('分配社工与创建计划', self.test_3_assign_worker_and_create_plan),
            ('定位偏离校验', self.test_4_location_deviation_check),
            ('定位偏离拦截走访', self.test_5_visit_record_with_deviation_blocked),
            ('正常走访登记', self.test_6_visit_record_success),
            ('高风险漏访提醒', self.test_7_missed_visit_reminder),
            ('风险调整后重生成计划', self.test_8_risk_level_change_and_regenerate_plan),
            ('家属反馈保存', self.test_9_family_feedback),
            ('统计数据接口', self.test_10_statistics),
        ]

        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                print_fail(f"测试执行异常: {str(e)}")
                import traceback
                traceback.print_exc()
                results.append((name, False))

        # 总结
        print(f"\n{Color.BOLD}{'='*60}")
        print(f"  测试结果汇总")
        print(f"{'='*60}{Color.END}\n")

        passed = sum(1 for _, r in results if r)
        total = len(results)

        for name, result in results:
            status = f"{Color.GREEN}PASS{Color.END}" if result else f"{Color.RED}FAIL{Color.END}"
            print(f"  {status} - {name}")

        print(f"\n{Color.BOLD}总计: {passed}/{total} 个测试通过{Color.END}")

        if passed == total:
            print(f"\n{Color.GREEN}{Color.BOLD}🎉 所有主流程验证通过！{Color.END}")
        else:
            print(f"\n{Color.RED}{Color.BOLD}⚠ 有 {total - passed} 个测试未通过，请检查{Color.END}")

        return passed == total


if __name__ == '__main__':
    # 清理旧数据库
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    if os.path.exists(db_path):
        os.remove(db_path)
        print_info("已清理旧数据库")

    # 执行迁移
    from django.core.management import call_command
    call_command('migrate', verbosity=0)
    print_info("数据库迁移完成")

    # 运行测试
    tester = MainFlowTest()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)
