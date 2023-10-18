#本系统运行时，在某些电脑可能会出现问题，目前不能找到本质原因，具体出在对order文件的解码操作上，其余文件的解码操作也有概率需要具体修改。
# -*- coding:utf-8 -*-
#coding: unicode_escape

class Order:
    def __init__(self, user, shop):
        self.user = user
        self.shop = shop
        
class User:
    def __init__(self, username, password, contact):
        self.username = username
        self.password = password
        self.contact = contact
        
class Shop:
    def __init__(self, id, name):
        self.id = id
        self.name = name


import os
import json
import re
import heapq
import random

class RestaurantDistanceFinder:
    
    def __init__(self, filepath, university_name, target_restaurant, encoding='GBK'):
        self.graph_with_names = self._load_distance_data(filepath, encoding)
        self.university_name = university_name
 
        
        # Set distance from the university to the target restaurant to 0
        self.graph_with_names[self.university_name] = {key: float('infinity') for key in self.graph_with_names.keys()}
        self.graph_with_names[self.university_name][target_restaurant] = 0
        
        # Ensure the target restaurant is in the graph and has distances to other restaurants
        if target_restaurant not in self.graph_with_names:
            self.graph_with_names[target_restaurant] = {key: float('infinity') for key in self.graph_with_names.keys()}
            self.graph_with_names[target_restaurant][university_name] = 0

    def _load_distance_data(self, filepath, encoding):
        distance_dict_with_names = {}
        with open(filepath, 'r', encoding=encoding) as file:
            distance_content = file.readlines()
        
        for line in distance_content[1:]:
            line = line.strip()
            if not line:
                continue
            parts = re.split(r'\s+', line)
            if len(parts) == 5:
                _, name1, _, name2, distance = parts
                distance = float(distance)
                distance_dict_with_names[(name1, name2)] = distance
                distance_dict_with_names[(name2, name1)] = distance
        
        graph_with_names = {}
        for (name1, name2), distance in distance_dict_with_names.items():
            if name1 not in graph_with_names:
                graph_with_names[name1] = {}
            graph_with_names[name1][name2] = distance
        
        return graph_with_names

    def dijkstra(self, start):
        distances = {node: float('infinity') for node in self.graph_with_names}
        distances[start] = 0
        priority_queue = [(0, start)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            if current_distance > distances[current_node]:
                continue
            for neighbor, weight in self.graph_with_names[current_node].items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        return distances

    def find_shortest_paths_from_university(self):
        shortest_paths = self.dijkstra(self.university_name)
        if self.university_name in shortest_paths:
            del shortest_paths[self.university_name]
        return shortest_paths

    def get_formatted_shortest_paths(self):
        shortest_paths = self.find_shortest_paths_from_university()
        formatted_paths = {}
        for restaurant, distance in shortest_paths.items():
            formatted_distance = "{:.2f}".format(distance)
            formatted_paths[restaurant] = f"该餐馆距离您的最短距离为 {formatted_distance} 千米"
        return formatted_paths






class RestaurantManagementSystem:
    def __init__(self,restaurant_finder):
        # Load data from files/Desktop/团队实验数据集/user.txt"')
        self.shops = self.load_shops_data('C://Users//月白//Desktop//团队实验数据集//shop.txt')
        self.orders = self.load_orders_data('C://Users//月白//Desktop//团队实验数据集//order.txt')

        self.users = self.load_users_data('C://Users//月白//Desktop//团队实验数据集//user.txt')
    
    def load_users_data(self, filename):
        filename = 'C://Users//月白//Desktop//团队实验数据集//user.txt'  # 请替换为你的文件路径
        users = []
        with open(filename, 'r', encoding='gbk') as file:
            # 跳过首行
            next(file)
            
            for line in file:
                #按照空格或制表符分割这行文本
                fields = line.split()
                # 检查我们是否有预期数量的字段
                if len(fields) == 3:
                    try:
                        user_data = [int(fields[0].strip()), int(fields[1].strip()), int(fields[2].strip())]
                        users.append(user_data)
                    except ValueError:
                        # 如果转换失败，可以在这里打印错误或采取其他操作
                        pass
                        
        return users

    def load_shops_data(self,filename):
        filename = 'C://Users//月白//Desktop//团队实验数据集//shop.txt'
        shops = []
        if not os.path.exists(filename):
            raise FileNotFoundError("File does not exist")
        else:
            with open(filename, 'r', encoding='gbk') as file:
                shop_data = {}
                for line in file:
                    line = line.strip()
                    if line:  # 查看该行是否为空
                        try:
                            key, value = line.split(': ', 1)
                        except ValueError:
                            continue  # 如果这行文本中没有冒号和空格，就跳过这行
                        if key == "shoptype":
                            if shop_data:  #如果已经有前一个商店的数据，保存它
                                shops.append(shop_data)
                                shop_data = {}  # #重新设置下一个商店的字典
                        shop_data[key] = value
                if shop_data:  #处理上一家商店
                    shops.append(shop_data)
                    
        return shops
    def load_orders_data(self, filename):
        # 这里不应该再次定义filename，因为它已经作为一个参数传递
        orders = []

        # 检查文件是否存在
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} 不存在")

        with open(filename, 'r', encoding='gbk') as file:
            # 跳过表头行
            next(file)
            line_number = 2
            for line in file:
                line = line.strip()
                if line:  # 检查行是否不为空
                    # 使用正则表达式匹配查找user_id和reservation_time
                    match = re.match(r'(\d+)\s+(.*\S)\s+(\d+月\d+日[午晚]餐)', line)
                    if match:
                        order = {
                            "user_id": match.group(1),
                            "shop_name": match.group(2),
                            "reservation_time": match.group(3)
                        }
                        orders.append(order)
                    else:
                        print(f"Line {line_number} doesn't match expected format. Line content: {line}")
                else:
                    print(f"Empty line found at line {line_number}.")
                line_number += 1
            return orders





        
    def save_data(self, data, filename):
        try:
            print(f"Saving data to {os.path.abspath(filename)}")
            
            # 读取现有数据
            existing_data = self._read_existing_data(filename)
            
            # 在适当的位置插入新数据
            updated_data = self._insert_data_in_order(data, existing_data)
            
            # 重新写入文件
            self._write_data(updated_data, filename)
            
            print(f"Data: {data}")
        except (OSError, TypeError, ValueError) as e:
            print(f"Error: {str(e)}")
        print(f"File size after save: {os.path.getsize(filename)} bytes")
        
    def _read_existing_data(self, filename):
        existing_data = []
        try:
            with open(filename, 'r') as file:
                # Skip the first two lines
                next(file)
                next(file)
                lines = file.readlines()
            for i, line in enumerate(lines):
                try:
                    # Ignore empty lines
                    if not line.strip():
                        continue
                    # Use regular expression to split the line
                    items = re.split(r'\s+', line.strip())
                    # Convert the split items to integers
                    existing_data.append(list(map(int, items)))
                except ValueError as e:
                    print(f"Warning: Skipping line {i+3} due to error: {str(e)}")
        except FileNotFoundError:
            pass
        return existing_data
    
    def _insert_data_in_order(self, data, existing_data):
        # 如果新数据是子列表，迭代每一行并插入它们
        if isinstance(data[0], list):
            for row in data:
                existing_data = self._insert_single_row(row, existing_data)
        else:
            existing_data = self._insert_single_row(data, existing_data)
        return existing_data

    def _insert_single_row(self, data, existing_data):
        # 确保输入数据是一个列表并且不为空
        if not isinstance(data, list) or len(data) == 0:
            print(f"Invalid data format. Expected a non-empty list. Received: {data}")
            return existing_data

        inserted = False
        for i, existing_row in enumerate(existing_data):
            # 确保现有的数据行是一个列表并且不为空
            if isinstance(existing_row, list) and len(existing_row) > 0:
                try:
                    if data[0] < existing_row[0]:
                        existing_data.insert(i, data)
                        inserted = True
                        break
                except TypeError:
                    # 打印出问题的数据
                    print(f"Error while comparing data. New data: {data}, Existing data: {existing_row}")
                    continue  # 继续下一次循环

        if not inserted:
            existing_data.append(data)
        return existing_data





    
    def _write_data(self, data, filename):
        with open(filename, 'w') as file:
            # Writing the header back
            file.write('\n用户账号\t密码\t联系方式\n')
            for row in data:
                line = '\t'.join(map(str, row))
                file.write(line + '\n')
# Sample modified save_data_order function snippet

    def save_data_order(self, orders, encoding='gbk'):
        order_file = 'C://Users//月白//Desktop//团队实验数据集//order.txt'
        
        # Check if the file path exists and if it's writable
        if not os.path.exists(order_file):
            print(f"错误：文件路径 {order_file} 不存在。")
            return False
        if not os.access(order_file, os.W_OK):
            print(f"错误：没有写入 {order_file} 的权限。")
            return False
            
        # Enhanced exception handling
        try:
            with open(order_file, 'a', encoding=encoding) as file:
                for order in orders:
                    line = f"{order.get('user_id', 'N/A')}\t{order.get('shop_name', 'N/A')}\t{order.get('reservation_time', 'N/A')}\n"
                    file.write(line)
            return True
        except UnicodeEncodeError:
            print("错误：写入文件时遇到编码错误。请检查订单中的字符是否都支持GBK编码。")
            return False
        except IOError as e:
            print(f"IO错误：写入文件时出错，错误信息: {e}")
            return False
        except Exception as e:
            print(f"错误：写入文件时出错，错误信息: {e}")
            return False

# This is just a snippet, and it requires the os module to be imported.
# Also, this code doesn't run here as it's just a demonstration.




    

    def delete_orders(self):

        try:
            # Requesting the user to input the number of orders to delete
            n = int(input("请输入要处理的订单数量："))
            
            # Confirming the deletion operation
            confirm = input(f"确定要处理前 {n} 个订单吗? (y/n)：")
            if confirm.lower() != 'y':
                print("删除操作已取消。")
                return
            
            with open('C://Users//月白//Desktop//团队实验数据集//order.txt', 'r', encoding='gbk') as file:
                lines = file.readlines()
                
            # Checking if the input n is valid
            if n > len(lines) or n < 0:
                print("输入的订单数量无效。删除操作已取消。")
                return
                
            # Deleting the first n orders
            del lines[:n]
            
            with open('C://Users//月白//Desktop//团队实验数据集//order.txt', 'w', encoding='gbk') as file:
                file.writelines(lines)
            
            print(f"成功处理前 {n} 个订单！")
        except ValueError:
            print("请输入有效的订单数量。")



    # User System
    def register_user(self):
        username = input("请输入账号: ")
        password = input("请输入密码: ")
        contact = input("请输入联系方式: ")
        
        # 将用户数据转换为整数列表
        user_data = [int(username), int(password), int(contact)]
        
        self.users.append(user_data)  # 将用户数据添加到列表中
        self.save_data(self.users, 'C://Users//月白//Desktop//团队实验数据集//user.txt')
        print(f"用户 {username} 注册成功！")





    def login_user(self):
        username = input("请输入账号: ")
        password = input("请输入密码: ")
        for user in self.users:
            if user[0] == int(username) and user[1] == int(password):  # Assuming username and password are integers
                print(f"用户 {username} 登录成功！")
                return user
        print("无效账户或密码！")
        return None


    def manage_user_info(self, user):
        print("1. 查看个人信息")
        print("2. 修改个人信息")
        print("3. 注销个人信息")
        choice = input("选择选项: ")
        if choice == '1':
            print(f"账户： {user[0]}")
            print(f"联系方式： {user[2]}")
        elif choice == '2':
            new_password = input("请输入新密码: ")
            new_contact = input("请输入新联系方式: ")
            user[1] = new_password
            user[2] = new_contact
            self.save_data(self.users, 'C://Users//月白//Desktop//团队实验数据集//user.txt')
            print("信息已更新！")
        elif choice == '3':
            self.users.remove(user)
            self.save_data(self.users, 'C://Users//月白//Desktop//团队实验数据集//user.txt')
            print("账户已注销！")
        else:
            print("无效选择！")




    def logout_personal_info(username):
        """注销个人信息"""
        lines = []
        with open("C://Users//月白//Desktop//团队实验数据集//user.txt", "r") as f:
            for line in f:
                if not line.startswith(username + ","):
                    lines.append(line.strip())
        with open("C://Users//月白//Desktop//团队实验数据集//user.txt", "w") as f:
            for line in lines:
                f.write(line + "\n")
    def menu(self):
            print("\n===== 餐馆管理信息系统 =====")
            print("1. 用户系统")
            print("2. 店主系统")
            print("3. 后台管理系统")
            print("4. 退出")
            choice = input("请输入选择: ")
            return choice

    # 商家系统


    def find_shop(self, name=None):
        if not name:
            name = input("请输入商家名称进行查找: ")
        for shop in self.shops:
            if shop.get('shopName') == name:
                print(f"商家 {name} 已被找到，商家ID为 {shop.get('shopId')}")
                return shop
        print("未找到餐馆！")
        return None

    #预定系统
    def place_order(self):
        self.recommend_run()
        shop_name = input("请输入商家名称以进行预定: ")

        # 获取大学到所有餐馆的最短路径
        distance_finder = RestaurantDistanceFinder(filepath='C://Users//月白//Desktop//团队实验数据集//distance.txt', university_name='中国矿业大学', target_restaurant='砂锅米线（矿大北门店）')
        shortest_paths = distance_finder.find_shortest_paths_from_university()

        # 查找到特定餐馆的最短路径
        if shop_name in shortest_paths:
            distance = shortest_paths[shop_name]
            formatted_distance = "{:.2f}".format(distance)
            print(f"到 {shop_name} 的最短距离是 {formatted_distance} km。")
        else:
            print(f"没有关于 {shop_name} 的有效距离信息。")

        shop = self.find_shop(shop_name)
        if shop:
            user_id = input("请输入您的用户ID: ")
            reservation_time = input("请输入预定时间 (例如：'12月20日午餐'): ")

            # Create a single order dictionary
            order = {
                'user_id': user_id,
                'shop_name': shop_name,
                'reservation_time': reservation_time
            }

            # Use the save_data_order function with a list containing the single order
            success = self.save_data_order([order])
            if success:
                print(f"已成功预定 {shop_name}！")
            else:
                print("预定失败。")
        else:
            print("未找到商店！")

# This is just a


    def view_orders(self, user):
        # 用get方法安全地从字典中获取值，并确保类型匹配
        user_id_str = str(user[0])   # 转换为字符串进行比较
        user_orders = [order for order in self.orders if order.get('user_id') == user_id_str]

        if user_orders:
            for order in user_orders:
                # 这里只使用shop_name，因为load_orders_data里面保存的是shop_name
                print(f"来自 {order.get('shop_name', 'Unknown shop')} 的预定")
        else:
            print("未找到预定信息！")




    def read_all_restaurants_from_file(self, filename):            
        with open(filename, 'r', encoding='gbk') as f:
            content = f.read()

        lines = content.strip().split("\n")
        restaurants = []
        current_restaurant = {}
        foods = []
        comments = []
        
        for line in lines:
            if line.startswith("shoptype:"):
                # 如果我们遇到一个新的餐厅，我们保存以前的，并开始一个新的字典
                if current_restaurant:
                    current_restaurant['foods'] = foods
                    current_restaurant['comments'] = comments
                    restaurants.append(current_restaurant)
                    current_restaurant = {}
                    foods = []
                    comments = []
                
                current_restaurant['shoptype'] = line.split(":")[1].strip()
            elif line.startswith("shopId:"):
                current_restaurant['shopId'] = int(line.split(":")[1].strip())
            elif line.startswith("shopName:"):
                current_restaurant['shopName'] = line.split(":")[1].strip()
            elif line.startswith("shopPassword:"):
                current_restaurant['shopPassword'] = line.split(":")[1].strip()
            elif line.startswith("avgScore:"):
                current_restaurant['avgScore'] = float(line.split(":")[1].strip())
            elif line.startswith("avePrice:"):
                current_restaurant['avePrice'] = float(line.split(":")[1].strip())
            elif line.startswith("address:"):
                current_restaurant['address'] = line.split(":")[1].strip()
            elif line.startswith("phone:"):
                current_restaurant['phone'] = line.split(":")[1].strip()
            elif line.startswith("food_id:"):
                food_info = line[len("food_id:"):].strip()
                food_parts = [part.strip() for part in food_info.split(",")]
                if len(food_parts) == 3:
                    food_id = int(food_parts[0])
                    food_name = food_parts[1].split(":")[1].strip()
                    food_price = float(food_parts[2].split(":")[1].strip())
                    food = {
                        'food_id': food_id,
                        'food_name': food_name,
                        'food_price': food_price
                    }
                    foods.append(food)
            elif line.startswith("Comment"):
                comments.append(line.split(":")[1].strip())
        
        # 添加最后一家餐厅（如果存在）
        if current_restaurant:
            current_restaurant['foods'] = foods
            current_restaurant['comments'] = comments
            restaurants.append(current_restaurant)
        
        return restaurants

    # 查询符合要求的餐馆

    def recommend(self, shoptype='', special_dish='', feature=''):
        try:
            filtered_restaurants = self.shops
            if shoptype:
                filtered_restaurants = [r for r in filtered_restaurants if r['shoptype'] == shoptype]
            if special_dish:
                filtered_restaurants = [r for r in filtered_restaurants for f in r.get('foods', []) if special_dish in f['food_name']]

            sorted_restaurants = sorted(filtered_restaurants, key=lambda r: r['avgScore'], reverse=True)

            # 输出结果
            if sorted_restaurants:
                print("以下是符合要求的餐馆：")
                for r in sorted_restaurants:
                    print(f"{r['shopName']} ({r['shoptype']}) - 评分: {r['avgScore']}")
            else:
                print("抱歉，没有符合要求的餐馆。")
        except Exception as e:
            print(f"出现错误：{e}")

    def recommend_run(self):
        filename = 'C://Users//月白//Desktop//团队实验数据集//shop.txt'
        restaurants = self.read_all_restaurants_from_file(filename)
        if restaurants:
            print(f"成功读取了 {len(restaurants)} 家餐馆的信息。")
        else:
            print(f"读取文件 {filename} 失败。请查看上面的错误信息。")

        # 用户输入
        shoptype = input("请输入餐馆类别：")
        special_dish = input("请输入特色菜：")
        feature = input("请输入餐馆特点：")

        # 推荐餐馆
        self.recommend(shoptype=shoptype, special_dish=special_dish, feature=feature)


    def admin_menu(self):
        print("1. 查看所有用户")
        print("2. 查看所有商家")
        print("3. 删除某个用户")
        print("4. 删除某个商家")
        print("5. 退出")
        choice = input("请输入选项: ")
        return choice

    def admin_run(self):
        while True:
            choice = self.admin_menu()
            if choice == '1':
                users = self.view_all_users()
                for user in users:
                    print(f"用户账号: {user[0]}, 联系方式: {user[2]}")
            elif choice == '2':
                shops = self.view_all_shops()
                for shop in shops:
                    print(f"商家 ID: {shop[0]}, 商家名称: {shop[1]}")
            elif choice == '3':
                username = input("请输入用户账号以删除: ")
                self.delete_user(username)
                print("用户已删除！")
            elif choice == '4':
                shopname = input("请输入商家名称以删除: ")
                self.delete_shop(shopname)
                print("商家已删除！")
            elif choice == '5':
                break  
    def view_all_users(self):  # <-- 添加self参数
        """查看所有用户"""
        users_data = self.load_users_data('C://Users//月白//Desktop//团队实验数据集//user.txt')
        return [(user['username'], user['contact']) for user in users_data]

    def view_all_shops(self):
        """查看所有商家"""
        shops_data = self.load_shops_data('"C://Users//月白//Desktop//团队实验数据集//shop.txt"')
        return [(shop['shopId'], shop['shopName']) for shop in shops_data]  
    def delete_user(self, username):  # <-- 添加self参数
        """删除用户"""
        lines = []
        with open("C://Users//月白//Desktop//团队实验数据集//user.txt", "r", encoding='gbk') as f:
            for line in f:
                if not line.startswith(username + ","):
                    lines.append(line.strip())
        with open("C://Users//月白//Desktop//团队实验数据集//user.txt", "w") as f:
            for line in lines:
                f.write(line + "\n")
    def delete_shop(self, shopname):
        """删除商家"""
        lines = []
        delete_mode = False
        
        with open("C://Users//月白//Desktop//团队实验数据集//shop.txt", "r", encoding='gbk') as f:
            for line in f:
                if "shopName:" in line and shopname in line:
                    delete_mode = True
                if "shopId:" in line and delete_mode:
                    delete_mode = False
                    continue  # skip the current shopId line
                if not delete_mode:
                    lines.append(line.strip())
                    
        with open("C://Users//月白//Desktop//团队实验数据集//shop.txt", "w", encoding='gbk') as f:
            for line in lines:
                f.write(line + "\n")


class InteractiveSystem:               
    def __init__(self):
        self.system = RestaurantManagementSystem(RestaurantDistanceFinder)
        

    def main_menu(self):
        while True:
            print("\n===== 餐馆信息管理系统 =====")
            print("1. 用户系统")
            print("2. 店主系统")
            print("3. 后台管理系统")
            print("4. 退出")
            choice = input("请输入选项: ")

            if choice == '1':
                self.user_system()
            elif choice == '2':
                self.shop_owner_system()
            elif choice == '3':
                self.admin_system()
            elif choice == '4':
                print("正在退出系统。再见！")
                break
            else:
                print("无效选项。请再次尝试！")

    def user_system(self):
        while True:
            print("\n----- 用户系统 -----")
            print("1. 注册")
            print("2. 登录")
            print("3. 返回主菜单")
            choice = input("请输入选项: ")

            if choice == '1':
                self.system.register_user()
            elif choice == '2':
                user = self.system.login_user()
                if user:
                    self.user_options(user)
            elif choice == '3':
                break
            else:
                print("无效选项。请再次尝试！")

    def user_options(self, user):
        while True:
            print(f"\n欢迎 {user[0]}！")

            print("1. 管理个人信息")
            print("2. 添加预定")
            print("3. 查看预定")
            print("4. 退出账号")
            choice = input("请输入选项: ")

            if choice == '1':
                self.system.manage_user_info(user)
            elif choice == '2':
                self.system.place_order()
            elif choice == '3':
                self.view_orders(user)
            elif choice == '4':
                print("已退出！")
                break
    def shop_owner_menu(self):
        print("1. 查看餐馆所有预定")
        print("2. 处理预定")
        print("3. 退出")
        choice = input("请输入选项: ")
        return choice

    def shop_owner_run(self):
        shop_name = input("请输入你的商家名称: ")
        while True:
            choice = self.shop_owner_menu()
            if choice == '1':
                self.view_orders_for_shop(shop_name)
            elif choice =='2':
                self.system.delete_orders()
            
            elif choice == '3':
                break
    def view_orders_for_shop(self, shop_name):
        orders_for_shop = [order for order in self.system.orders if order['shop_name'] == shop_name]
        if orders_for_shop:
            for order in orders_for_shop:
                print(f"Ordered by {order['user_id']}")
        else:
            print("未找到预定信息!")
    def view_orders(self, user):
        # 用get方法安全地从字典中获取值，并确保类型匹配
        user_id_str = str(user[0])  # 转换为字符串进行比较  # 转换为字符串进行比较
        user_orders = [order for order in self.system.orders if order.get('user_id') == user_id_str]

        if user_orders:
            for order in user_orders:
                # 这里只使用shop_name，因为load_orders_data里面保存的是shop_name
                print(f"预定来自 {order.get('shop_name', 'Unknown shop')} ")
        else:
            print("未找到预定信息！")

    def shop_owner_system(self):
        print("\n----- 店主系统 -----")
        self.shop_owner_run()

    def admin_system(self):
        while True:
            print("\n----- 后台管理系统 -----")
            print("1. 查看所有用户")
            print("2. 查看所有商家")
            print("3. 删除某个用户")
            print("4. 删除某个商家")
            print("5. 退出")
            choice = input("请输入选项: ")

            if choice == '1':
            
                users = self.system.load_users_data('C://Users//月白//Desktop//团队实验数据集//user.txt')
                print(users)
            elif choice == '2':
                shops = self.system.view_all_shops()
                for shop in shops:
                    print(f"商家ID: {shop[0]}, 商家名称: {shop[1]}")
            elif choice == '3':
                username = input("请输入用户名以删除: ")
                self.system.delete_user(username)
                print("用户已删除！")
            elif choice == '4':
                shopname = input("请输入商家名称以删除： ")
                self.system.delete_shop(shopname)
                print("商家已删除！")
            elif choice == '5':
                print("已返回主菜单！")
                break
            else:
                print("无效选项。 请再次尝试！")

if __name__ == '__main__':

    app = InteractiveSystem()
    app.main_menu()